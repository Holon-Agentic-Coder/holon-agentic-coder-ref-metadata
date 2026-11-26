---
# holon-agentic-coder-ref-metadata-0389
title:
  "Four bean-progress tests fail on the committed harness: they still expect the table from before the column rework"
status: completed
type: bug
priority: normal
tags:
  - harness
  - tests
  - bean-progress
created_at: 2026-11-23T14:31:54Z
updated_at: 2026-11-24T11:05:50Z
---

## Problem

`uv run pytest` in the harness gives `4 failed`, all in `tests/test_bean_progress.py`, on committed code (neither the
test file nor the `bean_progress` skill has uncommitted changes):

- `TestLiveProcessesAndChecks::test_ancestor_owner_ignores_child_claude_agent_flag`
- `TestLiveProcessesAndChecks::test_table_escaping_and_empty_cli`
- `TestTimesAndColumns::test_row_columns_and_runner_in_notes`
- `TestMappingFixes::test_duplicate_attempts_merge_per_bean`

## Cause

Commits `90f751a` (Agent and Model columns), `d7139f3` (Last Activity column) and `5d75a17` (compact table, details as a
list, `--wide`) changed the output without updating the tests. The tests still expect the header
`| Bean # | Target | Title | Stage | Time in Stage | PR & CI | Total Time | Notes |` and the model in the notes cell
(`opus-5-5 · 32m (PID ...)`); the code now prints
`| Bean # | Target | Title | Agent | Model | Stage | In Stage | PR & CI | Total |` and `live · 32m (PID ...)`, with
notes moved to the list under the table.

## Goal

- The four tests assert the current compact table, the `--wide` table and the details list.
- `uv run pytest` is green in the harness; the pre-commit check runs it so a stale test cannot be committed again.

## Notes

- Found on 2026-11-23 while verifying the importer of Bean 0215. Related: Bean 0388 (stale stage in bean progress).

## Resolution

Only the tests were stale; the script matches its documented behaviour and was not changed. In
`tests/test_bean_progress.py`:

- `test_ancestor_owner_ignores_child_claude_agent_flag`: the live runner string is now
  `live · 32m (PID ..., Antigravity)` (the model moved to its own column), so the assertion expects that.
- `test_table_escaping_and_empty_cli`: notes no longer sit in the compact table. It now asserts the title is escaped in
  the compact table, the note appears in the details list, and the `--wide` table escapes both title and note.
- `test_row_columns_and_runner_in_notes`: asserts the compact header (`Agent`, `Model`, `In Stage`, `Total`), the time
  cells, the idle state in the details list, and the exact `--wide` header.
- `test_duplicate_attempts_merge_per_bean`: asserts `live · 1h00m (PID 1, Claude Code)` in the notes cell and the model
  on the row.

Result: `tests/test_bean_progress.py` 17 passed (was 4 failed, 13 passed).
