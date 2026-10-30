---
# holon-agentic-coder-ref-metadata-0219
title: "Remove fallback defaults for agent runner and model resolution"
status: in-progress
type: task
priority: high
tags:
  - cli
  - flow
  - agent-defaults
  - safety
  - holon-agentic-coder
created_at: 2026-10-30T08:59:32Z
updated_at: 2026-10-30T12:40:00Z
---

## Problem

When executing `holon flow` (or any `holon` role subcommands such as `intent`, `plan`, `execute`, `review`, `calibrate`)
without specifying `--agent` or `--model`, the CLI currently falls back to implicit defaults:

```text
Agent runner resolved to antigravity-agent (source: fallback, no --agent, HOLON_AGENT or harness marker)
Model resolved to gemini-3.8-flash-medium (source: table, default model for antigravity-agent)
```

These fallback defaults are unsafe and must be removed:

1. **Unintended token/quota expenditure**: Operators or autonomous scripts can accidentally trigger expensive model runs
   without deliberate specification.
2. **Masked configuration errors**: Missing model or runner parameters in automation pipelines are silently masked
   instead of caught early.
3. **Explicit execution contract**: In the Holon ecosystem, runner selection (`claude-agent`, `antigravity-agent`, etc.)
   and model tier (`claude-opus-5-5`, `gemini-3.8-pro`, `gemini-3.8-flash`, etc.) are critical operational parameters
   and must be strictly mandatory.

## Scope & Implementation Plan

1. **Remove Fallback Defaults from `sandbox_executor.agent_defaults`**:
   - Remove `FALLBACK_AGENT = "antigravity-agent"`.
   - In `resolve_agent_runner()`: if `--agent` flag, `HOLON_AGENT` environment variable, or recognized harness marker is
     missing, fail immediately:
     ```text
     Error: Agent runner is mandatory. Please specify --agent <runner> or set HOLON_AGENT (supported: claude-agent, antigravity-agent, pi-agent, codex-agent).
     ```
   - In `resolve_model()`: remove table lookup fallbacks from `DEFAULT_MODELS`. If `--model` flag or `HOLON_MODEL`
     environment variable is missing, fail immediately:
     ```text
     Error: Model is mandatory. Please specify --model <model> or set HOLON_MODEL.
     ```
   - Preserve `LEGACY_DEFAULT_AGENT` and `LEGACY_DEFAULT_MODEL` strictly for back-filling historical ledger rows that
     were written before agent/model tracking was introduced.

2. **CLI Enforcement Across `holon flow` & Subcommands**:
   - `holon flow`, `holon intent`, `holon plan`, `holon execute`, `holon review`, `holon calibrate`:
     - If `--agent` and `--model` are not specified and not present in environment variables, fail with exit code `1`
       (or `2` for argument errors) and output the mandatory requirement.
     - **Resumption Exemption**: Resuming from a checkpoint (`holon flow --checkpoint <path>`) retains the agent and
       model recorded in the checkpoint file when flags are omitted.

3. **Help Text & Documentation**:
   - Update `argparse` descriptions across `cli.py` and `flow.py` to document `--agent` and `--model` as required
     options rather than showing default fallback values.

4. **Test Suite Adaptation**:
   - Update `tests/test_agent_defaults.py`, `tests/test_cli.py`, `tests/test_flow.py`, and `tests/test_preflight.py` to
     assert that omitting runner or model raises the mandatory error.
   - Update existing tests that relied on bare fallback defaults to supply explicit test parameters.

## Acceptance Criteria

1. Running `holon flow <intent.json>` without `--agent` or `HOLON_AGENT` exits with a non-zero code and an error stating
   that the agent runner is mandatory.
2. Running `holon flow <intent.json> --agent antigravity-agent` without `--model` or `HOLON_MODEL` exits with a non-zero
   code and an error stating that the model is mandatory.
3. Resuming a flow via `holon flow --checkpoint <checkpoint.json>` successfully reuses the checkpoint's saved agent and
   model when options are omitted.
4. No implicit fallback to `antigravity-agent` or `gemini-3.8-flash-medium` occurs anywhere in the codebase.
5. All test suites pass cleanly under `uv run pytest`.

## Progress (2026-10-30)

- Taken over from the interrupted session: intent `I-1793355604` and plan `P-1793355620` pushed; the execution branch
  `E-1793355656` holds only ledger and plan rows (Stage 3 produced no code). Resumed with
  `holon flow --checkpoint … --from-stage execute` (antigravity-agent / gemini-3.8-flash-medium, worktree
  `apps/holon-agentic-coder/flow-0219-remove-fallback-defaults`).
