---
# holon-agentic-coder-ref-metadata-0498
title:
  "A unit test measures the live tree against the live budget file, so it duplicates the hygiene gate in three jobs and
  fails every open PR after a budget merge"
status: todo
type: bug
priority: high
tags:
  - tests
  - ci
  - module-budgets
  - holon-agentic-coder
created_at: 2026-11-26T08:55:00Z
updated_at: 2026-11-26T08:55:00Z
---

## Evidence

Self-improvement audit 2026-11-26. PR #317 merged at 07:50:13Z (discovery-based budgets for all packages). Within 1 to
13 min the pipelines of the open PRs #320, #321 and #323 failed in `Test - Unit`, `Test - Stress` and `Test - Hygiene`
at 07:50:57Z, 07:52:52Z and 07:52:54Z. For #320 and #321 the unit failure is
`apps/sandbox-executor/tests/flow/test_module_budgets.py::test_the_live_configuration_passes_against_the_real_tree`
(`assert 1 == 0`) on ubuntu and macOS, so a check the hygiene job already runs (`scripts/check_module_budgets.py`) fails
again inside the unit selection, which runs in unit ubuntu, unit macOS and the Workspace survival child. #320 and #321
were re-approved at 08:13Z and 08:12Z after their approvals at 07:05Z and 07:06Z, so one merge cost them about 1 h of
rework each (see 0493/0494 for the approval side).

## Problem

A unit test that reads the repository's real tree and real configuration is not a unit test: its result depends on every
other open change, and it repeats a gate that already exists. Any module that grows by a line on a branch, or any main
merge that tightens a limit, fails 3 jobs (about 3 + 6 + 5 min of runner time) for one cause.

## Proposed change

Run the budget script against a synthetic tree in the unit test (keep that), and drop the real-tree case from the unit
selection; hygiene remains the one gate on the real tree. Add a rule to the test standards: a unit test never asserts a
property of the live checkout.

## Expected gain and cost

Removes 3 duplicate failing jobs per budget-tightening merge per open PR (here 3 PRs, 9 jobs). Cost: one test deleted or
rewritten; no coverage lost because hygiene runs the same script on every PR.
