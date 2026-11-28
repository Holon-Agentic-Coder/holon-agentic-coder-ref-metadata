---
# holon-agentic-coder-ref-metadata-0506
title: "Prune the existing single-flow Stage 4 KB-failure clutter from holon-knowledge"
status: completed
type: task
priority: medium
tags:
  - knowledge
  - kb-bloat
  - holon-agentic-coder
created_at: 2026-11-26T10:40:20Z
updated_at: 2026-11-26T23:05:26Z
---

Flow: prune-single-flow-kb-failures (todo/flow-prune-single-flow-kb-failures.log). Parked at Stage 4 on bean 0516
(review prompt too long for a 2,923-path deletion PR).

## Problem

Bean 0452 / PR #331 stops new single-flow Stage 4 review chatter from being promoted to `KB-failure-*.json`, but the
files already committed to `holon-knowledge/kb/failure_modes/` remain. About 2,900 of roughly 3,200 files span under one
hour and came from one flow's own review rows, and CI `make lint-json` scans every one of them.

## Proposed fix

- Identify the files whose `evidence.ledger_refs` are all `ACT-REV` / `ACT-FIND` from a single flow (same `I-...` root).
- Archive or delete them in one mechanical pass, keeping any file backed by `>= 2` distinct intents.
- Confirm `make lint-json` and the knowledge index still build; route the change through `holon flow` (sole change
  path).

parked 2026-11-26 21:03Z: Stage 4 review failed again with "Prompt is too long" on resume (see bean 0516). Checkpoint
kept at review in `flow-prune-single-flow-kb-failures`; PR #344 open, MERGEABLE/CLEAN at the time of the check. Resume
from checkpoint once the review prompt no longer inlines the bulk deletion.

## Resolution

Delivered via [PR #344](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/344) and merged into `main`
(`f37c1855`):

- **Key Architectural Deliverables**: `scripts/prune_kb_single_flow_failures.py` removes the single-flow Stage 4
  KB-failure files from `holon-knowledge/kb/failure_modes/` (about 3,400 deletions), keeping any file backed by two or
  more distinct intents; the script is kept for reuse.
- **Verification & Tests**: `apps/sandbox-executor/tests/test_prune_kb_single_flow_failures.py` (173 lines, hermetic).
- **Holon Flow Traversal**: Stages 1 to 5 completed in flow `prune-single-flow-kb-failures` after the Stage 4 review
  resumed past the prompt-length park; worktree and branches removed after merge.
