# Module: Blender as an AI Previs Instrument (NOT a 3D art course)

**Course hours: ~10** · Days 11, 12, 13
**Explicitly not taught:** modelling craft, sculpting, UV unwrapping, retopology, shading
networks, texture painting, rigging, character animation.

---

## 1. The thesis

> **Ugly 3D → controlled AI image/video is a professional workflow, not a shortcut.**

Generative models are excellent at surface and terrible at space. You are excellent at space
(or about to be) and slow at surface. So you supply geometry, camera and blocking; the model
supplies light, texture and detail. That division of labour is the entire module.

The geometry must be **geometrically correct**. It does not need to be attractive. A grey cube
in the right place with the right camera on it beats a beautiful asset shot from a made-up angle.

**Why Blender rose in value during this research:** the live Higgsfield catalog exposes
`video_references` as a first-class input role on six video models, plus
`hf_mult_motion_control` (Genjutsu) which explicitly *"transfers motion from a reference video
to subjects in reference images."* That means a 20-minute grey-box Blender animation is not a
vague influence on the output — it is the actual camera move. Previs stopped being a detour and
became the strongest control primitive you have.

---

## 2. Tooling decision (read `research/tool_decisions.md` for the full reasoning)

There are now **two** Blender MCPs, and the brief's URL was wrong.

| Option | Status | Asset generation | Use it for |
|---|---|---|---|
| **Official** Blender Foundation `blender_mcp` (~Apr 2026, `.mcpb` install, bundles API docs) | Official lab project | **No** Poly Haven / Sketchfab / Rodin | Driving the editor, authoring scripts |
| **Community** `ahujasid/blender-mcp` (Blender 3.0+, `uvx blender-mcp`) | COMMUNITY | Poly Haven (no key), Sketchfab, Poly Pizza, Hyper3D Rodin, Hunyuan3D | Optional asset convenience |
| ~~`MCPBlender/blender-mcp`~~ | **DOES NOT EXIST (404)** | — | The brief's URL is wrong |

**The decision that matters: the reproducible artifact is a `.py` file, not an MCP conversation.**

`tools/blender/previs_rig.py` in this repo is that file. Run it in Blender's Scripting tab, or
headless via `blender --background --python tools/blender/previs_rig.py`. An MCP is a
convenience for *authoring* the script. It is never a dependency for *running* it.

Three reasons, in order of importance:
1. **Stability.** No unstable software on the critical path (§34 of the brief).
2. **Reproducibility.** A script reruns identically. A chat does not.
3. **Hiring signal.** A recruiter can read `previs_rig.py`. They cannot read your chat log.

Community `execute_blender_code` runs **arbitrary Python** in Blender — the README says so.
Save your file first, every time.

---

## 3. What `previs_rig.py` gives you

```
previs_out/
  clay/    grey-box beauty frames per camera   → composition ref, start-frame base
  depth/   32-bit EXR Z + normalized PNG       → ComfyUI Workflow A (depth ControlNet)
  normal/  normal pass                          → optional ControlNet / relight reference
  mask/    object-index IDs                     → AE holdout mattes without roto
  move/    dolly camera image sequence          → Higgsfield video_references / Genjutsu driver
```

**Deliberate design choices in that script, and why:**

- **`sensor_width = 36.0`** on every camera. Without a fixed sensor, "50mm" means nothing. With
  full-frame set, your focal lengths mean what you already understand them to mean.
- **All three static cameras sit at negative Y.** The 180° line runs along the Y axis through
  the subject. This is enforced in geometry, not in a comment you might forget.
- **A foreground occluder.** A depth pass with no foreground element is nearly flat and gives
  ControlNet almost nothing to bite on. Parallax is the point.
- **Depth written as 32-bit EXR *and* normalized PNG.** Never quantise depth you intend to use
  as control; keep the PNG for eyeballing and for nodes that want 8-bit.
- **Depth inverted so near = white.** That is the ControlNet convention. Getting this backwards
  produces a control image that "does nothing", which is a maddening bug to chase.
- **The dolly move is eased, not linear.** A linear dolly reads as robotic — and the video model
  will faithfully copy that robotic feel into your shot.
- **`pass_index` set per object** (hero=10, foreground=20, background=30), so the mask pass gives
  you separable mattes for free.

---

## 4. The bridge: previs → generated shot

Three routes, in ascending order of control:

**Route 1 — Composition only.**
`clay/CAM_B_MED_50_0001.png` → Comfy **Workflow A** (depth ControlNet) → cinematic still →
Higgsfield `start_image`. You control framing and geometry; the model controls look.

**Route 2 — Camera motion.**
Encode the dolly frames to mp4, pass as `video_references` on `seedance_2_5`
(`mode: omni_reference`) or `wan3_0`. The model follows your camera path.

```bash
ffmpeg -framerate 24 -i previs_out/move/dolly_%04d.png \
       -c:v libx264 -pix_fmt yuv420p -crf 18 previs_out/move/dolly_ref.mp4
```

**Route 3 — Full motion transfer (strongest).**
`hf_mult_motion_control` (Genjutsu) with `video_references` = your dolly render and
`image_references` = your locked hero design. The motion is *yours*; the model only renders it.

**This is where the "at least one shot using 3D/previs control" requirement is satisfied — and
where you should aim your two difficult motion shots.**

---

## 5. AI-assisted 3D assets — optional, and usually unnecessary

For previs, grey boxes plus **Poly Haven** (free, no API key, available through the community
MCP) are almost always sufficient. Geometric correctness is the goal.

Reach for generated 3D only when a shot needs a *specific hero object* you cannot block by hand.
Then pick exactly one: **Tripo** (best speed/quality balance, ~$0.01/credit API, 2,000 free
credits on signup). Rodin is higher quality and aimed at hero assets you do not need; Meshy is
the strongest mainstream self-serve option; Hunyuan3D ships open weights but wants a 10–29 GB
GPU, which you do not have.

Reported production datapoint (UNVERIFIED, treat as directional): an animation studio cut hero
prop blockout from 6–8 hours of hand modelling to ~25 minutes using Rodin.

---

## 6. Hardware note
Everything in this module runs comfortably on a GTX 1660 SUPER. Grey-box EEVEE renders at 1080p
are seconds per frame. This module is *cheap* — which is exactly why it deserves 10 hours while
Unreal gets 5.

---

## 7. Exercise (the one required by the brief)

**B1 — Cinematic previs environment (4h).**
Build (or adapt `previs_rig.py` into) a scene with:
- one main subject
- one foreground object
- background geometry
- three cameras: 24–28mm wide, ~50mm medium, ~85mm close
- one simple camera move

Export: RGB/clay frame, depth pass, normal pass (optional), rough camera animation.

**Exit criteria — objective:**
1. All three static cameras are on the same side of the 180° line. Verify by sketching the
   floor plan and drawing the line.
2. The depth pass has visible near/mid/far separation (the foreground occluder reads clearly).
3. The 85mm close-up frames the subject as a genuine close-up, not a cropped medium — check the
   subject fills a comparable frame proportion to a real 85mm at that distance.
4. The camera move is eased, and reads as intentional at 24fps.
5. **The real test:** feed the depth pass into ComfyUI Workflow A and confirm the generated
   image has the *same geometry* as your clay render. If it does not, your control chain is
   broken and everything downstream of it is guesswork.
