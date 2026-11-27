---
# holon-agentic-coder-ref-metadata-0634
title: "Coherence: migrate remaining 36 env reads to CoherenceSettings and bound wire-log disk"
status: in-progress
type: task
priority: normal
tags:
  - holon-coherence
  - config
  - resilience
  - refactor
created_at: 2026-11-27T12:12:09Z
updated_at: 2026-11-27T17:45:05Z
---

## Notes

### Evidence (2026-11-27 fifth-merge Coherence audit, `4a02926b`)

- Bean `0529` closed after [PR #81](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/81) (`ffb48044`,
  `settings.py`) and [PR #82](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/82) (`4a02926b`,
  `Dockerfile`), yet two acceptance items from `0529` remain incomplete in `holon-coherence@4a02926b`:
  1. **36 direct `os.getenv`/`os.environ` call sites across 11 `src/` modules outside `settings.py`** (`settings.py`
     currently serves only `commands/runner.py`, `commands/web_token.py`, and `ringer_orchestrator.py`):
     - `commands/agents.py:198,201,221,246`, `commands/ca.py:35`, `commands/docker_ops.py:145`,
       `commands/metrics.py:56,83,219`, `commands/start.py:142,370,385,401`
     - `container/lifecycle.py:58,154,160,162,496`, `host_local.py:219,255`
     - `mitm_addon.py:87` (import-time `CACHE_DIR` freeze), `proxy/addon.py:72,200,213`
     - `proxy/wire_log.py:43,48,52,54,87,147` (import-time `WIRE_LOG_DIR` freeze + duplicated bool parsing)
     - `proxy/steps/route_local_target.py:41`, `proxy/steps/serve_dashboard.py:75,76,91`,
       `proxy/steps/wire_record.py:32,33`
  2. **Wire-log disk rotation & duplicate `turn_*.json` / `transactions.jsonl` overhead** in `proxy/wire_log.py`
     (`PR #69` bounded `_pending_wire_log_futures`, but disk files still grow unbounded).

### Proposed Change

1. Expand `CoherenceSettings.from_env()` in `src/holon_coherence/settings.py` to cover the remaining env vars
   (`CACHE_DIR`, `WIRE_LOG_DIR`, `ENABLE_WIRE_LOGGING`, `WIRE_LOG_MAX_PENDING`, `HOLON_PASSIVE_MONITORING`,
   `COHERENCE_TOKEN_REDUCTION`, `HOLON_CONTAINER_NAME`, `HOLON_IN_CONTAINER`, `HOLON_LOCAL_LLM_BASE`,
   `HOLON_WIRE_LOG_BASE_DIR`, `HOLON_COHERENCE_API_TOKEN`, `HOLON_COHERENCE_WEB_PASSWORD`, `AGY_MODEL`,
   `HOLON_LOCAL_MODEL`, `HOLON_AGENT_ID`, `HOLON_ROLE`, `HOLON_WEB_INSPECTOR`) and migrate the 11 remaining modules,
   eliminating import-time freezes in `mitm_addon.py` and `proxy/wire_log.py`.
2. Add bounded disk rotation / pruning for wire logs in `proxy/wire_log.py` (with unit tests).

### Expected Gain & Cost

- Completes single-source env configuration and eliminates import-time env freezes and unbounded wire-log disk growth.
- Cost: 2 focused slices (~150 lines + unit tests).

## Acceptance Criteria

- [ ] All runtime `os.getenv` / import-time env freezes across the 11 remaining `src/holon_coherence/` modules route
      through `CoherenceSettings.from_env()` with unit tests in `tests/test_settings.py`.
- [ ] Wire-log disk output in `proxy/wire_log.py` enforces bounded size/file retention with unit tests.
- [ ] `uv run pytest` and `uv run task lint` pass with zero docstrings or comments and untouched `module_budgets.json`.

## Flow

- **Slice 1 (`2026-11-27`, `coherence-proxy-settings-env`):** Migrates env reads across the 6 proxy/addon modules
  (`mitm_addon.py`, `proxy/addon.py`, `proxy/wire_log.py`, `proxy/steps/wire_record.py`,
  `proxy/steps/serve_dashboard.py`, `proxy/steps/route_local_target.py`) through `CoherenceSettings.from_env()` in
  `settings.py`, tested in `tests/test_settings.py`, `tests/proxy/test_wire_log.py`, `tests/proxy/test_steps.py`, and
  `tests/test_mitm_addon.py` (closed halted PR #89 after Stage 4 `touch_set_violation` on `tests/proxy/test_steps.py`
  and re-cut cleanly with expanded scope per `CF-0074`). Completed all 5 stages via `antigravity-agent`/`gemini-4-neon`
  in `apps/holon-coherence/flow-coherence-proxy-settings-env`
  (`.holon/flow/checkpoint-coherence-proxy-settings-env.json`):
  [PR #91](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/91)
  (`I-1795799285-coherence-proxy-settings-env/P-1795799308-ANA-G4N/E-1795799527-ANA-G4N/_`), consensus approved,
  calibration included (`plans/I-1795799285-coherence-proxy-settings-env/P-1795799308-ANA-G4N_calibration.md`, predicted
  EV `-1.06`, actual EV `0.19`, delta `+1.25`), `MERGEABLE`/`CLEAN`, 10/10 CI checks green, awaiting human merge.
  Remaining `commands/*`, `host_local.py`, `container/lifecycle.py`, and wire-log disk retention are deferred to Slice 2
  (`todo/intent-coverage-0634.json`).
- **Slice 2 (`2026-11-27`, `coherence-commands-settings`):** Migrates `HOLON_PROXY_PORT`, `HOLON_LOCAL_LLM_BASE`, and
  `HOLON_COHERENCE_WEB` in `commands/agents.py` and `commands/start.py` through `CoherenceSettings.from_env()` without
  modifying `settings.py`, verified in `tests/commands/test_agents.py`, `tests/commands/test_start.py`, and
  `tests/commands/test_start_web.py` (`todo/intent-0634-coherence-commands-settings.json`). Remaining `commands/ca.py`,
  `commands/metrics.py`, `host_local.py`, `container/lifecycle.py`, and wire-log disk retention stay deferred until open
  PRs `#91` and `#87` merge.

## Resolution
