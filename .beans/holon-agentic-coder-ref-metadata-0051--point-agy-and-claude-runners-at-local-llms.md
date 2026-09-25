---
# holon-agentic-coder-ref-metadata-0051
title: "Let the AGY and Claude Code harnesses run against arbitrary / host-local LLM endpoints"
status: todo
type: feature
priority: normal
tags:
  - agent-runner
  - local-llm
  - protocol-adapter
  - mitm-addon
  - agy
  - claude-code
created_at: 2026-09-26T09:58:00Z
updated_at: 2026-09-26T09:58:00Z
---

`holon-coherence <agent>` can intercept and optimise traffic to a host-local model server (Bean 0027), but only the
harnesses that natively accept a custom endpoint can actually _use_ one. Today that means **only `pi` works**. The AGY
and Claude Code runners are the two remaining harnesses where the endpoint, the model name and the wire protocol are all
locked to the vendor, so a local model (vMLX, Ollama, LM Studio, vLLM) is unreachable no matter what `--local-llm-base`
is set to.

## Auditing the reported claims

| Claim                                   | Verdict                | Measurement                                                                                                                                                                                                                                                                      |
| --------------------------------------- | ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "agy only allows Gemini models"         | **Partly true**        | `agy models` lists 14 ids incl. `claude-sonnet-4-6`, `claude-opus-4-6-thinking`, `gpt-oss-120b-medium` -- all served by Google.                                                                                                                                                  |
| "agy cannot point at a local LLM"       | **True in effect**     | Endpoint override exists (`AGY_GATEWAY_URL`) but the CLI then speaks **Gemini `v1beta` GenerateContent**, which no local server implements (vMLX `/v1beta/models/x:generateContent` → **404**).                                                                                  |
| (new, not in the report)                | **Hard blocker**       | `agy --model ollama/llama3` → `error: invalid model selection ... model ollama/llama3 is not recognized as a known model or custom model in settings`, exit 1, **zero network requests** -- the catalog is compiled in and validated client-side.                                |
| "claude code only allows Claude models" | **False as stated**    | `ANTHROPIC_BASE_URL=http://127.0.0.1:<port>` is honoured (answered from a local stub, `result: SNIFF_OK`); `--model JANGQ-AI/Qwen3.8-...` is accepted (warns `[claude-code:unrecognized_model]`) and is sent verbatim in `"model"`.                                              |
| "claude cannot use a local LLM"         | **True in effect**     | Claude Code sends Anthropic-only extensions that local servers reject: `thinking={"type":"adaptive","display":"omitted"}`, `output_config`, `context_management`, 11 `anthropic-beta` entries. vMLX → **HTTP 400** `qwen4_exp does not support native thinking_mode='adaptive'`. |
| "only these two harnesses need rework"  | **True for this repo** | `codex` ships `model_providers` / `base_url` / `wire_api` in `~/.codex/config.toml`; `opencode` takes `options.baseURL` in `opencode.json`; `pi` takes `providers{}.baseUrl` in `~/.pi/agent/models.json` (already wired by Beans 0027/0049).                                    |

Additional constraints found while probing:

1. **`GOOGLE_GEMINI_BASE_URL` does nothing for `agy`** (0 stub hits; the CLI answered from the real gateway), while
   **`AGY_GATEWAY_URL` is fully honoured** (1903 stub hits in 45 s,
   `POST /v1beta/models/gemini-3.8-flash:streamGenerateContent?alt=sse`, `Go-http-client/1.1`, no auth header at all).
2. **Go never proxies loopback.** With `HTTP_PROXY`/`HTTPS_PROXY`/`ALL_PROXY` pointed at a dead listener, `agy` still
   reached a loopback `AGY_GATEWAY_URL` **1141 times**. Bean 0027's `NO_PROXY` pruning therefore cannot intercept an
   `agy` gateway addressed as `localhost`/`127.0.0.1`/`*.localhost` -- the exemption is inside Go's `httpproxy`, not in
   the env. (Control with the host LAN address was inconclusive on this machine: the macOS application firewall blocked
   inbound `192.168.2.13:18785` even without a proxy.)
