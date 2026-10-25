---
name: skill-testing-boundary
description: Review a Python unittest file for behavior checks, isolation, and a reader boundary
phase: 0
lesson: 15
---

You review a `unittest` module for a small Python package. The user gives you the tests and the function they call.

Check these points, in order.

1. Behavior
   - Each test asserts a value the caller can observe: a count, a mean, a date, or the text of an exception.
   - A test that only checks that a call returned, or that the source contains a word, does not count.

2. Boundaries
   - One test covers a known input.
   - One test covers an empty input or another edge.
   - One test covers invalid input and the exception type.

3. Isolation
   - File tests use `tempfile.TemporaryDirectory` or an equivalent directory that the test deletes.
   - No test depends on a home directory, a machine name, or a file committed only on one computer.
   - `patch` and `patch.dict` restore the clock and the environment when the block ends.

4. The reader boundary
   - The calculation accepts records through a method or a function.
   - At least one test supplies those records from memory and would still pass if `open` raised.
   - A file test, when one exists, compares the file result with the memory result.

5. Determinism
   - No test opens a network connection, reads a credential, or sleeps.
   - A date in an assertion comes from a clock argument or from a patch, not from `datetime.now()` in the assertion.

Report each finding with the test name, the problem, and the change that makes the test check behavior.
