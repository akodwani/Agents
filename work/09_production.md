# PASS 9 — Production plan (the bonus)

**Shooting Script A, "Thirty-one uhhs."** No talent, no location, no lighting — a screen recording and a phone mic in a parked car. Highest predicted performance of the three (CPA at or under C05's $61.97) and the only one shootable alone in under an hour. Script C is the better second if you want a person on camera.

---

## 0. Script amendment from the build

Building the mock changed the script. The transcript naturally produces **four** tasks, and the fourth is the one the speaker audibly loses and recovers — *"there was a fourth thing… it's gone… oh — the contractor invoices."*

That's better than the scripted three, because the forgetting happens **on the recording** instead of being claimed afterward.

> **0:12–0:18 VO changes from:** "Three tasks. Two with names on them. One I'd completely forgotten about."
> **to:** "Four tasks. Two with names on them. One I'd completely forgotten I said."

One word longer. Runtime unchanged at ~24s.

---

## 1. Assets built and ready

| File | What it is |
|---|---|
| `assets/screen1.html` / `.png` | Transcript screen. Search field on `uhh`, **31 matches**, highlights down the page. 1170×2532 (3×). |
| `assets/screen2.html` / `.png` | Task screen. Four tasks, two with names, two overdue, each with the source quote it came from. |
| `assets/transcript.txt` | 265-word monologue. **The 31 count is programmatically verified**, not eyeballed — `assert` in the generator. |

**On the number.** Script A's rule was that the count must be real. It is — the transcript is a real 265 words and the mock genuinely contains 31 matches. If you re-cut the transcript, re-run the generator; the assert fails rather than letting a wrong number ship.

**Editing the mock:** both screens are single HTML files, no dependencies. Change text, re-render:
```
CH=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
$CH --headless --disable-gpu --no-sandbox --hide-scrollbars \
    --force-device-scale-factor=3 --window-size=390,844 \
    --screenshot=screen1.png file://$PWD/screen1.html
```

---

## 2. Shot list

| # | Shot | Framing | Dur | Notes |
|---|---|---|---|---|
| 1 | Screen recording — transcript, thumb scrolling | Full-frame phone screen | 10s | The whole first half. One take, no cuts. |
| 2 | Screen recording — tap → processing → task list resolves | Full-frame | 8s | Hold on the tasks. **Do not cut early — reading time is the proof.** |
| 3 | Split composite — transcript line ↔ the task it produced | Built in the edit | 3s | Priya line is the clearest pairing. |
| 4 | End card — LoopNote mark | Static | 3s | Built from `screen2.html`'s wordmark. |

Total 24s. **Shots 1 and 2 are the film.** 3 and 4 are assembled in the edit.

### Getting the screen recording without a real app
The mock is two static screens, so the "tap" is a cut, not an interaction. Two ways:

- **Simplest:** open each PNG full-screen in Photos on your phone, screen-record while scrolling screen 1, then swiping to screen 2. The swipe reads as a transition. **Works, do this.**
- **Better if you have 10 extra minutes:** open the HTML files in mobile Safari and record that. Real scroll physics, real rubber-banding — reads as a live app rather than a photo. Worth it, because the whole ad's argument is that this is real.

---

## 3. Phone settings

- **1080p / 30fps** — not 4K, not 60. Upload gets recompressed anyway and 30fps reads more native in-feed.
- **Screen recording:** enable mic in the Control Centre long-press so VO and screen are captured together if you want a live read. Cleaner to record VO separately (§4).
- **Lock brightness** at ~70% and turn off True Tone/auto-brightness — a brightness shift mid-recording looks like a glitch.
- **Do Not Disturb on.** A notification banner mid-take kills the take.
- **9:16 native.** Do not shoot 16:9 and crop.

## 4. VO

- Record in the car, engine off, windows up — **this is the best-sounding small room you own.** Upholstery kills reflection.
- Phone mic, held ~20cm, slightly off-axis so plosives miss it.
- **Read it like you're annoyed at yourself, not like you're selling.** The first line is a confession.
- Do 3 takes of the whole thing, pick one. Don't assemble line by line — the pacing goes plastic.
- Leave the real breath in. `Room tone only` in the script means exactly that: don't noise-gate it to silence.

## 5. Lighting

None. It's a screen recording. Shoot the phone screen at native brightness in a dim car and it exposes itself.

## 6. Edit order

1. Lay the VO down first. It's the spine.
2. Drop shot 1 under lines 1–3. Match the scroll to the pace of the read.
3. Cut to shot 2 on the tap. **Two beats of silence** before "Four tasks…" — the silence at 0:10–0:12 is scripted and it matters.
4. Split composite at 0:18.
5. End card 0:21.
6. Music in at 0:10, out on the last word. Not before — the first ten seconds are dry on purpose.

## 7. On-screen text

- Only one text element in the whole ad: **`Paid ad. Real memo.`** at 0:21.
- System sans, semibold, ~44px at 1080 wide, white, bottom third, above the safe area.
- **Everything else legible on screen is diegetic** — the match counter, the task titles, the date chips. That's the point: it's the product's own UI doing the talking, not a caption layer.
- Keep all text inside the middle 80% vertically — TikTok's UI eats the bottom ~15% and the top ~10%.

## 8. Sound

- No trending audio. A trend track is what C10 did (50% thumbstop, $190 CPA) and it recruits the wrong viewer — P1.
- One low, unobtrusive bed from 0:10. Something with no melody to speak of. It should be almost unnoticeable.
- **The single UI tick on the tap is the most important sound in the ad.** It's the moment the transformation starts.
- Mix VO well above the bed. If you can't hear every word on phone speakers at 50%, it's wrong.
- **Caption it.** Burned-in or platform auto-captions — most of this plays muted.

## 9. Exports

| Placement | Spec |
|---|---|
| TikTok in-feed | 9:16, 1080×1920, H.264, ~10 Mbps, AAC 128kbps |
| Meta Reels / Stories | 9:16, 1080×1920 — same master |
| Meta feed | 4:5, 1080×1350 — **re-frame, don't letterbox.** The phone screen is centred so it crops cleanly |
| Safe areas | TikTok: keep content out of bottom 15% / top 10%. Meta 4:5: bottom 20% for the CTA bar |

Export one 9:16 master, then re-frame to 4:5. Two files.

## 10. Pre-shoot checklist

- [ ] Transcript re-read — does it sound like you? Rewrite the words, then re-run the generator so the count stays true
- [ ] `assert` passed on the uhh count
- [ ] Both PNGs re-rendered after any text change
- [ ] Phone: DND on, brightness locked, 1080/30
- [ ] Car, engine off
- [ ] 3 VO takes
- [ ] Screen recording of scroll + swipe
- [ ] Check the read: **is anything in the ad a claim rather than something on screen?** If yes, cut it (P2)

---

## PASS 9 CHECKPOINT

**Produced:** Script A amended from what the build revealed; mock UI **built and rendered**, not described — two HTML screens plus 3× PNGs, with the hook's number machine-verified; shot list, phone settings, VO/lighting/edit/text/sound direction, export specs, pre-shoot checklist.

**Unsure about:** the mock is two static screens, so the tap is a cut rather than a real interaction. Recording the HTML in mobile Safari instead of the PNGs in Photos closes most of that gap and I've flagged it as the better path.

**Exit check:** Avi could shoot this tomorrow. The only decision left is whether to re-write the transcript in his own words first — recommended, and the generator protects the number when he does.

**Proceeding to Pass 10.**
