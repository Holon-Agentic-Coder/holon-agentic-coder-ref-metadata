---
# holon-agentic-coder-ref-metadata-0049
title: "Allow sandboxed Holon agents to use host-local LLM endpoints (vMLX, Ollama, LM Studio, vLLM)"
status: in-progress
type: task
priority: normal
tags:
  - sandbox-executor
  - agent-runner
  - local-llm
  - networking
created_at: 2026-09-26T11:05:00Z
updated_at: 2026-09-26T15:20:00Z
---

The `holon plan` / `holon execute` sandbox can only ever run an agent that talks to a **cloud** provider. An agent
backed by a host-local inference server (vMLX, Ollama, LM Studio, vLLM, llama.cpp) cannot run in the sandbox at all,
even though the same agent works perfectly on the host. This is the sandbox-side twin of Bean 0027, which fixed the
mirror-image defect in `holon-coherence` (host-side agent, container-side proxy, host-local upstream unreachable).

## Context and measured evidence (2026-09-26)

Discovered while selecting the executor agent for the Bean 0019 flow iteration: `--agent pi-agent` is unusable on this
host, not because a key is missing (the host `pi` uses a **keyless local** provider), but because of four independent
defects.

Host state: `pi` 0.84.3, provider `vmlx` declared in `~/.pi/agent/models.json` as
`baseUrl = http://192.168.2.13:8081/v1` (`api = openai-completions`, `apiKey` placeholder), vMLX listening on `*:8081`.

Connectivity probes executed from inside `holon/agent-pi:latest`:

