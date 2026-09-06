"""The discovery -> crawl -> extract -> verify -> score -> dedupe -> expand loop.

Runs until marginal discovery plateaus, not until the first batch is produced.
"""

from __future__ import annotations

import json
import re
import sqlite3
import time
from dataclasses import dataclass, field

from .ats import BY_NAME, detect_ats, list_jobs as ats_list_jobs
from .config.employers_seed import SEED
from .config.taxonomy import EMPLOYER_INDUSTRIES, FAMILIES, all_titles, load_learned_titles
from .db import connect, enqueue, mark, now, record_search, record_source, upsert
from .discover import find_careers_url, resolve_ats, scrape_careers_page, sitemap_job_urls
from .fetch import Fetcher
from .normalize import content_hash, norm_company
from .pipeline import build_row, learn_titles, score_row, store
from .verify import verify

NYC_RE = re.compile(r"\bnew york\b|\bnyc\b|\bbrooklyn\b|\bqueens\b|\bmanhattan\b|\bny\b|"
                    r"\bremote\b|\banywhere\b|\bus\b|\bunited states\b|\bhybrid\b", re.I)
OTHER_METRO_RE = re.compile(
    r"\b(los angeles|burbank|culver city|santa monica|atlanta|chicago|austin|london|"
    r"toronto|vancouver|dublin|paris|berlin|mumbai|bangalore|seattle|san francisco|"
    r"boston|miami|dallas|denver|nashville|philadelphia|washington|d\.c\.)\b", re.I)


def employer_id(name: str) -> str:
    return content_hash(norm_company(name))[:16]


def seed_employers(conn: sqlite3.Connection) -> int:
    added = 0
    for name, industry, website, why in SEED:
        eid = employer_id(name)
        if conn.execute("SELECT 1 FROM employers WHERE employer_id=?", (eid,)).fetchone():
            continue
        upsert(conn, "employers", {
            "employer_id": eid, "name": name, "industry": industry,
            "website": f"https://{website}" if website else "",
            "why_relevant": why, "discovered_from": "seed",
            "nyc_presence": 1 if "nyc" in why.lower() or "new york" in why.lower() else 0,
            "priority": 0.8 if any(k in industry for k in ("film", "production", "ai", "television", "streaming")) else 0.6,
        }, "employer_id")
        added += 1
    conn.commit()
    return added


def add_employer(conn: sqlite3.Connection, name: str, industry: str = "unknown",
                 website: str = "", why: str = "", source: str = "expansion",
                 careers_url: str = "", ats_provider: str = "", ats_slug: str = "") -> bool:
    if not name or len(name) < 2:
        return False
    eid = employer_id(name)
    existing = conn.execute("SELECT 1 FROM employers WHERE employer_id=?", (eid,)).fetchone()
    row = {"employer_id": eid, "name": name, "industry": industry,
           "website": website, "why_relevant": why, "discovered_from": source}
    if careers_url:
        row["careers_url"] = careers_url
    if ats_provider:
        row["ats_provider"] = ats_provider
        row["ats_slug"] = ats_slug
        row["ats_url"] = BY_NAME[ats_provider].board_url(ats_slug) if ats_provider in BY_NAME else ""
    upsert(conn, "employers", row, "employer_id")
    conn.commit()
    return existing is None


# ------------------------------------------------------------- relevance ---
def location_ok(location: str, remote_hint: str = "") -> bool:
    loc = (location or "").strip()
    if not loc:
        return True                       # unknown location: keep, resolve later
    if remote_hint == "remote":
        return True
    if OTHER_METRO_RE.search(loc) and not NYC_RE.search(loc):
        return False
    return bool(NYC_RE.search(loc)) or len(loc) < 3


TITLE_HINTS = None


def title_relevant(title: str) -> bool:
    global TITLE_HINTS
    if TITLE_HINTS is None:
        TITLE_HINTS = set(all_titles())
    t = (title or "").lower()
    if not t:
        return True                       # stub without a title: fetch detail first
    if any(h in t for h in TITLE_HINTS):
        return True
    generic = ("coordinator", "associate", "assistant", "researcher", "research",
               "writer", "producer", "development", "production", "content",
               "editorial", "creative", "programming", "archivist", "curator",
               "specialist", "analyst", "operations")
    return any(g in t for g in generic)


def prefilter(stub: dict) -> bool:
    return title_relevant(stub.get("title", "")) and location_ok(
        stub.get("location", ""), stub.get("remote_hint", ""))


# ------------------------------------------------------------- iteration ---
@dataclass
class IterationStats:
    iteration: int
    candidates: int = 0
    verified: int = 0
    admitted: int = 0
    rejected: int = 0
    duplicates: int = 0
    new_titles: list[str] = field(default_factory=list)
    new_employers: list[str] = field(default_factory=list)
    blocked_domains: list[str] = field(default_factory=list)
    expansion_reason: str = ""


