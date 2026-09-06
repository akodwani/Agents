"""Employer discovery: careers-page resolution and ATS detection.

Given an employer name and (optionally) a website, work out where its jobs
actually live. Order of attempts:

 1. any known/declared careers URL
 2. common careers paths on the employer domain
 3. ATS links found on those pages
 4. sitemap.xml scan for job-shaped URLs
"""

from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

from .ats import detect_ats, ADAPTERS
from .extract import links, html_to_text
from .fetch import Fetcher

CAREERS_PATHS = [
    "/careers", "/careers/", "/jobs", "/jobs/", "/about/careers", "/company/careers",
    "/join-us", "/work-with-us", "/opportunities", "/careers/open-positions",
    "/about/jobs", "/employment", "/careers/jobs", "/team/careers", "/careers/openings",
]

CAREERS_LINK_RE = re.compile(r"\b(careers?|jobs|join[- ]us|work with us|open (?:roles|positions)|employment|opportunities)\b", re.I)

ATS_HOST_RE = re.compile(
    r"(greenhouse\.io|lever\.co|ashbyhq\.com|workable\.com|smartrecruiters\.com|"
    r"jobvite\.com|icims\.com|bamboohr\.com|applytojob\.com|teamtailor\.com|"
    r"recruitee\.com|breezy\.hr|comeet\.com|rippling\.com|myworkdayjobs\.com|"
    r"pinpointhq\.com|jobs\.gem\.com|paylocity\.com|adp\.com|ultipro\.com|"
    r"successfactors\.com|taleo\.net|jazz\.co)", re.I)


def normalise_site(website: str) -> str:
    if not website:
        return ""
    if not website.startswith("http"):
        website = "https://" + website
    p = urlparse(website)
    return f"{p.scheme}://{p.netloc}"


def find_careers_url(website: str, f: Fetcher) -> tuple[str | None, str]:
    """Return (careers_url, status). Status is ok | unresolved | blocked | error."""
    base = normalise_site(website)
    if not base:
        return None, "unresolved"

    home = f.get(base)
    if home.blocked:
        return None, "blocked"
    if home.ok:
        for href in links(home.text, home.url):
            if urlparse(href).netloc and ATS_HOST_RE.search(href):
                return href, "ok"
        for href in links(home.text, home.url):
            path = urlparse(href).path.lower()
            if CAREERS_LINK_RE.search(path) and urlparse(href).netloc.endswith(urlparse(base).netloc.split(":")[0][-20:]):
                return href, "ok"

    for path in CAREERS_PATHS[:8]:
        r = f.get(urljoin(base, path))
        if r.ok and len(r.text) > 1500:
            return r.final_url or r.url, "ok"
        if r.blocked:
            return None, "blocked"
    return None, "unresolved"


def resolve_ats(careers_url: str, f: Fetcher) -> tuple[str | None, str | None, str | None]:
    """Return (provider, slug, board_url) for a careers page."""
    provider, slug = detect_ats(careers_url or "")
    if provider:
        from .ats import BY_NAME
        return provider, slug, BY_NAME[provider].board_url(slug)

    r = f.get(careers_url)
    if not r.ok:
        return None, None, None

    # Direct ATS links, iframes and embed scripts all show up in the raw HTML.
    for href in links(r.text, r.url):
        provider, slug = detect_ats(href)
        if provider:
            from .ats import BY_NAME
            return provider, slug, BY_NAME[provider].board_url(slug)
    for m in ATS_HOST_RE.finditer(r.text):
        window = r.text[max(0, m.start() - 200): m.end() + 200]
        for cand in re.findall(r"https?://[^\s\"'<>]+", window):
            provider, slug = detect_ats(cand)
            if provider:
                from .ats import BY_NAME
                return provider, slug, BY_NAME[provider].board_url(slug)
    return None, None, None


JOB_URL_RE = re.compile(r"/(?:job|jobs|career|careers|position|posting|opening|vacanc)[s]?/[^/]+", re.I)


def sitemap_job_urls(website: str, f: Fetcher, limit: int = 400) -> list[str]:
    base = normalise_site(website)
    if not base:
        return []
    found: list[str] = []
    queue = [urljoin(base, "/sitemap.xml"), urljoin(base, "/sitemap_index.xml")]
    seen = set()
    while queue and len(found) < limit:
        sm = queue.pop(0)
        if sm in seen:
            continue
        seen.add(sm)
        r = f.get(sm)
        if not r.ok:
            continue
        locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", r.text)
        for loc in locs:
            if loc.endswith(".xml") and len(seen) < 12:
                queue.append(loc)
            elif JOB_URL_RE.search(urlparse(loc).path):
                found.append(loc)
    return found[:limit]


def scrape_careers_page(careers_url: str, f: Fetcher) -> list[dict]:
    """Last-resort extraction of job links from a company-hosted careers page."""
    r = f.get(careers_url)
    if not r.ok:
        return []
    out, seen = [], set()
    for href in links(r.text, r.url):
        p = urlparse(href)
        if not JOB_URL_RE.search(p.path):
            continue
        if href in seen or p.path.rstrip("/") in {"/jobs", "/careers"}:
            continue
        seen.add(href)
        out.append({"url": href, "application_url": href, "title": "",
                    "location": "", "ats_provider": "company_site", "needs_detail": True})
    return out[:200]
