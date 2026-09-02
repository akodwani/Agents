# Module: Photoshop — Deliberately Small

**Course hours: ~3** · Woven into Days 2, 16 and 19. There is no Photoshop *day*.

## Why this module shrank

The brief scoped Photoshop for frame prep, generative fill, frame extension, cleanup and matte
creation. Since then, the live Higgsfield catalog shows those jobs have moved:

| Old Photoshop job | Now done by | Evidence |
|---|---|---|
| Generative fill | `nano_banana_2` (`mask` role + `is_inpaint`), `seedream_v5_pro` (`is_inpaint`) | DEMONSTRATED via live MCP |
| Extending frames / reframing | `flux_2_pro_outpaint` (per-side pixel expansion; negatives crop) | DEMONSTRATED |
| Background removal | `image_background_remover`, `seedream_v5_pro` (`remove_bg`) | DEMONSTRATED |
| Video matte extraction | `sam_3_video` (SAM-3, `apply_mask`) and AE Object Matte | DEMONSTRATED / DOCUMENTED |

Spending 8 hours on Photoshop to do what one API call does is the definition of a skill that
has not earned its place. Photoshop appears in 13 hard requirements, so you must be *fluent*,
not *expert*.

## What survives — the things models still do badly

1. **Precise hand-authored selections.** Pen tool paths and refined edges where a model's
   segmentation is 95% right and you need 100%. Quick Selection → Select & Mask → refine edge →
   decontaminate colours.
2. **Matte creation and handoff to AE.** Exporting an alpha channel or a clean PNG with
   transparency that AE reads correctly. This is a *pipeline* skill, not an art skill.
3. **Frame surgery on a start frame.** Your `start_image` determines the whole shot. If one
   element is wrong, fixing it in Photoshop is faster and more precise than re-rolling and
   losing everything else you liked.
4. **Colour adjustment for reference consistency.** Getting two locked references to sit in the
   same colour world before you use them as `image_references`.
5. **Compositing a rough frame from parts.** Sometimes the fastest route to a start frame is to
   paste three generated elements together roughly and let img2img (Comfy Workflow B) unify
   them. Rough is fine — you are making a *specification*, not a deliverable.

## What to skip
Photo retouching, frequency separation, brushwork, type design, layer-style craft, actions and
droplets, camera raw depth. None of it serves the pipeline.

## Exercise

**PS1 — Start-frame surgery (60 min).** Take a generated frame that is 90% right and has one
wrong element. Fix it using selection + generative fill (either Photoshop's or a round trip
through `nano_banana_2` with a mask you author in Photoshop).
**Exit: the fix is invisible at 100%, and the frame works as a `start_image` — verify by
generating a 4-second shot from it.**

**PS2 — Clean matte handoff (45 min).** Take a generated subject. Produce a pixel-accurate alpha
matte. Import to AE and confirm the edge holds against a contrasting background.
**Exit: no halo, no fringe, no chewed edges at 200%.**
