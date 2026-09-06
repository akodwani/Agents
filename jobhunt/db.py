"""SQLite persistence for the job-discovery system."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Iterable

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "jobs.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    job_id                        TEXT PRIMARY KEY,
    title                         TEXT,
    company                       TEXT,
    location                      TEXT,
    remote_status                 TEXT,      -- remote | hybrid | onsite | unknown
    employment_type               TEXT,      -- full_time | part_time | contract | internship | unknown
    salary_min                    INTEGER,
    salary_max                    INTEGER,
    salary_text                   TEXT,
    estimated_hours               TEXT,
    hours_confidence              TEXT,      -- KNOWN | LIKELY | UNCERTAIN
    schedule_flexibility          TEXT,
    experience_required           TEXT,
    education_required            TEXT,
    description                   TEXT,
    responsibilities              TEXT,
    qualifications                TEXT,
    date_posted                   TEXT,
    valid_through                 TEXT,
    source_discovered_from        TEXT,
    official_job_url              TEXT,
    application_url               TEXT,
    ats_provider                  TEXT,
    verification_status           TEXT,      -- LIVE_CONFIRMED | LIKELY_LIVE | UNCERTAIN | DEAD
    verification_timestamp        TEXT,
    verification_evidence         TEXT,
    film_relevance                TEXT,      -- high | medium | low | none
    family                        TEXT,
    acting_schedule_compatibility REAL,
    mental_drain_estimate         TEXT,      -- low | moderate | high | severe
    candidate_accessibility       TEXT,      -- strong | plausible | stretch | poor
    notes                         TEXT,
    red_flags                     TEXT,      -- json list
    green_flags                   TEXT,      -- json list
    score                         REAL,
    score_breakdown               TEXT,      -- json dict
    tier                          TEXT,      -- APPLY_NOW | APPLY_GOOD_FIT | STRETCH | RESEARCH_ONLY | REJECT
    dedupe_key                    TEXT,
    duplicate_of                  TEXT,
    content_hash                  TEXT,
    raw_snapshot                  TEXT,
    first_seen                    TEXT,
    last_seen                     TEXT
);
CREATE INDEX IF NOT EXISTS idx_jobs_dedupe ON jobs(dedupe_key);
CREATE INDEX IF NOT EXISTS idx_jobs_score  ON jobs(score DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(verification_status);

CREATE TABLE IF NOT EXISTS employers (
    employer_id      TEXT PRIMARY KEY,
    name             TEXT,
    industry         TEXT,
    website          TEXT,
    careers_url      TEXT,
    ats_provider     TEXT,
    ats_slug         TEXT,
    ats_url          TEXT,
    hq               TEXT,
    nyc_presence     INTEGER DEFAULT 0,
    why_relevant     TEXT,
    discovered_from  TEXT,
    last_checked     TEXT,
    check_status     TEXT,      -- ok | blocked | no_ats | unresolved | error
    matching_jobs    INTEGER DEFAULT 0,
    total_jobs_seen  INTEGER DEFAULT 0,
    priority         REAL DEFAULT 0.5,
    notes            TEXT
);

CREATE TABLE IF NOT EXISTS crawl_queue (
    url          TEXT PRIMARY KEY,
    kind         TEXT,         -- careers | ats_board | job | sitemap | search
    employer_id  TEXT,
    priority     REAL DEFAULT 0.5,
    state        TEXT DEFAULT 'pending',   -- pending | done | blocked | error
    attempts     INTEGER DEFAULT 0,
    last_error   TEXT,
    queued_at    TEXT,
    done_at      TEXT
);

CREATE TABLE IF NOT EXISTS searches (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    iteration     INTEGER,
    channel       TEXT,       -- websearch | ats_api | careers_crawl | sitemap
    query         TEXT,
    results_count INTEGER,
    new_urls      INTEGER,
    executed_at   TEXT,
    notes         TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_searches_q ON searches(channel, query);

CREATE TABLE IF NOT EXISTS sources (
    domain        TEXT PRIMARY KEY,
    status        TEXT,       -- ok | blocked_robots | blocked_network | error
    detail        TEXT,
    last_checked  TEXT
);

CREATE TABLE IF NOT EXISTS iterations (
    iteration     INTEGER PRIMARY KEY,
    started_at    TEXT,
    ended_at      TEXT,
    candidates    INTEGER,
    verified      INTEGER,
    admitted      INTEGER,
    rejected      INTEGER,
    new_titles    TEXT,
    new_employers TEXT,
    expansion_reason TEXT,
    self_critique TEXT
);
"""


def connect(path: Path | str = DB_PATH) -> sqlite3.Connection:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def upsert(conn: sqlite3.Connection, table: str, row: dict[str, Any], key: str) -> None:
    cols = [c for c in row if row[c] is not None]
    placeholders = ", ".join("?" for _ in cols)
    updates = ", ".join(f"{c}=excluded.{c}" for c in cols if c != key)
    sql = (
        f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders}) "
        f"ON CONFLICT({key}) DO UPDATE SET {updates}"
        if updates else
        f"INSERT OR IGNORE INTO {table} ({', '.join(cols)}) VALUES ({placeholders})"
    )
    conn.execute(sql, [row[c] for c in cols])


def enqueue(conn: sqlite3.Connection, url: str, kind: str,
            employer_id: str | None = None, priority: float = 0.5) -> bool:
    cur = conn.execute("SELECT 1 FROM crawl_queue WHERE url=?", (url,))
    if cur.fetchone():
        return False
    conn.execute(
        "INSERT INTO crawl_queue (url, kind, employer_id, priority, queued_at) VALUES (?,?,?,?,?)",
        (url, kind, employer_id, priority, now()),
    )
    return True


def pending(conn: sqlite3.Connection, kind: str | None = None, limit: int = 200) -> list[sqlite3.Row]:
    if kind:
        sql = "SELECT * FROM crawl_queue WHERE state='pending' AND kind=? ORDER BY priority DESC LIMIT ?"
        return conn.execute(sql, (kind, limit)).fetchall()
    sql = "SELECT * FROM crawl_queue WHERE state='pending' ORDER BY priority DESC LIMIT ?"
    return conn.execute(sql, (limit,)).fetchall()


def mark(conn: sqlite3.Connection, url: str, state: str, error: str | None = None) -> None:
    conn.execute(
        "UPDATE crawl_queue SET state=?, last_error=?, done_at=?, attempts=attempts+1 WHERE url=?",
        (state, error, now(), url),
    )


def record_search(conn: sqlite3.Connection, iteration: int, channel: str, query: str,
                  results: int, new_urls: int, notes: str = "") -> None:
    conn.execute(
        "INSERT OR REPLACE INTO searches (iteration, channel, query, results_count, new_urls, executed_at, notes)"
        " VALUES (?,?,?,?,?,?,?)",
        (iteration, channel, query, results, new_urls, now(), notes),
    )


def seen_query(conn: sqlite3.Connection, channel: str, query: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM searches WHERE channel=? AND query=?", (channel, query)
    ).fetchone() is not None


def record_source(conn: sqlite3.Connection, domain: str, status: str, detail: str = "") -> None:
    upsert(conn, "sources",
           {"domain": domain, "status": status, "detail": detail, "last_checked": now()},
           "domain")


def jobs_where(conn: sqlite3.Connection, clause: str = "1=1", params: Iterable = ()) -> list[sqlite3.Row]:
    return conn.execute(f"SELECT * FROM jobs WHERE {clause} ORDER BY score DESC", tuple(params)).fetchall()


def jload(value: Any, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default
