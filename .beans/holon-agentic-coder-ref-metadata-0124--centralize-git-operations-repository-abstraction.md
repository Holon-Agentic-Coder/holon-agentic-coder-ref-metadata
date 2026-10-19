---
# holon-agentic-coder-ref-metadata-0124
title: "Centralise Git operations and worktree commands into unified repository abstraction"
status: completed
type: task
priority: normal
tags:
  - architecture
  - refactor
  - git
  - flow
  - audit
parent: holon-agentic-coder-ref-metadata-0122
created_at: 2026-10-19T01:38:00Z
updated_at: 2026-10-19T04:40:00Z
---

Centralise raw `subprocess.run(["git", ...])` calls across `sandbox-executor` into a unified repository abstraction
module.

## Context

Audit finding `AUD-2026-02`: Multiple modules in `sandbox-executor` (`flow.py`, `calibration.py`, `pr_review_loop.py`,
`pre_commit_check.py`) independently invoke raw Git subprocesses. This results in duplicated error handling, varied
timeout thresholds, inconsistent output decoding, and redundant ref resolution logic.

## Tasks

- [x] Create `sandbox_executor.git` repository helper module with typed methods (`run_git`, `get_diff_numstat`,
      `resolve_ref`, `get_head_commit`, `branch_exists`).
- [x] Refactor `calibration.py` and `flow.py` to route all Git interactions through the centralised module.
- [x] Add unit tests verifying repository helper behaviour and error handling under transient Git failures.

## Resolution

- Created typed repository abstraction `apps/sandbox-executor/src/sandbox_executor/git.py` implementing `run_git` (with
  credential redaction and configurable timeouts), `get_diff_numstat`, `resolve_ref`, `get_head_commit`, and
  `branch_exists`.
- Refactored `flow.py` and `calibration.py` to delegate all Git commands and ref parsing to `sandbox_executor.git`.
- Added comprehensive unit tests in `apps/sandbox-executor/tests/test_git.py` (8/8 passed).
- Executed through full 5-stage Holon flow via PR #86:
  https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/86
