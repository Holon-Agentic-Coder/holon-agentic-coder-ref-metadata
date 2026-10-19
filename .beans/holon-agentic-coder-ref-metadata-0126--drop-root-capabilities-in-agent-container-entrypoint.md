---
# holon-agentic-coder-ref-metadata-0126
title: "Drop container root capabilities and enforce unprivileged execution in role dispatcher entrypoints"
status: completed
type: task
priority: normal
tags:
  - security
  - sandbox
  - docker
  - audit
parent: holon-agentic-coder-ref-metadata-0122
created_at: 2026-10-19T01:38:00Z
updated_at: 2026-10-19T04:40:00Z
---

Audit Docker container entrypoint invocations and role dispatchers to enforce least privilege, dropping unnecessary
Linux capabilities.

## Context

Audit finding `AUD-2026-04`: While container execution drops `NET_RAW` and runs as non-root user `holon`, container
security can be fortified by setting `--cap-drop=ALL` (or strict minimum whitelist) and
`--security-opt=no-new-privileges` across all agent dispatcher runners.

## Tasks

- [x] Audit `role_dispatcher.sh` and Docker run parameter construction in `sandbox_executor`.
- [x] Add `--cap-drop=ALL` with explicit minimal capability whitelisting as required.
- [x] Verify role agent execution survival under restricted capability profiles.

## Resolution

- Updated `build_network_isolation_args` in `apps/sandbox-executor/src/sandbox_executor/cli.py` to unconditionally pass
  `--cap-drop=ALL` and `--security-opt=no-new-privileges` to all Docker container executions.
- Verified unit test coverage in `apps/sandbox-executor/tests/test_cli.py` (55/55 passed).
- Executed through full 5-stage Holon flow via PR #86:
  https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/86
