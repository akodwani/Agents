# Phase 3 — Zero-response failure diagnosis

**Research date:** 2026-08-17

## 3.1 First, the base-rate math — because it changes what the zero means

Inputs, all from Phase 1:
- Average applications per posting: **242** ([Interview Guys, 2026](https://blog.theinterviewguys.com/the-average-job-opening-now-gets-242-applications/)); Glassdoor corporate average ~250.
- Application volume up **45% YoY** on LinkedIn, ~11,000/minute, AI-driven ([CNBC, 2026-01-11](https://www.cnbc.com/2026/01/11/ai-dominate-hiring-2026-linkedin-execs-top-tips-stand-out.html)).
- **>90% of employers screen with ATS before a human looks** ([Jobscan](https://www.jobscan.co/blog/resume-portfolio/)).
- Candidate's application count: **single digits.** Call it 8.

Response-rate assumptions (any-response, including rejection-with-a-pulse):
- A *well-matched* applicant to a posted role: ~5–10%.
- A **career changer with zero professional creative credits applying to creative reqs, through ATS, into a market where the reqs ask for 2–4 years**: realistically **0.5–2%**.

Expected number of responses across 8 applications:

| Assumed per-app response rate | Expected responses | P(zero responses) |
|---|---|---|
| 5% (generous) | 0.40 | 66% |
| 2% | 0.16 | 85% |
| 1% (most likely for this profile) | 0.08 | 92% |
| 0.5% | 0.04 | 96% |

**Conclusion: zero responses from eight applications is the single most likely outcome even if nothing whatsoever is wrong with him.** At a 1% rate you would need **~69 applications** to have even a 50/50 shot of one response, and **~300** to be 95% confident of one.

He has not run a failed experiment. **He has run an experiment with no statistical power and is reading the noise as a verdict.** That matters emotionally — the silence is not the market telling him he's untalented — but it must not become an excuse, because the fix is *not* "apply 300 times." See 3.3.

---

## 3.2 Ranked causes

### 1. Sample size — the zero carries almost no information. **Likelihood: ~95% (near-certain, arithmetic)**
Covered above. This explains the *observation* completely. It explains nothing about what to do next.

### 2. Wrong channel for this market. **Likelihood: high, ~80%**
This is the cause that predicts the **future**, and it is the one that matters.
- Every named success in the evidence (Liu Ziyu, Victor Moreno, Zack London) was discovered through **published finished work**, not an application. The one direct hiring-manager quote in the entire corpus describes exactly this: *"If you make great spec commercials, brands will find you."* — PJ Accetturo, CEO of Genre.ai ([The Media Brain](https://themediabrain.substack.com/p/ais-disruption-of-advertising-and)).
- Referrals are 30–50% of US hires from ~7% of applicants; referred candidates are **4x** more likely to get an offer ([ERIN, 2026](https://erinapp.com/blog/enterprise-employee-referral-statistics-you-need-to-know-for-2026/)).
- Cold DM reply rates on X (15–35% when personalized) and LinkedIn (15–25%) versus cold email (1–5%) and versus a job application (~1%) ([Phantom, 2026](https://phantomleads.ai/blog/cold-outreach-statistics-2026); [DMpro](https://www.dmpro.ai/blog/cold-dm-vs-cold-email)). *Caveat: these are B2B sales benchmarks, not creative-hiring benchmarks — directionally useful, not precise. Discount them.*

The channel he chose has the **worst yield of every channel available to him**, by roughly an order of magnitude.

### 3. Portfolio format/venue below bar. **Likelihood: high, ~75%**
Not "the work is bad." The work is **in the wrong container, on the wrong platform, in the wrong medium.** GitHub Pages + written case studies + still-image campaign, in a market that hires off finished video on video platforms. Zero finished start-to-finish pieces. Zero real-brand anchors. See Phase 2.

### 4. Resume/ATS mismatch. **Likelihood: moderate-high, ~65% — but only where ATS exists**
90%+ of employers filter by ATS. A resume reading *KeyBank commercial banking analyst → Ad Sales Revenue & Expense Operations* has essentially **no keyword surface** for a creative req: no "art direction," no "post-production," no "campaign creative," no tool names. At a holdco with a real ATS he is filtered before a human sees the portfolio link.

Important asymmetry: **this cause bites hardest exactly where he was applying (WPP) and barely at all where he should be applying** (independents and AI-native shops small enough that a founder reads the inbox). So fixing the resume is worth doing but is not the unlock — changing *who receives it* is.

### 5. Wrong role targets. **Likelihood: moderate, ~55%**
- The flagship application, **WPP Hex, is a creative *technologist* apprenticeship** — the lane he explicitly ruled out. **16 seats per cycle, globally**, drawn from a self-selected pool. That is a lottery ticket, and it is a lottery for a job he said he doesn't want.
- Nearly every posted role surfaced requires 2–4 years (Wonder Studios) or is mid-to-senior (Brandtech+'s 100 roles). His hard constraint of "early-career-accessible only" removes most of the visible market — correctly.
- The holdcos he was aiming at are in **net contraction**: WPP cutting hundreds more through 2026, Omnicom cutting 4,000 post-IPG on top of 8,200+, 91% of senior agency leaders expecting AI to cut headcount ([Ad Age](https://adage.com/agencies/aa-wpp-plans-hundreds-more-layoffs-by-end-of-2026/); [AI CERTs](https://www.aicerts.ai/news/marketing-agency-layoffs-surge-as-wpp-pursues-ai-efficiency-drive/)).

---

## 3.3 Which single cause does the evidence most support?

Two answers, and conflating them is the trap:

**The literal cause of the observed zero is sample size.** Eight applications produce zero responses ~92% of the time for this profile. Nothing is being measured.

**The cause that will keep it zero is channel.** And this is the actionable answer, because here is the adversarial point that closes the loop:

> Scaling the application channel is *also* the wrong move. Reaching statistical detectability requires ~70–300 applications, into postings that mostly require 2–4 years, at employers in active headcount reduction. He would spend the entire 90 days to buy one or two responses to jobs he isn't qualified for on paper.

**So: the diagnosis is not "apply more" and it is not "you're not good enough." It is that he built an engineering-shaped artifact and pushed it through the lowest-yield channel in the market, at a volume too small to learn anything from.**

Ranked one-liner: **channel (fatal and fixable) > portfolio format (fixable in ~3 weeks) > sample size (explains the past, not the future) > ATS/resume (matters only at big employers he shouldn't target) > role targets (partly self-inflicted via Hex).**

---

## 3.4 The asset nobody has priced

Flagging here because it reshapes Phases 4–6.

He is **inside DIRECTV Advertising, in ad sales revenue and expense operations, right now**, at a company that is actively standing up AI creative capability:
- DIRECTV is rolling out **AI-generated screensaver ads** on Gemini/Gemini Air devices via Glance starting early 2026 ([Engadget](https://www.engadget.com/directv-will-start-replacing-screensavers-with-ai-generated-ads-next-year-224436035.html); [TechSpot](https://www.techspot.com/news/109862-ai-generated-screensaver-ads-coming-directv-gemini-devices.html)).
- DIRECTV Advertising is expanding **pause ads with new creative capabilities** and creative-optimization tooling ([PubMatic partner interview](https://pubmatic.com/blog/partner-perspectives-directv-advertising-on-modernizing-the-tv-experience/)).
- DIRECTV executives publicly discussing CTV ad *creative* and generative AI making "TV-quality creative" cheaper ([Mike Shields, DIRECTV on CTV ad creative](https://mikeshields.substack.com/p/directv-on-why-ctv-ad-creative-still)).

Every AI artist competing for these jobs is a former hobbyist. **Almost none of them can read a campaign P&L, explain how a CTV ad buy is priced, or talk to a client about why a creative variant underperformed.** He can. That is not a soft transferable skill — in a market where the whole pitch of AI creative is "faster and cheaper campaign output," it is the scarcer half of the pair.

He has been treating the day job as the thing to escape. It is also the only warm network he has in the industry he wants to enter, and it is a company publicly building the exact capability he wants to work in.
