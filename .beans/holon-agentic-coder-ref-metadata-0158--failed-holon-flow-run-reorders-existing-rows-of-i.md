---
# holon-agentic-coder-ref-metadata-0158
title: "A failed holon flow run reorders existing rows of the append-only intents.jsonl"
status: todo
type: bug
priority: critical
tags:
  - ledger
  - holon-flow
  - holon-agentic-coder
created_at: 2026-10-26T04:23:42Z
updated_at: 2026-10-26T04:23:42Z
---

## Problem

Found on 2026-10-26 in worktree `apps/holon-agentic-coder/flow-0151-touch-set-admission` (clean checkout of
`origin/main` at `e3bbd67`). After a `holon flow --dry-run` and a real run that failed in Stage 1 (Bean 0157),
`holon-knowledge/ledger/intents.jsonl` was **staged** with no new row. Three existing rows
(`mergeability-missing-ref-not-conflict`, `redact-github-token-in-cli-echoes-v2`,
`flow-dispatch-role-agents-and-empty-diff-guard`) had been moved to new positions.

An append-only ledger must never be rewritten. It looks like a sort or merge pass that rewrites the whole file, for
example ordering by timestamp, or the union step used when resolving ledger append conflicts.

## Scope

- Find which code path (dry run, intent stage start, or failure handling) rewrites `intents.jsonl`, and make every
  ledger write a pure append under `LedgerLock`.
- A failed or dry-run stage must leave the ledgers byte-identical, or append only a failure record.
- Test: after a failed Stage 1 and after a dry run, the existing ledger bytes are a prefix of the new file.

## Notes

- **It also breaks the flow (2026-10-26, Bean 0159 run 2):** Stage 3 succeeded, but Stage 4 failed at once with "could
  not check out execution branch ... Your local changes to the following files would be overwritten:
  holon-knowledge/ledger/intents.jsonl". The reorder happens on the host worktree during each run, so every unattended
  `holon flow` run fails at review until it is fixed. Workaround: `git restore` the file, then resume with
  `--checkpoint ... --from-stage review`.

- Run through the Holon flow on holon-agentic-coder.