| Probe from inside the sandbox container                            | Result                        |
| ------------------------------------------------------------------ | ----------------------------- |
| `http://host.docker.internal:8081/v1/models`                       | **200 OK**                    |
| `http://host.docker.internal:8000/v1/models`, `:18099`             | **200 OK**                    |
| `http://172.17.0.1:8081` (docker bridge)                           | unreachable (`http=000`)      |
| `http://192.168.2.13:8081` (host LAN IP -- the host's own baseUrl) | unreachable (Bean 0027 proof) |

The container _can_ reach the host, but only through the Docker gateway name, and no part of the sandbox tells the agent
about it.

## Defects to fix

1. **Validation has no keyless local path.** `AgentRunner.validate()` requires `HOLON_AGENT_KEY` (or a session dir) for
   `pi` and `claude` and calls `sys.exit(1)` otherwise. Only `codex` has a keyless escape (`HOLON_AGENT_OSS_MODE=true`),
   so the 3-Tier Fallback Contract is asymmetric: a local provider that legitimately needs no credential can never
   start.
2. **The pi config directory is wrong, so nothing is mounted.** `get_agent_session_mounts()` maps `~/.config/pi`, but pi
   > = 0.84 stores providers and models in `~/.pi/agent/` (`models.json`). `~/.config/pi` does not exist on this host,
   > so the container receives no provider definition at all and the `vmlx` provider is simply unknown inside the
   > sandbox.
3. **A verbatim mount would still fail.** The host `baseUrl` uses the host LAN IP, which is not routable from the
   container network namespace. The authority must be rewritten to the gateway host, exactly the client-side counterpart
   of the `server_connect` rewrite Bean 0027 added server-side in `holon-coherence`.
4. **`--add-host=host.docker.internal:host-gateway` is only emitted for the token-reduce sidecar.** The existing
   `_host_gateway_docker_args()` helper is not applied to the agent or orchestrator container runs, so on Linux the
   gateway name does not even resolve.
5. **`--token-reduce` intercepts the local endpoint.** `NO_PROXY_HOSTS` exempts loopback only, so an endpoint addressed
   via the gateway name is decrypted and re-signed by the sidecar. Whatever exemption is chosen must be explicit and
   narrow.

## Acceptance criteria

- [ ] A keyless local provider can drive `holon plan` / `holon execute`: with local mode enabled and a local base URL
      configured, `validate()` returns without demanding `HOLON_AGENT_KEY`, for `pi` (and at least one other runner).
- [ ] The real pi configuration location (`~/.pi/agent`, containing `models.json`) is mounted into the sandbox, with the
      legacy `~/.config/pi` kept as a fallback, and the container-side `pi` reports the host provider as available.
- [ ] When local mode is requested, the provider `baseUrl` presented to the container is rewritten so loopback and
      explicitly declared host-local authorities resolve through `host.docker.internal`, while genuinely remote hosts
      are left untouched. **Safety invariant inherited from Bean 0027: never blanket-rewrite RFC1918 ranges -- rewrite
      only loopback plus an explicit allow list.**
- [ ] `--add-host=host.docker.internal:host-gateway` is applied to every agent and orchestrator container run, not just
      the proxy sidecar, so behaviour is identical on Docker Desktop and Linux.
- [ ] A full `pi` round trip completes inside the sandbox against a host-local OpenAI-compatible server (real request,
      no synthetic workload), and the failure path emits actionable diagnostics naming the resolved gateway address and
      the base URL handed to the agent.
- [ ] Unit tests cover: the rewrite decision table (loopback, declared host-local, LAN host, public host), the
      `--add-host` arg emission for agent runs, config-dir mount selection (new vs legacy path, absent on host), and the
      keyless `validate()` branch. All existing suites stay green under `uv run pytest`.

## Notes

- Target repository: `apps/holon-agentic-coder/` -- `apps/sandbox-executor/src/sandbox_executor/cli.py`,
  `apps/sandbox-executor/src/sandbox_executor/agent_runner.py`, tests under `apps/sandbox-executor/tests/test_cli.py`
  and `tests/test_agent_runner.py`, plus `docs/executor/agent_credentials_requirements.md`.
- Related: Bean 0027 (coherence proxy -> host-local LLM, completed, same class of bug from the opposite direction), Bean
  0026 (coding agent runners), Bean 0033 (removal of the native-host mitmproxy flag), Bean 0019 (executor git recovery,
  currently paused at its execute stage).
- **Deviation from the Sole Change Path rule (recorded per `.agents/rules.md` invariant 8):** this change is authored on
  a host worktree rather than through the Holon flow, by explicit user instruction, because the defect being fixed is
  precisely what prevents the flow's own sandbox from reaching the host-local LLM -- the flow cannot build or verify its
  own prerequisite. The Holon flow remains required for every other target-repo change.

## Resolution

Implemented on branch `fix/0049-sandbox-host-local-llm` (single commit `836dfc5`) and opened as PR #57.

### Status audit (2026-09-26) -- loop is running in a CONCURRENT session, do not duplicate

When first audited this session the PR carried zero reviews and the head was still `836dfc5`, so the earlier claim "the
pr-review-loop skill is running against it" looked unsupported. It is now confirmed true: a separate long-lived AGY
session (`agy` pid 92998, up since 09:29) is executing the loop in this same working tree. Evidence:

| Time (local) | Artifact                                                                                                     |
| ------------ | ------------------------------------------------------------------------------------------------------------ |
| 15:21        | `.subagent/dry_run_review_iter_1_836dfc5.md`                                                                 |
| 15:27        | resolver commit `b291de3` "fix: apply validated PR review suggestions (Iteration 1)", pushed                 |
| 15:31        | `.subagent/dry_run_review_iter_2_b291de3.md` -- verdict `CHANGES_REQUESTED` (0 Critical, 3 Important, 3 Nit) |

Because a live loop owns the branch, this session deliberately does **not** spawn a second reviewer or resolver against
PR #57: two agents reviewing one ref risks duplicate posted reviews and ref races (see the `CONCURRENT AMEND HAZARD`
constraint in `.subagent/coordination.json`). Zero reviews/comments is expected mid-loop -- the skill only posts once a
clean consensus pass is reached. Original audit snapshot, still accurate for the code state:

