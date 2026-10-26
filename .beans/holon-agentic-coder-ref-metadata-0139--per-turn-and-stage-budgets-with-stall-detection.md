---
# holon-agentic-coder-ref-metadata-0139
title: "Add per-turn and per-stage wall-clock budgets with stall detection to runner invocations"
status: completed
type: task
priority: high
tags:
  - holon-flow
  - reliability
  - timeouts
  - observability
  - agent-runner
created_at: 2026-10-22T07:20:00Z
updated_at: 2026-10-26T02:33:21Z
---

## Problem

Nothing bounds a runner invocation. A degenerate generation ran **17 minutes** before failing at Stage 2, and the only
timeout in the pipeline is a hardcoded 300-second `subprocess.run(..., timeout=300)` around the test run in
`flow.py:2366-2380`. A hung container, a quota-retrying CLI, or a model that rambles keeps an operator (and any
supervising agent) blocked indefinitely, and the failure is reported with no elapsed-time context.

Measured evidence used to size the budgets (all real, no synthetic numbers):

| measurement                         | source                                                                  |     value |
| :---------------------------------- | :---------------------------------------------------------------------- | --------: |
| planner turn, cloud runner          | merged `holon-coherence` PR #26 (`P-1792495105` stamp → `plan:` commit) |   3.0 min |
| planner turn, cloud runner          | merged `holon-coherence` PR #25 (`P-1792298388` stamp → `plan:` commit) |  31.4 min |
| executor stage, cloud runner        | merged `holon-coherence` PR #26 (`E-1792495303` → `execute:` commit)    |   9.3 min |
| executor stage, cloud runner        | merged `holon-coherence` PR #25 (`E-1792300295` → `execute:` commit)    |  11.1 min |
| local-model throughput              | gateway probe, `usage.completion_tokens / elapsed`                      | ~82 tok/s |
| one full 16,384-token response      | `pi -p --mode json` on the host-local model                             |    ~5 min |
| unbudgeted planner burn that failed | this session, Stage 2 on `pi-agent`                                     |    17 min |

## Scope

- **Per-turn budget `X = 5 minutes`** for a single assistant response, chosen as roughly one full 16,384-token response
  at the measured 82 tok/s (≈5 min) — i.e. it cannot fire on a legitimately full response and cannot mask one. Express
  it as `HOLON_TURN_TIMEOUT_SECONDS` (default `300`) rather than a literal.
- **Stall detection: 90 seconds with no streamed token or tool-call event** (`HOLON_TURN_STALL_SECONDS`, default `90`)
  kills a turn that produced nothing, which is a strictly better signal than elapsed time and catches dead connections
  and quota-retry loops in well under a minute.
- **Per-stage ceilings**, configurable, each ≥ the slowest legitimate observation above: intent 10 min, plan 35 min (the
  31.4 min PR #25 planner is real), execute 45 min, per review-loop iteration 15 min, calibration 10 min. A stage
  ceiling must be enforced as a wall-clock budget **with progress checkpoints**, so a stage that is still writing
  artifacts is not killed mid-section.
- On breach: terminate the container process group (not just the CLI), **salvage any partial artifact** (`plans/P-*.md`,
  execution notes), attempt exactly one resume-and-continue turn, and if that fails record the breach — action record
  with `entry_type: "action"`, an `ACT-BUDGET`-prefixed `action_id`, `outcome: "failure"`, the elapsed seconds, the
  budget that fired and the stage — into `holon-knowledge/ledger/executions.jsonl` under `LedgerLock` (Bean 0132's
  writer).
- Report elapsed vs budget in every stage summary line so operators see the margin, e.g. `plan: ok (4.1 min / 35 min)`.

## Acceptance criteria

- A turn exceeding `X`, or silent for the stall window, is terminated and reported; the stage is not left hanging.
- A stage that completes inside its budget is unaffected, and the summary prints elapsed vs budget.
- The failed-run path preserves a partial artifact and writes the budget action record.
- Tests use an injected clock/sleeper (the style already used by the readiness-poll tests in `holon-coherence`, and
  `apps/sandbox-executor/tests`) covering turn breach, stall breach, and stage-ceiling breach with salvage; all run
  under `uv run pytest`.

## Relates to

Bean 0138 (the artifact that gets salvaged must exist incrementally), Bean 0137 (pre-flight probe so a quota-dead runner
fails in seconds instead of minutes), Bean 0132 (where the breach record must be written).

## Resolution

- **Pull Request**:
  [Holon-Agentic-Coder/holon-agentic-coder#94](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/94)
- **5-Stage Provenance**:
  - Intent: `I-1792765424-incremental-artifacts-budgets-and-local-llm-envelope/_`
  - Plan: `P-1792788153-claude-agent-claude-opus-5-5`
  - Execution: `E-1792788550-claude-agent-claude-opus-5-5`
  - Review: 3-agent ensemble consensus `APPROVED` (3/3), first at `b9864ed` (review 5637813577). After merging `main`
    twice (#96, #95) it went through iterations 14–25 and was re-posted at `28ad58f` (review 5645812038).
  - Calibration: report `7e84078` plus Bean 0146 annotation `8496227` (Predicted EV 4.75 from the wrong row; Overall
    39.84 | Actual EV 5.07).
- **CI Status**: 10/10 passing, CodeQL 0 open alerts. Merged by the maintainer on 2026-10-26 as `e3bbd67`.
- **Outcome**, delivered together for Beans 0138, 0139 and 0140:
  - incremental `plans/` and `executions/` artefacts, with validated execution notes
  - per-turn and per-stage wall-clock budgets with stall supervision, handed down to every Stage 1–3 container
  - an explicit local-LLM model envelope (`maxTokens` and reasoning)
  - a unified `holon doctor`
  - one validated `models.json` loader
  - doctor sections that cannot crash, and finite numeric bounds
  - UTF-8 input validation and encoding-safe output
- **Follow-ups**: Bean 0146 (calibration reads the wrong plan row), Bean 0155 (`HOLON_*` forwarding on the argv, already
  on main).
