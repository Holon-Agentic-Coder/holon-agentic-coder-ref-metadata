---
# holon-agentic-coder-ref-metadata-0071
title: "Fix web dashboard port forwarding in Docker run command"
status: completed
type: bug
priority: normal
created_at: 2026-10-07T12:50:00Z
updated_at: 2026-10-09T11:45:00Z
---

## Summary

In `holon-coherence`, `cli.py` accepts `--web` and `--web-port` CLI flags to run mitmweb with an interactive telemetry
dashboard. However, when invoking the container via `docker run`, `cli.py` only binds `-p {port}:{port}` for the proxy
traffic port, omitting `-p {web_port}:{web_port}`. As a result, the web UI started inside the container is unreachable
from the host.

## Target Repository

- Repository: `holon-coherence` (`apps/holon-coherence/`)

## Key Tasks

- In `src/holon_coherence/cli.py`, add `-p {web_port}:{web_port}` to the docker run command arguments whenever `--web`
  is enabled.
- Verify `mitmweb` binds to `0.0.0.0` or `--web-host 0.0.0.0` inside container so forwarded ports receive requests from
  host.
- Add unit tests verifying docker command construction with and without `--web`.
- Update CLI usage docs and `docs/running_mitm_sidecar_guide.md`.

## Notes

- Discovered in comprehensive architectural and security audit (Bean 0045, `docs/audit_report.md` Finding BUG-01).

## Resolution

Resolved via the 5-stage Holon flow (coherence security & network hardening batch with Beans 0070 and 0073) in PR
[#11](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/11):

- In `src/holon_coherence/cli.py`, configured docker run command construction to bind
  `-p 127.0.0.1:{args.web_port}:8081` whenever `--web` is enabled.
- Ensured inside the container `mitmweb` launches with `--web-host 0.0.0.0 --web-port {web_port}` so the web dashboard
  is accessible from the host.
- Added 4 unit tests in `tests/test_cli.py` testing `--web`, custom `--web-port`, omission of `--web`, and container
  command argument structures.
- Updated documentation in `docs/running_mitm_sidecar_guide.md`.
- Approved unanimously by 3-agent reviewer ensemble (3/3 `APPROVED`, 0 Critical, 0 Important).
- Calibrated and carried calibration report onto PR branch (`2e9dfc8`) and `/calibrated` branch (`a3c0ae9`). All 7 CI
  checks pass.
