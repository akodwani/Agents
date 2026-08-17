# Phase 1 — Seat Census (Engine step E1)

**Run date:** 2026-08-17
**Window:** postings surfaced Feb–Aug 2026 (last ~6 months)
**Filter applied:** entry-accessible only — i.e. a candidate with 0 professional creative credits and ≤3 years total work history can plausibly be screened in.

---

## 0. METHOD AND ITS LIMITS (read this before trusting any count)

This environment's network egress policy blocks direct page fetches. Every attempt to
retrieve a posting page, an ATS board (`job-boards.greenhouse.io`, `jobs.ashbyhq.com`),
a publisher (Substack, Built In, Reddit, Wikipedia) returned `EGRESS_BLOCKED` / HTTP 403
at the proxy CONNECT stage. Verified:

```
curl https://job-boards.greenhouse.io/  -> CONNECT tunnel failed, 403
curl https://www.builtinnyc.com/        -> CONNECT tunnel failed, 403
curl https://www.reddit.com/r/advertising/ -> CONNECT tunnel failed, 403
WebFetch en.wikipedia.org               -> EGRESS_BLOCKED
```

**Consequence for evidence grading.** All evidence below is *search-surfaced*: the search
index returned the posting's title, employer, URL, and indexed body text. I could not open
a single posting to confirm it is still live or read its full requirement list. So every
claim in this research carries one of three labels, used consistently through all six phases:

| Label | Meaning |
|---|---|
| **[V]** verified-in-index | Specific employer + title + specific requirement/salary text returned by search. High confidence the posting exists and says this. |
| **[C]** count-only | Aggregator-reported posting count with a date. Admissible per the research-discipline rules *for counts only*. Inflated by duplicates and title noise — never treated as a supply of qualifying seats without a discount, and the discount is labeled modeled. |
| **[M]** modeled | My inference. Assumptions stated inline. |

Where the search index returned nothing usable, the file says **"no representative data
found."** That happens repeatedly and it is a finding, not a gap to paper over.

---

## 1. Lane 1 — AI Artist / AI creative producer

### Raw counts [C]
| Source | Query | Count | Date |
|---|---|---|---|
| ZipRecruiter | "Ai Artist" (national) | listings present, band $127k–$200k | Aug 2026 |
| ZipRecruiter | "Ai Artist" NYC | band $138k–$230k | Oct 2025 |
| Glassdoor | "ai creative artist" NYC | 1,308 | Feb 2026 |
| ZipRecruiter | "Generative Ai Artist" | band $95k–$180k, avg $111,753 | Apr 2026 |

The Glassdoor 1,308 is title-noise: the string matches any "creative" or "artist" role at any
company using "AI" anywhere in the body. Discount is severe. [M]

### Exemplar postings [V]
1. **Industrial Color / CoCreativ — "AI Artist (freelance to hire)", New York, NY.**
   Mid-to-senior AI Image & Video Artist. **Requires 5+ years in film, commercial production,
   VFX, animation, motion design, editing, or post-production.** Tool list: Veo, Kling,
   Seedance, Runway, Luma, Midjourney, Flux, ComfyUI **plus** After Effects, Nuke, Resolve,
   Premiere, Maya, C4D, or Houdini. "Ability to take projects from concept through final
   delivery." Comp $110k–$135k.
   — mediabistro.com/jobs/3541086246-ai-artist-freelance-to-hire ; builtinnyc.com/job/ai-artist-freelance-hire/9605702 ; careerbuilder.com/job-details/ai-artist-freelance-to-permanent-role-new-york-ny
2. **"AI Creative Producer"** — builtin.com/job/ai-creative-producer/7940664 (employer not
   resolvable without fetch).
3. **"Junior AI Creative Producer wanted"** — posted 2026-06-22 via a Glasgow School of Art
   careers feed; "intersection of creative concepting, brand interpretation, AI image-making,
   and workflow development." **Non-US, so out of the NYC/remote universe unless remote —
   unverifiable.** gsacareers.wordpress.com/2026/06/22/junior-ai-creative-producer-wanted/
4. **"AI Generalist Artist"** roles — generate and refine high-quality visual assets, **ComfyUI
   named as the platform**. Search-surfaced without a resolvable employer.
