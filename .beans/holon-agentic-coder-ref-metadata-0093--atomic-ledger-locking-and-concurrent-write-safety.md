---
# holon-agentic-coder-ref-metadata-0093
title: "Atomic ledger locking and concurrent write safety"
status: completed
type: task
priority: high
tags:
  - reliability
  - ledger
  - concurrency
  - locking
created_at: 2026-10-14T13:40:00Z
updated_at: 2026-10-15T15:38:00Z
---

# Bean 0093: Atomic Ledger Locking and Concurrent Write Safety

- **Bean ID:** 0093
- **Title:** Atomic Ledger Locking and Concurrent Write Safety
- **Status:** completed
- **Priority:** high
- **Category:** reliability
- **Components:** `apps/sandbox-executor/ledger.py`, `apps/sandbox-executor/flow.py`
- **Created At:** 2026-10-14
- **Parent Audit Finding:** BUG-01

---

## 1. Context & Motivation

The Holon control plane relies on append-only JSON Lines ledger files stored under `holon-knowledge/ledger/`
(`executions.jsonl`, `intents.jsonl`, `plans.jsonl`). As established in `holon-config/world/constraints.md` §3, ledgers
are the primary source of truth for execution telemetry, EV metric tracking, and post-execution calibration.

During the repository reliability audit (Finding BUG-01 in `docs/audit_report.md`), ledger append routines were found to
use uncoordinated `open(..., "a")` operations without inter-process or inter-thread file locking.

---

## 2. Problem Statement

1. In `apps/sandbox-executor/src/sandbox_executor/flow.py` and `ledger.py`, entries are appended directly to `.jsonl`
   files via standard buffered writes without synchronization.
2. When multiple autonomous agent instances, subagents, or background evaluation workers run concurrently, concurrent
   writes can interleave characters across lines, corrupting JSON records and breaking downstream query tools
   (`holon ledger query`, `jq`).

---

## 3. Proposed Remediation

1. **Advisory File Locking (`fcntl.flock`):** Wrap all ledger append operations in an atomic context manager that
   obtains an exclusive advisory lock (`fcntl.flock(fd, fcntl.LOCK_EX)`) prior to file writing.
2. **Lock Timeout and Retry:** Implement a bounded retry loop (e.g. 5-second timeout with exponential backoff) to
   prevent deadlocks in highly contended environments.
3. **Flush and Sync:** Explicitly invoke `f.flush()` and `os.fsync(f.fileno())` before releasing the file lock to
   guarantee on-disk persistence.
4. **Cross-Platform Compatibility:** Fall back gracefully to `msvcrt` locking or file-based lockfiles (`.lock`) on
   non-POSIX platforms.

---

## 4. Acceptance Criteria

- [x] Every ledger write in `flow.py`, `ledger.py`, and entrypoints acquires an exclusive advisory lock before writing.
- [x] Concurrent write stress tests demonstrate zero corrupted or interleaved lines across 100 simultaneous simulated
      write processes.
- [x] Lock acquisition failures emit descriptive diagnostics without crashing parent processes silently.

---

## 5. Verification Commands

```bash
# Run ledger concurrent write unit tests
uv run pytest apps/sandbox-executor/tests/test_ledger_query.py

# Verify linting and formatting
uv run ruff check .
npx prettier --check .beans/holon-agentic-coder-ref-metadata-0093--atomic-ledger-locking-and-concurrent-write-safety.md
```

---

## 6. Resolution

- Implemented `atomic_ledger_append` in `apps/sandbox-executor/src/sandbox_executor/ledger.py` utilizing non-blocking
  advisory file locking (`fcntl.flock` with `LOCK_EX | LOCK_NB`), exponential backoff, randomized jitter, explicit
  `f.flush()`, and `os.fsync(f.fileno())`.
- Wired uniformly across `flow.py`, `ledger.py`, and entrypoints (`entrypoint/executor.py`, `entrypoint/planner.py`,
  `entrypoint/intent_creator.py`).
- Added non-POSIX fallback and network filesystem error handling (`ENOSYS`/`EOPNOTSUPP`).
- Added concurrent write safety tests in `test_ledger_query.py`.
- Validated via Holon flow lifecycle stages 1-5; PR #77 achieved 3/3 unanimous ensemble consensus approval, 10/10 green
  CI checks, and pre-merge calibration ($\Delta EV$ +4.30); merged to `main` at commit
  `29aa1c14d060c4b90657803f046c964c6beb54e3`.
