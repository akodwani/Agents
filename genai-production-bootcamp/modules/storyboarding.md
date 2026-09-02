# Module: Shot Grammar, Storyboarding and Visual Development

**Course hours: ~10** · Days 1, 2, 15, 16

This module is why your films will read as *directed* rather than *generated*. It is also the
cheapest module — it costs almost no credits and no GPU — and it has the highest effect on
final quality. Do not rush it because it feels like "not the real work". It is the real work.

---

## 1. Shot grammar: the minimum a working director must own

### 1.1 Shot sizes
| Size | Frame | Job in a scene |
|---|---|---|
| EWS / Establishing | Subject tiny in environment | Where are we. Geography. |
| WS | Full body + context | Blocking and spatial relationships |
| MS | Waist up / object in context | The working shot. Action reads. |
| MCU | Chest up | Intent, decision |
| CU | Head / detail | Emotion, or **the reveal** |
| ECU | Eye, switch, texture | Tension, information |
| Insert | Detail cutaway | Plot-critical object |

**AI-specific note that matters:** generative models fail *differently* by shot size. Wide shots
fail at geometry and object permanence; close shots fail at fine articulation and texture
continuity. **Choose the shot size that hides your model's weakness.** That is not cheating —
that is what a cinematographer does with a real lens.

### 1.2 Lens logic
| Focal (FF equiv) | Feel | Use for |
|---|---|---|
| 18–24mm | Distorted, aggressive, space expands | Environment reveals, threat approaching camera |
| 28–35mm | Naturalistic wide | Establishing, walking-with |
| 50mm | Neutral, human eye | The default. Objectivity. |
| 85mm | Compressed, subject isolates | Emotion, isolation |
| 135mm+ | Heavy compression, background collapses | Surveillance, distance, dread |

**Lens progression is a story device.** Going 24 → 50 → 85 across a scene physically tightens
the audience's attention. Going the other way releases it. Your final film must show a
*deliberate* progression, and you must be able to say what it does.

### 1.3 The three continuity rules you cannot break
1. **The 180° line.** Draw a line through your two subjects (or subject and objective). All
   cameras stay on one side. Cross it and the audience believes the subject turned around.
2. **Screen direction.** If the vehicle exits frame right, it enters the next shot frame left.
   Consistently. This is what makes six clips feel like one chase.
3. **Eyeline / attention match.** Where a subject looks in shot A must correspond to what
   appears in shot B.

**These are the rules AI films break most often**, because each clip is generated independently
with no memory of the last. A film that respects them looks professional almost regardless of
per-shot quality. This is the single highest-leverage differentiator available to you.

### 1.4 Camera moves and what each *means*
| Move | Meaning |
|---|---|
| Static / locked | Objectivity, tension, letting the audience search the frame |
| Pan / tilt | Revealing, following |
| Dolly in | Realisation, commitment |
| Dolly out | Isolation, abandonment |
| Tracking / following | Alignment with the subject |
| Crane / boom | Scale, transition, arrival or departure |
| Handheld | Urgency, subjectivity |

A move without a reason is noise. In the final film, **at least two shots must be locked off.**
Constant movement is the most common tell of an inexperienced AI filmmaker.

---

## 2. The production pipeline: concept → locked references

```
CONCEPT (1 paragraph)
   ↓
BEATS (4–6 sentences; each is a change of state)
   ↓
SHOT LIST (CSV — the contract)
   ↓
STORYBOARD (8–12 frames, fast, ugly is fine, GEOMETRY MUST BE RIGHT)
   ↓
HERO FRAMES (the 2–3 frames that define the look; slow, expensive, 4k)
   ↓
LOCKED REFERENCES (character / environment / prop — frozen, versioned, never re-rolled casually)
   ↓
START + END FRAMES per shot (derived from the above)
   ↓
VIDEO
```

**The critical distinction — production boards vs pretty images.** A production board answers:
where is the camera, how big is the subject in frame, which way is everyone facing, what is the
lens, what changes during the shot. A pretty image answers none of those and will seduce you
into a film with no geography. Boards may look bad. They may not look *wrong*.

