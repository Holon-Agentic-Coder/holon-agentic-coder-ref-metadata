---
# holon-agentic-coder-ref-metadata-0244
title: "Treat knowledge and wisdom facts as immutable append-only records"
status: completed
type: task
priority: high
tags:
  - knowledge
  - wisdom
  - immutability
  - append-only
  - calibration
  - holon-agentic-coder
created_at: 2026-11-06T10:05:00Z
updated_at: 2026-11-06T14:55:00Z
---

## Problem

In Stage 5 Calibration, `promote_pending_candidates()` in `sandbox_executor/knowledge/wisdom.py` re-scans the historical
SQLite action index for all signatures with $\ge 2$ trials and invokes `persist_kb_fact()` and `persist_wb_rule()`.

These persistence functions currently overwrite existing JSON files on disk on every run, re-generating both
`created_ts` and `updated_ts` with `datetime.now(UTC).isoformat()`, even when zero evidence, counts, or payload fields
have changed.

Since Bean 0239 (PR #130) enabled `_commit_stage5_promoted_artifacts()` in Stage 5, this lack of immutability caused
hundreds of historical knowledge files (`holon-knowledge/kb/failure_modes/*.json`, `patterns/*.json`,
`wisdom/heuristics/*.json`) to be rewritten and committed on every flow calibration pass (e.g. 385 files and 1,540 lines
modified in PR #132).

Facts, failure modes, and patterns must be treated as **immutable append-only records**: once written, an existing fact
file must never be overwritten, touched, or re-serialized.

## Goal

1. **Immutable Fact Contract**:
   - Treat all fact and heuristic files in `holon-knowledge/kb/` and `holon-knowledge/wisdom/` as immutable append-only
     records.
   - When an entry already exists on disk (by file name / `kb_id` / `wb_id`), it is immutable: do not overwrite,
     re-serialize, touch, or regenerate its timestamps.
2. **Strictly New Entries**:
   - In `promote_pending_candidates()`, check whether a qualified candidate is already persisted on disk. Only persist
     entries for newly qualified signatures or facts that do not already have an established file.
   - New failure modes or patterns are strictly new files.
3. **Directory Index Immutability**:
   - In `_update_directory_index()`, do not rewrite subfolder `index.json` files if no new entries were added or
     substantively altered.
4. **Zero False Git Churn**:
   - When no new facts qualify for promotion, `promote_pending_candidates()` produces 0 disk writes, ensuring
     `_commit_stage5_promoted_artifacts()` performs a clean no-op with 0 files staged or committed.
5. **Dedicated Hermetic Unit Tests (Verify Facts Never Touched)**:
   - Add hermetic unit tests in `apps/sandbox-executor/tests/test_wisdom.py` asserting that pre-existing fact files on
     disk are **strictly never touched**:
     - Pre-populate a fact file (`KB-failure-*.json`, `KB-pattern-*.json`, `WB-heuristic-*.json`), record its SHA-256
       hash and exact nanosecond modification time (`os.stat(path).st_mtime_ns`).
     - Execute `promote_pending_candidates()` and `persist_kb_fact()` repeatedly against matching signatures.
     - Assert that `st_mtime_ns` and file contents remain 100% identical and that zero writes occur to existing files.
   - Add test coverage in `apps/sandbox-executor/tests/test_flow.py` asserting that Stage 5 calibration leaves existing
     fact files untouched and `_commit_stage5_promoted_artifacts()` results in a clean no-op when no new facts qualify.

## Resolution

Delivered via [PR #133](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/133) and merged into `main`
(`2a56a89`):

- **Immutable Fact Persistence**: In `apps/sandbox-executor/src/sandbox_executor/knowledge/wisdom.py`, treated fact
  files in `holon-knowledge/kb/` and `holon-knowledge/wisdom/` as immutable append-only records. When an entry already
  exists on disk, persistence is skipped without touching timestamps or file metadata.
- **Decomposed Candidate Promotion**: Decomposed `promote_pending_candidates()` into `_promote_failure_candidate()` and
  `_promote_success_candidate()` helpers, satisfying Ruff C901 cyclomatic complexity ($\le 6$).
- **Idempotent Directory Indices**: Guarded `_update_directory_index()` so index files are not re-serialized or touched
  unless entries change.
- **Hermetic Immutability Tests**: Added test suites in `apps/sandbox-executor/tests/test_wisdom.py` asserting that
  pre-existing fact files on disk maintain bit-for-bit identical SHA-256 digests and exact nanosecond `st_mtime_ns`
  across repeated promotion and persistence runs.
- **Zero-Churn Calibration Verification**: Added coverage in `test_flow.py` confirming
  `_commit_stage5_promoted_artifacts()` no-ops cleanly when no new facts qualify.
- Traversed all 5 stages of the Holon flow, passed 3/3 ensemble review approval, calibrated, and merged into `main`.
