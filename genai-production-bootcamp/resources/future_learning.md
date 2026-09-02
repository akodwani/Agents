# Future Learning — The Parking Lot

Everything deliberately excluded from the 21 days, with an honest ordering and an honest reason.
**Do not start any of these until you have shipped two pieces and applied to twenty jobs.**

---

## Tier 1 — Learn these second (highest return)

### 1. Wan VACE in ComfyUI — *~15h*
Structural control for **video**, not just images: unifies t2v, reference-to-video,
video-to-video with pose *and* depth control, plus inpainting and outpainting in one framework.
Depth Anything v2 (ViT-L) is the standard per-frame depth extractor.
**Why it was cut:** Genjutsu plus `video_references` reaches the same production outcome with far
less setup, and Cloud credits are finite.
**Why to take it:** *"I built a controlled video workflow in ComfyUI"* is a materially stronger
claim than *"I used a platform's motion transfer."* This is the best single addition to your
portfolio after the course.

### 2. A second finished piece — *~25h*
Not a skill, but the highest-return use of your next 25 hours. **Two pieces is the credibility
threshold — one can be luck.** With the pipeline built, a second piece costs a quarter of what
the first did.

### 3. LoRA training — *~20h*
**Why it was cut:** real cost, painful on 6 GB VRAM, and *using* provided LoRAs — which is what
Staircase Studios actually asks for — requires no training at all.
**Why to take it:** appears as a "plus" in ~9 roles, and a custom style LoRA is a strong
consistency tool. Rent cloud GPU; do not attempt it locally.

## Tier 2 — Role-dependent

### 4. Nuke — *~50h*
**The specific blocker** for VFX+GenAI at traditional houses and for senior compositing. Node-based
compositing, deep compositing, 3D system. Take it **only if** VFX houses are your actual target —
those roles generally want 5+ years anyway, so it is a second-job skill, not a first-job one.

### 5. Unreal in depth — *~40h*
Materials, lighting, Nanite/Lumen, full virtual production, nDisplay/LED volumes. Take it if
virtual production is genuinely your target — this course's 5 hours is a signal, not a capability.

### 6. Motion-graphics craft — *~30h*
Typography, kinetic type, design systems, expressions, brand motion. Take it if pure Motion+AI
designer roles are your target. Explicitly not taught here because it does not serve AI film.

### 7. DaVinci Resolve + grading — *~20h*
Real colour science, node-based grading, HDR. Take it if you drift toward finishing roles.
Luma Ray 3.2's EXR/HDR export becomes genuinely interesting at that point.

## Tier 3 — Situational

| Topic | Hours | When |
|---|---|---|
| **Houdini** | 80+ | Only for procedural VFX/simulation roles |
| **Cinema 4D** | 30 | Only if a specific employer requires it over Blender |
| **TouchDesigner** | 40 | Real-time/installation/live-visuals work |
| **ShotGrid / pipeline tools** | — | Genuinely learned on the job; not meaningfully self-taught |
| **Long-form narrative (2–5 min)** | 40+ | After your first credit |
| **Photogrammetry / volume capture** | 25 | Named by Promise Studios; niche but differentiating |
| **Advanced React / production front-end** | 40 | Only for Design Technologist / Creative Developer paths |

## Explicitly NOT worth your time

| Topic | Why |
|---|---|
| **ML/model training from scratch** | Not what these roles hire for. The brief was right to exclude it |
| **PyTorch internals** | Same |
| **Kubernetes / distributed systems** | You are not building infrastructure |
| **Prompt-engineering "courses"** | You already learned the only part that matters: prompting is rung 0 |
| **Every new video model that launches** | The control *concepts* transfer; the model ids do not. Learn the concept once, re-run `models_explore` when a name changes |

---

## The meta-lesson worth carrying

The specific tools in this course will change. Cinema Studio 3.0 will become 4.0; AE 26.2 already
deleted a tool that a thousand tutorials teach; the model list you learned is a snapshot dated
2026-09-02.

**What does not change:** shot grammar, the 180° line, the difference between specifying and
rolling, the discipline of a QC gate, and the habit of checking documentation before believing a
tutorial. Those transfer to whatever the stack looks like in two years — and they are, not
coincidentally, the things employers are actually screening for.
