# YouTube Playlist — Exact Viewing Order

# ⏱️ REQUIRED VIDEO MINUTES: **437** (7h 17m runtime)
*9 hours are budgeted across the day headers to allow for pausing, rewinding and note-taking.
Day 0's audit adds ~90 min. Total ≈ 10% of the 105-hour course.*

---

## 🛑 READ BEFORE WATCHING ANYTHING

**Every entry below is UNVERIFIED.** The environment that built this course could not reach
YouTube — the egress proxy returned HTTP 403 to CONNECT on `youtube.com`
(see `research/source_audit.md` §1). The `watch` skill was installed and validated
(yt-dlp 2026.08.19, ffmpeg 6.1.1, preflight exit 0), but no video could be downloaded, so
**none of these were watched, and none are scored.**

**Day 0 (90 min): audit them yourself.**
```bash
bash tools/audit-tutorials.sh          # pulls transcript + frames for every candidate
# then score each against rubrics/tutorial_qc.md and fill in research/video_evaluations.csv
```

**Keep at most ONE primary and ONE secondary per module.** If three survive, you scored too
generously.

**The course does not depend on these videos.** Every module's authoritative source is official
documentation. If a candidate fails your audit, delete it — the day still works.

---

## VIEWING ORDER

### ▸ DAY 2 — Higgsfield references & Elements · **25 min**
| | |
|---|---|
| **Module** | higgsfield |
| **Candidates** | `UdWYf6Ck2ZM` — *Higgsfield Cinema Studio 2.5 Full Tutorial & Workflow*<br>`jazMJOMGStc` — *Cinema Studio 2.5 Tutorial — Complete Workflow Guide* |
| **URL** | https://www.youtube.com/watch?v=UdWYf6Ck2ZM · https://www.youtube.com/watch?v=jazMJOMGStc |
| **Upload** | ~2026-03/04 |
| **WATCH** | **Reference / Elements management chapters ONLY.** Skip intro, skip hype, skip the feature tour |
| **REQUIRED** | Required — pick **one**, not both |
| **Why selected** | 2.5 is the closest available version to the live platform; it added Soul Cast integration, which is exactly the identity-locking surface you need |
| **Reproducibility** | PENDING AUDIT |
| **⚠️ VERSION WARNING** | **Platform is on Cinema Studio 3.0. These cover 2.5.** Watch for *concepts* — how references and Elements are organised — not for click paths |
| **After watching you can** | Organise locked references and Elements so they persist across shots |

### ▸ DAY 4 — Premiere setup + J/L cuts · **50 min**
| | |
|---|---|
| **Module** | premiere |
| **Candidate** | `pq-O1VgEj_4` — *My Exact Premiere Pro Workflow for Short-Form Content 2026* |
| **URL** | https://www.youtube.com/watch?v=pq-O1VgEj_4 |
| **Upload** | 2026-05-11 |
| **WATCH** | **Project setup + trim tools only (~30 min)**, then ~20 min on J/L cuts from your highest-scoring source |
| **REQUIRED** | Required |
| **Why selected** | Version-current (Premiere 26.x). Its short-form focus is useful for your **reel cut**, not for narrative editing |
| **⚠️ WARNING** | **Scope its use narrowly.** Short-form pacing advice is actively wrong for a 45-second narrative scene |
| **After watching you can** | Configure a disciplined 24fps project and execute J/L cuts |

### ▸ DAY 6 — After Effects foundations · **80 min**
| | |
|---|---|
| **Module** | after-effects |
| **Candidate** | `JZGqZWDSVPg` — *AI Compositing Tutorial in After Effects (Firefly and Runway)* + ~20 min graph-editor coverage from your highest scorer |
| **URL** | https://www.youtube.com/watch?v=JZGqZWDSVPg |
| **WATCH** | Foundations + compositing principles |
| **REQUIRED** | Required |
| **⚠️ VERSION WARNING — THE BIGGEST TRAP IN THIS PLAYLIST** | **AE 26.2 replaced the Roto Brush with the Object Matte tool.** If this video teaches Roto Brush, watch it for *matte judgement* (edge quality, spill, holdout) and **ignore the click path entirely.** Verify every tool location against your own 26.x UI |
| **After watching you can** | Build comps, use the graph editor, and reason about matte quality |

### ▸ DAY 7 — Tracking & integration · **45 min**
| | |
|---|---|
| **Module** | after-effects |
| **Candidate** | Your audited AE **secondary**, or the tracking/integration chapters of the Day 6 primary |
| **WATCH** | **Light wrap and grain matching specifically** — these two do most of the work and are most often skipped |
| **REQUIRED** | Required |
| **After watching you can** | Track a plate and run the full integration chain in order |

### ▸ DAY 8 — ComfyUI fundamentals · **80 min**
| | |
|---|---|
| **Module** | comfyui |
| **Candidate** | `-igiHGaxKek` — *ComfyUI Tutorial for Beginners: LoRAs, Style Transfer & ControlNets (2026)* |
| **URL** | https://www.youtube.com/watch?v=-igiHGaxKek |
| **Upload** | 2026 |
| **WATCH** | Node-graph chapters (60 min) + ControlNet chapters (20 min) |
| **REQUIRED** | **Required — this is the single highest-value video in the course** |
| **Why selected** | Covers the exact triad the course needs: LoRA *use*, style transfer, ControlNet. Dated 2026 |
| **⚠️ WARNING** | **If it is a LOCAL-install tutorial, skip the entire setup section.** Unusable on 6 GB VRAM and irrelevant on Comfy Cloud. Jump straight to the graph |
| **After watching you can** | Trace a graph end to end and wire a ControlNet |

