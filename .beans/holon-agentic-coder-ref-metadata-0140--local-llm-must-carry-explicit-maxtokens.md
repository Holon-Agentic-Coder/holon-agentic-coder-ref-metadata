---
# holon-agentic-coder-ref-metadata-0140
title: "local_llm must declare the sandbox's effective model envelope: maxTokens, reasoning mode, prefix cache"
status: completed
type: bug
priority: medium
tags:
  - sandbox
  - local-llm
  - pi
  - configuration
  - observability
  - reasoning
  - prefill-cache
created_at: 2026-10-22T07:20:00Z
updated_at: 2026-10-26T02:33:21Z
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

Two more knobs sit in the same "stated nowhere" class (see the live-verification findings below): **reasoning mode** —
the backend runs a `qwen3` reasoning parser and thinking is on by default while no config anywhere declares it, and
thinking tokens draw from the same 16,384 output budget as the artifact text — and **prefix cache state** — vMLX's
_Enable Prefix Cache_ / disk (dflash2) block cache and keep-warm TTL are settable only in the gateway UI, and the host
CLI never reads or reports whether flow turns hit the cache (measured: prefill 166 tps uncached vs 2,447 tps on a warm
hit), so a cold cache looks exactly like a slow model.

## Scope

### Output ceiling

- In `local_llm.prepare_agent_dir()`, require each model entry to carry an explicit `maxTokens`; when the host entry
  omits it, synthesise a conservative value (document the formula, e.g. `min(16384, context_window // 4)`) and **log the
  substitution** with model id, chosen value and reason, so the effective cap is never invisible.
- Never emit a `maxTokens` that exceeds the declared `contextWindow` minus a stated prompt reserve, and reject a
  non-positive or non-integer value with `LocalLLMConfigError` instead of passing it through.
- Reconcile with the gateway rather than only declare: when a local gateway is reachable, `holon doctor` fetches the
  per-model health endpoint and warns when the emitted `maxTokens` exceeds the server's
  `effective_defaults.max_output_tokens` or `contextWindow` exceeds `max_prompt_tokens` (the server default wins, which
  is the same silent-cap class this bean exists to eliminate).
- Print the effective per-model ceiling in the pre-flight/preflight output (Bean 0137's `holon doctor`) as
  `model=<id> context=<n> max_tokens=<n> source=host|synthesised`.

### Reasoning mode

- Let the sandbox declare a per-run reasoning override that survives into the container: `HOLON_REASONING_MODE` (default
  `auto`, or a model-specific value such as `low` where the backend honours it). The generated agent config must carry
  it (e.g. `"reasoning": true` on the model entry so pi's `--thinking` / `model:level` suffix takes effect, plus the
  chosen level), instead of leaving the model on the gateway's unmanaged default.
- For authoring stages with a fixed, small output cap, the default must be the least-thinking mode the backend accepts,
  and the choice must be logged with model id, mode and source (`env|default`), because thinking tokens consume the same
  single-response output budget as the artifact text.
- `holon doctor` reports `reasoning=<mode> source=env|host|default` alongside the `max_tokens` line.

### Prefix cache visibility

- Extend `holon doctor` to probe the local gateway's health endpoints (backend `memory.active_mb` / `peak_mb` /
  `cache_mb`, `kv_cache_quantization.enabled`, `speculative_decoding`, `last_request_time`) and report
  `prefill_cache=off|cold|warm` with the memory figures, so an operator can see whether flow turns hit the cache before
  spending an hour on a slow run. A warm hit is the difference between 166 tps and 2,447 tps on this host.
- Document the gateway-side levers that the probe reads (prefix cache enable, disk/SSD block-cache budget, TTL keep-warm
  window, `prefillStepSize` / `prefillBatchSize`) in the local-LLM docs page, using names the probe discovers rather
  than hard-coding one gateway's vocabulary, and keep every path in the target repository target-native.
- Keep the security invariant intact: only loopback and allow-listed authorities are rewritten; the added fields must
  not change mounting, `NO_PROXY` exemption, or `PI_CODING_AGENT_DIR` behaviour.
