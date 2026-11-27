---
# holon-agentic-coder-ref-metadata-0532
title: "Add Docker resource limits, read-only intent mount, 0o600 secret permissions, and Dockerfile pinning"
status: in-progress
type: task
priority: high
tags:
  - holon-agentic-coder
  - security
  - docker
  - secrets
created_at: 2026-11-26T13:35:00Z
updated_at: 2026-11-27T01:17:18Z
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

## Flow (2026-11-27)

flow slug secret-bundle-private-files (claude-agent, claude-opus-5-5) covers only the secret bundle part of item 2
(0o600 files, 0o700 directories, redacted warning in agent_runner.py). Left open: container resource limits and
read-only intent mount (touch launcher/containers.py, parked with 0390), local_llm modes (the container user needs
them), git.py terminators (tests assert exact git args), Dockerfile pin (needs a vendor checksum).

parked 2026-11-27: Stage 4 halted before push (pre-push tests test_flow_repo_templates history and
test_executor_run_salvage fail on the review-loop identity leak); PR #356 open. Resume from checkpoint (--checkpoint,
--from-stage review) once the review identity fix merges.

## Flow outcome (2026-11-27)

PR [#356](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/356) merged into `main` (`d3c68686`): secret
bundle files are unpacked owner-only (0o600 files, 0o700 directories) with a redacted warning on failure, in
`agent_runner.py`. This bean stays `in-progress` for the remaining scope:

- container resource limits (`--memory`, `--cpus`, `--pids-limit`), `--read-only` rootfs, and the read-only
  `/tmp/intent.json` mount (touches `launcher/containers.py`; parked with 0390);
- `local_llm` config modes (`0o777`/`0o644`; the container user needs them);
- `git.py` `--` terminators (tests assert exact git args);
- `Dockerfile` installer pin with SHA256 verification (needs a vendor checksum).

Follow-ups:

- (a) The resolver's uncommitted one-line change moving `os.fchmod` inside the `try` was dropped by the review stage;
  tracked in bean 0551 (backup patch in the scratchpad). Decide in a follow-up flow.
- (b) PR #356 added two docstrings to `agent_runner.py` against the self-explaining-code invariant; their removal is
  recorded on bean 0153.

## Flow outcome 2 (2026-11-27, PR #372)

PR [#372](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/372) merged into `main` (`ac01cd10`): the role
container `docker run` mounts the intent file at `/tmp/intent.json:ro` (`launcher/containers.py`), and the pinned
characterisation expectations were updated (`test_container_launch_characterisation.py`,
`test_host_worktree_sandbox.py`). This delivers only the read-only intent mount item of acceptance criterion 1. This
bean stays `in-progress` for the remaining scope: container resource limits (`--memory`, `--cpus`, `--pids-limit`) and
`--read-only` rootfs, `local_llm` modes, `git.py` `--` terminators, and the `Dockerfile` installer pin with SHA256
verification (excluded in `todo/intent-coverage-0532.json`).
