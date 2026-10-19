---
# holon-agentic-coder-ref-metadata-0127
title: "Implement file-locking concurrency guard for atomic ledger appends"
status: completed
type: task
priority: normal
tags:
  - ledger
  - concurrency
  - provenance
  - audit
parent: holon-agentic-coder-ref-metadata-0122
created_at: 2026-10-19T01:38:00Z
updated_at: 2026-10-19T04:40:00Z
---

Implement an advisory file-locking concurrency guard around `holon-knowledge/ledger/*.jsonl` mutations to prevent race
conditions during parallel agent execution.

## Context

Audit finding `AUD-2026-05`: High-frequency concurrent writes to `actions.jsonl` and `executions.jsonl` from parallel
review loop evaluations or multi-agent execution risk interleaving or partial writes. An advisory lock (`fcntl.flock`)
guarantees atomic append semantics.

## Tasks

- [x] Create a reusable file lock context manager (`LedgerLock`) in `sandbox_executor`.
- [x] Wrap all ledger append operations (`append_action_ledger`, `append_execution_record`) with the lock.
- [x] Write concurrency tests verifying that concurrent threads/processes append cleanly without line interleaving or
      corruption.

## Resolution

- Implemented `class LedgerLock` in `apps/sandbox-executor/src/sandbox_executor/ledger.py` using non-blocking advisory
  file locking (`fcntl.flock(LOCK_EX | LOCK_NB)`), exponential backoff with randomised jitter, configurable timeout
  (default 30s), and automatic flush and fsync guarantees.
- Refactored `atomic_ledger_append`, `append_action_record`, and `append_summary_record` to use `LedgerLock`. Added
  convenience aliases `append_action_ledger` and `append_execution_record`.
- Added multi-threaded concurrency stress tests in `apps/sandbox-executor/tests/test_ledger_lock.py` verifying 10
  concurrent threads appending 200 items cleanly without interleaving or corruption.
- Executed through full 5-stage Holon flow via PR #86:
  https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/86
