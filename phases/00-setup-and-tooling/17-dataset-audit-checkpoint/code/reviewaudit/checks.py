"""Apply the row-count and binary-label rules, then summarize."""

from __future__ import annotations

import logging
from collections.abc import Sequence

from .config import AuditConfig
from .report import Record, Summary, summarize


class CheckError(Exception):
    """The records failed a rule. The configuration itself was valid."""


def check_records(
    records: Sequence[Record],
    config: AuditConfig,
    logger: logging.Logger | None = None,
) -> Summary:
    """Reject a short batch or a label other than 0 or 1, then count.

    Logs the row count and the label counts. Does not log row text.
    """
    log = logger if logger is not None else logging.getLogger("reviewaudit")
    if len(records) < config.min_rows:
        log.warning(
            "audit rejected rows=%s min_rows=%s label_column=%s",
            len(records),
            config.min_rows,
            config.label_column,
        )
        raise CheckError(f"need at least {config.min_rows} rows, got {len(records)}")
    for index, record in enumerate(records, start=1):
        if record.label not in (0, 1):
            log.warning(
                "audit rejected record=%s label_column=%s",
                index,
                config.label_column,
            )
            raise CheckError(
                f"record {index}: {config.label_column} must be 0 or 1, got {record.label}"
            )
    summary = summarize(records)
    log.info(
        "audit kept rows=%s label_0=%s label_1=%s min_rows=%s",
        summary.count,
        summary.label_0,
        summary.label_1,
        config.min_rows,
    )
    return summary
