# jobhunt — persistent job-discovery system

A local, iterative job-discovery loop built for one candidate whose day job
exists to fund an acting career. It optimises for **income stability + low
drain + schedule control**, not prestige or maximum compensation.

```
discover → crawl → extract → verify → score → deduplicate → expand sources → repeat
```

## Quick start

```bash
python -m jobhunt.cli seed                 # load the 239-employer seed universe
python -m jobhunt.cli run -i 12 -n 40      # full loop until marginal discovery plateaus
python -m jobhunt.cli report               # regenerate the six deliverables in out/
```

Other commands:

```bash
python -m jobhunt.cli crawl -n 40                 # one crawl iteration
python -m jobhunt.cli verify -n 200 --min-score 0 # re-verify stored postings
python -m jobhunt.cli ingest data/ingest/leads.jsonl
python -m jobhunt.cli stats
```

Optional extras: `pip install playwright && playwright install chromium` enables
browser rendering for JS-only postings (Workday, iCIMS, some SPAs). Everything
else runs on `requests` alone.

## Layout

| Module | What it does |
|---|---|
| `config/candidate.py` | The candidate profile and life-design constraints. Tune the search here. |
| `config/taxonomy.py` | Job families, ~135 seed titles, query concepts, red/green flags, exclusions. Learns new titles into `data/learned_titles.json`. |
| `config/employers_seed.py` | 239 seed employers across 28 industry classes, NYC-weighted. |
| `fetch.py` | robots.txt-aware, rate-limited, retrying HTTP with a local cache. |
| `extract.py` | JSON-LD `JobPosting`, `__NEXT_DATA__`, Nuxt/Apollo state, HTML→text. |
| `ats/` | 17 ATS adapters (Greenhouse, Lever, Ashby, Workable, SmartRecruiters, Recruitee, Breezy, BambooHR, Teamtailor, Jobvite, iCIMS, JazzHR, Pinpoint, Comeet, Rippling, Gem, Workday). |
| `discover.py` | Careers-URL resolution, ATS detection, sitemap scanning, careers-page scraping. |
| `verify.py` | Live verification → `LIVE_CONFIRMED` / `LIKELY_LIVE` / `UNCERTAIN` / `DEAD`, with Playwright fallback. |
| `normalize.py` | Salary, experience, remote status, employment type, red/green flags, hours inference with stated confidence. |
| `score.py` | The 100-point model. |
| `pipeline.py` | Normalise → dedupe → score → persist; title learning. |
| `loop.py` | The iteration controller, employer expansion, plateau detection, self-critique. |
| `reports.py` | The six deliverables. |
| `db.py` | SQLite schema (`jobs`, `employers`, `crawl_queue`, `searches`, `sources`, `iterations`). |

## Scoring model (100 points)

| # | Category | Points | Notes |
|---|---|---|---|
| 1 | Acting compatibility | 30 | arrangement, predictability, after-hours load, hours left for training |
| 2 | Workload / drain | 20 | 30–35 h/wk scores full marks; 50+ scores ~0 |
| 3 | Subject-matter interest | 15 | development > production planning > AI creative > research > content > general |
| 4 | Compensation / stability | 15 | $45K floor, $50–65K band; high pay bought with long hours is docked |
| 5 | Accessibility | 15 | 0–2 yrs full marks; 5+ yrs heavily penalised |
| 6 | Career optionality | 5 | capped, so film proximity can never outweigh acting freedom |

Penalties (seniority titles, excluded fields, student-only, unpaid, commission-only)
are subtracted afterwards. Tiers: `APPLY_NOW` ≥75 · `APPLY_GOOD_FIT` 65–74 ·
`STRETCH` 55–64 · `RESEARCH_ONLY` 40–54 · `REJECT` <40.

By construction a $60K remote 32-hour research job outranks a $55K film job at
55 hours. That is the point, not a bug.

## Hours inference

Postings rarely state hours, so `normalize.estimate_hours` combines a job-family
prior with employer type, exempt/non-exempt language, on-set language and
red/green flag weight — and always labels the result `KNOWN`, `LIKELY` or
`UNCERTAIN`. An inferred 35-hour week is never recorded as known.

## Politeness and access

Only publicly accessible pages are requested. `fetch.py` honours robots.txt,
rate-limits per host, and treats 401/403/429 as "this source is inaccessible" —
recorded in the `sources` table and reported in `search_log.md`. Nothing here
attempts to bypass CAPTCHAs, logins, paywalls or anti-bot systems.

## Outputs (`out/`)

`jobs_live.csv` · `jobs_candidates.csv` · `apply_now.md` ·
`film_ecosystem_jobs.md` · `freedom_jobs.md` · `companies_to_watch.csv` ·
`search_log.md`
