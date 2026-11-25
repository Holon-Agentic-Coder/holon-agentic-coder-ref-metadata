---
# holon-agentic-coder-ref-metadata-0451
title:
  "dev-env CI lacks ci_bookkeeping_gate and runs test-unit (macos-latest) serially, causing 15+ min Stage 5 overruns"
status: todo
type: feature
priority: high
tags:
  - ci
  - dev-env
  - stage-5
  - pipeline
  - performance
created_at: 2026-11-25T05:07:00Z
updated_at: 2026-11-25T05:07:00Z
---

# `dev-env` CI lacks `ci_bookkeeping_gate` and runs `test-unit (macos-latest)` serially, causing `15+ min` Stage 5 overruns

## Summary

`thomashan/dev-env` GitHub Actions workflows lack a bookkeeping-only path gate (`ci_bookkeeping_gate`, equivalent to
`holon-agentic-coder`'s `.github/actions/bookkeeping-gate/action.yml`) and run `test-unit.yml`
(`uv run --extra test pytest -v -l --tb=short -m "not network"`) serially without `pytest-xdist`
(`-n auto --dist worksteal`). As a result, every Stage 4/Stage 5 bookkeeping commit (`holon-knowledge/` / `executions/`
/ `plans/` / `intents/` / `.holon/` only) triggers the full matrix including a `14.4–15.1 min` serial `macos-latest`
unit run, pushing Stage 5 far over its `10 min` budget.

## Evidence

- `/Users/thomashan/git/dev-env/main/.github/workflows/test-unit.yml`: no `bookkeeping-gate` step; line 44 executes
  `uv run --extra test pytest -v -l --tb=short -m "not network"` serially (no `-n auto --dist worksteal`).
- **`thomashan/dev-env#42` (`tmux-focus-events-on`, 2026-11-25T04:14Z–04:48Z):**
  - Head `ef1fbd76` (Stage 5 calibration bookkeeping commit only, zero code changes) ran all `5` workflows (`15.45 min`
    / `926.88 s` `final_head_ci` wait, `04:32:28Z..04:47:55Z`), driven by `test-unit (macos-latest)` running `203` tests
    serially in `862.45 s` (`14.4 min`, vs `2.3 min` on Ubuntu).
  - Total Stage 5 duration hit **`18.63 min`** (`04:29:19Z..04:48:00Z`, nearly `2x` the `10 min` budget), vs `0.28 min`
    Stage 1 + `2.53 min` Stage 2 + `4.85 min` Stage 3.
  - Earlier bookkeeping head `b1dc27bb` on `#42` also spent CI cycles until cancelled by `ef1fbd76` at `04:31:59Z`.
- **`thomashan/dev-env#41` (`tmux-shift-enter-extkeys`):**
  - Bookkeeping head `d6fb465c` similarly waited `15.1 min` on serial macOS unit CI.

## Proposed Change

1. Add a shared bookkeeping-gate composite action (matching `holon-agentic-coder`'s
   `.github/actions/bookkeeping-gate/action.yml`) to `thomashan/dev-env/.github/workflows/` (`test-unit.yml`,
   `test-converge.yml`, `make.yml`, `test-hygiene.yml` as appropriate) so commits touching only `holon-knowledge/`,
   `.holon/`, and `.md` docs skip heavy CI suites in `< 60 s` when prior code head passed or non-code files changed.
2. Add `pytest-xdist` (`-n auto --dist worksteal`) to `test-unit.yml` line 44 (verifying macOS test isolation / fixture
   safety first) to cut `macos-latest` unit runtime from `14.4 min` down toward Ubuntu speed (`~2–4 min`).

## Expected gain

Cuts `dev-env` Stage 5 `final_head_ci` waits on bookkeeping-only heads from **`~15.5 min` to `~1 min`** (bringing
`dev-env` Stage 5 well under the `10 min` budget) and speeds up genuine code-head `macos-latest` unit runs
substantially.

## Cost

Small-to-medium: CI workflow action + `pytest-xdist` adoption in `thomashan/dev-env` (via a `dev-env` Holon flow; verify
macOS tests pass under `-n auto`).

## Notes

- Target repo change through the Holon flow (`thomashan/dev-env`).
- Reference implementation: `apps/holon-agentic-coder/main/.github/actions/bookkeeping-gate/action.yml`.
- Audit source: `2026-11-25T05:07Z` fifth-merge self-improvement audit.
