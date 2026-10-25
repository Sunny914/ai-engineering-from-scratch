"""Read review rows from CSV. Calculations stay in stats.py."""

from __future__ import annotations

import csv
from pathlib import Path

from .stats import Record

REQUIRED_FIELDS = ("text", "label", "score")


def load_records(path: str | Path) -> list[Record]:
    """Load review rows. A header-only file returns an empty list."""
    csv_path = Path(path)
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{csv_path.name} has no header row")
        missing = [name for name in REQUIRED_FIELDS if name not in reader.fieldnames]
        if missing:
            raise ValueError(
                f"{csv_path.name} is missing columns: {', '.join(missing)}"
            )
        return [_row_to_record(row, line_no) for line_no, row in enumerate(reader, start=2)]


def _row_to_record(row: dict[str, str | None], line_no: int) -> Record:
    text = _required_text(row.get("text"), line_no)
    label = _parse_label(row.get("label"), line_no)
    score = _parse_score(row.get("score"), line_no)
    return Record(text=text, label=label, score=score)


def _required_text(raw: str | None, line_no: int) -> str:
    if raw is None or raw.strip() == "":
        raise ValueError(f"line {line_no}: text is missing")
    return raw.strip()


def _parse_label(raw: str | None, line_no: int) -> int:
    if raw is None or raw.strip() == "":
        raise ValueError(f"line {line_no}: label is missing")
    try:
        return int(raw.strip())
    except ValueError:
        raise ValueError(
            f"line {line_no}: label must be an integer, got {raw.strip()!r}"
        ) from None


def _parse_score(raw: str | None, line_no: int) -> float:
    if raw is None or raw.strip() == "":
        raise ValueError(f"line {line_no}: score is missing")
    try:
        score = float(raw.strip())
    except ValueError:
        raise ValueError(
            f"line {line_no}: score must be a number, got {raw.strip()!r}"
        ) from None
    if score != score or score in (float("inf"), float("-inf")):
        raise ValueError(f"line {line_no}: score must be finite, got {raw.strip()!r}")
    return score
