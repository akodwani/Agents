"""Raw posting -> normalised, deduplicated, scored row in the database."""

from __future__ import annotations

import difflib
import json
import re
import sqlite3
from typing import Any, Iterable

from .config.taxonomy import (FAMILIES, LEARNED_PATH, load_learned_titles,
                              save_learned_titles)
from .db import now, upsert
from .normalize import (classify_family, clean, content_hash, detect_remote,
                        drain_estimate, employment_type, estimate_hours,
                        norm_company, norm_location, norm_title, parse_experience,
                        parse_salary, remote_employable_from_ny, scan_flags)
from .score import score_job

# Source ranking: which URL we would rather send the candidate to.
URL_RANK = {
    "greenhouse": 10, "lever": 10, "ashby": 10, "workable": 9, "smartrecruiters": 9,
    "workday": 9, "icims": 8, "jobvite": 8, "bamboohr": 8, "jazzhr": 8,
    "teamtailor": 8, "recruitee": 8, "breezy": 8, "pinpoint": 8, "comeet": 8,
    "rippling": 8, "gem": 8, "company_site": 7, "employer_careers": 7,
    "aggregator": 2, "websearch": 2, "unknown": 1,
}

AGGREGATOR_HOSTS = re.compile(
    r"(linkedin\.com|indeed\.com|ziprecruiter\.com|glassdoor\.com|simplyhired|"
    r"jobs\.google|talent\.com|jooble|adzuna|builtin\.com|wellfound\.com|"
    r"angel\.co|otta\.com|welcometothejungle|dice\.com|monster\.com|"
    r"entertainmentcareers\.net|mediabistro|productionhub|staffmeup|"
    r"remoteok|weworkremotely|flexjobs|idealist\.org|mandy\.com)", re.I)

SEARCH_ENGINE_HOSTS = re.compile(r"(google\.[a-z.]+/search|bing\.com/search|duckduckgo\.com/\?q)", re.I)


def is_aggregator(url: str) -> bool:
    return bool(AGGREGATOR_HOSTS.search(url or ""))


def valid_application_url(url: str) -> bool:
    """Never let a search-engine URL become an application link."""
    return bool(url) and url.startswith("http") and not SEARCH_ENGINE_HOSTS.search(url)


def make_job_id(company: str, title: str, location: str, url: str) -> str:
    return content_hash(norm_company(company), norm_title(title), norm_location(location), url)[:20]


def dedupe_key(company: str, title: str, location: str) -> str:
    return f"{norm_company(company)}|{norm_title(title)}|{norm_location(location)}"