3. **A normalising rewrite is sufficient for Claude Code.** Forwarding the same request with `thinking`, `output_config`
   and `context_management` removed turned the 400 into **HTTP 200 + valid Anthropic SSE** from vMLX. The remaining work
   is streaming fidelity -- a naive buffered forwarder stalls Claude Code, so the adapter must pass SSE through
   incrementally.
4. **Local servers here already speak two of the three protocols**: vMLX `:8081` and `:8000` serve
   `/v1/chat/completions` **and** `/v1/messages` (including SSE with `thinking_delta`). Only the Gemini shape is
   missing.
5. **Coherence's own cleaner can break a local endpoint.** `PayloadCleaner` injects
   `cache_control: {"type": "ephemeral"}` into Anthropic payloads (`payload_cleaner.py:118`, `:346`) -- fine for
   `api.anthropic.com`, unvalidated for third-party Anthropic-compatible servers.
6. **Provider detection already works for local endpoints**: `detect_provider` keys on path, not host
   (`mitm_addon.py:318`), so `…/v1/messages` → `anthropic`, `…:streamGenerateContent` → `gemini`, `…/chat/completions` →
   `openai` regardless of the authority. Telemetry does not need new detection logic.
7. **The runner has no endpoint or model surface at all**: `build_agent_env` (`cli.py:818`) copies the environment and
   maps `HOLON_AGENT_KEY` to vendor keys, and nothing ever sets `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN`,
   `AGY_GATEWAY_URL` or a model name. The README is explicit that pointing the agent is the user's job
   (`README.md:229-232`) -- and its own example
   `holon-coherence agy --local-llm-base=http://127.0.0.1:11434/v1 -- --model=ollama/llama3` is impossible for both
   reasons in the table above. The doc is wrong, not just incomplete.

## What to build

1. **First-class endpoint + model selection in the runners.** Extend the per-invocation contract (today
   `--ephemeral | --port | --local-llm-base`) with something like `--model` and `--local-llm-endpoint` semantics, so a
   single declaration both (a) routes traffic the way Bean 0027 does and (b) configures the child harness:
   - `claude`: `ANTHROPIC_BASE_URL`, `ANTHROPIC_AUTH_TOKEN` (from `HOLON_AGENT_KEY`), `--model` /
     `ANTHROPIC_DEFAULT_{SONNET,OPUS,HAIKU}_MODEL` + `ANTHROPIC_CUSTOM_MODEL_OPTION*` so slash-commands do not offer
     Claude ids, and `--fallback-model` suppressed.
   - `agy`: `AGY_GATEWAY_URL` (never `GOOGLE_GEMINI_BASE_URL`), plus a **catalog-alias → local-model id map**, since the
     CLI refuses any `--model` outside its compiled-in catalog. Investigate the `customModels` settings path first (the
     binary carries `customModelsConfig`, `customModels[%s]: modelName is required`, `modelNameOverride`); the guessed
     `settings.json` shape (`{"customModels": {"localqwen": {"modelName": ...}}}`) was rejected, so the real schema is
     still to be found.
   - `codex` / `opencode` / `pi`: only pass-through and documentation work; their native provider config stays the
     source of truth.
2. **Wire adapters inside the existing addon path.** `mitm_addon.py` already rewrites outbound bodies with
   `flow.request.set_text(...)` (`:1222`), so this is the natural home:
   - `_strict-anthropic_` mode: strip/normalise `thinking`, `output_config`, `context_management`, unknown
     `anthropic-beta` entries and (optionally) the injected `cache_control` breakpoints when the upstream is not
     `api.anthropic.com`.
   - `_gemini bridge_`: translate `POST /v1beta/models/<id>:streamGenerateContent?alt=sse` ↔ the local
     `/v1/chat/completions` (or `/v1/messages`) endpoint in both directions, including SSE event re-encoding,
     `systemInstruction` → system message, `functionCall`/`functionResponse` ↔ `tool_calls`, and `usageMetadata`.
     Without this, `agy` + local model is not reachable at all.
   - Keep both behind an explicit opt-in (per invocation or per endpoint); cloud traffic must keep today's behaviour
     bit-for-bit.
