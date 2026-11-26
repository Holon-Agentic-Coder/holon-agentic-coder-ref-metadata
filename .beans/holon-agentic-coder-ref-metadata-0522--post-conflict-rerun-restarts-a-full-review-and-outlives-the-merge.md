---
# holon-agentic-coder-ref-metadata-0522
title:
  "A rerun after a post-approval conflict restarts a full review from the review stage and keeps running after the PR
  merges"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-4
  - merge-conflicts
  - holon-agentic-coder
created_at: 2026-11-26T13:40:00Z
updated_at: 2026-11-26T13:40:00Z
---

## Evidence

Self-improvement audit 2026-11-26T13:40Z, question (2). Logs: `todo/flow-fetch-execution-branch-retry.log`,
`todo/flow-agent-runner-spec-per-agent.log`.

- #340 and #343 both finished with approval and calibration, `PR #340 Mergeable: MERGEABLE, State: CLEAN` (12:29Z) and
  `PR #343 ... CLEAN` (12:44Z). #341 merged at 12:58Z and added the same `WB-heuristic-84a6ddeb.json`, so both PRs
  turned conflicting (bean 0517). The conflict was settled by hand and a rerun was launched with `--from-stage review`:
  #340 at 13:04:02Z, #343 at 13:04:08Z.
- Each rerun started a full ensemble iteration, `Review mode at iteration 3: full (last reviewed head unknown)`, even
  though the approval had been carried over by PR-own fingerprint earlier in the same log
  (`approval carried over ... fingerprint pf1:dd4d979e`). The only change on the head was a merge of main.
- The maintainer's merge queue merged #340 at 13:04:23Z and #343 at 13:04:41Z, 21 s and 33 s after the reruns began.
  Neither log has an end line after `git config --global user.name Holon Review Loop Agent`: the review containers and
  `holon flow` processes were left running against merged PRs, then post-merge removed the worktrees under them (this
  fits the vanishing worktrees of bean 0519 and the open bean 0420).
- The right restart stage was `calibrate` or nothing: the review had already approved and the merge added no PR-owned
  change. `review` re-spends 3 reviewers (about 12 to 26 min and the same tokens as iteration 1) for no gain; the gate
  that ends the flow is the pipeline and the consensus, and both were already passed.

## Proposed change

1. After a conflict resolution at the merge boundary, compute the PR-own fingerprint; if equal to the approved one,
   resume at `calibrate` (or just re-check CI on the new head), never at `review`. The wrapper prints the stage it
   picked and why.
2. Before any rerun and every minute while it runs, read the PR state and the merge queue; if the PR is merged or
   queued, stop the rerun, reap its `holon flow` and `docker run` children (0472), and leave the worktree alone until
   they are gone.
3. The delta review needs the last reviewed head; persist it in the checkpoint so a resume is not "unknown".

## Expected gain

Per post-approval conflict: one full review iteration (12 to 26 min, 3 reviewer calls) and one orphaned process set.
Frequency: 2 of 5 merges in the window (3 of 5 conflicted, see 0517). Related: 0420, 0472, 0519, 0517, 0497, 0513.
