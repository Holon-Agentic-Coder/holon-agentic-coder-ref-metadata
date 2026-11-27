---
# holon-agentic-coder-ref-metadata-0400
title: "Shorten the CI pipeline: the slowest jobs set every wait in the flow"
status: in-progress
type: task
priority: normal
tags:
  - ci
  - performance
  - holon-agentic-coder
created_at: 2026-11-24T08:30:00Z
updated_at: 2026-11-27T00:56:56Z
---

## Problem

Every flow waits for the pipeline at least twice. Over 33 measured waits the median was 7.9 minutes and the longest 11.9
minutes. The checks that finish last are `Workspace survival (ubuntu-latest)` and `unit (macos-latest)`.

## Goal

- Measure each job's queue time and run time (Bean 0166 has the dashboard) and name the two that set the total.
- Bring the pipeline's wall-clock time down: dependency and image caching, sharding the unit suite, running the macOS
  unit job only for changes that can behave differently there, moving `Workspace survival` off the critical path if it
  cannot be made faster.
- Fail fast inside the pipeline: `fail-fast` is `false` on the unit, make and integration matrices today, so a failed
  leg lets its sibling run to the end. Decide per workflow whether that is still wanted. (Superseded runs are already
  cancelled on pull requests.)

## Acceptance

- [ ] Each pipeline job's queue time and run time is measured, and the two jobs that set the total wall-clock time are
      named.
- [ ] The pipeline's median wall-clock time on full-pipeline heads is lower than the 7.6 min median recorded on
      2026-11-25, with the before and after figures stated.
- [ ] `unit (macos-latest)` run time on code heads is below its 7.0 min median, by dependency and image caching,
      sharding the unit suite, or both, with the measured result stated.
- [ ] `Workspace survival (ubuntu-latest)` is either faster than its 6.3 min median or no longer on the critical path,
      with the measured result stated.
- [ ] A decision is recorded for each of the unit, make and integration workflows on whether `fail-fast` stays `false`,
      and the workflow files match the decision.
- [ ] The macOS unit job runs only for changes that can behave differently there (delivered by PR #319).

## Assumptions

- No numeric target is set in the bean, so the targets are the medians the bean itself records (7.6 min pipeline, 7.0
  min macOS unit, 6.3 min Workspace survival). Validate: the maintainer confirms the baselines are the right bar, or
  states a ceiling.
- "Lower than the median" is read as a measured improvement over a comparable sample of heads. Validate: re-run the
  audit script's measurement on at least 20 post-change heads.
- The macOS gating item is already met by PR #319. Validate: the Progress section and the merge commit `412bed21`.

## Notes

- Logged from Bean 0394 (no unnecessary waiting in the holon flow), on the maintainer's word of 2026-11-24.
- Related: Bean 0168 (unit suite runs 1.7x slower on macOS), Bean 0166 (pipeline duration dashboard), Bean 0300 (CI runs
  once per change).
- No target is set here; the first step is the measurement.

## Audit evidence, 2026-11-25T05:45Z (self-improvement audit, fifth merge #288 to #299)

- Measured after #275 and #278 (74 PR heads, 00:33Z to 05:30Z,
  `todo/self-improvement-audit-2026-11-25a/pipeline-fixes.md`): full pipeline wall median 7.6 min, p90 8.7 min, down
  from 10.8 / 24.2 min before #272. Bookkeeping heads are gated to 0.9 min.
- The critical path is now `unit (macos-latest)`: median 7.0 min, longest 9.5 min, against 3.2 min for
  `unit (ubuntu-latest)` on the same heads. `Test - Stress` (Workspace survival) is second at 6.3 min. Running the macOS
  leg only for changes that can behave differently there would take about 3 min off every code and main-merge head.
- Main-merge heads now cost more than code heads: 28 of 78 heads in the period, 409 runner-min, against 167 runner-min
  for the 13 code heads (see Bean 0458 for the hand syncs behind most of them).

## Progress

