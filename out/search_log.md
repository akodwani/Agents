# Search log

Generated 2026-09-06T13:57:15Z.

## Run conditions - read this first

Discovery ran inside a sandbox whose egress proxy refuses CONNECT to every
external host (HTTP 403 at the gateway). That was verified with a 15-host probe
covering the ATS APIs, ATS job-board hosts, a Workday tenant, employer sites and
aggregators; all 15 were refused. The refusals are recorded in the Sources table
below and were **not** worked around.

Consequences, stated plainly:

* **The crawler could not run against live sources from this machine.** Every
  seeded employer that was not reached through search is marked
  `check_status=blocked`.
* **Discovery instead ran through the agent's web-search channel**, which does
  reach the open web. 37 distinct queries were executed across five iterations,
  biased towards public ATS domains so that results are direct application URLs
  rather than aggregator pages.
* **Nothing reached `LIVE_CONFIRMED`.** Verification requires opening the exact
  job URL, and that fetch is refused here. All 90 admitted postings therefore
  sit at `UNCERTAIN`, and `jobs_live.csv` is header-only by design. Work from
  `jobs_candidates.csv` and the "Not yet verifiable on this machine" section of
  `apply_now.md`, which carry the same rows with their status stated.
* **No status, salary, hour count or URL was invented to fill the gap.** Unknown
  fields say `UNKNOWN`; every URL below came back from a real search result.

On a machine with ordinary web access the whole pipeline runs unmodified:

```bash
python -m jobhunt.cli verify -n 200 --min-score 0   # promotes to LIVE_CONFIRMED / DEAD
python -m jobhunt.cli run -i 12 -n 40               # full crawl loop over the employer universe
python -m jobhunt.cli report
```

## Iterations

### Iteration 1 (2026-09-06T13:56:39Z → 2026-09-06T13:56:39Z)

- candidates seen: 80
- verified: 0
- admitted: 18
- rejected: 0
- why this iteration expanded: seed sweep: Tier A titles (development, physical production, AI creative) against public ATS boards

### Iteration 2 (2026-09-06T13:56:39Z → 2026-09-06T13:56:39Z)

- candidates seen: 80
- verified: 0
- admitted: 18
- rejected: 0
- why this iteration expanded: expansion: major NYC employers surfaced via SmartRecruiters/Workday; added lifestyle-first query axis (35-hour weeks)

### Iteration 3 (2026-09-06T13:56:39Z → 2026-09-06T13:56:39Z)

- candidates seen: 80
- verified: 0
- admitted: 18
- rejected: 0
- why this iteration expanded: expansion: Tier B research/editorial and film-nonprofit employers; targeted A24 board after A24 appeared with no direct link

### Iteration 4 (2026-09-06T13:56:39Z → 2026-09-06T13:56:39Z)

