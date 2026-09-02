# Shot QC Rubric

**Apply to every generated shot BEFORE it enters After Effects.**
A shot that fails this gate does not get comped — it gets regenerated or cut. Comping a broken
shot is the most common way beginners lose a week.

## How to run it (4 minutes per shot)

1. Extract first / middle / last frame and view the 3-up:
   `python3 tools/frames.py 06_gen/s04_v02.mp4 --out qc/`
2. Play at **100% speed**, then at **25% speed**, then **backwards**. Backwards playback is
   startlingly good at exposing temporal artifacts your eye smooths over forwards.
3. Score each criterion **PASS / MINOR / FAIL**.
4. Apply the gate below.

## Gate (objective)

| Result | Condition |
|---|---|
| **PASS** | 0 FAIL on Critical · ≤2 MINOR total |
| **CONDITIONAL** | 0 FAIL on Critical · 3–5 MINOR — proceed **only if** every MINOR is fixable in AE, and you name the fix now |
| **FAIL** | Any FAIL on a Critical criterion, **or** ≥6 MINOR |

---

## CRITICAL — any FAIL here kills the shot

| # | Criterion | FAIL looks like |
|---|---|---|
| C1 | **Subject consistency** | Subject changes design, colour, proportion or markings mid-shot |
| C2 | **Anatomy / structure** | Extra or missing limbs, wheels, legs; impossible joints; melted structure |
| C3 | **Physical plausibility** | Objects pass through each other; gravity ignored; mass reads wrong |
| C4 | **Object permanence** | Something appears from nothing or vanishes without leaving frame |
| C5 | **Contact physics** | Feet/wheels/tools slide on the ground instead of gripping. Floating contact |
| C6 | **Camera intent** | The camera does something other than the move you specified |
| C7 | **Screen direction** | Subject travels the wrong way relative to the adjacent shots |

**C5 deserves special attention.** Sliding contact is the single most reliable "this is AI" tell,
and it is nearly unfixable in comp. Catch it here.

## MAJOR — 2+ FAILs here means regenerate

| # | Criterion | FAIL looks like |
|---|---|---|
| M1 | **Wardrobe / prop consistency** | Details change between start and end of shot |
| M2 | **Lighting direction** | Key light flips side mid-shot, or contradicts adjacent shots |
| M3 | **Perspective** | Lens feel doesn't match the specified focal length; converging lines wrong |
| M4 | **Motion quality** | Stuttering, rubber-banding, unnatural acceleration, wrong weight |
| M5 | **Background stability** | Background warps, swims or breathes independently of camera motion |
| M6 | **Temporal artifacts** | Flicker, boiling texture, frame-to-frame identity drift |
| M7 | **Focus / DoF consistency** | Focus plane wanders; depth of field inconsistent with stated aperture |
| M8 | **Facial consistency** *(only if a face is visible)* | Identity drifts across frames |

## MINOR — count them, fix in post

| # | Criterion |
|---|---|
| N1 | Edge artifacts / halos around the subject |
| N2 | Grain mismatch with adjacent shots |
| N3 | Colour cast drift |
| N4 | Minor background element instability outside the region of interest |
| N5 | Softness / resolution shortfall (usually fixable via `bytedance_video_upscale` preset `aigc`) |
| N6 | Micro-flicker (fixable via `video_deflicker`) |
| N7 | Slightly wrong shot duration for the intended cut |
| N8 | Audio sync — *n/a in this course unless you used native audio* |

---

## Decision tree after a FAIL

```
FAIL
 ├─ Critical C1/C2/C4/C5 (consistency, anatomy, permanence, contact)
 │    → Are you below control rung 2?  → RAISE THE RUNG. Add start+end frames. Regenerate.
 │    → Already at rung 2+?            → The START FRAME is the problem. Fix the frame, not the prompt.
 │
 ├─ Critical C3/C6 (physics, camera)
 │    → Add a video_reference or use Genjutsu. The model cannot infer your intent from words.
 │
 ├─ Critical C7 (screen direction)
 │    → Usually a shot-list error, not a generation error. Check your 180° line. You may be
 │      able to fix it by horizontally flipping the shot — check for asymmetric details first.
 │
 └─ Major only
      → Attempt ≤ 6?  → one targeted change, regenerate
      → Attempt = 6?  → ABANDON. See below.
```

## Abandonment rule (this is the anti-gambling clause)

**At 6 failed generations of the same shot, stop generating.**

Six failures is not bad luck — it is evidence that your *specification* is wrong. Take one of
these three exits:

1. **Re-specify.** New start frame, new end frame. Most failures die here.
2. **Re-block.** Change shot size or camera angle so the model's weakness is out of frame.
   A close-up that keeps failing often works as a medium. This is a legitimate directorial
   choice, not a compromise.
3. **Cut the shot.** Your film has 6–10 shots. If one costs 20 generations, it is buying you
   less than a different shot would.

Record the abandonment in your production log with the reason. **Abandonments belong in your
portfolio breakdown** — they demonstrate judgement, and every experienced person reviewing your
work will recognise that. Hiding them makes you look inexperienced, not flawless.

## Log every shot

```
shot_id | attempt | rung | model | result | failed_criteria | action_taken | credits
S04     | 1       | 2    | seedance_2_0 | FAIL | C5, M4 | added video_ref from previs | 18
S04     | 2       | 4    | seedance_2_0 | PASS | —      | promote to 1080p            | 22
```

This table is a portfolio asset. Keep it.
