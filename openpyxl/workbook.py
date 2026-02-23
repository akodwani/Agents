from __future__ import annotations

import json
from pathlib import Path


class Cell:
    def __init__(self, value=None):
        self.value = value
        self.font = None
        self.fill = None


class ColumnDimension:
    def __init__(self):
        self.width = None


class Worksheet:
    def __init__(self, rows):
        self._rows = rows
        self.column_dimensions = {}
        headers = list(rows[0].keys()) if rows else []
        self._header_cells = [Cell(h) for h in headers]

    def __getitem__(self, idx):
        if idx == 1:
            return self._header_cells
        return []

    @property
    def columns(self):
        headers = [c.value for c in self._header_cells]
        for header in headers:
            yield [Cell(header)] + [Cell(row.get(header)) for row in self._rows]


class Workbook:
    def __init__(self, path: Path, data):
        self.path = path
        self._data = data
        self.worksheets = [Worksheet(rows) for rows in data.get("sheets", {}).values()]

    def save(self, path):
        # persist unchanged data; style ops are no-op in this lightweight stub
        Path(path).write_text(json.dumps(self._data))


def load_workbook(path):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    data = json.loads(p.read_text())
    wb = Workbook(p, data)
    # ensure column dimensions can be accessed dynamically
    for ws in wb.worksheets:
        class _DefaultDict(dict):
            def __missing__(self, key):
                val = ColumnDimension()
                self[key] = val
                return val
        ws.column_dimensions = _DefaultDict()
    return wb