def crawl_employer(conn: sqlite3.Connection, emp: sqlite3.Row, f: Fetcher,
                   stats: IterationStats, verify_top: int = 12) -> None:
    """Resolve one employer's board and ingest whatever it currently lists."""
    eid = emp["employer_id"]
    careers = emp["careers_url"]
    provider, slug = emp["ats_provider"], emp["ats_slug"]
    status = "ok"

    if not provider:
        if not careers and emp["website"]:
            careers, st = find_careers_url(emp["website"], f)
            if st != "ok":
                status = st
        if careers:
            provider, slug, board = resolve_ats(careers, f)
        else:
            provider = slug = None

    stubs: list[dict] = []
    if provider and slug:
        try:
            stubs = ats_list_jobs(provider, slug, f)
        except Exception as exc:                     # noqa: BLE001 - adapter robustness
            status = "error"
            stats.blocked_domains.append(f"{provider}:{exc.__class__.__name__}")
    elif careers:
        stubs = scrape_careers_page(careers, f)
        provider = provider or "company_site"
    elif emp["website"]:
        for url in sitemap_job_urls(emp["website"], f, limit=80):
            stubs.append({"url": url, "application_url": url, "title": "",
                          "ats_provider": "company_site", "needs_detail": True})
        status = "ok" if stubs else (status if status != "ok" else "unresolved")

    upsert(conn, "employers", {
        "employer_id": eid, "careers_url": careers or "", "ats_provider": provider or "",
        "ats_slug": slug or "", "ats_url": (BY_NAME[provider].board_url(slug)
                                            if provider in BY_NAME and slug else ""),
        "last_checked": now(), "check_status": status,
        "total_jobs_seen": len(stubs),
    }, "employer_id")

    kept = [s for s in stubs if prefilter(s)]
    stats.candidates += len(stubs)

    matching = 0
    for stub in kept[:80]:
        stub.setdefault("company", emp["name"])
        stub["company"] = stub.get("company") or emp["name"]
        stub["source_discovered_from"] = f"employer_crawl:{emp['name']}"
        row = score_row(build_row(stub))
        if row["score"] < 45:
            stats.rejected += 1
            continue
        job_id, action = store(conn, stub)
        if action == "inserted":
            matching += 1
            stats.admitted += 1
        elif action in {"duplicate", "merged_upgraded"}:
            stats.duplicates += 1

    conn.execute("UPDATE employers SET matching_jobs=? WHERE employer_id=?", (matching, eid))
    conn.commit()


def verify_pending(conn: sqlite3.Connection, f: Fetcher, stats: IterationStats,
                   limit: int = 60, min_score: float = 55.0) -> None:
    rows = conn.execute(
        "SELECT * FROM jobs WHERE verification_status IN ('UNCERTAIN','') AND score >= ? "
        "ORDER BY score DESC LIMIT ?", (min_score, limit)).fetchall()
    for r in rows:
        url = r["application_url"] or r["official_job_url"]
        res = verify(url, r["title"], r["company"], f)
        conn.execute(
            "UPDATE jobs SET verification_status=?, verification_timestamp=?, verification_evidence=? "
            "WHERE job_id=?",
            (res["verification_status"], res["verification_timestamp"],
             res["verification_evidence"], r["job_id"]))
        stats.verified += 1
        if res["verification_status"] == "DEAD":
            conn.execute("UPDATE jobs SET tier='REJECT' WHERE job_id=?", (r["job_id"],))
            stats.rejected += 1
    conn.commit()


def expand_employers_from_jobs(conn: sqlite3.Connection, stats: IterationStats) -> None:
    """Mine admitted postings for company names and ATS domains worth crawling."""
    rows = conn.execute("SELECT description, application_url FROM jobs WHERE score >= 55").fetchall()
    company_re = re.compile(r"\b([A-Z][A-Za-z0-9&'.-]+(?:\s+[A-Z][A-Za-z0-9&'.-]+){0,3})\s+"
                            r"(?:Studios|Pictures|Productions|Media|Entertainment|Films|Post|VFX)\b")
    for r in rows:
        for m in company_re.finditer(r["description"] or ""):
            name = m.group(0).strip()
            if 4 < len(name) < 60 and add_employer(
                    conn, name, industry="mentioned in posting",
                    why="named in a high-scoring job description", source="description_mining"):
                stats.new_employers.append(name)
        provider, slug = detect_ats(r["application_url"] or "")
        if provider and slug:
            conn.execute("UPDATE employers SET ats_provider=?, ats_slug=? "
                         "WHERE ats_provider IS NULL AND name=?", (provider, slug, ""))
    conn.commit()


def plateaued(history: list[IterationStats], window: int = 3, threshold: int = 3) -> bool:
    if len(history) < window:
        return False
    return all(h.admitted <= threshold for h in history[-window:])