### 2.1 The shot list is the contract
`01_dev/shotlist.csv` columns — this is also the exact schema the Shot Control Console stores:

```
shot_id, scene, size, lens_mm, camera_height, camera_angle, move, subject, action,
environment, screen_direction, duration_s, control_rung, model, refs, start_frame,
end_frame, notes
```

Fill this in **before** generating anything. If you cannot fill a row, you do not know the shot
yet, and generating will not teach you — it will just cost credits.

---

## 3. Building consistency (the part that actually breaks)

### 3.1 Character / subject
1. Build a **character sheet** first — front, 3/4, profile, at minimum. Use Higgsfield's
   `character-sheet` workflow (`get_workflow_instructions({workflow:"character-sheet"})`), which
   uses a slot-based architecture designed for exactly this.
2. Register the result as a **Soul Cast** identity (`soul_cast` — "consistent cinematic
   character identity").
3. Freeze it. `03_refs/char_hero_v3.png` is now law. Never casually regenerate a locked ref —
   version it (`v4`) and update every downstream frame deliberately.
4. Carry it into every generation via `image_references`.

Because this course requires **no acting**, prefer a subject where consistency is achievable:
a vehicle, a creature, a machine, a helmeted or masked figure, a distinctive object. Human
faces are the hardest continuity problem in AI film and you have 21 days.

### 3.2 Environment
Use `soul_location`, then lock it. Generate the *same* location at your three key lens/size
combinations before you shoot anything. If the environment cannot survive three angles, your
scene has no geography and you must simplify the location.

### 3.3 Prompt structure that is reusable, not artisanal
Keep a fixed slot order so prompts diff cleanly in git and vary in exactly one dimension:

```
[SHOT SIZE] [LENS] of [SUBJECT: locked ref] [ACTION]
in [ENVIRONMENT: locked ref].
Camera: [MOVE], [HEIGHT], [ANGLE].
Light: [KEY DIRECTION], [QUALITY], [TIME].
Look: [FILM STOCK / GRADE], [GRAIN].
```

Ten prompts built from one template beat ten hand-written prompts, because when shot 7 fails
you can see exactly which slot differed. This is literally what Wonder Studios means by
"structured, efficient, repeatable outputs".

---

## 4. Tools for this stage
| Job | Tool | Why |
|---|---|---|
| Fast boards | `nano_banana_pro` | Strong reasoning, follows structural instructions, cheap enough to iterate |
| Board frame repair | `nano_banana_2` + `mask` + `is_inpaint` | Fix one element without re-rolling the frame |
| Reframe / extend a board | `flux_2_pro_outpaint` | Per-side expansion; negatives crop |
| Hero frames | `cinematic_studio_2_5` (4k) or `soul_cinematic` | Cinema-grade stills |
| Character identity | `character-sheet` workflow → `soul_cast` | Purpose-built |
| Environment | `soul_location` | Purpose-built |

---

## 5. Exercises

**S1 — Grammar audit (45 min).** Take any 60-second sequence from a film you admire. Log every
shot: size, estimated lens, move, screen direction. Draw the 180° line.
**Exit: a shot log with ≥8 rows and the line correctly identified.**

**S2 — Beats to shot list (60 min).** Turn one of the three briefs in
`projects/final_project_brief.md` into 6–10 rows of `shotlist.csv`, fully populated.
**Exit: every column filled, no blanks, and a floor-plan sketch showing camera positions with
the 180° line drawn.**

**S3 — Coherent board (2h).** Generate 8–12 board frames from S2.
**Exit criteria (objective):**
- Subject is recognisably the same in every frame
- Environment is recognisably the same location
- Screen direction is consistent across all frames
- At least three distinct shot sizes appear
- A stranger can describe the story after viewing the boards **in order, with no narration**

That last one is the real test. If they can't, the problem is the board, not the model.