5. **Monks — "Senior Creative Developer, AI"** and **"AI Solution Director"**, New York.
   Both senior. monks.com/careers/new-york/content/senior-creative-developer-ai

### E1 finding for Lane 1
**Entry-accessible qualifying postings found: 0–1.** The one posting whose requirements are
fully legible (Industrial Color) is explicitly 5+ years and explicitly requires a finishing
NLE/compositor the candidate does not have. Every other legible AI-artist seat in the census
is senior. The lane's *paid staff seats in NYC are a mid-career market*, and the "AI-native,
no traditional craft" candidate is priced against people with a decade of post-production
behind them who also learned the AI stack. This corroborates the prior finding (portfolio below
staff bar) but sharpens it: **the problem is not only his portfolio, it is that the rung
doesn't exist at staff level.** The lane's accessible surface is freelance/marketplace, not
employment — carried forward to E6.

**Title trap:** "AI Artist" in this market means *senior compositor/finisher who also prompts*.
The title reads entry-level to an outsider and is not.

---

## 2. Lane 2 — Creative technologist

### Raw counts [C]
| Source | Query | Count | Date |
|---|---|---|---|
| Indeed | "creative technologist" NYC | **48** (7 new that day) | 2026-07-23 |
| Glassdoor | "creative technologist" NYC | **7** | Jun 2026 |
| LinkedIn | "creative technologist" NY state | 250 | Aug 2026 |
| ZipRecruiter | rate, NYC | avg **$53.76/hr**, band $52.88–$56.30 | 2026-07-24 |

The 7 (Glassdoor, tight title match) versus 250 (LinkedIn, loose match) spread is the whole
story: the true NYC market for the actual title is single-digit-to-low-double-digit at any
moment. [M]

### Exemplar postings [V]
1. **Publicis Groupe — "Creative Technologist: AI Prototyping & Innovation", New York.**
   **3–6 years in AI production required.** Researching and implementing generative AI tools,
   prototyping production pipelines. — bebee.com listing of the Publicis req.
2. **Microsoft — "Creative Technologist".** **MS in CS + 3+ years**, or BS + more. Shipping
   production code. — glassdoor.com/job-listing/creative-technologist-microsoft
3. **Wasserman — "Creative Technologist", Brooklyn/Dumbo (R5039-1).**
   teamwass.wd5.myworkdayjobs.com — seniority not resolvable without fetch.
4. **THE·TEAM — "Creative Technologist"** — builtin.com/job/creative-technologist/10046886
5. **Creative Technologist Intern** roles exist: "the team's builder and maker, bringing
   technical fluency to turn concepts, research findings, and innovation briefs into tangible
   prototypes." Intern-grade — fails the $50k floor as a destination, but is the only
   genuinely open rung surfaced.

### Requirement profile across the lane [V]
Consistent across postings: production-quality code for web experiences, interactive tools,
AR, AI-driven output; rapid interactive prototypes; **Three.js / WebGL / React**; p5.js,
Processing; Arduino/Pi physical computing; **hands-on AI API and LLM application building,
prompt engineering**.
— creativedevjobs.com/jobs/creative-technologist ; jobs.interactiveimmersive.io/job/creative-technologist-25 ; jobicy.com/careers/creative-technologist

### E1 finding for Lane 2
**Entry-accessible qualifying postings found: 1–2 (both intern-grade).** The requirement
*content* is the closest match in the whole census to what he has already built — Three.js
app shipped, LLM/agent tooling built, AI pipelines built. But the requirement *level* is
3–6 years or a CS master's. This is the lane where **his artifacts clear the bar and his
résumé does not**, which is a different failure mode from Lane 1 and matters for the revival
attempt in Phase 5.

**Title trap, both directions:** at Microsoft "creative technologist" is staff software
engineering; at agencies it can be a $53/hr freelance prototyper. Same title, different jobs.

---

## 3. Lane 3 — AI-enabled marketing / content roles

### Raw counts [C]
| Source | Query | Count | Date |
|---|---|---|---|
| Glassdoor | "social media content creator" NYC | 195 | Aug 2026 |
| Glassdoor | "social producer" NYC | 166 | May 2026 |
| Glassdoor | "content producer" NYC | 79 | Jul 2026 |
| Glassdoor | "branded content video producer" NYC | 24 | Jun 2026 |
| Glassdoor | "social media" NYC (all levels) | 807 | Aug 2026 |
| SimplyHired | "branded content producer" NYC | 37 | Aug 2026 |
| ZipRecruiter | "Social Media Producer" (national band) | $51k–$104k | May 2026 |
| ZipRecruiter | "Video Content Producer" NYC avg | $82,597 | 2026-07-05 |

