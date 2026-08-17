# Phase 5 — Adversarial pass

Top 3 entering this phase: **Krea Max**, **PixVerse Premium**, **fal.ai metered**.
Higgsfield carried separately for the steelman.

## Kill attempt 1 — Krea

Searched for throttling, nerfing, post-launch degradation, cancellations.

- **Nothing found.** No pattern of post-launch throttling, no ToS throttling clause surfaced, no
  cancellation/billing complaint cluster, no quality-downgrade reports.
- **Real weakness found instead:** the Max plan's "unlimited" is **in-house-models-only at relaxed
  rate** — so the unlimited label is useless for Seedance work. The plan must be bought for its
  60,000 metered credits + unlimited concurrency, not its unlimited badge.
- **Second real weakness: the credit→clip conversion is unverified.** Krea publishes API rates
  (Seedance 2.0 Fast from $0.0677/s, standard from $0.0849/s) but the mapping from subscription
  credits to those rates was not found. At face value 60,000 credits ≈ 175–200 5-second Seedance
  Fast clips; that estimate is **not confirmed** and is the single biggest unknown in this report.
- Krea also reported a **price cut** on Max ($105 → $70), which is the opposite of the degradation
  pattern being hunted.
- **Verdict: survives, rank unchanged.**

## Kill attempt 2 — PixVerse

- **Confirmed weaknesses:** "queue delays during peak hours and occasional platform glitches";
  "concurrency limits are strict, and if you're on a lower-tier plan, you may spend more time
  waiting than generating"; support "frequently flagged as slow or unresponsive"; Trustpilot/Reddit
  complaints about credits burning fast and failed generations.
- **But:** these are peak-hour and low-tier complaints. The recommendation is Premium (8 concurrent),
  not a low tier, and off-peak use is the explicit mitigation the platform itself prices for.
- No evidence of a *post-launch nerf* — no tier was downgraded after purchase.
- **Verdict: survives, drops to clear #2** on the strength of "you may spend more time waiting than
  generating" appearing in reviews at all.

## Kill attempt 3 — fal.ai

- No throttling/nerf pattern found.
- **Real weaknesses:** zero asset persistence (Phase 4 score 0), no creative UI, and **retail
  pricing is the highest of any route** — fal charges $0.2419/s for Seedance 2.0 Fast where Krea
  lists $0.0677/s and Dreamina lists $0.046/s for Seedance 2.0. Paying retail API rates for a
  400-generation month is the most expensive way to buy the same model.
- **Verdict: survives as the spend-capped alternative, not as primary.**

## Source conflict logged

**fal.ai Seedance 2.0 Fast pricing.** One source (useapi.net roundup) states **$0.022/sec** on Fast;
fal's own model pages state **$0.2419/sec** (Fast, 720p), $0.3034/sec (standard 720p), $0.682/sec
(1080p), $0.0928/sec (Mini I2V 720p), $0.0433/sec (Mini I2V 480p).
**Weighted to fal's own pages.** Reasons: (1) the precise decimal values match a real price table;
(2) $0.022/s would put a 10s flagship clip with native audio at $0.22, implausible against every
other provider; (3) the $0.022 figure most likely describes the **Mini** variant, which fal does
price an order of magnitude below Fast. The roundup appears to have collapsed Mini and Fast.

## Re-entry review — platforms filtered early

- **Magnific / Freepik Premium+ ($45, or $33.75 annual) — RE-ENTERS as the image-side answer.**
  Dropped in Phase 1 because unlimited excludes video. But the client's pipeline is half image
  generation (character sheets, face identity refs, location refs), and Premium+ gives **unlimited
  Nano Banana 2, Flux.2 Pro and Seedream 5.0 Lite** — three of his four named image models — flat
  rate. That solves the asset-creation half at fixed cost.
  **Carried with a warning:** the **2026-04-21 policy change** moved specific models off the
  unlimited tier post-purchase, and reviewers report models marketed as unlimited later being
  rate-limited or shifted to credit billing. This is a documented post-launch nerf — exactly the
  pattern this phase exists to catch. It is the one recommendation in this report with a known
  degradation history.
- **OpenArt Wonder — stays out.** 32 parallel generations is the best concurrency found, but $120/mo
  leaves no room for anything else and its unlimited is relaxed-queue on non-flagship models.
- **Dreamina — stays out of the top 3, retained as a price note.** Cheapest published Seedance rate
  anywhere ($0.046/s), first-party ByteDance, top-ranked on the image-to-video leaderboard. It is
  excluded from the primary recommendation only because its unlimited terms, concurrency and
  fair-use rules **could not be verified at all**, and an unverifiable unlimited is precisely what
  the client is trying to escape. Worth a $15 Basic month as a parallel test.
- **Runway — stays out.** ~63 clips/month at Max. Volume-disqualified regardless of queue quality.

## Higgsfield — adversarial findings (severe)

Not a speed problem alone. The record found:
- ToS §10.6 "dynamic throttling" for undefined "excessive" usage; post-backlash rewrite (2026-07-23
  → 2026-07-26) removed the most alarming language, **kept core training rights intact**, and still
  permits throttling and slower-queue placement.
- **BBB complaints**; a dedicated complaints site (higgsfieldsucks.com).
- Cancellation requests denied or stalled on Discord ("couldn't be verified"); refunds only within
  7 days, only with **zero credits used**, minus a **6% service fee**, none on renewals.
- Staff confirmed in writing that Cinema Studio 3.0 and Seedance 2.0 were "presently limited to
  verified Business users" despite Creator-plan promises; camera/lens options removed mid-production.
- **Mass account bans** (late Dec 2025 "Christmas Grinch" episode), many quietly reversed without
  explanation; **X account suspended 2026-02-09**.
- Outage reports: severe slowness, intermittent downtime, high generation-failure rates.

**Verdict: Higgsfield is not merely slow on unlimited — it carries counterparty risk.** For a solo
operator with client deliverables, mid-production model removal and stalled cancellations are a
bigger threat than queue time.

## Final ranking after adversarial pass

1. Krea Max $70 (unchanged)
2. PixVerse Premium $60 (down from tied-first)
3. fal.ai metered with hard cap (alternative, not primary)
— Magnific Premium+ re-enters as an image-side complement, with a nerf warning
— Higgsfield: exit recommended
