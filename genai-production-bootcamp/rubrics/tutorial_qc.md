# Tutorial QC Rubric

**Use with `tools/audit-tutorials.sh`.** Score every candidate in
`research/video_evaluations.csv` before spending time on it.

> **Why this rubric exists and why it is unfilled:** the environment that built this course could
> not reach YouTube (HTTP 403 at the egress proxy — see `research/source_audit.md` §1). Every
> candidate is UNVERIFIED. **You run this audit.** It takes 60–90 minutes and it is Day 0.

## The rule that saves the most time

**Never judge a tutorial by its title, thumbnail, description, channel, or transcript alone.**
A transcript will happily tell you the instructor "sets the ControlNet strength" without
revealing that the number was never on screen. **You must look at the frames.**

```bash
# collect transcript + scene-aware frames for the whole candidate list
bash tools/audit-tutorials.sh

# then re-look at a specific moment at maximum fidelity
python3 ~/.agents/skills/watch/scripts/watch.py <url> \
    --detail token-burner --start 12:30 --end 15:00
```

---

## Scoring — 100 points

| Weight | Criterion | What you are looking for **in the frames** |
|---|---|---|
| **20** | **Reproducibility** | Could a stranger follow this exactly? Are all values on screen? |
| **15** | **Production relevance** | Does this look like professional production, or a demo? |
| **15** | **Currentness** | Does the UI match the version you are running **right now**? |
| **15** | **Visual explanation** | Are nodes, menus, sliders and panels actually legible? |
| **10** | **Completeness** | Setup → execution → troubleshooting → final output |
| **10** | **Quality of result** | Is the final output genuinely good, judged honestly? |
| **10** | **Employer relevance** | Does this workflow map to a real job requirement? |
| **5** | **Efficiency** | Signal per minute. Is there an intro, a sponsor, 4 minutes of preamble? |

### Penalties (subtract)

| Penalty | Trigger |
|---|---|
| **−25** | The result depends on unexplained luck ("I generated a few and picked this one") |
| **−20** | Instructor hides prompts, settings, seeds or node values |
| **−20** | Relies on a deprecated model or a UI that no longer exists |
| **−20** | The workflow cannot reasonably be recreated (missing assets, private models) |
| **−15** | Mostly hype — announcement energy, not instruction |
| **−15** | Final output is weak despite the claims made |
| **−15** | Expensive iteration presented as mandatory, with no cheaper alternative offered |
| **−10** | Important failures are hidden — only the winning take is shown |

### Verdicts

| Score | Verdict |
|---|---|
| **≥ 75** | **PRIMARY** — the teaching source for that module |
| 60–74 | **SECONDARY** — watch only if the primary left a gap |
| 45–59 | **REFERENCE** — jump to specific timestamps only |
| **< 45** | **REJECT** — delete the row. Do not watch it "just in case" |

**Hard limit: at most ONE primary and ONE secondary per module.** If three videos survive, you
scored too generously — re-apply the duplication penalty and cut.

---

## The reproduction audit (for PRIMARY candidates only)

Before you commit hours to a primary, answer these. Every "no" is a warning; three "no"s is a
rejection regardless of score.

1. Are all required files and assets actually available?
2. Are prompts visible on screen?
3. Are settings/parameters visible on screen?
4. Are the important node connections visible (not just "and then I connect these")?
5. Does the process match the current official documentation?
6. Does the instructor show any failed attempts?
7. Is the final result plausibly produced by the workflow shown — or does it look like it needed
   hundreds of hidden generations?
8. Are expensive paid assets, plugins or models secretly required?
9. Does it use discontinued models or removed tools?
10. Are downloadable workflow files provided?

Then label your finding:

| Label | Meaning |
|---|---|
| **VERIFIED** | You reproduced the core workflow yourself and got a comparable result |
| **PARTIALLY VERIFIED** | You reproduced part of it; something was missing or differed |
| **UNVERIFIED** | You watched it but did not reproduce it |

**Do not write VERIFIED unless you actually executed it.** This labelling discipline is the
same one applied to this whole course (`research/source_audit.md`), and it is a habit worth
having: it is precisely what separates an engineer from an enthusiast.

---

## Known currentness traps in this specific candidate list

| Module | Trap |
|---|---|
| **After Effects** | **AE 26.2 replaced Roto Brush with Object Matte.** Any roto tutorial predating ~Apr 2026 is stale for the current UI. Watch for matte *judgement*, not the clicks |
| **Higgsfield** | Every discovered tutorial covers Cinema Studio **2.0 / 2.5**; the platform is on **3.0**. Verify the panel layout before trusting any click-path |
| **ComfyUI** | Verify the ControlNet matches the checkpoint architecture. **FLUX checkpoints need FLUX-trained ControlNets** — SD1.5/SDXL ControlNets silently do nothing |
| **Unreal** | Candidates are UE 5.3 / 5.5; current is **5.8**. Cine Camera concepts are stable; Movie Render Queue UI may differ |
| **Blender** | Confirm the version shown. Blender 5.x moved several menu locations vs 4.x |