3. **Interception for clients that refuse to proxy loopback (agy).** Because Go hard-codes the localhost exemption, the
   runner must hand the child a **non-loopback spelling** of the declared endpoint (the host's own address from the Bean
   0027 equivalence class, or a synthetic name such as `holon-llm.internal` resolved via `--add-host`-style mapping)
   while the container-side rewrite keeps dialling `host.docker.internal`. Document the Go rule where `NO_PROXY` pruning
   is described, so nobody re-adds a `localhost` example for `agy`.
4. **Fix the docs and the examples** in `README.md` / `AGENTS.md`: the current `agy` sample is unrunnable; state which
   protocols each local server speaks and that `--local-llm-base` alone still does not point the agent at a model.

## Acceptance criteria

- [ ] `holon-coherence claude` completes a real multi-turn round trip against a host-local Anthropic-compatible server
      (vMLX `:8081` here) with the model served locally, the transaction present in the wire logs, and token reduction
      recorded -- i.e. the `thinking` / `output_config` / `context_management` 400 is gone.
- [ ] `holon-coherence agy` completes a real round trip against the same host-local server through the Gemini bridge,
      with the catalog alias resolving to the local model id and the exchange visible in the wire logs.
- [ ] `agy` traffic is provably intercepted: the child receives a non-loopback endpoint spelling, and a wire log exists
      proving the proxy saw the request (a loopback-addressed gateway must emit an actionable diagnostic, not silently
      bypass the proxy).
- [ ] Cloud paths are unchanged: with no local endpoint declared, `claude` keeps `thinking`, betas and `cache_control`
      injection exactly as today (assert with existing suites plus new tests).
- [ ] Unit tests: endpoint/model env matrix per harness; the strict-Anthropic field-stripping table; Gemini ↔ OpenAI
      translation for text, streaming, tool calls and usage metadata; the non-loopback alias planner; provider detection
      for the three local URL shapes.
- [ ] `uv run pytest -m "not integration_test"` green, `uv run ruff check .` / `ruff format --check .` clean, and one
      verification against a **real** local model (no synthetic benchmarks, per repo rule 10).

## Notes

- Target repository: `holon-coherence` -- `src/holon_coherence/cli.py` (`build_agent_env`, `extract_runner_flags`,
  `run_agent`, `_print_agent_help`), `src/holon_coherence/mitm_addon.py` (`request`, `responseheaders`,
  `detect_provider`), `src/holon_coherence/payload_cleaner.py`, `src/holon_coherence/host_local.py`, tests in
  `tests/test_cli.py`, `tests/test_host_local.py`, `tests/test_coherence.py`, plus `README.md` / `AGENTS.md`.
- Work in a dedicated worktree off `origin/main` (`apps/holon-coherence/feat-0051-...`), never in
  `apps/holon-coherence/main`.
- Related: Bean 0026 (runners), Bean 0027 (host-local routing, the routing half this bean builds on), Bean 0033
  (`--native` removed -- there is no non-container escape hatch to fall back on), Bean 0049 (sandbox-side twin).
- Inherited safety invariant: rewrite **only** loopback plus explicitly declared authorities; never blanket-rewrite
  RFC1918 ranges.
- Out of scope: making `agy` accept a non-catalog model id without an alias (client-side validation, not ours to
  bypass), and protocol work for `codex` / `opencode` / `pi`, which already speak to custom endpoints natively.

## Resolution

Not yet started.
