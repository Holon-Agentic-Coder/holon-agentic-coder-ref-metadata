---
# holon-agentic-coder-ref-metadata-0519
title: "Flow worktree, checkpoint and intent/plan branches vanish after a Stage 3 overlap refusal"
status: in-progress
type: bug
priority: high
tags:
  - flow
  - checkpoint
  - holon-agentic-coder
created_at: 2026-11-26T13:10:00Z
updated_at: 2026-11-27T16:31:30Z
---

## Problem

On 2026-11-26 the flow `module-budget-default-350` (bean 0489) ran intent and plan, then Stage 3 refused on a touch-set
overlap with `I-1795665991-no-unneeded-full-review` (run with `--no-wait-on-overlap`, so it stopped as designed).
Afterwards the flow worktree `apps/holon-agentic-coder/flow-module-budget-default-350` was gone, with its
`.holon/flow/checkpoint-module-budget-default-350.json`, and the local `I-1795686809-module-budget-default-350/*`
branches were gone too. The intent and plan commits (5ac9ddd9, ac3712c8) survive only as unreferenced objects. The
overlapping flow's worktree (`flow-no-unneeded-full-review`) was also absent when checked, though its PR #334 merged
only later.

Parking a refused flow (per the holon-flow skill) depends on keeping the worktree, branches and checkpoint. Nothing in
the harness or the wrapper printed a removal, so the cause is not confirmed; a concurrent cleanup run (for example a
clean-branches or post-merge pass) is one candidate, and the flow engine's own failure path is another.

## Expected

A refused Stage 3 leaves the worktree, the I-/P- branches and the checkpoint in place, so the flow resumes with
`--checkpoint` once the blocker merges.

## Acceptance

- Identify what removed the worktree and branches (check the holon CLI failure path and the clean-branches / post-merge
  skills for `worktree remove` or `branch -D` of `I-*` refs).
- A test or wrapper guard that refuses to delete a parked flow's worktree or checkpoint.

## Diagnosis (maintainer, 2026-11-26)

The Stage 3 overlap check is not checking against the remote each time: it read a stale local branch. When the fresh
`module-budget-default-350` flow was admitted (about 13:05Z), PR #334 (`I-1795665991-no-unneeded-full-review`) had
already merged at 13:01:37Z and its remote branches were being deleted, but the local
`I-1795665991-no-unneeded-full-review*` branches (33 of them, removed by the #334 post-merge run a few minutes later)
and their remote-tracking refs were still in the shared repository, so admission counted a merged flow as in flight and
refused on `budgets.py`.

## Fix (admission)

- Before every admission check, `git fetch --prune origin` so deleted remote branches drop out, and judge "in flight"
  from the remote: an `I-*` branch counts only if it still exists on origin **and** (its PR is open, or a live runner
  holds its worktree). A local branch or worktree alone, or a branch whose PR is merged or closed, never blocks.
- Log, with the refusal, how the blocker was found (ref name, local or remote, PR number and state), so a stale match is
  visible at once.
- Add a test: a merged PR whose local branch still exists does not block admission.

## Still open

Why the refused flow's own worktree, checkpoint and branches disappeared is not explained by the above. Candidates: the
wrapper's cleanup on an early Stage 3 exit, or a concurrent post-merge run's stale-plan sweep (a plan-only worktree with
no PR matches that rule). Check both.

Second case, same day: the worktree `flow-agent-runner-spec-per-agent` (PR #343, merged 13:04:41Z) disappeared while a
review re-run was still live in it (its log ends
`cannot change to .../flow-agent-runner-spec-per-agent: No such file or directory`); the #343 post-merge run found it
already gone before its own cleanup step. So something other than the post-merge cleanup step removes flow worktrees:
find every `git worktree remove`/`rm -rf` path in the wrapper, the engine and the harness skills, and make each one
refuse while a runner holds the worktree.

## Audit evidence (2026-11-26T13:40Z)

- Today `apps/holon-agentic-coder/flow-module-budget-default-350` exists with its checkpoint and the `I-1795698612-*`
  branches, parked at 13:18:56Z on PR #342 (a live refusal, not the stale-ref case). So the original disappearance was
  followed by a relaunch that recreated them, or it was transient.
- Candidate for the still-open question: a post-merge pass running while a rerun is alive removes the worktree under it.
  #340 and #343 had reruns started 21 s and 33 s before they merged (bean 0522).

## Progress

- in-progress 2026-11-26: admission part (remote-aware in-flight check, fetch --prune before each Stage 3 check, refusal
  names how each blocker was found) launched as flow `admission-remote-in-flight` (intent
  todo/intent-0519-admission-remote-in-flight.json, worktree apps/holon-agentic-coder/flow-admission-remote-in-flight,
  claude-agent / claude-opus-5-5). Bean 0520 (trial merge) not implemented.
- parked 2026-11-26: flow `admission-remote-in-flight` (plan I-1795703012 / P-1795703035, checkpoint kept in the flow
  worktree) refused at Stage 3 admission: the touch set overlaps open PR #342 (branch
  I-1795694671-ledgers-sorted-chronologically, the flow in its PR) on
  apps/sandbox-executor/src/sandbox_executor/flow/lazy_exports.py. Resume from checkpoint (--checkpoint) once #342
  merges or releases that file. Note: the plan's touch set lists 14 files, nine of them outside the intent scope (incl.
  lazy_exports.py); logged as bean 0541.

- resumed 2026-11-26 from checkpoint (claude-agent / claude-opus-5-5, --no-wait-on-overlap): PR #342 merged 20:58:42Z,
  but Stage 3 refused again on a touch-set overlap with the parked flow `module-budget-default-350` (branch
  I-1795698612-module-budget-default-350/P-1795698637-CLA-CO5.5/_, blocked since 13:18:56Z on #342) on
  apps/sandbox-executor/src/sandbox_executor/flow/lazy_exports.py. parked 2026-11-26 20:59Z: blocked by parked flow
  module-budget-default-350 on lazy_exports.py; resume from checkpoint once that flow's worktree releases the file (its
  blocker #342 has merged, so it needs its own resume or its stale waiting state cleared).
- relaunched 2026-11-27T16:25:14Z cleanly from `origin/main` (`1f3331637`) with `antigravity-agent` / `gemini-4-neon` in
  `apps/holon-agentic-coder/flow-admission-remote-in-flight`: Stage 1 (`I-1795796714-admission-remote-in-flight/_`) and
  Stage 2 (`I-1795796714-admission-remote-in-flight/P-1795796752-ANA-G4N/_`, EV=45.68) succeeded, then Stage 3 refused
  on touch-set overlap. parked 2026-11-27T16:31:12Z: blocked by local flow
  `I-1795796484-hac-stage-registry-git-forge/P-1795796523-ANA-G4N/_` (worktree
  `apps/holon-agentic-coder/flow-hac-stage-registry-git-forge`) on
  `apps/sandbox-executor/src/sandbox_executor/flow/lazy_exports.py`; resume from checkpoint
  `apps/holon-agentic-coder/flow-admission-remote-in-flight/.holon/flow/checkpoint-admission-remote-in-flight.json` when
  `flow-hac-stage-registry-git-forge` finishes/merges or releases `lazy_exports.py`.