### ▸ DAY 9 — ControlNet wiring · **25 min**
| | |
|---|---|
| **Module** | comfyui |
| **Candidate** | `-ZyGkd0uRk8` — *Flux 2 Klein Control Net ComfyUI Workflow (Pose + Depth + Line Art)* |
| **URL** | https://www.youtube.com/watch?v=-ZyGkd0uRk8 |
| **WATCH** | ControlNet wiring chapters only |
| **REQUIRED** | Required |
| **⚠️ CRITICAL AUDIT POINT** | **Verify it uses a FLUX-trained ControlNet.** SD1.5/SDXL ControlNets are incompatible with FLUX checkpoints and **the failure is silent** — the control image is simply ignored. This is the #1 beginner time sink |
| **After watching you can** | Wire pose/depth/line-art control with matched architectures |

### ▸ DAY 11 — Blender → AI control · **60 min**
| | |
|---|---|
| **Module** | blender-ai-previs |
| **PRIMARY** | `1vB3JXzewx0` — **Andrew Price (Blender Guru), *How to control AI with Blender*** |
| **URL** | https://www.youtube.com/watch?v=1vB3JXzewx0 |
| **Upload** | ~2026-04 |
| **WATCH** | Full (~45 min) |
| **REQUIRED** | **Required — highest-priority candidate in the entire course** |
| **Why selected** | Reported to cover depth passes + ComfyUI + model generation: *exactly* the previs→AI bridge this course is built on. Creator has a long track record of complete, step-visible teaching |
| **Currentness** | CURRENT (2026, Blender 4.x/5.x) |
| **SECONDARY** | `g_YOqMaoIyE` — *COMPLETE Camera Tutorial Blender 5.1* — **camera-rig and animation chapters only (~15 min). Skip lighting and look-dev entirely** |
| **After watching you can** | Build a camera rig and export a depth pass that actually drives a model |

### ▸ DAY 12 — Depth pass reminder · **2 min**
| | |
|---|---|
| **Candidate** | `i301RLKrYUQ` — *Blender to After Effects: Depth Pass Workflow EXR & AGX* (**Short**) |
| **URL** | https://www.youtube.com/shorts/i301RLKrYUQ |
| **REQUIRED** | Optional |
| **⚠️ WARNING** | **A Short is a reminder card, never a teaching source.** Expect zero reproducibility. Do not score it as a primary |

### ▸ DAY 13 — ControlNet depth, in context · **20 min**
Rewatch **only** the ControlNet-depth section of your Day 8 primary — now that you have a real
depth pass to feed it. Context changes what you notice. No new video.

### ▸ DAY 14 — Unreal Cine Camera & Sequencer · **50 min** *(skip entirely if you cut Day 14)*
| | |
|---|---|
| **Module** | unreal-virtual-camera |
| **PRIMARY** | `aO_ceeiGHuw` — *Cinematography Deepdive for Beginners — Camera and Render Settings, UE 5.5* |
| **URL** | https://www.youtube.com/watch?v=aO_ceeiGHuw |
| **WATCH** | Cine Camera + Sequencer chapters |
| **REQUIRED** | Optional (Day 14 is the cuttable day) |
| **⚠️ VERSION WARNING** | UE **5.5**; current is **5.8**. Cine Camera concepts (filmback, focal length, aperture, focus) are stable across versions; **Movie Render Queue UI may differ.** Verify against the 5.8 docs |
| **BACKUP** | `-oV3oJZptEg` (UE 5.3) — two major versions behind. Use only if the primary fails audit |
| **After watching you can** | Build a Cine Camera and a Level Sequence with a Camera Cuts track |

---

## ❌ EXPLICITLY REJECTED — do not watch

| Video | Why |
|---|---|
| `buVZ7-0NX94` — *SEAMLESS Gameplay to Cinematic Finishers in UE5* | Gameplay-oriented. Out of scope. Listed so you don't rediscover it and lose an hour |
| `_WgYXtoiE1Y`, `ePel1kHEl8I`, `P1QIiMgk4do` — Cinema Studio **2.0** tutorials | Two versions behind, and mutually redundant. Use only if both 2.5 candidates fail audit |
| `4fILmWtW48c` — *EASY GUIDE 2026* | "Easy guide" framing = high filler risk. Audit the efficiency score hard before letting it in |

## Discovery queries to run yourself on Day 0
YouTube's own search was unreachable from the build environment, so these candidates came from
general web search. Run these queries directly on YouTube, sorted by upload date, to find
anything newer:

```
higgsfield cinema studio 3.0 tutorial workflow
comfyui controlnet depth flux 2026 workflow tutorial
after effects 26.2 object matte tutorial
blender depth pass controlnet ai video 2026
unreal engine 5.8 sequencer cine camera python
seedance 2.5 reference video control tutorial
```

Add anything that scores ≥75 to `research/video_evaluations.csv` and displace a weaker primary.
