# Current Market Summary — GenAI Filmmaker / Creative Technologist
Compiled 2026-09-02. Source confidence and collection limits: see `source_audit.md` §3.

## 1. Headline

The market has split into **three distinct buyer types**, and they want different proofs.
Building for all three at once is what makes this career target coherent rather than scattered.

| Buyer | Example employers | What they actually buy | Dominant proof |
|---|---|---|---|
| **A. AI-native studios** | Wonder Studios, Promise, Staircase, Leonine, Latent Space Media | Shot-level output at broadcast quality, fast | A reel + a shot you can explain |
| **B. Agencies / brand** | Publicis, Monks, Code and Theory, Superside, WPP Production | Repeatable workflows that survive client revisions | Pipeline thinking + Adobe finishing |
| **C. Product / platform** | Lightricks, C3.ai, Solve Intelligence, AI tool companies | Someone who can build *and* film | Code + video in one portfolio |

Your existing JS/Three.js/agentic background is nearly worthless to Buyer A, moderately useful
to Buyer B, and a **differentiator** for Buyer C. The Shot Control Console exists to convert
that background into a legible artifact for B and C without costing you Buyer-A craft time.

## 2. Skill frequency — weighted by how often it appeared as a hard requirement

Counts are across the ~40 roles recorded in `job_skill_matrix.csv`. "Hard" = listed under
requirements/qualifications; "Soft" = listed under nice-to-have/plus.

| Rank | Skill | Hard | Soft | Course hours | Verdict |
|---|---|---|---|---|---|
| 1 | **Generative video platforms** (Kling, Veo, Seedance, Runway, Luma, Sora) | 34 | 4 | ~28 | Core. Higgsfield routes all of these. |
| 2 | **ComfyUI / node-based AI workflows** | 26 | 9 | ~14 | **Core. Highest-leverage single gap you have.** |
| 3 | **Portfolio / reel** (often explicitly substitutes for YOE) | 31 | 0 | ~10 | Core. Terminal deliverable. |
| 4 | **After Effects** | 22 | 6 | ~15 | Core. |
| 5 | **Generative image models** (Midjourney, Nano Banana, Flux, Seedream) | 21 | 5 | ~10 | Core — you are already partly here. |
| 6 | **Premiere Pro / NLE** | 18 | 7 | ~9 | Core. |
| 7 | **Prompt engineering as a *repeatable system*** | 17 | 3 | woven | Core. Wonder Studios words it as "structured, efficient, repeatable outputs". |
| 8 | **Python** | 14 | 8 | ~8 | Core for Creative Technologist track. |
| 9 | **Photoshop** | 13 | 6 | ~3 | Reduced — see §4. |
| 10 | **3D DCC** (Blender / C4D / Maya) | 12 | 11 | ~10 | Core *as previs only*. |
| 11 | **ControlNet / SD / LoRA / IP-Adapter** | 11 | 9 | ~6 | Core (inside ComfyUI). LoRA *training* excluded. |
| 12 | **Real-time engine** (Unreal / Unity) | 9 | 12 | ~5 | Reduced to virtual camera only. |
| 13 | **Nuke** | 7 | 5 | 0 | **Excluded** — see §5. |
| 14 | **Upscaling / restoration** (Topaz) | 6 | 6 | woven | Core, cheap to add. |
| 15 | **Version control / pipeline hygiene** (Git, ShotGrid) | 5 | 7 | woven | Core, nearly free for you. |
| 16 | **DaVinci Resolve** | 4 | 8 | 0 | Excluded — Premiere covers the same signal. |
| 17 | **AI-assisted coding tools** (Claude Code, Cursor) | 3 | 6 | woven | Free — you already have this. |

### The three sentences that matter most

1. **ComfyUI is the gate.** It appears as a hard requirement in roughly two-thirds of serious
   listings and it is the one thing on that list you currently cannot do. It separates
   "person who prompts" from "person who builds workflows" in every job description that
   bothers to draw the line.
2. **Adobe finishing is the second gate**, and it is what makes AI output *shippable*. Agencies
   in particular do not believe a reel that has never been through a comp.
3. **Portfolio substitutes for years of experience far more often than in adjacent fields.**
   Multiple listings state this outright. This is the structural reason a 21-day sprint can
   move the needle at all — you are buying a portfolio, not a credential.

## 3. Concrete requirement language worth internalising

Verbatim-ish patterns that recurred, paraphrased from surfaced descriptions:

