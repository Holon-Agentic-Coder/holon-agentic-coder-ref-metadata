---
# holon-agentic-coder-ref-metadata-0112
title: "Update container images to latest agent runner versions and dependencies"
status: completed
type: task
priority: high
tags:
  - docker
  - images
  - agents
  - antigravity
  - claude
  - codex
  - pi
created_at: 2026-10-17T04:31:30Z
updated_at: 2026-10-17T04:31:30Z
---

Update and rebuild the Docker container images for all agent runners in `holon-agentic-coder` to incorporate the latest
agent CLI versions, model configurations, and runtime dependencies.

## Context

- The sandboxed agent runner images (`holon/agent-antigravity`, `holon/agent-claude`, `holon/agent-codex`,
  `holon/agent-pi`, `holon/orchestrator`) package specific versions of external agent binaries and dependencies.
- Recent changes to agent CLIs (e.g. Antigravity 2.0 flags, effort parameters, model identifier mappings, Playwright
  browser drivers, Codex trusted directory requirements) have caused runtime failures during container execution.
- In addition, session directory mounts (`~/.gemini/antigravity-cli`, `~/.codex`) require writable tmpfs overlays for
  internal logging and caching when running under hardened read-only (`:ro`) container session policies.

## Tasks

- [x] Audit Dockerfile in `apps/sandbox-executor/Dockerfile`:
  - `holon/base`
  - `holon/orchestrator`
  - `holon/agent-antigravity`
  - `holon/agent-claude`
  - `holon/agent-codex`
  - `holon/agent-pi`
  - `holon/agent-gemini`
  - `holon/agent-opencode`
- [x] Upgrade agent CLI packages (`@anthropic-ai/claude-code@2.1.302`, `@openai/codex@0.163.0`,
      `@google/gemini-cli@0.64.0`, `opencode-ai@1.19.3`, `@earendil-works/pi-coding-agent@1.3.0`) to latest stable
      releases.
- [x] Ensure non-interactive execution flags, model resolution overrides, and browser drivers are correctly configured.
- [x] Update `sandbox_executor/cli.py` container mounts to provide writable tmpfs for agent log and cache directories
      (`--tmpfs /home/holon/.gemini/antigravity-cli/log:uid=1000,gid=1000`,
      `--tmpfs /home/holon/.gemini/antigravity-cli/cache:uid=1000,gid=1000`,
      `--tmpfs /home/holon/.codex/log:uid=1000,gid=1000`, `--tmpfs /home/holon/.codex/cache:uid=1000,gid=1000`) while
      preserving credential isolation.
- [x] Build and verify images locally with `make build-all-images` / `build_all_images.sh`.
- [x] Test end-to-end plan and execute runs with updated images across supported agent runners.

## Resolution

Delivered via 5-stage Holon flow in [PR #80](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/80):

- Intent: `I-1792215929-update-docker-agent-images-and-build-bake/_`
- Plan: `P-1792216015-antigravity-agent-gemini-3.8-flash-medium`
- Execution: `E-1792216251-antigravity-agent-gemini-3.8-flash-medium`
- Stage 4 PR Review Loop: Approved unanimously (3/3 ensemble consensus).
- Stage 5 Calibration: Pre-merge calibration report committed and merged into PR diff.
