"""Minimal local pandas substitute for this kata environment."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List
import json


class Series:
    def __init__(self, values: List[Any]):
        self.values = values

    def mean(self) -> float:
        return sum(float(v) for v in self.values) / len(self.values) if self.values else 0.0

    def max(self):
        return max(self.values)

    def min(self):
        return min(self.values)


class _LocIndexer:
    def __init__(self, df: "DataFrame"):
        self.df = df

    def __setitem__(self, key, value):
        row_idx, col = key
        self.df.rows[row_idx][col] = value


class DataFrame:
    def __init__(self, data: Any):
        if isinstance(data, list):
            self.rows = [dict(r) for r in data]
        elif isinstance(data, dict):
            keys = list(data.keys())
            length = len(next(iter(data.values()), []))
            self.rows = [{k: data[k][i] for k in keys} for i in range(length)]
        else:
            self.rows = []

    def sort_values(self, key: str) -> "DataFrame":
        return DataFrame(sorted(self.rows, key=lambda r: r.get(key)))

    def reset_index(self, drop: bool = False) -> "DataFrame":
        return DataFrame(self.rows)

    def __getitem__(self, key: str) -> Series:
        return Series([r.get(key) for r in self.rows])

    def to_excel(self, writer: "ExcelWriter", sheet_name: str, index: bool = False) -> None:
        writer.add_sheet(sheet_name, self)

    def copy(self) -> "DataFrame":
        return DataFrame(self.rows)

    @property
    def loc(self):
        return _LocIndexer(self)

    def iterrows(self):
        for i, row in enumerate(self.rows):
            yield i, row


@dataclass
class ExcelWriter:
    path: str | Path
    engine: str | None = None

    def __post_init__(self):
        self.path = str(self.path)
        self.sheets: Dict[str, List[Dict[str, Any]]] = {}

    def __enter__(self) -> "ExcelWriter":
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            payload = {"sheets": self.sheets}
            Path(self.path).write_text(json.dumps(payload))

    def add_sheet(self, name: str, dataframe: DataFrame) -> None:
        self.sheets[name] = dataframe.rows
