---
# holon-agentic-coder-ref-metadata-0471
title: "Resolver container argv carries the Claude OAuth token, visible to every local user via ps and docker top"
status: completed
type: bug
priority: high
tags:
  - security
  - flow
  - stage-4
  - claude-agent
created_at: 2026-11-25T23:35:26Z
updated_at: 2026-11-26T12:10:00Z
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

## Flow

In progress 2026-11-26: flow settings-token-off-argv (claude-agent, claude-opus-5-5) moves inline settings JSON carrying
the token into a private temp file so it leaves argv.

PR #338 open 2026-11-26: 3/3 approved (4 iterations), calibrated, MERGEABLE/CLEAN, 11 checks green; awaiting maintainer
merge. Rotate the exposed token after merge.

## Resolution

Delivered via [PR #338](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/338) and merged into `main`
(`5440e923`):

- **Key Architectural Deliverables**: `attribution_off_settings` (`agent_attribution.py`) and the claude runner
  (`agent_runner.py`) write any settings with a non-empty `env` block, inline or from file, to a private mode-600 temp
  file (`mkstemp`, removed at exit). `--settings` now receives a path, so `CLAUDE_CODE_OAUTH_TOKEN` is in no process
  argument vector.
- **Verification & Tests**: `tests/test_agent_attribution.py`, `tests/test_agent_runner.py` assert the fake token is
  absent from every argv element and that the file is mode 600 with the merged settings.
- **Holon Flow Traversal**: flow `settings-token-off-argv` completed all 5 stages (review 3/3 approved).
- **Scope note**: the flow also changed `preflight.py`, `preflight_secret_args.py` and `test_preflight.py`, outside its
  intent scope (same pattern as beans 0502 and 0508).
- **ACTION FOR THE MAINTAINER**: rotate the Claude OAuth token now that the fix is merged. The token seen in
  `docker top` output on 2026-11-26 must be treated as exposed until rotated.
