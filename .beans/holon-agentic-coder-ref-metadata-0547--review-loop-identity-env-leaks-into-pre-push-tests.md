---
# holon-agentic-coder-ref-metadata-0547
title:
  "Review-loop git identity overlays os.environ for the whole run, so the resolver's pre-push tests see the review-loop
  author"
status: in-progress
type: bug
priority: high
tags:
  - flow
  - git
  - review-loop
  - tests
  - holon-agentic-coder
created_at: 2026-11-26T21:21Z
updated_at: 2026-11-27T10:20Z
---

## Problem

Flow `single-runner-per-checkpoint` (bean 0390) reached Stage 4 on 2026-11-26 (E-1795726850). The review loop ran one
iteration (CHANGES_REQUESTED, 5 open findings). The resolver then halted at its pre-push verification with two failing
tests, both deterministic:

- `apps/sandbox-executor/tests/test_executor_run_salvage.py::TestExecutorPartialWorkSalvage::test_agent_commits_with_clean_tree_record_the_agent_head`
  expected author `executor-agent@holon-agentic-coder.com`, got `review-loop-agent@holon-agentic-coder.com`.
- `apps/sandbox-executor/tests/test_flow_repo_templates.py::test_the_history_matches_build_flow_repos_and_commit_on`
  compared log identities `Holon Test` against `Holon Review Loop Agent`.

The flow halted with "Halting review loop at iteration 1: resolver failed", and the resolver's fixes stayed uncommitted
in the flow worktree.

## Cause

`apps/sandbox-executor/src/sandbox_executor/entrypoint/review_loop.py`, `main()`, wraps the whole run in
`with _review_git_identity(os.environ):`, which overlays `GIT_AUTHOR_*` / `GIT_COMMITTER_*` (review-loop agent) on the
process environment. Subprocesses inherit that environment, so the resolver's pre-push pytest run commits with the
review-loop identity. Bean 0518 (PR #350) stopped the identity leaking into the shared repository config, but the
environment overlay still reaches the tests that assert the executor identity.

## Goal

- Keep the review-loop identity off the environment of the pre-push test run (for example scope the overlay to the git
  commands the review loop makes, or clear the `GIT_*` identity variables for the test subprocesses).
- The two tests above pass inside the review loop's pre-push verification.
- Add a regression test that runs the pre-push verification with the review-loop overlay active.

## Notes

- Found while driving bean 0390; flow log `todo/flow-single-runner-per-checkpoint.log`.
- Bean 0390's resume from `--from-stage review` will halt the same way until this is fixed.

## Progress

- 2026-11-27: in-progress. Flow `review-identity-env-scope` (intent todo/intent-0547-review-identity-env-scope.json, log
  todo/flow-review-identity-env-scope.log, worktree apps/holon-agentic-coder/flow-review-identity-env-scope off
  origin/main cc1f256). Fix: the review identity is applied per git commit (`review_git_env()` in
  flow/review/git_identity.py, used by the resolver commit) and no longer overlaid on os.environ in main().
  Intent-check: no missing files.

## More evidence (from scrapped duplicate 0548)

Flow main-push-superseded-skip (bean 0514, PR #353) halted the same way at Stage 4 iteration 1: resolver pre-push pytest
2 failed / 9091 passed — test_flow_repo_templates.py::test_the_history_matches_build_flow_repos_and_commit_on and
test_executor_run_salvage.py (agent commits with clean tree record the agent head). Both pass on the host. A rerun from
review failed identically.

- 2026-11-27: flow `review-identity-env-scope` finished: PR #354
  (https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/354), 3/3 APPROVED at iteration 1 (approved head
  ffc6ec12), calibration report included in the PR diff (EV 63.44), MERGEABLE/CLEAN, all CI green. Awaiting the
  maintainer's merge; the bean closes after the post-merge step.
