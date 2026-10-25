"""Behavior tests for the dataset-audit checkpoint."""

from __future__ import annotations

import io
import logging
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(HERE)
sys.path.insert(0, CODE_DIR)

from reviewaudit import (
    AuditConfig,
    CheckError,
    ConfigError,
    Record,
    SchemaError,
    Summary,
    check_records,
    load_config,
    load_csv,
    summarize,
)

FIXTURE = Path(CODE_DIR) / "fixtures" / "reviews.csv"
TOKEN = "sk-test-secret-9000"
SAMPLE = (
    Record("good film", 1),
    Record("bad film", 0),
    Record("ok film", 1),
)


def capture_logger(level: str = "INFO") -> tuple[logging.Logger, io.StringIO]:
    buffer = io.StringIO()
    logger = logging.getLogger(f"reviewaudit.test.{id(buffer)}")
    logger.handlers.clear()
    logger.setLevel(level)
    logger.propagate = False
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger, buffer


class SampleTests(unittest.TestCase):
    def test_checked_in_fixture_matches_the_known_counts(self) -> None:
        logger, buffer = capture_logger()
        records = load_csv(FIXTURE, "label")
        summary = check_records(records, AuditConfig(), logger)
        self.assertEqual(records, list(SAMPLE))
        self.assertEqual(summary, Summary(count=3, label_0=1, label_1=2))
        self.assertIn("rows=3", buffer.getvalue())
        self.assertNotIn("good film", buffer.getvalue())

    def test_memory_records_match_a_temporary_csv(self) -> None:
        logger, _buffer = capture_logger()
        config = AuditConfig()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reviews.csv"
            path.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
            from_file = check_records(load_csv(path, "label"), config, logger)
        from_memory = check_records(SAMPLE, config, logger)
        self.assertEqual(from_file, from_memory)

    def test_empty_summary_is_zero_and_the_audit_rejects_it(self) -> None:
        logger, buffer = capture_logger()
        self.assertEqual(summarize([]), Summary(count=0, label_0=0, label_1=0))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.csv"
            path.write_text("text,label\n", encoding="utf-8")
            records = load_csv(path, "label")
        self.assertEqual(records, [])
        with self.assertRaises(CheckError) as caught:
            check_records(records, AuditConfig(), logger)
        self.assertIn("at least 1", str(caught.exception))
        self.assertIn("got 0", str(caught.exception))
        self.assertIn("min_rows=1", buffer.getvalue())


class FailureTests(unittest.TestCase):
    def test_missing_label_column_names_the_column(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reviews.csv"
            path.write_text("text,score\ngood film,0.9\n", encoding="utf-8")
            with self.assertRaises(SchemaError) as caught:
                load_csv(path, "label")
        self.assertIn("missing column label", str(caught.exception))
        self.assertNotIn("good film", str(caught.exception))

    def test_label_two_is_rejected(self) -> None:
        logger, buffer = capture_logger()
        records = (Record("good film", 1), Record("bad film", 2))
        with self.assertRaises(CheckError) as caught:
            check_records(records, AuditConfig(), logger)
        message = str(caught.exception)
        self.assertIn("record 2", message)
        self.assertIn("must be 0 or 1", message)
        self.assertIn("got 2", message)
        self.assertNotIn("bad film", buffer.getvalue())

    def test_min_rows_override_rejects_the_small_sample(self) -> None:
        logger, buffer = capture_logger()
        with patch.dict(os.environ, {"AUDIT_MIN_ROWS": "10000", "AUDIT_API_TOKEN": TOKEN}, clear=True):
            config = load_config()
            with self.assertRaises(CheckError) as caught:
                check_records(SAMPLE, config, logger)
        self.assertEqual(config.min_rows, 10000)
        self.assertIn("at least 10000", str(caught.exception))
        self.assertIn("got 3", str(caught.exception))
        self.assertNotIn(TOKEN, buffer.getvalue())
        self.assertNotIn(TOKEN, str(caught.exception))


class ConfigTests(unittest.TestCase):
    def test_empty_environment_uses_defaults(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            config = load_config()
        self.assertEqual(config, AuditConfig(min_rows=1, label_column="label", log_level="INFO"))

    def test_environment_overrides_select_the_label_column(self) -> None:
        logger, _buffer = capture_logger()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reviews.csv"
            path.write_text("text,topic\ngood film,1\nbad film,0\nok film,1\n", encoding="utf-8")
            with patch.dict(
                os.environ,
                {"AUDIT_MIN_ROWS": "3", "AUDIT_LABEL_COLUMN": "topic", "AUDIT_LOG_LEVEL": "warning"},
                clear=True,
            ):
                config = load_config()
                summary = check_records(load_csv(path, config.label_column), config, logger)
        self.assertEqual(config, AuditConfig(min_rows=3, label_column="topic", log_level="WARNING"))
        self.assertEqual(summary, Summary(count=3, label_0=1, label_1=2))

    def test_malformed_min_rows_omits_a_neighboring_token(self) -> None:
        with patch.dict(os.environ, {"AUDIT_MIN_ROWS": "ten", "AUDIT_API_TOKEN": TOKEN}, clear=True):
            with self.assertRaises(ConfigError) as caught:
                load_config()
        message = str(caught.exception)
        self.assertIn("AUDIT_MIN_ROWS", message)
        self.assertIn("integer", message)
        self.assertNotIn(TOKEN, message)

    def test_importing_main_prints_nothing(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-c", "import main"],
            cwd=CODE_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(completed.stderr, "")


if __name__ == "__main__":
    unittest.main()
