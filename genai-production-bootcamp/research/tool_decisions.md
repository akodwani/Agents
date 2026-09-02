# Tool Decisions

**Rule applied:** a tool may only be ADDED or SUBSTITUTED if it beats the incumbent on **at least
two** of: control, repeatability, output quality, speed, hiring signal, integration, cost
efficiency. Tool sprawl is treated as a cost, not a feature. Every ADD below states which two.

Hardware baseline assumed throughout: **GTX 1660 SUPER, 6 GB VRAM, ~22 GB RAM.** This single
constraint decides more of the stack than any preference does.

---

## THE LOCKED STACK (what you actually use)

| Stage | Tool | Status |
|---|---|---|
| Generative video + model routing | **Higgsfield** (Cinema Studio 3.0, Seedance 2.x, Kling 3.0, Veo 3.1, Wan 3.0) | KEEP |
| Motion/camera transfer | **Higgsfield Genjutsu** (`hf_mult_motion_control`) | **ADD** |
| Shot repair | **Higgsfield** `video_deflicker` + `bytedance_video_upscale(preset=aigc)` + `sam_3_video` | **ADD** |
| Storyboard + hero frames | **Nano Banana Pro / Nano Banana 2** via Higgsfield | KEEP |
| Character identity | **Soul Cast** + Higgsfield `character-sheet` workflow | KEEP |
| Structural image control | **Comfy Cloud** (hosted ComfyUI) | **ADD (substitutes local ComfyUI)** |
| Previs / spatial control | **Blender 5.x + Python (`bpy`)**, official Blender MCP as driver | KEEP, restructured |
| Virtual camera | **Unreal 5.8 + Sequencer Python** | KEEP, heavily downscoped |
| Compositing / cleanup | **After Effects 26.2+** | KEEP |
| Edit / master | **Premiere Pro 26.x** | KEEP |
| Image prep | **Photoshop** | KEEP, cut to ~3h |
| Automation + portfolio artifact | **Python + FastAPI + Pydantic + SQLite + React/TS** | KEEP |
| Agent integration | **Higgsfield MCP** (chat) / **CLI + Skills** (coding agents) | KEEP |

---

## DECISIONS IN DETAIL

### Higgsfield — **KEEP as primary**
**Why:** The live MCP probe (see `source_audit.md` §2.1) settled this. It is not a
"one-click generator" — it is a model router that exposes the exact control primitives this
curriculum is built on: `start_image`/`end_image` on ten different video models,
`video_references` as a first-class role, explicit motion transfer, and a native repair chain.
Replacing it would mean assembling five vendor subscriptions to get the same surface.
**What it replaces:** individual Runway / Kling / Luma / Veo subscriptions.
**When to use:** all video generation; all hero-frame generation; identity locking.
**Caveat:** vendor claims about Cinema Studio 3.0 ("physics-aware", "film reasoning") are
marketing until you test them. The *API surface* is verified; the *quality claims* are not.

### Higgsfield Genjutsu (`hf_mult_motion_control`) — **ADD**
**Beats on:** control + repeatability.
**Why:** *"Transfer motion from a reference video to subjects in reference images."* This is the
missing link the brief was reaching for. It converts a 20-minute grey-box Blender animation into
a deterministic motion driver for a generated shot. Without it, "previs" is a vague influence;
with it, previs is the actual camera and blocking.
**What it replaces:** hoping the prompt describes the camera move correctly.
**When to use:** any shot where the camera move or subject motion must be specific — which is
every one of the two "difficult motion shots" required in the final film.

### Higgsfield repair chain (`video_deflicker`, `bytedance_video_upscale` preset `aigc`, `sam_3_video`) — **ADD**
**Beats on:** speed + output quality.
**Why:** `preset: "aigc"` is an upscaler mode explicitly tuned for AI-generated footage.
`video_deflicker` targets the exact temporal artifact that marks a shot as AI-made.
`sam_3_video` gives you a tracked matte without hand-roto.
**What it replaces:** ~4 hours of AE grind per shot.
**When to use:** *before* the shot enters AE. Fix upstream what you would otherwise paint out.
**Rule:** never send a shot to AE that the repair chain could have fixed for pennies.

