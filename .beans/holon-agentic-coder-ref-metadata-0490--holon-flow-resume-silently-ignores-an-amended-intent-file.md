---
# holon-agentic-coder-ref-metadata-0490
title: "holon flow resume with --checkpoint silently ignores an amended intent file"
status: todo
type: bug
priority: high
tags:
  - holon-flow
  - engine
  - resume
  - holon-agentic-coder
created_at: 2026-11-26T06:35:00Z
updated_at: 2026-11-26T06:35:00Z
---

## Problem

`holon flow <intent.json> --checkpoint <ckpt>` (cli/commands/flow.py, `_resolve_checkpoint_and_intent`) loads the
checkpoint context and sets `intent_data = {}`: the intent file argument is ignored without a warning or an error. A
maintainer amendment to the goal (bean 0380: default 200 -> 400, 2026-11-26) therefore cannot reach a resumed flow. The
plan (Stage 2) and execution (Stage 3) branches, the intents ledger row and the checkpoint's `intent_data` all keep the
old goal, and `--from-stage plan|execute` reuses the checkpointed branches rather than amending them.

## Wanted

One supported path to amend a flow's intent: either refuse an intent file that differs from the checkpoint's
`intent_data` with a clear message, or (preferred) `--amend-intent` that records the amended intent as a new append-only
ledger row, updates the checkpoint, and re-runs plan and execute on the SAME PR branch lineage so Stage 4 re-reviews.
Until then an amended intent needs a fresh flow, which opens a new PR.
