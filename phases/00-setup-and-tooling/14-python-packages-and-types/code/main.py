"""
A small review-summary package: CSV loading stays out of the calculations.
See: phases/00-setup-and-tooling/14-python-packages-and-types/docs/en.md
The demo writes a three-row CSV, loads it through auditlib, and prints a summary.
Importing this module does not run the demo.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from auditlib import Summary, load_records, summarize

SAMPLE = """text,label,score
good film,1,0.9
bad film,0,0.2
ok film,1,0.6
"""


def format_summary(summary: Summary) -> str:
    labels = ", ".join(f"{label}: {count}" for label, count in sorted(summary.label_counts.items()))
    if summary.mean_score is None:
        mean = "n/a"
    else:
        mean = f"{summary.mean_score:.6f}"
    return "\n".join(
        [
            "Python packages and type hints",
            f"records  {summary.count}",
            f"labels   {labels or '(none)'}",
            f"mean     {mean}",
        ]
    )


def run_demo() -> str:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "reviews.csv"
        path.write_text(SAMPLE, encoding="utf-8")
        summary = summarize(load_records(path))
    return format_summary(summary)


def main() -> None:
    print(run_demo())


if __name__ == "__main__":
    main()
