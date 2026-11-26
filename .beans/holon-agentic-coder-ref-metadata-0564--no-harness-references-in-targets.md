---
# holon-agentic-coder-ref-metadata-0564
title: "Check: target repositories and intents never reference harness paths or bean ids"
status: todo
type: task
priority: critical
tags:
  - invariants
  - intent
  - tests
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-11-26T23:09:56Z
updated_at: 2026-11-26T23:09:56Z
---

## Instruction (maintainer, 2026-11-27 local)

"For the invariants that are not explicitly checked or there's no tests, create a bean so the invariants NEVER slip
through." Parent: Bean 0562.

## Invariant

Nothing in a target repository (code, docs, ledgers, KB, PR bodies) and no intent text names `.beans/`, `todo/`,
`.agents/`, the harness repository or a bean id.

## Check

- `holon intent-check` rejects an intent whose text contains those paths or a bean-id pattern (the intent text is copied
  into the append-only intents ledger, so it must be refused before Stage 1).
- CI hygiene test scanning the PR diff (added lines) and PR body for the same patterns; fails closed.
- A one-off scan of current main reports existing hits for clean-up.

## Common acceptance

- The check runs automatically (pre-commit hook and/or CI, and the flow gate where it applies); no agent has to remember
  it.
- The check is proven to fail on a real or reconstructed violation (a test with today's evidence) before it is trusted,
  and passes on the cleaned state.
- Self-explaining code invariant in anything written: no docstrings, no comments except `# why:`.
- Target-repository work goes through `holon flow`; the intent never names harness paths or bean ids.
