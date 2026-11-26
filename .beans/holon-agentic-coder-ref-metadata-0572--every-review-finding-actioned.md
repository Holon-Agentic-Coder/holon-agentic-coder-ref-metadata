---
# holon-agentic-coder-ref-metadata-0572
title: "Check: every review finding is applied or rejected with a reason"
status: todo
type: task
priority: high
tags:
  - review-loop
  - invariants
  - holon-agentic-coder
created_at: 2026-11-26T23:09:56Z
updated_at: 2026-11-26T23:09:56Z
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
