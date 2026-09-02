# Module: Premiere Pro — Edit, Sound and Master

**Course hours: ~9** · Days 4, 5, 20
**Market weight: 18 hard requirements.** Current build referenced: **26.x** (Object Masking,
Generative Extend for video *and* audio in 26.3, upgraded Media Intelligence, AI proxies).

**Goal: cut a professional 30–60 second cinematic piece and master it correctly.**
Everything that does not serve that is out.

---

## 1. Project hygiene (do this once, benefit for 21 days)

```
project/
  00_PROJECT.prproj
  bins/  01_FOOTAGE  02_COMPS  03_AUDIO  04_MUSIC  05_SEQUENCES  06_EXPORTS
```

- **Frame rate: 24 fps.** Decide once, at the start, and never mix. Mixed frame rates are the
  most common cause of stuttering AI edits — generators output 24/25/30 and Premiere will
  silently conform them badly.
- Sequence: 1920×1080 or 3840×2160, 24 fps, square pixels.
- **Proxies**: on a 1660 SUPER, generate proxies for anything above 1080p. Premiere 26 has AI
  proxies specifically for weaker hardware. Use them — do not fight playback.
- Label colours by shot state: red = needs regeneration, yellow = needs comp, green = final.
  Your timeline then shows your remaining work at a glance.

---

## 2. Editing skills required

**Source/record workflow.** Set in/out in the Source monitor before you touch the timeline.
Dragging whole clips from the bin is the slow habit that never gets unlearned.

**Trim tools and what each is for:**
| Tool | Effect on duration | Use when |
|---|---|---|
| Ripple | Changes overall duration | Tightening pace |
| Roll | Preserves duration, moves the cut point | Finding the exact frame between two shots |
| Slip | Preserves position and duration, changes clip content | The action is right but the framing timing is off |
| Slide | Moves the clip, keeps its content | Repositioning a beat |

**J-cuts and L-cuts.** The single technique that will most improve your edit. Audio leads the
picture (J) or lags it (L). This is what makes six generated clips feel like one continuous
scene rather than a slideshow. **In your final film, at least three cuts must be J or L.**

**Pacing.** Shot length is your rhythm instrument. Escalation = progressively shorter shots.
Payoff = one shot held noticeably longer than the audience expects. Cutting on action hides
generation inconsistencies; cutting on stillness exposes them.

**Nested sequences** for a section you want to treat as one block. **Speed changes** —
time remapping with eased ramps; generated footage often benefits from a subtle 90–95% slowdown
which reduces perceived motion artifacts.

**Generative Extend (26.x)** — when a generated shot is a few frames short of the cut you want.
Genuinely useful here; note it in your production log when used.

---

## 3. Sound — 30% of perceived quality, 10% of your time

You have no dialogue. That is a simplification, not an excuse. Silent AI video reads as a tech
demo; the same picture with designed sound reads as a film.

**Track layout:**
```
A1  Ambience / room tone   (continuous — this is the glue)
A2  Hard effects           (impacts, footsteps, mechanical, whoosh)
A3  Design / texture       (drones, risers, sub hits)
A4  Music
```

- **Ambience is the single highest-value element.** A continuous bed under every shot makes the
  cuts stop feeling like cuts. Lay it first, across the whole piece, before any effect.
- **Sub-bass on the payoff.** One low hit at the reveal does more than any visual effect.
- **Cut sound slightly before picture** on impacts (1–2 frames). Perceptually it lands together.
- Mixing targets: dialogue-free piece, aim for around **-14 LUFS integrated** for web, with
  **true peak below -1 dBTP**. Music sits ~6–10 dB under hard effects at the climax.
- Sources: freesound.org (check licences), Adobe Stock audio if you have CC, or generate
  ambience/SFX with `generate_audio` on Higgsfield.

**Media Intelligence (26.x)** lets you search audio by description — genuinely faster than
scrubbing a library.

---

## 4. Colour — Lumetri, practically

You are not grading a feature. You are making six generated shots look like they came from one
camera on one day.

1. **Match first, grade second.** Put your best shot on the timeline as the reference. Use the
   **Comparison view** and match every other shot to it: black point, white point, then hue.
2. Scopes: **use the Waveform** (exposure — keep blacks off 0 and whites off 100 unless
   intentional) and the **Vectorscope** (hue consistency, and to check skin/subject tone lines up
   between shots).
3. Then one adjustment layer over the whole timeline for the look.
4. Generated footage is often over-contrasted and over-saturated by default. Pulling it *back*
   frequently reads as more cinematic than pushing it further.

---

## 5. Export
| Deliverable | Setting |
|---|---|
| Portfolio master | H.264, 1080p or 2160p 24fps, VBR 2-pass, target 20–40 Mbps, AAC 320 kbps |
| Archive master | ProRes 422 HQ / DNxHR HQX |
| Reel cut (20–30s) | Same as master; 16:9 |
| Social vertical (optional) | 9:16, reframed — **do not** simply crop; re-frame per shot |

Always export with **Use Maximum Render Quality** off unless you scaled footage, and **Render at
Maximum Depth** on when you have gradients (it reduces banding in dark cinematic images —
a very common failure in this exact kind of piece).

---

## 6. Exercise (required by the brief)

**P1 — Three pacing styles (2.5h).** Take one 15–20 second generated sequence and cut it three
ways from the same footage:
1. **Tense** — long holds, few cuts, sound-led, one very late payoff cut
2. **Kinetic** — short shots, cuts on action, escalating rhythm
3. **Classical** — establishing → coverage → resolution, even rhythm, J/L cuts throughout

**Exit criteria:** all three are the *same length*; a viewer can tell them apart without being
told what you did; and you can name, per version, which cut is doing the work.

This exercise teaches the thing no tutorial teaches: that pacing is a choice you make, not a
property of the footage.
