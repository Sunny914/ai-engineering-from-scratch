"""Records and the report a review batch returns."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Record:
    text: str
    label: int
    score: float


@dataclass(frozen=True)
class Report:
    count: int
    mean_score: float | None
    accepted_rate: float | None
    checked_on: str
