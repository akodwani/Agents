# Project 1 — The Five-Second Study
**Ships: Day 5** · Budget: ~3h of the day's 5 · Target: 5–8 seconds, one shot

## Purpose
Prove — to yourself, before anything else is at stake — that you can produce a **specified**
shot rather than a *found* one. This is the smallest possible complete unit of the pipeline,
and it is also your first piece of portfolio material.

## Brief
**One subject. One environment. One camera move. One idea.**

Pick a subject with a hard silhouette and no face: a vehicle, a machine, a creature, a
distinctive object. Face-free is a requirement, not a preference — facial consistency is the
hardest continuity problem in AI film and you are five days in.

Three starting points (pick one, or bring your own):
1. A weathered mechanical object powering up in a dark space — the reveal is the light
2. A creature emerging from cover into a shaft of light — the reveal is the creature
3. A vehicle arriving and stopping hard in a specific location — the reveal is what it stopped for

## Hard requirements
- [ ] Written shot spec **before** any generation (one `shotlist.csv` row, all columns)
- [ ] **Control rung ≥ 2** — start frame AND end frame. No exceptions
- [ ] Locked reference for the subject, versioned in `03_refs/`
- [ ] A deliberate camera move with a stated reason
- [ ] Passes `rubrics/shot_qc.md` (PASS, not CONDITIONAL)
- [ ] Sidecar JSON complete enough that a stranger could rebuild it
- [ ] Sound: at minimum an ambience bed + one hard effect
- [ ] Exported master, 24fps, 1080p+

## Deliberate constraints (these are the lesson)
- **Maximum 8 generations.** Track every one.
- **No AE.** This project tests generation control, not repair. If it needs comp, it failed.
- **One environment only.** No cutaways.

## Exit criteria
| # | Criterion | How to verify |
|---|---|---|
| 1 | The shot matches your written spec | Read the spec aloud while watching. Discrepancies count |
| 2 | Shot QC = PASS | Fill the rubric. Do not self-forgive |
| 3 | ≤ 8 generations | Count them |
| 4 | Reproducible | Regenerate from the sidecar. Is it recognisably the same shot? |
| 5 | Sound is present and deliberate | Mute it — does the shot get noticeably worse? It should |

## What you learn
The gap between "I got a nice clip" and "I made the clip I specified". Almost everyone
discovers on this project that their prompt was doing far less work than they believed, and
that the start frame was doing almost all of it.

## Reel value
This becomes a 5–8 second beat in your reel and a social post. Keep the **rung 0 vs rung 2**
comparison (from exercise H2) — that side-by-side is more persuasive to a hiring manager than
the finished shot is.
