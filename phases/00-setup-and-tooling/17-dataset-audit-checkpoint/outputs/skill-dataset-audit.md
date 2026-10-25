---
name: skill-dataset-audit
description: Review a small dataset-audit package for module boundaries, checks, and safe logs
phase: 0
lesson: 17
---

You review a Python package that audits a small CSV. The user gives you the modules, one fixture or sample, and the tests.

Check these points, in order.

1. Boundaries
   - Loading a CSV, checking labels, counting, reading configuration, and creating a logger are separate.
   - The summary function does not open a file.
   - The loader does not decide whether a label of 2 is legal.
   - Importing the entry point does not run the demo.

2. Configuration
   - Defaults exist for the minimum row count, the label column, and the log level.
   - Environment values are parsed.
   - An invalid value raises `ConfigError` (or the module's equivalent) and names the variable.
   - The message does not dump the environment.

3. The dataset
   - A missing label column raises a schema error that names the column.
   - A label of 2 raises a check error that names the record.
   - A minimum larger than the file raises that same check error and reports both sizes.
   - The success summary states the row count and the counts of labels 0 and 1.

4. Logs
   - A success line contains counts, not row text.
   - A token left in the environment does not appear in the log or in an unrelated error.
   - There is no bare `except` and no `except Exception` whose job is to print a success summary anyway.

5. Tests
   - One test asserts the known sample counts.
   - One test uses a temporary directory or an in-memory list and does not edit the shared fixture.
   - `patch.dict` covers a default and an override such as `AUDIT_MIN_ROWS=10000`.

Report each finding with the module or test name, the problem, and the change that removes it. Do not ask the package to import Ruff, mypy, or pytest. Do not treat a passing sample as proof that the program is ready for production.
