---
# holon-agentic-coder-ref-metadata-0384
title:
  "The 90 s stall budget cuts long-thinking models: every Fable 5.2 reviewer failed, and the loop retried unchanged"
status: todo
type: bug
priority: high
tags:
  - flow
  - budgets
  - stage-4
  - models
  - holon-agentic-coder
created_at: 2026-11-23T12:40:00Z
updated_at: 2026-11-23T12:40:00Z
---

## Problem

With `--model claude-fable-5-2` every Stage 4 reviewer was cut: "review turn cut short: review stall budget of 90 s
exceeded after 90.2 s" (PR #260 iterations 1 to 3, PR #263 iteration 1, 2026-11-23). `HOLON_TURN_STALL_SECONDS` defaults
to 90 s of silence on the stream; Fable thinks longer than that before it streams anything. Planning and execution on
Fable were not cut. Setting `HOLON_TURN_STALL_SECONDS=600` fixed it (PR #260 approved 3/3 in a 38.8-minute round).

Each failed round cost a full ensemble launch, and the flow was resumed three times with nothing changed before the
cause was noticed: the failure reads as "the reviewer ensemble did not complete", not as a configuration problem.

## Goal

- Liveness is not only streamed text: thinking, tool-call and keep-alive events count, so a model that is working is not
  treated as stalled.
- The stall default depends on the runner and model capability (or scales with the turn timeout) instead of one 90 s
  constant; the resolved value is in the budgets log line.
- When every reviewer of a round is cut by the stall budget, the stage fails with a message that names the budget and
  the variable to raise, and the review loop does not count it as a review iteration.
- A resume that would repeat a round that failed identically (same head, same budget) refuses with that message instead
  of running it again.
