"""
previs_rig.py — Blender previs rig for AI-controlled filmmaking.

RUN:  Blender > Scripting tab > Open > Run Script
 OR:  blender --background --python tools/blender/previs_rig.py

WHAT IT BUILDS
  A grey-box cinematic environment with one hero subject, one foreground occluder and
  background geometry, plus three cine cameras (24mm wide / 50mm medium / 85mm close) that
  all respect a single 180-degree line, plus one animated dolly camera.

WHAT IT OUTPUTS  (into ./previs_out/)
  clay/   RGB grey-box beauty frames   -> composition reference + Higgsfield start-frame base
  depth/  32-bit EXR Z + normalized PNG -> ComfyUI Workflow A (depth ControlNet)
  normal/ normal pass                   -> optional ControlNet / relighting reference
  mask/   object-index IDs              -> AE / compositing holdout mattes
  move/   dolly camera image sequence   -> Higgsfield video_references / Genjutsu driver

DESIGN RULE: the geometry must be CORRECT, not beautiful. Grey boxes are the deliverable.

STATUS: written against the documented bpy API for Blender 4.2+ / 5.x. Verify on your machine
before relying on it (see research/source_audit.md — Blender could not be executed in the
environment that authored this course).
"""

import bpy, os, math
from mathutils import Vector

OUT = os.path.join(os.path.dirname(bpy.data.filepath) or os.getcwd(), "previs_out")
RES_X, RES_Y = 1920, 1080
FPS = 24
MOVE_FRAMES = 96           # 4 seconds at 24fps
SENSOR_WIDTH = 36.0        # full-frame; keeps focal lengths meaning what you think they mean


# ---------------------------------------------------------------- helpers
def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.cameras, bpy.data.lights):
        for b in list(block):
            if b.users == 0:
                block.remove(b)


def set_engine():
    """EEVEE variants renamed across versions; fall back gracefully."""
    sc = bpy.context.scene
    for name in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"):
        try:
            sc.render.engine = name
            print(f"[previs] render engine = {name}")
            return name
        except TypeError:
            continue
    raise RuntimeError("no usable render engine found")


def box(name, loc, scale, pass_index=0):
    bpy.ops.mesh.primitive_cube_add(size=2, location=loc)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = Vector(scale)
    ob.pass_index = pass_index          # -> object-index mask pass
    return ob


def make_camera(name, loc, look_at, lens_mm):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens_mm
    cam_data.sensor_width = SENSOR_WIDTH
    cam_data.display_size = 0.5
    cam = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = Vector(loc)
    # aim: -Z forward, +Y up
    direction = (Vector(look_at) - cam.location)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    return cam


# ---------------------------------------------------------------- scene
def build_scene():
    clear_scene()
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = RES_X, RES_Y
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, MOVE_FRAMES

    # --- ground
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
    bpy.context.active_object.name = "GROUND"
    bpy.context.active_object.pass_index = 1

    # --- HERO SUBJECT at world origin. Everything is staged around this.
    hero = box("HERO_SUBJECT", (0, 0, 1.0), (0.45, 0.45, 1.0), pass_index=10)

    # --- FOREGROUND OCCLUDER (camera right) — gives the depth pass real parallax
    box("FG_OCCLUDER", (2.6, -4.2, 1.4), (0.35, 0.35, 1.4), pass_index=20)

    # --- BACKGROUND GEOMETRY — two walls forming a corridor down +Y
    box("BG_WALL_L", (-5.0, 6.0, 3.0), (0.3, 9.0, 3.0), pass_index=30)
    box("BG_WALL_R", (5.0, 6.0, 3.0), (0.3, 9.0, 3.0), pass_index=30)
    box("BG_BLOCK", (0.0, 15.0, 2.0), (4.0, 0.4, 2.0), pass_index=30)

    # --- lighting: key / fill / rim. Direction matters for the AI stage; quality does not.
    key = bpy.data.lights.new("KEY", type="AREA"); key.energy = 900; key.size = 6
    ko = bpy.data.objects.new("KEY", key); bpy.context.collection.objects.link(ko)
    ko.location = (-6, -5, 8)
    ko.rotation_euler = (Vector((0, 0, 1.2)) - ko.location).to_track_quat("-Z", "Y").to_euler()

    fill = bpy.data.lights.new("FILL", type="AREA"); fill.energy = 200; fill.size = 8
    fo = bpy.data.objects.new("FILL", fill); bpy.context.collection.objects.link(fo)
    fo.location = (6, -6, 4)
    fo.rotation_euler = (Vector((0, 0, 1.2)) - fo.location).to_track_quat("-Z", "Y").to_euler()

    rim = bpy.data.lights.new("RIM", type="AREA"); rim.energy = 700; rim.size = 3
    ro = bpy.data.objects.new("RIM", rim); bpy.context.collection.objects.link(ro)
    ro.location = (2, 9, 5)
    ro.rotation_euler = (Vector((0, 0, 1.4)) - ro.location).to_track_quat("-Z", "Y").to_euler()

    # ------------------------------------------------------------------
    # CAMERAS — ALL ON THE SAME SIDE OF THE 180 DEGREE LINE.
    # The line runs along the Y axis through the hero. Every camera keeps
    # negative X..0 bias and shoots from -Y. Cross this and your edit breaks.
    # ------------------------------------------------------------------
    target = (0, 0, 1.1)
    cams = {
        "CAM_A_WIDE_24":   make_camera("CAM_A_WIDE_24",   (-3.2, -9.0, 1.7), target, 24),
        "CAM_B_MED_50":    make_camera("CAM_B_MED_50",    (-2.0, -5.4, 1.5), target, 50),
        "CAM_C_CLOSE_85":  make_camera("CAM_C_CLOSE_85",  (-1.4, -3.4, 1.2), target, 85),
    }

    # --- animated dolly: pushes in on the hero, 35mm. This render becomes the MOTION DRIVER.
    dolly = make_camera("CAM_D_DOLLY_35", (-2.4, -11.0, 1.7), target, 35)
    dolly.location = Vector((-2.4, -11.0, 1.7))
    dolly.keyframe_insert("location", frame=1)
    dolly.keyframe_insert("rotation_euler", frame=1)
    dolly.location = Vector((-1.2, -5.2, 1.4))
    dolly.rotation_euler = (Vector(target) - dolly.location).to_track_quat("-Z", "Y").to_euler()
    dolly.keyframe_insert("location", frame=MOVE_FRAMES)
    dolly.keyframe_insert("rotation_euler", frame=MOVE_FRAMES)
    # ease the move — a linear dolly reads as robotic and the video model will copy that
    for fc in dolly.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
            kp.easing = "EASE_IN_OUT"
    cams["CAM_D_DOLLY_35"] = dolly
    return cams


