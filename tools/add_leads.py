"""Append discovered postings to the ingest JSONL (one object per line)."""
import json, sys
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "data" / "ingest" / "leads.jsonl"


def add(records):
    PATH.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    if PATH.exists():
        for line in PATH.read_text().splitlines():
            if line.strip():
                seen.add(json.loads(line).get("url", ""))
    n = 0
    with PATH.open("a") as fh:
        for r in records:
            if r.get("url") in seen:
                continue
            seen.add(r.get("url"))
            fh.write(json.dumps(r) + "\n")
            n += 1
    return n


if __name__ == "__main__":
    print(add(json.load(sys.stdin)))
