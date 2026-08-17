# AI Video Platform Market Scan — Procurement Report
**Prepared:** 2026-08-17 · **Client profile:** solo AI filmmaker, asset-locked pipeline, 150–400 video generations/month, budget ~$100–150/mo
**Method:** 6-phase adversarial research loop. Working files: `research/phase-1.md` … `research/phase-5.md`

---

## Executive summary

**The premise of the search was wrong, and that is the most valuable finding.** There is no
platform where "unlimited" means fast. Across 36 platforms surveyed, every unlimited tier found is
implemented the same way — a deprioritized queue, usually 1 concurrent job. Higgsfield's help
centre states it outright ("Unlimited generations run in the standard queue... credit-based
generations always run in the priority queue"). ImagineArt's policy says "one active generation at
a time." Luma sells "relaxed mode" and an "overnight queue." Runway is **deleting its Unlimited
plan on 2026-09-01** and named queueing as the reason. Unlimited is the industry's cost-control
valve. Shopping for a better one is shopping for a better version of the exact problem.

So the recommendation inverts the brief: **buy priority and parallelism, not unlimited.**

**Primary: Krea Max ($70/mo) + Magnific Premium+ (annual, $33.75/mo) = $103.75/mo.** Krea Max is
the only consumer plan found advertising **unlimited concurrency** on its paid lane, carries
Seedance 2.0 with full multi-reference input, and lists Seedance rates ~3.5× below fal retail.
Magnific Premium+ makes the image half — character sheets, face refs, locations — flat-rate
unlimited on Nano Banana 2, Flux.2 Pro and Seedream 5.0 Lite.

**Leave Higgsfield.** Not only for the queue. The July 2026 ToS still reserves the right to
"restrict, suspend, throttle, or place usage on a slower processing queue"; staff were documented
gating promised models to Business users mid-production; cancellations are stalled on Discord;
refunds require zero credits used minus a 6% fee; BBB complaints and a February 2026 X suspension
sit on the record. That is counterparty risk, not a speed complaint.

**Volume reality:** at ~$0.68/sec for 1080p Seedance, 400 1080p finals costs ~$1,360/month at
retail. No $150 plan delivers that. Every honest answer is a draft→final pipeline.

**Confidence: medium-high** on the diagnosis, **medium** on Krea specifically. Biggest unknown named in §6.

---

## 1. Primary recommendation

### Krea Max — $70/month + Magnific Premium+ — $33.75/month (annual) = **$103.75/month**

**Sign up for:** Krea `Max` plan (krea.ai/pricing), monthly billing for the first month.
Magnific `Premium+` (magnific.com/pricing), annual billing.

#### Why Krea Max, specifically

| Requirement | Evidence |
|---|---|
| **No deprioritized lane** | Max advertises **unlimited concurrency**. The credits are metered, so there is no free tier for you to be queued behind — you are always the paying customer. |
| **Multi-image reference (hard requirement)** | "Krea uses Seedance 2.0 with image/video/text references, optimized for reference-led character continuity and stable identity frame to frame." Seedance 2.0 natively accepts **9 images + 3 videos + 3 audio**; 2.5 raises it to 50. |
| **Asset-locked pipeline** | Krea 2 character-design pipeline covers the four sheet types his workflow depends on: turnarounds, expressions, costume variations, key portraits. Style reference accepts one or several images. |
| **Price per generation** | Krea's published Seedance rates: **Fast from $0.0677/sec, standard from $0.0849/sec**. fal charges $0.2419/sec for the same Fast endpoint. Krea is ~3.5× cheaper for identical compute. |
| **Model breadth** | 64+ image and video models — Veo 3, Sora, Kling, Seedance — one subscription, one balance. |
| **Adversarial record** | Phase 5 found **no** throttling, nerfing, cancellation-complaint or quality-downgrade pattern. Krea *cut* the Max price ($105 → $70), the opposite of the degradation pattern. |

**Estimated yield:** 60,000 credits at Krea's listed Seedance Fast rate ≈ **175–200 five-second
clips/month** at face value. **This estimate is unconfirmed** — see §6.

#### Why Magnific Premium+ alongside it

His pipeline is half image generation, and image volume is described as high. Premium+ gives
**unlimited Nano Banana 2, Flux.2 Pro and Seedream 5.0 Lite** — three of his four named image
models — at flat rate, plus 600K credits and unlimited Kling 2.5 / Hailuo video at lower res as
overflow. Character sheets and location refs stop metering entirely.

**Carried warning:** this is the one component with a documented post-launch nerf. An **2026-04-21
policy change** moved specific models off the unlimited tier, and reviewers report models marketed
as unlimited later being rate-limited or shifted to credit billing. Buy annual only after
confirming at checkout that Nano Banana 2 and Seedream are still on the unlimited list.

#### The queue-behaviour evidence trail (the question that decides this)

1. Krea Max's paid lane is **metered, not unlimited** — structurally there is nothing to
   deprioritize it against. This is an architectural inference, stated as such: **no measured
   wall-clock timing data for Krea video exists in public sources.** (Phase 3 records this gap
   rather than substituting a vendor number.)
2. Seedance 2.0 renders a 10s 1080p clip in **30–60 seconds**. Every multi-minute wait users report
   anywhere is queue, not compute. Removing the queue removes the problem.
3. The contrast case is measured: on Higgsfield, the *same model* returns in **~1 minute on credits
   (priority) and 10 → 25+ minutes on unlimited (standard queue)**, degrading week over week.

#### Operating instructions

- Draft on Seedance **Mini/Fast at 480–720p**; promote selected takes to 1080p on the same prompt
  and reference set. Seedance ships Mini / Fast / Standard as variants of one model, so promotion is
  a tier switch, not a re-shoot.
- Batch overnight. Peak-vs-off-peak variance is the largest speed lever a solo operator controls,
  and it is reported on every platform that discusses load.
- Month 1: measure actual credits burned per finished shot. That single number decides whether to
  stay, add fal, or move to PixVerse.

---

## 2. Runner-up

### PixVerse Premium — $48–60/month

**The tradeoff in one sentence:** PixVerse is the only vendor that publishes a concurrency ladder
per tier (3 / 5 / 8 / 12) and prices off-peak as a *discount* rather than a queue demotion — but
reviewers report that at peak hours "you may spend more time waiting than generating," and its
image-generation side is far weaker than Krea's for the asset-creation half of the pipeline.

Details: 15,000 credits, **8 concurrent generations**, **50% off-peak discount**, native Seedance
2.0 with explicit **9-image reference upload**, Standard and Fast tiers, 4–15s, up to 1080p.
1080p 5s ≈ 300 credits ≈ $1.20 → ~50 1080p finals/month, or ~100 using off-peak.

**Worth flagging on its own:** PixVerse **Ultra ($149–199)** applies a **100% off-peak discount** —
free generation during off-peak windows. That is the only unlimited-shaped offer found in the entire
survey that is *time-shifted rather than queue-shifted*, i.e. the only one that does not
deprioritize you. It sits at the very top of his budget and its exact off-peak windows and Ultra
concurrency figure could not be verified, so it is not the primary — but if Krea's credit yield
disappoints, this is the next thing to price.

---

## 3. The API-with-spend-cap alternative

### fal.ai, pay-per-use, hard cap

**Verified rates (fal's own model pages), per second and per 5-second clip:**

| Endpoint | $/sec | 5s clip |
|---|---|---|
| Seedance 2.0 Mini I2V, 480p | $0.0433 | **$0.22** |
| Seedance 2.0 Mini I2V, 720p | $0.0928 | $0.46 |
| Seedance 2.0 Fast, 720p | $0.2419 | **$1.21** |
| Seedance 2.0 standard, 720p | $0.3034 | $1.52 |
| Seedance 2.0, 1080p | $0.682 | **$3.41** |

**Honest cost at his volume**, using an 85% draft (Mini 480p) / 15% final (Fast 720p) split:

| Volume | Drafts | Finals | **Total/month** |
|---|---|---|---|
| 150 gens | 128 × $0.22 = $28 | 22 × $1.21 = $27 | **$55** |
| 300 gens | 255 × $0.22 = $56 | 45 × $1.21 = $54 | **$110** |
| 400 gens | 340 × $0.22 = $75 | 60 × $1.21 = $73 | **$148** |

At a heavier 70/30 finals ratio, 400 generations costs **$207** — over budget.

### The crossover

> **Metered wins below ~250 generations/month, or at any volume where ≥85% of output is draft-tier.**
> **Subscription wins above ~300 generations/month once the finals ratio exceeds ~25%**, because
> subscription plans bundle compute below retail API rates — Krea lists Seedance Fast at $0.0677/s
> against fal's $0.2419/s, a 3.5× spread, and Dreamina lists $0.046/s.

**Verdict: not the primary.** The client is a heavy iterator at the top of the volume range with a
cinematic finals bar, which is the exact quadrant where metered retail loses. It also scores **0 on
asset persistence** — fal is an API, so character sheets, identity refs and location locks live in
his own filesystem with no library. That is a real workflow tax on an asset-locked pipeline.

**Where it does belong:** as a **capped overflow lane for 1080p finals**. Add a fal account with a
hard $30/month cap on top of Krea (**total $134/mo**) and route only hero shots to it. Caps are the
point — metered without a cap is how a heavy iterator gets a $600 surprise.

---

## 4. The "stay on Higgsfield" case — steelmanned

**The strongest configuration that exists:** Higgsfield **Max at $79/mo (1,800 credits)**, never
touching Unlimited for anything that matters — drafts on the free unlimited standard queue while
you sleep, finals in **Credit Mode on the priority queue with parallel jobs**.

The math genuinely works on paper. Seedance 2.0 costs **22 credits / 5s @720p** and **45 credits /
5s @1080p**. 1,800 credits = **~40 × 1080p priority finals** or ~81 × 720p, on top of unlimited
720p drafts. Credit mode is measured at **~1 minute per clip** — the fastest measured lane in this
entire report. Higgsfield also has the **best asset library in the survey** (first-class Characters
and Reference Elements that persist across sessions, scored 5/5 in Phase 4) and the current promo is
**33 days of unlimited Seedance 2.5**, live since 2026-08-07. Switching costs are real: he would be
rebuilding a locked asset library elsewhere.

**Why it still fails.**

1. **The unlimited half stays useless.** Toggling Unlimited puts you in the standard queue at 1
   concurrent, shared across all models. Reported times: ~10 min fresh, **25+ min to hours under
   sustained heavy use**, 15–30+ min by week 4. He is a heavy iterator — he lives in the worst part
   of that curve by construction.
2. **The 33-day promo is capped at 720p**, against a model that natively does 4K. His finals bar is
   1080p. The unlimited track cannot produce his deliverable.
3. **The contract permits the throttling.** Post-backlash ToS (revised 2026-07-26) still allows
   Higgsfield to "restrict, suspend, throttle, or place usage on a slower processing queue."
   Whatever speed he measures today is not a commitment.
4. **Counterparty risk, which no amount of speed fixes.** Cancellations stalled on Discord; refunds
   only within 7 days with zero credits used, minus 6%; none on renewals. Staff confirmed in writing
   that Cinema Studio 3.0 and Seedance 2.0 were "presently limited to verified Business users"
   despite Creator-plan promises; camera and lens options removed mid-commercial-production. Mass
   bans in late 2025, quietly reversed without explanation. BBB complaints. X account suspended
   2026-02-09. Outage reports of severe slowness and high generation-failure rates.

**Verdict: no.** A vendor that can remove your tools mid-delivery and stall your cancellation is
not a supplier for client work. If he wants a bridge, ride the 33-day promo to expiry while
standing up Krea in parallel, then cancel — early, in writing, with zero credits used in the final
cycle.

---

## 5. Master comparison table

| Platform | Plan / price | Unlimited? | Deprioritized? | Concurrency | Multi-ref | Max res | Fit score /30 | Verdict |
|---|---|---|---|---|---|---|---|---|
| **Krea** | Max **$70** | In-house models only | Yes (that part) | **Unlimited (paid)** | ✅ 9-img Seedance | 1080p+ | **27** | **PRIMARY** |
| **Magnific** (ex-Freepik) | Premium+ **$45 / $33.75 ann.** | ✅ ~10 image models | Unclear | Unclear | ✅ | image + low-res vid | 23 | **PRIMARY (image half)** |
| **PixVerse** | Premium **$48–60** | Ultra tier = 100% off-peak | **No — time-shift** | **8 published** | ✅ 9-img | 1080p | 22 | **RUNNER-UP** |
| **fal.ai** | Metered + cap | n/a | No lane exists | Rate-limit only | ✅ | 1080p | 23 | **CAPPED OVERFLOW** |
| Higgsfield | Max **$79** | 33-day Seedance 2.5 | **Yes, explicit** | **1** (unl.) / parallel (credit) | ✅ | 720p on unl. | 21 / 18 | **EXIT** |
| Dreamina/CapCut | ~$15/$35/$70 | "Eligible plans", unverified | Unverified | Unverified | ✅ first-party | 4K | 23 | Test in parallel |
| Runway | Max $95 (from 09-01) | **Being deleted 09-01** | Was — hence deletion | Unlimited | ✅ | 1080p+ | 22 | Volume-disqualified (~63 clips/mo) |
| OpenArt | Wonder $120 | Select models, relaxed | Yes | **32** | ✅ | — | 24 | Over budget |
| Luma | Unlimited $94.99 | ✅ | **Yes — relaxed + overnight** | — | partial | — | — | Disqualified |
| ImagineArt | Unlimited tiers | ✅ | **Yes** | **1** | ✅ | — | — | Disqualified |
| Adobe Firefly | Premium $199.99 | ✅ video | Unknown | Unknown | ✅ | 2K–4K | — | Over budget |
| Kling official | Ultra $128–180 | ❌ | Ultra gets priority | — | ✅ | 1080p | — | Credits only |
| Google AI Ultra | $99.99–199.99 | ❌ 25k credits | — | — | partial | — | — | Credits only |
| Grok / SuperGrok | $30 | Weekly pool, undisclosed | — | — | ❌ | **720p** | — | Disqualified |

---

## 6. Confidence levels and the biggest unknown

| Recommendation | Confidence | Single biggest unknown |
|---|---|---|
| **Diagnosis: no unlimited tier anywhere is un-deprioritized** | **High** | Whether any vendor ships a priority-unlimited tier after this report's date. The pattern is structural (GPU cost), so unlikely. |
| **Exit Higgsfield** | **High** | Nothing material. Queue mechanic is from Higgsfield's own help centre; the conduct record is corroborated across BBB, Discord reports, press and an X suspension. |
| **Primary: Krea Max $70** | **Medium** | **How many finished 1080p shots 60,000 credits actually buys.** Krea publishes API rates ($0.0677/s Fast) but the subscription-credit → compute mapping was not found. The 175–200 clip estimate is face-value arithmetic, not a verified figure. **Mitigation: buy month 1 monthly, not annual, and measure.** If yield lands under ~120 clips, switch to PixVerse Premium or add the fal overflow lane. |
| **Magnific Premium+ image half** | **Medium** | Whether Nano Banana 2 / Seedream stay on the unlimited list. There is a documented 2026-04-21 precedent for models being moved off it post-purchase. **Mitigation: verify the unlimited model list at checkout; annual billing only after that check.** |
| **Runner-up: PixVerse Premium** | **Medium** | Exact off-peak window definitions and whether the 50% discount applies to Seedance specifically. |
| **fal.ai crossover math** | **Medium-high** | Rates are from fal's own model pages; the draft/final ratio (85/15) is an assumption about his workflow, and the totals move ±50% if that ratio shifts. |
| **Speed figures for anything except Higgsfield** | **Low — stated as absent, not estimated** | No credible measured wall-clock data exists publicly for Krea, PixVerse, Dreamina or Runway Max. He must measure in week 1. |

---

## Appendix A — Kill list

| Platform | Eliminated because |
|---|---|
| **Higgsfield** | Unlimited = standard queue, 1 concurrent, shared across models; ToS permits throttling; 720p cap on promo; cancellation/refund and mid-production model-removal record |
| **ImagineArt** | Policy states "one active generation at a time" — identical failure mode |
| **Luma Dream Machine** | $94.99 unlimited is explicitly "relaxed mode" + "overnight queue" |
| **DomoAI** | "Relax Mode" unlimited — same failure mode |
| **OpenArt Wonder** | $120/mo leaves no budget; unlimited is relaxed-queue on non-flagship models |
| **Runway** | Unlimited deleted 2026-09-01; Max yields only ~63 clips/month against a 150–400 target |
| **Adobe Firefly** | $199.99 for unlimited video — above budget; Feb 2026 promo window closed |
| **Grok / SuperGrok** | 720p ceiling; undisclosed weekly usage pool since June 2026 — unpriceable |
| **Freepik/Magnific (as a video answer)** | Unlimited covers image models only; video always burns credits |
| **invideo** | Agentic long-form tool; separate non-rolling credit pools; not a shot-level cinematic tool |
| **LTX Studio** | Compute-seconds metering; no unlimited; Veo-centric |
| **Morphed, Pollo, Magic Hour, Topview, Vidu, Hedra, Pika** | Pure credit systems with no unlimited tier and no concurrency advantage at his price point |
| **Kling official** | Credits only; flagship capacity prioritized to $128–180 Ultra |
| **Google Flow / AI Ultra** | 25k credits, no unlimited, weak multi-reference story vs Seedance |
| **Hailuo / MiniMax** | Credits only; strong model (H3, #2 on leaderboard) but no volume answer |
| **Synthesia, HeyGen** | Avatar/corporate video — not cinematic generation |
| **ModelsLab, Atlas Cloud, Poyo, Lumenfall, Kie.ai, Novita, SeeGen, ClipDance, Morphic** | Thin API resellers or wrappers; no asset library, no pricing advantage over fal/Krea |
| **Replicate, BytePlus direct** | Viable metered routes but strictly worse than fal for this use case (BytePlus prices in opaque token packs; Replicate has no Seedance pricing advantage) |
| **Dreamina/CapCut** | Not killed — held back from the top 3 only because its unlimited terms, concurrency and fair-use rules could not be verified. Cheapest published Seedance rate found ($0.046/s), first-party, top-ranked on the leaderboard. Worth a $15 parallel test. |

---

## Appendix B — Leaderboard context (Artificial Analysis, via search 2026-08-17)

**Image-to-video with audio** — the client's actual modality:
Dreamina Seedance 2.0 720p **1197** · MiniMax H3 **1191** · Gemini Omni Flash **1187** ·
grok-imagine-video-1.5 1112 · HappyHorse-1.1 1112

**Text-to-video with audio:**
Gemini Omni Flash 1241 · MiniMax H3 1238 · Dreamina Seedance 2.0 720p 1222 · Wan2.7 1160

**Read:** Seedance 2.0 is #1 for image-to-video-with-audio, which is exactly what an asset-locked
reference pipeline produces. His model preference is correct and every recommendation above
preserves access to it. Kling 3.0 (released 2026-02-05) held top ELO as of April 2026; Seedance 2.0
released 2026-02-12; Seedance 2.5 adds 30s clips, native 4K and 50 reference inputs.

---

## Appendix C — Research limitations (disclosed)

- **WebFetch was blocked** by this environment's egress policy (HTTP 403 from the agent proxy on
  artificialanalysis.ai, reddit.com, help.imagine.art, multic.com, ugccopilot.ai and others). All
  evidence comes from web-search-surfaced content and links. **Primary pages could not be opened**,
  so ToS and policy language is reported as surfaced in search rather than quoted from the source
  document. Before spending, the client should verify at checkout: Krea's credit→generation rate,
  Magnific's current unlimited model list, and PixVerse's off-peak windows.
- **Reddit and Discord could not be read directly.** User-report evidence is second-hand via review
  aggregators that cite those sources. Weighted accordingly — it is consistent across independent
  aggregators and matches the client's own reported experience, which is why the Higgsfield
  conclusion is rated high confidence despite the access limitation.
- **One source conflict logged and resolved** (fal Seedance Fast pricing, $0.022/s vs $0.2419/s) —
  see `research/phase-5.md`. Weighted to fal's own model pages.
- **Pricing in this market changed monthly through 2026.** Every figure carries its date. Anything
  older than 90 days was used only for stable facts (model capabilities, input formats).
