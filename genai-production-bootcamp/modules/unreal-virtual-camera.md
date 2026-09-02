# Module: Unreal Engine — Virtual Camera and Previs ONLY

**Course hours: ~5** · Day 14 only
**This is the smallest module in the course, and that is a deliberate decision.**

## 1. Scope, and the honest cost/benefit

**Explicitly NOT taught:** gameplay programming, multiplayer, Blueprint architecture, Niagara,
materials mastery, environment art, MetaHuman animation, C++, lighting artistry.

**Why Unreal is in the course at all:** hiring signal. "Virtual production / Sequencer /
Cine Camera" on a CV opens doors that Blender alone does not — real-time engine experience
appears in ~9 hard and ~12 soft requirements in the role sample, and virtual production is the
vocabulary AI-native studios use.

**Why it only gets 5 hours:** on your hardware, Blender reaches the same previs outcome faster
and free. Unreal earns its place on *credential* more than on *capability* for this specific
21-day sprint.

> **If you fall behind schedule, Day 14 is the first day to cut.** It is the only module whose
> removal does not break a downstream dependency. Cutting it costs you a CV line, not a film.

## 2. Tooling decision — Python is the critical path (DOCUMENTED)

UE 5.8 ships a **first-party** "Unreal MCP" plugin. Epic's own documentation labels it:

> **Experimental** · localhost only · "incomplete in places" · APIs and data formats **may
> change** · "not designed for remote use"

That is a vendor telling you not to build on it yet. So:

| Path | Status | Role in this course |
|---|---|---|
| **Sequencer Python** (Python Editor Script Plugin + Sequencer Scripting) | **Official, stable** | **The taught path.** `tools/unreal/previs_sequencer.py` |
| Epic's Unreal MCP (5.8) | Official but **EXPERIMENTAL** | Optional accelerator. Always keep the Python fallback |
| `sam-david/unreal-mcp` (127 tools, **no mandatory C++ plugin**, uses built-in Python + Remote Control, UE 5.3+) | COMMUNITY | Optional, least invasive of the community options |
| Other community servers (aadeshrao123, GenOrca, ChiR24, ZiggyMar, remiphilippe) | COMMUNITY / UNSTABLE | Not recommended for a 5-hour module |

## 3. Required plugins
`Edit > Plugins`, enable and restart:
- **Python Editor Script Plugin**
- **Sequencer Scripting**  ← easy to miss; Sequencer Python fails without it
- **Movie Render Queue**

## 4. The required subset

| Concept | What you must be able to do |
|---|---|
| Project + level | Create a project, open a simple level, drop primitives |
| **Cine Camera Actor** | A virtual film camera whose **filmback, focal length, aperture and focus distance behave like the real thing** |
| **Filmback** | Set sensor size explicitly. Without it "50mm" is meaningless |
| Focal length | 24 / 50 / 85 as three distinct looks on the same geometry |
| Focus | **Manual.** Autofocus drifts and destroys repeatability |
| Aperture | Conceptual — enough to control depth of field deliberately |
| Transforms | Position and aim a camera precisely |
| **Sequencer / Level Sequence** | Multi-track editor. Set display rate to 24fps |
| **Camera Cuts track** | Cut between cameras inside one sequence |
| Keyframed transforms | A dolly, orbit, or tracking move |
| **Movie Render Queue** | Render a reference sequence out to PNG/EXR |

## 5. Known trap (COMMUNITY report, UNVERIFIED)
Users report cine cameras resetting position when a transform track is added to a level sequence
sitting at origin `(0,0,0)`. If your camera jumps to origin the moment you keyframe it: check
whether the camera is *possessable* vs *spawnable*, and set the first key from the camera's
current world transform rather than trusting the default.

`tools/unreal/previs_sequencer.py` sets the first keyframe explicitly from known coordinates
rather than from whatever the editor thinks the transform is — that is the mitigation.

## 6. The exercise (required by the brief)

**U1 — One scene, four camera setups (4h).**
Run `tools/unreal/previs_sequencer.py`, or build the same by hand:
1. Locked **wide** (24mm)
2. **Medium** (50mm)
3. **Close-up** (85mm)
4. One **3–5 second camera move** (35mm dolly)

All four must observe the same 180° line. Render each via Movie Render Queue.

**Then the actual test — does it improve control in a current video model?**
Take the rendered move, encode it to mp4, and feed it as `video_references` to
`seedance_2_5` (`mode: omni_reference`). Generate the same shot twice: once with the reference,
once without, same prompt.

**Exit criteria:**
- Four distinct camera setups exist in one Level Sequence with a working Camera Cuts track
- All observe the 180° line
- You have an A/B pair (with reference / without reference) and **a written one-paragraph
  verdict on whether the previs reference measurably improved camera control.**

That verdict is the deliverable. It is a legitimate finding either way — "I tested it and the
Blender route gave me better control per hour" is a *stronger* interview answer than pretending
Unreal was essential.

```bash
ffmpeg -framerate 24 -i Saved/MovieRenders/previs.%04d.png \
       -c:v libx264 -pix_fmt yuv420p -crf 18 ue_move_ref.mp4
```
