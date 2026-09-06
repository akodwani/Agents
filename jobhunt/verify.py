"""Live-job verification.

A search result is not evidence that a job is open. Every admitted posting is
re-opened at its canonical URL and classified:

    LIVE_CONFIRMED  page loads, title+employer present, apply mechanism found,
                    no closure language, validThrough (if any) not past
    LIKELY_LIVE     page loads and looks like the posting, but one signal is
                    missing (no apply control found, or JS-only page)
    UNCERTAIN       could not be fetched (blocked host, network error)
    DEAD            404 / closure language / validThrough in the past
"""

from __future__ import annotations

import datetime as dt
import re

from .config.taxonomy import CLOSED_PATTERNS
from .db import now
from .extract import html_to_text, job_posting_ld, parse_job_posting_ld
from .fetch import Fetcher
from .normalize import norm_company, norm_title

APPLY_RE = re.compile(
    r"(apply now|apply for this job|submit (?:your )?application|apply online|"
    r"start your application|<form[^>]+apply|id=[\"']apply|class=[\"'][^\"']*apply|"
    r"application form|apply to this job|/apply\b)", re.I)

CLOSED_RE = re.compile("|".join(CLOSED_PATTERNS), re.I)


def _title_present(title: str, text: str) -> bool:
    if not title:
        return False
    t = norm_title(title)
    words = [w for w in t.split() if len(w) > 3]
    if not words:
        return title.lower() in text.lower()
    hay = norm_title(text[:20000])
    hits = sum(1 for w in words if w in hay)
    return hits >= max(1, int(len(words) * 0.6))


def verify(url: str, expected_title: str, expected_company: str, f: Fetcher,
           use_browser: bool = True) -> dict:
    """Verify one posting URL. Returns dict of verification fields."""
    out = {
        "verification_status": "UNCERTAIN",
        "verification_timestamp": now(),
        "verification_evidence": "",
        "final_url": url,
    }
    if not url or not url.startswith("http"):
        out["verification_status"] = "UNCERTAIN"
        out["verification_evidence"] = "no usable URL"
        return out

    r = f.get(url)
    evidence: list[str] = []

    if r.status == 404 or (r.status and r.status >= 400 and r.status not in (401, 403, 429)):
        out["verification_status"] = "DEAD"
        out["verification_evidence"] = f"HTTP {r.status}"
        return out
    if not r.ok:
        reason = (r.reason or f"HTTP {r.status}")
        if "ProxyError" in reason or "403 Forbidden" in reason:
            reason = "host unreachable from this machine (egress proxy refused the connection)"
        out["verification_evidence"] = reason[:160]
        out["verification_status"] = "UNCERTAIN"
        return out

    html = r.text
    out["final_url"] = r.final_url or url
    text = html_to_text(html, limit=60000)

    if len(text) < 400 and use_browser:
        rendered = render_with_browser(url)
        if rendered:
            html = rendered
            text = html_to_text(html, limit=60000)
            evidence.append("rendered with headless browser")

    if CLOSED_RE.search(text[:8000]):
        m = CLOSED_RE.search(text[:8000])
        out["verification_status"] = "DEAD"
        out["verification_evidence"] = f"closure language: '{m.group(0)[:60]}'"
        return out

    ld = job_posting_ld(html)
    if ld:
        parsed = parse_job_posting_ld(ld)
        evidence.append("JobPosting JSON-LD present")
        out["ld"] = parsed
        vt = parsed.get("valid_through")
        if vt:
            try:
                if dt.date.fromisoformat(vt[:10]) < dt.date.today():
                    out["verification_status"] = "DEAD"
                    out["verification_evidence"] = f"validThrough {vt} is in the past"
                    return out
                evidence.append(f"validThrough {vt} still in future")
            except ValueError:
                pass
        if parsed.get("date_posted"):
            evidence.append(f"datePosted {parsed['date_posted']}")

    title_ok = _title_present(expected_title, text) or (
        ld is not None and _title_present(expected_title, (out.get("ld") or {}).get("title", "")))
    company_ok = (not expected_company) or norm_company(expected_company).split()[0] in \
        norm_company(text[:20000] + " " + ((out.get("ld") or {}).get("company", "")))
    apply_ok = bool(APPLY_RE.search(html))

    if title_ok:
        evidence.append("title present on page")
    if company_ok:
        evidence.append("employer present on page")
    if apply_ok:
        evidence.append("apply mechanism found")

    if title_ok and apply_ok and (company_ok or ld):
        out["verification_status"] = "LIVE_CONFIRMED"
    elif title_ok or ld:
        out["verification_status"] = "LIKELY_LIVE"
    else:
        out["verification_status"] = "UNCERTAIN"
        evidence.append("page loaded but posting content not recognised")

    out["verification_evidence"] = "; ".join(evidence)
    return out


_BROWSER_OK: bool | None = None


def render_with_browser(url: str, timeout_ms: int = 25000) -> str | None:
    """Render a JS-heavy posting (Workday, iCIMS, some SPAs) with Playwright."""
    global _BROWSER_OK
    if _BROWSER_OK is False:
        return None
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        _BROWSER_OK = False
        return None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")
            page.goto(url, timeout=timeout_ms, wait_until="domcontentloaded")
            page.wait_for_timeout(2500)
            html = page.content()
            browser.close()
            _BROWSER_OK = True
            return html
    except Exception:
        return None
