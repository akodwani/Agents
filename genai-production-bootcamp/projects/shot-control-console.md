# Project 3 — Shot Control Console
**Total: 8 hours** · 1h each on Days 3, 9, 13, 17 + 4h on Day 21
**This is your Creative Technologist artifact.** It is the thing that makes you legible to
Buyer B (agencies) and Buyer C (product companies), not just Buyer A (studios).

## Why this tool and not a flashier one

The temptation is to build something impressive-looking. Resist it. This tool is valuable
because **you actually use it during the course** — every shot in your final film passes
through it. A tool with 90 real rows of your own production data is dramatically more
persuasive than a beautiful demo with seed data, because you can answer follow-up questions
about it.

It also directly answers the requirement language found in the market research: *"translate
creative intent into structured, efficient, repeatable outputs"* (Wonder Studios) and
*"prototype and refine AI-assisted visual pipelines"* (Publicis).

## The core idea, in one sentence
**A shot is structured data, not a paragraph** — and once it has a schema you can validate it,
diff it, template from it, batch it, version it and reproduce it.

---

## Scope (resist all expansion)

### Must have
1. **Store a shot spec** — the `ShotSpec` Pydantic model from `modules/ai-development.md` §3
2. **Generate structured prompt variants** from a spec (template + LLM, 3 variants)
3. **Export a production manifest** (JSON + CSV) for the whole project
4. **Store reference paths + SHA-256 hashes** — this is what makes "locked references" real
5. **Store generation metadata** — model, params, seed, attempt, credits, QC result
6. **Compare versions** — diff v2 against v3 of a shot and show what changed
7. **Export JSON/CSV**

### Should have
8. **Call one real generation API** (Higgsfield via CLI/Skills, or Comfy Cloud) and record the result

### Explicitly out of scope
Auth, multi-user, deployment, cloud hosting, a media player, thumbnails, drag-and-drop, dark
mode, animations. **If you find yourself styling, stop and go finish a shot.**

---

## Stack

```
backend/    FastAPI + Pydantic + SQLite (sqlite3 stdlib — no ORM needed at this size)
frontend/   Vite + React + TypeScript   ← you already know this; it should cost you ~90 min
llm/        one provider, structured outputs
cli/        console add|list|prompt|manifest|diff   ← build this FIRST
```

**Build the CLI before the UI.** The CLI is what you will actually use during production; the
UI is what you screenshot for the portfolio. Getting that order wrong is how this project eats
15 hours instead of 8.

## Data model

```sql
CREATE TABLE shots (
  id INTEGER PRIMARY KEY,
  shot_id TEXT NOT NULL,
  version INTEGER NOT NULL,
  spec_json TEXT NOT NULL,           -- the full ShotSpec
  created_utc TEXT NOT NULL,
  UNIQUE(shot_id, version)
);
CREATE TABLE refs (
  id INTEGER PRIMARY KEY,
  shot_id TEXT, role TEXT,           -- start_image | end_image | image_ref | video_ref
  path TEXT, sha256 TEXT
);
CREATE TABLE generations (
  id INTEGER PRIMARY KEY,
  shot_id TEXT, version INTEGER, attempt INTEGER,
  model TEXT, params_json TEXT, seed INTEGER,
  output_path TEXT, cost_credits REAL,
  qc_result TEXT,                    -- PASS | CONDITIONAL | FAIL
  qc_failed_criteria TEXT,           -- "C5,M4"
  created_utc TEXT
);
```

Version rows are **append-only**. Never UPDATE a spec — insert `version+1`. That is what makes
`diff` meaningful and what makes the tool a production record rather than a form.

---

## Build schedule

| Day | Hours | Deliverable | Used immediately for |
|---|---|---|---|
| **3** | 1h | `ShotSpec` Pydantic model + SQLite schema + `console add` / `console list` | Storing the 5-second study's spec |
| **9** | 1h | `console prompt` — template-based prompt variants; `console manifest` | Generating micro-scene prompts |
| **13** | 1h | LLM structured-output expansion (one-line → full ShotSpec) + validation | Drafting final-film shot specs |
| **17** | 1h | Generation metadata capture + `console diff v2 v3` + ref hashing | Logging the final film's generations |
| **21** | 4h | FastAPI wrapper + minimal React UI + one live API call + README | The portfolio artifact |

## Exit criteria

| # | Criterion |
|---|---|
| 1 | Contains **real specs for every shot in your final film** — not seed data |
| 2 | `console manifest` exports a manifest that matches what you actually shot |
| 3 | `console diff` shows a real change you made during production |
| 4 | Reference hashes catch a modified reference (test it: alter a ref, re-run) |
| 5 | One live generation API call works end to end |
| 6 | README explains the problem, the schema decision and the limits, in under 400 words |
| 7 | Runs from a clean clone: `pip install -r requirements.txt && python -m console --help` |

## The README is the deliverable

Most people ship the code and no explanation. The README is what a hiring manager reads.
It must answer three questions in this order:

1. **What production problem does this solve?** ("Generated shots were unreproducible; I could
   not tell why shot 4 worked and shot 7 didn't.")
2. **Why is a schema the right answer?** (validation, diffing, templating, batching, versioning)
3. **What are its limits?** ("Single-user, local, no media management. It is a production log,
   not an asset manager.")

Stating limits clearly reads as senior. Overclaiming reads as junior.
