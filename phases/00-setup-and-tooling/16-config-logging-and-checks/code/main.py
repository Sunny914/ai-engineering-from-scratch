"""
Load default audit settings, check three in-memory rows, and log the result.
See: phases/00-setup-and-tooling/16-config-logging-and-checks/docs/en.md
The demo passes an empty environment so the sample does not depend on the shell.
Importing this module does not run the demo.
"""

from __future__ import annotations

import sys

from datasetaudit import audit_rows, configure_logging, load_config

SAMPLE_ROWS = (
    {"text": "good film", "label": "1"},
    {"text": "bad film", "label": "0"},
    {"text": "ok film", "label": "1"},
)


def run_demo() -> str:
    config = load_config({})
    logger = configure_logging(config, name="datasetaudit.demo", stream=sys.stdout)
    result = audit_rows(SAMPLE_ROWS, config, logger)
    return f"Dataset audit kept {result.kept} rows"


def main() -> None:
    print(run_demo())


if __name__ == "__main__":
    main()
