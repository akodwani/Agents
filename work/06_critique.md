# PASS 6 — Adversarial critique

Role: Newform evaluator. I've read 200 of these. Most of them have a data section that doesn't touch the scripts, and three scripts that are the same script.

Scored 1–5 on eight dimensions. Every ≤3 gets a specific fix.

---

## Scores

| Dimension | A "31 uhhs" | B "63 memos" | C "40 seconds" |
|---|---|---|---|
| Hook strength | 5 | 4 | 5 |
| Platform-nativeness (TV = fail) | 5 | **3** | 5 |
| Direct without salesy | 4 | 4 | 4 |
| Proof credibility | 5 | 5 | 5 |
| Data-responsiveness | 5 | 5 | **4** |
| Originality vs. Pass 3 | 4 | 4 | 4 |
| Producible on a phone in an hour | 5 | **3** | **3** |
| Conversion logic (paid, not just trial) | 4 | 4 | 4 |

Nothing is broken. Three things are wrong, one of them across all three scripts.

---

## The cross-cutting problem: the disclosure device is a tic

All three end on the same move — *"Paid ad. Real memo." / "paid ad — the sixty-three is real" / "Paid ad, real hallway."* Once, that's a sharp read of the brief's anti-masquerade line. Three times in a submission of three scripts, it stops being a thought and becomes a formula, and the evaluator's read is *"this person had one idea."*

Worse, on its own terms: it spends 2–3 seconds of a 20-second ad on **meta-commentary about the ad instead of the product.** On Script C that's 15% of the runtime. There is no evidence in the account that disclosure improves CPA. It's a differentiator for a *reader of the submission* — which is a different job from performing in-feed, and confusing the two is exactly the error the brief is testing for.

**FIX (all three):**
- **Script A keeps it in full.** "LoopNote made this ad. The memo's mine." earns its seconds there because it directly reinforces the proof device — it tells you which part is sponsored and which part is evidence.
- **Script B and C cut the spoken version.** Keep a persistent `Paid partnership · LoopNote` label from 0:00 — which is what platform-native disclosure actually looks like on Meta and TikTok, and costs zero runtime. Buys back 2s on B and 2s on C.

---

## Script B — three fixes

**B / platform-nativeness = 3.** This is a TV spot. Setup, escalation, an emotional turn at 0:24, a button. 31 seconds with a face, a reveal, and a resolution is a structure that would run before a YouTube video in 2014.

And the specific offender is **the line I like most in the whole submission:**

> *"I wasn't behind on work. I was behind on people."*

Apply the Quality Bar — *"If a sentence could appear in a competitor's ad unchanged, cut it."* It could. Otter could run it. Fireflies could run it. It's a copywriter's line, and it's doing what P2 forbids: it *tells you the meaning* of what the screen already showed. The screen showed two overdue promises with people's names on them. The viewer got there. Saying it out loud is the writer taking a bow.

**FIX:** cut it. Hold the two overdue items on screen for the two seconds the line was using. Silence lands harder than the line does, and it obeys P2 instead of violating it.

**B / producibility = 3.** The entire script depends on Avi's phone containing a large unplayed voice-memo backlog. If it holds eight memos, the ad is unshootable as written — and swapping in a fake 63 would break the one rule this submission has held all the way through.

**FIX:** the number is a variable, not a line. Shoot whatever the real count is and cut the VO to match. Pass 9 carries a pre-shoot check: open Voice Memos, count, write the number into the script. If the real number is small, **the script still works and arguably works better** — "eleven memos, and four of them had something in them I'd forgotten" is more credible than 63 and just as specific.

**B / length.** 31s with the payoff at 0:24. Cutting the turn line (−2s) and the spoken disclosure (−2s) and tightening the import beat from 4s to 2s brings it to **~25s with the payoff at 0:17.**

---

## Script C — two fixes

**C / data-responsiveness = 4.** P4 says put a real number where a claim would go. "Four things" is a count, not a number that could only belong to this person. C09 got 41% thumbstop on *"120 voice notes, 18 tasks"* — the specificity is the mechanism, and C's hook doesn't have it.

**FIX:** make the countdown the number. *"That call ended forty seconds ago"* → the phone's own clock is visible in frame, and the recording timestamp at 0:06 matches. The number becomes verifiable on screen rather than asserted, which is a stronger version of P4 than a bigger digit would be.

**C / producibility = 3.** The mock task screen has to match the four things said aloud at 0:06. If the take changes — and on a one-take corridor walk it will — the mock has to be rebuilt.

