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
updated_at: 2026-11-26T13:41:00Z
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

## Further evidence (PR #332, bean 0511, scrapped as a duplicate)

Batch 2 of bean 0405 (flow `tests-fewer-git-stage-pipeline`) hit the same defect with a different file set: when
`apps/sandbox-executor/tests/flow/stages/test_replan_request.py` is listed after a parent-directory file that follows
other `stages/` files (for example `stages/test_children.py flow/test_git_refs.py stages/test_replan_request.py`), its
eight cases error with "fixture 'no_origin_reconcile' not found", serially and under xdist. Listing the `stages/` files
contiguously, or a full-directory run, passes. The same order dependence (a fixture visible only to some argument
orders) points to conftest discovery as the cause, so the fix should cover both fixtures.

## Next step

Bisect the file list to the pair that triggers it (conftest discovery order or a module that imports a test module and
shadows `tests.flow`), then fix it in the Holon flow.

## Flow

Launched 2026-11-26 as flow `flow-fixtures-any-test-file` (claude-agent, claude-opus-5-5), worktree
`flow-flow-fixtures-any-test-file`, log `todo/flow-flow-fixtures-any-test-file.log`. Intent scope: the three conftest
files plus one new regression test. The slug was truncated to 32 characters (Bean 0426).

**Parked 2026-11-26T13:39Z:** Stage 3 refused the flow: the touch set overlaps the waiting
`single-runner-per-checkpoint` flow on `apps/sandbox-executor/tests/conftest.py`. Intent kept as
`todo/intent-0491-flow-fixtures-any-test-file-subset.json`; relaunch (checkpoint resume) once that flow merges. See Bean
0519 for the vanishing worktree after a refusal.
