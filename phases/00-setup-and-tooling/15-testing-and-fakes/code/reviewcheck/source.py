"""Ways to obtain review records. The report never opens a file itself."""

from __future__ import annotations

import csv
import os
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from .records import Record

REQUIRED_FIELDS = ("text", "label", "score")


class RecordSource(Protocol):
    """Anything with a read method can feed a review batch."""

    def read(self) -> Sequence[Record]:
        """Return the records for one batch."""


class MemoryReader:
    """In-memory source. Tests use this instead of a CSV file."""

    def __init__(self, records: Sequence[Record]) -> None:
        self._records = list(records)

    def read(self) -> list[Record]:
        return list(self._records)


class CsvReader:
    """Read review rows from one CSV file."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def read(self) -> list[Record]:
        with self.path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ValueError(f"{self.path.name} has no header row")
            missing = [name for name in REQUIRED_FIELDS if name not in reader.fieldnames]
            if missing:
                raise ValueError(
                    f"{self.path.name} is missing columns: {', '.join(missing)}"
                )
            return [
                _row_to_record(row, line_no)
                for line_no, row in enumerate(reader, start=2)
            ]


def path_from_env() -> Path:
    """Return the CSV path in REVIEW_CSV. A blank value is an error."""
    raw = os.environ.get("REVIEW_CSV", "").strip()
    if not raw:
        raise ValueError("REVIEW_CSV is not set")
    return Path(raw)


def _row_to_record(row: dict[str, str | None], line_no: int) -> Record:
    text = row.get("text")
    label_raw = row.get("label")
    score_raw = row.get("score")
    if text is None or text.strip() == "":
        raise ValueError(f"line {line_no}: text is missing")
    if label_raw is None or label_raw.strip() == "":
        raise ValueError(f"line {line_no}: label is missing")
    if score_raw is None or score_raw.strip() == "":
        raise ValueError(f"line {line_no}: score is missing")
    try:
        label = int(label_raw.strip())
    except ValueError:
        raise ValueError(
            f"line {line_no}: label must be an integer, got {label_raw.strip()!r}"
        ) from None
    try:
        score = float(score_raw.strip())
    except ValueError:
        raise ValueError(
            f"line {line_no}: score must be a number, got {score_raw.strip()!r}"
        ) from None
    return Record(text=text.strip(), label=label, score=score)
