---
# holon-agentic-coder-ref-metadata-0358
title: "Stage 4 resolver backgrounds the test suite and ends its turn, so the 90 s stall budget kills it"
status: completed
type: bug
priority: high
tags:
  - flow
  - stage-4
  - resolver
  - budgets
  - holon-agentic-coder
created_at: 2026-11-22T00:30:00+11:00
updated_at: 2026-11-23T10:45:00+11:00
---

## Problem

On 2026-11-21, the PR #230 review loop (`review-approved-and-fresh-tests`) failed twice at 12:52 and 13:23 UTC, the same
way each time:

1. The claude-opus-5-5 resolver applied its findings.
2. It ran `uv run task test` in the background and ended its turn: "I'll get a notification when `uv run task test`
   finishes".
3. The turn supervisor saw no output and stopped the agent: "turn stall budget of 90 s exceeded after 90.5 s".

The loop then halted. Nothing in the container ever delivers the notification the agent is waiting for, so the pattern
can never succeed. The antigravity runner has the same shape: it backgrounds a long command, exits, and leaves an empty
diff (Bean 0349).

The workaround used for #230 was to resume with `HOLON_TURN_STALL_SECONDS=900`. `HOLON_*` variables are passed into role
containers.

## Action

Through the Holon flow on `holon-agentic-coder`:

- **Turn budgets (Part 1, merged via PR #235, 134e333d):** `_run_resolver_agent` in `entrypoint/review_loop.py` passes
  `turn_budgets=load_budgets(os.environ).turn` to `run_turn(...)`, matching executor, planner and reviewer turns, with a
  hermetic unit test.
- **Prompts:** the resolver, executor and review-loop prompt templates (`holon-config/prompts/`) tell the agent to run
  tests and lint in the foreground and wait for the result inside the same turn. Never background a command and end the
  turn. Use the bounded commands the repo provides (`uv run task test` / a targeted `uv run pytest`).
- **Supervisor:** while the agent has a child test or lint process running, the stall budget does not fire. The process
  is visible as a running tool call or child process. The turn timeout still bounds it. Alternatively, a turn that ends
  with background work still running counts as unfinished and is resumed or re-prompted, not killed as stalled. Decide
  which in the plan.
- **Logging:** log a clear message when a turn ends with background processes still running, naming the command.
- **Hermetic tests:**
  - a resolver turn that runs a 3-minute fake test in the foreground is not killed at 90 s;
  - a turn that backgrounds a command and exits is reported clearly, not as a bare stall;
  - the prompt templates contain the foreground rule.

## Notes

- Related: Bean 0349 (antigravity backgrounding), Bean 0172 (stage and turn budgets), Bean 0354 (local test gate).

## Progress

- 2026-11-22: Started part 1 (resolver honours turn budgets only: `_run_resolver_agent` passes `turn_budgets`; the
  background-tests and stall-supervisor work stays in later parts). Flow `resolver-honours-turn-budgets` launched with
  `--allow-overlap` (maintainer-authorised for this flow only; overlaps PR #230 on `entrypoint/review_loop.py`).
- 2026-11-22: Completed part 1 only (resolver honours turn budgets: `_run_resolver_agent` now passes the loaded `turn`
  budgets, with hermetic tests). Flow `resolver-honours-turn-budgets` reached Stage 4 consensus APPROVED 3/3 at
  iteration 3 (0 critical, 0 important, 0 nit), CI 11/11 green, calibration included in the PR diff, PR #235
  MERGEABLE/CLEAN, awaiting human merge into main. Background-tests and stall-supervisor work remains for later parts.
- 2026-11-22: PR #235 merged into main (`134e333d`), holon CLI & Docker images rebuilt, and flow worktree pruned. Part 2
  (foreground test prompt and supervisor background-process guard) remains open.
- 2026-11-23: Started part 2 (foreground test prompts and supervisor guard for a live child process or background
  command). Flow `resolver-foreground-tests-stall` launched with `--allow-overlap` (intent
  `todo/intent-0358-resolver-foreground-tests-stall.json`).
- 2026-11-23: Part 2 flow `resolver-foreground-tests-stall` completed all five stages: Stage 4 consensus APPROVED 3/3 at
  iteration 2 (0 critical, 0 important, 0 nit), calibration included in the PR diff, CI clean, PR #237 MERGEABLE/CLEAN,
  awaiting human merge into main: https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/237

## Resolution

Delivered via [PR #237](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/237) and merged into `main`
(`032d9d44`):

- **Key Architectural Deliverables**: Stage 4 resolver and executor prompt templates now require running tests and lint
  in the foreground and waiting for the result in the same turn; the turn supervisor does not apply the stall budget
  while a child test or lint process is live; a turn that ends with background work still running is logged naming the
  command.
- **Verification & Tests**: Hermetic tests cover a 3-minute foreground fake test not killed at 90 s, a backgrounded
  command reported clearly rather than as a bare stall, and the foreground rule present in the prompt templates.
- **Holon Flow Traversal**: Flow `resolver-foreground-tests-stall` completed all five stages (Intent -> Plan -> Execute
  -> Review Loop -> Calibration); Stage 4 consensus APPROVED 3/3 at iteration 2 with 0 critical, 0 important, 0 nit
  findings.
