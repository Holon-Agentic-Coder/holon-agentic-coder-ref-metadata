---
# holon-agentic-coder-ref-metadata-0073
title: "Expand secret redaction patterns to prevent leaking auth and credentials in wire logs"
status: completed
type: bug
priority: high
created_at: 2026-10-07T12:50:00Z
updated_at: 2026-10-09T11:45:00Z
---

## Summary

In `holon-coherence`, `src/holon_coherence/payload_cleaner.py` uses `_SECRET_DICT_KEY_PATTERN` to mask sensitive fields
before writing request/response payloads to disk or telemetry. The regex currently checks
`(?:api[-_]?key|authorization|bearer|secret|token|password)`. However, common authentication payloads use fields like
`"auth"`, `"credential"`, `"credentials"`, or `"refresh_token"`, which bypass dictionary redaction and could expose raw
credentials in wire logs (CWE-312).

## Target Repository

- Repository: `holon-coherence` (`apps/holon-coherence/`)

## Key Tasks

- Expand `_SECRET_DICT_KEY_PATTERN` regex in `payload_cleaner.py` to cover `auth`, `credential`, `credentials`,
  `client_secret`, and `refresh_token`.
- Add test cases verifying that nested structures containing `"auth": {...}` or `"credentials": "..."` are properly
  masked.
- Verify zero regression in token counting and payload preservation for non-sensitive request structures.

## Notes

- Discovered in comprehensive architectural and security audit (Bean 0045, `docs/audit_report.md` Finding SEC-03).

## Resolution

Resolved via the 5-stage Holon flow (coherence security & network hardening batch with Beans 0070 and 0071) in PR
[#11](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/11):

- Expanded `_SECRET_DICT_KEY_PATTERN` and `_SECRET_HEADER_NAMES` across `src/holon_coherence/mitm_addon.py` and
  `src/holon_coherence/payload_cleaner.py` to match `auth`, `credential`, `credentials`, `client_secret` (and
  `client-secret`), and `refresh_token` (and `refresh-token`).
- Ensured case-insensitive recursive scrubbing for payloads, dictionaries, and headers replaces secrets with
  `[REDACTED]`.
- Added test cases in `tests/test_coherence.py` validating nested masking while preserving non-secret keys (`author`,
  `authenticity`).
- Approved unanimously by 3-agent reviewer ensemble (3/3 `APPROVED`, 0 Critical, 0 Important).
- Calibrated and carried calibration report onto PR branch (`2e9dfc8`) and `/calibrated` branch (`a3c0ae9`). All 7 CI
  checks pass.
