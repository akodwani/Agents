# Module: Production Pipeline, QC and Reproducibility

**Course hours: woven throughout — no dedicated block.**
This module is the connective tissue. It is also, bluntly, the thing that will make you look
professional to an employer faster than any single craft skill.

---

## 1. The pipeline, end to end

```
CONCEPT → BEATS → SHOT LIST ──────────────────────────────┐
                     ↓                                     │
                 STORYBOARD (nano_banana_pro)              │  everything
                     ↓                                     │  references
             HERO FRAMES + LOCKED REFS (4k)                │  the shot list
                     ↓                                     │
        ┌────────────┴────────────┐                        │
   PREVIS (Blender/Unreal)   COMFY CONTROL                 │
   clay / depth / normal      Workflow A: depth → image    │
   mask / camera move         Workflow B: ref+pose → hero  │
        └────────────┬────────────┘                        │
                     ↓                                     │
              START + END FRAMES per shot ─────────────────┤
                     ↓                                     │
        HIGGSFIELD GENERATION (control rung ≥ 2)           │
                     ↓                                     │
              ─── SHOT QC GATE ───  ◄── fail → regenerate ─┘
                     ↓ pass
        REPAIR (deflicker → upscale aigc → sam_3_video matte)
                     ↓
              AFTER EFFECTS (comp, cleanup, integration)
                     ↓
              PREMIERE (edit → sound → colour → master)
                     ↓
              ─── FILM QC GATE ───
                     ↓
        MASTER + BREAKDOWN + PORTFOLIO
```

**Two gates, and they are not optional.** A shot that fails Shot QC never reaches AE. A film
that fails Film QC never reaches your portfolio. The discipline of *stopping* at a gate is what
separates a production from a pile of clips.

---

## 2. Reproducibility: the sidecar contract

Every generated asset gets a sidecar JSON with the same basename.

```json
{
  "shot_id": "S04",
  "version": 3,
  "created_utc": "2026-09-14T11:02:41Z",
  "model": "seedance_2_0",
  "params": { "duration": 6, "resolution": "1080p", "mode": "std",
              "genre": "action", "generate_audio": false },
  "media_roles": {
    "start_image": {"path": "05_frames/s04_start_v2.png", "sha256": "a91f…"},
    "end_image":   {"path": "05_frames/s04_end_v2.png",   "sha256": "77c3…"},
    "video_references": [{"path": "04_previs/move/dolly_ref.mp4", "sha256": "0be2…"}]
  },
  "prompt": "MS 50mm of HERO …",
  "control_rung": 4,
  "seed": 812344,
  "attempt": 2,
  "qc": {"passed": true, "failed_criteria": [], "notes": "slight edge shimmer at 0:03, fixed by deflicker"},
  "cost_credits": 42
}
```

**The test:** hand the sidecar to a stranger. Can they reproduce the shot? If not, it is a
lucky accident, not a production asset. Run this test on yourself at every QC gate.

The `sha256` on references is not paranoia — it is how you catch the specific bug where you
"locked" a reference and then quietly regenerated it, and half your film drifts.

---

## 3. Versioning
- **Git for everything text**: shot lists, prompts, workflow JSON, scripts, sidecars, manifests.
- **Media stays out of git** (`.gitignore` the media dirs) — reference by path + hash instead.
- **Naming: `s04_v03_comp.mov`.** Shot, version, stage. No "final_FINAL_v2_real".
- **Never overwrite a version.** Increment. Disk is cheap; a lost good take is not.
- Tag the commit you rendered your master from. When an interviewer asks "could you rebuild
  this?", the answer is a git tag.

## 4. Cost control
- Iterate at **480p / `fast` / `mini`** tiers with `generate_audio: false`. Promote only on pass.
- **Hard cap 6 generations per shot.** At the cap, the spec is wrong — go fix the start frame.
- Batch overnight where the API supports it.
- Track spend per shot in the sidecar (`cost_credits`). At the end of the course you will be
  able to say "this 45-second film cost $63 and 91 generations" — which is a genuinely
  impressive interview answer, because it demonstrates you think like a producer.

## 5. What "production-grade" actually means here
Not "looks nice". It means:
1. **Specified** — written down before it was made
2. **Reproducible** — rebuildable from the sidecar
3. **Gated** — passed an explicit written QC standard
4. **Versioned** — you can show v1, v2, v3 and say what changed and why
5. **Explainable** — you can defend every tool and parameter choice out loud

Those five properties are what an employer is buying. The pretty picture is table stakes.
