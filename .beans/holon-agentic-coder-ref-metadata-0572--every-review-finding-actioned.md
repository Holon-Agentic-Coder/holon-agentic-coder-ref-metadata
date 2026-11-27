---
# holon-agentic-coder-ref-metadata-0572
title: "Check: every review finding is applied or rejected with a reason"
status: in-progress
type: task
priority: high
tags:
  - review-loop
  - invariants
  - holon-agentic-coder
created_at: 2026-11-26T23:09:56Z
updated_at: 2026-11-26T23:28:54Z
---

## Instruction (maintainer, 2026-11-27 local)

"For the invariants that are not explicitly checked or there's no tests, create a bean so the invariants NEVER slip
through." Parent: Bean 0562.

## Invariant

Every review finding, Nits and surviving mutants included, goes to the resolver and ends applied or rejected with a
written reason; never waved through. Review is a 3-reviewer ensemble.

## Check

- Stage 4/5 gate: each finding id in the review ledger rows has a matching resolver outcome row (applied with commit, or
  rejected with reason); a missing outcome fails the stage.
- Consensus approval requires exactly three reviewer verdicts recorded.
- Tests with a fake review loop.

## Common acceptance

- The check runs automatically (pre-commit hook and/or CI, and the flow gate where it applies); no agent has to remember
  it.
- The check is proven to fail on a real or reconstructed violation (a test with today's evidence) before it is trusted,
  and passes on the cleaned state.
- Self-explaining code invariant in anything written: no docstrings, no comments except `# why:`.
- Target-repository work goes through `holon flow`; the intent never names harness paths or bean ids.

## Flow log (parked)

parked 2026-11-27: blocked by PR #360 (flow 0549, test-failure-record-diagnose-fix) on
apps/sandbox-executor/src/sandbox_executor/flow/review/loop.py, apps/sandbox-executor/tests/test_review_ci_wait.py;
resume from checkpoint when PR #360 merges or releases those files. Stage 1 and 2 done (I-1795735540, P-1795735565 EV
37.60); Stage 3 execute commit E-1795735979 exists locally on the E branch; worktree flow-review-findings-all-actioned
and checkpoint kept.
