"""Ingest postings discovered through an out-of-process channel.

The crawler is the primary discovery route. When the machine running this
system cannot reach the open web directly (locked-down container, corporate
egress policy), discovery can still be performed by an agent with a search
tool, and its findings are handed to the same normalise -> dedupe -> score
pipeline through a JSONL file so nothing bypasses the scoring model.

Each line is one posting object using the raw-stub field names from
`pipeline.build_row` plus optional pre-set verification fields.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .db import connect
from .pipeline import store


def ingest_file(path: str | Path, conn: sqlite3.Connection | None = None,
                default_source: str = "websearch") -> dict[str, int]:
    own = conn is None
    conn = conn or connect()
    counts = {"inserted": 0, "duplicate": 0, "merged_upgraded": 0, "skipped_incomplete": 0}
    with Path(path).open() as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            raw = json.loads(line)
            raw.setdefault("source_discovered_from", default_source)
            _, action = store(conn, raw)
            counts[action] = counts.get(action, 0) + 1
    if own:
        conn.close()
    return counts
