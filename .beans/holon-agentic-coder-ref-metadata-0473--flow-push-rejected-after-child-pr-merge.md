---
# holon-agentic-coder-ref-metadata-0473
title:
  "Flow push of a parent branch is rejected after a child PR merges into it (stale local parent, no fetch before push)"
status: todo
type: bug
priority: high
tags:
  - flow
  - ledger-fragments-and-promotion
created_at: 2026-11-26T00:40:14Z
updated_at: 2026-11-26T00:40:14Z
---

## Problem

Flow ledger-fragments-and-promotion (bean 0371) split into 4 sub-intents. Sub-intent 1 ran through review and
calibration and its PR #310 merged into the parent branch
`I-1795584436-ledger-fragments-and-promotion/P-1795584464-CLA-CO5.5/_` at 2026-11-26T00:38:28Z. Seven seconds later the
flow's sync commit (789cbfab, merging origin/main into the parent) was pushed from a local parent ref that did not
contain the merge commit ba5e090d. The push was rejected ("fetch first"), and Stage 3 failed at sub-intent 2/4 with
"target sync ... was blocked". The message names the ledgers, which is misleading: the failure is a non-fast-forward
push race on the parent ref.

## Expected

After a child PR merges into the parent branch, the flow fetches the parent ref and integrates it (a plain merge, never
a force push) before the target sync and push.

## Evidence

- PR #310 baseRefName is the parent branch, mergedAt 2026-11-26T00:38:28Z, merge commit ba5e090d.
- Local sync commit 789cbfab (11:38:35 +11) is not a descendant of ba5e090d.
- Checkpoint: current_stage execute, completed_stages intent and plan; wrapper log in
  todo/flow-ledger-fragments-and-promotion.log.

## Acceptance

- The flow fetches and merges the remote parent head before pushing after a child merge.
- A rejected non-fast-forward push on a flow branch is retried after a fetch-and-merge, never forced.
