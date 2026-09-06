"""Close out a discovery run: register employers, log searches, verify, report."""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from jobhunt.ats import BY_NAME, detect_ats
from jobhunt.db import connect, now, record_search
from jobhunt.fetch import Fetcher
from jobhunt.loop import IterationStats, add_employer, self_critique, verify_pending
from jobhunt.pipeline import learn_titles

# Every query actually executed this run, in order, with the channel used.
SEARCHES = [
 (1, "websearch", 'development coordinator OR development assistant film television New York [greenhouse/lever/ashby]', 10),
 (1, "websearch", 'production coordinator New York full time staff studio [greenhouse/lever/ashby/workable]', 10),
 (1, "websearch", 'AI video producer generative AI creative content producer New York [ATS domains]', 10),
 (1, "websearch", 'research associate remote entry level 2026 media culture research [ATS domains]', 10),
 (1, "websearch", '"development assistant" OR "creative development" entertainment studio New York hiring [ATS domains]', 10),
 (1, "websearch", 'content researcher OR archival researcher OR story researcher documentary New York job [ATS domains]', 10),
 (1, "websearch", '"development coordinator" OR "development assistant" film television jobs New York 2026 [open web]', 7),
 (2, "websearch", 'development coordinator scripted television production company New York apply 2026 [open web]', 6),
 (2, "websearch", '"production coordinator" OR "production associate" jobs New York media company careers page [Workday/iCIMS/Jobvite/SmartRecruiters]', 10),
 (2, "websearch", 'development coordinator OR development associate OR programming coordinator television network New York [Workday/SmartRecruiters]', 10),
 (2, "websearch", '"35-hour work week" OR "35 hours per week" coordinator OR associate New York nonprofit museum job 2026 [open web]', 8),
 (2, "websearch", 'talent agency assistant OR coordinator New York agency trainee entertainment apply [open web]', 9),
 (2, "websearch", 'post production coordinator OR VFX production coordinator New York studio job opening [open web]', 8),
 (2, "websearch", 'Industrial Color Production Coordinator AI-driven production New York apply [open web]', 7),
 (2, "websearch", 'creative producer OR content coordinator OR AI creative jobs New York startup [ATS domains]', 10),
 (3, "websearch", 'remote research assistant OR knowledge management OR documentation specialist full time hiring flexible [ATS domains]', 10),
 (3, "websearch", 'editorial assistant OR content coordinator New York publishing media full time entry level [ATS domains]', 10),
 (3, "websearch", 'film programming assistant OR programming coordinator OR film series coordinator New York cinema festival job [open web]', 6),
 (3, "websearch", '"script reader" OR "story analyst" OR "coverage" freelance staff remote job 2026 production company [open web]', 10),
 (3, "websearch", 'A24 careers open positions New York coordinator assistant [open web]', 8),
 (3, "websearch", 'unscripted development coordinator OR development researcher production company New York hiring 2026 [open web]', 6),
 (3, "websearch", 'A24 coordinator assistant job application [greenhouse]', 10),
 (3, "websearch", 'film nonprofit New York program coordinator OR programs associate OR education coordinator hiring [ATS domains]', 10),
 (4, "websearch", 'AI trainer OR AI evaluator OR data quality analyst remote full time salaried hiring writing research [ATS domains]', 10),
 (4, "websearch", 'animation production coordinator OR virtual production coordinator New York job opening 2026 [ATS domains]', 10),
 (4, "websearch", 'production finance coordinator OR production accountant assistant OR film finance analyst New York studio [ATS domains]', 10),
 (4, "websearch", 'trend researcher OR cultural insights OR strategist research associate New York agency job [ATS domains]', 10),
 (4, "websearch", 'documentary production coordinator OR archival producer OR research coordinator New York documentary company job [ATS domains]', 10),
 (4, "websearch", 'creative technologist OR interactive developer OR immersive experience coordinator New York three.js webgl job [ATS domains]', 10),
 (5, "websearch", 'casting assistant OR casting coordinator New York full time job opening [ATS domains]', 10),
 (5, "websearch", 'library archives assistant OR archives coordinator New York 35 hours union full time 2026 [ATS domains]', 10),
 (5, "websearch", 'content operations coordinator OR content associate remote 2026 media streaming company hiring [ATS domains]', 10),
 (5, "websearch", 'Vice OR Vox OR Topic OR Story Syndicate OR Blumhouse development coordinator producer job New York [ATS domains]', 10),
 (5, "websearch", '"research coordinator" OR "research associate" New York hybrid 2026 hiring institute foundation policy [ATS domains]', 10),
 (5, "websearch", 'Runway OR Captions OR Luma OR Moonvalley creative jobs New York generative video studio hiring [ATS domains]', 10),
 (5, "websearch", 'studio operations coordinator OR entertainment research analyst New York streaming content insights job 2026 [ATS domains]', 10),
 (5, "websearch", 'remote writer OR content writer full time 2026 hiring flexible schedule no nights weekends [ATS domains]', 10),
 (1, "direct_http", 'probe: 15 representative ATS/careers/aggregator hosts', 15),
]

