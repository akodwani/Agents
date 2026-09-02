# Module: ComfyUI / Comfy Cloud — Structural Control

**Course hours: ~14** · Days 8, 9, 13
**Market weight: highest-priority gap.** ~26 hard requirements in the role sample. This module
is the difference between "prompts things" and "builds workflows".

---

## 1. Platform decision: Comfy Cloud, not local (DOCUMENTED)

Your GTX 1660 SUPER has **6 GB VRAM**. Current Flux-class models with ControlNet plus a video
stage do not fit. This is not a preference.

**Comfy Cloud** (verified specs):
- RTX PRO 6000 Blackwell, **96 GB VRAM**; 900+ preinstalled models; curated custom nodes
- Free tier **400 credits/month**, no card. Standard **$20/mo** (4,200 cr; $16/mo annual)
- **Max workflow runtime 30 min** (Standard/Creator), 1 hr (Pro)
- Serial queue — one prompt at a time per instance
- **The Cloud API requires an active paid subscription** — plan one $20 month if you want the
  Day 21 Console to call it for real

**Design consequences you must build around:** keep workflows under the runtime cap; do not
design for parallelism you do not have; assume a *curated* node set, not arbitrary GitHub nodes.

---

## 2. Concepts — the production subset only

This is not a diffusion theory class. You need enough to build, debug and explain.

| Concept | What you must be able to do |
|---|---|
| **Node / graph** | Read a graph, trace a tensor from load → sample → decode → save |
| **Checkpoint / model** | Pick one, and know what its ControlNets must match |
| **CLIP / text conditioning** | Positive and negative, and why negatives matter less on modern models |
| **VAE** | Latent ↔ pixel. Enough to know why a wrong VAE gives washed or blown output |
| **Latent space** | Why resolution changes composition, not just size |
| **Seed** | **Fix it.** Same seed + same graph + same inputs = same image. This is reproducibility |
| **Sampler / scheduler / steps / CFG** | Practical ranges only. Change one at a time |
| **img2img + denoise** | Denoise strength is the single most useful dial you own |
| **Mask / inpaint** | Region-limited generation |
| **ControlNet** | Depth, OpenPose, Canny, line-art — **structure imposed from outside** |
| **IPAdapter / reference conditioning** | Style and identity from an image rather than words |
| **LoRA** | *Loading and weighting* one. Training is out of scope |
| **Upscaling** | Latent vs pixel upscale; tiled hi-res |
| **Workflow JSON** | The artifact. `id` / `class_type` / `inputs` graph. Versioned in git |

### The compatibility rule that will silently ruin your day (DOCUMENTED)
**A FLUX checkpoint requires a ControlNet trained for FLUX.** SD1.5 and SDXL ControlNets are
**not** compatible with FLUX. The failure mode is not an error — it is output that quietly
ignores your control image. If your depth map appears to do nothing, check this *first*.

---

## 3. The two workflows you will build and keep

These are portfolio artifacts. Export both as JSON into `workflows/` and commit them.

### WORKFLOW A — `previs_depth_to_cinematic.json`
**Purpose: 3D/previs → controlled cinematic image. The geometry is yours; the model only
provides surface.**

```
Load Image (Blender depth pass EXR/PNG)
        │
        ├─→ [optional] Depth preprocessor / normalise range
        │
Load Checkpoint ──→ CLIP Text Encode (positive)  ─┐
        │       └─→ CLIP Text Encode (negative)  ─┤
        │                                          ├─→ ControlNet Apply (Depth, strength 0.6–0.9)
Load ControlNet (DEPTH, matched to checkpoint) ───┘        │
                                                            ↓
                                        KSampler (seed FIXED, steps 25–30, cfg 3.5–7)
                                                            ↓
                                                    VAE Decode → Save Image
```

**Why this matters:** it inverts the usual relationship. Instead of asking a model for a
composition and hoping, you *specify* the composition in Blender — camera height, focal length,
subject placement, occlusion — and the model fills in look. That is production control, and it
is exactly what "3D/previs where geometry matters" means on the final exam.

