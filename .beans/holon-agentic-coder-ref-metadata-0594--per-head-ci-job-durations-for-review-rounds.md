---
# holon-agentic-coder-ref-metadata-0594
title: "Measure per-head CI job durations so review-round cost can be attributed (macOS unit leg)"
status: in-progress
type: task
priority: normal
tags:
  - ci
  - measurement
  - holon-flow
  - timing
created_at: 2026-11-27T00:57:23Z
updated_at: 2026-11-27T11:07:53Z
---

## Evidence

- The audit was asked whether review rounds are dominated by the macOS unit job (beans 0400, 0404). It could not be
  answered. Final-head check rollups for PRs #360, #361, #362, #364, #366 show `unit (macos-latest)` at 0.2 to 0.3 min
  and `build (macos-latest)` at 0.1 to 0.2 min (the rollup keeps one run per check, so this is the last head only,
  probably the relevance gate skipping the job). Per-head durations of intermediate heads, which decide how long each
  review round waits, are not in any record the audit can read. PRs had 12 to 25 commits each (#360 25, #362 20, #361
  16, #364 15, #366 12) and one posted review each.
- Status: bean 0400 and 0404 are in-progress. 0404 still has open acceptance items (Workspace survival ceiling, the
  bimodal cause, the cancelled macOS jobs, the closing banner). Three 0400 intents (`macos-unit-only-when-relevant`,
  `-sensitive-paths-only`, `-sharded`) exist in `todo/`; the keeper queue held `0400/macos-unit-sharded` unlaunched from
  00:39Z (see the slot keeper bean).
- Per the audit rule, a step whose time cannot be read is "not measured" and gets a bean.

## Goal

For every flow PR, a table of every head: pushed-at, each job's start and end, the review iteration that waited on it,
and whether the head changed code or only bookkeeping.

## Design

- A read-only script (`gh run list` / `gh api` per head SHA) writes `todo/ci-per-head-<pr>.json` and a summary of median
  and longest job time per job and per head.
- The audit and the flow calibration report call it; the numbers decide whether the macOS leg (0400) or the review loop
  itself sets the wait.
- Heads that changed no code (bookkeeping, calibration commits) are flagged as churn, per the audit's end-state rule.

## Acceptance

- [ ] Script produces per-head, per-job durations for PRs #360 to #366 from GitHub only.
- [ ] Output separates code heads from bookkeeping heads and shows reviewer wait per iteration where the flow log has
      it.
- [ ] Bean 0400 and 0404 progress notes cite the table.
- [ ] Code has no docstrings and no comments except `# why:`; run with `uv run pytest`.