- **Wonder Studios** (Creative Technologist, NYC/LA): *demonstrated experience using generative
  AI tools in creative production (Midjourney, Nano Banana/Veo, Runway, Kling, Flux, ComfyUI or
  similar)*; *portfolio demonstrating strong visual design, conceptual thinking, and
  AI-integrated workflows*; *art direction across still, motion, and interactive*.
- **Wonder Studios** (AI Artist): *fluency in prompt engineering with the ability to translate
  creative intent into **structured, efficient, repeatable outputs** across image, video, and
  production systems*; familiarity with Premiere/AE/Blender/C4D/Nuke/Resolve; ComfyUI and
  node-based workflows.
- **Publicis Groupe** (AI Artist, Creative Technologist, NYC — $73,150–$112,554): 3–6 yrs;
  *evaluate emerging generative AI tools in the video, motion and image space*; *prototype and
  refine AI-assisted visual pipelines*; *develop clean, scalable node-based generation workflows
  including ComfyUI*; dataset curation and model testing. 3–5 yrs motion/animation/VFX.
- **Promise Studios** (Generative VFX Artist): *hands-on experience integrating Stable Diffusion,
  ControlNet or other image/video synthesis models into an artistic workflow*; ComfyUI or
  similar node-based AI interfaces a significant plus; photogrammetry familiarity; **ShotGrid**
  / professional asset + version control.
- **Superside** (AI Video Creative, remote): *strong foundation in filmmaking, cinematography,
  or post-production* — i.e. craft first, AI second.
- **Senior AI/Motion Designer** roles: expert Adobe CC (Pr, AE, Ps, Ai), often + C4D, 6–10 yrs,
  *familiarity with AI video/motion tools used in professional pipelines*.

## 4. Where the market moved *against* the brief's assumptions

- **Photoshop's role has shrunk.** The live Higgsfield catalog exposes `nano_banana_2` with a
  `mask` role + `is_inpaint`, `seedream_v5_pro` with `is_inpaint`/`remove_bg`, and
  `flux_2_pro_outpaint` for per-side canvas expansion. The frame-prep and frame-repair jobs
  Photoshop was scoped for are now one API call. Photoshop drops to ~3h — enough for masks,
  selections, and matte handoff to AE, which is the part no model replaces.
- **Roto is no longer a skill you grind.** AE 26.2's Object Matte plus Higgsfield's
  `sam_3_video` (SAM-3 video segmentation with `apply_mask`) mean the employable skill is now
  *judging and fixing* a matte, not pulling one by hand.
- **"Motion reference" became a first-class API input.** `video_references` on Seedance
  2.0/2.5, Wan 3.0, MiniMax H3, FLUX 3 Video, and Genjutsu's explicit motion transfer mean
  previs is no longer a nice-to-have detour — it is the highest-leverage control you have.
  This *raises* Blender's value while *lowering* Unreal's (Blender gets you a motion driver
  faster, for free, on a 1660 SUPER).

## 5. Deliberate exclusions and the market cost of each

| Excluded | Appears in | Why excluded | Cost to you |
|---|---|---|---|
| **Nuke** | ~12 roles, VFX-leaning | 3-week budget; AE covers the compositing *concept* and far more listings. Nuke is a 2nd-job skill. | Closes senior VFX-comp doors. Acceptable — those want 5+ yrs anyway. |
| **DaVinci Resolve** | ~12 | Premiere carries the same "can you edit" signal at lower switching cost | Near zero |
| **Houdini** | ~4 | Not a GenAI-adjacent skill at junior level | Zero |
| **LoRA training** | ~9 (mostly soft) | Real time cost, 6 GB VRAM makes local training painful, and you can *use* provided LoRAs without training them | Small. Parked. |
| **Cinema 4D** | ~9 | Blender covers the 3D signal | Small |
| **Traditional 3D modelling/sculpting/UV** | — | Explicitly out of scope, and previs doesn't need it | Zero |

## 6. Realistic outcome after 105 hours

**Honest framing:** this course targets the *lower* boundary of hireability, and it gets there
by making your portfolio disproportionately strong relative to your hours.

- **READY**: AI Video Artist / Generative Production Artist / Motion+AI (junior), AI Creative
  Technologist at agencies, AI-native studio production artist, freelance AI filmmaker.
- **STRETCH**: Creative Technologist (senior-titled but junior-scoped), GenAI Creative
  Technologist at product companies, AI/VFX artist at AI-native studios.
- **NOT READY**: VFX+GenAI at traditional VFX houses (needs Nuke + years), AI Pipeline TD
  (needs real studio pipeline exposure), Technical Artist at game studios.

See `recruiting/readiness_matrix.md` for the evidence-backed version of this.
