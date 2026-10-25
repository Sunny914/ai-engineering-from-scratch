"""Check a batch of review records. The source is someone else's job."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone

from .records import Report
from .source import RecordSource


def review_batch(
    source: RecordSource,
    clock: Callable[[], datetime] | None = None,
) -> Report:
    """Validate records from source and summarize them.

    An empty batch is valid. A label other than 0 or 1, or a score outside
    0 to 1, raises ValueError. Pass clock to make the date repeatable.
    """
    records = list(source.read())
    for index, record in enumerate(records, start=1):
        if record.label not in (0, 1):
            raise ValueError(f"record {index}: label must be 0 or 1, got {record.label}")
        if record.score != record.score or not 0.0 <= record.score <= 1.0:
            raise ValueError(
                f"record {index}: score must be from 0 to 1, got {record.score}"
            )
    checked = datetime.now(timezone.utc) if clock is None else clock()
    if checked.tzinfo is None:
        raise ValueError("clock must return a timezone-aware datetime")
    if not records:
        return Report(
            count=0,
            mean_score=None,
            accepted_rate=None,
            checked_on=checked.date().isoformat(),
        )
    accepted = sum(record.label == 1 for record in records)
    total = sum(record.score for record in records)
    return Report(
        count=len(records),
        mean_score=total / len(records),
        accepted_rate=accepted / len(records),
        checked_on=checked.date().isoformat(),
    )