# ---------------------------------------------------------------- passes
def enable_passes():
    vl = bpy.context.view_layer
    vl.use_pass_z = True
    vl.use_pass_normal = True
    vl.use_pass_object_index = True


def build_compositor(subdir):
    """Wire Render Layers -> File Output nodes for depth / normal / mask."""
    sc = bpy.context.scene
    sc.use_nodes = True
    nt = sc.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)

    rl = nt.nodes.new("CompositorNodeRLayers"); rl.location = (0, 0)

    # depth: full-precision EXR (never quantise depth you intend to use as control)
    d_exr = nt.nodes.new("CompositorNodeOutputFile"); d_exr.location = (500, 200)
    d_exr.base_path = os.path.join(OUT, "depth", subdir)
    d_exr.format.file_format = "OPEN_EXR"
    d_exr.format.color_depth = "32"
    d_exr.file_slots[0].path = "depth_exr_"
    nt.links.new(rl.outputs["Depth"], d_exr.inputs[0])

    # depth preview: normalized PNG for eyeballing and for nodes that want 8-bit
    norm = nt.nodes.new("CompositorNodeNormalize"); norm.location = (250, 60)
    nt.links.new(rl.outputs["Depth"], norm.inputs[0])
    inv = nt.nodes.new("CompositorNodeInvert"); inv.location = (370, 60)
    nt.links.new(norm.outputs[0], inv.inputs["Color"])   # near = white (ControlNet convention)
    d_png = nt.nodes.new("CompositorNodeOutputFile"); d_png.location = (500, 60)
    d_png.base_path = os.path.join(OUT, "depth", subdir)
    d_png.format.file_format = "PNG"
    d_png.file_slots[0].path = "depth_png_"
    nt.links.new(inv.outputs[0], d_png.inputs[0])

    if "Normal" in rl.outputs:
        n_out = nt.nodes.new("CompositorNodeOutputFile"); n_out.location = (500, -80)
        n_out.base_path = os.path.join(OUT, "normal", subdir)
        n_out.format.file_format = "PNG"
        n_out.file_slots[0].path = "normal_"
        nt.links.new(rl.outputs["Normal"], n_out.inputs[0])

    if "IndexOB" in rl.outputs:
        m_out = nt.nodes.new("CompositorNodeOutputFile"); m_out.location = (500, -220)
        m_out.base_path = os.path.join(OUT, "mask", subdir)
        m_out.format.file_format = "PNG"
        m_out.file_slots[0].path = "mask_"
        nt.links.new(rl.outputs["IndexOB"], m_out.inputs[0])


# ---------------------------------------------------------------- render
def render_stills(cams):
    sc = bpy.context.scene
    for name, cam in cams.items():
        if name == "CAM_D_DOLLY_35":
            continue
        sc.camera = cam
        enable_passes()
        build_compositor(name)
        sc.render.filepath = os.path.join(OUT, "clay", f"{name}_")
        sc.render.image_settings.file_format = "PNG"
        sc.frame_set(1)
        print(f"[previs] rendering still: {name}  ({cam.data.lens:.0f}mm)")
        bpy.ops.render.render(write_still=True)


def render_move(cams):
    sc = bpy.context.scene
    cam = cams["CAM_D_DOLLY_35"]
    sc.camera = cam
    enable_passes()
    build_compositor("CAM_D_DOLLY_35")
    sc.render.filepath = os.path.join(OUT, "move", "dolly_")
    sc.render.image_settings.file_format = "PNG"
    print(f"[previs] rendering {MOVE_FRAMES}-frame dolly move")
    bpy.ops.render.render(animation=True)


def main():
    for d in ("clay", "depth", "normal", "mask", "move"):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    set_engine()
    cams = build_scene()
    render_stills(cams)
    render_move(cams)
    print(f"\n[previs] DONE -> {OUT}")
    print("[previs] next: encode the move to mp4 for use as a motion reference:")
    print(f'[previs]   ffmpeg -framerate {FPS} -i "{os.path.join(OUT,"move","dolly_%04d.png")}" '
          f'-c:v libx264 -pix_fmt yuv420p -crf 18 "{os.path.join(OUT,"move","dolly_ref.mp4")}"')


if __name__ == "__main__":
    main()