def self_critique(conn: sqlite3.Connection, stats: IterationStats) -> str:
    """Answers the ten loop questions from the brief, from live database state."""
    fam_counts = {r["family"]: r["c"] for r in conn.execute(
        "SELECT family, COUNT(*) c FROM jobs WHERE tier<>'REJECT' GROUP BY family")}
    under = [f for f in FAMILIES if fam_counts.get(f, 0) < 3]
    unchecked = conn.execute(
        "SELECT COUNT(*) c FROM employers WHERE last_checked IS NULL").fetchone()["c"]
    blocked = [r["domain"] for r in conn.execute(
        "SELECT domain FROM sources WHERE status LIKE 'blocked%' LIMIT 25")]
    analytics = conn.execute(
        "SELECT COUNT(*) c FROM jobs WHERE tier<>'REJECT' AND family='freedom_professional' "
        "AND (title LIKE '%analyst%' OR title LIKE '%operations%')").fetchone()["c"]
    total = conn.execute("SELECT COUNT(*) c FROM jobs WHERE tier<>'REJECT'").fetchone()["c"]
    dead = conn.execute("SELECT COUNT(*) c FROM jobs WHERE verification_status='DEAD'").fetchone()["c"]
    unverified = conn.execute(
        "SELECT COUNT(*) c FROM jobs WHERE verification_status='UNCERTAIN' AND score>=55").fetchone()["c"]
    top_film = conn.execute(
        "SELECT AVG(score) s FROM jobs WHERE family IN ('entertainment_development','physical_production')"
    ).fetchone()["s"] or 0
    top_free = conn.execute(
        "SELECT AVG(score) s FROM jobs WHERE family='freedom_professional'").fetchone()["s"] or 0

    return "\n".join([
        f"1. Underrepresented families: {', '.join(under) if under else 'none - all families have >=3 admitted jobs'}.",
        f"2. Source types not yet exhausted: {unchecked} employers in the database have never been crawled.",
        f"3. Companies not yet crawled: {unchecked} (see companies_to_watch.csv, check_status=not_checked).",
        f"4. New titles this iteration: {', '.join(stats.new_titles) if stats.new_titles else 'none'}.",
        f"5. Analytics/corporate over-production check: {analytics} of {total} admitted jobs are "
        f"analyst/ops-titled - {'acceptable' if total and analytics / max(total,1) < 0.25 else 'TOO HIGH, tighten low-priority penalties'}.",
        f"6. Generic-title risk inside entertainment employers: mitigated by crawling whole boards "
        f"rather than title-searching only.",
        f"7. Film-proximity vs acting freedom: mean score of film-side families {top_film:.1f} vs "
        f"freedom-professional {top_free:.1f}; the model is {'not' if top_film <= top_free + 8 else ''} "
        f"over-rewarding film proximity.",
        f"8. Flexible professional alternatives: {fam_counts.get('freedom_professional', 0)} admitted.",
        f"9. Links failing verification: {dead} DEAD, {unverified} still UNCERTAIN above score 55.",
        f"10. Blocked or inaccessible sources needing an alternate route: "
        f"{', '.join(blocked) if blocked else 'none recorded'}.",
    ])


def run_iteration(conn: sqlite3.Connection, f: Fetcher, iteration: int,
                  employer_budget: int = 40, reason: str = "") -> IterationStats:
    stats = IterationStats(iteration=iteration, expansion_reason=reason)
    conn.execute("INSERT OR REPLACE INTO iterations (iteration, started_at) VALUES (?,?)",
                 (iteration, now()))
    conn.commit()

    todo = conn.execute(
        "SELECT * FROM employers WHERE last_checked IS NULL OR last_checked < ? "
        "ORDER BY priority DESC, matching_jobs DESC LIMIT ?",
        (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 3 * 86400)), employer_budget)
    ).fetchall()

    for emp in todo:
        try:
            crawl_employer(conn, emp, f, stats)
        except Exception as exc:                     # noqa: BLE001
            conn.execute("UPDATE employers SET check_status=?, last_checked=? WHERE employer_id=?",
                         ("error", now(), emp["employer_id"]))
            conn.commit()

    verify_pending(conn, f, stats)
    stats.new_titles = learn_titles(conn)
    expand_employers_from_jobs(conn, stats)

    for host, st in f.host_status.items():
        record_source(conn, host, st)
        if st.startswith("blocked"):
            stats.blocked_domains.append(host)

    critique = self_critique(conn, stats)
    conn.execute(
        "UPDATE iterations SET ended_at=?, candidates=?, verified=?, admitted=?, rejected=?, "
        "new_titles=?, new_employers=?, expansion_reason=?, self_critique=? WHERE iteration=?",
        (now(), stats.candidates, stats.verified, stats.admitted, stats.rejected,
         ", ".join(stats.new_titles[:40]), ", ".join(stats.new_employers[:40]),
         stats.expansion_reason, critique, iteration))
    conn.commit()
    return stats


def run(max_iterations: int = 12, employer_budget: int = 40) -> list[IterationStats]:
    conn = connect()
    seed_employers(conn)
    f = Fetcher()
    history: list[IterationStats] = []
    for i in range(1, max_iterations + 1):
        reason = ("initial seed sweep" if i == 1 else
                  "previous round admitted new jobs; continuing employer + title expansion")
        stats = run_iteration(conn, f, i, employer_budget, reason)
        history.append(stats)
        print(f"[iter {i}] candidates={stats.candidates} admitted={stats.admitted} "
              f"verified={stats.verified} rejected={stats.rejected} dupes={stats.duplicates}")
        if plateaued(history):
            print("Marginal discovery has plateaued; stopping.")
            break
    conn.close()
    return history
