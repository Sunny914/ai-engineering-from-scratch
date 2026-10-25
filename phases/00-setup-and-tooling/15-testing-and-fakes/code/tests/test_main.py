"""Behavior tests for the review-batch checker."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.dirname(HERE)
sys.path.insert(0, CODE_DIR)

from reviewcheck import CsvReader, MemoryReader, Record, path_from_env, review_batch
import main as entry

WHEN = datetime(2026, 1, 2, tzinfo=timezone.utc)
SAMPLE = [
    Record("good film", 1, 0.9),
    Record("bad film", 0, 0.2),
    Record("ok film", 1, 0.6),
]


class BatchTests(unittest.TestCase):
    def test_known_records_report_mean_and_acceptance(self) -> None:
        report = review_batch(MemoryReader(SAMPLE), clock=lambda: WHEN)
        self.assertEqual(report.count, 3)
        self.assertAlmostEqual(report.mean_score or 0.0, 1.7 / 3)
        self.assertAlmostEqual(report.accepted_rate or 0.0, 2 / 3)
        self.assertEqual(report.checked_on, "2026-01-02")

    def test_empty_batch_has_no_mean(self) -> None:
        report = review_batch(MemoryReader([]), clock=lambda: WHEN)
        self.assertEqual(report.count, 0)
        self.assertIsNone(report.mean_score)
        self.assertIsNone(report.accepted_rate)
        self.assertEqual(report.checked_on, "2026-01-02")

    def test_score_above_one_names_the_record(self) -> None:
        source = MemoryReader([Record("too high", 1, 1.4)])
        with self.assertRaises(ValueError) as caught:
            review_batch(source, clock=lambda: WHEN)
        self.assertIn("record 1", str(caught.exception))

    def test_core_check_does_not_open_a_file(self) -> None:
        with patch("builtins.open", side_effect=AssertionError("batch opened a file")):
            report = review_batch(MemoryReader(SAMPLE), clock=lambda: WHEN)
        self.assertEqual(report.count, 3)

    def test_default_clock_can_be_replaced(self) -> None:
        class FrozenDateTime(datetime):
            @classmethod
            def now(cls, tz=None):
                return WHEN

        with patch("reviewcheck.report.datetime", FrozenDateTime):
            report = review_batch(MemoryReader([]))
        self.assertEqual(report.checked_on, "2026-01-02")


class FileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.directory = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_temporary_csv_matches_the_memory_reader(self) -> None:
        path = self.directory / "reviews.csv"
        path.write_text(entry.SAMPLE, encoding="utf-8")
        from_file = review_batch(CsvReader(path), clock=lambda: WHEN)
        from_memory = review_batch(MemoryReader(SAMPLE), clock=lambda: WHEN)
        self.assertEqual(from_file, from_memory)

    def test_missing_column_raises_for_the_temporary_file(self) -> None:
        path = self.directory / "partial.csv"
        path.write_text("text,label\nfilm,1\n", encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            CsvReader(path).read()
        self.assertIn("score", str(caught.exception))

    def test_review_csv_is_read_from_the_environment(self) -> None:
        path = self.directory / "reviews.csv"
        path.write_text(entry.SAMPLE, encoding="utf-8")
        with patch.dict(os.environ, {"REVIEW_CSV": str(path)}):
            report = review_batch(CsvReader(path_from_env()), clock=lambda: WHEN)
        self.assertEqual(report.count, 3)

    def test_blank_review_csv_raises(self) -> None:
        with patch.dict(os.environ, {"REVIEW_CSV": "  "}):
            with self.assertRaises(ValueError) as caught:
                path_from_env()
        self.assertIn("REVIEW_CSV", str(caught.exception))


class FakeTests(unittest.TestCase):
    def test_a_local_fake_satisfies_the_same_boundary(self) -> None:
        class TwoReviews:
            def read(self):
                return SAMPLE[:2]

        report = review_batch(TwoReviews(), clock=lambda: WHEN)
        self.assertEqual(report.count, 2)
        self.assertAlmostEqual(report.mean_score or 0.0, 0.55)


if __name__ == "__main__":
    unittest.main()
