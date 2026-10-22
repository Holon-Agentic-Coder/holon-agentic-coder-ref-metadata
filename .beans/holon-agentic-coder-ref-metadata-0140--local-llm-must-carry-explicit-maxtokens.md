---
# holon-agentic-coder-ref-metadata-0140
title: "local_llm must carry an explicit maxTokens into the generated sandbox agent config"
status: todo
type: bug
priority: medium
tags:
  - sandbox
  - local-llm
  - pi
  - configuration
  - observability
created_at: 2026-10-22T07:20:00Z
updated_at: 2026-10-22T07:20:00Z
---

## Problem

In host-local model mode the sandbox receives a _generated_ `models.json`, and the generator copies the host entry
field-for-field with only the authority rewritten. `sandbox_executor/local_llm.py` contains no handling of `maxTokens`
(grep for `maxTokens` / `contextWindow` in that module returns nothing), so a host entry that omits the field hands the
sandboxed agent an **undisclosed** output ceiling.

pi sends `max_tokens: options?.maxTokens ?? model.maxTokens`, so an omitted field becomes pi's internal fallback.
Measured on the host-local gateway: a single response ended with `stopReason: length` at `usage.output: 16384`, i.e. an
effective 16,384-token output cap that was declared nowhere, while the entry did declare `contextWindow: 262144`. That
cap is what killed the Bean 0132 planner run (see Bean 0138 for why the stage could not route around it).

This is exactly the class of failure `local_llm.py` exists to prevent — its own docstring says the module's job is to
tell the sandboxed agent facts it would otherwise not know because the host's addressing does not survive into the
container namespace. Output ceilings belong in the same category, and the module's own error type
(`LocalLLMConfigError`, "never silently degraded") is the natural place for it.

## Scope

- In `local_llm.prepare_agent_dir()`, require each model entry to carry an explicit `maxTokens`; when the host entry
  omits it, synthesise a conservative value (document the formula, e.g. `min(16384, context_window // 4)`) and **log the
  substitution** with model id, chosen value and reason, so the effective cap is never invisible.
- Never emit a `maxTokens` that exceeds the declared `contextWindow` minus a stated prompt reserve, and reject a
  non-positive or non-integer value with `LocalLLMConfigError` instead of passing it through.
- Print the effective per-model ceiling in the pre-flight/preflight output (Bean 0137's `holon doctor`) as
  `model=<id> context=<n> max_tokens=<n> source=host|synthesised`.
- Keep the security invariant intact: only loopback and allow-listed authorities are rewritten; the added field must not
  change mounting, `NO_PROXY` exemption, or `PI_CODING_AGENT_DIR` behaviour.
- Tests: host entry without `maxTokens` yields a logged synthesis and a valid config; an absurd `maxTokens` (larger than
  the context window, zero, or a string) fails with `LocalLLMConfigError`; the rewritten authority still points at
  `host.docker.internal`; a host entry that declares `maxTokens` is passed through untouched.

## Acceptance criteria

- Every model entry the sandbox receives declares `maxTokens` explicitly.
- A synthesised ceiling is always logged, never silent.
- `uv run pytest` passes in `apps/sandbox-executor`.

## Note for the harness (already actioned, 2026-10-22)

`~/.pi/agent/models.json` now declares `"maxTokens": 16384` for the `vmlx` model, so the current cap is stated rather
than inferred; the backup is `~/.pi/agent/models.json.bak-20261022`. This bean is about the code path that hands that
field to the sandbox, not about the host file.

## Relates to

Bean 0138 (why a single-response cap is fatal today), Bean 0139 (turn budget), Bean 0049 (the module's original
purpose).
