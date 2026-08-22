# PASS 1 — Performance data forensics
No external tools used. Every number below is computed from the 10 rows in the brief.

---

## 1. Rebuilt table with derived metrics

| ID | Plat | Format | Len | Spend | TS | 6s | CTR | Trials | Paid | **CPA/paid** | CPA/trial | **T→P** | Paid/$1k | TS×6s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C01 | Meta | UGC problem/solution | 28s | $4,800 | 36% | 24% | 1.7% | 267 | 59 | **$81.36** | $17.98 | **22.1%** | 12.29 | 8.6 |
| C02 | Meta | Static screenshots | 15s | $3,200 | 25% | n/a | 0.9% | 133 | 35 | $91.43 | $24.06 | 26.3% | 10.94 | n/a |
| C03 | Meta | Founder talking head | 35s | $2,700 | 18% | 11% | 0.6% | 54 | 12 | $225.00 | $50.00 | 22.2% | 4.44 | 2.0 |
| C04 | TikTok | Creator skit | 23s | $5,100 | 45% | 31% | 2.4% | 300 | 42 | $121.43 | $17.00 | 14.0% | 8.24 | 14.0 |
| C05 | TikTok | Screen-record demo | 21s | $4,400 | 39% | 27% | 2.1% | 338 | 71 | **$61.97** | $13.02 | 21.0% | 16.14 | 10.5 |
| C06 | TikTok | AI avatar explainer | 30s | $3,000 | 22% | 15% | 0.8% | 64 | 9 | $333.33 | $46.88 | 14.1% | 3.00 | 3.3 |
| C07 | YTS | Before/after | 32s | $4,700 | 38% | 22% | 1.3% | 235 | 63 | **$74.60** | $20.00 | **26.8%** | 13.40 | 8.4 |
| C08 | YTS | Tutorial (students) | 45s | $3,900 | 33% | 29% | 1.1% | 112 | 13 | $300.00 | $34.82 | 11.6% | 3.33 | 9.6 |
| C09 | Meta | Creator testimonial | 26s | $5,500 | 41% | 26% | 2.0% | 306 | 67 | **$82.09** | $17.97 | 21.9% | 12.18 | 10.7 |
| C10 | TikTok | Trend remix | 18s | $3,800 | 50% | 35% | 1.9% | 174 | 20 | $190.00 | $21.84 | 11.5% | 5.26 | 17.5 |

**Account total:** $41,100 → 1,983 trials → 391 paid starts. **Blended CPA $105.12 against a $90 target — the account is 17% over.**

### Rank by CPA/paid start
`C05 $61.97 · C07 $74.60 · C01 $81.36 · C09 $82.09` ‖ **$90 target line** ‖ `C02 $91.43 · C04 $121.43 · C10 $190.00 · C03 $225.00 · C08 $300.00 · C06 $333.33`

**Six of ten rows are over target.** Only four clear it.

### Rank by trial→paid
`C07 26.8% · C02 26.3% · C03 22.2% · C01 22.1% · C09 21.9% · C05 21.0%` ‖ `C06 14.1% · C04 14.0% · C08 11.6% · C10 11.5%`

Note the shape: six rows cluster at 21–27%, four collapse to 11–14%. There is almost nothing in between. This is not a gradient — it is two populations.

---

## 2. The finding this whole submission rests on

**The top-4 by thumbstop and the top-4 by trial→paid share zero rows.**

- Top-4 thumbstop: C10, C04, C09, C05
- Top-4 trial→paid: C07, C02, C03, C01
- Overlap: **none**

And the cleanest cut in the data:

> **All four rows that beat the $90 target sit in a 36–41% thumbstop band. Every row outside that band missed target.**
> In band: C01 (36%), C07 (38%), C05 (39%), C09 (41%) → $81, $75, $62, $82.
> Below it: C03 18%, C06 22%, C02 25%, C08 33% → $225, $333, $91, $300.
> Above it: C04 45%, C10 50% → $121, $190.

Perfect separation, 10/10 rows. `[caveat]` n=10, one test window, no confidence intervals — this is a descriptive pattern, not a law, and the band boundaries are almost certainly not exactly 36 and 41. I am not proposing "target 38% thumbstop" as a media rule. I am proposing what it implies about *mechanism*, which is testable and is what the scripts are built on:

**There are two separate ways to lose money here, and they need opposite fixes.**

| Failure mode | Rows | Signature | Fix |
|---|---|---|---|
| **Nobody stops** | C03, C06 | TS 18–22%, CTR 0.6–0.8%, but T→P is *fine* (22.2%, 14.1%) | The argument works. The format is invisible. Re-house it. |
| **Everybody stops, nobody pays** | C04, C10 | TS 45–50%, CTR up to 2.4%, T→P collapses to 11–14% | The format works. It recruited the wrong person. Change who it stops. |

Correlations across all ten rows, directional only at n=10:

```
thumbstop vs trial→paid%   r = -0.30
6s hold   vs trial→paid%   r = -0.45   (n=9; C02 has no hold figure)
CTR       vs trial→paid%   r = -0.20
length    vs paid CPA      r = +0.56
```

