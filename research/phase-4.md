# Phase 4 — Workflow fit scoring

Scored 0–5 against the client's asset-locked pipeline. Survivors from Phase 2 plus Higgsfield
(carried for the steelman) and fal.ai (carried as the metered alternative).

Criteria:
(a) multi-image reference input per generation
(b) asset/character library persistence across sessions
(c) parallel generation count at ~$100–150
(d) draft→final pipeline (cheap tier that re-renders same setup at high quality)
(e) image-gen quality for the asset-creation half
(f) commercial rights clarity

| Platform | a | b | c | d | e | f | Total /30 |
|---|---|---|---|---|---|---|---|
| **Krea Max $70** | 5 | 4 | **5** | 4 | **5** | 4 | **27** |
| **PixVerse Premium $60** | **5** | 3 | 4 | 4 | 2 | 4 | **22** |
| **fal.ai metered** | 5 | 0 | **5** | **5** | 4 | 4 | **23** |
| **Magnific Premium+ $45** | 4 | 4 | 3 | 3 | **5** | 4 | **23** |
| **Dreamina Advanced $70** | **5** | 3 | 3 | 4 | 4 | 4 | **23** |
| **Higgsfield Max $79** | 5 | **5** | 4 (credit mode) / **1** (unlimited) | 4 | 4 | **2** | **21 / 18** |
| Runway Max $95 | 4 | 3 | 5 | 2 | 3 | 5 | 22 |
| OpenArt Wonder $120 | 4 | 4 | 5 | 3 | 4 | 4 | 24 (over budget) |

## Notes behind the scores

**(a) Multi-image reference — his hard requirement.** Seedance 2.0 natively accepts **up to 9 images
+ 3 videos + 3 audio**; Seedance 2.5 raises this to **50 reference inputs**. Confirmed available on:
PixVerse (explicitly "upload up to 9 reference images directly into your prompt"), Krea ("Seedance
2.0 with image/video/text references... optimized for reference-led character continuity"),
Dreamina/CapCut (first-party), ModelsLab, Atlas Cloud, SeeGen, fal (reference-to-video endpoints).
No survivor fails this test — the requirement filters out text-to-video-only tools, all of which
were already dropped in Phase 1.

**(b) Asset library persistence.** Higgsfield scores highest here and it is the real switching cost:
it has first-class Characters and Reference Elements objects that persist across sessions. Krea has
style reference + a character-design pipeline (turnarounds, expressions, costume variations, key
portraits) but reference management is looser. **fal scores 0** — it is an API; asset persistence is
the client's own filesystem. This is the honest cost of the metered route.

**(c) Parallelism at his price point.** Krea Max advertises **unlimited concurrency**; fal is bounded
only by API rate limits; PixVerse Premium publishes **8 concurrent**; Higgsfield credit mode gives
"multiple parallel jobs" (count unpublished) but **unlimited mode gives exactly 1**.

**(d) Draft→final.** Seedance ships Mini / Fast / Standard variants of the same model, so the same
prompt and references re-render at higher quality across tiers on any platform carrying the full
family. fal scores 5 because all three variants are separately addressable endpoints with identical
inputs. Runway scores 2 — at ~63 clips/month there is no draft budget.

**(e) Image side.** Magnific and Krea lead. Magnific Premium+ gives **unlimited Nano Banana 2, Flux.2
Pro, Seedream 5.0 Lite** — that is three of the client's four named image models, flat-rate. Krea
carries 64+ models plus its own Krea 2 (2-second generations vs 17.7s for Nano Banana Pro).
Reference points: Nano Banana 2 (released 2026-02-26) supports **14 reference images**, 0.5K–4K.

**(f) Commercial rights.** Pollo, Runway, Dreamina paid plans and PixVerse are clear. **Higgsfield
scores 2** — not because rights are absent but because the July 2026 ToS revision "kept its core
training rights fully intact" while tightening provisions in the company's favour, and staff were
documented telling Creator-plan users that models promised on their plan were "presently limited to
verified Business users." Rights that are contractually clear but operationally unreliable score low
in procurement.

## Volume reality check (the constraint nobody advertises)

At 1080p, Seedance retail is ~$0.68/sec (fal) → **~$3.41 per 5-second final**. 400 finals/month at
1080p is ~$1,360 at retail. **No $150 plan delivers 400 1080p finals. Not one.** Every workable
answer at his budget is a draft→final pipeline: high-volume cheap iteration, selective 1080p finals.
Any report implying otherwise is selling something.
