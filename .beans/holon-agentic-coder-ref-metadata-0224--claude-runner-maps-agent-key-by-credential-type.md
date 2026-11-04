---
# holon-agentic-coder-ref-metadata-0224
title:
  "Claude credentials just work: auto-discover ~/.holon/secrets/claude-oauth-token and map HOLON_AGENT_KEY by credential
  type"
status: todo
type: bug
priority: high
tags:
  - agent-runner
  - claude
  - credentials
  - holon-agentic-coder
created_at: 2026-11-04T01:30:00Z
updated_at: 2026-11-04T02:20:00Z
---

## Problem

`HOLON_AGENT_KEY` is the generic credential channel, and for the claude runner `_apply_generic_token` maps it to
`ANTHROPIC_API_KEY` unconditionally. But Claude accepts two credential types with distinct, detectable formats:

- a real Anthropic API key (`sk-ant-api…`) — correct as `ANTHROPIC_API_KEY`;
- a Claude Code subscription OAuth token from `claude setup-token` (`sk-ant-oat…`) — rejected as `ANTHROPIC_API_KEY`
  ("Invalid API key"); it only works as `CLAUDE_CODE_OAUTH_TOKEN`.

So an operator with a subscription token cannot use the documented credential channel at all. The working route today is
a workaround: tunnelling `CLAUDE_CODE_OAUTH_TOKEN` through the `--settings` JSON via `HOLON_AGENT_SETTINGS`, padded so
command echoes cannot truncate into the secret. The pre-flight failure hint compounds it by recommending
`HOLON_AGENT_KEY` first — the route that cannot work for a subscription token.

## Decision (maintainer, 2026-11-04)

The operator should not have to assemble any env blob at all. Holon already auto-discovers GitHub credentials and host
SSH agent sockets and mounts them safely into containers; the Claude credential gets the same treatment: read it from
the secrets file directly.

## Scope

- **Auto-discovery (the primary route)**: when the claude runner needs a credential and no explicit one is set, read
  `~/.holon/secrets/claude-oauth-token` (trimmed; 0600 expected, warn on looser permissions) and inject it into the
  container by its detected type, exactly as the GitHub credential discovery already behaves. Precedence: explicit
  `HOLON_AGENT_KEY` > secrets file > fail pre-flight with a hint naming the file path and `claude setup-token`.
- **Consume-once (maintainer, 2026-11-04)**: the secrets file is NOT persistent. Pre-flight reads it, validates the
  credential with the probe, holds it in process memory for the whole run, and **removes the file immediately after the
  successful read** — deletion is part of the pre-flight step itself. Consequences the implementation must honour: every
  stage of that run reuses the in-memory credential (never re-reads the file, which is gone); a later `--from-stage` /
  `--checkpoint` resume in a new process needs the file re-provisioned (or an explicit `HOLON_AGENT_KEY`), and the
  pre-flight failure hint says exactly that, naming `claude setup-token`; a failed pre-flight read does not delete the
  file.
- **Type mapping (both routes)**: inspect the credential value's format wherever it came from: `sk-ant-oat…` is exported
  into the container as `CLAUDE_CODE_OAUTH_TOKEN`; any other value keeps the existing `ANTHROPIC_API_KEY` mapping. Never
  log or echo the value either way; the token travels as a container env value, never on an echoed command line, so the
  echo pad becomes unnecessary for authentication (keep redaction tests proving it).
- The pre-flight probe and its NOT_LOGGED_IN hint name the secrets-file path first, then both env routes and which
  credential type each takes; the hint no longer recommends a route that rejects subscription tokens.
- Update `docs/executor/agent_credentials_requirements.md` accordingly; the `HOLON_AGENT_SETTINGS` tunnel keeps working
  (settings may carry other configuration) but is no longer required for authentication.
- Tests (pytest only; no real Docker, gh, git remotes or LLM calls): the file is removed after a successful pre-flight
  read and kept on a failed one; a resume with neither file nor explicit key fails with the re-provision hint;
  auto-discovery reads the file when no explicit key is set; explicit `HOLON_AGENT_KEY` wins over the file; a missing or
  empty file fails pre-flight with the file-path hint; oat-prefixed values map to `CLAUDE_CODE_OAUTH_TOKEN`;
  api-prefixed values map to `ANTHROPIC_API_KEY`; neither value appears in any echoed command or log.

## Notes

- Found 2026-11-04 during the Bean 0221b end-to-end flow test: pre-flight NOT_LOGGED_IN sent the maintainer to the
  `HOLON_AGENT_KEY` route, which rejects the subscription token.
- Run through the Holon flow on holon-agentic-coder. Touches `agent_runner.py` and preflight code; sequence with other
  runner-touching beans. Related: 0223 (flag/env audit; this is its "secret in the wrong channel" case), the
  `HOLON_AGENT_OAUTH_TOKEN` follow-up candidate noted in Bean 0143.
