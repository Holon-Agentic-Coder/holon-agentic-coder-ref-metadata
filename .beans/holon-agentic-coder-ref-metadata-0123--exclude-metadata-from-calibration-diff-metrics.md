---
# holon-agentic-coder-ref-metadata-0123
title: "Exclude metadata and planning artifacts from calibration diff metrics and State Surface Area"
status: completed
type: task
priority: high
tags:
  - calibration
  - flow
  - metrics
  - ssa
  - audit
parent: holon-agentic-coder-ref-metadata-0122
created_at: 2026-10-19T01:38:00Z
updated_at: 2026-10-19T01:38:00Z
---

Exclude metadata, planning artifacts, and append-only ledger files from calibration diff metrics, files changed counts,
and State Surface Area (SSA) calculations.

## Context

During Stage 5 calibration, `parse_actual_metrics` and `run_review_stage` measured changes relative to the plan branch
using `git diff --shortstat`. Because the flow appends records to `holon-knowledge/ledger/*.jsonl` and writes planning
markdown files under `plans/`, these metadata artifacts were counted as project code changes, skewing `files_changed`,
`insertions`, `deletions`, and inflating `ssa_obs`.

## Remediation

- Defined `METADATA_PATH_PREFIXES = ("holon-knowledge/", "plans/", ".holon/")` and `is_metadata_path(path)` in
  `sandbox_executor.calibration`. Strictly decoupled target repository from harness metadata paths (`.beans/`, `todo/`,
  `.agents/`) per Invariant 17.
- Switched diff parsing in `parse_actual_metrics` and `run_review_stage` to `git diff --numstat`, filtering out all
  paths matching `is_metadata_path`.
- Enforced that when zero project code files are modified (`actual.files_changed == 0`), `ssa_obs` evaluates strictly to
  `0.0`.
- Added unit tests in `test_calibration.py` verifying path filtering and metric calculations.
- Retired `actions.jsonl` and unified all discrete action events into `executions.jsonl` under `LedgerLock`.
- Executed through full 5-stage Holon flow via PR #85 (merged):
  https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/85
