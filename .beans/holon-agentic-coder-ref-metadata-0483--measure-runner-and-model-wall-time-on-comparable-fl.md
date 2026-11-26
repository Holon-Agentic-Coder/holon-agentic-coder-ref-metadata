---
# holon-agentic-coder-ref-metadata-0483
title: "Measure runner and model wall time on comparable flows to choose the default"
status: todo
type: task
priority: normal
tags:
  - flow
  - runners
  - performance
created_at: 2026-11-26T05:30:00Z
updated_at: 2026-11-26T05:30:00Z
---

## Problem

The flow time audit of 2026-11-26 cannot say which runner or model is fastest. claude-agent/opus flows #308 to #316 have
a median of 46 min active (p90 102). antigravity/gemini self-doc flows #296 to #307 have a median of 23.7 min. That is
not comparable work (different intent sizes and kinds), so there is no conclusion yet.

## Proposal

- Run a paired comparison: same-size intents, or the same intent run twice in dry-run, one per runner/model.
- Report wall time per stage and per role (planner, executor, reviewer, resolver).
- Record agent and model per turn in the ledger so the comparison can be read from data later. Bean 0412 covers the
  related timing and token gaps in `executions.jsonl`.

## Notes

- Open contradiction on the default runner: Bean 0411 item 3 (`AGENTS.md` says `antigravity-agent` with `gemini-4-neon`;
  recent practice is `claude-agent`). Linked, deliberately not resolved here.
- Source: `todo/flow-time-audit-2026-11-26.md` and its data directory.
