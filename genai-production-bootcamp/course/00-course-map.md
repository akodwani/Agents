# Course Map — 21 Days / 105 Hours

## The bargain

You have 105 hours. You cannot master eight tools in 105 hours and anyone who tells you
otherwise is selling something. What you *can* do is reach the **production-capable junior /
emerging professional threshold** with a portfolio that outperforms your hours.

Every hour in this plan is spent on one of four things:
**A.** output quality · **B.** control/reproducibility · **C.** employer credibility · **D.** speed.
Anything that served none of the four was cut. The cuts are documented in
`research/tool_decisions.md` — read them, because being able to defend what you *didn't* learn
is itself an interview skill.

## Hour budget

| Phase | Days | Hours | Theme |
|---|---|---|---|
| **0** | Day 0 | 1.5 | Setup + tutorial audit (do this before Day 1) |
| **1** | 1–5 | 25 | Production foundations → **ship a 5–8s study** |
| **2** | 6–10 | 25 | Control + post → **ship a 10–20s micro-scene** |
| **3** | 11–14 | 20 | 3D + virtual camera |
| **4** | 15–21 | 35 | Final production → **ship a 30–60s film + portfolio** |
| | | **105** | 5h/day × 21 = 35h/week. Fits the 30–40h/week, 90–120h envelope |

### Where the hours go

| Activity | Hours | % |
|---|---|---|
| **Making / testing / fixing** | 77 | 73% |
| Required video watching | 9 | **8.6%** ✅ (target was ≤20–25%) |
| Reading docs | 9 | 8.6% |
| QC, logging, portfolio writing | 10 | 9.5% |

**Required video: 437 minutes (7h 17m) of actual runtime.** The 9 hours budgeted across the day
headers includes buffer for pausing, rewinding and note-taking — you will not watch at 1×.
Day 0's tutorial audit adds 1.5h on top. Total video-adjacent time ≈ 10% of the course, which is
comfortably under the ≤20–25% ceiling. **This is deliberate: most of your time should be making,
and every module's authoritative source is documentation, not video.**

### Hours per tool

| Tool | Hours | Justification |
|---|---|---|
| Higgsfield + generation | 28 | The primary environment; #1 market skill |
| After Effects | 15 | #4 market skill; makes AI output shippable |
| ComfyUI / Comfy Cloud | 14 | **#2 market skill and your biggest gap** |
| Storyboard / shot grammar | 10 | Cheapest hours with the highest quality effect |
| Blender previs | 10 | Rose in value — `video_references` + Genjutsu made it load-bearing |
| Premiere | 9 | #6 market skill |
| AI dev / Console | 8 | Your differentiator; you start ahead |
| Unreal | 5 | Hiring signal only. **First thing to cut if behind** |
| Photoshop | 3 | Shrunk — models absorbed most of its old jobs |
| QC / portfolio / logging | 3 | — |

## Schedule

### PHASE 1 — PRODUCTION FOUNDATIONS (Days 1–5, 25h)
| Day | Title | Ships |
|---|---|---|
| 1 | Shot grammar and the control ladder | Shot log + first controlled generation |
| 2 | Storyboarding and locked references | 8–12 frame board + locked refs |
| 3 | Start/end frame bracketing + Console v1 | Bracketed shot + `ShotSpec` schema |
| 4 | Premiere fundamentals and pacing | Three pacing cuts |
| 5 | **SHIP: the five-second study** | **Finished 5–8s shot + sound + master** |

### PHASE 2 — CONTROL + POST (Days 6–10, 25h)
| Day | Title | Ships |
|---|---|---|
| 6 | After Effects core | AE1 — repaired artifact |
| 7 | Tracking, matting, integration | AE2 — tracked composite |
| 8 | ComfyUI on Comfy Cloud | Graph literacy + seed determinism proof |
| 9 | ComfyUI Workflow B + Console v2 | `reference_pose_to_hero_frame.json` |
| 10 | **SHIP: the controlled micro-scene** | **Finished 10–20s scene** |

