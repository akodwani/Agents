# Module: Higgsfield as a Model Router and Generative Production Environment

**Course hours: ~28 (spread across the whole course, not a block)**
**Evidence level: DEMONSTRATED — the capability tables below come from live MCP introspection
of the Higgsfield API on 2026-09-02, not from marketing pages.**

---

## 1. The reframe that makes this module worth 28 hours

Most people use Higgsfield as a slot machine with a nice UI: type a prompt, roll, roll again,
keep the good one. That habit is exactly what the market is *not* hiring for. Publicis asks for
"clean, scalable node-based generation workflows". Wonder Studios asks for "structured,
efficient, **repeatable** outputs".

So you will learn Higgsfield as three things:

1. **A model router.** ~25 video models and ~30 image models behind one credit balance and one
   auth. Your skill is *choosing*, not just prompting.
2. **A control surface.** Start frames, end frames, image references, video references, motion
   transfer, identity locks. Most of the variance you currently fight is variance you have not
   yet constrained.
3. **A programmable production environment.** MCP for conversational work, CLI + Skills for
   coding agents. This is what makes you a *creative technologist* rather than an operator.

---

## 2. The live capability map (DEMONSTRATED)

### 2.1 Video models and what they actually accept

`models_explore(action=list, type=video)` returned `has_more: false` — this is the complete list.

