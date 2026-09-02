# Primary Sources

Documentation beats tutorials for facts: API behaviour, limits, versions, supported inputs,
model capabilities, plugin installation. Use YouTube only for craft, technique and workflow
demonstration. **Never let one creator's opinion become your fact.**

## Higgsfield
| Source | URL |
|---|---|
| **Live model catalog (the authoritative one)** | `models_explore(action="list", type="video"\|"image"\|"3d")` via MCP |
| **Live workflow catalog** | `get_workflow_instructions()` — no argument lists all |
| Model constraints for a specific model | `models_explore(action="get", model_id="...")` |
| Presets | `presets_show` |
| CLI & Skills | higgsfield.ai/cli · higgsfield.ai/skills |
| MCP | higgsfield.ai/mcp |
| CLI/Skills help | higgsfield.ai/creator-hub/help-center/mcp-cli/how-do-i-access-higgsfield-via-cli |
| Cinema Studio guide | higgsfield.ai/creator-hub/help-center/tools/how-do-i-use-cinema-studio |
| Cinema Studio 3.0 announcement | higgsfield.ai/blog/cinema-studio-3 |
| Start & End frames | higgsfield.ai/blog/Storytelling-with-Start-End-Frames-by-Higgsfield |

> **When a model id 404s, re-run `models_explore`.** The catalog changes; this course's tables
> are a snapshot dated 2026-09-02.

## ComfyUI / Comfy Cloud
| Source | URL |
|---|---|
| Official docs | docs.comfy.org |
| **Cloud API reference** | docs.comfy.org/development/cloud/api-reference |
| Cloud pricing | comfy.org/cloud/pricing |
| Depth ControlNet example | docs.comfy.org/tutorials/controlnet/depth-controlnet |

## Blender
| Source | URL |
|---|---|
| Python API (`bpy`) | docs.blender.org/api/current |
| Manual | docs.blender.org/manual/en/latest |
| **Official MCP server** | blender.org/lab/mcp-server · projects.blender.org/lab/blender_mcp |
| Community MCP | github.com/ahujasid/blender-mcp |

> Enable **Developer Extras** in Blender preferences, then hover any field to see its Python
> path. This is faster than searching the API docs and it is how you debug `previs_rig.py`.

## Unreal Engine
| Source | URL |
|---|---|
| **Python Scripting in Sequencer** | dev.epicgames.com/documentation/unreal-engine/python-scripting-in-sequencer-in-unreal-engine |
| Cinematics and Movie Making | dev.epicgames.com/documentation/unreal-engine/cinematics-and-movie-making-in-unreal-engine |
| **Unreal MCP (5.8, EXPERIMENTAL)** | dev.epicgames.com/documentation/unreal-engine/unreal-mcp-in-unreal-editor |
| MCP plugin index | dev.epicgames.com/documentation/unreal-engine/API/PluginIndex/ModelContextProtocol |
| 5.8 release notes | dev.epicgames.com/documentation/unreal-engine/unreal-engine-5-8-release-notes |

## Adobe
| Source | URL |
|---|---|
| **AE Object Matte (replaces Roto Brush in 26.2)** | helpx.adobe.com/after-effects/desktop/roto-brush-and-refine-matte/roto-brush/object-matte.html |
| Roto Brush & Refine Matte | helpx.adobe.com/after-effects/using/roto-brush-refine-matte.html |
| AE release notes | community.adobe.com — search "After Effects 26.2 is here" |
| Premiere Pro help | helpx.adobe.com/premiere-pro |

## The `watch` skill
| Source | URL |
|---|---|
| Repository | github.com/bradautomates/claude-video |
| Install (agent skills) | `npx skills add bradautomates/claude-video -g` |
| Install (Claude Code plugin) | `/plugin marketplace add bradautomates/claude-video` then `/plugin install watch@claude-video` |
| Dependencies | `yt-dlp`, `ffmpeg`; optional Groq/OpenAI key for Whisper fallback |

## Job market
| Source | URL |
|---|---|
| AI Artist Jobs | aiartistjobs.co |
| Curious Refuge AI jobs board | curiousrefuge.com/ai-jobs-board |
| Built In NYC | builtinnyc.com/jobs/artificial-intelligence |

## How to verify a claim in this course
1. Is it labelled DEMONSTRATED? Then I ran it — but the environment differed from yours.
2. Is it labelled DOCUMENTED? Follow the link above and confirm; docs change.
3. Is it labelled INFERRED, EXPERIMENTAL, COMMUNITY or UNVERIFIED? **Treat it as a hypothesis.**
4. When a tutorial and a doc disagree, **the doc wins.**
