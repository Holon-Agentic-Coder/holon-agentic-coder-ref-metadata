---
# holon-agentic-coder-ref-metadata-0290
title: "Flow wrapper exports the Claude auth route, or fails loudly when it is missing"
status: completed
type: bug
priority: high
tags:
  - flow
  - harness
  - claude-agent
created_at: 2026-11-12T22:00:00Z
updated_at: 2026-11-12T22:00:00Z
---

## Problem

`scripts/run_holon_flow.py` (the `holon-flow` skill's runner) does not set the Claude auth route, and a shell that lacks
`HOLON_AGENT_SETTINGS` (token plus echo padding) gives the `claude-agent` containers no credentials. On 2026-11-12 a
resumed Stage 4 for the `ids` flow (PR #169) failed twice in about 15 seconds: all three reviewers exited with code 1
and the log said only `stop reason: unknown`. The host token and the `holon/agent-claude` image were both fine; the runs
launched from an agent shell simply had no `HOLON_*` variables. Relaunching with `HOLON_AGENT_SETTINGS` set fixed it.
Each failure also burns a review iteration number (iteration 5 and 6 were consumed).

## Goal

1. For `--agent claude-agent`, the wrapper builds `HOLON_AGENT_SETTINGS` itself from the OAuth token secrets file
   (padded past the planner and executor echo truncation) and sets `HOLON_TOKEN_REDUCE=0`, never printing or logging the
   token.
2. When no route is available (no env and no secrets file), the wrapper exits before dispatch with a message naming what
   is missing.
3. A hermetic test covers both paths with a fake secrets file; the token never appears in test output.
4. Update the `holon-flow` skill to state the route is built in.

## Notes

- Harness change (control plane only); directly editable.
- Related: the Claude OAuth route reference; Bean 0291 makes the reviewer failure visible.

## Resolution (completed, 2026-11-13)

Done directly in the harness (the control plane is not a Holon flow target), uncommitted for review.
`.agents/skills/holon_flow/scripts/flow_env.py` builds the child environment: for `claude-agent` it reads the token from
`CLAUDE_CODE_OAUTH_TOKEN` or `~/.holon/secrets/claude-oauth-token`, builds `HOLON_AGENT_SETTINGS` with the echo pad, and
sets `HOLON_TOKEN_REDUCE=0` and `PYTHONUNBUFFERED=1`; an existing `HOLON_AGENT_SETTINGS` is kept; missing credentials
raise an error naming what is missing, and `run_holon_flow.py` stops before dispatch. The environment is passed to the
child process, so the token is never printed. Seven tests in `tests/test_flow_env.py` use a fake secrets directory. The
`holon-flow` skill documents it.
