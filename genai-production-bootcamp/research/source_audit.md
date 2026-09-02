# Source Audit & Verification Ledger

Every claim in this course carries one of five labels. This file is the ledger. Read it before
you trust anything else in this repository.

| Label | Meaning |
|---|---|
| **DEMONSTRATED** | I executed it in this environment and observed the result. |
| **DOCUMENTED** | Stated by the vendor's own documentation / repository / release notes. |
| **INFERRED** | My reasoning from documented facts. Reasonable, not proven. |
| **EXPERIMENTAL** | Vendor itself labels it experimental / preview / lab. |
| **COMMUNITY / UNSTABLE** | Third-party, unofficial, may break without notice. |
| **UNVERIFIED** | Discovered but NOT inspected. Treat as a lead, not a recommendation. |

---

## 1. THE BLOCKING CONSTRAINT — READ THIS FIRST

**The tutorial-watching phase of this build could not be executed. The video evaluations in
`video_evaluations.csv` are UNVERIFIED candidate leads, not audited recommendations.**

### What was actually done (DEMONSTRATED)

| Step | Result |
|---|---|
| Inspected `bradautomates/claude-video` repo + README | ✅ Done. Install method verified as current. |
| `npx skills add bradautomates/claude-video -g` | ✅ Installed → `~/.agents/skills/watch`, symlinked to `~/.claude/skills/watch` |
| `yt-dlp` install | ✅ `2026.08.19` via pip |
| `ffmpeg` / `ffprobe` install | ✅ `6.1.1-3ubuntu5` via apt |
| `setup.py --json` preflight | ✅ `missing_binaries: []`, `can_proceed` gated only on Whisper key |
| `setup.py --check` after config | ✅ exit 0 — skill operational |
| `watch.py --help` | ✅ All documented flags present (`--detail`, `--timestamps`, `--start/--end`, `--no-whisper`) |
| **Actually watching a YouTube video** | ❌ **BLOCKED** |

### Why it is blocked (DEMONSTRATED)

This session runs behind a policy-enforcing egress proxy. `youtube.com`, `youtu.be`,
`googlevideo.com` and `i.ytimg.com` all return **HTTP 403 to CONNECT**:

```
$ yt-dlp --skip-download --print "%(title)s" "https://www.youtube.com/watch?v=..."
ERROR: Unable to connect to proxy ... Tunnel connection failed: 403 Forbidden

$ curl -sS "$HTTPS_PROXY/__agentproxy/status"
{"kind":"connect_rejected","host":"www.youtube.com:443",
 "detail":"gateway answered 403 to CONNECT (policy denial or upstream failure)"}
```

The proxy's own README states: *"The destination host is not allowed by your organization's
egress policy for this session. Do not retry or route around it — report the blocked host."*
I did not route around it. No Invidious/Piped mirror, no alternate front-end.

**The same block hit every documentation site**: `docs.comfy.org`, `helpx.adobe.com`,
`docs.blender.org`, `dev.epicgames.com`, `higgsfield.ai`, `comfy.org`, plus every job board
(`linkedin.com`, `boards.greenhouse.io`, `jobs.lever.co`). Only `github.com` /
`raw.githubusercontent.com` and package registries are reachable directly.

### What I used instead, and how much weight it carries

| Channel | Status | Weight |
|---|---|---|
| **Higgsfield MCP server (live)** | ✅ Working | **Highest.** Live API introspection = ground truth. |
| **WebSearch (hosted)** | ✅ Working | Good for docs/market. Second-hand summarisation — I flag as DOCUMENTED only where a vendor/official page is the cited source. |
| **WebFetch → github.com / raw.githubusercontent.com** | ✅ Working | Primary source for repos. |
| **WebFetch → everything else** | ❌ Blocked | — |
| **yt-dlp / watch skill** | ❌ Blocked | — |

### What this means for you, practically

1. Every video in `youtube_playlist.md` is marked **UNVERIFIED**.
2. Before Day 1, run `tools/audit-tutorials.sh` on your own machine (where YouTube resolves).
   It runs the installed `watch` skill over the candidate list and produces the visual evidence
   the rubric in `rubrics/tutorial_qc.md` needs. Budget **60–90 minutes**. This is Day 0.
