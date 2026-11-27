---
# holon-agentic-coder-ref-metadata-0611
title: "Promote Ledger no-ops green without bot token while 252 pending fragments pile up"
status: todo
type: bug
priority: high
tags:
  - ci
  - ledger
  - holon-agentic-coder
created_at: 2026-11-27T05:18:43Z
updated_at: 2026-11-27T05:18:43Z
---

## Notes

### Evidence (2026-11-27T04:43Z–05:18Z fifth-merge audit)

- On `holon-agentic-coder` `origin/main`, `holon-knowledge/ledger/pending/` has accumulated **252 pending fragment
  files** across `intents/`, `plans/`, and `executions/`.
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

## Resolution
