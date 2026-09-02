# Module: After Effects — Making AI Shots Look Finished

**Course hours: ~15** · Days 6, 7, 19 (+ finishing on 20)
**Market weight: 22 hard requirements. Second-highest gate after ComfyUI.**

**Goal: make AI shots look finished and integrated. NOT a motion-design curriculum.**
You are not learning to be a motion designer. You are learning to repair, integrate and finish
generated footage so it survives on a professional timeline.

---

## ⚠️ VERSION WARNING — READ BEFORE WATCHING ANY TUTORIAL

**After Effects 26.2 replaced the Roto Brush with the AI-powered Object Matte tool.**
Community reports confirm Roto Brush is absent in 26.2.1 and present in 25.6.5.
Adobe reference: `helpx.adobe.com/after-effects/desktop/roto-brush-and-refine-matte/roto-brush/object-matte.html`

- Object Matte: **click or marquee-select** the subject; AE generates the matte and tracks it.
  No painting. More accurate selection, much faster propagation.
- **Consequence: essentially every roto tutorial made before ~April 2026 is stale for the
  current UI.** Watch them for *matte judgement* — edge quality, spill, holdout — never for
  the clicks.
- Also new: **AE 26.0 added parametric meshes** (native 3D geometry inside AE).

---

## 1. Order of operations (do it in this order, always)

The single most common beginner failure is compositing before repairing.

```
0. REPAIR UPSTREAM FIRST (before AE!)
   Higgsfield: video_deflicker → bytedance_video_upscale(preset="aigc")
   Never grind in AE what a 20-cent API call fixes.
1. Ingest, interpret footage, set comp to project frame rate + resolution
2. Stabilise (if needed)
3. Matte / isolate  (Object Matte, or import sam_3_video matte)
4. Clean plate / removal (Content-Aware Fill)
5. Composite the element
6. Integrate: light wrap → colour match → defocus → motion blur → grain
7. Render to intermediate → hand off to Premiere
```

Step 6 in that order is not arbitrary. Grain goes **last and over everything**, because grain is
a property of the final image, not of any one layer. Getting this order wrong is the most
visible tell of an amateur comp.

---

## 2. Required skills

### 2.1 Foundations
Project/comp setup, frame rate discipline (pick 24 and never deviate), pre-comps, layer order,
solids, adjustment layers, render queue vs Media Encoder.

### 2.2 Animation
Keyframes; **the graph editor** (this is where amateur and professional separate — nothing in a
finished comp should have linear easing unless it is mechanical); easy-ease; hold keyframes.

### 2.3 Selection and combination
Masks (bezier, feather, expansion, animated); **track mattes** (alpha, luma, and the inverted
variants); blending modes — you need **Screen, Add, Multiply, Overlay, Soft Light** fluently and
can ignore the rest; stencil/silhouette.

### 2.4 Tracking
- **Point tracking** — for a screen replacement corner-pin, or a simple attach.
- **Planar tracking (Mocha AE)** — bundled. For any flat-ish surface: signage, screens, panels,
  walls. Mocha is the right tool far more often than beginners assume.
- **3D Camera Tracker** — solves a camera from the plate so you can place elements in space.
  On generated footage this often fails; when it does, the honest fix is to choose a locked-off
  shot instead of fighting it. Know when to abandon.

### 2.5 Isolation and cleanup
**Object Matte** (primary), Refine Matte, keying (Keylight) if you ever generate on a flat
background, **Content-Aware Fill for Video** for removals, Clone Stamp for the targeted fixes
CAF leaves behind (CAF artifacts are common — the hybrid CAF + clone approach is the
professional norm, not a failure).

### 2.6 Integration — the part that actually sells the shot
| Technique | What it fixes |
|---|---|
| **Light wrap** | Element looks pasted on. Wraps background light around the element's edge |
| **Colour match** | Lumetri/Curves on the element to match the plate's black point, white point and hue bias |
| **Defocus match** | Element is sharper than the plate. Camera Lens Blur to match |
| **Motion blur match** | Element too crisp during movement. Enable comp motion blur, or ReelSmart-style |
| **Edge treatment** | Choke/spread the matte 1–2px; kill the hard digital edge |
| **Grain match** | Add Grain / Match Grain sampled from the plate. **Always last, over everything** |

### 2.7 Deliberately excluded
Expressions beyond `wiggle()`, `time`, `loopOut()` and a linked slider. Character animation.
Complex rigging. Full motion-graphics systems. Element 3D. These do not serve the goal.

---

## 3. Which AI artifacts AE can and cannot fix

Being honest about this saves you hours.

| Artifact | Fix | Where |
|---|---|---|
| Temporal flicker | `video_deflicker` | **Upstream, not AE** |
| Softness / low res | `bytedance_video_upscale(preset="aigc")` | **Upstream** |
| Warping background object | Patch with a clean plate + track | AE — moderate |
| Morphing detail (hands, text, small props) | **Cut around it, or mask and replace** | AE — hard |
| Object popping in/out (permanence failure) | Usually unfixable | **Re-generate the shot** |
| Wrong physical motion / bad contact | Unfixable in comp | **Re-generate or re-cut** |
| Inconsistent grade between shots | Colour match | AE or Premiere — easy |
| Edge halos on generated subject | Choke + light wrap | AE — easy |
| Anatomy failure | Unfixable | **Re-generate. Do not sink AE hours into this.** |

**The rule: comp fixes surfaces, not physics.** If the shot is wrong in space or time, it is a
generation problem and going into AE is procrastination.

---

## 4. Exercises (the four required by the brief)

**AE1 — Repair an obvious AI artifact (2h).**
Take a generation with a visible failure — a warping background element or a morphing prop.
Fix it: stabilise if needed, patch or clone, track the patch, match grain.
**Exit: the artifact is invisible at 100% playback, and the patch does not slide. Export a
before/after split-screen — this goes straight into your portfolio breakdown.**

**AE2 — Track and composite a generated object into a plate (2.5h).**
Generate an object with a transparent or removable background (`sam_3_video` or
`image_background_remover` will help). Track a plate. Place the object. Integrate it fully.
**Exit: light wrap present, colour matched, defocus matched, motion blur matched, grain matched.
Toggle each integration layer off and on and be able to say what each one bought you.**

**AE3 — Integrate AI character/environment layers convincingly (3h).**
Multi-pass: generated subject on one layer, generated environment on another, atmosphere
(haze/dust/light shafts) between them.
**Exit: at least three depth layers with distinct defocus and atmospheric density. The subject
must sit *in* the environment, not on it.**

**AE4 — Finish one final-film shot to portfolio level (3h, Day 19).**
Full chain on a real shot from your film.
**Exit: passes every row of `rubrics/shot_qc.md`. Rendered to a lossless/high-bitrate
intermediate and imported into the Premiere timeline.**

---

## 5. Handoff to Premiere
- Work at project frame rate throughout (**24 fps**, decided once).
- Render an intermediate: **ProRes 422 HQ** (Mac) or **DNxHR HQX / high-bitrate H.264** if
  ProRes is unavailable on Windows. Do not hand H.264 at 10 Mbps to a colour pass.
- Dynamic Link is convenient and fragile. For a deliverable, **render the file.**
- Name it `s04_v03_comp.mov`. Version numbers, always.
