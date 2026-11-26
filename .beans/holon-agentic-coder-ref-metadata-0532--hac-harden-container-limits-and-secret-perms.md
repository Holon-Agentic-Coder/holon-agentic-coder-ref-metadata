---
# holon-agentic-coder-ref-metadata-0532
title: "Add Docker resource limits, read-only intent mount, 0o600 secret permissions, and Dockerfile pinning"
status: todo
type: task
priority: high
tags:
  - holon-agentic-coder
  - security
  - docker
  - secrets
created_at: 2026-11-26T13:35:00Z
updated_at: 2026-11-26T13:35:00Z
---

## Problem

While `.git` worktree host-hardening is strong, spawned role containers lack resource limits (`--memory`, `--cpus`,
`--pids-limit`), mount `/tmp/intent.json` writable, rely on `--add-host` for metadata IP blocking (which does not stop
direct IP requests), unpack secret bundles with process umask instead of `0o600`, write `local_llm` configs with
`0o777`/`0o644`, omit `--` terminators in `git.py`, and pipe an unpinned `install.sh` to `bash` in `Dockerfile`.

## Evidence

- Role container `docker run` assembly omits `--memory`, `--cpus`, `--pids-limit`, and `--read-only`.
- `apps/sandbox-executor/src/sandbox_executor/launcher/mounts.py:14-19`: `--add-host 169.254.169.254:127.0.0.1` only
  overrides hostname lookup, not direct IP HTTP requests to link-local metadata endpoints.
- `launcher/containers.py:194`: mounts `/tmp/intent.json` read-write inside the container.
- `local_llm.py:54-55,626-638`: sets `0o777` directory and `0o644` `models.json` permissions.
- `agent_runner.py:348-354`: unpacks secret bundles under default umask rather than `0o600` and logs unredacted
  exception errors.
- `git.py:105-200`: omits `--` option/path terminators before user/branch/path arguments.
- `Dockerfile:93`: pipes unpinned, unverified `install.sh` directly to `bash`.

## Proposed Change

1. Configure default Docker `--memory`, `--cpus`, and `--pids-limit` flags (and `--read-only` rootfs with scoped tmpfs
   where compatible), and change `/tmp/intent.json` mount to `:ro`.
2. Enforce `0o700`/`0o600` permissions on unpacked secret bundles and `local_llm.py` config files, and pass error
   messages around secret handling through `redaction.py`.
3. Add `--` terminators in `git.py` subprocess calls, implement/enforce network-level metadata CIDR
   (`169.254.169.254/32`) blocking where Docker network rules allow, and pin + SHA256-verify the installer script in
   `Dockerfile`.

## Acceptance Criteria

- Container launch tests assert `--memory`, `--cpus`, `--pids-limit`, and `/tmp/intent.json:ro` in generated Docker
  args.
- Unpacked secret files and `local_llm` configs are created with `0o600`/`0o700` and failures never emit unredacted
  secrets.
- `Dockerfile` verifies a pinned version and SHA256 checksum rather than piping unverified remote `install.sh`.

## Notes

- Target repository: `holon-agentic-coder` (evaluated at `HEAD f1e18bcd`).
- Source: 2026-11 ecosystem architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
