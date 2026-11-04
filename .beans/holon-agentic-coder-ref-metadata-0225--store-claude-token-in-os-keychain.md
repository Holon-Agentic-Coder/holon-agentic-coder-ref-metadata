---
# holon-agentic-coder-ref-metadata-0225
title: "Claude token lives only in the OS keychain; retire ~/.holon/secrets/claude-oauth-token entirely"
status: todo
type: feature
priority: normal
tags:
  - agent-runner
  - credentials
  - security
  - holon-agentic-coder
created_at: 2026-11-04T03:20:00Z
updated_at: 2026-11-04T04:15:00Z
---

## Problem

The Claude subscription token persists as plaintext in `~/.holon/secrets/claude-oauth-token` (0600). The credential
auto-discovery work keeps that file as the discovery source, which leaves a long-lived secret in the clear on disk. The
at-rest fix is the operating system's secret store, with the file kept only as a fallback for hosts without one.

## Decision (maintainer, 2026-11-04)

The plaintext file is retired entirely, not kept as a fallback. After this change the claude credential lives only in
the operating system's secret store; the file's sole remaining role is as one-time migration input.

## Scope

1. **Read side (credential discovery)**: OS keychain only — macOS
   `security find-generic-password -s holon -a claude-oauth-token -w`; Linux Secret Service via
   `secret-tool lookup service holon account claude-oauth-token` (libsecret; GNOME Keyring or KWallet). No
   `HOLON_AGENT_KEY` for claude, no file fallback. When no keychain entry (or no secret service at all) exists,
   pre-flight fails closed with a hint giving the store one-liner for this platform and `claude setup-token`. No
   headless path is needed: CI pipelines never invoke `holon flow` — flows run on operator machines, which have a
   keychain (maintainer, 2026-11-04).
2. **Write side**: document the store one-liners (`security add-generic-password -U …`, `secret-tool store …`) in
   `docs/executor/agent_credentials_requirements.md`; the token is piped via stdin, never an argv argument; no new CLI
   subcommand and no new environment variables.
3. **One-time migration**: when `~/.holon/secrets/claude-oauth-token` exists and the platform keychain is writable,
   import the token into the keychain and delete the plaintext file, printing exactly what was done. If the keychain
   write fails, the file is left untouched and pre-flight says so. This retires the interim file-discovery route from
   the preceding credential bean.
4. The token value is never echoed, logged or passed as a command-line argument; redaction tests cover the new paths.
5. Tests (pytest only; fake the `security`/`secret-tool` seams; no real keychain, Docker, gh, git remotes or LLM calls):
   keychain discovery on both platforms; no-entry and no-secret-service failures produce the platform hint; migration
   happy path, failed-write path (file kept) and already-migrated path (no file, no action); no secret in any echo or
   log.

## Dependencies

After the credential auto-discovery bean lands (it builds the discovery seam this extends). No new environment variables
and no new Python dependencies (subprocess calls to the platform CLIs only).

## Notes

- Run through the Holon flow on holon-agentic-coder.
- Maintainer context (2026-11-04): the file stays persistent (consume-once was rejected); this bean removes the at-rest
  plaintext exposure instead, which was the remaining concern.