- Tests: host entry without `maxTokens` yields a logged synthesis and a valid config; an absurd `maxTokens` (larger than
  the context window, zero, or a string) fails with `LocalLLMConfigError`; the rewritten authority still points at
  `host.docker.internal`; a host entry that declares `maxTokens` is passed through untouched; `HOLON_REASONING_MODE` is
  reflected in the generated config and the doctor output; a mocked gateway health body (frozen fixture, no live call)
  parses into the `off|cold|warm` states; a mismatch between emitted `maxTokens` and the gateway's
  `effective_defaults.max_output_tokens` produces a warning, not a silent cap.

## Acceptance criteria

- Every model entry the sandbox receives declares `maxTokens` explicitly; a synthesised ceiling is always logged, never
  silent.
- The sandboxed authoring stages run at a declared, logged reasoning mode; no stage relies on the gateway's unmanaged
  default.
- `holon doctor` reports `max_tokens`, `reasoning` and `prefill_cache` (with memory figures) for the local gateway, and
  the local-LLM docs explain which gateway setting moves the `prefill_cache` value.
- `uv run pytest` passes in `apps/sandbox-executor`.

## Note for the harness (already actioned, 2026-10-22)

`~/.pi/agent/models.json` now declares `"maxTokens": 16384` for the `vmlx` model, so the current cap is stated rather
than inferred; the backup is `~/.pi/agent/models.json.bak-20261022`. This bean is about the code path that hands that
field to the sandbox, not about the host file.

## Findings — live verification against the vmlx gateway (2026-10-22T14:21Z)

Verified on the host against the running vMLX stack (vMLX.app 1.6.81, gateway `:8081`, per-model backends
`:8000`–`:8006`; loaded backend `JANGQ-AI/Qwen3.8-27B-JANG_4D` on `:8004`, M5 Max / 128 GB):

1. **Host declaration now matches server enforcement.** `~/.pi/agent/models.json` declares `maxTokens: 16384` /
   `contextWindow: 262144` for both `vmlx` models, and the vmlx server reports
   `effective_defaults.max_output_tokens: 16384` and `max_prompt_tokens: 262144` for the same model. The effective cap
   is therefore stated on both sides of the wire on the host; the 16,384 figure is a server default, not an inference.
2. **The gateway exposes the cap machine-readably.** Gateway `:8081/health` lists all backends with status and port;
   each backend `:800x/health` returns `effective_defaults` (incl. `max_output_tokens`), `max_prompt_tokens`, and the
   last request's usage. The Bean 0137 pre-flight / `holon doctor` output
   (`model=<id> context=<n> max_tokens=<n> source=host|synthesised`) should therefore **reconcile** rather than only
   declare: fetch the gateway health endpoint and warn when the emitted `maxTokens` exceeds the server's
   `effective_defaults.max_output_tokens` (the server default would win — the same silent-cap class this bean exists to
   eliminate) or when `contextWindow` exceeds `max_prompt_tokens`. The rewritten `host.docker.internal` authority
   reaches the same endpoints from the sandbox.
3. **Thinking budget has no model-side field; `maxTokens` is the only ceiling.** The JANG bundle's
   `generation_config.json` declares no thinking/max-think budget; Qwen3-style reasoning is parsed server-side (`qwen3`
   reasoning parser) and thinking tokens draw from the 16,384 output budget. pi's `vmlx` entries also declare no
   `reasoning: true` (no `samplingParamsByThinkingLevel`), so pi exposes no thinking level for these models and the
   `maxTokens` field is the sole cap. Any future per-session thinking budget must be set server-side (vmlx request
   param) and mirrored in pi's thinking-level mapping — this strengthens the case that the output ceiling must always be
   explicit and logged, as scoped above.
4. **Capacity context for why a single-response 16,384 cap is hard** (relates to Bean 0138): measured on this host —
   prefill 166 tps uncached / 2,447 tps cached (dflash2 SSD prefix-cache hit), decode 28.8 tps (speculative dflash2, ~40
   % acceptance). A worst-case 16,384-token response is ≈ 9.5 minutes of generation. KV cache is hybrid SSM/attention
   (48 linear-attention + 16 full-attention layers, GQA 24q/4kv); turboquant KV quantisation is disabled (hybrid SSM
   state), dflash2 SSD block-cache budget ≈ 185.8 GiB. Prefill throughput and KV cache size are vmlx-engine / weight
   properties — not pi settings; pi only keeps `contextWindow` in sync with `max_prompt_tokens` and declares the output
   ceiling.

## Relates to

Bean 0138 (why a single-response cap is fatal today), Bean 0139 (turn budget), Bean 0049 (the module's original
purpose).

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