3. **The curriculum does not depend on the videos.** Every module is built so the
   *authoritative* path is official documentation plus your own hands-on reps. Video is
   supplementary craft demonstration. If a candidate video fails your audit, delete it and the
   day still works. This was a deliberate design response to the constraint, and it also
   happens to satisfy §26 of the brief (primary sources beat one creator's opinion).

### One more correction to the brief

`https://github.com/MCPBlender/blender-mcp` **does not exist** — `raw.githubusercontent.com`
returns HTTP 404 for it. The canonical community project is **`ahujasid/blender-mcp`**
(DOCUMENTED, README fetched and read). More importantly, the Blender Foundation shipped an
*official* MCP server in April 2026 that did not exist when the brief was written. See
`tool_decisions.md`.

---

## 2. VERIFIED PRIMARY SOURCES

### 2.1 Higgsfield — DEMONSTRATED (live MCP introspection, 2026-09-02)

I queried the live Higgsfield MCP server. This is the strongest evidence in the whole build:
it is the platform describing its own current capabilities through its API, not marketing copy.

`models_explore(action=list, type=video)` returned `has_more: false` — a **complete** video model
list. Load-bearing findings:

- **Start-frame + end-frame bracketing is real and model-portable.** Roles `start_image` /
  `end_image` are exposed by `cinematic_studio_3_0`, `cinematic_studio_video_v2`,
  `seedance_2_0`, `seedance_2_5`, `kling3_0`, `veo3_1_lite`, `wan3_0`, `minimax_h3`,
  `flux_3_video`, `gemini_omni_flash_1_1`. This is the backbone of the anti-variance method.
- **`video_references` exists as a first-class input role** on `seedance_2_0`, `seedance_2_5`,
  `wan3_0`, `minimax_h3`, `flux_3_video`, `gemini_omni`, `wan2_6`. This is what makes a Blender
  or Unreal previs clip usable as camera/motion guidance. It is the previs→AI bridge.
- **`hf_mult_motion_control` ("Genjutsu")** — *"Transfer motion from a reference video to
  subjects in reference images."* This is the single most important control primitive on the
  platform for this curriculum and it is **not** what the brief anticipated. It converts ugly
  Blender/Unreal previs into a motion driver directly.
- **`hf_mult_replace_object`** — replace objects in a source video using reference images.
- **Repair chain exists natively**: `video_deflicker` (temporal artifact repair),
  `bytedance_video_upscale` with `preset: "aigc"` (an upscaler preset explicitly tuned for
  AI-generated content), `topaz_video`, `sam_3_video` (SAM-3 segmentation → matte extraction
  from video, `apply_mask` param).
- **Image side**: `nano_banana_2` exposes a `mask` media role and `is_inpaint` boolean — true
  masked inpainting. `flux_2_pro_outpaint` does per-side pixel expansion (negative values crop).
  `seedream_v5_pro` has `is_inpaint` + `remove_bg`. **This is why the Photoshop allocation in
  this course is small** — the frame-repair jobs Photoshop was scoped for are now one API call.
- `soul_cast` = "Consistent cinematic character identity". `soul_location` = environments.
- `supports_unlim` (free-trial unlimited) currently reports `available: false` for this account.

`get_workflow_instructions()` returned the live bundled-workflow catalog. Relevant:
**`character-sheet`** (slot-based consistent character/model sheets — directly useful for
identity locking). The rest (`ugc-*`, `ad-multiplier`, `product-photoshoot`, `faceless-video`,
`thumbnail-generation`, `narrator`, `subtitles`, `website-builder-flow`) are marketing/UGC
surfaces that the brief explicitly rules out of scope. `video-editing` (higgsedit) is a
file-backed JS editing project — interesting, but Premiere is the employer-legible skill.

Full dump: see the "Higgsfield live catalog" table reproduced in `modules/higgsfield.md`.

### 2.2 Higgsfield CLI / MCP / Skills — DOCUMENTED
- Official MCP server shipped **2026-04-30**, hosted endpoint, OAuth via Higgsfield account, no API keys.
- CLI + Skills: `npx skills add higgsfield-ai/skills` → three skills (`generate`, `soul`, `product-photoshoot`).
- Vendor's own guidance on the distinction: **MCP for chat agents** (all tools, free parameter
  choice); **CLI/Skills for coding agents** (defined structure, lower token overhead, more
  consistent output). Source: higgsfield.ai/creator-hub/help-center/mcp-cli, higgsfield.ai/cli, /skills, /mcp.

