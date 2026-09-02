# Project 2 — The Controlled Micro-Scene
**Ships: Day 10** · Budget: ~4h of the day's 5 · Target: 10–20 seconds, 3–4 shots

## Purpose
The first time your work has to be a **scene** rather than a shot. This is where continuity,
screen direction and the 180° line stop being theory. It is also the dress rehearsal for the
final film — every failure mode you hit here is one you will not hit on Day 17.

## Brief
**One subject, one location, one small event, three or four shots.**

Structure: **setup → change → consequence.** That is the whole story. Do not attempt more.

Three starting points:
1. Something arrives somewhere it should not be, and the environment reacts
2. A machine begins a process; the process goes wrong; we see the result
3. A creature notices something off-screen, moves to it, and finds it

## Hard requirements
- [ ] `shotlist.csv` with 3–4 fully populated rows, written first
- [ ] A **floor plan sketch** with camera positions and the 180° line drawn
- [ ] Every shot at **control rung ≥ 2**
- [ ] **At least one shot uses ComfyUI structural control** (Workflow A or B) for its start frame
- [ ] At least three distinct shot sizes
- [ ] Consistent screen direction across all shots
- [ ] At least one **J-cut or L-cut**
- [ ] At least one shot receives an AE pass (repair or integration)
- [ ] Continuous ambience bed + ≥3 designed effects
- [ ] Colour matched across all shots (Lumetri comparison view)
- [ ] Every shot PASSes `rubrics/shot_qc.md`; the assembly scores ≥60 on `film_qc.md`

## Deliberate constraints
- **Maximum 25 generations total** across all shots
- **One location.** If you need a second location, your scene is too big
- **No dialogue, no acting**

## Exit criteria
| # | Criterion | How to verify |
|---|---|---|
| 1 | A stranger can describe what happened | Ask one. Say nothing first |
| 2 | The location reads as one place | Can they sketch the floor plan after watching? |
| 3 | Screen direction is consistent | Log direction per shot; check adjacencies |
| 4 | The ComfyUI-controlled shot's geometry matches its depth/control input | Compare side by side |
| 5 | Film QC ≥ 60/100, no criterion below 3 | Fill the rubric |
| 6 | ≤ 25 generations | Count them |

## The most likely failure, and how to avoid it
**You will be tempted to cut a shot that "looks great" into the scene even though it breaks
geography.** Do not. A beautiful shot that breaks the 180° line does more damage to your film
than a plain shot that respects it. This is the specific discipline the project exists to build.

## Reel value
A 10–20 second continuous scene is genuinely more impressive to an employer than a 60-second
montage. Keep this even after the final film exists — it shows you can do it twice.
