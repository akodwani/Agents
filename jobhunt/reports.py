"""Report generation: the six deliverables."""

from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path

from .db import connect, jload, now

OUT = Path(__file__).resolve().parents[1] / "out"

TIER_LABEL = {
    "APPLY_NOW": "APPLY NOW", "APPLY_GOOD_FIT": "APPLY - GOOD FIT",
    "STRETCH": "STRETCH", "RESEARCH_ONLY": "RESEARCH ONLY", "REJECT": "REJECT",
}

FILM_FAMILIES = {"entertainment_development", "physical_production", "ai_creative_production"}


def _arrangement(row) -> str:
    return {"remote": "Remote", "hybrid": "Hybrid", "onsite": "On-site"}.get(row["remote_status"], "UNKNOWN")


def _salary(row) -> str:
    if row["salary_min"]:
        if row["salary_max"] and row["salary_max"] != row["salary_min"]:
            return f"${row['salary_min']:,} - ${row['salary_max']:,}"
        return f"${row['salary_min']:,}"
    return row["salary_text"] or "UNKNOWN"


def _reason(row) -> str:
    bd = jload(row["score_breakdown"], {})
    bits = []
    if row["family"]:
        bits.append(row["family"].replace("_", " "))
    bits.append(f"acting-compat {bd.get('acting', 0):.0f}/30")
    bits.append(f"workload {bd.get('workload', 0):.0f}/20")
    bits.append(f"~{row['estimated_hours']} ({row['hours_confidence']})")
    if row["candidate_accessibility"]:
        bits.append(f"accessibility: {row['candidate_accessibility']}")
    return "; ".join(bits)


def _write_job_rows(path: Path, rows, with_status: bool = False) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = ["score", "tier", "title", "company", "salary", "location",
              "remote/hybrid/on-site", "estimated_hours", "hours_confidence",
              "acting_compatibility_score", "film_relevance", "accessibility",
              "reason_to_apply", "red_flags", "date_posted",
              "verification_timestamp", "direct_application_url"]
    if with_status:
        header.insert(2, "verification_status")
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        for r in rows:
            row = [
                f"{r['score']:.1f}", TIER_LABEL.get(r["tier"], r["tier"]), r["title"], r["company"],
                _salary(r), r["location"], _arrangement(r), r["estimated_hours"],
                r["hours_confidence"], f"{r['acting_schedule_compatibility']:.1f}",
                r["film_relevance"], r["candidate_accessibility"], _reason(r),
                "; ".join(jload(r["red_flags"], [])) or "none detected",
                r["date_posted"], r["verification_timestamp"],
                r["application_url"] or r["official_job_url"],
            ]
            if with_status:
                row.insert(2, r["verification_status"])
            w.writerow(row)
    return path


def jobs_live_csv(conn: sqlite3.Connection, path: Path | None = None) -> Path:
    """Spec-faithful: LIVE_CONFIRMED postings only."""
    rows = conn.execute(
        "SELECT * FROM jobs WHERE verification_status='LIVE_CONFIRMED' AND tier<>'REJECT' "
        "ORDER BY score DESC").fetchall()
    return _write_job_rows(path or OUT / "jobs_live.csv", rows)


def jobs_candidates_csv(conn: sqlite3.Connection, path: Path | None = None) -> Path:
    """Everything admitted, with its verification status stated in-line.

    This is what to work from whenever `jobs_live.csv` is empty because the
    verifier could not reach the network from the machine that ran discovery.
    """
    rows = conn.execute(
        "SELECT * FROM jobs WHERE tier<>'REJECT' ORDER BY score DESC").fetchall()
    return _write_job_rows(path or OUT / "jobs_candidates.csv", rows, with_status=True)


def _job_block(r) -> str:
    bd = jload(r["score_breakdown"], {})
    reds = jload(r["red_flags"], [])
    greens = jload(r["green_flags"], [])
    hours_basis = r["schedule_flexibility"]
    return f"""### {r['title']} — {r['company']}

- **Score:** {r['score']:.1f}/100 ({TIER_LABEL.get(r['tier'], r['tier'])})
- **Compensation:** {_salary(r)}
- **Location:** {r['location']}
- **Work arrangement:** {_arrangement(r)}
- **Estimated workload:** {r['estimated_hours']} — confidence **{r['hours_confidence']}**; drain estimate: {r['mental_drain_estimate']}
- **Why this fits:** {_reason(r)}{('; positive signals: ' + ', '.join(greens)) if greens else ''}
- **Main concern:** {'; '.join(reds) if reds else 'no red-flag language detected in the posting'}
- **Experience fit:** required: {r['experience_required']}; candidate accessibility: **{r['candidate_accessibility']}**
- **Acting compatibility:** {bd.get('acting', 0):.1f}/30 — {r['remote_status']}, ~{r['estimated_hours']}
- **Direct application:** {r['application_url'] or r['official_job_url']}
- **Verified live:** {r['verification_status']} at {r['verification_timestamp'] or 'UNKNOWN'}{(' — ' + r['verification_evidence']) if r['verification_evidence'] else ''}
"""


