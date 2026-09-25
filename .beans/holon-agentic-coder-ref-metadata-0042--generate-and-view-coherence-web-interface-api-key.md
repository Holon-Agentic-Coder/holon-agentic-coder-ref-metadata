---
# holon-agentic-coder-ref-metadata-0042
title: "Generate and view holon-coherence web interface API key and password"
status: todo
type: task
priority: normal
tags:
  - cli
  - holon-coherence
  - security
  - web-ui
created_at: 2026-09-26T09:24:00Z
updated_at: 2026-09-26T15:20:00Z
---

Add support for generating, configuring, and viewing the API key / password for the `holon-coherence` web interface
(`mitmweb` dashboard).

## Context

When running `holon-coherence start --web`, the underlying `mitmweb` server automatically protects its dashboard and
REST API with authentication. By default, if no password is provided, `mitmweb` generates an ephemeral random token on
startup. In detached Docker mode (`-d`), this token is buried in container logs and unknown to the user, causing browser
access at `http://127.0.0.1:8081` to fail or block at a password prompt.

Users need an explicit, seamless mechanism to specify, auto-generate, and inspect the web interface API key / token.

## Acceptance Criteria

1. **Configuration Support**:
   - Add CLI option `--web-password <password>` to `holon-coherence start`.
   - Support environment variable `HOLON_COHERENCE_WEB_PASSWORD` as a fallback.
   - If no password is provided, auto-generate a secure random token (e.g. via `secrets.token_urlsafe(16)`).
   - Persist the active token to `~/.holon/web-token` with restricted file permissions (`0600`).
2. **Container Passthrough**:
   - Ensure the password is passed to the containerized `mitmweb` process via `--set web_password=<password>` (or
     environment variable inside the container).
3. **Display & Inspection**:
   - On `holon-coherence start --web`, print the dashboard URL along with the authentication credentials:
     ```text
     🌐 Web dashboard exposed at http://127.0.0.1:8081/?token=<token>
     🔑 Web API Key / Password: <token>
     ```
   - Update `holon-coherence status` to display the web dashboard URL and active API key / token when the web interface
     is enabled.
   - Provide a dedicated helper command `holon-coherence web-key` (or `holon-coherence web-token`) to print the active
     dashboard URL and token from `~/.holon/web-token`.
4. **Documentation & Verification**:
   - Update `apps/holon-coherence/README.md` with instructions on accessing the web dashboard, setting custom passwords,
     and inspecting the generated API key.
   - Add unit tests in `apps/holon-coherence/tests/test_cli.py` covering token generation, file persistence, CLI
     display, and Docker argument forwarding.

## Notes

- Target repository: `apps/holon-coherence/`
- Target files:
  - `src/holon_coherence/cli.py`
  - `tests/test_cli.py`
  - `README.md`

## Status Verification (2026-09-26)

Still open. Verified against the current tip of the target repository: there is no `--web-password` option, no
`HOLON_COHERENCE_WEB_PASSWORD` lookup, no `~/.holon/web-token` persistence and no `web-key`/`web-token` command anywhere
in `apps/holon-coherence/src/holon_coherence/`.
