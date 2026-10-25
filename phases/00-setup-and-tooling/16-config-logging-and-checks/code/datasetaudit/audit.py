"""Apply a validated audit config to in-memory rows."""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .config import AuditConfig


class AuditError(Exception):
    """The rows failed a check. The configuration itself was valid."""


@dataclass(frozen=True)
class AuditResult:
    kept: int
    label_counts: dict[str, int]


def audit_rows(
    rows: Sequence[Mapping[str, str]],
    config: AuditConfig,
    logger: logging.Logger | None = None,
) -> AuditResult:
    """Count labels when the batch is large enough and every row has the label column.

    Logs counts and the column name. Does not log row text or any other setting.
    """
    log = logger if logger is not None else logging.getLogger("datasetaudit")
    if len(rows) < config.min_rows:
        log.warning(
            "audit rejected rows=%s min_rows=%s label_column=%s",
            len(rows),
            config.min_rows,
            config.label_column,
        )
        raise AuditError(f"need at least {config.min_rows} rows, got {len(rows)}")
    counts: dict[str, int] = {}
    for index, row in enumerate(rows, start=1):
        if config.label_column not in row:
            log.warning(
                "audit rejected row=%s missing_column=%s",
                index,
                config.label_column,
            )
            raise AuditError(f"row {index} is missing column {config.label_column}")
        label = row[config.label_column]
        counts[label] = counts.get(label, 0) + 1
    log.info(
        "audit kept rows=%s label_column=%s min_rows=%s",
        len(rows),
        config.label_column,
        config.min_rows,
    )
    return AuditResult(kept=len(rows), label_counts=counts)
