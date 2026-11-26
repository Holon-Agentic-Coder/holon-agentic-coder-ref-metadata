---
# holon-agentic-coder-ref-metadata-0430
title: "The review-loop resolver turn has no turn budget, and a spinning test run defeats the stall budget"
status: todo
type: bug
priority: high
tags:
  - flow
  - budgets
  - stage-4
  - holon-agentic-coder
created_at: 2026-11-24T15:55:00Z
updated_at: 2026-11-24T17:45:00Z
---

## Problem

On 2026-11-24 the Stage 4 resolver container for bean 0405 (`festive_swirles`, PR #275, `claude-fable-5-2`) was
dispatched at 13:45:14Z and was still running at 15:49Z (2 h 4 min) with the flow log silent since 13:45:17Z. The
wrapper had `HOLON_TURN_STALL_SECONDS=600` and the default 3600 s turn budget. Neither fired.

Two gaps in `sandbox_executor/turns.py` and `entrypoint/review_loop.py`:

1. The resolver calls `run_turn(cmd, cwd=repo_dir, turn_budgets=...)` with no `watch_path` and no `watch_tree`.
   `turn_observable` is therefore false and `_turn_breach` never fires. The only bound left is the stall window, so the
   resolver turn is effectively unlimited whenever the stall window keeps being reset.
2. The stall window is reset by tool progress: any descendant of the runner that burns at least
   `TOOL_CPU_PROGRESS_SECONDS` (0.5 s) of CPU in a `TOOL_SCAN_INTERVAL_SECONDS` (10 s) scan counts as activity. The
   agent here looped an A/B timing harness (`ab.sh` running `pytest -n auto` many times, container CPU about 1200
   percent), so the stall budget was reset every ten seconds for two hours. A hung or merely endless test loop looks
   identical to progress.

In this occurrence the agent was genuinely working (it was benchmarking the test suite for the speed-up task), so the
outcome was benign, but nothing would have cut it had it been stuck in a spinning child.

## Occurrence 2026-11-24 (17:26Z): the unbounded turn ended in SIGABRT

The same resolver container (`festive_swirles`) ran 221 min (dispatched 13:45:14Z, `docker events` die at 17:26:20Z with
`execDuration=13264`, container exit code 1, no `oom` event). The agent inside reported exit code -6 (SIGABRT), and the
flow failed at 17:32:22Z with `review: failed (227.5 min / 120 min)`: the 120 min review iteration budget was exceeded
by 107 min without cutting the turn, which confirms the missing resolver bound. The flow log was silent from 13:45:17Z
to 17:32:22Z. The turn left 18 modified test files (835 insertions, 422 deletions) uncommitted in the worktree; they
were saved to a patch outside it. The abort cause itself is unconfirmed (see bean 0432). Likely a long-lived runner
failing after hours of accumulated output, which a bounded turn would have prevented.

## Fix direction

- Give the resolver turn a bound that does not depend on artefact progress: apply `turn_seconds` as a wall-clock ceiling
  on the whole resolver turn (or watch the worktree), so a resolver cannot outlive the turn budget.
- Count tool CPU as progress only for a bounded time per response (for example cap consecutive tool-progress resets at
  the turn budget), so a spinning child cannot hold the stall window open indefinitely.
- Log a periodic heartbeat naming the live descendants while a turn is held open by tool progress, so the flow log is
  not silent for hours.

## Notes

- Related: 0384 (stall budget too short for Fable), 0394 (no unnecessary waiting), 0425 (review iterations on Fable are
  slow). Target repository: holon-agentic-coder, flow `unit-suite-slowest-tests-speedup`.
