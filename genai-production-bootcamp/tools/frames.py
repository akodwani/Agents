#!/usr/bin/env python3
"""
frames.py — first / middle / last frame extraction + contact sheet.

The Shot QC pass (rubrics/shot_qc.md) starts by looking at first, middle and last frame
side by side. This does that in one command, so QC costs seconds instead of scrubbing.

USAGE
    python3 tools/frames.py 06_gen/s04_v02.mp4
    python3 tools/frames.py 06_gen/*.mp4 --out day18/qc
    python3 tools/frames.py shot.mp4 --n 5          # 5 evenly spaced frames instead of 3

OUTPUT
    <out>/<stem>_f001.png ... plus <out>/<stem>_contact.png

REQUIRES: ffmpeg + ffprobe on PATH.
"""
import argparse, json, shutil, subprocess, sys
from pathlib import Path


def probe_duration(path: Path) -> float:
    """Seconds, via ffprobe. Falls back to the stream duration if the container lacks one."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json",
         "-show_entries", "format=duration:stream=duration",
         str(path)],
        capture_output=True, text=True, check=True).stdout
    data = json.loads(out)
    for candidate in (data.get("format", {}).get("duration"),
                      *(s.get("duration") for s in data.get("streams", []))):
        try:
            d = float(candidate)
            if d > 0:
                return d
        except (TypeError, ValueError):
            continue
    raise RuntimeError(f"could not determine duration of {path}")


def grab(path: Path, ts: float, dest: Path) -> None:
    # -ss before -i seeks fast; -update 1 keeps ffmpeg from treating the output as a sequence.
    subprocess.run(
        ["ffmpeg", "-nostdin", "-v", "error", "-y",
         "-ss", f"{ts:.3f}", "-i", str(path),
         "-frames:v", "1", "-update", "1", str(dest)],
        check=True)


def contact_sheet(frames: list[Path], dest: Path, width: int = 640) -> None:
    """Horizontal strip. Uses ffmpeg's hstack so there is no Pillow dependency."""
    if len(frames) == 1:
        shutil.copy(frames[0], dest)
        return
    args = ["ffmpeg", "-nostdin", "-v", "error", "-y"]
    for f in frames:
        args += ["-i", str(f)]
    scale = "".join(f"[{i}:v]scale={width}:-1[s{i}];" for i in range(len(frames)))
    stack = "".join(f"[s{i}]" for i in range(len(frames)))
    args += ["-filter_complex", f"{scale}{stack}hstack=inputs={len(frames)}[out]",
             "-map", "[out]", str(dest)]
    subprocess.run(args, check=True)


def process(path: Path, out_dir: Path, n: int) -> None:
    dur = probe_duration(path)
    # Pull slightly inside the boundaries — the true last frame often fails to decode.
    if n == 1:
        points = [dur / 2]
    else:
        span = dur - 0.10
        points = [0.05 + span * i / (n - 1) for i in range(n)]

    out_dir.mkdir(parents=True, exist_ok=True)
    made = []
    for i, ts in enumerate(points, 1):
        dest = out_dir / f"{path.stem}_f{i:03d}.png"
        grab(path, ts, dest)
        made.append(dest)

    sheet = out_dir / f"{path.stem}_contact.png"
    contact_sheet(made, sheet)
    print(f"{path.name}  {dur:.2f}s  ->  {len(made)} frames + {sheet.name}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract QC frames and build a contact sheet.")
    ap.add_argument("videos", nargs="+", type=Path)
    ap.add_argument("--out", type=Path, default=Path("qc_frames"))
    ap.add_argument("--n", type=int, default=3, help="frames per clip (default 3)")
    args = ap.parse_args()

    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            print(f"error: {tool} not found on PATH", file=sys.stderr)
            return 1
    if args.n < 1:
        print("error: --n must be >= 1", file=sys.stderr)
        return 1

    failures = 0
    for v in args.videos:
        if not v.exists():
            print(f"skip (missing): {v}", file=sys.stderr); failures += 1; continue
        try:
            process(v, args.out, args.n)
        except (subprocess.CalledProcessError, RuntimeError) as e:
            print(f"FAILED {v}: {e}", file=sys.stderr); failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
