---
# holon-agentic-coder-ref-metadata-0248
title: "Add holon models command to list supported models across agent runners"
status: in-progress
type: feature
priority: high
tags:
  - cli
  - models
  - agent-runner
  - discovery
  - holon-agentic-coder
created_at: 2026-11-07T02:35:00Z
updated_at: 2026-11-07T02:35:00Z
---

## Problem

Currently, developers and autonomous agents have no way to discover which models, aliases, and reasoning effort levels
are supported across coding agent runners without trial and error or failing pre-flight probes.

For example:

- Passing `--model gemini-3.8-pro` to `antigravity-agent` fails because `--effort` is unsupported on Pro models by
  `agy`.
- Passing `--model gemini-3.8-flash-high` fails unless `HOLON_AGENT_EFFORT=high` is explicitly set due to a conflict
  with the default `--effort medium`.
- Passing Claude models requires knowing specific aliases (`fable`, `opus`, `sonnet`, `haiku`).
- Running `holon doctor` without a model errors out fail-closed with `Model is mandatory` rather than listing the valid
  choices for the specified runner.

Without an introspection command, operators frequently hit invalid model selection errors, wasting debugging time and
flow setup overhead.

## Goal

Add a dedicated `holon models` (and `holon list-models`) command to inspect and list supported models, aliases, effort
levels, and fallback ladders across all registered agent runners.

### 1. `holon models` CLI Command

Create `apps/sandbox-executor/src/sandbox_executor/cli/commands/models.py` registered in `cli/main.py`:

```bash
# List all supported models across all registered agent runners
holon models

# Filter by a specific agent runner
holon models --agent antigravity-agent
holon models --agent claude-agent

# Output structured JSON for automation and agent scripts
holon models --json
```

Output format should present a clear, human-readable table containing:

- **Runner**: Agent runner name (`antigravity-agent`, `claude-agent`, `pi-agent`, etc.).
- **Model**: Canonical model identifier and known aliases.
- **Effort / Reasoning**: Supported effort levers (e.g. `low`, `medium`, `high`, or `none`).
- **Tier / Ladder**: Fallback ladder priority (Primary, Secondary, Fallback).
- **Status / Auth**: Whether local credentials or session tokens are currently detected.

### 2. Centralised Model Registry & Capabilities

Define a centralised specification in `apps/sandbox-executor/src/sandbox_executor/agent_defaults.py` (or a dedicated
`model_registry.py`):

- Mapping of runners to supported model envelopes, aliases, and allowed effort configurations.
- Automatic normalisation and conflict detection (e.g. ensuring `-high` / `-medium` model suffixes correctly set or
  validate `--effort`).
- Discovery of local credentials/sessions for each runner without leaking secret values.

### 3. Integration with `holon doctor` & Pre-flight Hints

- When `holon doctor` is invoked without `--model`, or when an invalid model string is passed:
  - Display the specific available models for the selected agent.
  - Suggest running `holon models` for the complete matrix.

### 4. Hermetic Unit Tests (Minimise Mocking)

In `apps/sandbox-executor/tests/test_models_cli.py`:

- Test `holon models` outputs the complete table across all registered runners.
- Test `holon models --agent <name>` filters results strictly to that runner.
- Test `holon models --json` emits valid JSON matching the schema.
- Test invalid runner names produce clean, helpful error messages.
- Test against real runner configurations without mocking internal data structures.

## Constraints

- Australian English spelling in all documentation and code comments.
- Zero new external dependencies; dependencies managed strictly via `uv`.
- All tests executed strictly via `uv run pytest`.
- Linting and documentation gates (`uv run task check` or `make lint`) must pass cleanly.
- Keep target repositories isolated with zero harness path leaks.
- Merge remains human-only.
