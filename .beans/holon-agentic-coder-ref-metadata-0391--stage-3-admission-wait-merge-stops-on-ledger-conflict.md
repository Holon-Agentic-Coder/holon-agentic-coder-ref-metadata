---
# holon-agentic-coder-ref-metadata-0391
title: "Stage 3 stops after an overlap wait when merging main into the plan branch conflicts only in the ledgers"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-3
  - ledger
  - conflicts
  - holon-agentic-coder
created_at: 2026-11-24T06:08:11Z
updated_at: 2026-11-24T13:00:00Z
---

## Problem

On 2026-11-24 the flow `ledger-temp-worktree-cleanup` (Bean 0387) waited 1 h 43 min at Stage 3 admission for PR #265 to
merge. When the overlap cleared, Stage 3 merged `origin/main` into the plan branch, hit conflicts in
`holon-knowledge/ledger/intents.jsonl` and `plans.jsonl` only, aborted the merge and failed the stage:

> Stage 3 stopped before dispatch: merging origin/main into '.../P-1795493432-CLA-CF5.2/\_' after the admission wait
> conflicts in holon-knowledge/ledger/intents.jsonl, holon-knowledge/ledger/plans.jsonl; the merge was aborted and
> nothing was pushed. Merge origin/main into the plan branch by hand (merge, do not rebase) and resume the flow.

A resume from the checkpoint failed the same way, so the runner exited. Every flow that waits out an overlap will hit
this, because the merges it waited for always append ledger rows: the wait ends in a guaranteed stop.

## Cause

The post-admission-wait merge in Stage 3 does not use the mechanical ledger resolution that the Stage 4 and Stage 5
conflict gates already apply (keep both sides' rows, ordered by `created_at`). The installed `holon` at the time
predated the merge of PR #265 (Bean 0376, in-flow conflict resolution); check whether `main` after #265 already covers
this path before changing code.

## Goal

- A ledger-only (or knowledge-base-only) conflict in the post-wait merge is resolved mechanically and Stage 3
  dispatches; only a conflict in other files stops the stage.
- `run_holon_flow.py` does not resume a second time into the same deterministic failure.
- A test: plan branch and target both append ledger rows, admission wait ends, Stage 3 dispatches.

## Notes

- Overlap: Bean 0371 (per-flow ledger fragments) removes the ledger conflicts at source and Bean 0376 (in-flow conflict
  resolver) handles the rest. Bean 0376 owns the in-flow merge handling; this bean is the Stage 3 admission-wait case.
- Through the Holon flow for the engine part. Related: Bean 0376, Bean 0371 (ledger fragments remove the conflict
  altogether), Bean 0387 (worked around by a resolve-conflict run and a resume).
