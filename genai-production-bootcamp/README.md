# GenAI Filmmaker + Creative Technologist — 21-Day Production Bootcamp

A reproducible 105-hour curriculum that takes you from *"I generate AI video"* to
*"I direct, control, finish and explain production-grade GenAI sequences"* — and leaves you with
a portfolio built for the roles that are actually hiring.

**Built 2026-09-02.** Research method, evidence levels and one significant limitation are
documented in **[`research/source_audit.md`](research/source_audit.md)** — read it first.

---

## ⚠️ START HERE: one thing could not be done for you

The environment that built this course **could not reach YouTube.** The egress proxy returned
HTTP 403 to CONNECT on `youtube.com`, and its own documentation says not to route around a
policy denial. So:

- ✅ The `watch` skill **is installed and validated** — `npx skills add bradautomates/claude-video -g`,
  yt-dlp 2026.08.19, ffmpeg 6.1.1, preflight exit 0, `watch.py --help` confirmed.
- ❌ **No tutorial could be downloaded, watched, or scored.** Every video in
  `resources/youtube_playlist.md` is an **UNVERIFIED candidate**, not a recommendation.
- ✅ **`tools/audit-tutorials.sh` does the audit for you, on your machine.** ~60–90 min. That is
  **Day 0**. The harness itself was tested end to end (queue building, ID parsing, skip logic,
  graceful failure) — only the network step is blocked here.

**The curriculum does not depend on the videos.** Every module's authoritative source is official
documentation, which *was* reachable and *was* verified. Video is supplementary craft
demonstration. If a candidate fails your audit, delete it — the day still works.

What *was* verified directly: the **live Higgsfield MCP catalog** (queried through the API, not
read off a marketing page), plus current documentation for ComfyUI/Comfy Cloud, Blender, Unreal
5.8, After Effects 26.2 and Premiere 26.x.

---

## Day 0 — Setup (1.5h, do this before Day 1)

```bash
# 1. Dependencies
pip install --user yt-dlp
brew install ffmpeg        # macOS
sudo apt install ffmpeg    # Linux

# 2. The watch skill
npx skills add bradautomates/claude-video -g
python3 ~/.agents/skills/watch/scripts/setup.py --json     # expect missing_binaries: []

# 3. Audit the tutorial candidates  ← the part that could not be done for you
bash tools/audit-tutorials.sh
#    then LOOK AT THE FRAMES and score each against rubrics/tutorial_qc.md,
#    writing results back into research/video_evaluations.csv

# 4. Accounts
#    - Higgsfield (you have this) + MCP or CLI/Skills wired to your agent
#    - Comfy Cloud: free tier is enough for Days 8-9 learning.
#      ⚠️ The Cloud API needs a PAID subscription ($20/mo) — start it now if you want
#         Day 21's Console to make a live call.
#    - Adobe CC (Premiere + AE + Photoshop)
#    - Blender 5.x, Unreal 5.8 (optional — Day 14 is cuttable)
```

---

## The first file to open

👉 **[`course/00-course-map.md`](course/00-course-map.md)** — hour budget, phase structure,
dependency graph and the red-team pass.
Then **[`course/01-day-01.md`](course/01-day-01.md)**.

## What you will have on Day 21

| # | Artifact |
|---|---|
| **A** | A 30–60 second coherent cinematic GenAI sequence |
| **B** | A 20–30 second reel cut |
| **C** | A full production breakdown — **including the failures** |
| **D** | The Shot Control Console (FastAPI + SQLite + CLI, with real production data) |
| **E** | Two reproducible ComfyUI workflows (JSON + READMEs + strength sweep) |
| **F** | A Blender previs rig as a committed, rerunnable `.py` |
| **+** | Readiness matrix, rehearsed interview answers, one index page |

## Repository map

| Path | What it is |
|---|---|
| `course/` | The 21 daily lessons + course map + **14-day compressed version** |
| `modules/` | Deep reference per tool. The days link here |
| `projects/` | The three build briefs + the Console spec |
| `rubrics/` | Shot QC · Film QC · Tutorial QC — **the gates** |
| `recruiting/` | Readiness matrix, case-study template, reel plan, interview questions, gap analysis |
| `research/` | Market data, tool decisions, video candidates, **and the source audit** |
| `resources/` | Primary sources, playlist, troubleshooting, parking lot |
| `tools/` | `audit-tutorials.sh` · `frames.py` (QC contact sheets) · `blender/previs_rig.py` · `unreal/previs_sequencer.py` |

## The thesis, in one paragraph

Most people use generative video as a slot machine: prompt, roll, keep the good one. Every
serious job description in the market research asks for the opposite — Wonder Studios wants
*"structured, efficient, repeatable outputs"*; Publicis wants *"clean, scalable node-based
generation workflows."* This course is built around one idea, the **control ladder**: each rung
(start frame → end frame → image references → video references → motion transfer → locked
identity) removes a category of randomness from your output. Rung 0 is prompting. Rung 5 is a
Blender camera move transferred onto a locked reference between two frames you authored. The
difference between those two is the difference between a hobbyist and a hire.

## Honest scope

**This gets you to the junior / emerging-professional threshold, not to mastery.** In 105 hours
you will be READY for AI Video Artist, Generative Production Artist, AI Filmmaker, Motion+AI, and
agency AI Creative Technologist roles; STRETCH for Creative Technologist and AI/VFX; and NOT
READY for traditional VFX houses (Nuke), pipeline TD, or games technical art. Those verdicts are
evidenced in `recruiting/readiness_matrix.md`, and the exclusions are defended in
`research/tool_decisions.md` — being able to explain what you *didn't* learn, and why, is itself
an interview skill.

## Labelling convention used throughout

**DEMONSTRATED** (executed here) · **DOCUMENTED** (vendor's own docs) · **INFERRED** (my
reasoning) · **EXPERIMENTAL** (vendor says so) · **COMMUNITY/UNSTABLE** · **UNVERIFIED**
(discovered, not inspected). Nothing unstable sits on the critical path, and everything that
could not be verified says so.
