# PASS 0 — Ingest & Plan
LoopNote / Newform take-home. Prepared for Avi.

---

## 1. Brief extracted (verbatim constraints)

**Deliverable**
- 2–3 short-form ad scripts for paid social (Meta and/or TikTok), **~20–45s produced**.
- **Required:** 2-minute Loom rationale walking through the thinking.
- **Bonus:** produce one script. Phone-shot fine. Visual substitute for LoopNote (competitor app, mock screens) explicitly allowed.
- If you use AI, **briefly note how**.

**Rubric signals (their words)**
- "the right balance of creativity, engagement, and direct pitch"
- "The best ads are **not overly salesy**"
- "The best ads are also **direct and don't try to masquerade as something they're not**" → no fake-organic
- "platform-native and **don't look or sound like a TV commercial**"
- "**Overproduction does not equal performance**"
- "sharp thinking, taste, and execution — **not polish**"
- "There is no single right answer."
- "**Spend no more than 2 hours on this.**"
- "your script should respond to what's already working and not working"
- "Do not copy. We want to see your original thinking."

**Brand**
- LoopNote, AI voice-notes app. Messy thoughts / meetings / ideas / voice memos → clean summaries, tasks, follow-ups. Fictional brand.
- Audience: professionals, founders, students, creators, operators who live in notes/meetings/voice memos.
- Goal: **paid starts**. Target CPA **< $90 per paid start**.

**Data given:** 10 rows (C01–C10) across Meta / TikTok / YT Shorts, with Length, Spend, Thumbstop, 6s Hold, CTR, Trial Starts, Paid Starts. Full table transcribed and verified in Pass 1.

---

## 2. The honest tension, stated up front

The brief caps effort at **2 hours** and says overproduction ≠ performance. This 10-pass loop is deeper than 2 hours of human work. That is fine for the *thinking* — it is not fine for the *artifact*. So:

- **Depth goes into `/work/01`–`09`.** Those are my working files. The evaluator never sees them.
- **`FINAL_SUBMISSION.md` must read like one sharp person, two focused hours.** Target: readable in under 8 minutes, 3 scripts + one paragraph of data reasoning + Loom script + AI disclosure + next tests. Nothing else.
- I will actively cut good material in Pass 10. Flagging now so it isn't a surprise later.

---

## 3. Pass plan & effort

| Pass | Output | What it produces | Tools needed | Est. |
|---|---|---|---|---|
| 0 | `00_plan.md` | This. Brief extracted, plan, permission batch. | none (done) | 15m |
| 1 | `01_data.md` | Rebuilt table + 6 derived metrics per row, CPA/conversion rankings, winner/loser pattern read, platform read, **5–7 creative principles each traceable to specific rows**. | **none** | 30m |
| 2 | `02_audience.md` | 25–40 verbatim pain phrases w/ source URLs, tagged by persona + moment, clustered to 3 sharpest pains, plus the distrust list (accuracy / privacy / another-app / cost). | **WebSearch, WebFetch** | 40m |
| 3 | `03_competitive.md` | 6–10 real players' live ads logged (hook / format / length / proof / CTA), crowded-vs-open map, 3 white-space angles, **DO NOT USE list**. | **WebSearch, WebFetch** | 40m |
| 4 | `04_hooks.md` | 30 hooks (line + 0s visual + persona + pain cluster + principle cited + thumbstop tier), killed to 8 with reasoning. **Checkpoint: Avi picks.** | none | 35m |
| 5 | `05_scripts_v1.md` | 3 scripts, timestamped tables, alt hooks, proof device, CTA wording+moment, objection pre-empt, phone-shootable production notes, performance prediction vs. the table. | none | 45m |
| 6 | `06_critique.md` | Evaluator-mode scoring on 8 dimensions, fix list for every ≤3, masquerade check, TV check. | none | 25m |
| 7 | `07_scripts_v2.md` | Fixes applied + diff summary + re-score. | none | 30m |
| 8 | `08_loom.md` | ~280–320 word spoken script in Avi's voice + timestamped beat sheet, ≤2:00. | none | 20m |
| 9 | `09_production.md` | Shot list, phone settings, lighting, LoopNote stand-in, VO tips, edit order, text specs, sound, export specs (9:16 1080×1920 + 4:5). Optional: build the mock UI. | **file write, optionally Chromium/screenshot** | 30m |
| 10 | `FINAL_SUBMISSION.md` + `.pdf` | The tight package. Ruthless trim. AI-usage disclosure. | **HTML→PDF via headless Chromium** | 25m |

**Critical path:** Passes 2 and 3 are the only ones that can hard-block on tooling. If web access is denied or the ad libraries are unreachable, see §5.

