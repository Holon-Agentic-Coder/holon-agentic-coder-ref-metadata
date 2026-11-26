---
# holon-agentic-coder-ref-metadata-0563
title: "Check: exactly three append-only ledgers in each target repository"
status: todo
type: task
priority: high
tags:
  - ledger
  - invariants
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

A target repository keeps exactly three append-only ledgers: `intents`, `plans`, `executions` (plus their per-flow
fragments). No fourth ledger; existing rows are never edited or deleted.

## Check

- Hygiene test: the set of ledger stores (files/dirs matching the ledger layout, and any new `*.jsonl` ledger-like file
  outside the KB) equals exactly those three.
- CI diff check: in a PR, ledger rows present on the base are byte-identical on the head (append-only); fragments only
  add.
- Both in holon-agentic-coder and holon-coherence (one flow each).

## Common acceptance

- The check runs automatically (pre-commit hook and/or CI, and the flow gate where it applies); no agent has to remember
  it.
- The check is proven to fail on a real or reconstructed violation (a test with today's evidence) before it is trusted,
  and passes on the cleaned state.
- Self-explaining code invariant in anything written: no docstrings, no comments except `# why:`.
- Target-repository work goes through `holon flow`; the intent never names harness paths or bean ids.
