---
name: skill-config-and-logs
description: Review a small Python config loader for parsing, validation, and safe logs
phase: 0
lesson: 16
---

You review a Python module that loads a few settings and logs a decision. The user gives you the loader, the function that uses the settings, and one test.

Check these points, in order.

1. Defaults
   - Ordinary settings have an explicit default.
   - A missing variable and a blank value both use that default.
   - The function that does the work receives the typed settings, not `os.environ`.

2. Parsing
   - An integer setting is parsed with a dedicated check.
   - A non-integer raises a `ConfigError` (or the module's equivalent), not an uncaught `ValueError` from `int`.
   - A value that parses but breaks a rule, such as a minimum below 1, raises the same error type.
   - The message names the variable and the rule.

3. Secrets
   - The error text does not include unrelated environment values.
   - Log lines do not include tokens, passwords, row text, or a dump of the environment.
   - Unknown variables are ignored rather than copied into the config object.

4. Failures
   - An expected data failure has its own exception and is allowed to propagate.
   - There is no bare `except`.
   - There is no `except Exception` whose only job is to continue.

5. Tests
   - `patch.dict` or an explicit mapping covers a default, a valid override, and an invalid value.
   - One test asserts that a planted secret is absent from the log or the error.
   - One test shows the core function using the parsed value, not the raw string.

Report each finding with the function name, the problem, and the change that removes it. Do not ask the module to import Ruff, mypy, or pytest.
