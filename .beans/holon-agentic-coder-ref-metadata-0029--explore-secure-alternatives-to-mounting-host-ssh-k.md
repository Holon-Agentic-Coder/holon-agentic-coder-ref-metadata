---
# holon-agentic-coder-ref-metadata-0029
title: Explore secure alternatives to mounting host SSH keys in Docker sandbox
status: completed
type: task
priority: normal
created_at: 2026-07-23T11:35:24Z
updated_at: 2026-09-22T13:10:00Z
---

Investigate and implement safer git checkout options in the sandbox executor (e.g., SSH agent forwarding,
repository-specific deploy keys, or GitHub token auth) to replace mounting the host's entire ~/.ssh directory.

## Summary of Changes

- **Token Authentication**: Added support for token-based HTTPS clone/push by checking `GITHUB_TOKEN` and `GH_TOKEN`
  environment variables. When detected, git operations construct an authenticated HTTPS URL.
- **Deploy Key Authentication**: Added support for custom SSH deploy keys using the `HOLON_SSH_KEY_PATH` environment
  variable.
- **SSH Agent Forwarding**: Retained fallback to standard SSH authentication which works out-of-the-box with forwarded
  SSH agents.
- **Unit Tests**: Added four comprehensive unit tests in `apps/sandbox-executor/tests/test_agent_runner.py` verifying
  all authentication options. Passed all 25 tests successfully.

> [!NOTE] **Status Vocabulary (2026-09-22)** This bean's status was earlier rewritten from `completed` to `done` to
> match a local vocabulary that did not match the `beans` CLI. `done` is not a valid CLI status and is never archived,
> so it reads `completed` again. No change to the recorded outcome.
