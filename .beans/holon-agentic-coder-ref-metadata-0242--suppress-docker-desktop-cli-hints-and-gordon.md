---
# holon-agentic-coder-ref-metadata-0242
title: "Suppress Docker Desktop CLI hints and Gordon suggestions via DOCKER_CLI_HINTS=false"
status: completed
type: bug
priority: normal
tags:
  - flow
  - docker
  - cli
  - ux
  - holon-agentic-coder
created_at: 2026-11-06T06:01:17Z
updated_at: 2026-11-06T10:10:24Z
completed_at: 2026-11-06T10:10:24Z
---

## Problem

Whenever a Docker container exits with a non-zero exit code (for example, when a test suite or sub-process in the
container reports a failure), Docker Desktop CLI automatically appends promotional and diagnostic hints to `stderr`:

```
What's next:
    Debug this container error with Gordon → docker ai "help me fix this container error"
```

In automated flows and CI/orchestration pipelines, these promotional CLI hints:

1. Pollute logs and stream outputs with interactive Docker Desktop suggestions that are irrelevant to headless agent
   execution.
2. Interfere with clean stdout/stderr log parsing and telemetry capture in `sandbox_executor`.

## Goal

1. **Set `DOCKER_CLI_HINTS=false`**: Ensure that all Docker invocations made by `sandbox_executor` (in `flow.py`,
   `turns.py`, container dispatchers, and shell execution helpers) set `DOCKER_CLI_HINTS=false` in the subprocess
   environment.
2. **Global Engine Environment**: Ensure the `holon` CLI and flow runner propagate `DOCKER_CLI_HINTS=false` to all
   spawned child processes.
3. **Tests**: Add unit tests verifying that subprocess execution commands pass `DOCKER_CLI_HINTS="false"` in their
   environment mapping.

## Resolution

Delivered via 5-stage Holon flow on branch `I-1793955677-suppress-docker-desktop-cli-hints/...` and merged in
[PR #132](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/132)
(`d932d48c936aa2acc8e586179db1fd49cd34bb91`). `DOCKER_CLI_HINTS=false` is exported across CLI entrypoints, runner
environments, container parameters, and subprocess helpers with hermetic unit tests in
`apps/sandbox-executor/tests/test_turns.py`. Passed 3/3 unanimous consensus review and completed Stage 5 calibration
(`plans/P-1793955693-antigravity-agent-gemini-3.8-flash-medium_calibration.md`).
