# PASS 2 — Audience & pain
**Exit check FAILED as specified. Read §0 before using anything here.**

---

## 0. What I could and couldn't get — read this first

Pass 0 §5 said: if sources are unreachable, say so plainly and don't invent quotes. That's what happened.

**Blocked, verified individually:**

| Source | Result |
|---|---|
| reddit.com (all subs) | Blocked to the crawler by Reddit's own policy — both direct fetch and domain-filtered search |
| apps.apple.com — App Store reviews | `EGRESS_BLOCKED` by the container's network policy |
| itunes.apple.com review RSS | Gateway `403` on CONNECT |
| g2.com | `EGRESS_BLOCKED` |
| news.ycombinator.com | `EGRESS_BLOCKED` |
| facebook.com/ads/library | `EGRESS_BLOCKED` |

The container's egress proxy permits Anthropic APIs and package registries; arbitrary hosts are denied. Web *search* works (it runs server-side), so I have **titles, URLs, and the search backend's summaries of pages — not page bodies I read myself.**

**So the brief's requirement — "25–40 verbatim pain phrases with source URLs, ≥5 quotes per cluster" — I cannot meet. I am not going to write 30 plausible-sounding Reddit quotes and attach URLs to them.** That would be the single worst thing I could put in this submission, and it would be undetectable to Avi, which is exactly why I won't.

**Every line below carries a tier:**
- `[retrieved]` — real source, real URL, surfaced by search; **summary-level, body not read by me**
- `[brief]` — from the LoopNote brief, including tested ad copy **with performance data attached**
- `[assumption]` — my inference. Unverified.

---

## 1. The substitute source, and why it's arguably better

I have something most voice-of-customer research doesn't: **ten pieces of copy that were actually put in front of this exact audience, with thumbstop, CTR, and paid conversion attached to each one.**

A Reddit comment tells me a phrase exists. C01 tells me a phrase **stopped 36% of scrollers and produced paid starts at $81.36.** That is voice-of-customer data with a price tag on it.

Treating the brief's hook copy as the primary corpus `[brief]`:

| Language actually tested | Row | TS | T→P | CPA | Read |
|---|---|---|---|---|---|
| "I used to leave every meeting with 4 tabs open…" | C01 | 36% | 22.1% | $81.36 | **Pain + number + aftermath moment. Winner.** |
| "I imported 120 voice notes and found 18 tasks" | C09 | 41% | 21.9% | $82.09 | **Personal number, backlog framing. Highest TS of any winner.** |
| "Turn a rambling voice memo into a task list" | C05 | 39% | 21.0% | $61.97 | **Two-state, plain verb. Best row in the test.** |
| "Before vs. after meeting notes" | C07 | 38% | **26.8%** | $74.60 | **Pure contrast. Best conversion in the test.** |
| "POV: your boss asks what was decided in the meeting" | C04 | **45%** | 14.0% | $121.43 | **Pain is real — highest TS in the account bar one. Framing is a joke, so it sells nothing.** |
| "Things I stopped doing after using AI" | C10 | **50%** | 11.5% | $190.00 | Topic-of-AI bait. Recruits the wrong person. |
| "AI notes in one tap" | C02 | 25% | 26.3% | $91.43 | Abstract. Lowest CTR in the set (0.9%). |
| "Meet your AI productivity assistant" | C06 | 22% | 14.1% | $333.33 | Dead on every axis. |
| "Why we built LoopNote" | C03 | 18% | 22.2% | $225.00 | Nobody stops; those who do convert 4th-best. |
| "3 ways students use LoopNote" | C08 | 33% | 11.6% | $300.00 | Watched to completion, not paid for. |

**C04 is the most valuable row in this table for Pass 2 purposes.** 45% thumbstop says *"your boss asks what was decided in the meeting"* is one of the two most resonant sentences ever put in front of this audience. It failed at 14% trial→paid because it was staged as a bit. **The pain is validated; the treatment wasted it.** Reclaiming that moment in a non-comedic frame is the highest-confidence move available.

---

## 2. Three pain clusters

### Cluster 1 — The meeting aftermath gap `[brief, strongest evidence in the set]`
The 60 seconds to 10 minutes after a call ends. The decisions are still in your head; nothing is written down; the next call starts.

- C01 and C04 both target this exact moment and post **36% and 45% thumbstop — two of the four highest in the account.** `[brief]`
- C07 (before/after meeting notes) sits on the same moment and returns the **best trial→paid in the test, 26.8%.** `[brief]`
- Three of the four rows aimed at this moment beat or nearly beat target. `[brief]`
- Persona: operator, founder. Moment: post-meeting.
- Published corroboration that action items decay after meetings exists, but it's vendor content marketing recycling unsourced figures ("44% of action items never get completed", "71% of meetings fail their objectives") `[retrieved]`. **I would not put either number in an ad** — I can't trace them to a primary study, and a laundered stat is exactly the kind of claim that reads as fake. See §4.

