---
# holon-agentic-coder-ref-metadata-0525
title: "Harden /holon/* dashboard Host validation, /holon/api/mode auth, CORS, and wire_log_dir"
status: in-progress
type: bug
priority: critical
tags:
  - holon-coherence
  - security
  - proxy
created_at: 2026-11-26T13:35:00Z
updated_at: 2026-11-27T06:11:45Z
---

## Problem

The proxy's local dashboard and mode-control endpoint intercept `/holon/*` paths regardless of the request `Host`
header, expose an unauthenticated control endpoint with wildcard CORS that accepts arbitrary `wire_log_dir` filesystem
paths, and ignore runtime mode overrides in `GET /holon/api/mode` when `HOLON_PASSIVE_MONITORING=1` is set.

## Evidence

- `src/holon_coherence/proxy/steps/serve_dashboard.py:16-93`:
  - Matches `path_clean` without checking `Host` header, allowing any upstream domain serving `/holon/*` (or browser
    CSRF) to hit the local control plane.
  - Line 24: sets `Access-Control-Allow-Origin: *`.
  - Line 39: exposes unauthenticated `POST /holon/api/mode` accepting an arbitrary unvalidated `wire_log_dir` path.
  - Line 59: `GET /holon/api/mode` ignores runtime overrides when `HOLON_PASSIVE_MONITORING=1`.

## Proposed Change

1. Restrict `/holon/*` interception in `serve_dashboard.py` to explicit loopback/holon `Host` headers (e.g.,
   `localhost`, `127.0.0.1`, `[::1]`, or an explicit internal dashboard host).
2. Require bearer/web-token authentication on `POST /holon/api/mode` and drop `Access-Control-Allow-Origin: *`.
3. Reject arbitrary `wire_log_dir` paths or confine them strictly inside an allowed configured base directory via
   `Path.resolve()` containment checks.
4. Fix `GET /holon/api/mode` to report active runtime overrides consistently with `POST /holon/api/mode`.

## Acceptance Criteria

- Requests for `/holon/*` targeting external `Host` headers pass through upstream untouched.
- Unauthenticated or cross-origin `POST /holon/api/mode` requests return `401`/`403`, and path traversal / out-of-bounds
  `wire_log_dir` values return `400`.
- `GET /holon/api/mode` returns the effective runtime mode even when `HOLON_PASSIVE_MONITORING=1`.

## Notes

- Target repository: `holon-coherence` (evaluated at `HEAD 18084f3`).
- Source: 2026-11 ecosystem architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
