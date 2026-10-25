---
name: skill-package-boundary
description: Review a small Python project for a public package boundary and a quiet import
phase: 0
lesson: 14
---

You review a small Python project that should be importable without running its demo. The user gives you a package directory and the file they run from the command line.

Check these points, in order.

1. Responsibilities
   - Calculations accept values. They do not open files, sockets, or environment variables.
   - One module owns each external read. Other modules call that function.

2. Public surface
   - `__init__.py` exports the names callers need.
   - Names that start with `_` are absent from that list.
   - Call sites outside the package import the package, not a helper from a submodule.

3. Types
   - Each exported function annotates its parameters and its return.
   - A dataclass used as a record is frozen when callers must not change it later.

4. Import behavior
   - The command-line file calls its demo only under `if __name__ == "__main__"`.
   - `import` of the package prints nothing and does not require a data file to exist.

5. Failures
   - Invalid rows raise `ValueError` and name the line.
   - A missing path raises `FileNotFoundError`.
   - `except` names the exception type.

Report each finding with the file, the problem, and the change that restores the boundary.
