# Recruiting Readiness Matrix

Evaluated against the 42 roles in `research/job_skill_matrix.csv`. Fill in the evidence column
with **your actual artifacts** on Day 21 — a claim without a linked artifact is not evidence.

---

## Part 1 — Readiness by role family

| Role family | Verdict on completion | Evidence you will have | The gap that remains |
|---|---|---|---|
| **AI Video Artist / AI Video Designer** | **READY** | Film, reel, breakdown, shot QC logs | Volume of finished work (you have 3 pieces, not 30) |
| **Generative Production Artist** | **READY** | Film + Comfy workflows + repeatable prompt system | Studio-scale throughput experience |
| **AI Filmmaker** | **READY** | Coherent scene with story, geography and payoff | Longer-form (2–5 min) work |
| **Motion + AI Designer** | **READY** | AE work, Premiere edit, sound design | Pure motion-graphics/typography craft — genuinely not taught here |
| **AI Creative Technologist (agency)** | **READY** | Console + Comfy workflows + pipeline documentation | Client-facing delivery experience |
| **Generative AI Artist** | **READY** | ComfyUI workflows with strength sweeps + LoRA usage | LoRA *training*; dataset curation |
| **AI Artist (AI-native studio)** | **READY** | Reel + identity locking + repair chain | Volume; studio pipeline conventions (ShotGrid) |
| **Creative Technologist (generalist)** | **STRETCH** | Console, Three.js background, DRCA, DJ Tutor | Interactive/installation work; a shipped client project |
| **GenAI Creative Technologist (product co.)** | **STRETCH** | Console + API integration + agentic workflow | Production software engineering depth |
| **AI/VFX Artist** | **STRETCH** | AE compositing + integration chain | **Nuke.** This is the specific blocker |
| **Design Technologist** | **STRETCH** | Front-end + generative media | Design-systems depth |
| **Creative AI Engineer** | **STRETCH → NOT READY** | Python, FastAPI, structured outputs | Real backend engineering; model-level work |
| **VFX + GenAI (traditional house)** | **NOT READY** | — | Nuke, ShotGrid, years, shot volume |
| **AI Pipeline / Production Technologist** | **NOT READY** | — | Studio pipeline exposure; ShotGrid; team scale |
| **Technical Artist (games)** | **NOT READY** | — | Engine depth, shaders, DCC tooling |

**Read this honestly.** Seven READY families is a good outcome for 105 hours. Applying to the
NOT READY families wastes your time and theirs — but the STRETCH families are worth applying to,
because portfolio frequently substitutes for YOE in this market and a strong artifact can carry
you past a nominal requirement.

---

## Part 2 — FINAL PRACTICAL ASSESSMENT (score /100)

The pass condition is not "I watched the videos". It is: **can you do the thing, start to
finish, and explain it?** Score each honestly. Partial credit allowed.

| # | Competency | Pts | How you prove it | Score |
|---|---|---|---|---|
| 1 | Take a concept to a workable premise | 5 | `01_dev/final_beats.md` + brief rationale | |
| 2 | Produce a coherent storyboard | 7 | 8–12 frame board that passes the stranger test | |
| 3 | Lock shot grammar | 7 | Shot list + floor plan + 180° line + lens progression | |
| 4 | Create controlled reference frames | 7 | Locked, hashed refs + start/end frames per shot | |
| 5 | Use 3D/previs where geometry matters | 8 | `previs_rig.py` + clay/depth passes + the shot that used them | |
| 6 | Generate video under control | 8 | All shots at rung ≥2; ≥2 at rung 4/5 | |
| 7 | Identify failed generations | 6 | Completed Shot QC sheets with failed criteria logged | |
| 8 | Repair or replace failures | 6 | Repair-chain before/after + documented abandonments | |
| 9 | Composite at least one shot | 8 | AE4 hero shot + before/after + integration toggle demo | |
| 10 | Edit a full scene | 7 | Premiere timeline, ≥3 J/L cuts, deliberate pacing | |
| 11 | Sound design | 6 | Ambience + ≥5 effects + sub-bass payoff, mixed to spec | |
| 12 | Export a professional master | 4 | Correct fps/codec/bitrate, no banding | |
| 13 | Show a reproducible Comfy workflow | 8 | Workflow A + B JSON + READMEs + strength sweep | |
| 14 | Explain the pipeline technically | 6 | Portfolio breakdown; can narrate it aloud in 3 min | |
| 15 | Show a production tool you built | 5 | Console with real production data + README | |
| 16 | Defend model and tool selection | 2 | Can answer "why Higgsfield over Runway" without notes | |
| | **TOTAL** | **100** | | |

### Thresholds

| Score | Meaning |
|---|---|
| **80+** | **RECRUITING READY** for junior / all-level applications. Apply now. |
| 65–79 | Nearly there. Identify your two lowest scores and spend 10–20 hours. See `current-role-gap-analysis.md` |
| 50–64 | The film probably shipped but the *system* around it did not. Rebuild the breakdown and the QC logs — that is usually where the points are |
| <50 | Something major was skipped. Most often: ComfyUI, or sound design |

**80+ does NOT mean senior mastery.** It means you can be handed a shot and deliver it, and you
can explain how. That is precisely what a junior/all-level GenAI production role is buying.

### Self-scoring integrity check
Before you record a score, ask: *could I do this in front of someone, on a Monday, without
looking anything up?* If not, it is at most half marks. Inflating this table only defers the
discovery to an interview, where it costs more.
