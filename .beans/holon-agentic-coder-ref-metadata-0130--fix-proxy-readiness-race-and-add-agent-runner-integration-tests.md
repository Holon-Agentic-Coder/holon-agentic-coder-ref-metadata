---
# holon-agentic-coder-ref-metadata-0130
title: "Fix proxy readiness race condition and add agent runner startup integration tests"
status: completed
type: bug
priority: critical
tags:
  - coherence
  - proxy
  - agy
  - integration-tests
  - networking
created_at: 2026-10-20T11:15:00Z
updated_at: 2026-10-20T11:15:00Z
---

Fix proxy readiness polling race condition during cold container startup and introduce an end-to-end integration test
suite verifying cold-start execution of agent runners (`holon-coherence agy`, `pi`, `claude`, `codex`, `opencode`).

## Context & Findings

When running `holon-coherence agy` (or other agent runners like `pi`, `claude`, `codex`, `opencode`) from a cold state
(where the background proxy container `holon-coherence-proxy` is not yet running), the command abruptly fails with
connection drop errors:

```text
> hello

⚠ Eligibility Check
  ⎿  Eligibility check failed: Post "https://daily-cloudcode-pa.googleapis.com/v1internal:loadCodeAssist": unexpected EOF
```

### Root Cause

1. **Host Port Binding vs Container Readiness**:
   - `ensure_proxy_running()` launches the proxy container via `docker run -d -p 127.0.0.1:8080:8080 ...` and
     immediately calls `wait_for_proxy_ready(port)`.
   - `wait_for_proxy_ready(port)` relies on `is_port_in_use(port)`.
   - Because Docker's host-side `docker-proxy` process binds `127.0.0.1:8080` on the host OS virtually instantaneously
     upon container creation, `is_port_in_use(port)` returns `True` immediately (within 0–5ms).
2. **In-Container Process Bootstrapping Delay**:
   - Inside the container, Python and `mitmdump` take approximately 300–400ms to boot, import dependencies, compile
     `mitm_addon.py`, and begin listening on container port 8080.
3. **Premature Subprocess Execution**:
   - `run_agent()` launches the target agent CLI (`agy`) immediately while `mitmdump` is still booting.
   - When `agy` connects to `127.0.0.1:8080` for initial background eligibility and discovery requests
     (`loadCodeAssist`, `userinfo`), `docker-proxy` cannot forward to the container port yet and terminates the
     connection with `unexpected EOF` (or connection reset).
   - In `agy` (written in Go), this failure is cached in the in-memory `singleflight` cache. When the user subsequently
     submits input in the interactive REPL, the cached failure aborts execution.
4. **Warm vs Cold State**:
   - Once the container has finished starting up, all subsequent calls succeed cleanly because `mitmdump` is actively
     serving traffic.

## Proposed Remediation

### 1. HTTP-Level Readiness Probe in `wait_for_proxy_ready`

Replace the pure TCP port check in `wait_for_proxy_ready()` with an active HTTP probe against the proxy's internal
metrics endpoint:

- Poll `http://127.0.0.1:{port}/holon/api/metrics` (or `/_holon/metrics`) using `urllib.request` with a short timeout
  (e.g. 0.25s).
- Consider the proxy ready only when an HTTP 200 response is successfully received from `mitmproxy`.
- Retain fail-fast handling if the container stops running (`is_container_running(name)` returns `False`).
- Maintain timeout safeguards (`PROXY_READY_TIMEOUT_SECONDS`).

### 2. Comprehensive Agent Runner Startup Integration Tests

Add automated integration tests (`@pytest.mark.integration_test`):

- Ensure proxy container is stopped prior to the test.
- Execute `holon-coherence agy -- --help` (or non-interactive test flags) and verify it automatically boots the
  container and exits cleanly with return code 0.
- Execute other agent entrypoints (`holon-coherence pi -- --help`, `claude`, `codex`, `opencode`) to verify uniform
  cold-start behaviour without connection resets or EOF errors.
- Verify unit tests in `tests/test_cli.py` for `wait_for_proxy_ready` reflect the HTTP readiness polling logic.

## Acceptance Criteria

- [x] `wait_for_proxy_ready()` verifies HTTP 200 response from the proxy before declaring readiness.
- [x] Running `holon-coherence agy` from a cold state (no container running) boots the proxy and connects successfully
      without `unexpected EOF` or eligibility check errors.
- [x] Integration tests verify cold-start launch of supported agent runners (`agy`, `pi`, `claude`, `codex`,
      `opencode`).
- [x] All unit and integration test suites pass via `uv run pytest`.

## Resolution

- **Pull Request**:
  [Holon-Agentic-Coder/holon-coherence#26](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/26)
- **5-Stage Provenance**:
  - Intent: `I-1792495073-coherence-fix-proxy-readiness-and-agent-tests/_`
  - Plan: `P-1792495105-antigravity-agent-gemini-3.8-flash-medium`
  - Execution: `E-1792495303-antigravity-agent-gemini-3.8-flash-medium`
  - Review: Consensus `APPROVED` (Reviewer Ensemble, Iteration 1)
  - Calibration: `plans/P-1792495105-antigravity-agent-gemini-3.8-flash-medium_calibration.md` (Predicted EV: 7.33 |
    Actual EV: 7.08 | ΔEV: -0.25)
- **CI Status**: 7/7 passing across Linux and macOS workflows.
