# Portfolio Case Study Template

**This document is worth more than the film.** Most AI reels are pretty pictures with no
evidence of process. A breakdown proves you can be handed a shot on a Monday and deliver it on a
Thursday. That is the actual hiring question.

Target length: **8–12 sections, scrollable in 3 minutes.** Publish as a web page (you have
Vite/React — use it), a PDF, or a Notion page. One link.

---

## 1. THE ONE-LINER
> *"A 45-second controlled GenAI sequence. 8 shots, one location, one subject. Built with a
> Blender previs rig, two ComfyUI control workflows, Higgsfield generation, and an After Effects
> finish. 91 generations, $63, 21 days."*

Lead with the numbers. Numbers signal production thinking; adjectives signal a hobbyist.

## 2. THE FILM
Embedded. Autoplay muted, with an obvious unmute. **Above the fold.**

## 3. THE BRIEF AND THE CONSTRAINTS
What you set out to make, and what you deliberately excluded.
> *"No dialogue, no human faces — I chose a subject where identity consistency was achievable in
> the time available. That constraint shaped the shot design."*

Stating a constraint you chose deliberately reads as directing. Stating none reads as luck.

## 4. SHOT GRAMMAR
Floor plan with camera positions and the **180° line**. Lens progression table with one sentence
on what it does.
> **Very few AI reels show a floor plan. It is disproportionately persuasive** because it proves
> you thought in space rather than in prompts.

## 5. STORYBOARD → HERO FRAMES
Boards beside the final shots. Show the boards even though they are ugly — the point is that the
final matches the plan.

## 6. PREVIS AND UTILITY PASSES
Clay render · depth pass · camera-move clip · the shot they produced. Include `previs_rig.py` or
a link to it.
> *"The camera move is not a prompt. It is a Blender animation transferred onto the generated
> subject via motion transfer."*

## 7. THE COMFYUI WORKFLOWS
Screenshot of each graph + link to the JSON + the README. **Include the strength sweep**
(0.3 / 0.6 / 0.9). The sweep is what demonstrates methodology rather than a lucky result.

## 8. THE CONTROL LADDER
Your Day 1 rung 0 vs rung 2 vs rung 4 comparison.
> **This is the single most persuasive exhibit you have** for the "structured, efficient,
> repeatable outputs" language that appears verbatim in real job descriptions.

## 9. THE GENERATION PIPELINE
Model selection logic, control rung per shot, iteration counts, credit spend. A table.
> *"Shot 6 needed a specific camera move, so it went to Genjutsu motion transfer with a Blender
> driver rather than a text description. Two takes instead of an unknown number."*

## 10. AFTER EFFECTS — BEFORE / AFTER
Split-screen of the hero shot. Then the integration toggle demo: light wrap, colour match,
defocus, motion blur, grain, switched on one at a time.

## 11. FAILURES AND ABANDONMENTS ← **DO NOT SKIP THIS**
Two or three shots that failed, what the QC criterion was, what you changed, and the one you
abandoned and why.
> *"Shot 4 failed contact physics (C5) four times. Sliding contact is nearly unfixable in comp,
> so I re-blocked it as a medium shot with the ground out of frame. It passed on the next take."*

Every experienced reviewer will recognise these failures because they have had them. Showing
them signals honesty and judgement. Hiding them signals inexperience — because a flawless
process is not a thing that exists.

## 12. THE TOOL
Shot Control Console: screenshot, the schema, a link to the repo, and the problem statement from
its README.

## 13. WHAT I WOULD DO DIFFERENTLY
Two or three sentences. Specific and technical, not self-deprecating.
> *"I would build the previs rig before the storyboard rather than after — the depth pass would
> have improved three more start frames at no extra cost."*

---

## Tone rules
- **Numbers over adjectives.** "91 generations, 6-take cap, $63" beats "extensive iteration".
- **Name the tools and the versions.** Specificity is credibility.
- **Never claim you did something you did not.** If a shot was one lucky take, say so.
- **Never say "AI-powered"** about your own work. Everyone reading it knows.
