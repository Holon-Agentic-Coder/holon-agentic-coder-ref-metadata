---
# holon-agentic-coder-ref-metadata-0536
title: "Unify structured logging, bound checkpoint context.logs, and remove FlowCheckpoint dual-writes"
status: todo
type: task
priority: normal
tags:
  - holon-agentic-coder
  - observability
  - logging
created_at: 2026-11-26T13:35:00Z
updated_at: 2026-11-26T13:35:00Z
---

## Problem

Flow execution emits unstructured plain-text logs with mixed `print()` and `logging` calls, appends unbounded
`context.logs` arrays directly inside persisted `FlowCheckpoint` JSON snapshots, and maintains dual-write redundancy in
`FlowCheckpoint.to_dict()`.

## Evidence

- Mixed `print()` and unstructured `logging` across stage/CLI execution paths.
- Unbounded `context.logs` persisted inside checkpoint JSON files (slowing atomic checkpoint
  serialization/deserialization on long or restarted flows).
- `apps/sandbox-executor/src/sandbox_executor/flow/checkpoint.py:124-128`: `FlowCheckpoint.to_dict()` duplicates
  `admission` fields alongside legacy aliases such as `repo_dir`.

## Proposed Change

1. Introduce structured log event helpers (supporting JSON or key=value line format) and route execution progress
   through `logging` rather than ad-hoc `print()`.
2. Bound `context.logs` inside `FlowCheckpoint` (e.g., tail ring buffer of recent entries) while writing full logs to
   the dedicated flow log file.
3. Deprecate and remove dual-write `admission` / `repo_dir` redundancy from `FlowCheckpoint.to_dict()` while preserving
   read compatibility for existing checkpoints.

## Acceptance Criteria

- Checkpoint JSON size stays bounded regardless of flow iteration count or restart count.
- `FlowCheckpoint.to_dict()` emits a single canonical schema without duplicate `admission` / `repo_dir` fields, while
  `from_dict()` still loads older checkpoints cleanly.

## Notes

- Target repository: `holon-agentic-coder` (evaluated at `HEAD f1e18bcd`).
- Coordinate with Bean `0412` / `0476` / `0495` on flow log streaming.
- Source: 2026-11 ecosystem architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
