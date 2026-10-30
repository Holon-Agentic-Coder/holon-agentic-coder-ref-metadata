---
# holon-agentic-coder-ref-metadata-0198
title: "Agent runner registry: one RunnerSpec module per agent instead of shared dicts and an if-chain"
status: todo
type: task
priority: normal
tags:
  - refactor
  - open-closed
  - agent-runner
  - holon-agentic-coder
blocked_by:
  - holon-agentic-coder-ref-metadata-0185
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-29T12:20:00Z
---

## Problem

Spawned by Bean 0177. Facts about each agent are spread over shared structures on `993b686`:
`agent_defaults.AGENT_IMAGE_MAPPING` and `DEFAULT_MODELS` (six entries each) and `StandardAgentRunner.validate` (CC 31,
one branch per `custom_validator`). Adding or dropping an agent edits all of them, plus `role_dispatcher.sh` and
`docker-bake.hcl`, so two runner changes always conflict (`agent_runner.py` 16 commits, `test_agent_runner.py` 17).

## Scope

1. `runners/<agent>.py` per agent (`antigravity`, `claude`, `pi`, `codex`, `gemini`, `opencode`) defining a `RunnerSpec`
   (image, default model, credential check, env mapping).
2. `runners/__init__.py` discovers the specs from the package; `AGENT_IMAGE_MAPPING`/`DEFAULT_MODELS` become derived
   views (or are removed with callers updated).
3. `StandardAgentRunner.validate` calls `spec.check_credentials()`; no per-agent branches remain in it.
4. A test asserts every spec has an image built by `docker-bake.hcl` and a dispatcher case in `role_dispatcher.sh`.
5. `HOLON_AGENT_KEY` stays the only credential variable outside container entrypoints.

## Touch set

`agent_defaults.py`, `agent_runner.py`, new `runners/`, `tests/test_agent_runner.py`, `tests/test_agent_defaults.py`.

## Dependencies

Blocked by 0185. Parallel-safe with 0187, 0188, 0195.

## Notes

- Run through the Holon flow on holon-agentic-coder.