This is, by volume, **the largest entry-accessible surface in the census by roughly an order
of magnitude.** Even discounting hard for title noise and seniority, hundreds of NYC seats
per quarter carry 0–2 year requirements. [M on the discount, C on the raw counts]

### Exemplar / requirement evidence [V]
1. A paid in-office **summer social content program**: trainees "ideate, produce, publish, and
   engage" across TikTok/IG/YouTube; **listed top skills: AI Tools, CapCut, video editing.**
2. **"Content & Prompt Operations Specialist"** — manages AI-assisted content workflows,
   writing prompts, drafting content, improving AI outputs. This is a *new title category*
   that did not exist in the last cycle and is native to what he does.
3. Postings requiring "**AI Proficiency** — demonstrated experience using AI tools like LLMs
   for research and AI-driven video/audio editing... to enhance productivity and creative
   output."
4. **Social Content Producer** roles: "plan, create, and design motion and graphic assets,"
   in-house teams "producing thousands of ads monthly."
5. NYC tech startup launching an **in-house media studio** producing podcast/YouTube content
   about **AI agents and vibecoding** — a posting whose subject matter is literally his other
   portfolio object.
   — builtinnyc.com/jobs/content/entry-level ; glassdoor NYC content/social searches above

### E1 finding for Lane 3
**Entry-accessible qualifying postings: ≥5 comfortably — this is the only lane where supply
is not the binding constraint.** Note the recurring requirement pair: **CapCut / editing +
AI tools.** The finishing gap is a *listed requirement* here, not an implied one.

**Title trap:** "Growth creative" and some "content producer" reqs are performance-marketing
media-buying roles measured on CAC, not making roles. Screen each posting for whether it
owns spend or owns assets.

---

## 4. Lane 4 — Creative strategist

### Raw counts [C]
| Source | Query | Count | Date |
|---|---|---|---|
| Glassdoor | "junior strategist" NYC | **91** | Jan 2026 |
| Indeed | "junior strategist digital advertising agency" NYC | 351 | 2026 |
| LinkedIn | "entry level brand strategy" US | 374 | Aug 2026 |
| ZipRecruiter | "junior creative strategist" NYC avg | **$101,613** (band $74.9k–$112.7k) | 2026-07-16 |
| ZipRecruiter | "creative strategist" NYC | band $74k–$150k | Aug 2026 |
| Glassdoor | "meta ads specialist" remote | 88 | Jul 2026 |