def build_row(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalise one raw posting stub into a full jobs-table row (unscored)."""
    title = clean(raw.get("title"))
    company = clean(raw.get("company"))
    location = clean(raw.get("location"))
    desc = clean(raw.get("description"))
    resp = clean(raw.get("responsibilities"))
    quals = clean(raw.get("qualifications"))
    blob = " ".join(filter(None, [title, desc, resp, quals, clean(raw.get("salary_text"))]))

    family, film_rel, _ = classify_family(title, blob)
    et = employment_type(blob, raw.get("employment_type_raw", ""))
    remote = raw.get("remote_status") or (
        "remote" if raw.get("remote_hint") == "remote" else detect_remote(location, blob))

    smin, smax = raw.get("salary_min"), raw.get("salary_max")
    stext = raw.get("salary_text") or ""
    if smin is None:
        smin, smax, parsed_text = parse_salary(blob)
        stext = stext or parsed_text
    if not stext:
        stext = "UNKNOWN"

    years, years_raw = parse_experience(blob)
    reds, red_w, greens, green_w = scan_flags(blob)
    hours = estimate_hours(title, company, blob, family, et)

    url = raw.get("url") or raw.get("official_job_url") or ""
    app_url = raw.get("application_url") or url
    if not valid_application_url(app_url):
        app_url = url if valid_application_url(url) else ""

    ats = raw.get("ats_provider") or "unknown"

    row = {
        "job_id": make_job_id(company, title, location, url or app_url),
        "title": title, "company": company, "location": location or "UNKNOWN",
        "remote_status": remote, "employment_type": et,
        "salary_min": smin, "salary_max": smax, "salary_text": stext,
        "estimated_hours": hours.text, "hours_confidence": hours.confidence,
        "schedule_flexibility": "; ".join(greens) or "UNKNOWN",
        "experience_required": years_raw, "education_required": clean(raw.get("education_required")) or "UNKNOWN",
        "description": desc[:12000], "responsibilities": resp[:4000], "qualifications": quals[:4000],
        "date_posted": raw.get("date_posted") or "UNKNOWN",
        "valid_through": raw.get("valid_through") or "UNKNOWN",
        "source_discovered_from": raw.get("source_discovered_from") or ats,
        "official_job_url": url, "application_url": app_url, "ats_provider": ats,
        "verification_status": raw.get("verification_status") or "UNCERTAIN",
        "verification_timestamp": raw.get("verification_timestamp") or "",
        "verification_evidence": raw.get("verification_evidence") or "",
        "film_relevance": raw.get("film_relevance") or film_rel,
        "family": family,
        "mental_drain_estimate": drain_estimate(hours, red_w, family),
        "red_flags": json.dumps(reds), "green_flags": json.dumps(greens),
        "notes": clean(raw.get("notes")),
        "content_hash": content_hash(title, company, desc[:4000]),
        "raw_snapshot": (raw.get("raw_snapshot") or desc)[:4000],
        "dedupe_key": dedupe_key(company, title, location),
        "first_seen": now(), "last_seen": now(),
        "_hours": hours, "_reds": reds, "_red_w": red_w, "_greens": greens, "_green_w": green_w,
        "_years": years, "_blob": blob,
        "_remote_ny_ok": remote_employable_from_ny(blob),
    }
    return row


def score_row(row: dict[str, Any]) -> dict[str, Any]:
    job = dict(row)
    job["years_required"] = row.get("_years")
    res = score_job(job, row["_hours"], row["_reds"], row["_red_w"], row["_greens"], row["_green_w"])

    # Remote roles that explicitly exclude New York are not usable.
    if row["remote_status"] == "remote" and row.get("_remote_ny_ok") is False:
        res.total = max(0.0, res.total - 25)
        res.rationale.append("remote work appears restricted to other states (-25)")
        res.tier = "REJECT" if res.total < 40 else res.tier

    out = dict(row)
    out["score"] = res.total
    out["acting_schedule_compatibility"] = res.acting
    out["candidate_accessibility"] = res.accessibility_label
    out["tier"] = res.tier
    out["score_breakdown"] = json.dumps(res.as_dict())
    return {k: v for k, v in out.items() if not k.startswith("_")}


# ------------------------------------------------------------------ dedupe --
def find_duplicate(conn: sqlite3.Connection, row: dict[str, Any]) -> str | None:
    cur = conn.execute("SELECT job_id, application_url, official_job_url, description, ats_provider "
                       "FROM jobs WHERE dedupe_key=?", (row["dedupe_key"],))
    for other in cur.fetchall():
        if other["job_id"] != row["job_id"]:
            return other["job_id"]
    # URL identity
    for col in ("application_url", "official_job_url"):
        if row.get(col):
            r = conn.execute(f"SELECT job_id FROM jobs WHERE {col}=? AND job_id<>?",
                             (row[col], row["job_id"])).fetchone()
            if r:
                return r["job_id"]
    # Description similarity within the same company
    if len(row.get("description") or "") > 600:
        cur = conn.execute("SELECT job_id, description FROM jobs WHERE company=? AND job_id<>?",
                           (row["company"], row["job_id"]))
        for other in cur.fetchall():
            if not other["description"]:
                continue
            ratio = difflib.SequenceMatcher(
                None, row["description"][:2500], other["description"][:2500]).quick_ratio()
            if ratio > 0.93:
                return other["job_id"]
    return None


def better_url(a: dict, b: sqlite3.Row) -> bool:
    """Is `a` (new) a better canonical source than `b` (stored)?"""
    return URL_RANK.get(a.get("ats_provider", "unknown"), 1) > URL_RANK.get(b["ats_provider"] or "unknown", 1)


def store(conn: sqlite3.Connection, raw: dict[str, Any]) -> tuple[str, str]:
    """Normalise, score, dedupe and persist. Returns (job_id, action)."""
    row = score_row(build_row(raw))
    if not row["title"] or not row["company"]:
        return "", "skipped_incomplete"

    dup = find_duplicate(conn, row)
    if dup:
        stored = conn.execute("SELECT * FROM jobs WHERE job_id=?", (dup,)).fetchone()
        if better_url(row, stored):
            merged = dict(row)
            merged["job_id"] = dup
            merged["first_seen"] = stored["first_seen"]
            merged["notes"] = clean((stored["notes"] or "") + " | merged duplicate")
            upsert(conn, "jobs", merged, "job_id")
            conn.commit()
            return dup, "merged_upgraded"
        conn.execute("UPDATE jobs SET last_seen=? WHERE job_id=?", (now(), dup))
        conn.commit()
        return dup, "duplicate"

    upsert(conn, "jobs", row, "job_id")
    conn.commit()
    return row["job_id"], "inserted"


# --------------------------------------------------------- title learning --
GENERIC_WORDS = re.compile(r"\b(?:i{1,3}|senior|junior|jr|sr|nyc|new york|remote|hybrid|"
                           r"full[- ]time|part[- ]time|temp|contract|\d{4})\b", re.I)


def learn_titles(conn: sqlite3.Connection, min_score: float = 62.0) -> list[str]:
    """Feed unexpected but high-scoring titles back into the taxonomy."""
    known = set()
    for fam in FAMILIES.values():
        known.update(fam["titles"])
    known.update(load_learned_titles())

    new: list[str] = []
    for r in conn.execute("SELECT title FROM jobs WHERE score >= ?", (min_score,)):
        t = GENERIC_WORDS.sub(" ", (r["title"] or "").lower())
        t = re.sub(r"[^a-z ]+", " ", t)
        t = re.sub(r"\s+", " ", t).strip()
        if not t or len(t) < 6:
            continue
        if any(k in t for k in known):
            continue
        new.append(t)
    if new:
        save_learned_titles(load_learned_titles() + new)
    return sorted(set(new))
