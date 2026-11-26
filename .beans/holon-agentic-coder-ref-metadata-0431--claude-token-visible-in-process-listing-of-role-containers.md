---
# holon-agentic-coder-ref-metadata-0431
title: "The Claude token is visible in the process listing of a role container"
status: completed
type: bug
priority: high
tags:
  - security
  - credentials
  - sandbox
  - holon-agentic-coder
created_at: 2026-11-24T15:55:00Z
updated_at: 2026-11-26T12:10:00Z
---

## Problem

On 2026-11-24 at about 15:49Z a read-only diagnosis of a running resolver container (image `holon/agent-claude`, flow of
Bean 0405) ran `docker top <container>` and saw the Claude OAuth token in the output. The token was not copied or
repeated. A value that appears in `docker top` is on a process command line or otherwise readable from the process
table, so anyone who can run `docker top` or `ps` on the host, and any process inside the container, can read it.

Pull request #271 (Bean 0225) moved the token out of the plaintext file into the OS keychain on the host. This is the
next leak in the chain: the token is handed to the container in a way that puts it in a process listing.

## To establish first

- Which process shows it, and whether it is in the arguments or the environment as rendered by `docker top`: the
  `docker run` client on the host (the engine passes an `--env-file`, which should keep it off the host command line),
  the role dispatcher, or the `claude` process and its children inside the container. The harness wrapper builds
  `HOLON_AGENT_SETTINGS` as a JSON string that carries the token; check whether any entrypoint passes that string, or
  the token, as a command-line argument (for example `claude --settings '<json>'`).
- Whether the same holds for the other runners' credentials.

## Goal

- The token never appears in any process's arguments, on the host or in the container. It reaches `claude` through the
  environment or a file readable only by the agent user (mode 600, on a tmpfs), never through `argv`.
- A test starts a role with a fake token and asserts the token is absent from the argument vectors of every process it
  spawns.
- The echo-padding workaround that keeps the token out of truncated logs is reviewed at the same time: if the token no
  longer travels inside a settings string, the padding may no longer be needed.

## Notes

- Found by the diagnosis subagent for Bean 0430 (resolver turn with no budget); reported, not exploited.
- Until fixed: avoid pasting `docker top` or `ps` output of role containers into logs, beans or reports.
- Related: Bean 0225 (token in the OS keychain, completed), Bean 0406 (wrapper reads the keychain).

## Flow

In progress 2026-11-26: flow settings-token-off-argv (claude-agent, claude-opus-5-5) moves inline settings JSON carrying
the token into a private temp file so it leaves argv. Same defect as 0471.

PR #338 open 2026-11-26: 3/3 approved (4 iterations), calibrated, MERGEABLE/CLEAN, 11 checks green; awaiting maintainer
merge. Rotate the exposed token after merge.

## Resolution

Delivered via [PR #338](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/338) and merged into `main`
(`5440e923`), the same fix as bean 0471: the claude runner passes the settings file path, never the token-bearing JSON,
on the command line.

- **Echo padding**: reviewed and kept as is by the PR (the settings content keeps its padding entry).
- **Scope note**: `preflight.py`, `preflight_secret_args.py` and `test_preflight.py` were changed outside the intent
  scope.
- **ACTION FOR THE MAINTAINER**: rotate the Claude OAuth token now that the fix is merged; the exposure observed on
  2026-11-24 and 2026-11-26 is not closed until it is rotated.
