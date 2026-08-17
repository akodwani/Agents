# Phase 2 — Unlimited-tier deep dive

**Run date:** 2026-08-17. Sources = web search surfacing; direct page fetch blocked by egress policy.

## The central finding

Across every platform found in Phase 1, "unlimited" is implemented as a **deprioritized queue**.
Not one vendor offers unlimited generation at priority. The Higgsfield failure mode the client
described is the industry-standard implementation, not an outlier.

## Platform-by-platform

### Higgsfield — DISQUALIFIED (reproduces the exact failure mode)
- **Mechanic, from Higgsfield's own help center:** "Unlimited generations run in the standard
  queue, while credit-based generations always run in the priority queue." Unlimited = **1
  concurrent job**; credit mode = priority queue + **multiple parallel jobs**.
- **Concurrency is shared across all models** — you cannot run two different unlimited models
  simultaneously; both draw the same single slot.
- **ToS, post-backlash revision (sent 2026-07-23, revised 2026-07-26):** still states unlimited
  plans are subject to "fair-use limits and dynamic speed limitations," and that Higgsfield may
  "restrict, suspend, throttle, or place usage on a slower processing queue" for usage that
  "materially exceeds typical individual use." The original §10.6 "dynamic throttling" clause with
  no definition of "excessive" was the trigger for a viral thread (331k+ views).
- **Current offer (live):** 33 days of unlimited Seedance 2.5, launched 2026-08-07. **Capped at
  720p** despite the model's native 4K. Days of access vary by plan tier and billing period.
- Earlier add-on: 30-day Seedance Unlimited on Enhanced Seedance 2.0 Fast (June 2026), one
  generation at a time.
- **Plans as of 2026-08-05:** Basic $9 / 120 cr · Pro $29 / 600 cr · Max $79 / 1,800 cr.
  (Older "Plus/Ultra" tier names in most articles are stale.)
- Credit cost: Seedance 2.0 ≈ **22 credits / 5s @ 720p, 45 credits / 5s @ 1080p**.

### ImagineArt — DISQUALIFIED
Own policy page: Unlimited "supports **one active generation at a time**." Plus fair-use rate
limiting/throttling language. Identical failure mode.

### Luma Dream Machine — DISQUALIFIED
Unlimited $94.99/mo ($119.99 iOS) = 10,000 fast credits + **unlimited "relaxed mode" and an
"overnight queue."** Explicitly lower-priority. The unlimited half is the slow lane by design.

### OpenArt Wonder ($120/mo annual) — DISQUALIFIED for unlimited, notable for concurrency
Unlimited applies only to "select models" (workhorse/older models), and only if "willing to stay in
a 'relaxed' queue during high-traffic times." Flagship models still burn credits.
**Notable:** 32 parallel generations on the credit side — highest concurrency found anywhere.

### Krea Max ($70/mo) — SURVIVES with caveat
- Unlimited portion is "relaxed-rate, **in-house-model-only**" on top of a 60,000-credit meter.
  So the unlimited half is not usable for Seedance/Veo/Kling work.
- **But:** the plan advertises **unlimited concurrency** on the metered credit side. That is the
  opposite of the Higgsfield trap — the paid lane has no concurrency cap.
- Seedance 2.0 is available on Krea on all paid plans, with image/video/text references.
- Krea's own published rates: Seedance 2.0 Fast from **$0.0677/sec**, standard from **$0.0849/sec**
  — roughly 3.5x cheaper than fal's retail rate for the same model.

### Freepik / Magnific (rebranded 2026-04-28) — DISQUALIFIED for video, STRONG for image
- Unlimited covers ~10 **image** models on Premium+/Pro: Nano Banana 2, Flux.2 Pro, Seedream 5.0
  Lite, Kling 2.5, Grok. Premium+ also includes unlimited **Kling 2.5 and Hailuo video at lower
  resolutions** + 600K credits for heavier video.
- **Post-purchase nerf documented:** an **2026-04-21 policy change** moved specific models off the
  unlimited tier; multiple reviewers report models marketed as unlimited were later rate-limited or
  shifted to credit billing. This is exactly the Phase-5 degradation pattern — recorded here.
- Premium+ $45/mo monthly, $33.75/mo annual.

