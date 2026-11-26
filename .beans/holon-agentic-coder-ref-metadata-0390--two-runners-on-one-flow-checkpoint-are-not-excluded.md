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
updated_at: 2026-11-26T20:59Z
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
- 2026-11-26 (post-merge of PR #332): the blocker is released (flow `tests-fewer-git-stage-pipeline` merged; its
  worktree and branches are removed). Still parked: open PR #334 (`I-1795665991-no-unneeded-full-review`) also touches
  `apps/sandbox-executor/tests/flow/conftest.py`, so resume only after #334 merges or releases that file.
- resumed 2026-11-26 10:55Z from checkpoint (stage execute, `--checkpoint`, claude-agent / claude-opus-5-5): PR #332
  (the earlier blocker) has merged, but Stage 3 admission refused again on a touch-set overlap with open PR #334
  (`I-1795665991-no-unneeded-full-review`, flow worktree `flow-no-unneeded-full-review`) on
  `apps/sandbox-executor/tests/flow/conftest.py`. Parked again; checkpoint kept (stage execute), no runner live. Resume
  with `--checkpoint` once PR #334 merges or releases conftest.py.

- resumed 2026-11-26 13:03Z from checkpoint (stage execute, `--checkpoint`, claude-agent / claude-opus-5-5): PR #334
  (the blocker) merged at 13:01Z, so the conftest.py overlap is released. Flow running; log
  `todo/flow-single-runner-per-checkpoint.log`.
- parked 2026-11-26 13:04Z: resume attempt at 13:03Z refused by Stage 3 on a touch-set overlap with the older waiting
  flow `split-calibration-package` (I-1795669744, worktree flow-split-calibration-package, blocked since 05:16Z) on
  apps/sandbox-executor/tests/flow/conftest.py. PR #334 itself merged at 13:01Z, so that blocker is gone. Checkpoint
  kept (stage execute); no runner live. Resume with `--checkpoint` once split-calibration-package merges or releases
  conftest.py.
- resumed 2026-11-26 14:29Z from checkpoint (stage execute, `--checkpoint`, claude-agent / claude-opus-5-5,
  no-wait-on-overlap). Blocker split-calibration-package has completed (checkpoint stage completed); its PR #347 is open
  and does not touch conftest.py. Log `todo/flow-single-runner-per-checkpoint.log`.
- parked 2026-11-26 14:50Z: resume 14:29Z admitted Stage 3 and executed (E-1795703416), but execute failed: the
  execution touched apps/sandbox-executor/src/sandbox_executor/flow/lazy_exports.py and launcher/run_tracking.py outside
  the plan touch set; re-plan (P-1795704471) widened the touch set and Stage 3 then refused on a touch-set overlap with
  open PR #342 (I-1795694671-ledgers-sorted-chronologically) on flow/lazy_exports.py. Checkpoint kept (stage execute,
  worktree flow-single-runner-per-checkpoint); no runner or container live. Resume with `--checkpoint` once PR #342
  merges or releases lazy_exports.py.

- resumed 2026-11-26T20:59Z from checkpoint (stage execute, `--checkpoint`, claude-agent / claude-opus-5-5,
  no-wait-on-overlap): blocker PR #342 (lazy_exports.py) merged 2026-11-26 20:58Z. Log
  `todo/flow-single-runner-per-checkpoint.log`.

- parked 2026-11-26T21:21Z: resumed run executed Stage 3 (E-1795726850, touch set admitted, PR #342 merged) and Stage 4
  ran one review iteration (CHANGES_REQUESTED, 5 open findings). The resolver then halted at its pre-push tests on bean
  0547 (review-loop identity overlay in os.environ reaches the test run; deterministic). Checkpoint kept at stage
  review; no runner live. Resolver's uncommitted fixes remain in the flow worktree (patch copy:
  /private/tmp/claude-501/-Users-thomashan-git-holon-agentic-coder-ref-metadata/f956a41e-6830-4ee3-9257-8c114a4af5b9/scratchpad/resolver-uncommitted-0390.patch).
  Resume with `--from-stage review` once 0547 is merged and the branch has merged origin/main.