### Comfy Cloud — **ADD, substituting local ComfyUI**
**Beats on:** speed + cost efficiency (and, on your hardware, feasibility).
**Why:** 6 GB VRAM cannot run current video or large-image ControlNet workflows. Comfy Cloud
runs RTX PRO 6000 Blackwell / 96 GB VRAM with 900+ preinstalled models. Free tier: 400
credits/month, no card. Standard $20/mo. **Note the constraint that matters for the Console:
the Cloud API requires an active paid subscription** — so plan a single $20 month, not a free
tier, if you want Day 21's API integration to be live rather than mocked.
**What it replaces:** a local ComfyUI install that would fail or thrash on your GPU.
**When to use:** all structural control (depth/pose/edge → image), all workflow-JSON artifacts.
**Caveats:** 30-min workflow runtime cap (Standard/Creator); serial queue, one prompt at a time;
custom-node support is a *curated* set, not everything on GitHub. Design workflows accordingly.

### Blender — **KEEP, but restructured (Python-first, MCP second)**
**Why the restructure:** the brief assumed a community MCP would be the interface. Since then
the Blender Foundation shipped an **official** MCP (~2026-04-28, `.mcpb` install, bundles API
docs to reduce hallucination) — but it deliberately has **no** Poly Haven / Sketchfab / Rodin
asset integrations. Meanwhile the community `ahujasid/blender-mcp` has all the asset backends
and arbitrary Python execution, but is a community plugin.
**Decision:** *the reproducible artifact is a `.py` file*, not an MCP conversation. You will
write `previs_rig.py` and run it in Blender's Scripting tab. An MCP (either one) is a
convenience for *authoring* that script, never a dependency for *running* it. This satisfies
§34 — no unstable software on the critical path — and it also produces a better portfolio
artifact, because a recruiter can read a script but cannot read your chat log.
**Also note:** the brief's `github.com/MCPBlender/blender-mcp` **does not exist** (404).

### Unreal Engine — **KEEP but heavily downscoped; official Python is the critical path**
**Why:** UE 5.8 now ships a **first-party** Unreal MCP plugin — but Epic itself labels it
**Experimental**, localhost only, "incomplete in places", APIs may change, "not designed for
remote use". That is a direct instruction not to build a curriculum on it.
**Decision:** Sequencer Python (Python Editor Script Plugin + Sequencer Scripting) is the taught
path. Epic's MCP is an optional accelerator, clearly labelled. Community servers
(`sam-david/unreal-mcp` is the least invasive — no mandatory C++ plugin) are OPTIONAL only.
**Honest cost/benefit:** Unreal gets **5 hours** and one exercise. On your hardware Blender
reaches the same previs outcome faster. Unreal earns its place on *hiring signal* alone —
"virtual production / Sequencer" on a CV opens doors Blender does not. If you fall behind
schedule, **Day 14 is the first day to cut.**

### After Effects — **KEEP** (with a mandatory version warning)
**Why:** 22 hard requirements in the market sample. Non-negotiable.
**Critical currentness note:** **AE 26.2 replaced Roto Brush with the AI Object Matte tool.**
Every pre-2026 roto tutorial is stale for the current UI. This is the single biggest trap in
the playlist and is flagged on every affected entry.

### Premiere Pro — **KEEP**. Resolve **REJECTED** (same signal, extra switching cost).

### Photoshop — **KEEP but cut from a full module to ~3 hours**
**Why cut:** the live catalog shows `nano_banana_2` (mask role + `is_inpaint`),
`seedream_v5_pro` (`is_inpaint`, `remove_bg`) and `flux_2_pro_outpaint` (per-side expansion).
Frame extension, cleanup and generative fill are now one API call from inside your existing
environment. What survives in Photoshop is what models still do badly: precise hand-authored
masks and clean matte handoff to AE.

---

## EVALUATED AND REJECTED