- candidates seen: 60
- verified: 0
- admitted: 18
- rejected: 0
- why this iteration expanded: expansion: production finance (matches candidate's finance background), trend research, casting-adjacent and creative-technology titles

### Iteration 5 (2026-09-06T13:56:39Z → 2026-09-06T13:56:39Z)

- candidates seen: 80
- verified: 90
- admitted: 18
- rejected: 0
- why this iteration expanded: expansion: content operations, policy/institutional research, generative-video studios, remote writing; employer universe mined from admitted postings

**Self-critique:**

1. Underrepresented families: none - all families have >=3 admitted jobs.
2. Source types not yet exhausted: 0 employers in the database have never been crawled.
3. Companies not yet crawled: 0 (see companies_to_watch.csv, check_status=not_checked).
4. New titles this iteration: none.
5. Analytics/corporate over-production check: 0 of 89 admitted jobs are analyst/ops-titled - acceptable.
6. Generic-title risk inside entertainment employers: mitigated by crawling whole boards rather than title-searching only.
7. Film-proximity vs acting freedom: mean score of film-side families 60.9 vs freedom-professional 65.5; the model is not over-rewarding film proximity.
8. Flexible professional alternatives: 26 admitted.
9. Links failing verification: 0 DEAD, 85 still UNCERTAIN above score 55.
10. Blocked or inaccessible sources needing an alternate route: boards-api.greenhouse.io, api.lever.co, api.ashbyhq.com, apply.workable.com, api.smartrecruiters.com, job-boards.greenhouse.io, jobs.lever.co, jobs.ashbyhq.com, condenast.wd5.myworkdayjobs.com, www.entertainmentcareers.net, www.a24films.com, runwayml.com, www.nytimes.com, www.idealist.org, www.linkedin.com.



## Searches executed

Total distinct queries: **38**

| # | iter | channel | query | results | new |
|---|------|---------|-------|---------|-----|
| 1 | 1 | websearch | development coordinator OR development assistant film television New York [greenhouse/lever/ashby] | 10 | 10 |
| 2 | 1 | websearch | production coordinator New York full time staff studio [greenhouse/lever/ashby/workable] | 10 | 10 |
| 3 | 1 | websearch | AI video producer generative AI creative content producer New York [ATS domains] | 10 | 10 |
| 4 | 1 | websearch | research associate remote entry level 2026 media culture research [ATS domains] | 10 | 10 |
| 5 | 1 | websearch | "development assistant" OR "creative development" entertainment studio New York hiring [ATS domains] | 10 | 10 |
| 6 | 1 | websearch | content researcher OR archival researcher OR story researcher documentary New York job [ATS domains] | 10 | 10 |
| 7 | 1 | websearch | "development coordinator" OR "development assistant" film television jobs New York 2026 [open web] | 7 | 7 |
| 8 | 1 | direct_http | probe: 15 representative ATS/careers/aggregator hosts | 15 | 15 |
| 9 | 2 | websearch | development coordinator scripted television production company New York apply 2026 [open web] | 6 | 6 |
| 10 | 2 | websearch | "production coordinator" OR "production associate" jobs New York media company careers page [Workday/iCIMS/Jobvite/SmartRecruiters] | 10 | 10 |
| 11 | 2 | websearch | development coordinator OR development associate OR programming coordinator television network New York [Workday/SmartRecruiters] | 10 | 10 |
| 12 | 2 | websearch | "35-hour work week" OR "35 hours per week" coordinator OR associate New York nonprofit museum job 2026 [open web] | 8 | 8 |
| 13 | 2 | websearch | talent agency assistant OR coordinator New York agency trainee entertainment apply [open web] | 9 | 9 |
| 14 | 2 | websearch | post production coordinator OR VFX production coordinator New York studio job opening [open web] | 8 | 8 |
| 15 | 2 | websearch | Industrial Color Production Coordinator AI-driven production New York apply [open web] | 7 | 7 |
| 16 | 2 | websearch | creative producer OR content coordinator OR AI creative jobs New York startup [ATS domains] | 10 | 10 |
| 17 | 3 | websearch | remote research assistant OR knowledge management OR documentation specialist full time hiring flexible [ATS domains] | 10 | 10 |
| 18 | 3 | websearch | editorial assistant OR content coordinator New York publishing media full time entry level [ATS domains] | 10 | 10 |
| 19 | 3 | websearch | film programming assistant OR programming coordinator OR film series coordinator New York cinema festival job [open web] | 6 | 6 |
| 20 | 3 | websearch | "script reader" OR "story analyst" OR "coverage" freelance staff remote job 2026 production company [open web] | 10 | 10 |
| 21 | 3 | websearch | A24 careers open positions New York coordinator assistant [open web] | 8 | 8 |
| 22 | 3 | websearch | unscripted development coordinator OR development researcher production company New York hiring 2026 [open web] | 6 | 6 |
| 23 | 3 | websearch | A24 coordinator assistant job application [greenhouse] | 10 | 10 |
| 24 | 3 | websearch | film nonprofit New York program coordinator OR programs associate OR education coordinator hiring [ATS domains] | 10 | 10 |
| 25 | 4 | websearch | AI trainer OR AI evaluator OR data quality analyst remote full time salaried hiring writing research [ATS domains] | 10 | 10 |
| 26 | 4 | websearch | animation production coordinator OR virtual production coordinator New York job opening 2026 [ATS domains] | 10 | 10 |
| 27 | 4 | websearch | production finance coordinator OR production accountant assistant OR film finance analyst New York studio [ATS domains] | 10 | 10 |
| 28 | 4 | websearch | trend researcher OR cultural insights OR strategist research associate New York agency job [ATS domains] | 10 | 10 |
| 29 | 4 | websearch | documentary production coordinator OR archival producer OR research coordinator New York documentary company job [ATS domains] | 10 | 10 |
| 30 | 4 | websearch | creative technologist OR interactive developer OR immersive experience coordinator New York three.js webgl job [ATS domains] | 10 | 10 |
| 31 | 5 | websearch | casting assistant OR casting coordinator New York full time job opening [ATS domains] | 10 | 10 |
| 32 | 5 | websearch | library archives assistant OR archives coordinator New York 35 hours union full time 2026 [ATS domains] | 10 | 10 |
| 33 | 5 | websearch | content operations coordinator OR content associate remote 2026 media streaming company hiring [ATS domains] | 10 | 10 |
| 34 | 5 | websearch | Vice OR Vox OR Topic OR Story Syndicate OR Blumhouse development coordinator producer job New York [ATS domains] | 10 | 10 |
| 35 | 5 | websearch | "research coordinator" OR "research associate" New York hybrid 2026 hiring institute foundation policy [ATS domains] | 10 | 10 |
| 36 | 5 | websearch | Runway OR Captions OR Luma OR Moonvalley creative jobs New York generative video studio hiring [ATS domains] | 10 | 10 |
| 37 | 5 | websearch | studio operations coordinator OR entertainment research analyst New York streaming content insights job 2026 [ATS domains] | 10 | 10 |
| 38 | 5 | websearch | remote writer OR content writer full time 2026 hiring flexible schedule no nights weekends [ATS domains] | 10 | 10 |

## Sources and their status

| domain | status | detail | last checked |
|--------|--------|--------|--------------|
| api.ashbyhq.com | blocked_network | network: ProxyError: HTTPSConnectionPool(host='api.ashbyhq.com', port=443): Max retries exceeded with url: /posting-api/ | 2026-09-06T13:42:56Z |
| api.lever.co | blocked_network | network: ProxyError: HTTPSConnectionPool(host='api.lever.co', port=443): Max retries exceeded with url: /v0/postings/vev | 2026-09-06T13:42:55Z |
| api.smartrecruiters.com | blocked_network | network: ProxyError: HTTPSConnectionPool(host='api.smartrecruiters.com', port=443): Max retries exceeded with url: /v1/c | 2026-09-06T13:42:57Z |
| apply.workable.com | blocked_network | network: ProxyError: HTTPSConnectionPool(host='apply.workable.com', port=443): Max retries exceeded with url: /api/v1/wi | 2026-09-06T13:42:56Z |
| boards-api.greenhouse.io | blocked_network | network: ProxyError: HTTPSConnectionPool(host='boards-api.greenhouse.io', port=443): Max retries exceeded with url: /v1/ | 2026-09-06T13:42:54Z |
| condenast.wd5.myworkdayjobs.com | blocked_network | network: ProxyError: HTTPSConnectionPool(host='condenast.wd5.myworkdayjobs.com', port=443): Max retries exceeded with ur | 2026-09-06T13:43:01Z |
| job-boards.greenhouse.io | blocked_network | network: ProxyError: HTTPSConnectionPool(host='job-boards.greenhouse.io', port=443): Max retries exceeded with url: /the | 2026-09-06T13:42:58Z |
| jobs.ashbyhq.com | blocked_network | network: ProxyError: HTTPSConnectionPool(host='jobs.ashbyhq.com', port=443): Max retries exceeded with url: /promise-stu | 2026-09-06T13:43:00Z |
| jobs.lever.co | blocked_network | network: ProxyError: HTTPSConnectionPool(host='jobs.lever.co', port=443): Max retries exceeded with url: /bustle (Caused | 2026-09-06T13:42:59Z |
| runwayml.com | blocked_network | network: ProxyError: HTTPSConnectionPool(host='runwayml.com', port=443): Max retries exceeded with url: / (Caused by Pro | 2026-09-06T13:43:03Z |
| www.a24films.com | blocked_network | network: ProxyError: HTTPSConnectionPool(host='www.a24films.com', port=443): Max retries exceeded with url: / (Caused by | 2026-09-06T13:43:03Z |
| www.entertainmentcareers.net | blocked_network | network: ProxyError: HTTPSConnectionPool(host='www.entertainmentcareers.net', port=443): Max retries exceeded with url:  | 2026-09-06T13:43:02Z |
| www.idealist.org | blocked_network | network: ProxyError: HTTPSConnectionPool(host='www.idealist.org', port=443): Max retries exceeded with url: / (Caused by | 2026-09-06T13:43:05Z |
| www.linkedin.com | blocked_network | network: ProxyError: HTTPSConnectionPool(host='www.linkedin.com', port=443): Max retries exceeded with url: / (Caused by | 2026-09-06T13:43:06Z |
| www.nytimes.com | blocked_network | network: ProxyError: HTTPSConnectionPool(host='www.nytimes.com', port=443): Max retries exceeded with url: / (Caused by  | 2026-09-06T13:43:04Z |

## Employer coverage

- employers in database: **284**
- employers whose current openings were actually reached: **56**
- status `blocked`: 226
- status `ok_via_search`: 56
- status `unresolved`: 2

## Job funnel

- UNCERTAIN: 90
- tier STRETCH: 44
- tier APPLY_GOOD_FIT: 41
- tier RESEARCH_ONLY: 4
- tier REJECT: 1
