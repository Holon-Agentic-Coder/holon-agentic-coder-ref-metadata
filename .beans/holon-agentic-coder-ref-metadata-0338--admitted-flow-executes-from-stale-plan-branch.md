---
# holon-agentic-coder-ref-metadata-0338
title:
  "A flow admitted after waiting out an overlap executes from a stale plan branch and conflicts with the PR it waited
  for"
status: completed
type: bug
priority: high
tags:
  - flow
  - stage-3
  - admission
  - concurrency
  - holon-agentic-coder
created_at: 2026-11-20T16:55:00+11:00
updated_at: 2026-11-20T18:08:00+11:00
---

## Problem

Seen on the `blockedflow` flow (Bean 0337, PR #209), 2026-11-20. The flow was refused at Stage 3 because its touch set
overlapped PR #207 and then PR #208, and the harness runner waited both out. When #208 merged, Stage 3 admitted the flow
and the executor started from the plan tip `cabbebff`, which was cut from `main` before #207 and #208 merged. Stage 3
passed (4471 tests), but Stage 4 stopped at once with "Unresolvable merge conflicts detected in stage 'review'" on five
files (`flow_module_budgets.json`, `flow/__init__.py`, `flow/admission.py`, `tests/flow/stages/test_decomposition.py`,
`tests/flow/test_admission.py`), and a resolve-conflict pass had to merge `origin/main` by hand before the flow could
resume.

This is not bad luck: a flow only waits on a pull request because it touches the same files, so executing from the old
plan base guarantees a conflict with exactly the change it waited for. The executor also writes code against a version
of those files that no longer exists on `main`.

## Decision (maintainer, 2026-11-20)

After waiting out an overlap, the flow updates its plan branch from `origin/main` before Stage 3 executes.

## Action

Through the Holon flow on `holon-agentic-coder`:

- **Refresh the plan branch on admission.** When Stage 3 admits a flow whose checkpoint records an earlier blocked state
  (Bean 0337's `admission.state` went from `blocked` to `admitted`), fetch `origin` and merge `origin/main` into the
  plan branch before the executor branch is cut. Merge, never rebase: plan branches are pushed and must not be
  rewritten. Push the updated plan branch.
- **Ledgers merge mechanically.** Conflicts in the three append-only ledgers are resolved by interleaving rows by
  `created_at`; the plan markdown and other plan files keep the plan side unless `main` changed them.
- **Stop cleanly on a real conflict.** A conflict outside the ledgers stops Stage 3 before dispatch with a message
  naming the files, and the checkpoint stays resumable; nothing is executed against a half-merged tree.
- **Record it.** The executions ledger row (or the checkpoint) notes the `main` commit the plan branch was refreshed to,
  so calibration can tell a refreshed base from the original one.
- **Hermetic tests:** a blocked-then-admitted flow gets `origin/main` merged into its plan branch before execution; a
  flow admitted on the first try is not touched; a ledger-only conflict is resolved by `created_at`; a code conflict
  stops before dispatch with a resumable checkpoint.

## Notes

- Related: Bean 0337 (blocked admission state, PR #209), Bean 0335 (resume from the execution branch tip, PR #208), Bean
  0264 (`flow_module_budgets.json` makes most flows overlap). The harness runner's overlap wait
  (`.agents/skills/holon_flow/scripts/run_holon_flow.py`) needs no change: it resumes from the checkpoint, and Stage 3
  does the refresh.

## Progress

- 2026-11-20 16:55 (+11:00): Holon flow `refresh-plan-after-overlap-wait` started (claude-agent, claude-opus-5-5) in
  worktree `apps/holon-agentic-coder/flow-refresh-plan-after-overlap-wait`, concurrently with the
  `review-keeps-worktree-on-branch` and `planner-api-error-not-a-plan` flows.
- 2026-11-20 18:01 (+11:00): Flow completed all 5 stages; PR #211
  (https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/211) MERGEABLE/CLEAN, CI 11/11 green, consensus
  APPROVED 3/3 at review iteration 2, calibration report in the PR diff. Stage 3 waited out PR #210 (blocked admission),
  executed 12.4 min; Stage 4 first stopped on the expected stale-base conflict in `flow_module_budgets.json`, resolved
  by merging `origin/main` (description texts combined, ledgers interleaved, lint and 4620 tests green, merge commit
  12ec758) and resumed from the checkpoint. EV predicted 44.16, actual -18.21 (calibration scored P(success) 0.00 and
  impact 0 despite approval and green CI). Awaiting human merge.

## Resolution

Delivered via [PR #211](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/211) and merged into `main`
(`1610809`, squash commit `16108098`):

- **Key Architectural Deliverables**: `flow/plan_refresh.py` merges `origin/main` into the plan branch on Stage 3
  admission after a blocked wait, before the execution branch is cut. Ledger-only conflicts are interleaved by
  `created_at`; any other conflict aborts the merge and stops Stage 3 before dispatch, naming the files, with a
  resumable checkpoint. The refreshed target commit is recorded as a `plan_refresh` row and as `refreshed_to` in the
  checkpoint's admission object. A first-check admission is unchanged.
- **Verification & Tests**: hermetic tests for the blocked-then-admitted refresh, the first-try no-op, ledger-only
  resolution by `created_at`, and the resumable code-conflict stop. CI 11/11 green; consensus APPROVED 3/3 at review
  iteration 2.
- **Holon Flow Traversal**: all 5 stages completed. Stage 3 waited out PR #210. Stage 4 stopped on the expected
  stale-base conflict in `flow_module_budgets.json`. That run predates the refresh code, so the conflict was resolved by
  hand: `origin/main` (refreshed main commit `30d7c77c`, PR #210) merged at `12ec758`, then resumed from the checkpoint.
- **Calibration caveat**: the calibration EV (predicted 44.16, actual -18.21) is wrong because of the bug in Bean 0339
  (P(success) scored 0.00 and impact 0 despite approval and green CI). Do not use that EV as a signal.
