---
# holon-agentic-coder-ref-metadata-0322
title: "Remove the gemini-agent runner, made redundant by antigravity-agent"
status: todo
type: task
priority: low
tags:
  - runners
  - cleanup
  - holon-agentic-coder
created_at: 2026-11-17T14:40:00Z
updated_at: 2026-11-17T14:40:00Z
---

## Problem

`gemini-agent` has been superseded by `antigravity-agent` and has never run a flow: `plans.jsonl` and `executions.jsonl`
record only `claude-agent` and `antigravity-agent`. It is still fully wired into `holon-agentic-coder` (`origin/main`,
2026-11-18), so `--agent gemini-agent` is still accepted and its image is still built on every bake:

- **Image**: the `agent-gemini` target in `apps/sandbox-executor/Dockerfile` and `docker-bake.hcl`, and its row in
  `docs/docker_bake.md`.
- **Runner**: `GeminiAgentRunner` and its registry entry and `gemini` validator in `agent_runner.py`.
- **Registry**: the `gemini` entries in `AGENT_IMAGE_MAPPING`, `DEFAULT_MODELS` and `RUNNER_CAPABILITIES`, and the
  `GEMINI_API_KEY`/`GOOGLE_API_KEY` and `~/.config/gcloud` auth detection, in `agent_defaults.py`; the `gemini` entry in
  `cli/__init__.py`.

## Action

Run through the Holon flow on `holon-agentic-coder`. Remove the runner, its image target and its registry entries, and
make `--agent gemini-agent` fail with a message pointing to `antigravity-agent`.

Keep what is not the runner: Gemini **models** (`gemini-3.8-flash-medium` and others) stay, since antigravity runs them;
the provider detection for `gemini` URLs in `token_reduction/mitm_addon.py` stays; the places that treat `antigravity`
and `gemini` alike (`agent_defaults.py` lines 207 and 252) need checking, not blind deletion. Historical ledger rows are
untouched.

## Notes

- Touches `agent_defaults.py`, as does Bean 0321; run the two flows one after the other. After Bean 0321 a runner
  without a ticker is rejected at intent time, so `gemini-agent` is already unusable for flows and this becomes pure
  clean-up.
- `local-model` in `RUNNER_CAPABILITIES` is a placeholder with no image, not a runner; decide here whether it stays.
