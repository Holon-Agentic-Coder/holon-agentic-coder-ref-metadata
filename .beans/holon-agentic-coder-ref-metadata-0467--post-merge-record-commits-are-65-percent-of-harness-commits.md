---
# holon-agentic-coder-ref-metadata-0467
title: "Per-merge record commits make up 60 of the last 92 harness commits"
status: todo
type: task
priority: normal
tags:
  - harness
  - churn
  - post-merge
created_at: 2026-11-25T22:49:00Z
updated_at: 2026-11-25T22:49:00Z
---

## Problem

Every merged pull request produces its own harness commit that appends one line to Bean 0153 ("docs(bean-0153): record
PR #NNN merged"), and the same for other post-merge bookkeeping. Since 2026-11-24T00:00Z the harness branch has 92
commits, 60 of them matching `bean-0153` or `post-merge`. Bean 0153 is now 419 lines. Several commits record several PRs
at once (#302, #303, #304), others one PR (#305, #306, #307 as three commits within minutes), so the batching is
inconsistent. None of this affects the pipeline or the consensus of any target PR: it is churn that buries real harness
changes in history and (with Bean 0465) makes the squash at the end harder.

## Evidence (self-improvement audit, 2026-11-25T22:49Z)

- `git log --since=2026-11-24T00:00:00Z --oneline`: 92 commits, 60 bookkeeping.
- `b4e8b2f`, `82019d1`, `f549984`: three single-PR commits for #307, #306, #305.

## Proposed change

- Move the merged-PR record out of the bean body into a generated ledger (or the triage file) that the `post-pr-merge`
  skill regenerates from `gh pr list`, so no per-merge edit of a bean is needed.
- If it stays in the bean, the skill batches all merges seen in one run into one commit, and the self-improvement
  audit's merge count reads the same generated source.

## Expected gain and cost

About two thirds fewer harness commits and a stable, derived merge count for the audit. Cost: one change to the
`post-pr-merge` skill and a one-off conversion of the existing lines.

## Audit evidence (2026-11-26T03:50Z, fifth-merge audit)

- All `5` of the last `5` commits on the harness branch (`757bbf0`, `53cc14f`, `e5b1de8`, `0b1d299`, `c7cafb8`) are
  `docs(post-merge)` commits (`100%` in this window).
