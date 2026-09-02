# Troubleshooting

Ordered by how much time each problem typically costs.

---

## ComfyUI

**The control image appears to do nothing.**
**Check this first, every time: architecture mismatch.** A FLUX checkpoint requires a
FLUX-trained ControlNet. SD1.5/SDXL ControlNets are not compatible and **fail silently** —
no error, the control is just ignored. This is the single largest time sink for beginners.
Then: depth inverted (near should be **white**), or strength below ~0.4.

**Output changes when it should not.** A seed is randomised somewhere. Find it before debugging
anything else — you cannot debug a non-deterministic system.

**Output identical when it should not be.** You edited a node that is not wired into the graph.
Trace the wire from the sampler backwards.

**Washed out / blown / grey.** Wrong VAE, or CFG far too high or low. Try CFG 3.5 on a modern
checkpoint.

**Job cancelled.** You exceeded the Cloud runtime cap — **30 min** on Standard/Creator, 1 hr on
Pro. Split the workflow.

**Node missing on Comfy Cloud.** Custom-node support is a *curated* set, not all of GitHub. Find
a supported equivalent rather than fighting it.

**API returns 401/403.** The Comfy Cloud **API requires an active paid subscription**. The free
tier gives you the UI, not the API.

---

## Higgsfield

**Model id 404s / unknown model.** The catalog changes. Re-run
`models_explore(action="list", type="video")`. This course's tables are a 2026-09-02 snapshot.

**End frame ignored.** Not every model exposes `end_image`. `veo3_1`, `kling3_0_turbo`,
`kling2_6`, `veo3` accept `start_image` only. Check `models_explore` before assuming a bug.

**Output morphs unpleasantly between start and end.** The two frames are too far apart in scale,
angle or lighting. Derive the end frame *from* the start frame via img2img, and/or shorten the
duration.

**`video_references` ignored.** Confirm the model exposes that role. It exists on `seedance_2_0`,
`seedance_2_5`, `wan3_0`, `wan2_6`, `minimax_h3`, `flux_3_video`, `gemini_omni`. Not on Veo.

**Genjutsu output ignores your motion.** The driving clip is too short, too fast, or too
ambiguous. Grey-box motion must be legible — simplify it and slow it down.

**Credits draining fast.** You are iterating at full resolution. Drop to 480p, `mode: "fast"` or
the `_mini` variant, and set `generate_audio: false`.

**Upscale made it worse.** `bytedance_video_upscale` can over-sharpen. Try
`model_version: "standard"` instead of `"pro"`, or skip it for that shot.

---

## Blender

**`previs_rig.py` errors on my version.** Most likely the render engine name (the script tries
`BLENDER_EEVEE_NEXT` → `BLENDER_EEVEE` → `CYCLES`) or a compositor node name. Enable
**Developer Extras** in preferences and hover any field to see its exact Python path.

**Depth map is flat.** No depth range in the scene — the foreground occluder is missing or too
close to the subject. Parallax is the whole point.

**Depth appears inverted.** Check the Invert node. ControlNet convention is **near = white**.

**Camera move looks robotic.** Keyframe interpolation is linear. Set BEZIER + EASE_IN_OUT.
The video model will faithfully reproduce robotic motion, so fix it here.

**Blender is fighting me.** Run headless — `blender --background --python tools/blender/previs_rig.py`
— which removes the entire UI as a variable and makes errors much clearer.

---

## Unreal

**Python calls fail silently.** The **Sequencer Scripting** plugin is not enabled. This is
separate from the Python Editor Script Plugin and is very easy to miss.

**`add_master_track` not found.** Renamed to `add_track` in UE 5.4+. The provided script tries
both.

**Camera resets to origin when I add a transform track.** Known community report. Set the first
keyframe explicitly from known world coordinates rather than trusting the editor default.

**UE unusable on a 1660 SUPER.** Set scalability to Low. You are rendering grey boxes — you do
not need Lumen or Nanite.

---

## After Effects

**Roto Brush is missing.** **It was replaced by the Object Matte tool in 26.2.** Not a bug.
Every roto tutorial predating ~April 2026 is stale for the current UI.

**The composited element still looks pasted on.** Almost always missing **light wrap**, or the
matte edge is too hard. Choke 1–2 px and add the wrap.

**Grain looks wrong.** You applied it to one layer. Grain is a property of the final image —
adjustment layer, on top, over everything, always last.

**Patch slides.** Point tracking failed. Try **Mocha AE** planar tracking; on flat-ish surfaces
it is right far more often than beginners expect.

**3D camera track fails.** Expected on generated footage. Do not fight it — switch to a
locked-off plate or a planar track, and log the finding as a real production insight.

---

## Premiere

**Timeline stutters.** Mixed frame rates — the most common problem with generated footage.
Generators output 24/25/30 and Premiere conforms them badly. Interpret every clip to 24 fps.

**Playback is unusable.** Generate proxies. Premiere 26 has AI proxies specifically for weaker
hardware.

**Banding in dark areas of the export.** Enable **Render at Maximum Depth**, and add ~1% grain
over the whole piece. Grain hides banding. Check the *exported file*, not the timeline.

**It feels like a montage, not a scene.** Your ambience bed is not continuous under every cut.
This single fix converts more montages into scenes than anything else in this document.

---

## The `watch` skill

**`yt-dlp` fails with a proxy 403.** Your network blocks YouTube. That is what happened in this
course's build environment. Do not route around an organisational policy denial — run the audit
on a machine where YouTube resolves.

**No captions available.** Add a `GROQ_API_KEY` (preferred — cheaper and faster) or
`OPENAI_API_KEY` to `~/.config/watch/.env` for Whisper fallback, or accept frames-only with
`--no-whisper`.

**Frame extraction is slow.** Use `--detail efficient` (keyframes, cap 50) instead of `balanced`
(scene-aware, cap 100) for a first pass, then re-look at specific moments with
`--detail token-burner --start MM:SS --end MM:SS`.