**Tuning:** ControlNet strength is your dial between "obeys geometry" (0.9) and "interprets
loosely" (0.5). Log the value you used. Below ~0.4 you have lost the control and should ask why
you rendered depth at all.

### WORKFLOW B — `reference_pose_to_hero_frame.json`
**Purpose: locked character + pose/environment → controlled hero frame.**

```
Load Image (locked character ref) ──→ IPAdapter / reference encoder ─┐
Load Image (pose or line-art from previs) ──→ ControlNet (Pose/Canny)─┤
Load Checkpoint ──→ CLIP encode (+/-) ───────────────────────────────┤
[optional] Load LoRA (style, weight 0.5–0.8) ────────────────────────┤
                                                                      ↓
                                              KSampler (seed FIXED)
                                                      ↓
                                          VAE Decode → [Upscale] → Save
```

**This is the frame you then feed to Higgsfield as `start_image`.** That handoff — Comfy
controls the frame, Higgsfield animates it — is the spine of the whole pipeline.

---

## 4. Reproducibility discipline (this is the employable part)

1. **Fix every seed.** A workflow with a random seed is a demo, not a workflow.
2. **Version workflow JSON in git** with a semantic name: `A_depth2cine_v3.json`.
3. **Write a `README.md` beside each workflow** stating: inputs, required models, expected
   runtime, credit cost, and the three parameters worth touching.
4. **Change one variable per run.** Log it. A/B, never A/Z.
5. **Record failures.** Your portfolio breakdown should show a failed depth-strength value and
   why. Employers trust people who show the failures.

---

## 5. Debugging playbook

| Symptom | First thing to check |
|---|---|
| Control image appears ignored | **ControlNet architecture ≠ checkpoint architecture** (the FLUX rule) |
| Washed out / blown / grey output | Wrong VAE, or CFG far too high/low |
| Output ignores prompt | CFG too low; or conditioning wired to the wrong sampler input |
| Identical output every run despite changes | Seed fixed *and* you edited a node not connected to the graph — trace the wire |
| Everything is different every run | Seed is randomised — fix it before debugging anything else |
| Depth map does nothing | Range/normalisation wrong (inverted near/far), or strength too low |
| Job cancelled | Exceeded the 30-min Cloud runtime cap — split the workflow |
| Node missing on Cloud | Custom node not in the curated set — find a supported equivalent |

---

## 6. Optional stretch: Wan VACE
VACE unifies t2v, reference-to-video, video-to-video (**pose and depth control**), inpainting
and outpainting in one framework; VACE 14B covers 480p–720p. Depth Anything v2 (ViT-L) is the
standard per-frame depth extractor.

**Marked OPTIONAL** because Genjutsu plus `video_references` on Higgsfield gets the same
production result far faster, and your Cloud credits are finite. Take it only if you finish
early — it is a genuinely strong portfolio piece ("I built a controlled video workflow in
ComfyUI") and is parked in `resources/future_learning.md`.

---

## 7. Exercises

**C1 — Graph literacy (60 min).** Load a default text-to-image workflow on Comfy Cloud. Without
generating, write down every node, its inputs and what it hands to the next.
**Exit: you can trace the path from checkpoint to saved pixel with no gaps.**

**C2 — Seed determinism (30 min).** Fix a seed. Run twice. Confirm the files are byte-identical
(or visually identical). Change only the seed. Run again.
**Exit: you have proven determinism to yourself, and you have the screenshots.**

**C3 — Build Workflow A (3h).** With a depth pass from Day 11–12.
**Exit: same depth map + same seed + three different prompts → three images whose *geometry* is
identical and whose *content* differs. That is the whole point of the module. Export the JSON.**

**C4 — Build Workflow B (3h).**
**Exit: your locked character rendered in a pose you specified, recognisably the same character.
Export the JSON.**

**C5 — Strength sweep (45 min).** Workflow A at ControlNet strength 0.3 / 0.6 / 0.9. Same seed.
**Exit: a labelled 3-up image and one sentence on where control breaks down. Put this in the
portfolio breakdown — it demonstrates methodology, not luck.**
