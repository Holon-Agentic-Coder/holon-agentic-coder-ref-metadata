---
# holon-agentic-coder-ref-metadata-0055
title: Apply comments from PR 21 and fix build
status: completed
type: task
priority: normal
created_at: 2026-07-23T12:34:45Z
updated_at: 2026-09-27T13:05:00Z
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

> [!NOTE] **Status Vocabulary (2026-09-22)** This bean's status was earlier rewritten from `completed` to `done` to
> match a local vocabulary that did not match the `beans` CLI. `done` is not a valid CLI status and is never archived,
> so it reads `completed` again. No change to the recorded outcome.

## ID Normalisation (2026-09-27)

Renamed from the base36 id `7mdd` to the sequential integer id `0055` (by the maintainer) to comply with the strictly
sequential 4-digit rule in `.beans.yml` and `.beans/template.md`. Historical review artefacts in the git-ignored
`.subagent/` directory still mention `7mdd` -- including a note that it was "intentionally left random" -- and are left
untouched as records of what was true when they were written. `0055` also raises the next available id to `0056`.
