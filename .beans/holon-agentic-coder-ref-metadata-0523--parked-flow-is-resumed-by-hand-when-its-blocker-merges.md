---
# holon-agentic-coder-ref-metadata-0523
title:
  "A flow parked at Stage 3 is resumed by hand when its blocker merges; record the blocker and resume on its state
  change"
status: todo
type: feature
priority: normal
tags:
  - flow
  - coordination
  - parked
  - holon-agentic-coder
created_at: 2026-11-26T13:40:00Z
updated_at: 2026-11-26T13:40:00Z
---

## Evidence

Self-improvement audit 2026-11-26T13:40Z, question (1).

- `module-budget-default-350` was refused at 13:18:56Z on PR #342 and exited (`Pipeline halted`, checkpoint kept,
  worktree present). `single-runner-per-checkpoint` has been parked since 09:35Z, relaunched twice by hand and refused
  again each time (10:56Z, 13:04Z). Nothing connects a parked flow to the event that frees it; the harness agent has to
  notice the merge, rerun `run_holon_flow.py --checkpoint` and often finds a different blocker.
- The wrapper already prints `gh event listen --resource <pr> --event ...state.changed.v1` hints; `gh event listen`
  exits on the first event, which fits a one-shot resume.

## Proposed change

- On a Stage 3 refusal the wrapper writes `todo/parked/<slug>.json` with the blocker (PR number or branch), the
  checkpoint path and the resume command, then exits.
- A small watcher (extends the merge-event hook of bean 0512) runs `gh event listen` on each blocker PR, and on merge or
  close relaunches the flow with `--checkpoint`, after the same `git fetch --prune` admission re-check of 0519. If the
  new refusal names another blocker, it updates the record and waits again. It honours the 4-flow cap.
- Parked flows are listed by `bean_progress` with their blocker.

## Expected gain

Removes the idle time between a blocker merging and a human relaunching (not measured; bean 0412 would record it) and
the repeated manual probes. Related: 0512, 0519, 0520, 0481, 0394.
