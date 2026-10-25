"""Summary counts for records that already passed the checks."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    text: str
    label: int


@dataclass(frozen=True)
class Summary:
    count: int
    label_0: int
    label_1: int


def summarize(records: Sequence[Record]) -> Summary:
    """Count labels 0 and 1. An empty sequence is a valid summary of nothing."""
    zeros = 0
    ones = 0
    for record in records:
        if record.label == 0:
            zeros += 1
        elif record.label == 1:
            ones += 1
        else:
            raise ValueError("summary expects every label to be 0 or 1")
    return Summary(count=len(records), label_0=zeros, label_1=ones)


def format_summary(summary: Summary) -> str:
    """Return the three-line report a person reads after a successful audit."""
    return (
        f"rows      {summary.count}\n"
        f"label 0   {summary.label_0}\n"
        f"label 1   {summary.label_1}\n"
    )
