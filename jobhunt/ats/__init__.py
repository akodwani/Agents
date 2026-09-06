"""Applicant-tracking-system adapters.

Each adapter exposes:
    PROVIDER      : str
    detect(url)   -> slug | None
    board_url(slug) -> str
    list_jobs(slug, fetcher) -> list[dict]   # normalised posting stubs

Every endpoint used here is the public, unauthenticated job-board feed that the
ATS itself serves to anonymous browsers.
"""

from __future__ import annotations

import re
from typing import Callable
from urllib.parse import urlparse

from ..fetch import Fetcher
from ..extract import html_to_text, job_posting_ld, links, next_data, parse_job_posting_ld, walk


def _txt(v) -> str:
    return (v or "").strip() if isinstance(v, str) else ""


# ---------------------------------------------------------------------------
# Greenhouse
# ---------------------------------------------------------------------------
class Greenhouse:
    PROVIDER = "greenhouse"
    PATTERNS = [r"boards\.greenhouse\.io/(?:embed/job_board\?for=)?([a-z0-9_-]+)",
                r"job-boards\.greenhouse\.io/([a-z0-9_-]+)",
                r"boards\.eu\.greenhouse\.io/([a-z0-9_-]+)",
                r"greenhouse\.io/embed/job_board\?for=([a-z0-9_-]+)"]

    @classmethod
    def detect(cls, url: str) -> str | None:
        for p in cls.PATTERNS:
            m = re.search(p, url or "", re.I)
            if m and m.group(1) not in {"embed", "jobs"}:
                return m.group(1)
        return None

    @staticmethod
    def board_url(slug: str) -> str:
        return f"https://job-boards.greenhouse.io/{slug}"

    @staticmethod
    def list_jobs(slug: str, f: Fetcher) -> list[dict]:
        data, resp = f.get_json(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true")
        if not data:
            return []
        out = []
        for j in data.get("jobs", []):
            out.append({
                "title": j.get("title", ""),
                "location": (j.get("location") or {}).get("name", ""),
                "url": j.get("absolute_url", ""),
                "application_url": j.get("absolute_url", ""),
                "date_posted": (j.get("updated_at") or "")[:10],
                "description": html_to_text(j.get("content", "")),
                "ats_provider": "greenhouse",
                "external_id": str(j.get("id", "")),
                "departments": ", ".join(d.get("name", "") for d in j.get("departments", [])),
            })
        return out


# ---------------------------------------------------------------------------
# Lever
# ---------------------------------------------------------------------------
class Lever:
    PROVIDER = "lever"

    @classmethod
    def detect(cls, url: str) -> str | None:
        m = re.search(r"jobs\.(?:eu\.)?lever\.co/([a-z0-9_.-]+)", url or "", re.I)
        return m.group(1) if m else None

    @staticmethod
    def board_url(slug: str) -> str:
        return f"https://jobs.lever.co/{slug}"

    @staticmethod
    def list_jobs(slug: str, f: Fetcher) -> list[dict]:
        data, _ = f.get_json(f"https://api.lever.co/v0/postings/{slug}?mode=json")
        if not isinstance(data, list):
            return []
        out = []
        for j in data:
            cats = j.get("categories") or {}
            out.append({
                "title": j.get("text", ""),
                "location": cats.get("location", ""),
                "url": j.get("hostedUrl", ""),
                "application_url": j.get("applyUrl") or j.get("hostedUrl", ""),
                "date_posted": "",
                "description": html_to_text(j.get("descriptionPlain") or j.get("description", "")) + " " +
                               " ".join(html_to_text(s.get("text", "")) for s in (j.get("lists") or [])),
                "ats_provider": "lever",
                "external_id": j.get("id", ""),
                "employment_type_raw": cats.get("commitment", ""),
                "departments": cats.get("team", ""),
            })
        return out


# ---------------------------------------------------------------------------
# Ashby
# ---------------------------------------------------------------------------
class Ashby:
    PROVIDER = "ashby"

    @classmethod
    def detect(cls, url: str) -> str | None:
        m = re.search(r"jobs\.ashbyhq\.com/([a-zA-Z0-9_.-]+)", url or "")
        return m.group(1) if m else None

    @staticmethod
    def board_url(slug: str) -> str:
        return f"https://jobs.ashbyhq.com/{slug}"

    @staticmethod
    def list_jobs(slug: str, f: Fetcher) -> list[dict]:
        data, _ = f.get_json(
            f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true")
        if not data:
            return []
        out = []
        for j in data.get("jobs", []):
            comp = j.get("compensation") or {}
            summary = ""
            if isinstance(comp, dict):
                summary = comp.get("compensationTierSummary") or ""
            out.append({
                "title": j.get("title", ""),
                "location": j.get("location", "") or (j.get("address") or {}).get("postalAddress", {}).get("addressLocality", ""),
                "url": j.get("jobUrl", ""),
                "application_url": j.get("applyUrl") or j.get("jobUrl", ""),
                "date_posted": (j.get("publishedAt") or "")[:10],
                "description": html_to_text(j.get("descriptionHtml") or j.get("descriptionPlain", "")),
                "ats_provider": "ashby",
                "external_id": j.get("id", ""),
                "employment_type_raw": j.get("employmentType", ""),
                "salary_text": summary,
                "departments": j.get("department", ""),
                "remote_hint": "remote" if j.get("isRemote") else "",
            })
        return out


# ---------------------------------------------------------------------------
# Workable
# ---------------------------------------------------------------------------
class Workable:
    PROVIDER = "workable"

    @classmethod
    def detect(cls, url: str) -> str | None:
        m = re.search(r"apply\.workable\.com/([a-z0-9_-]+)", url or "", re.I)
        return m.group(1) if m else None

    @staticmethod
    def board_url(slug: str) -> str:
        return f"https://apply.workable.com/{slug}/"

    @staticmethod
    def list_jobs(slug: str, f: Fetcher) -> list[dict]:
        data, _ = f.get_json(
            f"https://apply.workable.com/api/v1/widget/accounts/{slug}?details=true")
        jobs = (data or {}).get("jobs", []) if isinstance(data, dict) else []
        out = []
        for j in jobs:
            out.append({
                "title": j.get("title", ""),
                "location": ", ".join(filter(None, [j.get("city"), j.get("state"), j.get("country")])),
                "url": j.get("url") or j.get("application_url", ""),
                "application_url": j.get("application_url") or j.get("url", ""),
                "date_posted": (j.get("published_on") or "")[:10],
                "description": html_to_text((j.get("description") or "") + " " + (j.get("requirements") or "")),
                "ats_provider": "workable",
                "external_id": j.get("shortcode", ""),
                "employment_type_raw": j.get("employment_type", ""),
                "departments": j.get("department", ""),
                "remote_hint": "remote" if j.get("telecommuting") else "",
            })
        return out


# ---------------------------------------------------------------------------
# SmartRecruiters
# ---------------------------------------------------------------------------
class SmartRecruiters:
    PROVIDER = "smartrecruiters"

    @classmethod
    def detect(cls, url: str) -> str | None:
        m = re.search(r"(?:jobs|careers)\.smartrecruiters\.com/([A-Za-z0-9_-]+)", url or "")
        return m.group(1) if m else None

    @staticmethod
    def board_url(slug: str) -> str:
        return f"https://jobs.smartrecruiters.com/{slug}"

    @staticmethod
    def list_jobs(slug: str, f: Fetcher) -> list[dict]:
        out, offset = [], 0
        while offset < 400:
            data, _ = f.get_json(
                f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=100&offset={offset}")
            if not data or not data.get("content"):
                break
            for j in data["content"]:
                loc = j.get("location") or {}
                out.append({
                    "title": j.get("name", ""),
                    "location": ", ".join(filter(None, [loc.get("city"), loc.get("region"), loc.get("country")])),
                    "url": j.get("ref", "") or f"https://jobs.smartrecruiters.com/{slug}/{j.get('id','')}",
                    "application_url": f"https://jobs.smartrecruiters.com/{slug}/{j.get('id','')}",
                    "date_posted": (j.get("releasedDate") or "")[:10],
                    "description": "",
                    "ats_provider": "smartrecruiters",
                    "external_id": j.get("id", ""),
                    "employment_type_raw": (j.get("typeOfEmployment") or {}).get("label", ""),
                    "departments": (j.get("department") or {}).get("label", ""),
                    "remote_hint": "remote" if loc.get("remote") else "",
                })
            offset += 100
            if len(data["content"]) < 100:
                break
        return out


# ---------------------------------------------------------------------------
# Recruitee / Breezy / BambooHR / Teamtailor / Personio-style JSON boards
# ---------------------------------------------------------------------------
class Recruitee:
    PROVIDER = "recruitee"

    @classmethod
    def detect(cls, url: str) -> str | None:
        m = re.search(r"([a-z0-9_-]+)\.recruitee\.com", url or "", re.I)
        return m.group(1) if m else None

    @staticmethod
    def board_url(slug: str) -> str:
        return f"https://{slug}.recruitee.com/"

    @staticmethod
    def list_jobs(slug: str, f: Fetcher) -> list[dict]:
        data, _ = f.get_json(f"https://{slug}.recruitee.com/api/offers/")
        offers = (data or {}).get("offers", []) if isinstance(data, dict) else []
        return [{
            "title": o.get("title", ""),
            "location": ", ".join(filter(None, [o.get("city"), o.get("state_code"), o.get("country")])),
            "url": o.get("careers_url") or o.get("careers_apply_url", ""),
            "application_url": o.get("careers_apply_url") or o.get("careers_url", ""),
            "date_posted": (o.get("published_at") or "")[:10],
            "description": html_to_text((o.get("description") or "") + " " + (o.get("requirements") or "")),
            "ats_provider": "recruitee",
            "external_id": str(o.get("id", "")),
            "employment_type_raw": o.get("employment_type_code", ""),
            "departments": o.get("department", ""),
            "remote_hint": "remote" if o.get("remote") else "",
        } for o in offers]


class Breezy:
    PROVIDER = "breezy"

    @classmethod
    def detect(cls, url: str) -> str | None:
        m = re.search(r"([a-z0-9_-]+)\.breezy\.hr", url or "", re.I)
        return m.group(1) if m else None

    @staticmethod
    def board_url(slug: str) -> str:
        return f"https://{slug}.breezy.hr/"

    @staticmethod
    def list_jobs(slug: str, f: Fetcher) -> list[dict]:
        data, _ = f.get_json(f"https://{slug}.breezy.hr/json")
        if not isinstance(data, list):
            return []
        return [{
            "title": j.get("name", ""),
            "location": ((j.get("location") or {}).get("name")
                         or ", ".join(filter(None, [((j.get("location") or {}).get("city") or {}).get("name", ""),
                                                    ((j.get("location") or {}).get("country") or {}).get("name", "")]))),
            "url": j.get("url") or f"https://{slug}.breezy.hr/p/{j.get('id','')}",
            "application_url": j.get("url", ""),
            "date_posted": (j.get("published_date") or "")[:10],
            "description": html_to_text(j.get("description", "")),
            "ats_provider": "breezy",
            "external_id": j.get("id", ""),
            "employment_type_raw": (j.get("type") or {}).get("name", ""),
            "departments": (j.get("department") or {}).get("name", ""),
        } for j in data]


class BambooHR:
    PROVIDER = "bamboohr"

    @classmethod
    def detect(cls, url: str) -> str | None:
        m = re.search(r"([a-z0-9_-]+)\.bamboohr\.com", url or "", re.I)
        return m.group(1) if m else None

    @staticmethod
    def board_url(slug: str) -> str:
        return f"https://{slug}.bamboohr.com/careers"

    @staticmethod
    def list_jobs(slug: str, f: Fetcher) -> list[dict]:
        data, _ = f.get_json(f"https://{slug}.bamboohr.com/careers/list")
        results = (data or {}).get("result", []) if isinstance(data, dict) else []
        out = []
        for j in results:
            loc = j.get("location") or {}
            out.append({
                "title": j.get("jobOpeningName", ""),
                "location": ", ".join(filter(None, [loc.get("city"), loc.get("state"), loc.get("country")]))
                            or ("Remote" if j.get("isRemote") else ""),
                "url": f"https://{slug}.bamboohr.com/careers/{j.get('id','')}",
                "application_url": f"https://{slug}.bamboohr.com/careers/{j.get('id','')}",
                "date_posted": (j.get("datePosted") or "")[:10],
                "description": "",
                "ats_provider": "bamboohr",
                "external_id": str(j.get("id", "")),
                "employment_type_raw": j.get("employmentStatusLabel", ""),
                "departments": j.get("departmentLabel", ""),
                "remote_hint": "remote" if j.get("isRemote") else "",
            })
        return out


class Teamtailor:
    PROVIDER = "teamtailor"

    @classmethod
    def detect(cls, url: str) -> str | None:
        m = re.search(r"([a-z0-9_-]+)\.teamtailor\.com", url or "", re.I)
        return m.group(1) if m else None

    @staticmethod
    def board_url(slug: str) -> str:
        return f"https://{slug}.teamtailor.com/jobs"

    @staticmethod
    def list_jobs(slug: str, f: Fetcher) -> list[dict]:
        r = f.get(f"https://{slug}.teamtailor.com/jobs")
        if not r.ok:
            return []
        out, seen = [], set()
        for href in links(r.text, r.url):
            if "/jobs/" in href and href not in seen:
                seen.add(href)
                out.append({"title": "", "location": "", "url": href,
                            "application_url": href, "ats_provider": "teamtailor",
                            "needs_detail": True})
        return out


# ---------------------------------------------------------------------------
# HTML-only boards (Jobvite, iCIMS, JazzHR, Pinpoint, Comeet, Rippling, Gem)
# ---------------------------------------------------------------------------
class _HtmlBoard:
    PROVIDER = "generic"
    HOST_RE = ""
    LINK_RE = ""
    URL_TMPL = ""

    @classmethod
    def detect(cls, url: str) -> str | None:
        m = re.search(cls.HOST_RE, url or "", re.I)
        return m.group(1) if m else None

    @classmethod
    def board_url(cls, slug: str) -> str:
        return cls.URL_TMPL.format(slug=slug)

    @classmethod
    def list_jobs(cls, slug: str, f: Fetcher) -> list[dict]:
        r = f.get(cls.board_url(slug))
        if not r.ok:
            return []
        out, seen = [], set()
        for href in links(r.text, r.url):
            if re.search(cls.LINK_RE, href) and href not in seen:
                seen.add(href)
                out.append({"title": "", "location": "", "url": href, "application_url": href,
                            "ats_provider": cls.PROVIDER, "needs_detail": True})
        # Next.js-powered boards often carry the whole list in __NEXT_DATA__.
        nd = next_data(r.text)
        if nd:
            for node in walk(nd, lambda n: isinstance(n, dict) and
                             {"title"} <= set(n) and any(k in n for k in ("url", "slug", "id"))):
                title = _txt(node.get("title"))
                if not title:
                    continue
                url = _txt(node.get("url")) or f"{r.url.rstrip('/')}/{_txt(node.get('slug')) or node.get('id')}"
                if url in seen:
                    continue
                seen.add(url)
                out.append({"title": title,
                            "location": _txt(node.get("location")) or _txt(node.get("locationName")),
                            "url": url, "application_url": url,
                            "ats_provider": cls.PROVIDER, "needs_detail": not node.get("description")})
        return out


class Jobvite(_HtmlBoard):
    PROVIDER = "jobvite"
    HOST_RE = r"jobs\.jobvite\.com/([a-z0-9_-]+)"
    LINK_RE = r"/job/|/jobs/"
    URL_TMPL = "https://jobs.jobvite.com/{slug}/search"


class ICIMS(_HtmlBoard):
    PROVIDER = "icims"
    HOST_RE = r"(?:careers-)?([a-z0-9_-]+)\.icims\.com"
    LINK_RE = r"/jobs/\d+/"
    URL_TMPL = "https://careers-{slug}.icims.com/jobs/search?ss=1&searchRelation=keyword_all"


class JazzHR(_HtmlBoard):
    PROVIDER = "jazzhr"
    HOST_RE = r"([a-z0-9_-]+)\.applytojob\.com"
    LINK_RE = r"/apply/[A-Za-z0-9]+"
    URL_TMPL = "https://{slug}.applytojob.com/apply"


class Pinpoint(_HtmlBoard):
    PROVIDER = "pinpoint"
    HOST_RE = r"([a-z0-9_-]+)\.pinpointhq\.com"
    LINK_RE = r"/postings/"
    URL_TMPL = "https://{slug}.pinpointhq.com/"


class Comeet(_HtmlBoard):
    PROVIDER = "comeet"
    HOST_RE = r"comeet\.com/jobs/([a-z0-9_-]+)"
    LINK_RE = r"/jobs/[^/]+/[^/]+/"
    URL_TMPL = "https://www.comeet.com/jobs/{slug}"


class Rippling(_HtmlBoard):
    PROVIDER = "rippling"
    HOST_RE = r"ats\.rippling\.com/([a-z0-9_-]+)"
    LINK_RE = r"/jobs/[a-f0-9-]+"
    URL_TMPL = "https://ats.rippling.com/{slug}/jobs"


class Gem(_HtmlBoard):
    PROVIDER = "gem"
    HOST_RE = r"jobs\.gem\.com/([a-z0-9_-]+)"
    LINK_RE = r"/jobs?/"
    URL_TMPL = "https://jobs.gem.com/{slug}"


# ---------------------------------------------------------------------------
# Workday (public cxs endpoint)
# ---------------------------------------------------------------------------
class Workday:
    PROVIDER = "workday"

    @classmethod
    def detect(cls, url: str) -> str | None:
        m = re.search(r"https?://([a-z0-9-]+)\.(wd\d+)\.myworkdayjobs\.com/(?:[a-z]{2}-[A-Z]{2}/)?([^/?#]+)",
                      url or "", re.I)
        return "|".join(m.groups()) if m else None

    @staticmethod
    def board_url(slug: str) -> str:
        tenant, dc, site = slug.split("|")
        return f"https://{tenant}.{dc}.myworkdayjobs.com/{site}"

    @staticmethod
    def list_jobs(slug: str, f: Fetcher, search: str = "") -> list[dict]:
        try:
            tenant, dc, site = slug.split("|")
        except ValueError:
            return []
        api = f"https://{tenant}.{dc}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
        out, offset = [], 0
        while offset < 200:
            try:
                resp = f.session.post(api, json={"appliedFacets": {}, "limit": 20,
                                                 "offset": offset, "searchText": search},
                                      timeout=f.timeout,
                                      headers={"Content-Type": "application/json",
                                               "Accept": "application/json"})
            except Exception:
                break
            if resp.status_code != 200:
                break
            data = resp.json()
            posts = data.get("jobPostings", [])
            for j in posts:
                path = j.get("externalPath", "")
                out.append({
                    "title": j.get("title", ""),
                    "location": j.get("locationsText", ""),
                    "url": f"https://{tenant}.{dc}.myworkdayjobs.com/{site}{path}",
                    "application_url": f"https://{tenant}.{dc}.myworkdayjobs.com/{site}{path}",
                    "date_posted": j.get("postedOn", ""),
                    "description": "",
                    "ats_provider": "workday",
                    "external_id": j.get("bulletFields", [""])[0] if j.get("bulletFields") else "",
                    "needs_detail": True,
                })
            if len(posts) < 20:
                break
            offset += 20
        return out


ADAPTERS = [Greenhouse, Lever, Ashby, Workable, SmartRecruiters, Recruitee, Breezy,
            BambooHR, Teamtailor, Jobvite, ICIMS, JazzHR, Pinpoint, Comeet,
            Rippling, Gem, Workday]

BY_NAME = {a.PROVIDER: a for a in ADAPTERS}


def detect_ats(url: str) -> tuple[str, str] | tuple[None, None]:
    for a in ADAPTERS:
        slug = a.detect(url)
        if slug:
            return a.PROVIDER, slug
    return None, None


def list_jobs(provider: str, slug: str, fetcher: Fetcher) -> list[dict]:
    a = BY_NAME.get(provider)
    return a.list_jobs(slug, fetcher) if a else []
