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
updated_at: 2026-11-28T00:03:58Z
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

## Audit evidence, 2026-11-25T04:02Z (self-improvement audit, fifth merge)

- **`1 of 2` active flows (`no-unneeded-full-review`)** left **no** `todo/flow-*.log` in the `02:54Z–03:54:45Z` window.
- **`todo/flow-workspace-survival-job-parallel.log`:** wrapper pre-flight lines (`lines 1–11`, `88–98`) still lack UTC
  timestamps; `calibrate.end_time` (`03:37:54Z`) again preceded `final_head_ci` wait (`03:38:05Z–03:39:13Z`); and
  `End-of-flow sync` re-entry (`03:39:20Z–03:54:45Z+`) is unrecorded in `checkpoint.context.logs` and
  `checkpoint.stage_results` while running (see Bean `0445`).
- Pre-flight, individual pushes, conflict merges, per-reviewer latencies inside the `3.7 / 9.5 / 4.2 min` ensembles, and
  executor inner tool-vs-model split (`42.1 min` Stage 3) remain unmeasured.

## Audit evidence, 2026-11-25T05:07Z (self-improvement audit, fifth merge #290–#294)

- **`dev-env#42` (`tmux-focus-events-on`) and `0407` (`no-unneeded-full-review`)** left no `todo/flow-*.log` in the
  window, leaving pre-flight (credential probe, image check, worktree creation) `not measured`.
- Individual git pushes, conflict probe/merge timings, per-reviewer latencies inside the `4.40 / 4.13 min` (`hac#308`)
  and `14.85 min` (`dev-env#42`) ensembles, and inner tool-vs-model splits inside Stage 3 (`4.80 min` on `dev-env#42`)
  and Stage 4 resolvers (`27.02 min` + `4.47 min` on `hac#308`) remain unmeasured.
- `review_local` drops `TestMeasurement.output_excerpt` and failing test node IDs from logs and `executions.jsonl`
  (tracked separately in Bean `0450`).

## Audit evidence, 2026-11-25T05:41Z (self-improvement audit, fifth merge #295–#299)

- New flows `0371` (`todo/flow-ledger-fragments-and-promotion.log`) and `0438`
  (`todo/flow-calibration-merge-adapted-file.log`) wrote timestamped stage logs, yet wrapper pre-flight lines
  (`lines 1–13` in both logs) still carry no UTC timestamps.
- Antigravity flows (`#295–#301` and `0407`) still leave no `todo/flow-*.log` (e.g., `#301`'s `05:32:48Z` `origin/main`
  merge); individual git pushes, conflict merges, per-reviewer latencies inside `4.47 / 3.83 min` ensembles (`#308` i4,
  `#309` i1), and inner tool-vs-model splits inside `4.98 min` Stage 3 (`#309`) and `7.45 / 15.20+ min` Stage 4
  resolvers (`#308`) remain unmeasured.

## Audit evidence, 2026-11-25T05:45Z (self-improvement audit, fifth merge #288 to #299)

- Antigravity flows still write no wrapper log. The ledger rows give iteration times (13 iterations, median 7.5 min) and
  resolver times (2, median 3.2 min). They give no per-reviewer split, no push times and no idle time.
- Gaps between checkpoint stages that nothing records: plan end to execute start of 76 to 109 s on all 8 Antigravity
  flows (median 86 s; Claude flows go straight to admission, 16 to 44 s); execute end to review start of 28.9 min on
  #308 (03:10:31Z to 03:39:28Z) and 6.0 min on `decomposition-rule-self-doc`; review end to calibrate start of 8.0 min
  on #308 and 7.5 min on `github-pr-merge-self-doc`.
- Hand `resolve-conflict` syncs done outside a flow (13 in the period, Bean 0458) leave no timing record at all; only
  commit times show them.

## Audit evidence, 2026-11-25T06:05Z (self-improvement audit, fifth merge #300–#304)

