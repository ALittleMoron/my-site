---
paths:
  - "backend/**/*.py"
---

# Common backend rules

## Code Style

- line-length: 100 (ruff + black)
- ruff: ALL rules, see ignores in pyproject.toml
- mypy: strict mode (`disallow_untyped_defs = true` etc.)
- No docstrings unless interface is non-obvious from types
- Comments: only for non-obvious WHY, never WHAT