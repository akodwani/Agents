# Phase 1 — Universe Construction (breadth pass)

**Run date:** 2026-08-17
**Tooling constraint:** WebFetch is blocked by this environment's egress policy (403 from the
agent proxy on every research domain tried: artificialanalysis.ai, reddit.com, help.imagine.art,
multic.com, ugccopilot.ai). All evidence below comes from web search result content + links.
Primary-source pages could not be opened directly, so verbatim ToS quoting is limited to what
search surfaces. This is disclosed in the final report.

## Master platform table

| # | Platform | Category | Models offered (claimed) | Unlimited tier? |
|---|---|---|---|---|
| 1 | Higgsfield | Aggregator | Seedance 2.0/Fast, Kling, Veo, Nano Banana Pro, Soul | Yes — Seedance Unlimited add-on + "Unlimited models" |
| 2 | Krea | Aggregator | 64+ image/video models: Veo3, Sora, Kling, Flux | Max $70 — "unlimited" on in-house models, relaxed |
| 3 | Freepik / Magnific (rebrand 2026-04-28) | Aggregator | Kling, Veo, Seedance, Flux, Seedream | Unlimited on ~10 **image** models only; video always credits |
| 4 | OpenArt | Aggregator | Multi-model + Director/Story modes | Wonder $120/mo — unlimited on *select* models, relaxed queue |
| 5 | ImagineArt | Aggregator | Multi-model video + image | Yes — explicit **1 active generation at a time** |
| 6 | invideo | Agentic + aggregator | 200+ models incl. Veo 3.1, Sora 2, Kling 3.0 | No true unlimited; credit pools per tier |
| 7 | Morphed | Aggregator | Flux 2 Pro, Sora 2 Pro, Kling 2.6, Veo 3.1, Seedream v4, Hailuo 2.3 | No — universal credits only |
| 8 | Topview | Aggregator (ecom/UGC) | Multi | No — credits; 4–8 concurrent tasks by tier |
| 9 | Pollo AI | Aggregator | Veo 3, Kling, Runway, Pika, Hailuo, Luma, Seedance | Credits; commercial rights on all paid |
| 10 | Dreamina / CapCut (ByteDance) | First-party-ish | Seedance 2.0 / 2.5 native | "Unlimited generation with eligible plans" — terms unclear |
| 11 | LTX Studio | Agentic/director | LTX-2, Veo, Kling, FLUX | No — compute-seconds |
| 12 | PixVerse | Aggregator/first-party | PixVerse + **Seedance 2.0 w/ 9-image ref** | Ultra tier = 100% off-peak (de-facto unlimited off-peak) |
| 13 | Runway | First-party | Gen-4.5, Seedance 2.0 | **Unlimited being retired 2026-09-01** → Max $95 |
| 14 | Pika | First-party | Pika 2.2 | Credits |
| 15 | Luma Dream Machine | First-party | Ray/Dream Machine | Unlimited $94.99 — **relaxed mode + overnight queue** |
| 16 | Hailuo / MiniMax | First-party | MiniMax H3 (Hailuo 3.0), 2K, native audio | Credits $7.99–$199.99 |
| 17 | Kling (Kuaishou) | First-party | Kling 3.0 | Credits; Ultra gets priority capacity |
| 18 | Google Flow / Gemini | First-party | Veo 3.1 | AI Ultra $99.99/$199.99, 25k credits |
| 19 | Grok Imagine (xAI) | First-party | Grok Imagine 1.5 | SuperGrok $30 — weekly pooled cap, 720p ceiling |
| 20 | Adobe Firefly | First-party + partner models | Firefly video + partner models | Premium $199.99 — unlimited video; promo unlimited offers |
| 21 | Vidu | First-party | Vidu Q/Cinema | Credits |
| 22 | Hedra | First-party | Character-3 | Credits from $10 |
| 23 | DomoAI | Aggregator | Multi | $9.99+ unlimited via **Relax Mode** |
| 24 | fal.ai | API/infra | Seedance 2.0 (std/fast/1080p), most models | Metered |
| 25 | Replicate | API/infra | Broad | Metered |
| 26 | BytePlus (ByteDance official) | API/infra | Seedance 2.0/2.5 official API | Metered |
| 27 | ModelsLab | API/infra | Seedance 2.0 Multi-Reference (9 img/3 vid/3 audio) | Metered |
| 28 | Atlas Cloud | API/infra | Seedance 2.0 reference-to-video | Metered |
| 29 | Poyo.ai | API/infra | Seedance 2 API | Metered |
| 30 | Lumenfall | API aggregator/price index | Seedance providers | Metered |
| 31 | SeeGen AI | Aggregator | Seedance 2.0, 9 img refs, claims no watermark | Freemium |
| 32 | ClipDance | Aggregator | Seedance 2.0 | Freemium |
| 33 | Morphic | Aggregator | Seedance 2.0 | Unknown |
| 34 | Magic Hour | Aggregator | Multi | Credits |
| 35 | Kie.ai / Novita | API/infra | Multi incl. Hailuo H3 | Metered |
| 36 | Synthesia / HeyGen | Avatar/corporate | Avatar-first | Out of scope (not cinematic gen) |

Count: 36 platforms enumerated (target was 25+).

## Leaderboard snapshot (Artificial Analysis, via search 2026-08-17)
Could not fetch the leaderboard directly (egress blocked). Search-surfaced standings:

- **Text-to-video (with audio):** Gemini Omni Flash 1241 · MiniMax H3 1238 · Dreamina Seedance 2.0 720p 1222 · Wan2.7-260612 1160 · HappyHorse-1.1 1146
- **Image-to-video (with audio):** Dreamina Seedance 2.0 720p 1197 · MiniMax H3 1191 · Gemini Omni Flash 1187 · grok-imagine-video-1.5 1112 · HappyHorse-1.1 1112
- Seedance 2.0 released 2026-02-12; Alibaba ATH HappyHorse-1.0 April 2026.
- Kling 3.0 released 2026-02-05; held top ELO as of April 2026 per Atlas Cloud.

**Client-relevant read:** Seedance 2.0 is #1 on image-to-video-with-audio — which is the exact
modality his asset-locked pipeline uses. That validates his model preference.

## Early structural finding (drives Phase 2)

Every "unlimited" tier found in this pass is implemented the same way: a **relaxed / standard /
off-peak queue that is deprioritized behind paying-per-generation traffic**, usually with low or
single concurrency. This is not a Higgsfield quirk — it is the industry's cost-control mechanism.
Named instances already found:

- Higgsfield: standard queue, 1 concurrent (own help center)
- ImagineArt: "one active generation at a time" (own policy page)
- Luma: "relaxed mode" + "overnight queue"
- OpenArt Wonder: "relaxed queue during high-traffic times"
- Krea Max: "relaxed-rate, in-house-model-only"
- DomoAI: "Relax Mode"
- Runway: killed Unlimited *because* of queueing (2026-06-01 announcement)

Implication for Phase 2: the winning answer may not be an unlimited tier at all. It may be a
**credit plan with high concurrency + off-peak discounting**, or metered API with a spend cap.
Phase 2 must test that hypothesis rather than hunting for a better unlimited.

## Kill-list seeds (to be confirmed in later phases)
- Freepik/Magnific — unlimited excludes video entirely
- invideo, Morphed, Topview, LTX Studio, Pika, Vidu, Hedra, Magic Hour — no unlimited, pure credits
- Synthesia/HeyGen — avatar/corporate, not cinematic
- Grok Imagine — 720p ceiling, opaque weekly pool
- DomoAI — Relax Mode = the failure mode
