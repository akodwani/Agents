#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Day 0 — Tutorial audit harness
#
# WHY THIS EXISTS
#   The machine that built this course could not reach YouTube (egress policy
#   returned HTTP 403 to CONNECT on youtube.com — see research/source_audit.md §1).
#   Every row in research/video_evaluations.csv is therefore an UNVERIFIED lead.
#   This script performs the audit that could not be performed there, on your
#   machine, where YouTube resolves.
#
# WHAT IT DOES
#   For each candidate URL it runs the installed `watch` skill to pull the
#   transcript plus scene-aware frames into a per-video folder. You then open
#   that folder, look at the frames, and score the video against
#   rubrics/tutorial_qc.md. Frames are the point: a transcript alone cannot tell
#   you whether the instructor actually showed the node graph and the settings.
#
# TIME BUDGET: 60–90 minutes for the full candidate list.
#
# PREREQUISITES (verified working in the build environment):
#   yt-dlp   >= 2026.08.19   pip install --user yt-dlp
#   ffmpeg   >= 6.1          apt install ffmpeg   |   brew install ffmpeg
#   watch skill              npx skills add bradautomates/claude-video -g
# ---------------------------------------------------------------------------
set -uo pipefail

SKILL_DIR="${SKILL_DIR:-$HOME/.agents/skills/watch}"
OUT_ROOT="${OUT_ROOT:-./audit}"
DETAIL="${DETAIL:-balanced}"     # transcript | efficient | balanced | token-burner
CSV="${CSV:-research/video_evaluations.csv}"

if [ ! -f "$SKILL_DIR/scripts/watch.py" ]; then
  echo "ERROR: watch skill not found at SKILL_DIR=$SKILL_DIR" >&2
  echo "Install it:  npx skills add bradautomates/claude-video -g" >&2
  echo "Then re-run with:  SKILL_DIR=/path/to/skills/watch $0" >&2
  exit 1
fi

echo "== preflight =="
python3 "$SKILL_DIR/scripts/setup.py" --check || {
  echo "watch preflight failed — running installer" >&2
  python3 "$SKILL_DIR/scripts/setup.py"
}

mkdir -p "$OUT_ROOT"

# Pull module+url from the candidate CSV, skipping the header and any row
# already marked REJECT-ON-SIGHT in its notes.
python3 - "$CSV" <<'PY' > "$OUT_ROOT/queue.tsv"
import csv,sys
with open(sys.argv[1]) as f:
    for r in csv.DictReader(f):
        if "OUT OF SCOPE" in r["notes"]: continue
        if not r["url"].startswith("http"): continue
        print(f"{r['module']}\t{r['url']}\t{r['title'][:60]}")
PY

total=$(wc -l < "$OUT_ROOT/queue.tsv")
echo "== $total candidates queued (detail=$DETAIL) =="
i=0
while IFS=$'\t' read -r module url title; do
  i=$((i+1))
  slug=$(echo "$url" | sed 's/.*[?&]v=//; s/.*shorts\///; s/[^A-Za-z0-9_-]//g' | cut -c1-16)
  dest="$OUT_ROOT/$module/$slug"
  if [ -d "$dest" ] && [ -n "$(ls -A "$dest" 2>/dev/null)" ]; then
    echo "[$i/$total] SKIP (already audited) $module/$slug"; continue
  fi
  mkdir -p "$dest"
  echo "[$i/$total] $module :: $title"
  # --no-whisper: rely on native captions. Add a GROQ_API_KEY to
  # ~/.config/watch/.env if you want Whisper fallback for caption-less videos.
  python3 "$SKILL_DIR/scripts/watch.py" "$url" \
      --detail "$DETAIL" --out-dir "$dest" --no-whisper \
      > "$dest/watch.log" 2>&1 \
    || echo "  !! FAILED — see $dest/watch.log (common causes: age-gate, region lock, no captions)"
done < "$OUT_ROOT/queue.tsv"

cat <<'NEXT'

== AUDIT COLLECTED ==

Now do the part no script can do — LOOK AT THE FRAMES.

For each folder under ./audit/<module>/<id>/ :
  1. Read watch.log for the transcript and the extracted frame paths.
  2. OPEN THE FRAMES. Ask specifically:
       - Is the node graph / settings panel / timeline actually legible on screen?
       - Are prompts and seeds visible, or cropped out / blurred?
       - Does the UI match the version you are running RIGHT NOW?
       - Are failed attempts shown, or only the winning take?
  3. Score against rubrics/tutorial_qc.md (0–100, penalties included).
  4. Write the score back into research/video_evaluations.csv, replacing
     PENDING-AUDIT and setting verdict to PRIMARY / SECONDARY / REFERENCE / REJECT.

STOP RULE: keep at most ONE primary + ONE secondary per module. If three videos
survive, you scored too generously — re-apply the duplication penalty.

Targeted re-look at a single moment:
  python3 "$SKILL_DIR/scripts/watch.py" <url> --detail token-burner \
      --start 12:30 --end 15:00
NEXT
