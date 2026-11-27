---
# holon-agentic-coder-ref-metadata-0563
title: "Check: exactly three append-only ledgers in each target repository"
status: in-progress
type: task
priority: high
tags:
  - ledger
  - invariants
  - tests
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-11-26T23:09:56Z
updated_at: 2026-11-27T00:30:35Z
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

## Progress (2026-11-27)

- **holon-agentic-coder: delivered** by PR #362 (flow slug `three-ledgers-append-only-gate`), merged into `main`
  (`d6f513b`, 2026-11-27T00:28:06Z). Delivered: `scripts/check_ledger_stores.py` (fails on a fourth ledger-like store or
  a missing canonical ledger), `scripts/check_ledger_rows_append_only.py` (base rows must stay byte-identical on the
  head; fragments and promotion pass; an unreadable base fails closed), CI workflow
  `.github/workflows/test-ledger-invariants.yml` on `pull_request`, hermetic fail-case tests in
  `apps/sandbox-executor/tests/test_ledger_stores_exactly_three.py` and `test_ledger_rows_append_only_diff.py`, and a
  README entry. Registry entry `three-append-only-ledgers` is `partial`.
- **Acceptance check against the merged diff (CF-0025):**
  - Hygiene test, store set is exactly the three ledgers: delivered (holon-agentic-coder).
  - CI diff check, base rows byte-identical on the head: delivered (holon-agentic-coder).
  - Both repositories: holon-agentic-coder only. **holon-coherence not delivered** (no coherence change in #362).
  - Runs automatically: CI on `pull_request` delivered. Pre-commit hook and flow gate not wired in the diff.
  - Proven to fail before trusted: delivered with reconstructed fixtures; no run against today's real violation
    evidence.
  - Self-explaining code: zero docstrings and zero non-`# why:` comments in the added code (measured).
  - Through `holon flow`, no harness paths or bean ids in the intent: delivered (no hits in the intent, plan or
    execution rows).
- **Remaining:** the holon-coherence half (its own `holon flow`), pre-commit and flow-gate wiring for
  holon-agentic-coder, and a fail-proof against today's evidence. Bean stays `in-progress` until the coherence flow
  lands.
