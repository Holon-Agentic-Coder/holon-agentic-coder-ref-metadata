---
# holon-agentic-coder-ref-metadata-0506
title: "Prune the existing single-flow Stage 4 KB-failure clutter from holon-knowledge"
status: todo
type: task
priority: medium
tags:
  - knowledge
  - kb-bloat
  - holon-agentic-coder
created_at: 2026-11-26T10:40:20Z
updated_at: 2026-11-26T10:40:20Z
---

## Problem

Bean 0452 / PR #331 stops new single-flow Stage 4 review chatter from being promoted to `KB-failure-*.json`, but the
files already committed to `holon-knowledge/kb/failure_modes/` remain. About 2,900 of roughly 3,200 files span under one
hour and came from one flow's own review rows, and CI `make lint-json` scans every one of them.

## Proposed fix

- Identify the files whose `evidence.ledger_refs` are all `ACT-REV` / `ACT-FIND` from a single flow (same `I-...` root).
- Archive or delete them in one mechanical pass, keeping any file backed by `>= 2` distinct intents.
- Confirm `make lint-json` and the knowledge index still build; route the change through `holon flow` (sole change
  path).