| Tool | Verdict | Why | What would change this |
|---|---|---|---|
| **Krea** | OPTIONAL | Genuinely good — real-time node canvas, 60+ models in one room. But it is *another router*, and you already have one. Beats Higgsfield on *exploration feel*, not on control or repeatability. One axis, not two. | If you find Higgsfield's ideation loop too slow, Krea is the sanctioned swap. |
| **Runway** | REJECT as core | Gen-4.5 director controls are strong, but Higgsfield routes comparable models. Adding it is a second subscription for overlapping capability. | A Runway-specific feature becoming a job requirement. |
| **Luma** | REJECT as core | Ray 3.2's **EXR + HDR export** is the one genuinely differentiated feature here (real grading pipeline integration). Still only one axis for this course. | If you move toward finishing/grading roles, revisit — this is the strongest of the rejects. |
| **FLORA** | REJECT | Node-canvas creative tool; overlaps Comfy Cloud without Comfy's hiring signal. Employers name ComfyUI, not FLORA. | Nothing foreseeable. |
| **Meshy / Tripo / Rodin / Hunyuan3D** | OPTIONAL — pick at most ONE | For *previs*, grey-box geometry plus Poly Haven is free and sufficient; geometric correctness is the goal, not beauty. Rodin's quality is real but aimed at hero assets you do not need. | If a shot needs a specific hero object you cannot block by hand. Then: **Tripo** (best speed/quality balance, ~$0.01/credit API, 2000 free credits on signup). |
| **Wan VACE (in Comfy)** | OPTIONAL | The open-source route to structural *video* control (pose + depth + inpaint/outpaint under one framework). Technically excellent. But Genjutsu + `video_references` reaches the same production result with far less setup, and Comfy Cloud credits are finite. | If you want an employer-facing "I built a controlled video workflow in Comfy" artifact. Strong stretch goal. |
| **Nuke** | REJECT | 3-week budget. See `current_market_summary.md` §5. | A second learning sprint. |
| **DaVinci Resolve** | REJECT | Premiere carries the same signal. | Employer-specific requirement. |
| **Houdini / C4D / TouchDesigner / Rive** | REJECT | Out of scope per brief; nothing in the market data overturns it. | — |
| **Local ComfyUI (video)** | REJECT | 6 GB VRAM. Not a preference — a hardware fact. | New GPU. |
| **LoRA training** | REJECT (parked) | Real cost, painful locally, and *using* provided LoRAs (which is what Staircase Studios actually asks for) needs no training. | Parked in `resources/future_learning.md`. |
| **Higgsfield Marketing Studio / UGC / Clipify / thumbnail workflows** | REJECT | Explicitly out of scope per brief. Confirmed present in the live workflow catalog and deliberately skipped. | — |
| **Higgsfield `higgsedit` (video-editing workflow)** | REJECT | A file-backed JS editing system — genuinely interesting for your coding background. But Premiere is the employer-legible skill and the hours are scarce. | Parked. Would make a strong *second* portfolio piece. |

---

## COST PLAN

| Item | Cost | Necessity |
|---|---|---|
| Adobe CC (Premiere + AE + Photoshop) | ~$60/mo | **Required.** Non-substitutable for the target roles. |
| Higgsfield plan | Your existing plan | **Required.** Already held. |
| Comfy Cloud Standard | $20 × 1 month | **Required if** you want Day 21's live API call. Free tier (400 cr) covers the Comfy *learning*, not the API. |
| Higgsfield generation credits | ~$40–90 for the course | **Expect this.** See below. |
| Blender | $0 | Required |
| Unreal Engine | $0 | Required |
| Tripo / Meshy | $0 (free tiers) | Optional |
| Krea / Runway / Luma | $0 | Skip |
| **Total incremental** | **~$120–170 for 21 days** | |

**Generation spend discipline (this is where budgets die):**
- Iterate at **480p `fast`/`mini` tiers**; promote to 1080p/4k **only after the shot passes QC**.
  Seedance 2.0 Mini and `mode: fast` exist for exactly this.
- **Hard cap: 6 generations per shot.** Failing that cap means the *specification* is wrong, not
  the model. Go back to the start frame. See `rubrics/shot_qc.md` §Abandonment.
- Generate audio **off** (`generate_audio: false`) during iteration — you are sound-designing in
  Premiere anyway, and it costs credits on several models.
- Budget roughly: 5-second study ~8 gens, micro-scene ~25 gens, final film ~90 gens including
  repair passes.

## AVOIDABLE SPEND
Do **not** buy: a second video platform subscription; Topaz standalone (routed inside
Higgsfield); a Rodin Business plan; any "AI filmmaking course"; a GPU upgrade for this course.