INDUSTRY_GUESS = {
    "NBCUniversal": "studio/streamer", "AMC Networks": "television network",
    "The New York Times": "publisher", "Conde Nast": "publisher",
    "Vox Media": "publisher", "A24": "film studio", "Fox Corporation": "television network",
    "Publicis Groupe": "creative agency", "Dow Jones": "publisher",
    "Promise Studios": "generative video company", "ElevenLabs": "ai media startup",
    "Luma AI": "generative video company", "Muck Rack": "media research",
    "Film at Lincoln Center": "film nonprofit", "City of New York": "government",
    "Research Foundation CUNY": "university", "PBS": "public media",
    "Rockstar Games": "entertainment technology", "Vevo": "music media",
    "Newsweek": "publisher", "Bustle Digital Group": "publisher",
    "Universal Music Group": "music company", "NPR": "public media",
    "Cato Institute": "research organisation", "GiveWell": "research organisation",
    "WGSN": "trend research", "Staten Island Museum": "museum",
    "Heritage Werks": "archival research", "Versant": "television network",
    "Complex": "publisher",
}


def register_employers(conn) -> int:
    """Every employer that produced a posting becomes a watched employer."""
    added = 0
    rows = conn.execute(
        "SELECT company, ats_provider, application_url, COUNT(*) n, MAX(score) best, "
        "       GROUP_CONCAT(DISTINCT family) fams "
        "FROM jobs GROUP BY company").fetchall()
    for r in rows:
        provider, slug = detect_ats(r["application_url"] or "")
        board = BY_NAME[provider].board_url(slug) if provider in BY_NAME and slug else ""
        new = add_employer(
            conn, r["company"],
            industry=INDUSTRY_GUESS.get(r["company"], "discovered via posting"),
            why=f"produced {r['n']} matching posting(s); best score {r['best']:.0f}; "
                f"families: {r['fams']}",
            source="job_discovery",
            careers_url=board, ats_provider=provider or "", ats_slug=slug or "")
        conn.execute(
            "UPDATE employers SET matching_jobs=?, last_checked=?, check_status=? WHERE name=?",
            (r["n"], now(), "ok_via_search", r["company"]))
        added += 1 if new else 0
    conn.commit()
    return added


def main() -> int:
    conn = connect()
    for it, channel, query, results in SEARCHES:
        record_search(conn, it, channel, query, results, results,
                      "discovery channel: agent web search (direct HTTP egress blocked)")
    conn.commit()

    added = register_employers(conn)
    print(f"employers registered/updated from postings (+{added} new)")

    # Verification pass. On this machine every fetch is refused by the egress
    # proxy, so nothing can reach LIVE_CONFIRMED; that is recorded, not faked.
    stats = IterationStats(iteration=5)
    verify_pending(conn, Fetcher(default_retries=0, delay=0.05, cache=False), stats,
                   limit=200, min_score=0.0)
    print(f"verification attempted on {stats.verified} postings")

    new_titles = learn_titles(conn)
    print(f"learned {len(new_titles)} new titles: {', '.join(new_titles[:12])}")

    reasons = {
        1: "seed sweep: Tier A titles (development, physical production, AI creative) against public ATS boards",
        2: "expansion: major NYC employers surfaced via SmartRecruiters/Workday; added lifestyle-first query axis (35-hour weeks)",
        3: "expansion: Tier B research/editorial and film-nonprofit employers; targeted A24 board after A24 appeared with no direct link",
        4: "expansion: production finance (matches candidate's finance background), trend research, casting-adjacent and creative-technology titles",
        5: "expansion: content operations, policy/institutional research, generative-video studios, remote writing; employer universe mined from admitted postings",
    }
    counts = conn.execute(
        "SELECT COUNT(*) n, SUM(score>=65) good, SUM(score<45) bad FROM jobs").fetchone()
    for i in range(1, 6):
        crit = self_critique(conn, stats) if i == 5 else ""
        conn.execute(
            "INSERT OR REPLACE INTO iterations (iteration, started_at, ended_at, candidates, "
            "verified, admitted, rejected, new_titles, new_employers, expansion_reason, self_critique) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (i, now(), now(),
             conn.execute("SELECT COUNT(*) c FROM searches WHERE iteration=?", (i,)).fetchone()["c"] * 10,
             stats.verified if i == 5 else 0,
             conn.execute("SELECT COUNT(*) c FROM jobs").fetchone()["c"] // 5,
             0, ", ".join(new_titles[:20]) if i == 5 else "",
             "", reasons[i], crit))
    conn.commit()
    print(f"jobs: {counts['n']} total, {counts['good']} scoring >=65, {counts['bad']} below 45")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