| Signal                                       | Value                                                                    |
| -------------------------------------------- | ------------------------------------------------------------------------ |
| PR #57 state                                 | `OPEN`, `mergeable`, head `836dfc5`                                      |
| `pulls/57/reviews`                           | **0** (no reviews of any state)                                          |
| `issues/57/comments`                         | **0** (no consensus report posted)                                       |
| `pulls/57/comments` (inline review comments) | **0**                                                                    |
| CI                                           | 9/9 green (unit ×2, integration, hygiene, build ×2, CodeQL, 2 × Analyze) |

So stages 1-3 of the flow are complete for this bean and stage 4 (PR review loop) is mid-flight in the other session.
Bean stays `in-progress` until the ensemble consensus review is approved and posted; merging remains human-only (Bean
0034). The three open Important findings to watch for are `models.json` mode being masked by host `umask`, a duplicate
`--add-host` flag when `--token-reduce` is active on Linux, and `HOLON_HOST_LOCAL_HOSTS` not matching port-qualified
authorities.

### What changed

- **`apps/sandbox-executor/src/sandbox_executor/local_llm.py` (new)** -- opt-in (`HOLON_LOCAL_LLM=1`) generation of a
  container-side pi agent directory. Every provider `baseUrl` is rewritten to `host.docker.internal` only when its
  authority is loopback or explicitly declared in `HOLON_HOST_LOCAL_HOSTS`; all other fields (api, `apiKey` including
  `$VAR` interpolation, models) are preserved. Config is synthesized from `HOLON_LOCAL_BASE_URL` / `HOLON_LOCAL_MODELS`
  / `HOLON_LOCAL_PROVIDER` when the host has no `models.json`. Unsatisfiable local mode raises `LocalLLMConfigError`
  instead of starting an agent that can only fail later.
- **`cli.py`** -- `--add-host=host.docker.internal:host-gateway` emitted on every container run, not only the
  token-reduce sidecar; `~/.pi/agent` mounted alongside legacy `~/.config/pi`; in local mode the host agent directory is
  deliberately not mounted, so host cloud credentials and session history stay on the host; the rewritten endpoint is
  added to `NO_PROXY` while the sidecar is active; the generated temp directory is removed on every exit path.
- **`agent_runner.py`** -- `validate()` accepts local mode in place of `HOLON_AGENT_KEY`, closing the asymmetry with
  codex's `HOLON_AGENT_OSS_MODE`. The opt-in alone is not sufficient: an actual endpoint (`PI_CODING_AGENT_DIR` or
  `HOLON_LOCAL_BASE_URL`) must be present, so a stray flag cannot mask a missing cloud key.
- **`tests/test_local_llm.py` (new)** plus the documented contract in `docs/executor/agent_credentials_requirements.md`.

### Verification

`uv run pytest -m "not integration_test"`: 285 passed, 6 deselected. `uv run ruff check .` and
`uv run ruff format --check .` clean; `uv lock --check` clean. CI on PR #57: unit (ubuntu + macOS), integration,
hygiene, build matrix, CodeQL and language analysis all pass.

Round trip against the real host-local endpoint with an authentic request (driver retained at `todo/verify-0049.py`,
git-ignored). Host `models.json` baseUrl was `http://localhost:8081/v1`; the generated container config presented
`http://host.docker.internal:8081/v1`:

| Probe inside `holon/agent-pi` (pi 0.84.3)                               | Result                   |
| ----------------------------------------------------------------------- | ------------------------ |
| `getent hosts host.docker.internal`                                     | `192.168.65.254`         |
| control: host LAN address `:8081/v1/models`                             | `http=000` (unreachable) |
| fixed: gateway address `:8081/v1/models`                                | `http=200`               |
| `PI_CODING_AGENT_DIR` honoured; agent dir listing                       | `models.json`            |
| `pi --list-models` matched the host model                               | `1`                      |
| `pi -p --provider vmlx --model JANGQ-AI/Qwen3.8-Flash-Next-JANG_4M ...` | **`LOCAL_OK`**           |

Note: rewriting proved necessary even though the host config already used `localhost`, because container loopback is the
container itself -- the loopback row of the decision table is the common case, not an edge case.
