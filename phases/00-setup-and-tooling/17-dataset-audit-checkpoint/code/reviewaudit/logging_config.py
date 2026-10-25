"""Attach one log handler. Messages stay in the caller, not in this module."""

from __future__ import annotations

import logging
import sys
from typing import TextIO

from .config import AuditConfig


def configure_logging(
    config: AuditConfig,
    name: str = "reviewaudit",
    stream: TextIO | None = None,
) -> logging.Logger:
    """Set the logger level from config. The default stream is stderr."""
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(config.log_level)
    logger.propagate = False
    handler = logging.StreamHandler(stream if stream is not None else sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    logger.addHandler(handler)
    return logger
