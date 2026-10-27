---
# holon-agentic-coder-ref-metadata-0169
title: "PR #97 residual review Nits: split the pasted checkpoint test and complete the git_flow section list"
status: todo
type: task
priority: normal
tags:
  - tests
  - docs
  - holon-agentic-coder
created_at: 2026-10-27T12:10:02Z
updated_at: 2026-10-27T12:10:02Z
---

## Problem

The maintainer merged holon-agentic-coder PR #97 (Bean 0159) at head `b65ac56` on 2026-10-27, during review-loop
iteration 33 of 35. CI was 10/10 green and the last 30 review iterations found no open Critical finding. The
iteration-33 dry run (`.subagent/holon-agentic-coder_pr97_dry_run_review_iter_33_b65ac56.md`) left two Nits open:

1. **N-33-1:** iteration 32 pasted the new sub-intent checkpoint test into the middle of
   `test_atomic_checkpoint_save_and_load` in `apps/sandbox-executor/tests/test_flow.py`. This moved that test's
   missing-file check into the new test. The original test no longer checks what it is named for.
2. **N-33-2:** the section list in `docs/git_flow.md` §1.5 (the sections that describe the target model, not the current
   flow) omits the target-model example in §7.4.

The iteration-33 resolver was stopped before it pushed. It left uncommitted partial edits to these two files in
`apps/holon-agentic-coder/pr97-entropy-budget-no-human-halt`. They are discardable once this bean is picked up on the
new `main`.

## Scope

- Move the sub-intent checkpoint test into its own function, and restore `test_atomic_checkpoint_save_and_load` exactly
  as it was before iteration 32, including its missing-file check.
- Add §7.4 to the target-model section list in `docs/git_flow.md` §1.5.
- Verify fast-first: lint and Prettier, then the affected test file, then the full suite.

## Notes

- Run through the Holon flow on holon-agentic-coder. It is small and touches only `test_flow.py` and `git_flow.md`, so
  check for overlap with other open flows.
- Other #97 deferrals already have beans: decomposed-child chaining, the parent PR and resume safety (Bean 0161); the
  stress test's `core.hooksPath` dependence (Bean 0167); pre-existing bean ids on `main` (Bean 0147).