### 2.3 Comfy Cloud — DOCUMENTED
- Free tier 400 credits/mo, no card. Standard $20/mo (4,200 cr, $16/mo annual), Creator $35/mo
  (7,400 cr), Pro $100/mo (21,100 cr).
- Hardware: NVIDIA RTX PRO 6000 Blackwell, **96 GB VRAM**. 900+ preinstalled models, curated custom nodes.
- **API access requires an active paid subscription.** Ref: docs.comfy.org/development/cloud/api-reference
- Max workflow runtime **30 min** (Standard/Creator), **1 hr** (Pro). Over-limit jobs auto-cancelled.
- Serial queue: one prompt at a time per instance.
- Workflow JSON = directed graph; nodes carry `id`, `class_type`, `inputs` referencing literals
  or `[node_id, output_slot]`.

### 2.4 Unreal Engine — DOCUMENTED + EXPERIMENTAL
- **UE 5.8 ships a first-party "Unreal MCP" plugin. Epic labels it EXPERIMENTAL, localhost only.**
  Epic's own warning: incomplete in places, APIs and data formats may change, not designed for
  remote use. Exposes actor spawning, lighting, material instances, Slate inspection, automation
  tests; extensible with custom tools.
  Ref: dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor
- **Stable path: official Python.** "Python Scripting in Sequencer in Unreal Engine" (UE 5.8 docs).
  Requires **Python Editor Script Plugin** + **Sequencer Scripting** plugin enabled.
  Ref: dev.epicgames.com/documentation/unreal-engine/python-scripting-in-sequencer-in-unreal-engine
- Community MCP servers (COMMUNITY / UNSTABLE, none inspected): `sam-david/unreal-mcp`
  (127 tools, no mandatory C++ plugin, uses built-in Python + Remote Control, UE 5.3+ — the
  least invasive), `aadeshrao123/Unreal-MCP` (288 cmds), `GenOrca/unreal-mcp` (253 actions +
  `execute_python`), `ChiR24/Unreal_mcp` (C++ bridge, UE 5.0–5.8), `ZiggyMar/unreal-mcp`,
  `remiphilippe/mcp-unreal` (UE 5.7).
- Known community pain point (forums, UNVERIFIED): cine cameras resetting position when a
  transform track is added to a level sequence sitting at 0,0,0.

### 2.5 Blender — DOCUMENTED
- **Official**: Blender Foundation `blender_mcp` — projects.blender.org/lab/blender_mcp,
  docs at blender.org/lab/mcp-server. Released ~2026-04-28. Drag-and-drop `.mcpb` install;
  bundles API documentation to suppress hallucination. **No** Poly Haven / Sketchfab / Rodin
  integration. It is a Blender *lab* project — treat as EXPERIMENTAL-but-official.
- **Community**: `ahujasid/blender-mcp` — README fetched and read. Blender 3.0+, Python 3.10+.
  Install: `uv` → `uvx blender-mcp` → `uvx blender-mcp install-addon` → enable addon → start
  server from sidebar. Tools: scene inspection, object create/modify/delete, materials,
  **arbitrary Python execution**, camera positioning, rendering. Asset backends: Poly Haven
  (no API key), Sketchfab, Poly Pizza (~10.6k models), Hyper3D Rodin, Hunyuan3D.
  README's own warning: `execute_blender_code` runs arbitrary Python — save before running.
- Blender 5.1 is the current-generation release referenced by 2026 tutorial material.

### 2.6 Adobe — DOCUMENTED (this one changes the AE module materially)
- **After Effects 26.2: the Roto Brush has been replaced by the AI-powered Object Matte tool.**
  Click or marquee-select a subject; AE generates and tracks the matte with no painting.
  Adobe help page: helpx.adobe.com/after-effects/desktop/roto-brush-and-refine-matte/roto-brush/object-matte.html
  Community threads confirm Roto Brush is absent in 26.2.1 and present in 25.6.5.
  **Consequence: every Roto Brush tutorial made before ~April 2026 is stale for the current UI.**
  This is the single largest currentness trap in the whole playlist.