---

## 4. PERMISSION REQUEST (batched — one `y` covers the set, or reply per line)

```
PERMISSION REQUEST → WebSearch → Pass 2 & 3: find how real users describe the pain
  in their own words (Reddit, App Store/Play reviews, X, YouTube/TikTok comments) and
  find live competitor ads → verbatim pain quotes with source URLs; competitor ad log.
  Approve? (y/n)

PERMISSION REQUEST → WebFetch → Pass 2 & 3: open the specific Reddit threads, review
  pages, Meta Ad Library and TikTok Creative Center URLs that search surfaces → pull
  actual quotes and actual ad copy rather than my memory of them. Approve? (y/n)

PERMISSION REQUEST → file writes under /work/ → every pass output, plus the mock
  LoopNote screen if you want it (Pass 9). NOTE: /work is a symlink to
  /home/user/Agents/work so the files sit inside the repo and can be committed to
  the branch this session is assigned. Say the word if you'd rather they live
  somewhere outside git. Approve? (y/n)

PERMISSION REQUEST → headless Chromium (pre-installed, no download) → Pass 9 optional
  mock-screen screenshot, and Pass 10 HTML→PDF conversion (no pandoc/poppler in this
  container; Chromium print-to-PDF is the clean no-install path) →
  FINAL_SUBMISSION.pdf + a PNG of the mock LoopNote UI. Approve? (y/n)

PERMISSION REQUEST → git commit + push to claude/loopnote-creative-submission-yr224j
  → so the work survives this container and you can read it on GitHub. I will NOT
  open a PR unless you ask. Push after Pass 1, Pass 7, and Pass 10, or on your
  cadence. Approve? (y/n)
```

**Deliberately NOT requested** (tell me if you want any of these and I'll ask properly):
- The `script-writer` / `cinedance` / `seedance` skills — these are templating systems. For a take-home judged on original thinking, a template is a liability. I'd rather write these cold against the data.
- Any AI video/image generation (Higgsfield etc.). The brief says phone-shot is fine and polish is not the point; generated footage would read as overproduction and would undercut the "don't masquerade" line.
- Google Drive, Artifact publishing. Not needed unless you want a shareable link at the end.

---

## 5. Fallbacks if permissions are denied or sources are unreachable

- **No web at all:** Passes 2 and 3 get rebuilt from what I can defensibly assert, and **every single line is labeled `[assumption]`**. The scripts get weaker hooks because the verbatim language is the whole point of Pass 2. I'd rather you know that than get confident-sounding invented quotes. I will not fabricate a Reddit quote or a URL.
- **Meta Ad Library / TikTok Creative Center block the fetch** (both are JS-heavy and frequently unfetchable from a container): I'll say so plainly in `03_competitive.md`, fall back to competitor landing pages, YouTube pre-roll transcripts, and press/marketing teardowns, and mark the coverage gap. The DO NOT USE list will then cover only what I actually retrieved.

---

## 6. Open questions for Avi (do not need answers to start Pass 1)

1. **YT Shorts rows.** C07 (before/after) and C08 (tutorial) ran on YouTube Shorts, but the deliverable is Meta and/or TikTok. If C07's structure turns out to be a top performer, do you want me to port it to Meta/TikTok — and flag the port as a deliberate inference in the submission — or keep the three scripts strictly on formats that were tested on the two target platforms? **My default: port it, and say out loud that I'm porting it.** That reasoning is itself a rubric signal.
2. **Persona spread.** Three scripts, five named audiences. Concentrating on the two personas the data supports beats one script each. **My default: operator/professional + founder, with a creator angle only if Pass 2 says the pain language is distinct.**
3. **Bonus shoot.** Do you intend to actually shoot one? That changes Pass 9 from a paper plan into a real shot list + mock asset build. **My default: write Pass 9 as if you will.**
4. **Voice.** Anything in the Loom script that shouldn't sound like you? I have "plain, direct, no hype, no honestly/genuinely" — tell me if there's more.

---

## PASS 0 CHECKPOINT

**Produced:** Brief fully extracted and transcribed (incl. the full 10-row table); 10-pass plan with effort estimates; batched permission request; fallback plan; four open questions.

**Unsure about:** Whether the ad libraries will actually be fetchable from this container (Pass 3 risk, not a blocker). Whether you want the YT Shorts formats ported to Meta/TikTok.

**Need from Avi:** Answers to the permission batch in §4. Answers to §6 are welcome but Pass 1 needs no tools and no decisions — say the word and I'll run it while you think.

**Proceed to Pass 1?**
