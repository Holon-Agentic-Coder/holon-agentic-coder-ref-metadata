---
# holon-agentic-coder-ref-metadata-0224
title: "Claude runner maps HOLON_AGENT_KEY by credential type: OAuth tokens become CLAUDE_CODE_OAUTH_TOKEN"
status: todo
type: bug
priority: high
tags:
  - agent-runner
  - claude
  - credentials
  - holon-agentic-coder
created_at: 2026-11-04T01:30:00Z
updated_at: 2026-11-04T01:30:00Z
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

## Scope

- In the claude runner, inspect the `HOLON_AGENT_KEY` value's format: `sk-ant-oat…` is exported into the container as
  `CLAUDE_CODE_OAUTH_TOKEN`; any other value keeps the existing `ANTHROPIC_API_KEY` mapping. Never log or echo the value
  either way.
- The pre-flight probe and its NOT_LOGGED_IN hint name both credential types and which env route each takes; the hint no
  longer recommends a route that rejects subscription tokens.
- Update `docs/executor/agent_credentials_requirements.md` accordingly; the `HOLON_AGENT_SETTINGS` tunnel keeps working
  (settings may carry other configuration) but is no longer required for authentication.
- Tests (pytest only; no real Docker, gh, git remotes or LLM calls): oat-prefixed key maps to `CLAUDE_CODE_OAUTH_TOKEN`;
  api-prefixed key maps to `ANTHROPIC_API_KEY`; neither value appears in any echoed command or log; the pre-flight hint
  text covers both routes.

## Notes

- Found 2026-11-04 during the Bean 0221b end-to-end flow test: pre-flight NOT_LOGGED_IN sent the maintainer to the
  `HOLON_AGENT_KEY` route, which rejects the subscription token.
- Run through the Holon flow on holon-agentic-coder. Touches `agent_runner.py` and preflight code; sequence with other
  runner-touching beans. Related: 0223 (flag/env audit; this is its "secret in the wrong channel" case), the
  `HOLON_AGENT_OAUTH_TOKEN` follow-up candidate noted in Bean 0143.
