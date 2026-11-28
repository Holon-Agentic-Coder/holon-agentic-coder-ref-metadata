---
# holon-agentic-coder-ref-metadata-0472
title: "Flow runner does not refuse a second run on the same intent and does not reap its children after a halt"
status: completed
type: bug
priority: high
tags:
  - flow
  - harness
  - stage-4
created_at: 2026-11-25T23:35:26Z
updated_at: 2026-11-26T22:58:29Z
---

## Problem

Observed on intent 0405 (`workspace-survival-job-parallel`, resume from `review`, PR #308):

1. Several `run_holon_flow.py --from-stage review` invocations for the same intent and the same `flow-<slug>` worktree
   ran at once. Nothing refused the second or third run or took a lock on the intent, checkpoint, or worktree. Each run
   launched its own Stage 4 resolver container with the worktree mounted read-write, so the runs wrote into the same
   tree while the target-sync check ran.
2. After a run printed "Holon flow exited with non-zero code 1" and "Pipeline halted", its `holon flow` process stayed
   alive for more than seven minutes at 0% CPU, and its `docker run` client and resolver container kept running. The
   wrapper's exit did not stop or reap the children.
3. The resulting "target sync blocked: the worktree has uncommitted tracked changes" failure on `flow_start` (the same
   symptom as 0432) came from these racing writers, not from a dead resolver turn. Once the duplicates were stopped the
   tree was clean at the same HEAD and a single run proceeded.

## Fix direction

- Take an advisory lock per intent slug and worktree (for example a lock file under the worktree's `.holon/flow/`), and
  refuse a second `--from-stage` or fresh run with a message naming the live pid.
- On a halted run, terminate the `holon flow` child process group and the `docker run` clients it started, and let
  `docker stop` reach the containers that mount the worktree.
- Make the `flow_start` dirty-tree check ignore a tree whose writers are the current run's own containers, or wait for
  them, rather than failing the stage.

## Notes

- The duplicates were started by the harness agent, not by a flow bug alone. The runner should still refuse them.
- Related: 0432 (dead resolver edits block target sync), 0443, 0449.

## Audit evidence (2026-11-26T03:50Z, fifth-merge audit)

- `thomashan/dev-env#43` (`ubuntu-wsl-ghostty-terminfo`) contains **4 separate plan commits** from **2 distinct intent
  IDs** (`I-1795646837-ubuntu-wsl-ghostty-terminfo` and `I-1795646845-ubuntu-wsl-ghostty-terminfo`, created 8 s apart at
  `22:47Z`–`22:58Z`: `P-1795646862-ANA-G4N`, `P-1795646869-ANA-G4N`, `P-1795647050-ANA-G4A`, `P-1795647322-ANA-G3.8F`)
  committed into the same PR branch (`dev-env#43`), leaving orphan plan files on `main` when merged.

## Progress (2026-11-26)

- in-progress: flow `single-runner-per-checkpoint` (intent `todo/intent-0390-single-runner-per-checkpoint.json`, log
  `todo/flow-single-runner-per-checkpoint.log`), covering this bean and 0472 (same defect). Stage 3 overlap refusals are
  parked, not waited out.
- parked 2026-11-26: blocked by flow `tests-fewer-git-stage-pipeline` (I-1795684868, worktree
  flow-tests-fewer-git-stage-pipeline) on apps/sandbox-executor/tests/flow/conftest.py; Stage 3 admission refused the
  plan's touch set. Checkpoint kept at
  apps/holon-agentic-coder/flow-single-runner-per-checkpoint/.holon/flow/checkpoint-single-runner-per-checkpoint.json
  (stage execute); resume with --checkpoint only once that flow merges or releases conftest.py.
- resumed 2026-11-26 10:55Z from checkpoint (stage execute, `--checkpoint`, claude-agent / claude-opus-5-5): PR #332
  (the earlier blocker) has merged, but Stage 3 admission refused again on a touch-set overlap with open PR #334
  (`I-1795665991-no-unneeded-full-review`, flow worktree `flow-no-unneeded-full-review`) on
  `apps/sandbox-executor/tests/flow/conftest.py`. Parked again; checkpoint kept (stage execute), no runner live. Resume
  with `--checkpoint` once PR #334 merges or releases conftest.py.

## Resolution

Delivered via [PR #351](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/351) and merged into `main`
(`2f29d8c`), together with bean 0390 (same defect). Each flow checkpoint now takes an exclusive advisory lock per intent
slug in the git common directory, so a second fresh, `--from-stage` or `--checkpoint` run exits before any stage runs; a
run that halts, fails or receives SIGINT/SIGTERM reaps its docker clients, containers and process groups
(`flow/run_lock.py`, `flow/process_reaper.py`).

Not in PR #351: the `flow_start` dirty-tree check that ignores the run's own containers (third fix-direction item). The
lock removes the racing writers that caused the dirty tree in the first place.