- 2026-11-26 06:11Z: macOS part delivered by PR #319
  (https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/319), merged as `412bed21` (flow slug
  `macos-unit-sensitive-paths-only`, plan `P-1795669298-CLA-CO5.5`). Rule: the `unit (macos-latest)` steps after
  `Install uv` run on a pull request only when a changed file (new or old version, deleted or renamed files judged by
  their old path and content) matches a platform-sensitive path or content list (`scripts/macos_relevance_rules.py`);
  otherwise the gate skips them and the job succeeds under the same check name. The leg always runs on push to `main`,
  with the `ci-macos` label, and when the changed-file list is empty or unreadable. Accepted risk: a macOS-only break in
  a file judged neutral is caught by the push-to-main run after merge. Replay share: `1 / 62` merged pull requests #241
  to #314 would skip the macOS leg (1.6%, only #264; 46 runs by `sensitive-content`, 15 by `sensitive-path`), so the
  saving is small on past history. Measured macOS time: the approved code head `b159b7d` ran the full leg in 8.9 min
  (job 05:57:40Z to 06:06:34Z; `Run unit tests` 9.5 min); the bookkeeping-only heads `af89e4c` and `4e9af1d` skipped it
  in about 0.3 min. Replay counts are from the execution record (`executions/E-1795670038-CLA-CO5.5.md`); the PR body's
  "74 pull requests" is not what the replay counted. Superseded attempt PR #315 closed unmerged; its branches and
  worktree were removed after #319 merged.
- Remaining scope (bean stays in-progress): dependency and image caching; sharding the unit suite; moving
  `Workspace survival` off the critical path (or making it faster); the fail-fast decision per workflow.

- 2026-11-26: #315's neutral-list gate (skip the macOS leg when every changed file is platform-neutral) would have
  skipped 0 of 74 merged pull requests #241 to #314, because every flow pull request changes code. Replaced by intent
  `macos-unit-sensitive-paths-only` (sensitive-path rule: run the macOS leg only when a changed file matches a stated
  platform-sensitive path or content list; maintainer choice 2026-11-26). Flow launched 2026-11-26 05:01Z by
  `run_holon_flow.py` (claude-agent / claude-opus-5-5, worktree `flow-macos-unit-sensitive-paths-only`, log
  `todo/flow-macos-unit-sensitive-paths-only.log`). PR #315 is superseded by #319 (closed unmerged; see the 2026-11-26
  06:11Z entry).
- In progress, 2026-11-25: holon flow `macos-unit-only-when-relevant` (scope: the macOS leg only, the
  `unit (macos-latest)` relevance gate), run by `run_holon_flow.py` with claude-agent / claude-opus-5-5 in worktree
  `flow-macos-unit-only-when-relevant`, log `todo/flow-macos-unit-only-when-relevant.log`.
- Stage 1 and Stage 2 done (plan P-1795647426-CLA-CO5.5, EV 34.1). Stage 3 refused for a touch-set overlap with the
  local flow `intent-0371-ledger-fragments-and-promotion` on `.github/workflows/README.md`; the wrapper exited instead
  of waiting (Bean 0468). Resume from the checkpoint once that flow finishes; no `--allow-overlap`.
- 2026-11-25 23:33Z: flow parked at Stage 3 admission. Overlap with `intent-0371-ledger-fragments-and-promotion` (PR
  #310, open, MERGEABLE) on `.github/workflows/README.md`. No `--allow-overlap`. Resume from
  `/Users/thomashan/git/holon-agentic-coder-ref-metadata/apps/holon-agentic-coder/flow-macos-unit-only-when-relevant/.holon/flow/checkpoint-macos-unit-only-when-relevant.json`
  after #310 merges (see Bean 0468 for the wrapper's missing overlap wait).
- 2026-11-26 04:49Z: flow completed through Stage 5 for PR #315
  (https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/315, OPEN, MERGEABLE/CLEAN, head ddb315bf). Review
  approved (iteration 3, head a913aafb); calibration report `P-1795666532-CLA-CO5.5_calibration.md` is in the PR diff;
  final head CI success per the flow summary. Awaiting human merge. Bean stays in-progress until the maintainer merges
  PR #315.

## Audit evidence, 2026-11-26 (flow time audit)

Flow time audit (`todo/flow-time-audit-2026-11-26.md`), all workflow jobs of PRs #296 to #316 (21 PRs, 146 heads with
CI): queue time is negligible (median 2 s, p90 4 s for every job). Run time median / p90: `unit (macos-latest)` 6.0 /
8.8 min, `Workspace survival (ubuntu-latest)` 5.2 / 7.7, `unit (ubuntu-latest)` 3.0 / 4.2, `integration` 2.2 / 2.5,
`build` 1.7 / 2.0, `hygiene` 1.0 / 1.1. Full-pipeline heads take about 8 to 10 min; bookkeeping-only heads are now quick
(Stage 5 CI wait 1.2 to 1.7 min, Bean 0403 working). The approving review iteration of every flow ends when the pipeline
ends (reviewers wait for it, Bean 0478), so the macOS unit leg sets about 6 to 9 min of every flow. Up to 46 superseded
runs per long PR were cancelled (for example 46 of 138 on #308, 40 of 102 on #310).
