---
# holon-agentic-coder-ref-metadata-0568
title: "Check: main worktrees are never edited, built or measured in"
status: todo
type: task
priority: high
tags:
  - harness
  - worktrees
  - invariants
created_at: 2026-11-26T23:09:56Z
updated_at: 2026-11-26T23:09:56Z
---

## Instruction (maintainer, 2026-11-27 local)

"For the invariants that are not explicitly checked or there's no tests, create a bean so the invariants NEVER slip
through." Parent: Bean 0562.

## Invariant

`apps/holon-agentic-coder/main` and `apps/holon-coherence/main` stay pristine: on `main`, equal to or behind
`origin/main` only by fast-forward, clean tree (except the known untracked `todo/`). CF-0011 broke it.

## Check

- A harness script (and test) asserting the state; run by the coordinator after every subagent and by post-pr-merge
  before and after its fast-forward. A violation is recorded in the failure ledger and reported at once.
- `pre-commit` / `post-checkout` hook in those worktrees refusing commits and non-main checkouts (the post-merge
  fast-forward is the only allowed move).

## Common acceptance

- The check runs automatically (pre-commit hook and/or CI, and the flow gate where it applies); no agent has to remember
  it.
- The check is proven to fail on a real or reconstructed violation (a test with today's evidence) before it is trusted,
  and passes on the cleaned state.
- Self-explaining code invariant in anything written: no docstrings, no comments except `# why:`.
- Target-repository work goes through `holon flow`; the intent never names harness paths or bean ids.
