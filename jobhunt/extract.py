"""Structured-data extraction from arbitrary careers/job pages."""

from __future__ import annotations

import json
import re
from html import unescape
from typing import Any

SCRIPT_LD = re.compile(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.S | re.I)
NEXT_DATA = re.compile(r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>', re.S | re.I)
NUXT_DATA = re.compile(r'window\.__NUXT__\s*=\s*(\{.*?\});?\s*</script>', re.S)
APOLLO = re.compile(r'window\.__APOLLO_STATE__\s*=\s*(\{.*?\});?\s*</script>', re.S)
TAG = re.compile(r"<[^>]+>")
STYLE_SCRIPT = re.compile(r"<(script|style|noscript)[^>]*>.*?</\1>", re.S | re.I)
BR = re.compile(r"<(br|/p|/li|/div|/h\d)\s*/?>", re.I)


def html_to_text(html: str, limit: int = 40000) -> str:
    if not html:
        return ""
    s = STYLE_SCRIPT.sub(" ", html)
    s = BR.sub("\n", s)
    s = TAG.sub(" ", s)
    s = unescape(s)
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()[:limit]


def json_ld_blocks(html: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for raw in SCRIPT_LD.findall(html or ""):
        raw = raw.strip()
        # Tolerate trailing commas / concatenated objects.
        for candidate in (raw, raw.rstrip(";")):
            try:
                data = json.loads(candidate)
            except ValueError:
                continue
            if isinstance(data, list):
                out.extend(d for d in data if isinstance(d, dict))
            elif isinstance(data, dict):
                if "@graph" in data and isinstance(data["@graph"], list):
                    out.extend(d for d in data["@graph"] if isinstance(d, dict))
                else:
                    out.append(data)
            break
    return out


def job_posting_ld(html: str) -> dict[str, Any] | None:
    for block in json_ld_blocks(html):
        t = block.get("@type")
        types = t if isinstance(t, list) else [t]
        if any(str(x).lower() == "jobposting" for x in types if x):
            return block
    return None


def parse_job_posting_ld(ld: dict[str, Any]) -> dict[str, Any]:
    """Map schema.org JobPosting -> our field names."""
    def _txt(v):
        if isinstance(v, dict):
            return v.get("name") or v.get("value") or ""
        if isinstance(v, list):
            return ", ".join(filter(None, (_txt(x) for x in v)))
        return str(v or "")

    loc = ld.get("jobLocation")
    location = ""
    if isinstance(loc, list) and loc:
        loc = loc[0]
    if isinstance(loc, dict):
        addr = loc.get("address") or {}
        if isinstance(addr, dict):
            location = ", ".join(filter(None, [addr.get("addressLocality"),
                                               addr.get("addressRegion"),
                                               addr.get("addressCountry") if not addr.get("addressRegion") else None]))
        else:
            location = _txt(addr)
    remote_type = ld.get("jobLocationType") or ""

    salary_min = salary_max = None
    salary_text = ""
    bs = ld.get("baseSalary")
    if isinstance(bs, dict):
        val = bs.get("value")
        if isinstance(val, dict):
            unit = (val.get("unitText") or "").lower()
            mn, mx = val.get("minValue"), val.get("maxValue")
            single = val.get("value")
            try:
                mn = float(mn) if mn is not None else (float(single) if single is not None else None)
                mx = float(mx) if mx is not None else mn
            except (TypeError, ValueError):
                mn = mx = None
            if mn is not None:
                mult = {"hour": 2080, "day": 260, "week": 52, "month": 12, "year": 1}.get(unit, 1)
                salary_min, salary_max = int(mn * mult), int((mx or mn) * mult)
                salary_text = f"{ld.get('baseSalary',{}).get('currency','USD')} {mn:,.0f}-{(mx or mn):,.0f} per {unit or 'year'}"

    from .extract import html_to_text as _h
    return {
        "title": _txt(ld.get("title")),
        "company": _txt(ld.get("hiringOrganization")),
        "location": location or ("Remote" if "telecommute" in str(remote_type).lower() else ""),
        "remote_hint": "remote" if "telecommute" in str(remote_type).lower() else "",
        "description": _h(ld.get("description") or ""),
        "date_posted": _txt(ld.get("datePosted"))[:10],
        "valid_through": _txt(ld.get("validThrough"))[:10],
        "employment_type_raw": _txt(ld.get("employmentType")),
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_text": salary_text,
        "education_required": _txt(ld.get("educationRequirements")),
        "experience_raw": _txt(ld.get("experienceRequirements")),
        "official_job_url": _txt(ld.get("url")),
        "direct_apply": ld.get("directApply"),
    }


def next_data(html: str) -> dict | None:
    m = NEXT_DATA.search(html or "")
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except ValueError:
        return None


def embedded_state(html: str) -> dict | None:
    for rx in (NUXT_DATA, APOLLO):
        m = rx.search(html or "")
        if m:
            try:
                return json.loads(m.group(1))
            except ValueError:
                continue
    return None


def walk(obj: Any, pred) -> list[Any]:
    """Depth-first collect of nodes matching pred."""
    found = []
    stack = [obj]
    while stack:
        node = stack.pop()
        if pred(node):
            found.append(node)
        if isinstance(node, dict):
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return found


LINK_RE = re.compile(r'href=["\']([^"\'#]+)["\']', re.I)


def links(html: str, base: str = "") -> list[str]:
    from urllib.parse import urljoin
    out = []
    for href in LINK_RE.findall(html or ""):
        if href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        out.append(urljoin(base, href) if base else href)
    return out