### PHASE 3 — 3D + VIRTUAL CAMERA (Days 11–14, 20h)
| Day | Title | Ships |
|---|---|---|
| 11 | Blender previs rig | Three cameras + 180° line + clay renders |
| 12 | Depth/normal/mask passes + camera move | Full previs pass set + motion driver |
| 13 | Workflow A + the previs→video bridge | `previs_depth_to_cinematic.json` + Genjutsu test |
| 14 | Unreal virtual camera *(cuttable)* | Four setups + A/B verdict |

### PHASE 4 — FINAL PRODUCTION (Days 15–21, 35h)
| Day | Title | Ships |
|---|---|---|
| 15 | Lock the film: brief, beats, shot list | Shot list + floor plan (**Gate G1**) |
| 16 | Boards, hero frames, locked refs | Board + start/end frames (**Gates G2, G3**) |
| 17 | Generation pass 1 | Shots 1–5 through QC (**Gate G4**) |
| 18 | Generation pass 2 + repair | All shots PASS + repair chain applied |
| 19 | After Effects finishing | AE4 — hero shot to portfolio level |
| 20 | Edit, sound, colour, master | **Finished film** (**Gates G5, G6**) |
| 21 | Console + portfolio package | **Recruiting package complete** |

## Dependency graph — what breaks what

```
Day 1 (grammar) ──→ everything. Non-negotiable.
Day 2 (refs) ─────→ Day 3, 5, 16, 17
Day 3 (bracketing)→ Day 5, 10, 17, 18     ← the core anti-variance skill
Day 4 (Premiere) ─→ Day 5, 10, 20
Day 6,7 (AE) ─────→ Day 10, 19, 20
Day 8,9 (Comfy) ──→ Day 13, 16            ← required for "ComfyUI structural control" shot
Day 11,12 (Blender)→ Day 13, 17           ← required for "3D/previs control" shot
Day 13 (bridge) ──→ Day 17, 18            ← where the difficult motion shots come from
Day 14 (Unreal) ──→ NOTHING                ← this is why it is the safe cut
Day 15,16 ────────→ Day 17-21
```

**Only Day 14 has no downstream dependency.** If you lose a day to illness, life, or a shot that
fights you, cut Day 14 and redistribute. Do not cut Days 8–9 or 11–13 — they are what make the
final film's technique requirements achievable.

## Red-team pass (§29 Round 11)

I attacked this plan and fixed what broke.

| Attack | Verdict | Fix applied |
|---|---|---|
| **Too many tools?** | Partly guilty | Photoshop 8h→3h; Unreal 12h→5h and marked cuttable; Nuke/Resolve/C4D/Houdini/TouchDesigner cut entirely |
| **Too much watching?** | No | 437 required minutes = 8.6% of course. Well under the 20–25% target |
| **Too little making?** | No | 67% making. Every day ships an artifact |
| **Too much theory?** | Was guilty | ComfyUI trimmed to production concepts; diffusion theory removed; AE expressions cut to four |
| **Too much stochastic generation?** | Was guilty | Added the control-ladder rung system, the 6-generation abandonment cap, and a rule that no final-film shot may be below rung 2 |
| **Does 105h actually fit?** | Yes, tightly | Days 17–20 are the risk. Mitigation: Day 14 is cuttable and Day 18 has slack designed in |
| **Are exercises cumulative?** | Yes | Day 5 study → Day 10 scene → Day 21 film. Each reuses the previous day's artifacts |
| **Does the final project prove the target jobs?** | Yes | It hits ComfyUI, AE, Premiere, generative video, 3D previs, Python tooling and a portfolio — the top 8 market skills |
| **Hidden prerequisite gaps?** | Found three | (1) No colour-management grounding → added to Day 4. (2) Assumed audio sourcing → added to Day 5. (3) Assumed Comfy Cloud API access is free → **it needs a paid subscription**; flagged on Days 8 and 21 |
| **What if the tutorials are all bad?** | Handled | Every day's authoritative source is documentation, not video. Videos are supplementary. The course survives a total tutorial failure |
| **What if Higgsfield changes mid-course?** | Partly handled | The control *concepts* (start/end frames, references, motion transfer) are portable across models and vendors. The specific model ids are not — re-run `models_explore` if something 404s |

## The one thing to get right

If you do only one thing well in 21 days, make it **the control ladder** (`modules/higgsfield.md`
§4). Everything else in this course is downstream of the difference between specifying a shot
and rolling for one.
