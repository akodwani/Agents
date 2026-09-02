# Module: Light AI Development — the Creative Technologist Half

**Course hours: ~8** · Distributed 1h blocks on Days 3, 9, 13, 17 + 4h on Day 21.

**You start ahead here.** JavaScript, HTML/CSS, Vite, Three.js, browser apps, some Python, and
real experience driving coding agents. That is most of a creative technologist already. What is
missing is the *production* half: talking to generation APIs properly, structuring creative
intent as data, and having an artifact that proves it.

**Explicitly not taught:** Kubernetes, distributed systems, ML training, PyTorch internals,
advanced backend architecture, auth systems, deployment pipelines.

---

## 1. Python — only what the pipeline needs

You know programming. This is a vocabulary transfer, not a language course.

| Topic | The specific thing |
|---|---|
| Functions, typing | Type hints everywhere — they make Pydantic and your agent both work better |
| `pathlib` | `Path` over string concatenation. You will handle thousands of media paths |
| JSON | `json.dump(..., indent=2, sort_keys=True)` so specs diff cleanly in git |
| `httpx` / `requests` | `httpx` — it does sync and async with one API |
| async | Enough to fire N generation jobs and await them together. `asyncio.gather` |
| Env vars | `os.environ` + `.env` via `python-dotenv`. **Never commit a key** |
| `subprocess` | Driving `ffmpeg` from Python. This is most of your media automation |
| Errors + retries | `try/except` with exponential backoff. Generation APIs fail transiently |
| `hashlib` | Hash your reference images. That is how "same inputs" becomes provable |

## 2. The async job pattern — the one API shape that matters

Nearly every generation API follows this. Learn it once, reuse everywhere:

```
POST /generate        → 202 { job_id }
GET  /jobs/{id}       → { status: queued|running|succeeded|failed, result_url? }
   ... poll with backoff ...
GET  result_url       → download bytes
```

Rules that separate a working tool from a broken one:
- **Poll with backoff**, never a tight loop: 2s, 4s, 8s, capped at ~30s.
- **Always set a timeout.** Comfy Cloud will cancel a job at 30 minutes (Standard/Creator);
  your poller must not outlive the job.
- **Persist `job_id` immediately**, before the first poll. If your script dies you can resume.
- **Retry only idempotent operations.** Retrying a generation costs credits — retry the *poll*,
  not the *submit*.
- **Record the full request body** alongside the result. That record *is* your reproducibility.

## 3. Structured data with Pydantic

The insight worth carrying into interviews: **creative intent is structured data.** A shot is
not a paragraph — it is a record with a schema. Once it has a schema you can validate it,
diff it, template from it, batch it and version it.

```python
from pydantic import BaseModel, Field
from typing import Literal

ShotSize = Literal["EWS","WS","MS","MCU","CU","ECU","INSERT"]

class ShotSpec(BaseModel):
    shot_id: str
    scene: str
    size: ShotSize
    lens_mm: int = Field(ge=8, le=300)
    camera_height_m: float
    camera_angle: Literal["eye","low","high","dutch","overhead"]
    move: Literal["static","pan","tilt","dolly_in","dolly_out","track","crane","handheld"]
    subject: str
    action: str
    environment: str
    screen_direction: Literal["L2R","R2L","toward","away","neutral"]
    duration_s: float = Field(ge=1, le=30)
    control_rung: int = Field(ge=0, le=6)   # see modules/higgsfield.md §4
    model: str
    refs: list[str] = []
    start_frame: str | None = None
    end_frame: str | None = None
    seed: int | None = None
    notes: str = ""
```

That model is simultaneously: your shot list, your prompt template input, your API call, your
production manifest and your QC checklist. **One schema, five jobs.** That is the argument you
make when someone asks why you built the Console.

## 4. FastAPI — the minimum

```python
from fastapi import FastAPI
app = FastAPI()

@app.post("/shots")        # create/replace a shot spec
@app.get("/shots")         # list
@app.get("/shots/{id}")    # read, with version history
@app.post("/shots/{id}/prompt")    # generate prompt variants
@app.post("/shots/{id}/generate")  # optional: call a real generation API
@app.get("/manifest")      # export the production manifest
```

Run with `uvicorn app:app --reload`. Free interactive docs at `/docs` — use it as your test UI
before you build any front end. Do not build auth. Do not deploy it. It runs on localhost.

## 5. LLM integration — structured outputs and tool calls

Two patterns, both of which you will demo in an interview:

**Structured output.** Give the model your Pydantic schema and require conforming JSON. Use it
to expand `"hero approaches the door, tense"` into a fully populated `ShotSpec` you then edit.
The model drafts; you direct. Validation is the safety net.

**Tool/function calling + a multi-step workflow.** One real, small chain:

```
read shotlist.csv
  → for each row, draft 3 prompt variants (structured output)
  → validate each against ShotSpec
  → submit the chosen variant to the generation API
  → poll
  → download
  → write the sidecar JSON (spec + params + ref hashes)
  → append a row to the production manifest
```

That is a genuine production automation. It is also exactly what Publicis means by "prototype
and refine AI-assisted visual pipelines".

## 6. Production APIs you will actually touch

| API | Auth | Notes |
|---|---|---|
| **Higgsfield MCP** | OAuth via account, **no API keys** | Shipped 2026-04-30. Best for interactive/agentic work |
| **Higgsfield CLI + Skills** | Account | `npx skills add higgsfield-ai/skills` → `generate`, `soul`, `product-photoshoot`. **Lower token overhead, more consistent output — this is the batch path** |
| **Comfy Cloud API** | Subscription required | `docs.comfy.org/development/cloud/api-reference`. Submit workflow JSON, poll, download |
| `ffmpeg` (not an API but your most-used tool) | — | Frame extraction, encoding, concatenation, contact sheets |

**Security, briefly but seriously:** keys in `.env`, `.env` in `.gitignore`, never in prompts,
never in commits, never in screenshots you put in a portfolio. Rotate anything you leak.

## 7. Exercises

**D1 — ffmpeg fluency (45 min).** `tools/frames.py` ships working (verified: extracts N evenly
spaced frames and builds an hstack contact sheet). **Read it, run it, then extend it**: add a
`--grid` mode that stacks 2 rows instead of one strip, and make it write a `qc.csv` row per clip
recording duration and frame count.
**Exit: you can explain every ffmpeg flag in it, and your extension works. You then use it in
your QC pass from Day 5 onward** — QC starts with looking at first/middle/last.

**D2 — Async job runner (90 min).** Submit 3 generation jobs concurrently, poll with backoff,
download all 3, write sidecar JSONs.
**Exit: it survives one job failing without losing the other two.**

**D3 — Structured expansion (60 min).** Feed a one-line shot description to an LLM with the
`ShotSpec` schema; get back valid JSON; validate with Pydantic; write it to the DB.
**Exit: an invalid model response is caught and reported, not silently written.**

**D4 — The Console (4h, Day 21).** See `projects/shot-control-console.md`.
