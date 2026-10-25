"""Behavior tests for audit settings, validation, and safe logs."""

from __future__ import annotations

import io
import logging
import os
import sys
import unittest
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(HERE)
sys.path.insert(0, CODE_DIR)

from datasetaudit import (
    AuditConfig,
    AuditError,
    ConfigError,
    audit_rows,
    configure_logging,
    load_config,
)

TOKEN = "sk-test-secret-9000"
ROWS = (
    {"text": "good film", "label": "1"},
    {"text": "bad film", "label": "0"},
    {"text": "ok film", "label": "1"},
)


def capture_logger(level: str = "INFO") -> tuple[logging.Logger, io.StringIO]:
    buffer = io.StringIO()
    logger = logging.getLogger(f"datasetaudit.test.{id(buffer)}")
    logger.handlers.clear()
    logger.setLevel(level)
    logger.propagate = False
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger, buffer


class ConfigTests(unittest.TestCase):
    def test_empty_environment_uses_defaults(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            config = load_config()
        self.assertEqual(config, AuditConfig(min_rows=1, label_column="label", log_level="INFO"))

    def test_environment_overrides_are_parsed(self) -> None:
        with patch.dict(
            os.environ,
            {
                "AUDIT_MIN_ROWS": "4",
                "AUDIT_LABEL_COLUMN": "topic",
                "AUDIT_LOG_LEVEL": "warning",
            },
            clear=True,
        ):
            config = load_config()
        self.assertEqual(config, AuditConfig(min_rows=4, label_column="topic", log_level="WARNING"))

    def test_malformed_min_rows_names_the_variable(self) -> None:
        with patch.dict(os.environ, {"AUDIT_MIN_ROWS": "ten", "AUDIT_API_TOKEN": TOKEN}, clear=True):
            with self.assertRaises(ConfigError) as caught:
                load_config()
        message = str(caught.exception)
        self.assertIn("AUDIT_MIN_ROWS", message)
        self.assertIn("integer", message)
        self.assertNotIn(TOKEN, message)

    def test_zero_min_rows_violates_the_lower_bound(self) -> None:
        with patch.dict(os.environ, {"AUDIT_MIN_ROWS": "0"}, clear=True):
            with self.assertRaises(ConfigError) as caught:
                load_config()
        self.assertIn("at least 1", str(caught.exception))

    def test_blank_override_keeps_the_default(self) -> None:
        with patch.dict(os.environ, {"AUDIT_MIN_ROWS": "  "}, clear=True):
            config = load_config()
        self.assertEqual(config.min_rows, 1)


class AuditTests(unittest.TestCase):
    def test_validated_config_rejects_a_short_batch(self) -> None:
        logger, buffer = capture_logger()
        config = AuditConfig(min_rows=3, label_column="label", log_level="INFO")
        with self.assertRaises(AuditError) as caught:
            audit_rows(ROWS[:2], config, logger)
        self.assertIn("at least 3", str(caught.exception))
        self.assertIn("min_rows=3", buffer.getvalue())
        self.assertNotIn("good film", buffer.getvalue())

    def test_validated_config_keeps_a_large_enough_batch(self) -> None:
        logger, buffer = capture_logger()
        config = AuditConfig(min_rows=2, label_column="label", log_level="INFO")
        result = audit_rows(ROWS, config, logger)
        self.assertEqual(result.kept, 3)
        self.assertEqual(result.label_counts, {"1": 2, "0": 1})
        self.assertIn("rows=3", buffer.getvalue())

    def test_logs_omit_a_secret_left_in_the_environment(self) -> None:
        logger, buffer = capture_logger()
        with patch.dict(os.environ, {"AUDIT_API_TOKEN": TOKEN}, clear=True):
            config = load_config()
            result = audit_rows(ROWS, config, logger)
        text = buffer.getvalue()
        self.assertEqual(result.kept, 3)
        self.assertNotIn(TOKEN, text)
        self.assertNotIn("AUDIT_API_TOKEN", text)

    def test_info_line_is_hidden_when_the_level_is_error(self) -> None:
        logger, buffer = capture_logger("ERROR")
        config = AuditConfig(min_rows=1, label_column="label", log_level="ERROR")
        audit_rows(ROWS, config, logger)
        self.assertNotIn("audit kept", buffer.getvalue())

    def test_configure_logging_uses_the_config_level(self) -> None:
        config = AuditConfig(min_rows=1, label_column="label", log_level="WARNING")
        logger = configure_logging(config, name="datasetaudit.levelcheck")
        self.assertEqual(logger.level, logging.WARNING)
        self.assertTrue(logger.handlers)


if __name__ == "__main__":
    unittest.main()
