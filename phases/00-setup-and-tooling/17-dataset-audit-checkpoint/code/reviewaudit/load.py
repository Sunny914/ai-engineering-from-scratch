"""Read review rows from CSV. Counts and label rules live elsewhere."""

from __future__ import annotations

import csv
from pathlib import Path

from .report import Record


class SchemaError(ValueError):
    """The CSV is missing a header, a required column, or a parseable field."""


def load_csv(path: str | Path, label_column: str) -> list[Record]:
    """Load rows. A header and no data rows returns an empty list.

    A missing file raises FileNotFoundError. A missing column or a label that
    is not an integer raises SchemaError. This function does not check whether
    the label is 0 or 1, and it does not log.
    """
    csv_path = Path(path)
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise SchemaError(f"{csv_path.name} has no header row")
        required = ("text", label_column)
        missing = [name for name in required if name not in reader.fieldnames]
        if missing:
            raise SchemaError(
                f"{csv_path.name} is missing column {', '.join(missing)}"
            )
        return [_row_to_record(row, line_no, label_column) for line_no, row in enumerate(reader, start=2)]


def _row_to_record(row: dict[str, str | None], line_no: int, label_column: str) -> Record:
    text = row.get("text")
    if text is None or text.strip() == "":
        raise SchemaError(f"line {line_no}: text is missing")
    raw_label = row.get(label_column)
    if raw_label is None or raw_label.strip() == "":
        raise SchemaError(f"line {line_no}: {label_column} is missing")
    try:
        label = int(raw_label.strip())
    except ValueError:
        raise SchemaError(f"line {line_no}: {label_column} must be an integer") from None
    return Record(text=text.strip(), label=label)
