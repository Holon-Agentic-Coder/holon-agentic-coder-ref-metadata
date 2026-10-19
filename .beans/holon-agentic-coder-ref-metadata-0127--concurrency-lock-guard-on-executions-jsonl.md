---
# holon-agentic-coder-ref-metadata-0127
title: "Implement file-locking concurrency guard for atomic ledger appends"
status: todo
type: task
priority: normal
tags:
  - ledger
  - concurrency
  - provenance
  - audit
parent: holon-agentic-coder-ref-metadata-0122
created_at: 2026-10-19T01:38:00Z
updated_at: 2026-10-19T01:38:00Z
---

Implement an advisory file-locking concurrency guard around `holon-knowledge/ledger/*.jsonl` mutations to prevent race
conditions during parallel agent execution.

## Context

Audit finding `AUD-2026-05`: High-frequency concurrent writes to `actions.jsonl` and `executions.jsonl` from parallel
review loop evaluations or multi-agent execution risk interleaving or partial writes. An advisory lock (`fcntl.flock`)
guarantees atomic append semantics.

## Tasks

- [ ] Create a reusable file lock context manager (`LedgerLock`) in `sandbox_executor`.
- [ ] Wrap all ledger append operations (`append_action_ledger`, `append_execution_record`) with the lock.
- [ ] Write concurrency tests verifying that concurrent threads/processes append cleanly without line interleaving or
      corruption.
