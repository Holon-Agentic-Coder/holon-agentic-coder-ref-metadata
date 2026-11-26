---
# holon-agentic-coder-ref-metadata-0471
title: "Resolver container argv carries the Claude OAuth token, visible to every local user via ps and docker top"
status: todo
type: bug
priority: high
tags:
  - security
  - flow
  - stage-4
  - claude-agent
created_at: 2026-11-25T23:35:26Z
updated_at: 2026-11-25T23:35:26Z
---

## Problem

During the Stage 4 resolver turn of `workspace-survival-job-parallel` (claude-agent, claude-opus-5-5), the in-container
`claude` process is started with its settings JSON on the command line (`--settings {"env": {...}}`). That JSON carries
`CLAUDE_CODE_OAUTH_TOKEN` in plain text, so the long-lived OAuth token appears in the argv of the process for the whole
turn. Any local user can read it with `ps` or `docker top <container>`. The token is also echoed into agent tool output
when anyone lists processes, so it must be treated as exposed.

## Fix direction

- Pass the token through the container environment (`docker run -e`, or an env-file that is removed after start), never
  through argv or a settings string on the command line.
- Keep the `HOLON_ECHO_PAD` padding, but do not place the secret in the padded argument.
- Add a test that the review and resolver argv never contain the token value.
- Rotate the exposed token once the fix lands.

## Notes

- Observed 2026-11-26 (local time) by `docker top` on a live resolver container for bean 0405.
- Related: 0432 (resolver turn failures), bean "claude-agent OAuth route" memory note (token via HOLON_AGENT_SETTINGS).