### The exemplar that reframes this lane [V]
**Mammoth Brands (Harry's / Flamingo parent) — "Junior Creative Strategist," New York, NY.
$90,800–$113,500 + equity. In-office Tue/Wed/Thu.**
Duties as indexed:
- "close partner to the Creative Director"
- "sitting in brainstorms, **reading performance data**, and translating approved concepts
  into tight briefs that editors and production can execute"
- "turning approved concepts into detailed briefs in ClickUp, and specifying exactly what's
  needed (**footage, VO, graphics, references, format, length**) so production can move forward"
- "spending time in **Meta Ads Manager and creative analytics tools** to surface what's
  winning and provide **weekly insights** to the Creative Team"

Sources: job-boards.greenhouse.io/mammothbrands/jobs/7868418 ;
jobs.thrivecap.com/companies/mammoth-brands-2/jobs/76845470-junior-creative-strategist ;
ziprecruiter.com/c/Mammoth-Brands/Job/Junior-Creative-Strategist/-in-New-York,NY ;
lensa.com/job-v1/mammoth-brands/new-york-ny/junior-creative-strategist

**This req is a near-line-by-line description of the candidate's actual current job plus his
actual hobby.** Reading performance data and writing production-executable briefs specifying
references and format *is* revenue-and-expense-operations-brain applied to creative, and
building a 46-asset reference system *is* the "references" deliverable. Flag loudly for Phase 3.

### Other exemplars [V]
- **Mammoth Brands — "Creative Strategist, Growth Marketing," NYC** (a second, adjacent req at
  the same company).
- **Prophet — "Senior Creative Strategist," NYC** (senior; out of scope, marks the ceiling).
- **M Booth — Digital Strategist, Lifestyle,** NYC. **M+A — Associate, Creative Resourcing,** NYC.
- **24 Seven Talent — "Creative Strategist, Meta, Paid Social."**
- **"Junior Creative Strategist (Meta Ads & AI Specialist)"** — onlinejobs.ph, i.e. this junior
  title is *also* being offshored. Noted as a wage-pressure signal for Phase 5.

### Two distinct sub-lanes, and they screen differently [V]
1. **Traditional agency brand/comms strategist** — screens on thinking, a written strategy
   POV, culture; heavily fed by portfolio schools and internships. Requirement text emphasizes
   "study or experience in advertising, creative writing, or English literature."
2. **Performance / growth creative strategist (DTC + performance agencies)** — screens on
   *ad performance literacy*. Documented requirement: "ability to analyze ad creative
   performance data and translate findings into new strategies," "deep knowledge of Meta Ads
   and how creative performs in-platform," direct-response copy principles, Meta Ads Manager
   fluency, **"Creative & AI Fluency — proficiency in the modern AI creative stack (Midjourney,
   ChatGPT for copy, AI video tools)."** Documented proof object: **"3 to 5 of their best ads
   with the numbers (spend, ROAS or CPA, how long they ran) and their hypothesis behind it."**
   Documented gate posture: **"the DTC paid media industry in 2026 is dominated by
   practitioners who learned on the job... Academic backgrounds are rarely decisive.
   Portfolio of results, account access for audit, and practical interview tasks are the most
   reliable evaluation methods."**
   — mhigrowthengine.com/blog/dtc-creative-strategist-role/ ; 3searchgroup.com/creative-strategist/ ;
   constanthire.com/creative-strategist-recruitment-agency ; marketerhire.com/g/roles/dtc/creative-strategist ;
   mediabistro.com/jobs/3419471580-creative-strategist-meta-paid-social

Also surfaced: **"Creative Strategists are in high-demand, however, as the role itself is still
fairly new to the market, the talent pool is small."** — 3searchgroup.com/creative-strategist/
(recruiter source, so self-interested; treat as directional, not measured.)

### Acquirable credential [V]
**Meta Certified Creative Strategy Professional** — $150, 90-minute multiple-choice exam,
professional tier, valid 1 year; published prep guidance 20–30 hours for an intermediate
practitioner (40–60 for a true beginner). Training materials free.
— stackmatix.com/blog/meta-ads-certification ; livecertification.com/cert/mkt-meta ;
markampus.com/blog/free-meta-advertising-certifications-2026/
This is the only credential in the entire census that is (a) named in postings and (b)
acquirable inside the 90-day window on his budget.

### E1 finding for Lane 4
**Entry-accessible qualifying postings: ≥5, concentrated in the performance/growth sub-lane,
and the titles literally say "Junior."** Comp band is the highest of any accessible lane in
the census ($90.8k–$113.5k at the named exemplar vs a $50k floor). Sub-lane 1 (traditional
agency strategy) is the gatekept one; sub-lane 2 is the open one.

**Title trap:** "Creative strategist" at a holding company = brand planning, portfolio-school
pipeline. "Creative strategist" at a DTC brand or performance shop = ad-performance analyst
who briefs creative. Same words, opposite doors.

---

## 5. Lane 5 — Junior under a creative director

### Raw counts [C]
| Source | Query | Count | Date |
|---|---|---|---|
| Glassdoor | "junior art director" NYC | 297 | May 2026 |
| Glassdoor | "junior art director" NYC | 257 | Mar 2026 |
| Glassdoor | "art director" NYC | 261 | Aug 2026 |
| Glassdoor | "entry level advertising" NYC | 1,624 | Jun 2026 |
| ZipRecruiter | "junior art director" NYC hourly | avg **$27.26/hr** (band $15.77–$42.07) | Aug 2026 |
| ZipRecruiter | "entry level creative" national | **$38k–$58k** | May 2026 |

$27.26/hr ≈ $56.7k at 2,080 hours — clears the $50k floor, but the band's bottom
($15.77/hr ≈ $33k) does not, and the national entry-creative band $38k–$58k straddles it.

