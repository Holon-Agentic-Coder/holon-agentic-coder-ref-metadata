---
# holon-agentic-coder-ref-metadata-0474
title:
  "Flow integration of a plan branch into its execution branch refuses an append-only executions.jsonl merge as 'not a
  pure ledger append'"
status: todo
type: bug
priority: high
tags:
  - flow
  - ledger
  - ledger-fragments-and-promotion
created_at: 2026-11-26T03:36:30Z
updated_at: 2026-11-26T03:36:30Z
---

## Problem

After all 4 sub-intents of flow ledger-fragments-and-promotion (bean 0371) merged into the plan branch
`I-1795584436-ledger-fragments-and-promotion/P-1795584464-CLA-CO5.5/_` (PRs #310-#313), Stage 3 failed with "integrating
... into .../E-1795647346-CLA-CO5.5/_ failed: merging ... conflicts in holon-knowledge/ledger/executions.jsonl (outside
holon-knowledge/ledger/*.jsonl or not a pure ledger append)".

Both sides were append-only relative to their merge base (48b4ab08): the execution branch added 138 rows and the plan
branch added 288 rows, with zero deletions on either side. The conflict was the usual append-append at end of file. The
gate judged it not a pure append, so the flow halted instead of applying the ledger rule (main's rows in order, then
this branch's own rows).

## Evidence

- `git diff --numstat <base> E` -> 138 added, 0 deleted; `git diff --numstat <base> origin/P` -> 288 added, 0 deleted.
- Resolved mechanically with `resolve_known.py`: 10646 base rows + 138 own rows = 10784, every row present; committed as
  f22ac491 and pushed fast-forward (6dd14494..f22ac491).
- Wrapper log: todo/flow-ledger-fragments-and-promotion.log, entry 2026-11-26T03:30:33Z.

## Expected

An append-only ledger conflict (both sides only add lines, no deletions) is settled by the ledger rule, for every merge
direction (plan into execution branch, and execution into plan branch), not refused as a judgement call.
