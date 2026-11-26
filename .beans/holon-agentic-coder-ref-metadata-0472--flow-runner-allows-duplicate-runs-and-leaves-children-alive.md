---
# holon-agentic-coder-ref-metadata-0472
title: "Flow runner does not refuse a second run on the same intent and does not reap its children after a halt"
status: todo
type: bug
priority: high
tags:
  - flow
  - harness
  - stage-4
created_at: 2026-11-25T23:35:26Z
updated_at: 2026-11-25T23:35:26Z
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
