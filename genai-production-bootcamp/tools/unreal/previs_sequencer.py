"""
previs_sequencer.py — Unreal Engine virtual-camera previs via official Python.

RUN:  Unreal Editor > Output Log > Cmd dropdown -> "Python" -> exec this file
 OR:  Window > Execute Python Script

REQUIRED PLUGINS (Edit > Plugins, then restart):
  * Python Editor Script Plugin
  * Sequencer Scripting
  * Movie Render Queue   (for the render step)

WHY PYTHON AND NOT MCP
  UE 5.8 ships a first-party "Unreal MCP" plugin, but Epic labels it EXPERIMENTAL, localhost
  only, "incomplete in places", with APIs that "may change". A course must not put an
  experimental plugin on its critical path. This script is the stable path and it is also the
  better portfolio artifact — a recruiter can read a script; they cannot read your chat log.
  Use an MCP to help you AUTHOR this file if you like. Ship the file.

WHAT IT BUILDS
  Four Cine Camera Actors around one subject, all on the same side of the 180-degree line:
    CAM_A  24mm wide      CAM_B  50mm medium
    CAM_C  85mm close     CAM_D  35mm animated dolly
  A Level Sequence at 24fps with a Camera Cuts track and a keyframed transform on CAM_D.

STATUS: written against the documented UE 5.x Python API. Version-fragile calls are wrapped
with fallbacks and printed warnings. VERIFY IN YOUR EDITOR — Unreal could not be executed in
the environment that authored this course (see research/source_audit.md).
"""

import unreal

SEQ_PATH   = "/Game/Previs"
SEQ_NAME   = "SEQ_Previs"
FPS        = 24
DURATION_F = 96                        # 4 seconds
SUBJECT    = unreal.Vector(0, 0, 110)  # cm. Unreal is Z-up, centimetres.


# --------------------------------------------------------------- compat shims
def _actor_subsystem():
    """EditorLevelLibrary is deprecated in UE5; prefer the subsystem."""
    try:
        return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    except Exception:
        return None


def spawn(cls, location, rotation):
    sub = _actor_subsystem()
    if sub:
        return sub.spawn_actor_from_class(cls, location, rotation)
    return unreal.EditorLevelLibrary.spawn_actor_from_class(cls, location, rotation)


def add_seq_track(seq, track_cls):
    """add_master_track (<=5.3) vs add_track (>=5.4)."""
    for name in ("add_track", "add_master_track"):
        fn = getattr(seq, name, None)
        if fn:
            try:
                return fn(track_cls)
            except Exception:
                continue
    raise RuntimeError("could not add sequence track — check your UE version's API")


def look_at(from_v, to_v):
    return unreal.MathLibrary.find_look_at_rotation(from_v, to_v)


# --------------------------------------------------------------- cameras
def make_cine_camera(label, loc, focal_mm, target=SUBJECT):
    rot = look_at(loc, target)
    actor = spawn(unreal.CineCameraActor, loc, rot)
    actor.set_actor_label(label)

    comp = actor.get_cine_camera_component()
    comp.set_editor_property("current_focal_length", float(focal_mm))

    # Filmback: set it explicitly so focal lengths mean what a stills photographer expects.
    try:
        fb = comp.get_editor_property("filmback")
        fb.set_editor_property("sensor_width", 36.0)
        fb.set_editor_property("sensor_height", 20.25)   # 16:9 on full-frame width
        comp.set_editor_property("filmback", fb)
    except Exception as e:
        unreal.log_warning(f"[previs] filmback not set on {label}: {e}")

    # Focus on the subject, manual — autofocus drifts and ruins a repeatable previs.
    try:
        fs = comp.get_editor_property("focus_settings")
        fs.set_editor_property("focus_method", unreal.CameraFocusMethod.MANUAL)
        dist = unreal.MathLibrary.vector_distance(loc, target)
        fs.set_editor_property("manual_focus_distance", float(dist))
        comp.set_editor_property("focus_settings", fs)
    except Exception as e:
        unreal.log_warning(f"[previs] focus not set on {label}: {e}")

    # Aperture: shallow enough to read as cinematic, deep enough to keep geometry legible.
    try:
        comp.set_editor_property("current_aperture", 4.0)
    except Exception:
        pass

    unreal.log(f"[previs] camera {label}: {focal_mm}mm @ {loc}")
    return actor