### Requirement profile [V]
"Outstanding portfolio demonstrating clean, contemporary design principles, strong typography,
layout, and photography direction"; "portfolio submission is often a requirement"; "solid
background in visual design, branding, and creative concept development, typically supported
by a bachelor's degree in graphic design"; **"proficiency in Adobe Creative Suite (Photoshop,
Illustrator, InDesign)"** and print/digital production familiarity.
— glassdoor NYC junior-art-director searches; ziprecruiter junior-art-director NYC

### The structural finding [V]
- **MediaPost, 2026-06-09 — "How Cutting Entry-Level Agency Jobs Impacts The Entire Industry":**
  a **4A's and DBC** report suggests agencies "have killed the traditional 'apprenticeship
  model' the industry has used to develop the next generation of leaders."
  mediapost.com/publications/article/415632/
- **Forrester:** US ad agencies will automate **7.5% of jobs by 2030, most of them
  entry-level**. AI adoption is replacing work "typically handled by interns and junior
  employees."
- **eMarketer — "AI cuts into junior advertising jobs, raising long-term talent risks":**
  agencies risk a "hollowed-out" middle for the next decade.
  emarketer.com/content/junior-ad-employees-disappearing--their-relevance-endures
- **Creative Boom, 2026 — "what creative recruiters are looking for in juniors":** "It's tougher
  than ever to get hired as a junior"; "the days when a design degree was enough... are long
  gone"; **"studios hire people, not portfolios"** — i.e. the screen is relational, which is
  precisely the asset he lacks. creativeboom.com/tips/in-2026-heres-what-creative-recruiters-are-looking-for-in-juniors/
- Holdco consolidation (**IPG/Omnicom**) is producing cuts "across the board."
- Named entry programs are **internship-shaped and calendar-locked**: Ogilvy Group 2026 Creative
  Summer Internships, NYC, **application deadline Jan 5** — i.e. the next cycle's door closed
  seven months before this analysis ran.

### E1 finding for Lane 5
**Entry-accessible qualifying postings: nominally many (hundreds by count), functionally the
most contested and structurally contracting rung in the census.** The count is real; the door
is not, for someone with no book, no Adobe, no school pipeline, and no relationships. The
posting count is a *trap indicator* here — high volume, near-zero conversion for this
specific profile. Carried into Phase 3 and Phase 5.

---

## 6. Phase 1 summary table

| Lane | Entry-accessible qualifying postings [M, from C+V] | Comp at entry [V] | Level of the legible seats |
|---|---|---|---|
| 1 AI Artist | **0–1** | $110k–$135k (but 5+ yrs) | mid/senior only |
| 2 Creative technologist | **1–2, intern-grade** | $53.76/hr freelance; staff = 3–6 yrs | mid/senior + intern, nothing between |
| 3 AI-enabled marketing/content | **many (≥5, order of magnitude larger)** | $51k–$104k; NYC video producer avg $82.6k | genuinely junior |
| 4 Creative strategist (performance sub-lane) | **≥5, titled "Junior"** | **$90.8k–$113.5k** at named exemplar | genuinely junior |
| 5 Junior under a CD | high count, contracting rung | $27.26/hr avg ≈ $56.7k | junior by title, gatekept by pipeline |

## 7. What Phase 1 changes about the working assumption

The candidate's stated aim (Lane 1) has, in this census, **the fewest accessible seats of any
of the five lanes and the highest experience floor.** The two lanes with real junior doors are
3 and 4. Lane 4's named exemplar pays roughly double the salary floor and asks for exactly the
skills his day job has been building for five months. That is the Phase 1 headline, and Phases
3–4 will test whether it survives a competitive read.

## 8. Open questions for later phases
- Do Lane 4 performance-strategist screens accept *self-run* ad spend as "portfolio of
  results," or only client/employer accounts? (Determines whether a ~$150/mo self-funded test
  is a valid proof object.) → Phase 2
- Who is actually in the Lane 3 and Lane 4 applicant pools? → Phase 3
- Can Lane 2 be revived on artifact strength despite the years floor? → Phase 5
- Is the Lane 1 freelance/marketplace surface (QuickFrame Creator Collective, 5,000+ vetted
  creators/production companies; Upwork AI-video demand) a real door or a race to the bottom? → Phase 2/E6
