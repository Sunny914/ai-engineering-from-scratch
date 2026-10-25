"""Tests for the review-summary package."""

from __future__ import annotations

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

from auditlib import Record, Summary, load_records, summarize
import main as entry


def write_csv(directory: Path, name: str, text: str) -> Path:
    path = directory / name
    path.write_text(text, encoding="utf-8")
    return path


class SummaryTests(unittest.TestCase):
    def test_known_records_have_counts_and_mean(self) -> None:
        records = [
            Record("good film", 1, 0.9),
            Record("bad film", 0, 0.2),
            Record("ok film", 1, 0.6),
        ]
        summary = summarize(records)
        self.assertEqual(summary.count, 3)
        self.assertEqual(summary.label_counts, {1: 2, 0: 1})
        self.assertAlmostEqual(summary.mean_score or 0.0, 1.7 / 3)

    def test_empty_sequence_is_a_summary_with_no_mean(self) -> None:
        summary = summarize([])
        self.assertEqual(summary, Summary(count=0, label_counts={}, mean_score=None))

    def test_summarize_does_not_open_a_file(self) -> None:
        records = [Record("good film", 1, 0.9)]
        with patch("builtins.open", side_effect=AssertionError("calculation opened a file")):
            summary = summarize(records)
        self.assertEqual(summary.count, 1)
        self.assertEqual(summary.mean_score, 0.9)


class LoaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.directory = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_sample_file_matches_the_known_summary(self) -> None:
        path = write_csv(self.directory, "reviews.csv", entry.SAMPLE)
        summary = summarize(load_records(path))
        self.assertEqual(summary.count, 3)
        self.assertEqual(summary.label_counts[1], 2)
        self.assertAlmostEqual(summary.mean_score or 0.0, 1.7 / 3)

    def test_header_only_file_loads_no_records(self) -> None:
        path = write_csv(self.directory, "empty.csv", "text,label,score\n")
        self.assertEqual(load_records(path), [])
        self.assertEqual(summarize(load_records(path)).mean_score, None)

    def test_missing_column_names_the_file(self) -> None:
        path = write_csv(self.directory, "partial.csv", "text,label\nfilm,1\n")
        with self.assertRaises(ValueError) as caught:
            load_records(path)
        self.assertIn("score", str(caught.exception))
        self.assertIn("partial.csv", str(caught.exception))

    def test_bad_score_names_the_line(self) -> None:
        path = write_csv(
            self.directory,
            "bad.csv",
            "text,label,score\ngood film,1,0.9\nbad film,0,high\n",
        )
        with self.assertRaises(ValueError) as caught:
            load_records(path)
        self.assertIn("line 3", str(caught.exception))

    def test_missing_file_raises_before_a_summary(self) -> None:
        missing = self.directory / "absent.csv"
        with self.assertRaises(FileNotFoundError):
            load_records(missing)


class PackageTests(unittest.TestCase):
    def test_public_import_is_the_calculation_and_the_loader(self) -> None:
        import auditlib

        self.assertIs(auditlib.summarize, summarize)
        self.assertIs(auditlib.load_records, load_records)
        self.assertFalse(hasattr(auditlib, "_row_to_record"))
        self.assertFalse(hasattr(auditlib, "SAMPLE"))

    def test_importing_the_entry_point_does_not_run_the_demo(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-c", "import main"],
            cwd=CODE_DIR,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, "")
        self.assertEqual(completed.stderr, "")


if __name__ == "__main__":
    unittest.main()
