---
# holon-agentic-coder-ref-metadata-0095
title: "Agent runner session state and credential isolation"
status: completed
type: task
priority: high
tags:
  - security
  - credentials
  - session
  - dbus
created_at: 2026-10-14T13:40:00Z
updated_at: 2026-10-15T15:38:00Z
---

# Bean 0095: Agent Runner Session State and Credential Isolation

- **Bean ID:** 0095
- **Title:** Agent Runner Session State and Credential Isolation
- **Status:** completed
- **Priority:** high
- **Category:** security
- **Components:** `apps/sandbox-executor/cli.py`, `apps/sandbox-executor/agent_runner.py`
- **Created At:** 2026-10-14
- **Parent Audit Finding:** SEC-02

---

## 1. Context & Motivation

To allow sandboxed agent CLIs (such as `antigravity-agent`, `claude-code`, `gemini-cli`, `pi-coding-agent`, and `codex`)
to execute without requiring interactive user authentication inside containers,
`apps/sandbox-executor/src/sandbox_executor/cli.py` mounts host session directories (e.g. `~/.gemini/antigravity-cli`,
`~/.config/claude`, `~/.codex`) into the sandbox container.

During the security audit (Finding SEC-02 in `docs/audit_report.md`), two isolation risks were identified:

1. On Linux hosts, the user's raw D-Bus session socket (`/run/user/<uid>/bus`) is automatically mounted into the
   container if present.
2. Mounted session directories can contain persistent host tokens, cached credentials, and broad write permissions.

---

## 2. Problem Statement

1. **D-Bus Escape Vector:** Mounting the host D-Bus socket grants sandboxed processes the ability to communicate with
   host desktop daemons, systemd user services, and system secret managers (such as GNOME Keyring / FreeDesktop Secret
   Service), circumventing container isolation tiers (`holon-config/world/constraints.md` §2).
2. **Session Pollution:** If a containerized agent writes corrupted state or rogue plugins into mounted host
   directories, the host developer environment may be impacted.

---

## 3. Proposed Remediation

1. **Eliminate D-Bus Socket Mounting:** Remove `/run/user/<uid>/bus` mounting from `get_agent_session_mounts()`. If an
   agent requires a bus endpoint for headless keytar operations, run an isolated, ephemeral `dbus-daemon --session`
   inside the container entrypoint.
2. **Ephemeral Read-Only Session Copies:** Rather than bind-mounting host directories directly as read-write, copy
   required session tokens into an ephemeral sandbox directory or tmpfs mount with strict read-only permissions for
   public files and private permissions (`0600`) for token files.
3. **Dedicated Post-Run Scrubbing:** Ensure all ephemeral tokens and credentials written to `/tmp` or `/run/secrets` are
   securely shredded upon container exit.

---

## 4. Acceptance Criteria

- [x] No host `/run/user/*/bus` socket paths are mounted into container run commands.
- [x] Sandboxed agent runners continue to authenticate successfully using mapped environment variables
      (`HOLON_AGENT_KEY`, `AGY_USER_TOKEN`, `ANTHROPIC_API_KEY`) and read-only credential mounts.
- [x] Containerized execution cannot mutate host session directories.

---

## 5. Verification Commands

```bash
# Verify session mount generation does not include dbus socket
uv run pytest apps/sandbox-executor/tests/test_cli.py -k "session"

# Verify linting and formatting
uv run ruff check .
npx prettier --check .beans/holon-agentic-coder-ref-metadata-0095--agent-runner-session-state-and-credential-isolation.md
```

---

## 6. Resolution

- Removed host `/run/user/<uid>/bus` D-Bus socket mounting from `get_agent_session_mounts()` in
  `apps/sandbox-executor/src/sandbox_executor/cli.py`.
- Enforced read-only (`:ro`) session mounts to eliminate host state mutation from container processes.
- Implemented `cleanup_ephemeral_credentials()` on `StandardAgentRunner` and wired it into `atexit` handlers and
  container execution `finally` blocks in `cli.py`, `planner.py`, and `executor.py`.
- Added unit tests in `test_cli.py` and `test_agent_runner.py`.
- Validated via Holon flow lifecycle stages 1-5; PR #77 achieved 3/3 unanimous ensemble consensus approval, 10/10 green
  CI checks, and pre-merge calibration ($\Delta EV$ +4.30); merged to `main` at commit
  `29aa1c14d060c4b90657803f046c964c6beb54e3`.
