---
# holon-agentic-coder-ref-metadata-0138
title: "Planner and executor must write plans/ and execution artifacts incrementally, never via one final response"
status: completed
type: bug
priority: high
tags:
  - holon-flow
  - planner
  - executor
  - prompts
  - robustness
created_at: 2026-10-22T07:20:00Z
updated_at: 2026-10-26T02:33:21Z
---

## Problem

Both authoring stages funnel the agent's entire work product through the **stdout of one final assistant message**,
which converts a per-response output cap into a fatal stage failure and disables the runner's own truncation recovery.

- `entrypoint/planner.py` runs the agent as a single `pi -p` (or `agy`) invocation, then, when `plans/P-<...>.md` does
  not already exist, writes `result.stdout` (optionally extracting a fenced `markdown` block) to that path (`:272-289`).
  Stage failure follows at `:307` when the file is missing or shorter than 50 bytes.
- `holon-config/prompts/planner.template.md` is a 167-line template demanding a metrics table, per-step metric
  derivations, EV arithmetic and step-by-step justification — i.e. a long single answer.

The runner does recover from truncation in general: `pi-agent-core`'s loop routes a truncated response **that contains
tool calls** through `failToolCallsFromTruncatedMessage()`, feeding back "Re-issue the tool call with complete
arguments" and continuing. A truncated **final message with no tool calls** cannot be recovered — `hasMoreToolCalls` is
false, the loop ends, and `dist/modes/print-mode.js` exits 1 because `stopReason === "length"`. Holon's stdout contract
manufactures precisely that shape.

Measured on the host-local model: a single response is capped at `max_tokens = 16384` output tokens
(`stopReason: length` with `usage.output: 16384`); the planner burned 17 minutes and then died with
`Response was truncated` followed by `Error: agent command failed or returned empty. code=1`, discarding the whole run.
The plan template itself is only a few thousand tokens, so the failure mode is "one oversized final answer", not "the
plan does not fit".

## Scope

- Change the prompts (`planner.template.md`, `executor.template.md`) to require the agent to create the target artifact
  with its **write tool** and extend it section by section (`## Overall Plan Metrics` first, then each step, then the
  justification), so no single response has to carry more than one section.
- In `entrypoint/planner.py`: prefer the file the agent wrote; treat `stopReason === "length"` / exit code 1 as
  **informational** when `plans/P-*.md` exists, exceeds the size floor and parses as a valid metrics table. Keep stdout
  capture only as a compatibility fallback, and log loudly when it is used.
- Validate before committing: metrics table parses, every referenced metric is numeric, required sections present. On
  failure, re-prompt once with the specific missing sections rather than re-running the whole plan.
- Do the same for the executor artifact (diff summary / execution notes) so a long implementation step cannot fail the
  same way.
- Tests: an agent that writes the file and then exits 1 with a truncated final message must still produce a committed,
  valid plan; an agent that writes nothing must fail with the metrics-validation reason, not a generic "returned empty";
  a partially written plan must trigger a targeted re-prompt, not a full restart.

## Acceptance criteria

- No authoring stage depends on a single response's output length.
- A truncated final message after a valid artifact never fails the stage.
- `uv run pytest` passes in `apps/sandbox-executor`.

## Relates to

Bean 0139 (per-turn budget so the 17-minute burn is impossible), Bean 0140 (declare the model's real output ceiling),
Bean 0134 (the runner that authors nothing at all).

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
