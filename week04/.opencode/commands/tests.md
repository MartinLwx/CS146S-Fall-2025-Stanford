---
description: Run tests with coverage
agent: build
subtask: true
---

Run the tests with `PYTHONPATH=. uv run pytest -q backend/tests --maxfail=1 -x` and, if gree, run coverage

Summarize failures and suggest next steps.
