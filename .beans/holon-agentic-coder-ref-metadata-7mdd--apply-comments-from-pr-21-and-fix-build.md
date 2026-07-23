---
# holon-agentic-coder-ref-metadata-7mdd
title: Apply comments from PR 21 and fix build
status: completed
type: task
priority: normal
created_at: 2026-07-23T12:34:45Z
updated_at: 2026-07-23T12:40:32Z
---

Go through comments on PR 21, apply the suggestions, and verify build passes.

## Summary of Changes

Applied all reviewer suggestions on PR #21:

- Updated the dockerfile inside `apps/sandbox-executor/Dockerfile` to use `printf` instead of `echo` for portability,
  prepended a newline to ensure proper appending, and added a security note about disabling strict host key checking.
- Updated `get_repo_url()` inside `apps/sandbox-executor/src/sandbox_executor/agent_runner.py` to support overriding via
  the `HOLON_REPO_URL` env var.
- Added a unit test `test_ssh_agent_forwarding_override` in `apps/sandbox-executor/tests/test_agent_runner.py` to verify
  the repo URL override works.
- Patched the default unit test `test_ssh_agent_forwarding_default` to mock `os.environ` to prevent test flakiness from
  `HOLON_REPO_URL` env var pollution.
- Clarified SSH key preconditions and empty `SSH_AUTH_SOCK` handling for Linux in `docs/sandbox/create_intent.md`,
  `docs/sandbox/create_plan.md`, and `intents/README.md`.
- Ran unit tests and formatters/linters, and verified all checks pass successfully.
