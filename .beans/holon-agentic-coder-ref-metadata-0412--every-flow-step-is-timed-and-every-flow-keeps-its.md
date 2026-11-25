---
# holon-agentic-coder-ref-metadata-0412
title: "Every flow step is timed and every flow keeps its log: the steps the audit could not measure"
status: todo
type: feature
priority: normal
tags:
  - flow
  - harness
  - logging
  - timing
  - holon-agentic-coder
created_at: 2026-11-24T11:00:00Z
updated_at: 2026-11-25T03:08:00Z
---

## Why

The audit protocol requires a timing table of every step of the flow and says missing timing is itself a finding. These
steps could not be measured from the evidence.

## Evidence

Logged by the self-improvement audit of 2026-11-24 (first audit, period 2026-11-21 to 2026-11-24T11:00Z). The scripts
and their output are in the git-ignored audit folder `todo/self-improvement-audit-2026-11-24/`.

Not measured, and why:

| Step                                                                                        | Why it could not be measured                                                        |
| :------------------------------------------------------------------------------------------ | :---------------------------------------------------------------------------------- |
| Pre-flight (credential probe, image check, worktree creation)                               | the wrapper's own lines carry no timestamp                                          |
| Each push (execution branch, resolver, ledger rows, calibration)                            | no start or end line; pushes are folded into the turn around them                   |
| Each conflict probe and each merge of the target                                            | only the outcome is logged, not its start                                           |
| Each reviewer of the ensemble                                                               | only the ensemble's end is logged; the slowest reviewer is unknown                  |
| The overlap wait inside a run                                                               | the engine exits on refusal and the wait shows only as a gap before the next launch |
| Idle between a stop and its resume when the resume is written to another log                | logs are per launch name, not per flow                                              |
| 22 of the 47 merged pull requests (all 8 of `holon-coherence`, 14 of `holon-agentic-coder`) | no flow log was kept at all; their review iterations could not be counted           |

- The wrapper prints to its stdout; whether a log exists depends on how the launching subagent redirected it. The
  `holon-coherence` flows of 2026-11-24 left none.

## Proposed change

1. The wrapper owns its log: it writes `flow-<slug>.log` itself in append mode, every line prefixed with a UTC
   timestamp, including its own pre-flight lines, whatever runtime launched it.
2. The engine logs a start and an end line, with the elapsed seconds, for every push, conflict probe, merge of the
   target, reviewer and wait, and records the same in the checkpoint's step log (Bean 0383 Goal 4 builds the per-stage
   breakdown on these).
3. The overlap wait is logged as a wait with its start and end, not as a series of refused runs.

## Expected gain

The next audit can time every step for every flow, and a flow suggestion can name the time it saves. No direct time
saving.

## Cost

Small: wrapper (`.agents/skills/holon_flow/scripts/run_holon_flow.py`) and logging calls in the engine.

## Notes

- Overlap: Bean 0385 (the log stays empty until the run ends) owns the flushing; Bean 0383 Goal 4 (Stage 5 timing
  breakdown) is a subset of the timing this bean records. This bean owns the timing for all other steps.
- Related: Bean 0385 (log stays empty until the run ends; buffering), Bean 0383 Goal 4 (timing breakdown in the flow
  summary).

## Audit evidence, 2026-11-24T12:58Z (self-improvement audit, fifth merge)

- Flows launched from the Antigravity session (Beans 0265, 0399, 0376 and 0153, and the flows of PR #274 and coherence
  PRs #53 to #55) wrote no `todo/flow-<slug>.log`. For them only stage start and end could be read, from the
  checkpoints; see Bean 0423.
- Checkpoint timing disagrees with itself: `flow-intent-0393-preflight-retry` records calibrate `start_time` 12:11:32Z,
  `end_time` 12:11:45Z and `elapsed_seconds` 641.9.
- An executor turn is one opaque step. Bean 0405's Stage 3 took 125.4 minutes; its notes list 39 test runs with about 15
  minutes of reported pytest time and a mutant run that hung until the tool's 10-minute limit, so roughly 95 minutes
  were model time, but nothing records it. Add: the engine logs each tool call's start and duration from the runner's
  event stream (or at least the summed tool time and model time per turn).

## Audit evidence, 2026-11-25T00:28Z (self-improvement audit, fifth merge)

- **19 of 24 active flows** (`18` `holon-agentic-coder` flows + `holon-coherence#56`) left **no** `todo/flow-<slug>.log`
  entries between `2026-11-24T12:59Z` and `2026-11-25T00:19Z` (only 5 flows wrote logs).
- `checkpoint-split-cli-init-modules.json` recorded `review: status=failed start=None end=None elapsed=1.161`, leaving
  failed Stage 4 entry timestamps unmeasured.
- `todo/flow-unit-suite-slowest-tests-speedup.log` logged container error timestamps in `+11:00` local time inside a
  `[2026-11-24T23:52:07Z]` prefix (`time="2026-11-24T23:52:07+11:00"`), mixing UTC and local timezones.
- Stage 5 `calibrate.elapsed_seconds` includes `merged_head_ci` + `final_head_ci` waits while `start_time..end_time`
  covers only `run_calibrate` (`config-env-self-doc`: `2.6 min` vs `5.0 min`; `timing-gate-judges-test-time`: `0.3 min`
  vs `30.8 min`).
- Pre-flight, individual pushes, conflict probes/merges, per-reviewer turns, Stage 4 ledger commits, Stage 3 re-plans,
  and Stage 4 empty-diff/PR guards remain unmeasured in checkpoints.

## Audit evidence, 2026-11-25T02:54Z (self-improvement audit, fifth merge)

- **12 of 14 active flows** (`11` Antigravity flows + `split-cli-init-modules`) left **no** `todo/flow-*.log` entries
  between `2026-11-25T00:28Z` and `02:54Z` (only `flow-timing-gate-judges-test-time.log` and
  `flow-workspace-survival-job-parallel.log` logged in the window; wrapper pre-flight lines in the latter carry no
  timestamps).
- Stage 5 `calibrate.end_time` (`calibrate.py:300`) is recorded before `publish_calibration` and `final_head_ci` wait,
  so `calibrate.elapsed_seconds` (`3.9–12.6 min`) diverges from `start_time..end_time` (`2.6 min` across `11` flows).
- Pre-flight, individual pushes, target conflict merges, per-reviewer latencies inside the `~7.0 min` ensemble, and
  executor inner tool-vs-model split remain unmeasured.
