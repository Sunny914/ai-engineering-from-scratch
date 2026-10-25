"""Pure summaries of review records. This module does not read files."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    text: str
    label: int
    score: float


@dataclass(frozen=True)
class Summary:
    count: int
    label_counts: dict[int, int]
    mean_score: float | None


def summarize(records: Sequence[Record]) -> Summary:
    """Count labels and average scores. An empty sequence is a valid summary."""
    if not records:
        return Summary(count=0, label_counts={}, mean_score=None)
    label_counts: dict[int, int] = {}
    total = 0.0
    for record in records:
        label_counts[record.label] = label_counts.get(record.label, 0) + 1
        total += record.score
    return Summary(
        count=len(records),
        label_counts=label_counts,
        mean_score=total / len(records),
    )