- AE 26.0 introduced parametric meshes (native 3D geometry inside AE).
- Content-Aware Fill for Video remains the primary object-removal tool.
- **Premiere Pro 26.x**: AI Object Masking, Generative Extend (video **and** audio as of 26.3),
  substantially upgraded Media Intelligence search, AI proxies for weaker hardware,
  Frame.io integration. Current build referenced: 26.3.x.

### 2.7 ComfyUI control stack — DOCUMENTED / INFERRED
- ControlNet types in production use: Depth, OpenPose, Canny, HED/line-art.
- **Hard compatibility rule (DOCUMENTED)**: a FLUX-based checkpoint requires a ControlNet
  trained for FLUX. SD1.5/SDXL ControlNets are **not** compatible with FLUX checkpoints.
  This is the #1 silent failure for beginners and is baked into the Day 8 failure conditions.
- Depth Anything v2 (ViT-L) is the standard per-frame depth extractor in current workflows.
- **Wan VACE** (Video All-in-one Creation and Editing) unifies t2v, reference-to-video,
  video-to-video (pose + depth control), inpainting and outpainting. VACE 14B covers 480p–720p.
  This is the open-source route for structural video control. Marked OPTIONAL in this course:
  Genjutsu + `video_references` on Higgsfield gets you the same production result for less setup.

### 2.8 Anti-variance / consistency techniques — DOCUMENTED + INFERRED
- Seedance 2.5 exposes a large multimodal reference architecture (reported as a 50-slot design)
  for locking identity and wardrobe across a take. **INFERRED** at the specific number; the
  live MCP schema confirms `image_references`, `video_references` and `audio_references` roles.
- Multi-reference stacking materially beats single-reference prompting: stacking image + video +
  audio references removes camera, lighting, pose, colour and style from the model's guesswork.
- Seed locking across a batch of related shots produces more consistent output than re-rolling
  similar prompts — where the model exposes a seed.

---

## 3. MARKET RESEARCH SOURCES

Job-board *detail pages* were egress-blocked, so role data comes from search-surfaced
descriptions and aggregator summaries rather than fetched ATS pages. Roles below are recorded
in `job_skill_matrix.csv`. Confidence is per-row; the aggregate signal is strong because the
same tool names recur across independent sources.

Named employers surfaced: Wonder Studios (NYC/LA), Publicis Groupe (NYC), Promise Studios (LA),
Latent Space Media, Leonine Studios (Munich, Mediawan), Staircase Studios, The Gardening
Club/Sweetshop, Obsidian Studio, Lightricks (NYC), Solve Intelligence (NYC), Code and Theory,
Wonder/WPP Production, Superside, C3.ai, Ksar Production.

Boards/aggregators used: aiartistjobs.co, builtinnyc.com / builtin.com, curiousrefuge.com
AI jobs board, mediabistro, ziprecruiter, indeed, glassdoor, jobright.

---

## 4. RESEARCH ROUND LOG (§29 stopping rule)

| Round | Focus | Materially new? |
|---|---|---|
| 1 | Official docs: Higgsfield/Comfy/Blender/Unreal/Adobe | **YES** — AE Object Matte; Comfy Cloud specs |
| 2 | Live job market | **YES** — ComfyUI as the dominant hard requirement |
| 3 | Tutorial discovery | **YES** — candidates found; Higgsfield tutorials all lag platform version |
| 4 | Watch candidates | **BLOCKED** (see §1) |
| 5 | Terminology/tool expansion from R1–R3 | **YES** — Genjutsu, VACE, official Blender MCP, UE 5.8 MCP |
| 6 | Search the discoveries | **YES** — UE 5.8 first-party MCP confirmed; Blender official MCP confirmed |
| 7 | Watch newly surfaced | **BLOCKED** |
| 8 | Cross-check vs docs + live MCP | **YES** — live catalog corrected several assumptions |
| 9 | Alternatives sweep (Krea/Luma/Runway/Meshy/Tripo/Rodin) | **NO** — nothing beat the stack on 2+ axes |
| 10 | Consistency/anti-variance techniques | **NO** — confirmed what the live schema already showed |
| 11 | Technical-artist / pipeline market slice | **NO** — same tool signal as Round 2 |
| 12 | Curriculum design + red-team | — (see `course/00-course-map.md` §Red-team) |

**Stopping rule satisfied**: rounds 9, 10 and 11 produced no resource, tool or technique that
would materially alter the course. Research stopped there.