- Wrapper pre-flight (`lines 1–13` of `todo/flow-ledger-fragments-and-promotion.log` and
  `todo/flow-calibration-merge-adapted-file.log`) still prints no UTC timestamps, leaving wrapper startup time
  unmeasured.
- Stage 4 inner sub-steps remain opaque:
  - Per-reviewer latencies inside ensembles (`#309` Iter 1 `3.9 min`, Iter 2 `10.1 min`; `#308` Iter 4 `8.4 min`) are
    not recorded individually.
  - Inside `#309`'s **`6.58 min`** Markdown-only resolver pass (`05:40:17Z..05:47:06Z`) and `#308`'s **`37+ min`**
    active Iter 4 resolver (`d7a5f5ec82a1` since `05:25:12Z`), container boot vs LLM turns vs `lint`/`pytest`
    verification time are unmeasured.
  - Individual git push latencies and exact `review_local` wall duration (vs logged test rate/verdict) remain
    unmeasured.
- On `#309`, Stage 5 calibration work (`05:57:50Z..06:00:26Z`, `2.60 min`) vs `chore(calibration)` push/head settle
  (`11 s` before `06:00:37Z` CI registration wait) vs `final_head_ci` inner check registration (`18 s`) + polling
  (`48.93 s`, total `3.98 min` stage) must still be reconstructed by grepping text logs instead of structured step
  metrics in checkpoint JSON.
- On `#300–#304` (worktrees already pruned) and live `0407` (idle since `02:41:40Z`), Antigravity flow wrapper logs do
  not exist on disk, leaving exact pre-flight, admission-poll, push, and inter-stage idle gaps unmeasured.

## Audit evidence (2026-11-26T03:50Z, fifth-merge audit)

- Still unmeasured in `2026-11-25T22:49:00Z..2026-11-26T03:50:09Z`:
  - Wrapper pre-flight timestamps before `Pipeline run initiated` (`run_holon_flow.py`).
  - Per-reviewer latency inside the Stage 4 ensemble and the inner `review_local` reviewer-turn vs CI-wait split.
  - Individual Stage 4 git push and conflict-merge durations.
  - Missing flow logs for `holon-coherence#56` and `thomashan/dev-env#42`–`#44`, plus the final `36+ min` of
    `todo/flow-macos-unit-only-when-relevant.log` (`03:01:05Z..03:37:15Z+` buffered under `0385`).

## Audit evidence, 2026-11-26 (flow time audit)

Instrumentation gaps from section 4 of `todo/flow-time-audit-2026-11-26.md`:

- Wrapper log lines carry no timestamps.
- Per-reviewer timing is missing; only the ensemble end is logged.
- Executor and resolver test runs and pushes inside agent turns are not logged.
- `executions.jsonl` rows have no turn durations or token counts.
- No flow log exists for the antigravity flows #296 to #307 or for #316 (0-byte log; Bean 0385).

## Audit evidence, 2026-11-27T07:49Z (fifth-merge audit)

- **`10/10` newer `holon-coherence` flows (`#59`–`#66`, plus running/parked Coherence flows)** left **no**
  `todo/flow-<slug>.log` file on disk; only `checkpoint-*.json` `context.logs` captured engine events, losing wrapper
  pre-flight lines and Stage summaries.
- `todo/flow-self-doc-tests-49.log` (`#408`) stopped at `05:22:54Z` (line 204), while `8` subsequent `--from-stage`
  resumes (`05:31:53Z`–`06:32:14Z`) logged only to `checkpoint-self-doc-tests-49.json`.
- Still `not measured` in `05:19:35Z`–`07:49:25Z`: wrapper pre-flight before `Pipeline run initiated`,
  `stage5_ci_reg_wait`, per-reviewer latencies inside Stage 4 ensembles (`44` ensemble runs), resolver inner splits
  (container boot vs LLM turns vs local pytest/lint vs push), and hand pre-merge `origin/main` syncs (`#403`, `#406`,
  `#407`, `#409`, `#410`, `#411`).