| Model id | Accepts | Duration | Max res | Distinguishing parameter |
|---|---|---|---|---|
| `cinematic_studio_3_0` | image, **start_image, end_image** | 4–15s | 4k | `genre` (action/horror/noir/drama/epic), `generate_audio` |
| `cinematic_studio_video_v2` | image, **start_image, end_image** | 3–12s | — | **`multi_shots` + `multi_shot_mode`**, `cfg_scale` (0–1), `speedramp`, `preset_id` |
| `seedance_2_0` | **start/end**, image_refs, **video_refs**, audio_refs | 4–15s | 4k | `mode` std/fast, `bitrate_mode`, `genre` |
| `seedance_2_0_mini` | same as above | 4–15s | 720p | budget tier — **use this for iteration** |
| `seedance_2_5` | **start/end**, image/video/audio refs | 4–30s | 1080p | `mode`: t2v / **omni_reference** / **video_edit** / **video_extension** |
| `kling3_0` | **start_image, end_image** | 3–15s | 4k | multi-shot, audio sync, motion transfer |
| `kling3_0_turbo` | start_image | 3–15s | 1080p | fast/budget |
| `veo3_1` | start_image | 4/6/8s | ultra | `quality` basic/high/ultra |
| `veo3_1_lite` | **start_image, end_image** | 4/6/8s | — | budget batch |
| `wan3_0` / `wan3_0_prime` | **start/end**, image/video/audio refs | 2–30s | 1080p | `enable_thinking`, smart duration (-1) |
| `wan2_7` | start/end, audio_refs | 2–15s | 1080p | character consistency |
| `minimax_h3` | **start/end**, image/video/audio refs | 4–15s | 2K | `batch_size` 1–4 |
| `flux_3_video` | **start/end**, image_refs, video_refs | 5–20s | 1080p | video **continuation** |
| `gemini_omni_flash_1_1` | **start/end**, image/video refs | 3–10s | 4k | `mode`: t2v/i2v/ref2v/**edit** |
| `grok_video_v15` | start_image, image/audio refs | 2–15s | 1080p | physics, camera-motion (preview) |
| **`hf_mult_motion_control`** | **image_refs + video_refs** | — | 1080p | **"Transfer motion from a reference video to subjects in reference images"** |
| **`hf_mult_replace_object`** | image_refs + video_refs | — | 1080p | replace objects in a source video |

**Utility / repair (these are why your shots will look finished):**

| Model id | Function |
|---|---|
| `video_deflicker` | Temporal artifact repair — the flicker that screams "AI" |
| `bytedance_video_upscale` | `preset: "aigc"` is tuned for AI-generated footage. `fps` 24–60, up to 4k, `model_version` std/pro |
| `topaz_video` | Enhancement + frame interpolation |
| `sam_3_video` | SAM-3 video segmentation → tracked matte. `apply_mask` bool |
| `video_upscale`, `sync_so` | Generic upscale; lipsync (unused — no acting in this course) |

### 2.2 Image models that matter for this course

| Model id | Use in this pipeline |
|---|---|
| `nano_banana_pro` | **Storyboard frames + hero frames.** 1k/2k/4k, strong prompt reasoning |
| `nano_banana_2` | **Frame repair — exposes a `mask` media role and `is_inpaint`.** True masked inpainting |
| `soul_cinematic` (Soul Cinema) | Cinema-grade stills / concept art, accepts `soul_id` |
| `soul_cast` | **Consistent cinematic character identity** (`budget` 10–500) |
| `soul_location` | Environment / location generation |
| `cinematic_studio_2_5` | Cinema Studio Image, up to 4k |
| `seedream_v5_pro` | Instruction editing, `is_inpaint`, `remove_bg`, 2k |
| `flux_2_pro_outpaint` | **Per-side pixel expansion** (negative values crop) — reframing without Photoshop |
| `gpt_image_2` / `openai_hazel` | Text rendering, typography, diagrams (titles, end cards) |

### 2.3 What is deliberately ignored

The live workflow catalog also exposes `ad-multiplier`, `marketing_studio_video`, `ms_image`
(DTC ads), all six `ugc-*` workflows, `faceless-video`, `thumbnail-generation`, `clipify`
(Personal Clipper), `narrator` and `website-builder-flow`. **All out of scope** per the brief.

**One exception worth taking:** the `character-sheet` workflow. It builds slot-based consistent
character/model sheets. That is identity locking, which is core. Load it with
`get_workflow_instructions({workflow: "character-sheet"})`.

---

## 3. Model selection logic — the decision you get paid for

Do not memorise "best model". Route by **what constraint the shot has**.

```
Does the shot need a specific camera move or specific subject motion?
├─ YES → do you have a previs clip (Blender/Unreal render)?
│        ├─ YES → hf_mult_motion_control (Genjutsu)          ← strongest control
│        └─ NO  → seedance_2_5 (omni_reference) with video_references
└─ NO  → does the shot have to start and end on specific images?
         ├─ YES → any start/end model. Default: seedance_2_0 (fast tier to iterate)
         └─ NO  → does it need >15 seconds?
                  ├─ YES → seedance_2_5 (to 30s) or wan3_0 (to 30s)
                  └─ NO  → cinematic_studio_3_0 for look, veo3_1 for realism,
                           kling3_0 for physical motion
```

**Iteration tier discipline (this is a money rule):**
`seedance_2_0_mini` or `mode: "fast"` at **480p** with `generate_audio: false` until the shot
passes QC. Only then re-run the *same* specification at 1080p/4k `std`. Changing resolution
changes the result somewhat — accept that; it is still far cheaper than iterating at 4k.

---

## 4. The anti-gambling control ladder

Every rung removes a category of randomness. Climb until the shot is deterministic enough.

| Rung | Control | What it removes |
|---|---|---|
| 0 | Text prompt only | *Nothing.* This is the slot machine. |
| 1 | **Start frame** | Composition, framing, lighting, subject design, lens feel at t=0 |
| 2 | **Start + end frame** | The *entire arc* of the shot. The model now interpolates instead of inventing |
| 3 | **+ image_references** | Identity, wardrobe, props, colour, style across shots |
| 4 | **+ video_references** | Camera path and timing |
| 5 | **Genjutsu motion transfer** | Motion itself — driven by your previs, not the model's guess |
| 6 | **+ Soul Cast / character sheet** | Character identity locked as a reusable asset |

**Rule of the course: no shot in the final film may be generated below Rung 2.**
At least two shots must reach Rung 4 or 5.

### What remains stochastic even at Rung 5
Be honest with yourself and with interviewers about this. Even fully constrained:
- micro-motion of cloth, hair, smoke, water
- exact sub-pixel timing of an action beat
- fine hand/finger articulation
- background crowd and foliage behaviour
- grain, compression and micro-contrast between takes

You do not fix these by re-rolling. You fix them by **choosing shots that do not depend on
them**, or by repairing them in post. That is a director's decision, not a prompting problem.

### Reasonable iteration counts
| Rung | Expected takes to a usable shot |
|---|---|
| 2 (start+end) | 2–4 |
| 4 (+video ref) | 2–3 |
| 5 (Genjutsu) | 1–3 |

**Abandonment rule: at 6 failed takes, stop.** The specification is wrong. Go back and fix the
start frame, or change the shot. Six failures is a design signal, not bad luck.

---

## 5. Production organisation

Higgsfield generations are disposable; **your specifications are not**. Everything lives in git:

```
project/
  01_dev/        script.md, beats.md, shotlist.csv
  02_boards/     board_s01.png ...
  03_refs/       char_hero_v3.png, env_alley_v2.png, prop_*.png
  04_previs/     blender/previs_rig.py, renders/, depth/, clay/
  05_frames/     s01_start_v2.png, s01_end_v2.png ...
  06_gen/        s01_v01.mp4 ... + s01_v01.json  ← the spec that made it
  07_comp/       AE projects
  08_edit/       Premiere project
  09_master/     final exports
  shots.db       Shot Control Console
```

**Every generated file has a sidecar JSON** recording model id, all parameters, media roles and
the reference file hashes. If you cannot reproduce a shot from its sidecar, it is not a
production asset — it is a lucky accident. The Shot Control Console (Day 21) automates this.

---

## 6. MCP vs CLI + Skills (DOCUMENTED)

| | MCP | CLI + Skills |
|---|---|---|
| Built for | Chat agents (Claude web/desktop) | **Coding agents (Claude Code, Cursor)** |
| Surface | All tools, free parameter selection | Each skill has a defined structure |
| Token cost | Higher | **Lower** |
| Output consistency | Varies with the model's parameter choices | **More consistent by design** |
| Setup | Add hosted MCP server URL, OAuth via account, no API keys | `npx skills add higgsfield-ai/skills` → `generate`, `soul`, `product-photoshoot` |

Official MCP server shipped **2026-04-30**.

**Use both, for different jobs:** MCP when exploring interactively ("what models support end
frames?"); **CLI/Skills when batch-generating from your shot list**, because that is the part
that must be repeatable. The Shot Control Console targets the CLI/Skills path.

---

## 7. Exercises

**H1 — Router literacy (45 min).** Without generating anything, write the model choice and the
justifying *constraint* for ten shot descriptions supplied in
`projects/final_project_brief.md`. Check against §3. **Exit: 8/10 correct.**

**H2 — Control ladder ablation (90 min).** One shot. Generate it at Rung 0, Rung 1, Rung 2 and
Rung 4. Same intent each time. Put the four side by side in Premiere.
**Exit: you can state, in one sentence per rung, exactly what stopped varying.** This single
exercise is the most persuasive thing you will have in an interview — keep the comparison.

**H3 — Repair chain (60 min).** Take your worst usable generation. Run `video_deflicker` →
`bytedance_video_upscale(preset="aigc")`. Screenshot before/after at 200%.
**Exit: a measurable reduction in temporal flicker you can point at.**

**H4 — Identity lock (60 min).** Build a character sheet via the `character-sheet` workflow,
register it as a Soul Cast identity, and generate the same character in three different
environments and lighting conditions. **Exit: a stranger identifies all three as the same
character without being told.**
