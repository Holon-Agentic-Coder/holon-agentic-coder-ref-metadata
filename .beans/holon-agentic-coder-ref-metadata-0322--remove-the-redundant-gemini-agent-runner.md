---
# holon-agentic-coder-ref-metadata-0322
title: "Completely remove the gemini-agent runner and all gemini runner special-cases"
status: in-progress
type: task
priority: low
tags:
  - runners
  - cleanup
  - holon-agentic-coder
created_at: 2026-11-17T14:40:00Z
updated_at: 2026-11-20T23:44:00+11:00
---

## Problem

`gemini-agent` has been superseded by `antigravity-agent` and has never run a flow: `plans.jsonl` and `executions.jsonl`
record only `claude-agent` and `antigravity-agent`. It is still wired into `holon-agentic-coder`:

- **Image & docs**: the `agent-gemini` target in `apps/sandbox-executor/Dockerfile` and `docker-bake.hcl`, its row in
  `apps/sandbox-executor/docs/docker_bake.md`, and `gemini-agent` entries in `docs/agents.md` and
  `docs/planner/agent_credentials_requirements.md`.
- **Runner**: `GeminiAgentRunner`, its registry entry, and the `"gemini"` `custom_validator` branch in
  `agent_runner.py`.
- **Registry & CLI**: the `gemini` entries and comments in `AGENT_IMAGE_MAPPING`, `DEFAULT_MODELS`,
  `RUNNER_CAPABILITIES`, and `GEMINI_API_KEY`/`GOOGLE_API_KEY`/`~/.config/gcloud` runner auth detection in
  `agent_defaults.py`; the `"gemini"` mount entry in `cli/__init__.py`; and `gemini` in `cli/commands/models.py` help
  text.

## Action

Run through the Holon flow on `holon-agentic-coder` (maintainer decision 2026-11-20: complete removal with **no**
special-case deprecation or migration branches for `gemini`):

- Remove the runner, its image target, its registry/default/capability/auth/mount entries, its CLI help reference, and
  its docs rows completely.
- Do **not** add `if agent_id == "gemini":` or `if norm == "gemini":` special-case checks anywhere — passing
  `--agent gemini-agent` or `--agent gemini` must simply fail through the standard generic unsupported-runner error
  path.
- Keep only what is not the `gemini-agent` runner: Gemini **models** (`gemini-3.8-flash`, `gemini-3.8-flash-medium`,
  etc.) under `antigravity-agent`, `antigravity-agent`'s `~/.gemini/antigravity-cli` session mounts and effort
  coordination, `local-model` in `RUNNER_CAPABILITIES`, `gemini` URL detection in `token_reduction/mitm_addon.py`,
  Google/Gemini API key patterns in `knowledge/records.py`, and untouched historical ledger rows.
- Update tests and add hermetic assertions verifying `gemini` / `gemini-agent` is rejected as an unsupported runner with
  no `gemini`-specific runner code remaining.

## Notes

- PR #218 (`remove-gemini-agent-runner`) was closed on 2026-11-20 because it followed the earlier wording and added
  `if agent_id == "gemini":` / `if norm == "gemini":` migration branches; replaced by fresh flow
  `purge-gemini-agent-runner`.
- `local-model` in `RUNNER_CAPABILITIES` stays (maintainer decision 2026-11-20, used by Bean 0226).
