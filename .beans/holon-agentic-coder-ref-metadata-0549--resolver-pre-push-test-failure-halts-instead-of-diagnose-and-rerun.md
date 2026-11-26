---
# holon-agentic-coder-ref-metadata-0549
title: "Failed tests: record in the ledger, diagnose, fix and re-run in a loop until they pass"
status: todo
type: feature
priority: high
tags:
  - flow
  - review-loop
  - executor
  - tests
  - ledger
  - holon-agentic-coder
created_at: 2026-11-26T22:27:00Z
updated_at: 2026-11-27T00:10:00Z
---

## Instruction (maintainer, 2026-11-27)

"Make a bean so for failed tests you record it in the ledger, diagnose the issue, rerun the tests -> diagnose/fix loop
until the tests pass." Earlier: "Shouldn't you diagnose why the tests fail and rerun the tests?" and "Every single
failure you produce is valuable information."

## Problem

When a test run inside a flow fails (the Stage 3 executor's run, or the Stage 4 resolver's pre-push run), the engine
marks the turn failed and halts the flow (`Resolver pre-push test failed (exit code 1)`). Nothing records which tests
failed or why, nothing classifies the failure, and nothing tries to fix it. On 2026-11-26 three flows halted on the same
two tests
(`test_executor_run_salvage.py::TestExecutorPartialWorkSalvage::test_agent_commits_with_clean_tree_record_the_agent_head`,
`test_flow_repo_templates.py::test_the_history_matches_build_flow_repos_and_commit_on`; 2 failed / 9,082-9,124 passed)
caused by the review-loop identity environment from PR #350 (Bean 0547, fix PR #354); the cause was found only by hand.

## Design

A test-failure loop wherever the flow runs the suite (Stage 3 executor, Stage 4 resolver pre-push, Stage 5 checks):

1. **Record.** Every failed run appends a row to the flow's execution ledger fragment (the per-flow ledger since #314):
   run id, stage, head SHA, failing test ids, a short output excerpt per test (assertion and location), environment
   summary (scrubbed of secrets), and later the classification and fix attempt. Repeated failure signatures are promoted
   to the knowledge base as failure modes at Stage 5, so later flows see them.
2. **Diagnose.** Re-run only the failing ids three ways: in the same environment, in a scrubbed environment (no
   `GIT_AUTHOR_*`/`GIT_COMMITTER_*`, clean HOME/TMPDIR), and on the PR base (origin/main merged). Classify:
   - **introduced** (fails with the change, passes on base),
   - **flaky** (passes on a plain re-run),
   - **environment** (fails only in the flow's environment),
   - **pre-existing** (fails on base too).
3. **Fix.** Feed the classification, the failing ids and the excerpts to an agent turn:
   - introduced → the executor/resolver fixes the change;
   - flaky → re-run up to N times, record the flake, and propose a test fix as a finding;
   - environment or pre-existing → fix the cause if it is inside the flow's scope; otherwise create or link the blocker
     (a bean / flow for the cause, Bean 0497 `blocked_on`), park with the evidence, and resume automatically when the
     blocker lands (Bean 0523).
4. **Re-run** the full selection after every fix and go back to step 1 **until the tests pass**.
5. **Guard against spinning.** If the same failure signature repeats after a fix with no progress, step up a model tier
   (claude ladder) and try again; after the tier ladder is exhausted, park with `blocked_on` and the full ledger trail
   rather than loop forever. Every iteration is in the ledger, so a park is fully diagnosed.

## Acceptance

- A failed test run in any stage produces ledger rows with the failing ids, excerpts and classification.
- An introduced failure gets a fix turn and a re-run; the flow continues when the suite passes, without halting.
- A flaky test is re-run and recorded; an environment / pre-existing failure parks with `blocked_on` and evidence.
- The 2026-11-26 case (identity env leak) would have been classified "environment" within one iteration.
- Tests for each classification path, using a fake test runner.
- Related: 0497, 0523, 0547, 0412.
