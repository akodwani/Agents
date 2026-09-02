# Interview Questions

Practise these **out loud**, timed. Written answers do not transfer to speech.
Target: 60–90 seconds per answer. Every answer should name a specific artifact you can show.

---

## §1 — CRAFT (they are testing whether you are a director or a prompter)

**1. Walk me through how you made one shot, start to finish.**
> The whole interview often turns on this. Structure: *intent → specification → control method →
> generation → QC → finish*. Name the shot. Show it if you can.
> Weak answer: "I prompted it and iterated until it looked right."

**2. How do you get consistency across shots?**
> Locked, hashed references; character sheet → Soul Cast identity; start/end frame bracketing;
> image_references on every call. Then the honest part: what *stays* inconsistent and how you
> shot-designed around it.

**3. What is your process when a shot won't work?**
> The abandonment rule. Six takes, then three exits: re-specify the start frame, re-block the
> shot so the failing element leaves frame, or cut it. **Name the shot you actually abandoned.**

**4. How do you plan camera in AI video?**
> Shot list before generation; floor plan with the 180° line; lens progression with a stated
> purpose; previs in Blender for anything where the camera move must be specific.

**5. What do you do about AI artifacts?**
> The repair chain first (`video_deflicker` → `aigc` upscale), because it is cheaper than comp.
> Then AE for what is left. Then the boundary: comp fixes surfaces, not physics. Anatomy,
> object permanence and contact physics are regeneration problems.

## §2 — TECHNICAL (they are testing whether you understand or just operate)

**6. Explain a ComfyUI workflow you built.**
> Trace the graph aloud: load → conditioning → ControlNet → sampler → VAE decode → save. Name the
> ControlNet strength you chose and why. **Show the strength sweep.**

**7. Why did you use ControlNet rather than just prompting?**
> Because I wanted the geometry to be mine. Same depth map + same seed + three prompts →
> identical geometry, different content. Prompting cannot give you that.

**8. How do you make your work reproducible?**
> Fixed seeds; workflow JSON in git; sidecar JSON per generation with model, params, seed and
> **SHA-256-hashed references**; the test being that a stranger can rebuild the shot from the
> sidecar.

**9. Why Higgsfield rather than Runway or Luma?**
> It is a router, not a single model — one auth and one balance across ~25 video models, and it
> exposes the control primitives I need: start/end frames on ten models, `video_references`, and
> explicit motion transfer. Adding Runway would be a second subscription for overlapping
> capability. *Then name what would change your mind* — that shows judgement, not loyalty.

**10. What are the limits of your approach?**
> Micro-motion (cloth, hair, smoke), fine articulation, exact frame-level action timing, and
> background crowd behaviour remain stochastic even at full control. I design shots around them.

## §3 — PIPELINE (agency and studio interviews live here)

**11. How would you make this repeatable for a team?**
> The schema. A shot is structured data — validate it, diff it, template from it, batch it,
> version it. Show the Console. Then the honest limit: it is single-user and local; a team would
> need shared storage and a real asset manager.

**12. How do you control cost?**
> Iterate at 480p fast/mini tiers with audio off; promote only on QC pass; hard cap per shot;
> track credits per shot in the sidecar. **Quote your actual numbers.**

**13. How do you decide when a shot is done?**
> A written QC rubric with objective criteria and a gate, not a feeling. Show `shot_qc.md`.

**14. What would you do differently with more time / a bigger budget?**
> Have two or three specific technical answers ready. Vagueness here reads as not having thought
> past the deliverable.

## §4 — THE HONEST ONES (do not bluff these)

**15. What can't you do yet?**
> Nuke. LoRA training. Long-form. Studio pipeline tools like ShotGrid. **Say it plainly, then say
> what you did instead and why that was the right call for the time available.** Interviewers
> trust candidates who can name their edges; they discount candidates who cannot.

**16. How much of this is you and how much is the model?**
> The story, the shot design, the geography, the camera, the cut, the sound and the finish are
> mine. The pixels are generated — under constraints I specified. Then: *"Here is the same shot
> at rung 0 with no constraints"* — and show it. **The control-ladder comparison answers this
> question better than any sentence can.**

**17. Isn't this just prompting?**
> No, and the ladder comparison proves it. Rung 0 is prompting. Rung 4 is a Blender camera move
> transferred onto a locked reference between two authored frames.

## §5 — QUESTIONS YOU SHOULD ASK THEM

Asking nothing reads as passive. Ask two or three of these:

1. What does your generation-to-final pipeline look like today? Where does it break?
2. Who owns quality control on generated shots — the artist, a supervisor, or a rubric?
3. How do you handle reproducibility when a client asks for a change three weeks later?
4. Is the AI work replacing a traditional pipeline stage or sitting alongside one?
5. What is the ratio of exploration to delivery on a typical project here?
6. Which tools have you tried and abandoned, and why?

**Question 3 is the strongest one you can ask.** Almost nobody has a good answer, and asking it
signals immediately that you have thought about production rather than output.

---

## Preparation checklist
- [ ] Every answer names a specific artifact
- [ ] You can narrate the pipeline in 3 minutes with the breakdown open
- [ ] You can answer Q16 by *showing* rather than arguing
- [ ] You have rehearsed Q15 without flinching or over-apologising
- [ ] You have your numbers memorised: shot count, generation count, cost, days
