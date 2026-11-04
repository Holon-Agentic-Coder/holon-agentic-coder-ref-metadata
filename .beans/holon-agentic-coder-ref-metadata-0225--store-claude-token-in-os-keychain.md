---
# holon-agentic-coder-ref-metadata-0225
title: "Store the Claude OAuth token in the OS keychain (macOS Keychain / Linux Secret Service), file as fallback"
status: todo
type: feature
priority: normal
tags:
  - agent-runner
  - credentials
  - security
  - holon-agentic-coder
created_at: 2026-11-04T03:20:00Z
updated_at: 2026-11-04T03:20:00Z
---

## Problem

The Claude subscription token persists as plaintext in `~/.holon/secrets/claude-oauth-token` (0600). The credential
auto-discovery work keeps that file as the discovery source, which leaves a long-lived secret in the clear on disk. The
at-rest fix is the operating system's secret store, with the file kept only as a fallback for hosts without one.

## Scope

1. **Read side (credential discovery order)**, extending the discovery seam: explicit `HOLON_AGENT_KEY` > OS keychain >
   `~/.holon/secrets/claude-oauth-token` (fallback, with a one-line warning that the keychain is preferred) > pre-flight
   failure with a hint naming all three routes.
   - macOS: `security find-generic-password -s holon -a claude-oauth-token -w` (the `security` CLI; no new Python
     dependency).
   - Linux: the freedesktop Secret Service API via `secret-tool lookup service holon account claude-oauth-token`
     (libsecret; backed by GNOME Keyring or KWallet). Headless hosts without a Secret Service daemon fall through to the
     file with the warning; `systemd-creds` may be documented as the headless alternative but is not implemented in this
     change.
2. **Write side**: document the one-liners for storing the token (`security add-generic-password -U …` on macOS,
   `secret-tool store …` on Linux) in `docs/executor/agent_credentials_requirements.md`; no new CLI subcommand and no
   new environment variables.
3. **One-time migration**: when the plaintext file exists and the platform keychain is writable, import the token into
   the keychain and remove the plaintext file, printing exactly what was done. If the keychain is unavailable, leave the
   file untouched.
4. The token value is never echoed, logged or passed on a command line as an argument (the keychain CLIs read/write via
   stdin/stdout where supported); redaction tests cover the new paths.
5. Tests (pytest only; no real keychain, Docker, gh, git remotes or LLM calls — fake the `security`/`secret-tool`
   seams): discovery order incl. both platforms and the headless fall-through; migration happy path, keychain-missing
   path and failed-write path (file kept); warning emitted on file fallback; no secret in any echo or log.

## Dependencies

After the credential auto-discovery bean lands (it builds the discovery seam this extends). No new environment variables
and no new Python dependencies (subprocess calls to the platform CLIs only).

## Notes

- Run through the Holon flow on holon-agentic-coder.
- Maintainer context (2026-11-04): the file stays persistent (consume-once was rejected); this bean removes the at-rest
  plaintext exposure instead, which was the remaining concern.
