---
# holon-agentic-coder-ref-metadata-0124
title: "Centralise Git operations and worktree commands into unified repository abstraction"
status: todo
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
updated_at: 2026-10-19T01:38:00Z
---

Centralise raw `subprocess.run(["git", ...])` calls across `sandbox-executor` into a unified repository abstraction
module.

## Context

Audit finding `AUD-2026-02`: Multiple modules in `sandbox-executor` (`flow.py`, `calibration.py`, `pr_review_loop.py`,
`pre_commit_check.py`) independently invoke raw Git subprocesses. This results in duplicated error handling, varied
timeout thresholds, inconsistent output decoding, and redundant ref resolution logic.

## Tasks

- [ ] Create `sandbox_executor.git` repository helper module with typed methods (`run_git`, `get_diff_numstat`,
      `resolve_ref`, `get_head_commit`, `branch_exists`).
- [ ] Refactor `calibration.py` and `flow.py` to route all Git interactions through the centralised module.
- [ ] Add unit tests verifying repository helper behaviour and error handling under transient Git failures.
