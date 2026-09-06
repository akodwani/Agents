"""Command line entry points.

    python -m jobhunt.cli seed            # load the employer universe
    python -m jobhunt.cli crawl [-n 40]   # one crawl iteration
    python -m jobhunt.cli run [-i 12]     # the full loop until plateau
    python -m jobhunt.cli ingest FILE     # ingest externally discovered postings
    python -m jobhunt.cli verify [-n 60]  # re-verify pending postings
    python -m jobhunt.cli report          # regenerate the six deliverables
    python -m jobhunt.cli stats           # funnel summary
"""

from __future__ import annotations

import argparse
import sys

from .db import connect
from .fetch import Fetcher
from .ingest import ingest_file
from .loop import IterationStats, run, run_iteration, seed_employers, verify_pending
from .reports import generate_all


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="jobhunt")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("seed")
    c = sub.add_parser("crawl"); c.add_argument("-n", "--employers", type=int, default=40)
    r = sub.add_parser("run"); r.add_argument("-i", "--iterations", type=int, default=12)
    r.add_argument("-n", "--employers", type=int, default=40)
    g = sub.add_parser("ingest"); g.add_argument("file")
    v = sub.add_parser("verify"); v.add_argument("-n", "--limit", type=int, default=60)
    v.add_argument("--min-score", type=float, default=55.0)
    rep = sub.add_parser("report"); rep.add_argument("--preamble", default="")
    sub.add_parser("stats")

    a = p.parse_args(argv)
    conn = connect()

    if a.cmd == "seed":
        print(f"seeded {seed_employers(conn)} new employers")
    elif a.cmd == "crawl":
        s = run_iteration(conn, Fetcher(), iteration=_next_iter(conn), employer_budget=a.employers,
                          reason="manual crawl invocation")
        print(f"candidates={s.candidates} admitted={s.admitted} verified={s.verified}")
    elif a.cmd == "run":
        run(max_iterations=a.iterations, employer_budget=a.employers)
    elif a.cmd == "ingest":
        print(ingest_file(a.file, conn))
    elif a.cmd == "verify":
        stats = IterationStats(iteration=_next_iter(conn) - 1)
        verify_pending(conn, Fetcher(), stats, limit=a.limit, min_score=a.min_score)
        print(f"verified {stats.verified}")
    elif a.cmd == "report":
        for path in generate_all(preamble=a.preamble):
            print(path)
    elif a.cmd == "stats":
        for q, label in [("SELECT verification_status k, COUNT(*) c FROM jobs GROUP BY k", "verification"),
                         ("SELECT tier k, COUNT(*) c FROM jobs GROUP BY k", "tier"),
                         ("SELECT family k, COUNT(*) c FROM jobs GROUP BY k", "family")]:
            print(f"-- {label}")
            for row in conn.execute(q):
                print(f"   {row['k']}: {row['c']}")
    conn.close()
    return 0


def _next_iter(conn) -> int:
    row = conn.execute("SELECT MAX(iteration) m FROM iterations").fetchone()
    return (row["m"] or 0) + 1


if __name__ == "__main__":
    sys.exit(main())
