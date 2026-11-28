---
# holon-agentic-coder-ref-metadata-0534
title: "Eliminate silent except-pass catches, library sys.exit calls, and GitHub/Git adapter error gaps"
status: in-progress
type: bug
priority: normal
tags:
  - holon-agentic-coder
  - resilience
  - error-handling
created_at: 2026-11-26T13:35:00Z
updated_at: 2026-11-28T00:03:59Z
---

## Problem

Three `except Exception: pass` blocks silently swallow failures (including temporary credential cleanup), library
modules call `sys.exit(1)` instead of raising domain exceptions, `GitHubAdapter` bypasses `parse_gh_json` and drops
`self.proxy_env` in `gh()`, and `git.py` raises untyped `RuntimeError` exceptions.

## Evidence

- Silent `except Exception: pass` at `apps/sandbox-executor/src/sandbox_executor/launcher/containers.py:211` (temp
  credential cleanup), `agent_runner.py:433`, and `flow/pipeline.py:430` (among 133 broad `except Exception` blocks).
- `sys.exit(1)` inside library modules: `agent_runner.py:380,686` and `launcher/mounts.py:84`.
- `flow/github/adapter.py:91` calls raw `json.loads` rather than `parse_gh_json`; `GitHubAdapter.gh()` at lines
  `114-116` omits `self.proxy_env`.
- `git.py:43`: raises generic `RuntimeError` instead of a structured `GitCommandError`.

## Proposed Change

1. Replace the 3 silent `except Exception: pass` blocks with narrowed exception types and explicit warning/cleanup
   logging (and triage/narrow the highest-risk remaining broad `except Exception` catches).
2. Replace `sys.exit(1)` in `agent_runner.py` and `launcher/mounts.py` with typed exceptions handled at the CLI
   entrypoint boundary.
3. Update `flow/github/adapter.py:91` to use `parse_gh_json` and pass `self.proxy_env` through `GitHubAdapter.gh()`.
4. Introduce a typed `GitCommandError` in `git.py` carrying `returncode`, `cmd`, and `stderr`.

## Acceptance Criteria

- Zero silent `except Exception: pass` blocks remain in `src/sandbox_executor/`.
- No library module calls `sys.exit(...)` outside CLI/script entrypoints.
- `GitHubAdapter.gh()` respects `proxy_env` and surfaces malformed `gh` JSON via `parse_gh_json`; `git.py` raises
  `GitCommandError`.

## Notes

- Target repository: `holon-agentic-coder` (evaluated at `HEAD f1e18bcd`).
- Source: 2026-11 ecosystem architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).

## Flow

- **Slice 1 (`hac-silent-except-agent-runner`):** Merged into `main` via
  [PR #453](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/453) (`579c13e245`) via
  `todo/intent-0534-silent-except-agent-runner.json` (`todo/intent-coverage-0534.json`), replacing the silent
  `except Exception: pass` in `agent_runner.py` with narrowed handling and tests in `tests/test_agent_runner.py`
  (`16/16` CI checks `SUCCESS`).
  - **Readiness (`pr_readiness.py --record`)**: Head `df65de5f`, Consensus `APPROVED` (`8e241c9e`), Stage 5 calibration
    `calibrate=success` (`plans/I-1795817858-hac-silent-except-agent-runner/P-1795817889-ANA-G4N_calibration.md`),
    `gates: consensus=ok, calibration=ok, pipeline=ok`. Bean stays `in-progress` for remaining catches, `sys.exit`,
    adapter, and `git.py` slices.
- Remaining `launcher/containers.py` / `flow/pipeline.py` except-pass catches, `sys.exit(1)` refactors, and
  `GitHubAdapter` / `GitCommandError` slices are deferred (`todo/intent-coverage-0534.json`).
- **Audit update (`2026-11-28T00:01Z`, `27b4197e7`):** `PR #444` (`ec16d88c3`, narrow broad excepts) + `PR #453`
  (`579c13e24`, `agent_runner.py`) reduced `except Exception` in `src/` from `137` (`3` silent `pass`) to **`131` (`2`
  silent `pass` at `flow/pipeline.py:392` and `launcher/containers.py:255`)**.
