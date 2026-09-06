"""Probe representative source hosts once each and record accessibility.

Establishes, honestly and cheaply, which source classes this machine can reach.
Blocked hosts are recorded as blocked; nothing here attempts to work around a
network policy.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from jobhunt.db import connect, now, record_source
from jobhunt.fetch import Fetcher

PROBES = [
    ("boards-api.greenhouse.io", "https://boards-api.greenhouse.io/v1/boards/a24/jobs"),
    ("api.lever.co", "https://api.lever.co/v0/postings/vevo?mode=json"),
    ("api.ashbyhq.com", "https://api.ashbyhq.com/posting-api/job-board/promise-studios"),
    ("apply.workable.com", "https://apply.workable.com/api/v1/widget/accounts/heritage-werks-inc"),
    ("api.smartrecruiters.com", "https://api.smartrecruiters.com/v1/companies/NBCUniversal3/postings?limit=1"),
    ("job-boards.greenhouse.io", "https://job-boards.greenhouse.io/thenewyorktimes"),
    ("jobs.lever.co", "https://jobs.lever.co/bustle"),
    ("jobs.ashbyhq.com", "https://jobs.ashbyhq.com/promise-studios"),
    ("condenast.wd5.myworkdayjobs.com", "https://condenast.wd5.myworkdayjobs.com/CondeCareers"),
    ("www.entertainmentcareers.net", "https://www.entertainmentcareers.net/"),
    ("www.a24films.com", "https://www.a24films.com/"),
    ("runwayml.com", "https://runwayml.com/"),
    ("www.nytimes.com", "https://www.nytimes.com/"),
    ("www.idealist.org", "https://www.idealist.org/"),
    ("www.linkedin.com", "https://www.linkedin.com/"),
]


def main() -> int:
    conn = connect()
    f = Fetcher(cache=False, delay=0.2)
    blocked = 0
    for host, url in PROBES:
        r = f.get(url, retries=0)
        if r.ok:
            status, detail = "ok", f"HTTP 200, {len(r.text)} bytes"
        elif r.blocked or "403" in (r.reason or "") or r.reason.startswith("network"):
            status, detail = "blocked_network", (r.reason or "blocked")[:160]
            blocked += 1
        else:
            status, detail = "error", (r.reason or f"HTTP {r.status}")[:160]
        record_source(conn, host, status, detail)
        print(f"{status:16} {host:38} {detail[:70]}")
    conn.commit()

    if blocked == len(PROBES):
        conn.execute("UPDATE employers SET check_status='blocked', last_checked=? "
                     "WHERE last_checked IS NULL", (now(),))
        conn.commit()
        print(f"\nAll {blocked} probe hosts blocked by this machine's egress policy; "
              "every seeded employer marked check_status=blocked.")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