Every attention metric runs **against** conversion quality. More attention, and more retained attention, is associated with a *worse* trial. That is the opposite of how these ads are usually optimized.

---

## 3. Which formats get cheap attention but don't convert

**C10 trend remix — the most efficient attention purchase in the entire test, and the second-worst CPA.**
50% thumbstop and 35% 6s hold, both best in the set. $21.84 per trial, mid-pack. Then it falls off a cliff: **11.5% trial→paid, dead last.** 174 trials, 20 paid.
Stated in money: C05 produced a paid start for every $62. Had C10's $3,800 run through C05's format it would have returned ~61 paid starts instead of 20. **C10 cost the account roughly 41 paid starts.**
Why: "Things I stopped doing after using AI" recruits people interested in *AI as a topic*. It never shows LoopNote doing anything. The viewer's payoff is the list, and they got it for free in the ad.

**C04 creator skit — highest CTR in the test (2.4%), third-worst trial→paid (14.0%).**
45% thumbstop, 31% hold, $17.00 per trial — cheaper trials than C01 or C09. 300 trials, the second-highest trial count in the set. Only 42 paid. The click is real and the intent behind it is not. "POV: your boss asks what was decided in the meeting" is a *joke about* the pain. Laughing at a problem and paying to solve it are different transactions.

**C08 tutorial — worth separating out, because it fails differently than it looks.**
Its 6s hold is 29%, third best. Hold-through (6s ÷ thumbstop) is 88%, **the best in the entire test** — nearly everyone who stopped stayed. And it converted at 11.6%. People watched the whole thing and did not buy. It is 45s, the longest, but length is not the primary defect: the audience is students, and the framing ("3 ways students use LoopNote") teaches features to a segment with low willingness to pay a subscription. Recutting it shorter would not fix it.

---

## 4. Which formats convert trial→paid best, and what they share

`C07 26.8% · C02 26.3% · C01 22.1% · C09 21.9% · C05 21.0%`

**The mechanism: does the product's output appear on screen, or does someone describe it?**

| Cohort | Rows | Spend | Paid | **CPA** | **T→P** | Avg TS |
|---|---|---|---|---|---|---|
| **Shows the transformation** | C01, C02, C05, C07, C09 | $22,600 | 295 | **$76.61** | **23.1%** | 36% |
| **Talks about it** | C03, C04, C06, C08, C10 | $18,500 | 96 | **$192.71** | **13.6%** | 34% |

**2.5× on CPA. Average thumbstop is nearly identical across both cohorts (36% vs 34%) — so this is not an attention effect. It is entirely downstream of the click.**

C08 is the one row that could be argued into either cohort — a tutorial does put the app on screen. Scored as "shows," the split is still $86.04 vs $175.90. The distinction that keeps it in "tells": a tutorial demonstrates *features*, it doesn't stage a *before→after*. That difference is exactly what the next principle is about.

**The three things the winners share:**

1. **A two-state structure — mess in, structure out.** C05 ("rambling voice memo → task list") and C07 ("before vs. after meeting notes") are #1 and #2 on CPA and #1 on trial→paid. Both are literally two-state ads. C02 shows only the *after* — "AI notes in one tap" — and lands at $91.43 with the lowest CTR in the set, 0.9%. The clean output on its own does not sell. **The contrast is the product.**
2. **A specific number in the hook.** C09 ("I imported 120 voice notes and found 18 tasks") — $82.09 at 41% thumbstop, the highest thumbstop of any winner. C01 ("4 tabs open") — $81.36. These are the two biggest budgets in the test ($5,500 and $4,800), so they held up at the largest scale tested. The abstract-claim rows: C02 "AI notes in one tap" $91.43, C06 "Meet your AI productivity assistant" $333.33.
3. **A pain that costs the viewer something specific,** not a pain that's funny. C01 opens on tabs left open after a meeting. C04 opens on a boss asking a question. Both are meeting-aftermath pains. C01 frames it as a cost; C04 frames it as a bit. $81 vs $121.

## 5. What the losers share

C03 founder head · C06 AI avatar · C08 student tutorial · C10 trend remix · C04 skit.

Common thread: **a person or a persona is the content, and LoopNote is a subject they mention.** In the winners the product is the content and the person is the frame around it.

**But do not read C03 as "the founder message failed."** C03 converts trial→paid at **22.2% — 4th best of ten, above C05 and C09.** It only produced 54 trials, on the worst thumbstop (18%) and worst CTR (0.6%) in the test. Everyone who made it through converted at a healthy rate. Its argument is fine; its container is invisible. That is a real, non-obvious asset sitting in the "losers" pile.

---

## 6. Platform read

| | Spend | Trials | Paid | CPA/paid | CPA/trial | T→P |
|---|---|---|---|---|---|---|
| Meta | $16,200 | 760 | 173 | **$93.64** | $21.32 | **22.8%** |
| TikTok | $16,300 | 876 | 142 | $114.79 | **$18.61** | **16.2%** |
| YT Shorts | $8,600 | 347 | 76 | $113.16 | $24.78 | 21.9% |

