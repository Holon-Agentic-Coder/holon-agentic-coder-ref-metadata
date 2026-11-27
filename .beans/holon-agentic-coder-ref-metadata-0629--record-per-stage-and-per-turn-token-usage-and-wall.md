---
# holon-agentic-coder-ref-metadata-0629
title: "Record per-stage and per-turn token usage and wall timings in checkpoints"
status: todo
type: feature
priority: normal
tags:
  - flow
  - telemetry
  - tokens
  - holon-agentic-coder
created_at: 2026-11-27T11:52:42Z
updated_at: 2026-11-27T11:55:26Z
---

## Notes

### Evidence (2026-11-27T11:52Z fifth-merge audit)

- While Bean `0412` tracks wrapper `todo/flow-*.log` persistence and missing sub-step wall timings (`pre_flight`,
  `stage5_ci_reg_wait`, per-reviewer latencies, resolver inner splits), inspecting `checkpoint-*.json` context fields,
  `executions/E-*.md`, and `holon-knowledge/ledger/pending/executions/*.jsonl` at `hac@2a83e4cc7` confirms that **LLM
  token usage** (input, output, cached, total tokens) and **structured per-stage / per-turn wall seconds** are not
  recorded in checkpoint JSON or execution records.
- When `post-pr-merge` prunes merged flow worktrees (as happened for 6 of the 7 HAC PRs `#412`, `#414`, `#416–#418`,
  `#422`), any unlogged timing or token data disappears completely from disk (`0/14` flows wrote `todo/flow-*.log` in
  `10:49Z–11:47Z`).
- Without structured token and wall-time fields in `executions.jsonl` / `P-*_calibration.md`, audits cannot compare
  token cost or per-stage latency across `gemini-4-neon` vs fallback tiers (`gemini-4-argon`, `gemini-4-hydrogen`).

### Proposed Change

1. Capture runner-emitted token usage (`input_tokens`, `output_tokens`, `cached_tokens`, `total_tokens`) and per-turn
   elapsed seconds in `turns.py` / `TurnOutcome` when reported by the runner or proxy summary.
2. Persist structured `step_timings` and `token_usage` per stage/turn in `FlowContext` (`checkpoint-*.json`), append
   compact summary fields to `executions.jsonl` and `executions/E-*.md`, and surface totals in Stage 5
   `P-*_calibration.md`.

### Expected Gain & Cost

- Makes token cost and stage/turn latency observable even after worktree pruning, enabling data-driven model-ladder and
  prompt-budget tuning.
- Cost: ~80 lines across `turns.py`, `flow/context.py`, `calibration/`, and hermetic unit tests.

## Acceptance Criteria

- [ ] `TurnOutcome` and `FlowContext` record optional structured token counts (`input`, `output`, `cached`, `total`) and
      per-stage / per-turn elapsed seconds when available.
- [ ] `checkpoint-*.json`, `executions/*.jsonl`, and Stage 5 `P-*_calibration.md` include the recorded duration and
      token summary fields without breaking append-only schema checks.
- [ ] Hermetic tests verify token and timing propagation with `uv run pytest` and `uv run task lint`.

## Resolution