def apply_now_md(conn: sqlite3.Connection, path: Path | None = None, limit: int = 60) -> Path:
    path = path or OUT / "apply_now.md"
    rows = conn.execute(
        "SELECT * FROM jobs WHERE tier IN ('APPLY_NOW','APPLY_GOOD_FIT') "
        "AND verification_status <> 'DEAD' ORDER BY score DESC LIMIT ?", (limit,)).fetchall()
    live = [r for r in rows if r["verification_status"] == "LIVE_CONFIRMED"]
    likely = [r for r in rows if r["verification_status"] == "LIKELY_LIVE"]
    unverified = [r for r in rows if r["verification_status"] == "UNCERTAIN"]
    body = [f"# Apply now\n\nGenerated {now()}. Ranked by fit with the candidate's "
            f"acting-first constraints — acting compatibility (30) and workload (20) "
            f"dominate the 100-point model.\n",
            f"**{len(live)}** LIVE_CONFIRMED, **{len(likely)}** LIKELY_LIVE and "
            f"**{len(unverified)}** unverified postings below.\n",
            "\n## Primary list — verified live\n"]
    body += [_job_block(r) for r in live] or ["_No postings currently hold LIVE_CONFIRMED status._\n"]
    if likely:
        body.append("\n## Secondary list — likely live, verification incomplete\n")
        body += [_job_block(r) for r in likely]
    if unverified:
        body.append(f"\n## Not yet verifiable on this machine ({len(unverified)})\n")
        body.append("These were discovered through search and scored normally, but the direct-fetch "
                    "verifier could not open them from the machine that ran discovery (see "
                    "`search_log.md` → Sources). Run `python -m jobhunt.cli verify -n 200 "
                    "--min-score 0` on a machine with ordinary web access to promote them to "
                    "LIVE_CONFIRMED or mark them DEAD.\n")
        body += [_job_block(r) for r in unverified]
    path.write_text("\n".join(body))
    return path


def film_ecosystem_md(conn: sqlite3.Connection, path: Path | None = None) -> Path:
    path = path or OUT / "film_ecosystem_jobs.md"
    q = ("SELECT * FROM jobs WHERE family IN ('entertainment_development','physical_production',"
         "'ai_creative_production') AND tier<>'REJECT' ORDER BY score DESC")
    rows = conn.execute(q).fetchall()
    groups = {
        "Entertainment development": "entertainment_development",
        "Physical production / production planning": "physical_production",
        "AI / creative media production": "ai_creative_production",
    }
    body = [f"# Film-ecosystem jobs\n\nGenerated {now()}. Development, production planning, "
            "physical production, creative production, entertainment research and AI creative media.\n",
            "> Film relevance never outranks acting compatibility here — a 55-hour set job scores "
            "below a 35-hour remote job by design.\n"]
    for label, fam in groups.items():
        sub = [r for r in rows if r["family"] == fam]
        body.append(f"\n## {label} ({len(sub)})\n")
        body += [_job_block(r) for r in sub] or ["_Nothing currently qualifies._\n"]
    path.write_text("\n".join(body))
    return path


def freedom_jobs_md(conn: sqlite3.Connection, path: Path | None = None) -> Path:
    path = path or OUT / "freedom_jobs.md"
    rows = conn.execute(
        "SELECT * FROM jobs WHERE family NOT IN ('entertainment_development','physical_production') "
        "AND tier<>'REJECT' AND acting_schedule_compatibility >= 20 "
        "AND (salary_min IS NULL OR salary_min >= 45000) ORDER BY score DESC").fetchall()
    body = [f"# Freedom jobs\n\nGenerated {now()}. Less film-relevant, but unusually strong on the "
            "things that actually protect an acting career: remote work, predictable schedule, "
            "low drain, $45K+.\n",
            "> A $60K remote 30-35h research job outranks a $55K film job at 55h. That is the "
            "intended behaviour of the model, not a bug.\n"]
    body += [_job_block(r) for r in rows] or ["_Nothing currently qualifies._\n"]
    path.write_text("\n".join(body))
    return path