### Runway — DISQUALIFIED (the tier is being deleted in 12 days)
- Unlimited **auto-converts to Max on 2026-09-01**; Unlimited unchanged only through 2026-08-31.
- Runway's own stated reason: relaxed-rate generation created queue waits. Max = 9,500 credits,
  "no wait times or limits on how many videos you can create at once," 1 month rollover, $95/mo.
- **Volume math kills it anyway:** Seedance 2.5 at 720p = 30 credits/sec with an 80-credit minimum
  → 150 credits per 5s clip → **~63 clips/month**. Against a 150–400 target, Runway is not in the
  conversation.

### Adobe Firefly — DISQUALIFIED on price
Premium $199.99/mo (promo $139.91 first year through 2026-08-26) includes unlimited video. Above
budget, and the Feb 2026 unlimited promo window has closed.

### PixVerse — SURVIVES, structurally different mechanism
- **Published concurrency ladder** (the only vendor found that publishes it per tier):
  Standard $8–10 → 3 concurrent · Pro $24–30 → 5 · Premium $48–60 → 8 · Team Premium $99/seat → 12.
- Ultra $149–199 → 25,000 credits.
- **Off-peak discount ladder:** Standard 20% (preview mode) · Pro 30% · Premium 50% ·
  **Ultra 100% (free generation during off-peak).**
- Native Seedance 2.0 with **9-image reference input**, Standard and Fast tiers, 4–15s, up to 1080p.
- Credit cost: 1080p 5s Seedance ≈ 300 credits ≈ $1.20 on Premium ($0.004/credit).
- **Why this matters:** Ultra's "unlimited" is a *time-window* discount, not a *queue-priority*
  demotion. It is the only unlimited-shaped offer found that does not deprioritize the user.

### Dreamina / CapCut (ByteDance first-party) — SURVIVES on price, unclear on terms
- Cheapest published Seedance rate anywhere: **$0.046/sec** (Seedance 2.0, best current monthly
  promo); Seedance 2.5 from $0.097/sec on the compared annual plan.
- Plans ≈ Basic $15 / Standard $35 / Advanced $70 (May 2026 capture); Basic ≈ 2,420 credits/mo.
  Free tier 225 credits/day.
- Paid plans include watermark removal, commercial licensing, **priority queue access**.
- Seedance 2.5 unlimited "available with eligible plans" — **terms, concurrency and fair-use rules
  could not be verified**. Max 720p / 30s on that track.
- Documented user complaints: slow or failed generations, rising credit costs, weak support.

### DomoAI — DISQUALIFIED
$9.99+ unlimited via "Relax Mode." Same failure mode.

### Grok Imagine / SuperGrok — DISQUALIFIED
720p ceiling on the consumer tier; since June 2026 a single **undisclosed weekly usage pool** across
all Grok products. xAI has not published pool sizes for any tier. Unpriceable at his volume.

## Summary flag table

| Platform | Unlimited exists | Deprioritized? | Concurrency | Verdict |
|---|---|---|---|---|
| Higgsfield | Yes (33-day Seedance 2.5) | **Yes, explicit** | **1** | Disqualified |
| ImagineArt | Yes | Yes | **1** | Disqualified |
| Luma | Yes ($94.99) | **Yes, "relaxed"/overnight** | n/a | Disqualified |
| OpenArt Wonder | Select models | Yes, "relaxed" | 32 (paid side) | Disqualified (unlimited) |
| Krea Max | In-house models only | Yes (that portion) | **Unlimited (paid side)** | Survives |
| Magnific Premium+ | Images + low-res video | Unclear | Unclear | Survives (image only) |
| Runway | Being deleted 2026-09-01 | Was, hence deletion | Unlimited on Max | Disqualified (volume) |
| PixVerse | Ultra off-peak = 100% off | **No — time-shift, not queue-shift** | 3/5/8/12 published | Survives |
| Dreamina | "Eligible plans" | Unverified | Unverified | Survives (unverified) |
| Adobe Firefly | Yes, Premium | Unknown | Unknown | Disqualified (price) |
| DomoAI | Yes, Relax Mode | Yes | n/a | Disqualified |
| Grok | Weekly pool | n/a | n/a | Disqualified |
