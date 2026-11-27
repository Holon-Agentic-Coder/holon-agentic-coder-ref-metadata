---
# holon-agentic-coder-ref-metadata-0533
title: "Add mypy/pyright to CI, unify agent-ID and numstat helpers, and drive runtime env from env_registry"
status: in-progress
type: task
priority: high
tags:
  - holon-agentic-coder
  - typing
  - clean-code
  - dry
created_at: 2026-11-26T13:35:00Z
updated_at: 2026-11-27T11:48:05Z
---

## Problem

99.5% of functions carry return annotations, yet CI runs no static type checker (`mypy`/`pyright`). Core
normalization/parsing logic (agent IDs, runner metadata, `git diff --numstat`) is duplicated across 4–5 sites, runtime
code does not consume `env_registry.py` (causing real documentation/behavior drift like `HOLON_AGENT_EFFORT`), and
legacy `os.environ` mutations plus dead shims remain.

## Evidence

- No `mypy`/`pyright` check in `.github/workflows/`.
- 4 separate agent-ID normalizers: `agent_defaults.py:328` (`normalise_agent_id`), `local_llm.py:92`
  (`normalize_agent_id`), `agent_runner.py:682`, `entrypoint/role_dispatcher.sh:14-18`.
- Duplicate runner metadata between `agent_defaults.py` and `runners/*.py`.
- 5 separate `git diff --numstat` parsers (including literal tab parsing at `flow/stages/review.py:139`).
- `env_registry.py:4-5,55` and `config_env_keys.py:10` document `HOLON_AGENT_EFFORT` for Claude, whereas only
  `AntigravityAgentRunner` reads it (`agent_runner.py:517`).
- Process-global `os.environ` mutations in `cli/main.py:47` and `agent_runner.py:336,436`.
- Dead legacy artifacts: `_support_legacy_repo_dir` monkey-patch decorator (`flow/context.py:120-132`) and unreachable
  `sys.version_info >= (3, 12)` check (`agent_runner.py:81-84`).

## Proposed Change

1. Wire `mypy` or `pyright` into CI across `sandbox_executor` and fix surfaced type mismatches.
2. Unify agent-ID normalization into one shared helper (consumed by Python and shell/dispatcher wrappers) and
   consolidate `git diff --numstat` parsing into `git.py`.
3. Generate or validate runtime env lookups directly from `env_registry.py` (fixing `HOLON_AGENT_EFFORT` alignment) and
   pass scoped `env` mappings instead of mutating process-global `os.environ`.
4. Delete `_support_legacy_repo_dir` and the dead `sys.version_info >= (3, 12)` guard.

## Acceptance Criteria

- CI executes `mypy` or `pyright` cleanly on every PR.
- Single canonical helper exists for agent-ID normalization and `git diff --numstat` parsing.
- `HOLON_AGENT_EFFORT` docs and runner behavior agree, verified via `test_environment_reference.py`.

## Notes

- Target repository: `holon-agentic-coder` (evaluated at `HEAD f1e18bcd`).
- Coordinate env consolidation with Bean `0223`.
- Source: 2026-11 ecosystem architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
- **Progress (2026-11-27)**: [PR #422](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/422) (`2a83e4cc`,
  `hac-unify-agent-id-numstat`) merged into `main`: delegated `local_llm.normalize_agent_id` to `agent_defaults.py`,
  extracted canonical `git.parse_numstat` across `calibration_diff.py`, `flow/stages/review.py`,
  `flow/review/delta_review_git.py`, and `calibration/actual_evidence.py`, and added
  `apps/sandbox-executor/tests/test_dry_normalization_numstat.py` (Stage 4 approved and Stage 5 calibrated). Keeping
  `status: in-progress` for remaining slices (CI static type checker, `env_registry.py` runtime alignment, and legacy
  cleanup).