def companies_csv(conn: sqlite3.Connection, path: Path | None = None) -> Path:
    path = path or OUT / "companies_to_watch.csv"
    rows = conn.execute("SELECT * FROM employers ORDER BY matching_jobs DESC, priority DESC, name").fetchall()
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["employer", "industry", "careers_url", "ats", "why_relevant",
                    "last_checked", "check_status", "current_matching_jobs"])
        for r in rows:
            w.writerow([r["name"], r["industry"], r["careers_url"] or r["ats_url"] or "UNRESOLVED",
                        r["ats_provider"] or "UNKNOWN", r["why_relevant"],
                        r["last_checked"] or "never", r["check_status"] or "not_checked",
                        r["matching_jobs"]])
    return path


def search_log_md(conn: sqlite3.Connection, path: Path | None = None, preamble: str = "") -> Path:
    path = path or OUT / "search_log.md"
    lines = [f"# Search log\n\nGenerated {now()}.\n"]
    if preamble:
        lines.append(preamble + "\n")

    iters = conn.execute("SELECT * FROM iterations ORDER BY iteration").fetchall()
    lines.append("## Iterations\n")
    if not iters:
        lines.append("_No iterations recorded._\n")
    for it in iters:
        lines.append(f"### Iteration {it['iteration']} ({it['started_at']} → {it['ended_at'] or 'running'})\n")
        lines.append(f"- candidates seen: {it['candidates']}")
        lines.append(f"- verified: {it['verified']}")
        lines.append(f"- admitted: {it['admitted']}")
        lines.append(f"- rejected: {it['rejected']}")
        if it["new_titles"]:
            lines.append(f"- new titles discovered: {it['new_titles']}")
        if it["new_employers"]:
            lines.append(f"- new employers discovered: {it['new_employers']}")
        if it["expansion_reason"]:
            lines.append(f"- why this iteration expanded: {it['expansion_reason']}")
        if it["self_critique"]:
            lines.append(f"\n**Self-critique:**\n\n{it['self_critique']}\n")
        lines.append("")

    lines.append("\n## Searches executed\n")
    rows = conn.execute("SELECT * FROM searches ORDER BY iteration, id").fetchall()
    lines.append(f"Total distinct queries: **{len(rows)}**\n")
    lines.append("| # | iter | channel | query | results | new |")
    lines.append("|---|------|---------|-------|---------|-----|")
    for i, r in enumerate(rows, 1):
        q = (r["query"] or "").replace("|", "\\|")
        lines.append(f"| {i} | {r['iteration']} | {r['channel']} | {q} | {r['results_count']} | {r['new_urls']} |")

    lines.append("\n## Sources and their status\n")
    lines.append("| domain | status | detail | last checked |")
    lines.append("|--------|--------|--------|--------------|")
    for r in conn.execute("SELECT * FROM sources ORDER BY status, domain"):
        lines.append(f"| {r['domain']} | {r['status']} | {(r['detail'] or '')[:120]} | {r['last_checked']} |")

    lines.append("\n## Employer coverage\n")
    tot = conn.execute("SELECT COUNT(*) c FROM employers").fetchone()["c"]
    reached = conn.execute(
        "SELECT COUNT(*) c FROM employers WHERE check_status NOT IN "
        "('blocked','not_checked','unresolved','error') AND check_status IS NOT NULL").fetchone()["c"]
    lines.append(f"- employers in database: **{tot}**")
    lines.append(f"- employers whose current openings were actually reached: **{reached}**")
    for r in conn.execute("SELECT check_status, COUNT(*) c FROM employers GROUP BY check_status"):
        lines.append(f"- status `{r['check_status'] or 'not_checked'}`: {r['c']}")

    lines.append("\n## Job funnel\n")
    for r in conn.execute("SELECT verification_status s, COUNT(*) c FROM jobs GROUP BY s"):
        lines.append(f"- {r['s']}: {r['c']}")
    for r in conn.execute("SELECT tier t, COUNT(*) c FROM jobs GROUP BY t ORDER BY c DESC"):
        lines.append(f"- tier {r['t']}: {r['c']}")

    path.write_text("\n".join(lines) + "\n")
    return path


def generate_all(db_path: Path | None = None, preamble: str = "") -> list[Path]:
    conn = connect(db_path) if db_path else connect()
    paths = [jobs_live_csv(conn), jobs_candidates_csv(conn), apply_now_md(conn), film_ecosystem_md(conn),
             freedom_jobs_md(conn), companies_csv(conn), search_log_md(conn, preamble=preamble)]
    conn.close()
    return paths