### Cluster 2 — The voice-memo graveyard `[brief + retrieved]`
You record because your hands are busy — driving, walking, between meetings. You never play it back. The recording was the point and also the end of the process.

- C05 targets exactly this and is **the single best row in the test, $61.97.** C09's "imported 120 voice notes" presupposes a backlog nobody has processed. `[brief]`
- Category corroboration: AudioPen's entire public positioning is converting rambling voice notes into structured text, and its reviews centre on that same job `[retrieved]` — real, and it means the pain is commercially proven **and that the language around it is crowded** (see Pass 3).
- Persona: founder, creator, operator. Moment: commuting, mid-task idea.

### Cluster 3 — Re-deriving a decision you already made `[assumption, partial retrieved]`
Not "I forgot the meeting." Worse: you remember *having decided*, and you have to rebuild the reasoning from scratch. The cost isn't the lost note, it's doing the thinking twice.

- Ebbinghaus's forgetting-curve work is real and shows steep same-day decay of unreinforced material `[retrieved]`, though the exact "70% in 24 hours" figure gets mangled across sources — I'd cite the phenomenon, never the number.
- No row in the brief tests this framing directly. **This is the cluster I'd most want real user language for, and it's the one I'm least able to evidence.** Marked `[assumption]` and used only as a secondary beat, never as a hook.

**Ranked by evidence strength: Cluster 1 ≫ Cluster 2 > Cluster 3.** The scripts weight accordingly.

---

## 3. Moments × personas

| | post-meeting | commuting | mid-task idea | end-of-day |
|---|---|---|---|---|
| **Operator** | **C1 — strongest** | — | C3 | C3 |
| **Founder** | **C1** | **C2** | **C2** | C3 |
| **Creator** | — | C2 | **C2** | — |
| **Student** | C1 | — | — | C3 | 

Student is deliberately empty of emphasis: C08 aimed at students, held attention better than any row in the test (88% hold-through) and converted at 11.6%. `[brief]` Students watch and don't pay. Per Pass 0 default, the scripts go operator + founder.

---

## 4. What this audience doesn't trust about AI notetakers

Four objections surfaced. Their relevance to LoopNote is not equal, and that gap is the strategic find of this pass.

1. **Accuracy / hallucination.** Reported cases include an AI notetaker attributing commitments to a user that they never made, and tools shipping with "review these notes for accuracy" warnings `[retrieved]`. **Directly applies to LoopNote.** If the ad claims clean tasks out of messy speech, the viewer's live question is *"but is it right?"*
2. **Privacy / consent — and this is the interesting one.** The category's live legal exposure is meeting bots recording participants without all-party consent `[retrieved]`. **This barely applies to LoopNote.** LoopNote is a solo voice-notes app — you record yourself. There is no uninvited bot in someone else's call. **The category's biggest trust liability is not LoopNote's, and no ad in the account has ever said so.**
3. **"Another app I'll abandon."** `[assumption]` Not evidenced in what I could retrieve. Treated as real but unproven.
4. **Bot stigma.** Granola's positioning reportedly rests on nobody knowing you're taking notes `[retrieved]` — the category itself treats visible AI note-taking as socially awkward.

**Objection each script must pre-empt: #1, accuracy.** It's the one that actually applies, it's the one the winning formats can answer *structurally* rather than verbally — a real screen recording where the viewer reads the output and judges it themselves is a proof device, not a claim — and answering it verbally would violate P2.

**#2 is not an objection to pre-empt. It's an unclaimed positioning asset.** Flagged for Pass 3.

### On numbers in the scripts
P4 says put a real number where a claim would go. Combined with §2 Cluster 1's unsourceable vendor stats, the rule for Pass 4 onward:

> **Every number in a script must be the speaker's own, produced on screen by the product — never an industry statistic.**

This is what C09 already does ("120 voice notes → 18 tasks", $82.09 at the largest budget in the test) and it needs no citation, can't be laundered, and is visible in frame. `[brief]`

---

## PASS 2 CHECKPOINT

**Produced:** Documented source blockage with per-domain verification; an evidence-tier system applied line by line; the brief's tested copy reframed as the primary corpus, with the C04 finding (validated pain, wasted framing); 3 ranked pain clusters; persona × moment grid; 4-item distrust list with the LoopNote-specific relevance split; a hard rule on numbers.

**Unsure about / falling short:** **The stated exit check is not met.** No verbatim user quotes, no ≥5-quotes-per-cluster. Cluster 3 rests on inference. If Avi can give me web access from an unblocked machine, or paste 20 raw quotes from r/productivity or App Store reviews, Pass 4's hooks get materially sharper — that's the one input that would most improve this submission.

**Need from Avi:** Nothing blocking, but see above — this is a real gap, not a formality.

**Proceeding to Pass 3** (competitive scan — expect the same blockage on the ad libraries).
