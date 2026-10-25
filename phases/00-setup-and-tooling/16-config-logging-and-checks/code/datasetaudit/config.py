"""Load a small audit configuration from defaults and environment strings."""

from __future__ import annotations

import logging
import os
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TextIO

MIN_ROWS_ENV = "AUDIT_MIN_ROWS"
LABEL_ENV = "AUDIT_LABEL_COLUMN"
LEVEL_ENV = "AUDIT_LOG_LEVEL"
LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")
DEFAULT_MIN_ROWS = 1
DEFAULT_LABEL = "label"
DEFAULT_LEVEL = "INFO"


class ConfigError(ValueError):
    """The audit settings are invalid. The message names the variable and the rule."""


@dataclass(frozen=True)
class AuditConfig:
    min_rows: int = DEFAULT_MIN_ROWS
    label_column: str = DEFAULT_LABEL
    log_level: str = DEFAULT_LEVEL


def load_config(environ: Mapping[str, str] | None = None) -> AuditConfig:
    """Build a config from environ. None reads os.environ. Blank values use defaults."""
    env = os.environ if environ is None else environ
    return AuditConfig(
        min_rows=_parse_min_rows(_blank_as_missing(env, MIN_ROWS_ENV)),
        label_column=_parse_label(_blank_as_missing(env, LABEL_ENV)),
        log_level=_parse_level(_blank_as_missing(env, LEVEL_ENV)),
    )


def configure_logging(
    config: AuditConfig,
    name: str = "datasetaudit",
    stream: TextIO | None = None,
) -> logging.Logger:
    """Attach one handler to name and set its level from config.

    The default stream is stderr. The demo passes stdout so the log line and
    the summary stay in order when both are captured together.
    """
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(config.log_level)
    logger.propagate = False
    handler = logging.StreamHandler(stream if stream is not None else sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    logger.addHandler(handler)
    return logger


def _blank_as_missing(env: Mapping[str, str], name: str) -> str | None:
    raw = env.get(name)
    if raw is None:
        return None
    stripped = raw.strip()
    if stripped == "":
        return None
    return stripped


def _parse_min_rows(raw: str | None) -> int:
    if raw is None:
        return DEFAULT_MIN_ROWS
    try:
        value = int(raw)
    except ValueError:
        raise ConfigError(f"{MIN_ROWS_ENV} must be an integer with no decimal point") from None
    if value < 1:
        raise ConfigError(f"{MIN_ROWS_ENV} must be at least 1")
    return value


def _parse_label(raw: str | None) -> str:
    if raw is None:
        return DEFAULT_LABEL
    if not raw.isidentifier():
        raise ConfigError(f"{LABEL_ENV} must be an identifier such as label")
    return raw


def _parse_level(raw: str | None) -> str:
    if raw is None:
        return DEFAULT_LEVEL
    level = raw.upper()
    if level not in LOG_LEVELS:
        allowed = ", ".join(LOG_LEVELS)
        raise ConfigError(f"{LEVEL_ENV} must be one of {allowed}")
    return level
