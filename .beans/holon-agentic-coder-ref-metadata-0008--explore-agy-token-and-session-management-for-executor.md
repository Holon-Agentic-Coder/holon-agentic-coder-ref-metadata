---
# holon-agentic-coder-ref-metadata-0008
title: Explore universal agent token and session token standardization for sandbox execution
status: done
type: task
priority: high
created_at: 2026-07-25T22:27:00Z
updated_at: 2026-07-25T22:34:00Z
---

## Overview

When building the execution phase for `holon-agentic-coder-ref`, running agent CLIs (`agy`, `claude`, `pi`, `codex`,
`gemini`, `opencode`) inside containerized Docker sandboxes requires valid authentication credentials (API keys, user
tokens, or session tokens).

Vendor-specific authentication mechanisms (such as GCP Service Accounts or GCP ADC) are not universal solutions because
non-Google agents (`claude`, `pi`, `open-codex`, `opencode`) do not support them.

This task tracks the intent creation, planning, and evaluation of vendor-neutral, cloud-agnostic standardization options
for injecting and managing user/session tokens across ALL supported agents in the sandbox executor.

## Multi-Agent Authentication Taxonomy

Supported agents fall into two primary credential categories:

1. **Stateless API Keys / Bearer Tokens**: (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, `PI_API_KEY`,
   `AGY_USER_TOKEN`)
2. **Stateful Session / OAuth Profiles**: (`~/.gemini/antigravity-cli`, `~/.config/claude`, `~/.config/pi`, `~/.codex`)

## Standardized Authentication Options Analyzed

### Option 1: Universal Standardized Environment Variable Mapping (Recommended for Stateless Keys)

- **Mechanism**: Define a standardized environment contract (`HOLON_AGENT_API_KEY`, `HOLON_AGENT_SESSION_TOKEN`) mapped
  by `agent_runner.py` to agent-specific CLI flags or env vars inside the container.
- **Pros**: Vendor-agnostic, 100% cloud-portable (K8s/Docker/CI), zero filesystem dependencies.
- **Cons**: Stateless API keys do not preserve interactive OAuth session state without token refresh logic.

### Option 2: Ephemeral Secret Bundle Injection (`/run/secrets/holon_auth.json`) (Recommended for Unified Auth)

- **Mechanism**: Orchestrator writes an ephemeral JSON secret bundle containing keys/tokens for the targeted agent to
  `/run/secrets/holon_auth.json` with `0600` permissions. `agent_runner.py` parses the bundle to set up agent
  env/session files.
- **Pros**: Vendor-neutral, prevents secret leakage in process dumps (`env`/`ps`), supports both API keys and session
  tokens cleanly.
- **Cons**: Requires host CLI wrapper to construct and clean up secret bundles.

### Option 3: Read-Only Session Directory Mount Mapping (Recommended for Interactive Local Sessions)

- **Mechanism**: Host orchestrator bind-mounts agent-specific session directories as read-only (`:ro`) into container
  target locations (e.g. `~/.config/claude` -> `/home/holon/.config/claude:ro`).
- **Pros**: Reuses active interactive host logins for any agent without exposing raw secret keys to user inputs.
- **Cons**: OS-specific host path mapping variations; UID/GID permission differences.

### Option 4: Universal Auth Proxy Socket (`HOLON_AUTH_SOCK`) (Long-Term Enterprise Vision)

- **Mechanism**: Forward a host authentication domain socket into the container (similar to SSH Agent forwarding). A
  host daemon signs or injects headers into outgoing API requests.
- **Pros**: Maximum security; raw credentials never enter untrusted container filesystem or memory.
- **Cons**: Highest implementation complexity.

## Standardized Architecture Recommendation

Adopt a **Unified 3-Tier Multi-Agent Fallback Contract**:

1. **Tier 1 (Ephemeral Secret Bundle / Env Contract)**: `/run/secrets/holon_auth.json` or single unified variable
   `HOLON_AGENT_KEY` (with fallback to `HOLON_AGENT_AUTH_TOKEN` / `HOLON_AGENT_API_KEY`). Automatically mapped to agent
   envvars (`AGY_USER_TOKEN` + `GOOGLE_API_KEY` for Antigravity, `ANTHROPIC_API_KEY` for Claude, `OPENAI_API_KEY` for
   Codex).
2. **Tier 2 (Agent-Specific Standard Env Vars)**: Existing `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`,
   `AGY_USER_TOKEN`.
3. **Tier 3 (Read-Only Session Directory Mounts)**: `:ro` bind-mount of host config dirs (`~/.config/claude`,
   `~/.gemini/antigravity-cli`, `~/.codex`).

## Resolution

Explored and agreed upon a cloud-agnostic, vendor-neutral 3-Tier Fallback Architecture for agent authentication across
all supported agent runners (`agy`, `claude`, `pi`, `codex`, `gemini`, `opencode`). Documented the detailed
specification in
[.beans/holon-agentic-coder-ref-metadata-0008--explore-agy-token-and-session-management-for-executor.md](.beans/holon-agentic-coder-ref-metadata-0008--explore-agy-token-and-session-management-for-executor.md)
and [todo/agy_token_execution_plan.md](todo/agy_token_execution_plan.md).
