---
# holon-agentic-coder-ref-metadata-0270
title: "Discover runner models dynamically through each harness instead of the hardcoded model table"
status: todo
type: task
priority: high
tags:
  - models
  - harness
  - antigravity
  - holon-agentic-coder
created_at: 2026-11-10T03:08:00Z
updated_at: 2026-11-10T03:12:00Z
---

## Problem

`holon models`, `holon doctor` and model validation read the hardcoded `RUNNER_CAPABILITIES` table in
`apps/sandbox-executor/src/sandbox_executor/agent_defaults.py`. Harness model catalogues change independently of
`holon`, so the table is always stale. Observed 2026-11-10: `agy models` (run in `holon/agent-antigravity`) lists
`gemini-4-argon-*`, `gemini-3.8-flash-*`, `claude-opus-5-5-*`, `claude-sonnet-5-5-*` and `gpt-oss-120b-medium`, while
`holon models` lists only three Gemini 3.8 Flash entries and rejects the rest with `Unrecognised model`. Claude Sonnet
5.5 works through `agy` (`pong` returned) but `holon` cannot select it, which left Bean 0262 with no usable runner when
the Gemini quota ran out.

## Decision

Do not add Sonnet 5.5 to the table. Remove the hardcoded catalogue and resolve models per harness, dynamically:

- Each runner provides its own model discovery through its harness (for `antigravity-agent`, `agy models` run inside the
  runner image, which prints `<id>\t<label>`; other runners use their own CLI or config, and a runner with no discovery
  mechanism accepts the model verbatim and lets the harness reject it).
- `holon models`, `holon doctor` and `--model` validation use the discovered list. Effort levels come from the id suffix
  (`-low|-medium|-high`) the harness reports, not from a table.
- Fallback ladders are derived from the discovered list (order reported by the harness, or explicit
  `HOLON_MODEL_FALLBACKS`), not hardcoded names such as `gemini-3.8-pro`.
- Discovery results are cached briefly, and a discovery failure (not logged in, quota, no image) reports the cause
  rather than falling back to a stale list.

## Scope

- `apps/sandbox-executor/src/sandbox_executor/agent_defaults.py` and the callers of `get_model_capabilities`,
  `is_valid_model_for_runner`, `normalise_model_and_effort`, `default_model_for`
- `holon models` and `holon doctor` commands; `run_holon_flow.py` ladders in this harness repo
- tests and docs that enumerate models

## Notes

- Must be produced by `holon flow`. The flow is blocked (Antigravity quota ~92h, `claude-agent` `NOT_LOGGED_IN`), so it
  needs a Claude login or an explicit maintainer instruction to hand-author it.
- Bean 0262 resumes once a runner is usable.
