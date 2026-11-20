---
# holon-agentic-coder-ref-metadata-0342
title: "Stage 5 logs a running total of promoted knowledge candidates as if this flow promoted them"
status: in-progress
type: bug
priority: low
tags:
  - flow
  - calibration
  - knowledge
  - logging
  - holon-agentic-coder
created_at: 2026-11-20T20:40:00+11:00
updated_at: 2026-11-20T20:40:00+11:00
---

## Problem

Stage 5 logs "Stage 5 promoted N knowledge/wisdom candidate(s)" (`flow/stages/calibrate.py`, about line 297) using the
length of whatever `promote_pending_candidates` returns. That function goes through every qualifying candidate in
`holon-knowledge/.index/action_index.db` (at least 2 trials), so N is a running total: on 2026-11-20 it climbed across
flows (576, 587, 593, …, 632, 640) while one flow actually added about 11 failure-mode files.

## Action

Through the Holon flow on `holon-agentic-coder`: log only the candidates this run newly promoted (and, separately if
useful, the total), with a hermetic test. Check that promotion itself is not repeating work on already promoted
candidates on every flow.

## Progress

- 2026-11-20: Holon flow started (slug `promoted-count-this-run-only`, claude-agent / claude-opus-5-5, worktree
  `apps/holon-agentic-coder/flow-promoted-count-this-run-only`).
