---
# holon-agentic-coder-ref-metadata-0126
title: "Drop container root capabilities and enforce unprivileged execution in role dispatcher entrypoints"
status: todo
type: task
priority: normal
tags:
  - security
  - sandbox
  - docker
  - audit
parent: holon-agentic-coder-ref-metadata-0122
created_at: 2026-10-19T01:38:00Z
updated_at: 2026-10-19T01:38:00Z
---

Audit Docker container entrypoint invocations and role dispatchers to enforce least privilege, dropping unnecessary
Linux capabilities.

## Context

Audit finding `AUD-2026-04`: While container execution drops `NET_RAW` and runs as non-root user `holon`, container
security can be fortified by setting `--cap-drop=ALL` (or strict minimum whitelist) and
`--security-opt=no-new-privileges` across all agent dispatcher runners.

## Tasks

- [ ] Audit `role_dispatcher.sh` and Docker run parameter construction in `sandbox_executor`.
- [ ] Add `--cap-drop=ALL` with explicit minimal capability whitelisting as required.
- [ ] Verify role agent execution survival under restricted capability profiles.
