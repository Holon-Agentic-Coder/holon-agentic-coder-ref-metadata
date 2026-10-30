---
# holon-agentic-coder-ref-metadata-0176
title: "Remove every unittest reference from holon-agentic-coder; the suite is pytest only"
status: todo
type: task
priority: high
tags:
  - tests
  - pytest
  - holon-agentic-coder
blocked_by:
  - holon-agentic-coder-ref-metadata-0168
created_at: 2026-10-28T09:38:48Z
updated_at: 2026-10-29T23:34:36Z
---

## Problem

The maintainer's rule (2026-10-28): "we rely solely on `pytest` not `unittest`" and "there should be no mention of
`unittest`". `holon-agentic-coder` main (`fbd3b35`) still mentions `unittest` in 29 tracked files:

- 59 `unittest.TestCase` classes (largest: `test_calibration.py` 30 mentions, `test_agent_runner.py` 27,
  `test_local_llm.py` 13, `test_ledger_query.py` 11).
- About 60 `unittest.mock` imports (`MagicMock`, `patch`, `from unittest import mock`).
- `unittest.main`, `unittest.skipIf`, and `python -m unittest` / `python3 -m unittest` in docs and plans
  (`apps/sandbox-executor/docs/hermetic_testing.md` and `tests/hermetic_fixtures.py` among them).

## Goal

Run through the Holon flow (intent, plan, execute, review, calibrate) after PR #99 (Bean 0168) merges, because it
touches the same test files (sequential overlapping flows). PR #99 merged as `0e54457` (2026-10-28T09:59:25Z), so the
flow can start.

1. Convert every `unittest.TestCase` class to plain pytest classes or functions: `setUp`/`tearDown` to fixtures,
   `self.assert*` to bare `assert` / `pytest.raises` / `pytest.approx`, `subTest` to `pytest.mark.parametrize` or
   pytest's `subtests`, `skipIf` to `pytest.mark.skipif`, drop `unittest.main` blocks.
2. Replace `unittest.mock` usage with pytest-native mocking. Decide in the plan between `monkeypatch` plus small fakes
   and the `pytest-mock` `mocker` fixture (one pinned dev dependency); either way no source file imports or names
   `unittest`.
3. Reword docs, comments and fixture docstrings so they state the pytest-only rule without naming `unittest`.
4. Add a hygiene or lint check that fails on any `unittest` token in tracked files (excluding the append-only ledgers
   and historical `plans/` / `executions/` records, which cannot be rewritten), so it cannot return.
5. No test weakened, skipped or deleted; test count and subtest count unchanged or higher; full suite via
   `uv run task test` and CI green.

## Notes

- Historical flow records (`holon-knowledge/ledger/*.jsonl`, `plans/P-*.md`, `executions/E-*.md`) are audited and
  append-only; they keep their existing text. The check in step 4 must exclude them.
- PR #99 itself only rewords the one `hermetic_testing.md` sentence it already touches.
