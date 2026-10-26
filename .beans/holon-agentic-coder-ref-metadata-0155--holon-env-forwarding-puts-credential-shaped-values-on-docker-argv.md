---
# holon-agentic-coder-ref-metadata-0155
title: "General HOLON_* env forwarding puts credential-shaped non-URL values on the docker argv"
status: todo
type: bug
priority: high
tags:
  - security
  - redaction
  - holon-agentic-coder
created_at: 2026-10-25T12:06:22Z
updated_at: 2026-10-25T12:06:22Z
---

## Problem

Found by the PR #94 iteration-18 resolver on 2026-10-25. The behaviour is already on `main` and is not caused by #94.

The general `HOLON_*` forwarding loop in `sandbox_executor/cli.py` (around line 1335) passes accepted non-URL `HOLON_*`
settings to the container as `-e NAME=value` on the docker command line. It also prints them in the `Executing:` echo.
#96 routes URL values that carry userinfo, and known secret variables, through the 0600 env-file. A credential-shaped
value in any other forwarded setting still reaches the host argv and the echo, where `ps` on the host and the logs can
see it. Example: a budget variable that ignores the bad value and falls back to its default, but is still forwarded.

## Scope

- Decide the rule:
  - **Default:** forward every `HOLON_*` value through the 0600 env-file, so none reach the argv.
  - **Narrower alternative:** run the canonical `redact_agent_secrets` classifier on every forwarded value and send
    anything credential-shaped through the env-file.
- Apply it to the main run and the pre-flight probe.
- Keep the `Executing:` echo masked.
- Tests: run the URL/message fuzz matrix values through every forwarded `HOLON_*` name, and assert neither argv (main
  run or probe) nor the echo contains a fragment of the value.

## Notes

- Run through the Holon flow on holon-agentic-coder.
- Related: Bean 0148 (redaction gaps in ledger `error_context`).
