---
# holon-agentic-coder-ref-metadata-0010
title: Abstract all agent-specific env vars to `HOLON_AGENT_*` prefix
status: done
type: task
priority: high
created_at: 2026-07-26T21:28:00Z
updated_at: 2026-07-27T18:48:00Z
branch_metadata: feat/holon-agent-envvar-abstraction
branch_ref: feat/holon-agent-envvar-abstraction
---

## Overview

Currently, `agent_runner.py` in `apps/sandbox-executor` accepts and passes through a mix of agent-specific environment
variables (e.g. `AGY_EFFORT`, `PI_PROVIDER`, `CLAUDE_SETTINGS`, `CODEX_OSS`). These leak agent implementation details
into the orchestrator interface, making the system harder to reason about and tightly coupled to individual agent CLIs.

This task replaces **all** agent-specific env vars with a standardised `HOLON_AGENT_*` prefix. The agent runner is then
responsible for mapping each `HOLON_AGENT_*` var to its agent-specific equivalent internally, keeping the public
interface completely agent-agnostic.

This is a **hard cutover** — old agent-specific env vars are removed entirely (no fallback, no deprecation warnings).

---

## Env Var Mapping

| Old (agent-specific)                                                                                                                                                                      | New (`HOLON_AGENT_*`)              | Passed to                                |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- | ---------------------------------------- |
| `AGY_USER_TOKEN`, `AGY_SESSION_TOKEN`, `GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`, `CLAUDE_CODE_API_KEY`, `PI_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, `OPENCODE_API_KEY`, `KIMI_API_KEY` | `HOLON_AGENT_KEY` (already exists) | All agents — canonical auth var          |
| `AGY_EFFORT`                                                                                                                                                                              | `HOLON_AGENT_EFFORT`               | `agy --effort`                           |
| `PI_PROVIDER`, `OPEN_CODEX_PROVIDER`                                                                                                                                                      | `HOLON_AGENT_PROVIDER`             | `pi --provider`, `open-codex --provider` |
| `CLAUDE_SETTINGS`                                                                                                                                                                         | `HOLON_AGENT_SETTINGS`             | `claude --settings`                      |
| `CODEX_CONFIG`                                                                                                                                                                            | `HOLON_AGENT_CONFIG`               | `codex -c`                               |
| `OPENCODE_AGENT`                                                                                                                                                                          | `HOLON_AGENT_MODE`                 | `opencode --agent`                       |
| `CODEX_OSS`                                                                                                                                                                               | `HOLON_AGENT_OSS_MODE`             | `codex --oss` (boolean flag)             |
| `CODEX_LOCAL_PROVIDER`                                                                                                                                                                    | `HOLON_AGENT_LOCAL_PROVIDER`       | `codex --local-provider`                 |

---

## Files to Change

- `apps/sandbox-executor/src/sandbox_executor/agent_runner.py` — primary change:
  - Update all `EnvMapping` entries to use `HOLON_AGENT_*` env var names.
  - Update `AntigravityAgentRunner.build_cmd` to read `HOLON_AGENT_EFFORT` instead of `AGY_EFFORT`.
  - Update `validate()` and `_apply_generic_token()` to remove references to old agent-specific auth env vars.
  - Update `required_keys` lists on all `StandardAgentRunner` instances to use `HOLON_AGENT_KEY` only.
  - Update error messages in validators to reference `HOLON_AGENT_KEY` instead of old vars.
- `apps/sandbox-executor/tests/test_agent_runner.py` — update all test fixtures and assertions to use the new
  `HOLON_AGENT_*` env var names.
- Any docs or README files referencing old env vars (check `docs/`, `intents/README.md`, `README.md`).

---

## Acceptance Criteria

- [x] No agent-specific env var names (`AGY_*`, `PI_*`, `OPEN_CODEX_*`, `CLAUDE_*`, `CODEX_*`, `OPENCODE_*`,
      `ANTHROPIC_*`, `OPENAI_*`, `GEMINI_*`, `GOOGLE_API_KEY`, `KIMI_*`) remain in `agent_runner.py`.
- [x] All new `HOLON_AGENT_*` vars are correctly mapped to their agent-specific CLI flags inside each runner.
- [x] Auth consolidation: `HOLON_AGENT_KEY` is the single canonical auth env var; `_apply_generic_token` and all
      validators reference only `HOLON_AGENT_KEY`.
- [x] All existing unit tests pass with updated env var names.
- [x] Docs/README updated to reflect new env var interface.
- [x] All Python formatters and linters pass.

---

## Branches

- **Metadata repo** (`holon-agentic-coder-ref-metadata`): `feat/holon-agent-envvar-abstraction`
- **Reference repo** (`holon-agentic-coder-ref`): `feat/holon-agent-envvar-abstraction`
  - Worktree path: `holon-agentic-coder-ref/feat-holon-agent-envvar-abstraction`
  - Based off: `origin/develop`

---

## Resolution

- Replaced all agent-specific env vars with `HOLON_AGENT_*` equivalents in `agent_runner.py` and `cli.py`.
- Completely removed legacy/vendor API key fallbacks and checks from validation logic, so validators strictly expect
  `HOLON_AGENT_KEY` (or `HOLON_AGENT_OSS_MODE`).
- Automatically forward all environment variables starting with `HOLON_AGENT_` and `GITHUB_TOKEN` from host `os.environ`
  to the Docker container.
- Pushed target CLI native variables mapping out of Python to the container boundary (`role_dispatcher.sh`). It detects
  the active `HOLON_AGENT_ID` and maps `HOLON_AGENT_KEY` (whether passed directly or extracted from an ephemeral secret
  bundle via `jq`) into target API key variables before executing Python.
- Added comprehensive unit tests: `test_run_docker_container_forward_env_vars` to assert forwarding of variables and
  `test_secret_bundle_api_key_only` to verify config files unpacking.
- Documented single-agent-per-execution assumption near the runner registry.
- Removed `MIGRATION.md` documentation file as requested.
- Formatted python code with `ruff format` and verified ruff check and prettier are passing successfully.
- Verified all unit and integration tests compile and pass cleanly on local and remote environments.
