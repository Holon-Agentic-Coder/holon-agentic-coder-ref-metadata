---
# holon-agentic-coder-ref-metadata-0443
title: "Stage 4 pushes review ledger rows seconds after resolver or conflict merge, cancelling CI"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-4
  - ci
  - performance
  - holon-agentic-coder
created_at: 2026-11-25T03:08:00Z
updated_at: 2026-11-25T03:08:00Z
---

## Problem

In Stage 4 (`sandbox_executor/flow/review/loop.py` and `ledger_commit.py`), whenever the resolver container pushes a fix
or `conflict_gate.py` pushes a `Merge main` commit, the engine immediately runs `_commit_pending_ledger_rows` (`9–12 s`
later) and pushes `chore(review): record review ledger rows` as a separate GitHub push. Because GitHub Actions cancels
in-progress runs per PR branch, that follow-up push immediately cancels the 5 CI workflows triggered on the code/merge
head, wastes `Docker Build` runner time (`96–126 s`), and defeats `ci_bookkeeping_gate` (`PR #272`), forcing the
ledger-row commit itself to run the full `6–9 min` CI suite because the cancelled parent head never passed CI.

## Evidence (2026-11-25T00:28Z–02:54Z fifth-merge audit)

All `5` cancelled CI heads across `holon-agentic-coder` PRs in the window were caused by this `9–12 s` double-push race:

- **`PR #305` (`git-refs-self-doc`):** `01:40:54Z` `4ea64923` (`fix(review)`) pushed $\rightarrow$ `01:41:03Z` (`+9 s`)
  `10da1c03` (`chore(review): record review ledger rows (iteration 1)`) pushed; all `5` cancellable workflows on
  `4ea64923` cancelled (`8–9 s`, `Docker Build` wasted `96 s`), forcing `10da1c03` to run full CI (`Unit: 438 s`,
  `Stress: 290 s`).
- **`PR #306` (`github-pr-merge-self-doc`):**
  - `02:07:06Z` `1a49bac5` (`fix(review)`) pushed $\rightarrow$ `02:07:15Z` (`+9 s`) `4b7c7498` (`chore(review)`)
    pushed; `5` workflows on `1a49bac5` cancelled (`9–15 s`), forcing full CI on `4b7c7498` (`Unit: 441 s`,
    `Stress: 430 s`).
  - `02:15:13Z` `4ba9ecf7` (`Merge main`) pushed $\rightarrow$ `02:15:25Z` (`+12 s`) `69fae7f4` (`chore(review)`)
    pushed; `5` workflows on `4ba9ecf7` cancelled (`13–51 s`, `Docker Build` wasted `104 s`), forcing Stage 5
    `merged_head_ci` to wait `456 s` (`7.6 min`) on `69fae7f4`.
- **`PR #296` (`split-cli-init-modules`):**
  - `00:27:55Z` `b646d346` (`fix(review)`) pushed $\rightarrow$ `ac5d3c5e` (`chore(review)`) cancelled `b646d346`
    (`8–9 s`) and ran full CI (`397 s`).
  - `00:35:45Z` `59d41deb` (`Merge main`) pushed $\rightarrow$ `00:35:57Z` (`+12 s`) `c2f861c4` (`chore(review)`)
    pushed; `5` workflows on `59d41deb` cancelled (`17–51 s`, `Docker Build` wasted `126 s`), forcing Stage 5
    `merged_head_ci` to wait `475 s` (`7.9 min`) on `c2f861c4`.

Code locations: `apps/holon-agentic-coder/main/apps/sandbox-executor/src/sandbox_executor/flow/review/loop.py:329,857`,
`conflict_gate.py:112,182`, and `ledger_commit.py:135-155`.

## Proposed change

1. Eliminate the `9–12 s` double push:
   - Have the host (not the resolver container, or deferring the container's push to the host) push once after the host
     appends and commits iteration ledger rows on top of the resolver's commit, OR fold pending Stage 4 ledger rows into
     the resolver/conflict-gate push before pushing to `origin`.
   - At `conflict_gate` / `loop.py:857` (Stage 4 exit before Stage 5), avoid pushing a bare `chore(review)` commit
     `12 s` after `Merge main` when Stage 5 is entering immediately (or push `Merge main` + final Stage 4 ledger rows
     together in one push).
2. Add a hermetic Stage 4 test asserting that a resolver fix + iteration ledger rows (and conflict-gate merge + exit
   ledger rows) result in a single `push_commit` call, not two sequential pushes.

## Expected gain

Eliminates `100%` of self-inflicted Stage 4 CI cancellations (`5` cancelled heads / `~500 s` of wasted `Docker Build`
runs in 2.4 h) and avoids invalidating `ci_bookkeeping_gate` on follow-up ledger commits.

## Cost

Medium: push batching in `flow/review/loop.py`, `ledger_commit.py`, `conflict_gate.py`, and resolver handoff, delivered
via the Holon flow.

## Notes

- Target repo change through the Holon flow (`holon-agentic-coder`).
- Related: Bean `0383` (Stage 4/5 inline commits & one push per step), Bean `0394` (Rec. 6), Bean `0403`
  (`ci_bookkeeping_gate`).
