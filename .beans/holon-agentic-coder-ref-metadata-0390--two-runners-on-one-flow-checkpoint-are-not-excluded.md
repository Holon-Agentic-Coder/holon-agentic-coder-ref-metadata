---
# holon-agentic-coder-ref-metadata-0390
title: "Two runners can drive the same flow checkpoint at once; nothing locks a flow or a bean against a second launch"
status: in-progress
type: bug
priority: high
tags:
  - holon-flow
  - harness
  - holon-agentic-coder
  - concurrency
created_at: 2026-11-23T15:20:54Z
updated_at: 2026-11-23T15:20:54Z
---

## Problem

On 2026-11-23 two sessions picked up Bean 0382 within 20 seconds of each other (14:28 UTC): one Claude Code session and
one Antigravity session that backfilled a free slot. Two flows were launched for the same bean, then two runners drove
the **same** intent and checkpoint (`fable-model-registry-entry`): both dispatched Stage 2, and the run halted with
`Plan stage failed: ambiguous P-branches under I-1795444112-fable-model-registry-entry: 2 appeared during dispatch`. The
resulting pull request (#267) carries two plan files. One runner was also killed from outside (exit 144) and left no
reason in its log.

## Cause

- **Harness:** the bean was claimed only by setting `status: in-progress`, which both sessions did at the same moment;
  `.agents/coordination.md` "Task Locking" names no atomic claim, and `run_holon_flow.py` does not check whether a flow
  for the same bean or slug is already live.
- **Target:** `holon flow` takes no lock on its checkpoint or flow worktree, so a second process resumes the same
  checkpoint and dispatches the same stage.

## Goal

- `holon flow` holds an exclusive lock per checkpoint (or flow worktree) for the life of the run and refuses a second
  runner with a message naming the holder's PID; a stale lock from a dead PID is taken over. Through the Holon flow.
- `run_holon_flow.py` refuses to launch when a live runner already drives an intent for the same bean id or slug, and
  the claim of a bean is atomic (for example an exclusive-create claim file naming the session). Harness edit.
- A runner stopped by a signal writes the signal and time to its log before exiting.

## Notes

- Related: Bean 0360 (duplicate P- branch after an interrupted plan stage), Bean 0385 (empty flow log).

## Occurrence (2026-11-24, bean 0387)

- A session restart at about 07:19Z killed the wrapper of `ledger-temp-worktree-cleanup` but left its Stage 3 executor
  container running. A resume at 07:22Z took its pre-dispatch snapshot while that container was still to push
  `E-1795504454`; the new run pushed `E-1795504981`, and Stage 3 failed with "ambiguous E-branches ... 2 appeared during
  dispatch; refusing to guess" (`flow/git_refs.py`, `_discover_child_branch`). Two full executions were wasted.
- Asks for this bean: a resume must detect a live role container on the same worktree (not only a live host runner) and
  wait or refuse; and a resume should be able to adopt a completed, pushed execution branch of a killed run instead of
  executing again.

## Progress (2026-11-26)

- in-progress: flow `single-runner-per-checkpoint` (intent `todo/intent-0390-single-runner-per-checkpoint.json`, log
  `todo/flow-single-runner-per-checkpoint.log`), covering this bean and 0472 (same defect). Stage 3 overlap refusals are
  parked, not waited out.
- parked 2026-11-26: blocked by flow `tests-fewer-git-stage-pipeline` (I-1795684868, worktree
  flow-tests-fewer-git-stage-pipeline) on apps/sandbox-executor/tests/flow/conftest.py; Stage 3 admission refused the
  plan's touch set. Checkpoint kept at
  apps/holon-agentic-coder/flow-single-runner-per-checkpoint/.holon/flow/checkpoint-single-runner-per-checkpoint.json
  (stage execute); resume with --checkpoint only once that flow merges or releases conftest.py.