- **Meta is cheaper per paid start. TikTok is cheaper per trial.** TikTok buys the most trials per dollar in the account and loses the most of them.
- **The trial→paid gap is biggest on TikTok: 16.2% vs Meta's 22.8%** — a 6.6pt spread. Same product, same offer, same landing page. The difference is who the creative recruited.
- **But TikTok is bimodal, not bad.** C05 at $61.97 is the single best row in the whole test, on TikTok. The other three TikTok rows ($121, $190, $333) are three of the five worst. TikTok is not a worse platform — it punishes entertainment framing and rewards demo framing *harder* than Meta does. The upside there is larger than Meta's and so is the downside.

**Reallocation, for scale:** the six over-target rows consumed $21,700. Run at the four winners' blended CPA of $74.62, that budget returns ~291 paid starts instead of 131. Account total goes from 391 paid at $105.12 to ~551 at **$74.62 — 17% over target to 17% under**, with no change in spend, offer, or landing page. Creative selection alone is the whole gap. `[assumption]` this treats CPA as stable under reallocation, which ignores auction and saturation effects; it is a scale illustration, not a forecast.

---

## 7. THE CONSTITUTION — 7 principles, each traceable to rows

Every script in Pass 5 must obey these. Any script that violates one gets killed or rewritten.

**P1 — Stop the right person, not the most people.**
All four sub-$90 rows sit at 36–41% thumbstop (C01, C07, C05, C09). Below the band you are not seen (C03 18% → $225; C06 22% → $333). Above it you have bought entertainment-seekers (C04 45% → $121; C10 50% → $190). A hook that would stop anyone is a defect, not an achievement.

**P2 — Show the transformation. Never describe it.**
Shows-cohort $76.61 CPA / 23.1% T→P (C01, C02, C05, C07, C09) vs tells-cohort $192.71 / 13.6% (C03, C04, C06, C08, C10). Average thumbstop is the same in both. If a line could be delivered with the app off screen, it is the wrong line.

**P3 — The mess is the hook. The clean output is the payoff. You need both.**
C05 and C07, the only two explicitly two-state ads, are #1 and #2 on CPA and #1 on T→P (C07, 26.8%). C02 shows only the clean end state and gets the lowest CTR in the test (0.9%) at $91.43. Open on the mess.

**P4 — Put a real number where a claim would go.**
C09 (120 notes → 18 tasks) $82.09 at 41% TS; C01 (4 tabs) $81.36 — both at the two largest budgets in the test. Abstract framing: C02 "one tap" $91.43, C06 "your AI productivity assistant" $333.33. A number is the cheapest proof device available and it survives scale.

**P5 — Clicks are not intent. Ignore CTR when choosing a hook.**
C04 has the best CTR in the test (2.4%) and 14.0% T→P. C02 has the worst CTR of any Meta row (0.9%) and 26.3% T→P, second best. Across the set CTR runs mildly against T→P (r = −0.20). Nothing in this account gets selected on CTR.

**P6 — The two failure modes need opposite fixes; don't apply the wrong one.**
C03's message converts (22.2% T→P, 4th of 10) inside a container nobody watches (18% TS, 0.6% CTR) — keep the argument, change the format. C08 has the best hold-through in the test (88%) and the second-worst T→P (11.6%) — keep nothing about the targeting, the recut won't save it. Diagnose before rewriting.

**P7 — Play to each platform's actual bias.**
Meta $93.64/paid at 22.8% T→P; TikTok $114.79/paid at 16.2% T→P but holds the best single row in the test (C05, $61.97). TikTok gets the demo. Meta gets the proof-and-testimonial structures (C01, C09 both land $81–82 there). Do not run the same cut on both and call it a test.

---

## 8. Where this points the three scripts

- **C05 lineage (TikTok, screen-record, two-state):** best row in the test, cheapest trials, and it is the format TikTok rewards. Non-negotiable — one script must be this.
- **C09 + C01 lineage (Meta, numeric proof + felt pain):** $82.09 and $81.36, at the two largest budgets, on the platform with the better T→P. Second script.
- **C07 lineage (before/after, 26.8% T→P — best conversion in the test):** ran on YT Shorts, and the deliverable is Meta/TikTok. **Porting it, and flagging the port.** Its mechanism (two-state contrast) is platform-independent and is the same mechanism that makes C05 win on TikTok; the risk in porting is the 32s length, which I will cut hard.
- **The C03 salvage:** its argument converts at 22.2%. Somewhere in the three scripts, the founder's actual reason for building this should survive — spoken over a screen recording, not into a lens.

---

## PASS 1 CHECKPOINT

**Produced:** Full rebuilt table with 6 derived metrics; CPA and T→P rankings; the zero-overlap finding; the 36–41% thumbstop band; shows-vs-tells cohort split ($76.61 vs $192.71); two-failure-mode diagnosis; platform read; 7 row-traceable principles.

**Unsure about:** n=10 with no variance data, so the thumbstop band is descriptive rather than predictive and I've labeled it that way. The shows/tells split depends on how C08 is classified — I show the number both ways and it holds either way. Reallocation math ignores auction saturation and is labeled.

**Need from Avi:** nothing blocking.

**Proceeding to Pass 2** (audience pain research — web).
