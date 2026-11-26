---
# holon-agentic-coder-ref-metadata-0491
title: "Running a subset of unit test files loses the flow_repos fixture"
status: todo
type: bug
priority: normal
tags:
  - tests
  - holon-agentic-coder
created_at: 2026-11-26T07:10:00Z
updated_at: 2026-11-26T07:10:00Z
---

## Problem

Found in the test suite audit of 2026-11-26 (main `412bed21`). Running the 20 files listed in
`todo/test-suite-audit-2026-11-26/serial-top20-files.txt` together (serially with `-p no:xdist` or with `-n 6`) gives
`fixture 'flow_repos' not found` for 48 tests (`tests/flow/stages/test_children.py`, `test_plan_decision.py`,
`test_plan_resume_adopts_branch.py`, `test_integration.py` and `tests/flow/test_git_refs.py`) and 5 failures in
`tests/flow/review/test_conflict_gate.py` and `tests/flow/test_pipeline.py`. Each file alone passes, and so does the
full unit selection. Logs: `todo/test-suite-audit-2026-11-26/serial-top20-rerun.log`, `gitphase-run.log`.

## Why it matters

Flows that re-measure only their in-scope files (every test-speed intent) hit false failures, and the order dependence
it reveals (bean 0386) can hide a real one.

## Next step

Bisect the file list to the pair that triggers it (conftest discovery order or a module that imports a test module and
shadows `tests.flow`), then fix it in the Holon flow.