# --------------------------------------------------------------- sequence
def build():
    # ---- 180-DEGREE LINE: the line runs along the Y axis through the subject.
    # Every camera sits at NEGATIVE Y. Do not put one at +Y or your edit will flip.
    cams = [
        ("CAM_A_WIDE_24",  unreal.Vector(-320, -900, 170), 24),
        ("CAM_B_MED_50",   unreal.Vector(-200, -540, 150), 50),
        ("CAM_C_CLOSE_85", unreal.Vector(-140, -340, 120), 85),
    ]
    actors = {label: make_cine_camera(label, loc, mm) for label, loc, mm in cams}

    dolly_start = unreal.Vector(-240, -1100, 170)
    dolly_end   = unreal.Vector(-120, -520, 140)
    dolly = make_cine_camera("CAM_D_DOLLY_35", dolly_start, 35)
    actors["CAM_D_DOLLY_35"] = dolly

    # ---- create the Level Sequence asset
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    seq = tools.create_asset(SEQ_NAME, SEQ_PATH, unreal.LevelSequence,
                             unreal.LevelSequenceFactoryNew())
    seq.set_display_rate(unreal.FrameRate(FPS, 1))
    seq.set_playback_start(0)
    seq.set_playback_end(DURATION_F)

    bindings = {}
    for label, actor in actors.items():
        b = seq.add_possessable(actor)
        bindings[label] = b

    # ---- keyframe the dolly move on CAM_D
    tb = bindings["CAM_D_DOLLY_35"]
    ttrack = tb.add_track(unreal.MovieScene3DTransformTrack)
    tsec = ttrack.add_section()
    tsec.set_range(0, DURATION_F)

    rot_start = look_at(dolly_start, SUBJECT)
    rot_end   = look_at(dolly_end,   SUBJECT)

    # channel order: loc X,Y,Z | rot X(roll),Y(pitch),Z(yaw) | scale X,Y,Z
    ch = tsec.get_all_channels()
    keys = [
        (0, [dolly_start.x, dolly_start.y, dolly_start.z,
             rot_start.roll, rot_start.pitch, rot_start.yaw, 1.0, 1.0, 1.0]),
        (DURATION_F, [dolly_end.x, dolly_end.y, dolly_end.z,
                      rot_end.roll, rot_end.pitch, rot_end.yaw, 1.0, 1.0, 1.0]),
    ]
    for frame, vals in keys:
        for i, v in enumerate(vals):
            if i < len(ch):
                ch[i].add_key(unreal.FrameNumber(frame), float(v))

    # ---- Camera Cuts: A (wide) -> B (medium) -> C (close) -> D (move)
    cut_track = add_seq_track(seq, unreal.MovieSceneCameraCutTrack)
    order = ["CAM_A_WIDE_24", "CAM_B_MED_50", "CAM_C_CLOSE_85", "CAM_D_DOLLY_35"]
    span = DURATION_F // len(order)
    for i, label in enumerate(order):
        sec = cut_track.add_section()
        sec.set_range(i * span, (i + 1) * span)
        try:
            bid = unreal.MovieSceneObjectBindingID()
            bid.set_editor_property("guid", bindings[label].get_id())
            sec.set_camera_binding_id(bid)
        except Exception as e:
            unreal.log_warning(f"[previs] camera cut binding for {label} failed: {e}. "
                               "Assign it by hand in Sequencer — 30 seconds of clicking.")

    unreal.EditorAssetLibrary.save_loaded_asset(seq)
    unreal.log(f"[previs] DONE -> {SEQ_PATH}/{SEQ_NAME}")
    unreal.log("[previs] next: Window > Cinematics > Movie Render Queue, add this sequence, "
               "render PNG sequence, then encode with ffmpeg for use as a motion reference.")
    return seq


if __name__ == "__main__":
    build()
