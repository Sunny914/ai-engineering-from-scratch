"""
Audit the checked-in review CSV and print the label counts.
See: phases/00-setup-and-tooling/17-dataset-audit-checkpoint/docs/en.md
The demo passes an empty environment so the sample does not depend on the shell.
Importing this module does not run the demo.
"""

from __future__ import annotations

import sys
from pathlib import Path

from reviewaudit import check_records, configure_logging, format_summary, load_config, load_csv

SAMPLE_PATH = Path(__file__).resolve().parent / "fixtures" / "reviews.csv"


def run_demo() -> str:
    config = load_config({})
    logger = configure_logging(config, name="reviewaudit.demo", stream=sys.stdout)
    records = load_csv(SAMPLE_PATH, config.label_column)
    summary = check_records(records, config, logger)
    return format_summary(summary)


def main() -> None:
    print(run_demo(), end="")


if __name__ == "__main__":
    main()
