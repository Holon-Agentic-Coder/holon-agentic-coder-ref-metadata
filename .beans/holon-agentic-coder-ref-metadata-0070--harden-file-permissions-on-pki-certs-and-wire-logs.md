---
# holon-agentic-coder-ref-metadata-0070
title: "Harden file permissions on PKI certs, wire logs, and cache database"
status: completed
type: bug
priority: high
created_at: 2026-10-07T12:50:00Z
updated_at: 2026-10-09T11:45:00Z
---

## Summary

In `holon-coherence`, sensitive files including private CA keys, TLS proxy certificates, sqlite cache databases, and
wire request logs are written using default umask (`0o644` / `0o755`), creating security risks (CWE-732) where secrets
or private keys could be read by non-privileged users on multi-tenant hosts.

## Target Repository

- Repository: `holon-coherence` (`apps/holon-coherence/`)

## Key Tasks

- Enforce `0o700` permissions on CA key and certificate directories created in `ca_generator.py`.
- Restrict generated private key files (`ca.key`, host keys) to `0o600`.
- Enforce `0o600` on wire log dumps (`requests.jsonl`, `telemetry.jsonl`) and sqlite cache databases (`cache.db`).
- Set process `umask` or explicit file descriptor permissions when initializing storage directories.
- Add unit and regression tests verifying restrictive file mode permissions across all storage operations.

## Notes

- Discovered in comprehensive architectural and security audit (Bean 0045, `docs/audit_report.md` Finding SEC-01 &
  SEC-04).

## Resolution

Resolved via the 5-stage Holon flow (coherence security & network hardening batch with Beans 0073 and 0071) in PR
[#11](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/11):

- Enforced `0o700` mode on CA certificate directories (`ca_generator.py`), cache directories (`hybrid_cache.py`), wire
  log directories (`mitm_addon.py`), and CLI directories (`cli.py`).
- Enforced `0o600` on Root CA private keys, `mitmproxy-ca.pem`, `llm_cache.db`, and wire transaction logs
  (`transactions.jsonl` and individual turn JSON files) using atomic `os.open(..., 0o600)` and `os.chmod(..., 0o600)`.
- Added comprehensive unit tests in `tests/test_coherence.py` validating exact octal modes using `stat.S_IMODE`.
- Approved unanimously by 3-agent reviewer ensemble (3/3 `APPROVED`, 0 Critical, 0 Important).
- Calibrated and carried calibration report
  (`plans/P-1791537711-antigravity-agent-gemini-3.8-flash-medium_calibration.md`) onto PR branch (`2e9dfc8`) and
  `/calibrated` branch (`a3c0ae9`). All 7 CI checks pass.
