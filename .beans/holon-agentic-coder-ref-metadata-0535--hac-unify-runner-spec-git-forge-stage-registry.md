---
# holon-agentic-coder-ref-metadata-0535
title: "Make RunnerSpec single-source runner registration and add GitForge Protocol + stage registry"
status: in-progress
type: task
priority: normal
tags:
  - holon-agentic-coder
  - extensibility
  - architecture
created_at: 2026-11-26T13:35:00Z
updated_at: 2026-11-27T21:46:37Z
---

## Problem

Adding a new coding-agent runner still requires coordinated edits across ~8 files spanning Python, shell, and Docker
configs. Meanwhile, GitHub CLI (`gh`) calls are hardcoded with no forge `Protocol`, `flow/pipeline.py` dispatches stages
via hardcoded `if/elif`, only 2 `Protocol` classes exist across 341 modules, and `subprocess` is imported directly in 50
modules.

## Evidence

- Adding a runner spans `agent_runner.py`, `agent_defaults.py`, `launcher/mounts.py`, `entrypoint/role_dispatcher.sh`,
  `Dockerfile`, `docker-bake.hcl`, `env_registry.py`, and docs despite `runners/spec.py` (`RunnerSpec`).
- `flow/pipeline.py:176-199`: hardcoded `if/elif` stage dispatch.
- Only 2 `Protocol` definitions across 341 source files; no `GitForge` `Protocol` decoupling PR/CI operations from `gh`
  JSON; `subprocess` imported directly in 50 modules.

## Proposed Change

1. Make `RunnerSpec` (`runners/spec.py`) the single source of truth driving `agent_defaults.py`, `launcher/mounts.py`,
   and generated/manifested role-dispatcher runner metadata.
2. Define a `GitForge` `Protocol` implemented by `GitHubAdapter` so stage code depends on the protocol rather than `gh`
   subprocess internals.
3. Replace the `if/elif` stage dispatch in `flow/pipeline.py:176-199` with a declarative stage registry mapping stage
   enum/keys to handlers.

## Acceptance Criteria

- Runner mounts, defaults, and model-discovery hooks read from `RunnerSpec` without duplicating per-runner tables in
  `agent_defaults.py`.
- Pipeline stage dispatch uses a registry table and PR/CI consumers type against `GitForge`.

## Notes

- Target repository: `holon-agentic-coder` (evaluated at `HEAD f1e18bcd`).
- Related: Bean `0270` (dynamic model discovery).
- Source: 2026-11 ecosystem architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
- parked 2026-11-27: blocked by PR #412
  (`I-1795767086-stage4-carried-finding-clean/P-1795767114-ANA-G4N/E-1795767405-ANA-G4N/_`) on
  `apps/sandbox-executor/src/sandbox_executor/flow/review/loop.py`; resume from checkpoint
  `apps/holon-agentic-coder/flow-hac-stage-registry-git-forge/.holon/flow/checkpoint-hac-stage-registry-git-forge.json`
  when PR #412 merges.

## Flow

- **Slice 1 (`2026-11-27`, `hac-stage-registry-git-forge`):** Completed all 5 stages on `antigravity-agent` /
  `gemini-4-neon` and opened [PR #431](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/431) (`OPEN`,
  `MERGEABLE` / `CLEAN`, `16/16` CI `SUCCESS`, Consensus `APPROVED`,
  `Predicted EV 54.48 / Actual EV 74.14 / ΔEV +19.66`). Waiting for human maintainer merge.
- **Slice 2 (`2026-11-27`, `hac-runnerspec-single-source`):** Launched covering AC #1 (`RunnerSpec` single-source
  mounts, defaults, and model-discovery hooks across `runners/*.py`, `agent_defaults.py`, `launcher/mounts.py`, tested
  in `tests/test_agent_defaults.py` and `tests/test_runner_specs.py`, `todo/intent-coverage-0535.json`). Opened
  [PR #441](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/441), which halted at Stage 4 iter 1
  (`touch_set_violation`: resolver delegated `launcher/antigravity_mounts.py` and `launcher/pi_mounts.py` to
  `runners/`). Closed `#441` (`CF-0077`) and re-cut Slice 2 with the expanded 15-file scope including
  `launcher/antigravity_mounts.py`, `launcher/pi_mounts.py`, `tests/test_antigravity_mounts.py`, and
  `tests/test_pi_mounts.py`. Stage 3 execution (`E-1795813140-ANA-G4N`) passed `10875` tests but modified
  `apps/sandbox-executor/tests/test_self_doc_runners_launcher.py`; re-plan (`P-1795815148-ANA-G4N`) added it and parked
  cleanly at Stage 3 admission (`admission.state = "blocked"`, `CF-0078`) behind open
  [PR #428](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/428) (`prune-self-doc-test-copies`, which
  deletes `test_self_doc_runners_launcher.py`). Worktree `apps/holon-agentic-coder/flow-hac-runnerspec-single-source`
  and checkpoint
  `apps/holon-agentic-coder/flow-hac-runnerspec-single-source/.holon/flow/checkpoint-hac-runnerspec-single-source.json`
  preserved for immediate resume once PR #428 merges.
