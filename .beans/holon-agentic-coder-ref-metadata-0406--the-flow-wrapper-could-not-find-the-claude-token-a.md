---
# holon-agentic-coder-ref-metadata-0406
title: "The flow wrapper could not find the Claude token after it moved to the OS keychain"
status: completed
type: bug
priority: high
tags:
  - harness
  - flow
  - credentials
created_at: 2026-11-24T10:05:00Z
updated_at: 2026-11-24T10:05:00Z
---

## Problem

Pull request #271 (Bean 0225) merged at 09:55Z on 2026-11-24. The post-merge install migrated the Claude OAuth token
from `~/.holon/secrets/claude-oauth-token` into the OS keychain (service `holon`, account `claude-oauth-token`) and
deleted the file at 09:56Z.

The harness wrapper's `.agents/skills/holon_flow/scripts/flow_env.py` read only `CLAUDE_CODE_OAUTH_TOKEN` or that file,
so every new `claude-agent` flow launch stopped with "claude-agent needs credentials, but none were found". The flows of
Beans 0197, 0216 and 0403 stopped within three minutes of the move. Wrappers already running kept working because they
held the token in their environment.

## Resolution

- `flow_env.py` now looks in the environment, then the legacy file, then the OS secret store
  (`security find-generic-password` on macOS, `secret-tool lookup` on Linux). It never prints the token, and its error
  message names the keychain entry.
- Four tests added in `tests/test_flow_env.py`, with an autouse fixture so no test reads the real store.
- `uv run pytest tests/test_flow_env.py` passes (22 tests).
- Verified with a real lookup that a token is found.

## Notes

- Uncommitted on the harness branch `docs/harness-20261123`.
- Lesson: a target-repo change that moves where a secret lives needs the harness wrapper changed in the same step.
