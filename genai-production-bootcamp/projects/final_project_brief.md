# Final Project Brief
**Ships: Day 21** · Target: **30–60 seconds, 6–10 shots, ONE coherent scene**

## The standard

Not a montage. Not disconnected clips. **One scene, in one place, with one objective, that
begins, escalates and pays off.** A viewer who knows nothing must be able to tell you what
happened.

**No acting component.** Your protagonist is a creature, vehicle, machine, object or a
non-performing figure. This is a constraint that helps you: it removes the hardest continuity
problem in AI film and focuses the assessment on camera, geography, motion and finish.

---

## Three candidate briefs

All three test the same skills. **Pick one on Day 15.** They are ordered by difficulty; pick
honestly, not ambitiously — a completed Brief A beats an abandoned Brief C.

### BRIEF A — "THE SIGNAL" *(recommended — lowest continuity risk)*
A derelict mechanical object in an isolated landscape begins transmitting. Something in the
landscape responds. The reveal is *what* responds.

- **Subject:** a machine — hard silhouette, no articulation problems
- **Environment:** one exterior, sparse — desert, tundra, industrial yard
- **Escalation:** signal → environmental reaction → the responder arrives
- **Payoff:** the reveal shot
- **Why it's easiest:** static hero, minimal contact physics, environment does the work

### BRIEF B — "THE INTRUDER" *(medium)*
A creature enters a confined built environment where it does not belong, hunting something. It
finds it. The reveal is what it was hunting.

- **Subject:** a creature — organic movement, harder consistency
- **Environment:** one interior — corridor, warehouse, station
- **Escalation:** entry → search → detection → strike
- **Payoff:** the strike or the reveal of the prey
- **Why it's harder:** locomotion and contact physics are your biggest QC risks (C5)

### BRIEF C — "THE PURSUIT" *(hardest)*
A vehicle is pursued through a constrained environment and escapes by doing something
unexpected. The reveal is the escape method.

- **Subject:** a vehicle — consistency is easy, motion is hard
- **Environment:** one traversable location with clear geography
- **Escalation:** flight → closing → the trap → the solution
- **Payoff:** the escape
- **Why it's hardest:** sustained screen direction across a moving scene, plus the two most
  difficult motion shots in the course. **This is the strongest portfolio piece if you land it.**

---

## Hard requirements (all briefs)

**Story**
- [ ] One main synthetic character/object/creature/vehicle
- [ ] One coherent environment
- [ ] A clear objective and action
- [ ] Beginning · escalation · payoff/reveal
- [ ] 6–10 shots, 30–60 seconds total

**Craft**
- [ ] Consistent geography — you can draw the floor plan
- [ ] Consistent screen direction
- [ ] Deliberate lens progression you can defend in one sentence
- [ ] At least **two locked-off shots**
- [ ] At least **three distinct shot sizes**

**Technique (these are the assessment)**
- [ ] **≥2 difficult motion shots** (sustained camera movement, or complex subject motion)
- [ ] **≥1 shot using 3D/previs control** (Blender or Unreal → `video_references` or Genjutsu)
- [ ] **≥1 shot using ComfyUI structural control** (Workflow A or B for its start frame)
- [ ] **≥1 substantial After Effects composite/cleanup**
- [ ] Every shot at **control rung ≥ 2**

**Finish**
- [ ] Coherent edit with ≥3 J/L cuts
- [ ] Sound design: continuous ambience + ≥5 hard effects + sub-bass on the payoff
- [ ] Colour consistency across all shots
- [ ] Production log complete (every shot, every attempt, every abandonment)
- [ ] Exported master + 20–30s reel cut

---

## Shot-by-shot rubric

Score each shot 0–5 on each. **Shot minimum 20/30. Film minimum 80% of shots ≥ 24/30.**

| # | Criterion |
|---|---|
| 1 | **Specification match** — the shot matches what you wrote before generating |
| 2 | **Technical quality** — passes `rubrics/shot_qc.md` with 0 Critical fails |
| 3 | **Compositional strength** — the frame is deliberately composed, not accepted |
| 4 | **Continuity** — consistent with the shots either side (subject, light, direction) |
| 5 | **Motion quality** — movement reads as physically real |
| 6 | **Contribution** — the film is worse without this shot. If not, cut it |

Criterion 6 is the one people skip. Apply it ruthlessly on Day 20: a 40-second film with 7
necessary shots beats a 60-second film with 10 shots where 3 are padding.

---

## QC gates (do not skip; each one prevents a specific expensive failure)

| Gate | Day | Blocks | Catches |
|---|---|---|---|
| **G1 — Story** | 15 | Boarding | A story that cannot be told in 6–10 shots |
| **G2 — Board** | 16 | Generation | Broken geography, before it costs credits |
| **G3 — Frames** | 16 | Generation | Weak start frames — the #1 cause of bad shots |
| **G4 — Shot QC** | 17–18 | Comp | Broken shots entering AE and eating a day |
| **G5 — Assembly** | 20 | Finishing | A cut that does not tell the story |
| **G6 — Film QC** | 20 | Portfolio | Shipping something that will be judged badly |

**G2 is the highest-value gate in the course.** Fixing geography on a board costs 20 minutes.
Fixing it after generation costs a day and 40 generations.

---

## Completion standard

The film is done when:
1. Film QC ≥ 75/100 with no criterion below 3
2. Fewer than 3 AI-slop flags
3. A naive viewer correctly describes what happened
4. Every shot is reproducible from its sidecar
5. The production log is complete, **including failures and abandonments**
6. Master and reel cut are exported and named correctly

## Deliberate anti-goals

Do **not**: add a second location; add a second character; extend past 60 seconds; add dialogue
or voiceover; use a text crawl to explain the story. Every one of these is a way of avoiding the
actual difficulty, which is telling a story with camera and cutting.