**FIX:** invert the order. **Build the mock first, with four fixed tasks. Then perform to it.** The line at 0:06 is improvised *around* four known items. Removes the dependency, and the improvisation gets better because the destination is known.

**C / secondary risk (not scored down, but flagged).** 0:06–0:12 is six seconds of someone talking at their phone — 30% of the runtime. That's structurally adjacent to C03's failure mode (founder talking head, 18% thumbstop, $225). It's mid-ad rather than at the hook so thumbstop is unaffected, but **hold** is exposed. **Mitigation:** keep walking during the record — motion under the dialogue — and cut to the screen at 0:11 rather than 0:12. If the produced version shows a drop-off cliff at 6s, that's the cause.

---

## Masquerade check

**All three pass, but only after the fix above changes how.** v1 passed by *saying* it was an ad. v2 passes by carrying a platform-native paid-partnership label from frame one on B and C, and by A's explicit line. Neither uses a fake-organic convention — no "storytime", no faked discovery, no pretending a sponsored post is a personal one.

**One integrity note that has to reach the submission:** all three show a **mock** LoopNote UI while claiming the memo, the number, and the hallway are real. That's true as written — the claim is scoped to the input, not the interface — but a viewer would reasonably infer the interface is the real product too. For a fictional brand in an evaluation exercise this is fine and the brief explicitly permits mock screens. **It goes in the AI-usage / production disclosure in Pass 10 regardless.** An ad whose whole argument is "judge the evidence yourself" cannot be quiet about which part is a prop.

---

## TV check

Read as a 30-second spot:

- **A** — fails as TV, which is the pass condition. It's a screen recording with a voice over it; there's no shot, no talent, no button. Doesn't work on a television. Correct.
- **B (v1)** — **works as a TV spot. That's the fail.** Arc, face, emotional turn, resolution. After the fixes — no turn line, silence where the meaning was, 25s — it stops resolving and starts just ending, which is what in-feed does.
- **C** — fails as TV. A handheld corridor walk with breath in the mic and an improvised sentence would read as an error on television. Correct.

---

## Conversion logic — the dimension I under-argued

All three scored 4, and the reason none scored 5 is that Pass 5 never states *why* these produce **paid** starts rather than just cheap trials. The data answers it and I left it implicit:

> **The ad is the expectation contract.** C04 promised entertainment and delivered software — 14.0% trial→paid. C05 promised exactly what the app does and delivered it — 21.0%. C07 promised a specific transformation and delivered it — 26.8%, best in the test. Trial→paid isn't a landing-page metric. **It's set by how accurately the ad described the product before the click.**

That reframes the whole submission: showing the transformation isn't just a better hook, it's the mechanism that makes the trial convert, because nobody arrives expecting something else. It's the strongest thing in the data and it should be the first thing out of Avi's mouth in the Loom.

**FIX:** surface it as **P8** in the final package, and lead the Loom with it.

---

## Fix list

| # | Script | Fix | Cost |
|---|---|---|---|
| 1 | A, B, C | Spoken disclosure stays on A only; B and C use a persistent paid-partnership label | −2s on B and C |
| 2 | B | Cut "I wasn't behind on work. I was behind on people." Hold the overdue items in silence. | −2s, +P2 compliance |
| 3 | B | Number becomes a shoot-day variable; pre-shoot count in Pass 9 | 0 |
| 4 | B | Tighten import beat 4s → 2s. Target 25s, payoff at 0:17. | −4s total |
| 5 | C | Visible clock/timestamp so "forty seconds" is verifiable on screen | 0 |
| 6 | C | Build mock first with four fixed tasks; improvise to it | 0, removes dependency |
| 7 | C | Keep walking under the 0:06 dialogue; cut to screen at 0:11 | −1s, protects hold |
| 8 | all | Add **P8 — the ad is the expectation contract**; lead the Loom with it | 0 |

---

## PASS 6 CHECKPOINT

**Produced:** 8-dimension scoring; four scores at ≤4 with specific fixes; identification of the disclosure device as a formula rather than an idea; masquerade check with the mock-UI integrity note; TV check that Script B v1 fails; the P8 finding.

**Unsure about:** whether cutting the "behind on people" line is right. It's the best line I wrote and it's a P2 violation. I'm cutting it because the constitution says so, and a constitution that bends for a good line isn't one — but Avi can overrule.

**Proceeding to Pass 7.**
