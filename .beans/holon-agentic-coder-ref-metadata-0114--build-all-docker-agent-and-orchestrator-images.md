---
# holon-agentic-coder-ref-metadata-0114
title: "Build all Docker agent and orchestrator images using Buildx Bake"
status: completed
type: task
priority: high
tags:
  - docker
  - buildx
  - bake
  - images
  - agents
created_at: 2026-10-17T05:33:00Z
updated_at: 2026-10-17T05:33:00Z
---

## Summary

Build and load all Docker container images for the Holon agentic environments (`holon/base`, `holon/orchestrator`,
`holon/agent-antigravity`, `holon/agent-claude`, `holon/agent-codex`, `holon/agent-gemini`, `holon/agent-opencode`,
`holon/agent-pi`, and `holon-coherence`) into the local Docker daemon using `apps/sandbox-executor/build_all_images.sh`
and `docker-bake.hcl`.

## Context & Motivation

- Currently, the local container images for agent execution (e.g. `holon/agent-antigravity`) were built on **26
  September 2026**.
- Since then, substantial enhancements have been merged into `holon-agentic-coder`:
  - Granular action logging
    ([Bean 0077](holon-agentic-coder-ref-metadata-0077--append-every-action-to-execution-ledger.md)).
  - Always-enabled action logging
    ([Bean 0113](holon-agentic-coder-ref-metadata-0113--append-execution-and-pr-review-loop-actions-to-executions-ledger.md)).
  - Upgraded session directory tmpfs mount paths (`--tmpfs /home/holon/.gemini/antigravity-cli/log` and `cache`).
  - Model resolution updates and CLI argument adjustments.
- Because container images bake the `src/` directory into `/home/holon/src/` at build time, running `holon execute`
  continues executing the stale 26-September image until all images are rebuilt and loaded into the local Docker engine.

## Tasks & Scope

- [x] Execute `apps/sandbox-executor/build_all_images.sh` (or
      `docker buildx bake -f apps/sandbox-executor/docker-bake.hcl --load`).
- [x] Build all targets defined in `docker-bake.hcl`:
  - `holon/base`
  - `holon/agent-antigravity`
  - `holon/agent-claude`
  - `holon/agent-codex`
  - `holon/agent-gemini`
  - `holon/agent-opencode`
  - `holon/agent-pi`
  - `holon/orchestrator`
- [x] Verify image creation timestamps via `docker images` and `docker inspect`.
- [x] Perform container smoke checks:
  - Verify `python3 -m sandbox_executor.entrypoint.executor --help` or version check succeeds inside each built image.
  - Verify that `is_action_logging_enabled` and `ActionRecord` are importable from `/home/holon/src/sandbox_executor`.
- [x] Document build times and cache considerations in `apps/sandbox-executor/docs/docker_bake.md`.

## Resolution

Delivered via 5-stage Holon flow in [PR #80](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/80):

- Intent: `I-1792215929-update-docker-agent-images-and-build-bake/_`
- Plan: `P-1792216015-antigravity-agent-gemini-3.8-flash-medium`
- Execution: `E-1792216251-antigravity-agent-gemini-3.8-flash-medium`
- Stage 4 PR Review Loop: Approved unanimously (3/3 ensemble consensus).
- Stage 5 Calibration: Pre-merge calibration report committed and merged into PR diff.
