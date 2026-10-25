"""
Check a review CSV through a reader, then print a deterministic report.
See: phases/00-setup-and-tooling/15-testing-and-fakes/docs/en.md
The demo writes a temporary file, reads it with CsvReader, and passes a fixed clock.
Importing this module does not run the demo.
"""

from __future__ import annotations

import tempfile
from datetime import datetime, timezone
from pathlib import Path

from reviewcheck import CsvReader, Report, review_batch

SAMPLE = """text,label,score
good film,1,0.9
bad film,0,0.2
ok film,1,0.6
"""

FIXED_CLOCK = datetime(2026, 1, 2, tzinfo=timezone.utc)


def format_report(report: Report) -> str:
    if report.mean_score is None:
        mean = "n/a"
    else:
        mean = f"{report.mean_score:.6f}"
    if report.accepted_rate is None:
        accepted = "n/a"
    else:
        accepted = f"{report.accepted_rate:.6f}"
    return "\n".join(
        [
            "Testing with fakes",
            f"records   {report.count}",
            f"mean      {mean}",
            f"accepted  {accepted}",
            f"checked   {report.checked_on}",
        ]
    )


def run_demo() -> str:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "reviews.csv"
        path.write_text(SAMPLE, encoding="utf-8")
        report = review_batch(CsvReader(path), clock=lambda: FIXED_CLOCK)
    return format_report(report)


def main() -> None:
    print(run_demo())


if __name__ == "__main__":
    main()
