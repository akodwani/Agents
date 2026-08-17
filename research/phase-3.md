# Phase 3 — Speed benchmarking (evidence over claims)

**Run date:** 2026-08-17. Evidence hierarchy applied: third-party benchmark > timestamped user
report (≤90 days) > vendor claim (marked unverified).

## Baseline: what the model itself costs in wall-clock render time

Seedance 2.0, 10s @ 1080p: **30–60 seconds of actual render** (Atlas Cloud / Segmind guides, 2026).
Atlas Cloud Fast tier claims ~30% reduction — vendor claim, **unverified**.

**This is the whole point.** Render is under a minute. Every multi-minute wait a user experiences is
**queue**, not compute. So queue policy is ~90% of the client's real-world speed, which is why
Phase 2 is the decisive phase and this one is confirmatory.

## Higgsfield — the only platform with rich timestamped user data

| Lane | Reported wall-clock (5–10s clip) | Source class | Date |
|---|---|---|---|
| Credit mode (priority queue) | **~1 minute** | Aggregated Reddit + review reports | 2026 |
| Unlimited, week 1 / fresh | **~10 minutes** | Aggregated Reddit + review reports | 2026 |
| Unlimited, sustained heavy use | **25+ minutes to hours** | Aggregated Reddit + review reports | 2026 |
| Unlimited, week 4+ | **15–30+ minutes** | Subscriber reports | 2026 |
| Paid unlimited vs new free trial account | Trial instant vs **40-minute** paid queue | Multic guide | 2026 |
| Vendor claim | "<5 min average across ~24,000 generations in first 7 hours after launch" | **Higgsfield marketing — unverified, and launch-window sampling by construction** | 2026 |

**Degradation curve, explicitly reported:** week 1 fast → weeks 2–3 slight slowdown → week 4+
significant delays. Higgsfield's "Battery" system dynamically manages render speed against demand.
Off-peak (late night / early morning US EST) materially reduces waits.

The vendor's own number is measured in the **first 7 hours of a launch promotion** — the single
least representative window possible for a queue that degrades with accumulated load. Weighted at
near-zero against the user reports, which agree with each other across independent sources and
match the client's lived experience.

**Peak vs off-peak variance is real and large on every platform reporting it** (Higgsfield,
PixVerse, OpenArt, Krea all describe high-traffic degradation). This is the single most actionable
speed lever available to a solo operator who controls his own schedule.

## Other candidates — honest gaps

| Platform | Real timing data found? |
|---|---|
| **PixVerse** | **No hard numbers.** Qualitative only: "queue delays during peak hours," "concurrency limits are strict... on a lower-tier plan you may spend more time waiting than generating." Concurrency ladder is published (3/5/8/12) but no measured wall-clock. |
| **Krea** | **No video timing data found.** Only image-side: Krea 2 Raw/Turbo ~2s vs Nano Banana Pro 17.7s vs Seedream 4.5 ~17s. Nothing on Seedance-through-Krea queue behavior. |
| **Dreamina** | **No timing data found.** Marketing claims "queue-free creation"; user complaints mention "slow or failed generations" without numbers. Vendor claim — unverified. |
| **Runway Max** | **No post-transition data possible** — Max doesn't take over until 2026-09-01. Vendor claim of "no wait times" is unverified and untestable today. |
| **Magnific** | No timing data found. |
| **fal.ai** | No queue-wait reports found. Structurally, metered API has no free tier to be deprioritized behind; latency ≈ render time + minor scheduling. This is an inference from architecture, not a measurement — labelled as such. |

**Stated plainly:** outside Higgsfield, there is no credible measured wall-clock timing data for any
candidate at his usage pattern. Anyone claiming otherwise is quoting vendor marketing. The correct
response is not to substitute vendor numbers, but to pick platforms on **queue architecture** —
which is knowable — and to measure wall-clock himself in week 1.

## Architectural speed ranking (what can actually be concluded)

1. **Metered API (fal, BytePlus direct)** — no deprioritized lane exists; you are always the paying
   priority customer. Fastest by construction.
2. **Krea Max metered credits** — unlimited concurrency on the paid side; parallelism compensates
   for any per-job latency.
3. **PixVerse Premium/Ultra off-peak** — 8+ concurrent, and off-peak is a discount not a demotion.
4. **Higgsfield credit mode** — priority queue, parallel jobs, ~1 min measured. Genuinely fast.
5. **Higgsfield unlimited / Luma relaxed / ImagineArt / DomoAI** — 1 concurrent, deprioritized,
   10–30+ min and degrading.