## Audit evidence, 2026-11-27T10:55Z (fifth-merge audit)

- **`100%` of flows launched in `07:29Z–10:49Z`** (`#67`–`#75`, `#412`–`#415`, `0538`, `0617`, `0619`, `0615`, `0616`,
  `0621`, `0623`, `0527`, `0599`) left **no** `todo/flow-<slug>.log` file on disk; only `checkpoint-*.json`
  `context.logs` captured engine events, losing wrapper pre-flight lines and Stage summaries (and pruned flows `#68`,
  `#69`, `#71`, `#75`, `#72`, `#73`, `#74` lost their checkpoint logs once post-merge pruned their worktrees).
- Still `not measured` in `07:49:25Z`–`10:55Z`: wrapper pre-flight before `Pipeline run initiated`, per-reviewer
  latencies inside Stage 4 ensembles (`8` ensemble runs), resolver inner splits (`5` runs), Stage 5
  `publish_calibration` vs `stage5_cal_work` split, and post-merge pruned flow timings when no `todo/flow-*.log` exists.

## Audit evidence, 2026-11-27T11:54Z (fifth-merge audit)

- **`0/14` flows active or completed in `10:49Z–11:47Z`** wrote any `todo/flow-*.log` entries (newest `todo/flow-*.log`
  mtime on disk remains `06:04Z`), and `post-pr-merge` pruned the worktrees for 6 of the 7 merged HAC PRs (`#412`,
  `#414`, `#416`–`#418`, `#422`), leaving only git commit timestamps and GitHub PR metadata for those flows.
- Still `not measured` in `10:49Z–11:54Z`: wrapper pre-flight (`0` logs), per-reviewer latencies inside `13` Stage 4
  ensemble runs, resolver inner splits (`4` runs), Stage 5 `ci_reg_wait` vs `publish_calibration` splits (`7` runs), and
  token usage (tracked separately in Bean `0629`).

## Audit evidence, 2026-11-27T15:46Z (fifth-merge audit)

- **`5/8` merged PRs (`HAC #415`, `HAC #424`, `COH #67`, `COH #84`, `COH #85`)** left **no** `todo/flow-*.log` file on
  disk (only `HAC #425` `todo/flow-0601.log`, `HAC #426` `todo/flow-0153-self-doc-tests-49.log`, and `COH #83`
  `todo/flow-0528.log` were preserved).
- Still `not measured` in `12:14Z–15:46Z`: wrapper pre-flight (`8/8` flows), Stage 1 start/duration (`5/8` unlogged),
  Stage 3 admission wait & target-sync split (`5/8` unlogged), Stage 4 per-reviewer/resolver inner splits (`5/8`
  unlogged; `#415` iter-2 active review vs `~104 min` quota idle unseparated in commit timestamps), and per-turn LLM
  tokens (`8/8`, Bean `0629`).

## Audit evidence, 2026-11-28T00:01Z (fifth-merge audit)

- **`27/31` merged PRs** (`19/23` HAC `#428..#447, #452..#455` + `8/8` Coherence `#86..#88, #90..#94`) left **no**
  `todo/flow-*.log` file on disk (only `flow-0368.log`, `flow-hac-provider-cooldown.log`,
  `flow-tests-fewer-git-calibrate.log`, and `flow-tests-fewer-git-review-decomp.log` were preserved since `15:55Z`), and
  post-merge pruned their worktrees/checkpoints.
- Leaving `not measured` across `27/31` flows: Pre-flight (`31/31` unlogged in wrapper), Stage 1 (`27/31`), Stage 3
  admission wait (`27/31`), Stage 4 inner reviewer/resolver/CI splits (`27/31`), and the `~838.5 min` unexplained
  `18:06Z–20:51Z` idle gap across `HAC #442` (`145.6m`), `#443` (`173.5m`), `#444` (`169.9m`), `#448` (`171.3m`), `#449`
  (`178.3m`) (only `#448`/`#449` had logs showing `18:06Z -> 20:51Z` stop/resume).
