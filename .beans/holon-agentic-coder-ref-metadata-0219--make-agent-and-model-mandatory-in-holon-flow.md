---
# holon-agentic-coder-ref-metadata-0219
title: "Make --agent and --model mandatory in holon flow; eliminate silent fallbacks"
status: todo
type: task
priority: high
tags:
  - cli
  - flow
  - agent-defaults
  - safety
  - holon-agentic-coder
created_at: 2026-10-30T08:59:32Z
updated_at: 2026-10-30T08:59:32Z
---

## Problem

When invoking `holon flow` (or `holon` subcommands) without specifying `--agent` and `--model` (and without setting
`HOLON_AGENT` / `HOLON_MODEL`), `agent_defaults.py` silently falls back:

```text
Agent runner resolved to antigravity-agent (source: fallback, no --agent, HOLON_AGENT or harness marker)
Model resolved to gemini-3.8-flash-medium (source: table, default model for antigravity-agent)
```

This silent fallback is dangerous and error-prone:

1. It permits developers and autonomous agents to inadvertently launch container tasks on whatever model happens to be
   default in the table, burning tokens or session quota on unselected models.
2. It masks omission of required model configurations in automated scripts or subagents.
3. Explicit runner and model specification is a core safety property: every flow execution must be deliberate about
   which role runner (`claude-agent`, `antigravity-agent`, etc.) and model tier (`claude-opus-5-5`, `gemini-3.8-pro`,
   `gemini-3.8-flash`, etc.) is executing each stage.

## Scope & Requirements

1. **Eliminate Silent Fallbacks**:
   - In `apps/sandbox-executor/src/sandbox_executor/agent_defaults.py`:
     - Remove `FALLBACK_AGENT = "antigravity-agent"`.
     - Remove silent fallback in `resolve_agent_runner()`. If no `--agent` flag, `HOLON_AGENT` env var, or valid harness
       marker is provided, fail closed with a clear error:
       `Error: Agent runner is mandatory. Please specify --agent <runner> or set HOLON_AGENT.`
     - Remove silent table-based default model resolution in `resolve_model()`. If no `--model` flag or `HOLON_MODEL`
       env var is provided, fail closed with a clear error:
       `Error: Model is mandatory. Please specify --model <model> or set HOLON_MODEL.`
   - Keep `LEGACY_DEFAULT_AGENT` and `LEGACY_DEFAULT_MODEL` strictly for back-filling historical provenance records
     where older ledgers lacked agent/model fields.

2. **Flow & Subcommand Invocations**:
   - Update `holon flow` and role subcommands (`holon intent`, `holon plan`, `holon execute`, `holon review`,
     `holon calibrate`):
     - When invoked without `--agent` or `--model` (and without environment variables), exit immediately with a non-zero
       exit code and display a user-friendly error message detailing supported runners and models.
     - **Checkpoint Resumption Exemption**: When resuming an in-flight flow via `holon flow --checkpoint <path>`,
       preserve the runner and model stored in the checkpoint if `--agent` / `--model` are omitted.

3. **Help Documentation & Usage**:
   - Update help text across `holon flow --help`, `holon --help`, etc. to show `--agent` and `--model` as required
     options rather than showing default fallbacks.

4. **Test Updates**:
   - Update `apps/sandbox-executor/tests/test_agent_defaults.py`, `test_cli.py`, `test_flow.py`, `test_preflight.py` to
     assert that missing runner/model raises the expected error.
   - Update existing test cases that relied on bare default resolution to pass explicit dummy/test runners and models.

## Acceptance Criteria

1. Running `holon flow <intent.json>` without `--agent` or `HOLON_AGENT` fails with non-zero exit code and a clear error
   message.
2. Running `holon flow <intent.json> --agent antigravity-agent` without `--model` or `HOLON_MODEL` fails with non-zero
   exit code and a clear error message.
3. Resuming via `holon flow --checkpoint <checkpoint.json>` successfully reads the agent and model from the checkpoint
   when flags are omitted.
4. All existing and new tests pass cleanly under `uv run pytest`.
5. Linting and formatting pass with `uv run task lint` and `npx prettier --check "**/*.md"`.
