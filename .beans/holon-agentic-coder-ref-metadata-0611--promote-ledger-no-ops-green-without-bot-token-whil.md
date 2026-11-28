---
# holon-agentic-coder-ref-metadata-0611
title: "Promote Ledger no-ops green without bot token while 252 pending fragments pile up"
status: completed
type: bug
priority: high
tags:
  - ci
  - ledger
  - holon-agentic-coder
created_at: 2026-11-27T05:18:43Z
updated_at: 2026-11-27T12:33:36Z
---

## Notes

### Evidence (2026-11-27T04:43Z–05:18Z fifth-merge audit)

- On `holon-agentic-coder` `origin/main`, `holon-knowledge/ledger/pending/` has accumulated **252 pending fragment
  files** across `intents/`, `plans/`, and `executions/` (grown to **270** at `0d8d1249f` after PRs `#403`,
  `#406`–`#411`, and **291** at `2a83e4cc7` after PRs `#412`, `#414`, `#416`–`#419`, `#422`, while PR `#413` remains
  halted on `CF-0055`).
- `.github/workflows/promote-ledger.yml` run `45943839152` (`05:06:56Z`) exited `success` in 2 s with notice:
  `Ledger promotion skipped: the repository secret HOLON_LEDGER_BOT_TOKEN is not configured, so the run stays green.`
- Because `promote-ledger.yml` triggers on every `push` to `main` with
  `concurrency: { group: promote-ledger, cancel-in-progress: false }`, burst merges queue multiple runs and GitHub
  cancels intermediate pending runs: **15 of the 20** most recent `Promote Ledger` runs were `cancelled`
  (`04:36Z–04:39Z` and `05:06Z–05:13Z`), and the runs that actually started were all 2-second green no-ops.

### Proposed Change

- Configure `HOLON_LEDGER_BOT_TOKEN` (maintainer/repo secret) OR replace the silent green no-op with an explicit
  non-silent backlog warning/threshold check (e.g., flag in readiness/post-merge when `holon-knowledge/ledger/pending/`
  exceeds a count threshold).
- Debounce `promote-ledger.yml` (schedule + `workflow_dispatch` or `paths: ['holon-knowledge/ledger/pending/**']` with
  post-burst cadence) instead of firing a cancelled no-op run on every individual merge commit.

### Expected Gain & Cost

- Stops 75% (`15/20`) cancelled workflow churn during merge bursts and drains the `252`-file pending ledger backlog on
  `main` so canonical ledgers stay current.
- Cost: tiny workflow edit + secret configuration (or threshold alert).

## Acceptance Criteria

- `.github/workflows/promote-ledger.yml` avoids per-merge cancelled run storms by removing the unguarded `on.push`
  trigger (relying on periodic `schedule` + `workflow_dispatch`, or `paths: ['holon-knowledge/ledger/pending/**']` with
  debounced cadence).
- When `HOLON_LEDGER_BOT_TOKEN` is absent, `.github/workflows/promote-ledger.yml` checks out the pending directory count
  (or emits an explicit `::warning::` naming the pending fragment backlog and action required rather than a silent
  `::notice::` green no-op).
- Unit tests in `apps/sandbox-executor/tests/test_promote_ledger_workflow.py` assert the workflow triggers, non-silent
  warning behavior, and self-explaining YAML compliance via `uv run pytest`, and `uv run task lint` passes cleanly.

## Resolution

Delivered via [PR #424](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/424) and merged into `main`
(`c03385aff`):

- **Key Architectural Deliverables**:
  - Removed the unguarded `on.push` trigger and obsolete job-level `if:` condition from
    `.github/workflows/promote-ledger.yml`, leaving daily `schedule` (`cron: "41 3 * * *"`) and `workflow_dispatch`
    triggers so merge bursts no longer trigger cancelled run storms, and brought all YAML comments into `# why:`
    self-explaining compliance.
  - Added a read-only sparse checkout of `holon-knowledge/ledger/pending` and a non-failing `::warning::` step (plus job
    summary entry) reporting the pending fragment count and required `HOLON_LEDGER_BOT_TOKEN` maintainer action whenever
    `HOLON_LEDGER_BOT_TOKEN` is unset.
  - Updated `.github/workflows/README.md` (`## Workflows` and `## Ledger Promotion`) to document the schedule/dispatch
    triggers and missing-token pending-backlog warning.
  - Updated `apps/sandbox-executor/tests/test_promote_ledger_workflow.py` to verify schedule/dispatch-only triggers,
    sparse checkout + `::warning::` alert behavior, secret scoping across checkout steps, README alignment, and
    self-explaining YAML compliance.
- **Verification & Tests**:
  - Targeted workflow tests
    (`uv run pytest apps/sandbox-executor/tests/test_promote_ledger_workflow.py apps/sandbox-executor/tests/test_workflow_triggers.py`):
    `46 passed, 0 failed` (`0.37s`).
  - Repository lint (`uv run task lint` covering `uv lock --check`, `ruff check`, `ruff format --check`, module budgets,
    and `scripts/check_self_explaining.py`): passed; Prettier check on modified markdown files passed.
  - Full unit test suite (`uv run task test`): `10809 passed, 0 failed, 7 skipped` (`64.33s`).
- **Holon Flow Traversal**: Completed all 5 stages (`I-1795780652-promote-ledger-debounce-alert` ->
  `P-1795780678-ANA-G4N` -> `E-1795780889-ANA-G4N` -> Stage 4 review `APPROVED 3/3` (`1` full review, `0` churn) ->
  Stage 5 calibration: `100.0%` Touch Set precision/recall, `EV_pred = 55.88`, `EV_actual = 76.58`, calibrated `+20.70`
  EV).
