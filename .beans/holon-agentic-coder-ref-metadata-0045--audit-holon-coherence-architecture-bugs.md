---
# holon-agentic-coder-ref-metadata-0045
title: "Audit holon-coherence architecture, security, bugs, and improvements"
status: completed
type: task
priority: high
tags:
  - architecture
  - audit
  - security
  - bugfix
  - holon-coherence
created_at: 2026-09-26T09:26:00Z
updated_at: 2026-10-07T12:52:00Z
---

Conduct a comprehensive architectural, security, bug, and quality audit of the `holon-coherence` codebase (located in
`apps/holon-coherence/`).

Each identified inconsistency, security issue, bug, or improvement **must spin off its own dedicated,
sequentially-numbered task bean** in `.beans/` so they can be tracked, prioritized, and executed individually.

## Audit Scope

1. **Architectural Inconsistencies & Cohesion**:
   - Proxy supervision and lifecycle management (`holon-coherence start`, `stop`, `status`, daemonization vs attached
     mode).
   - Package structure and script entries (ensuring clean single entrypoint `holon-coherence`).
   - Separation of concerns between `mitm_addon.py`, `payload_cleaner.py`, proxy routing, and telemetry aggregation.
   - Alignment with coding agent runner requirements (Claude Code, Gemini, Antigravity, OpenCodeInterpreter).

2. **Security & Cryptography**:
   - MITM proxy CA certificate generation, storage permissions, and cleanup (`~/.mitmproxy/` vs isolated project
     directories).
   - Web UI interface security: credential generation, persistent tokens, localhost binding vs non-loopback exposure.
   - API key scrubbing, prompt header isolation, and payload token sanitization.
   - Prevention of unintended upstream traffic leakage or request tampering.

3. **Bugs & Edge Cases**:
   - Port conflict detection and recovery logic for proxy (8080) and web UI (8081).
   - Server-Sent Events (SSE) streaming desynchronization, chunk buffering, and non-streaming fallback edge cases.
   - LLM endpoint routing failures for host-local engines (Ollama, LM Studio, vLLM via `host.docker.internal` or
     bridge).
   - Graceful shutdown handling on `SIGINT`, `SIGTERM`, and child process teardown.

4. **Performance & Reliability Improvements**:
   - Streaming regex efficiency and memory allocation during high-throughput LLM payload scrubbing.
   - Cache hit rate determination and token reduction computation accuracy.
   - TTFT (Time To First Token) and TPS (Tokens Per Second) calculation fidelity under concurrent requests.
   - Automated testing coverage for edge-case payloads, malformed JSON, and network dropouts.

## Requirements & Spin-Off Mandate

- Perform a rigorous deep-dive code review and static analysis across all files in `apps/holon-coherence/`.
- Document all findings systematically in an audit report.
- **Spin Off Individual Beans**: For every distinct actionable finding (whether an architectural refactoring, bug fix,
  security patch, or feature improvement), create a dedicated bean in `.beans/` using the strict sequential numbering
  format (`0046`, `0047`, etc.).
- Each spin-off bean must include:
  - Exact file references and line numbers.
  - Clear explanation of the issue/improvement and its architectural impact.
  - Concrete step-by-step remediation plan and verification criteria.

## Notes

- Target Repository: `apps/holon-coherence` (bare repo `apps/holon-coherence/.git`, feature worktrees).
- Subagent delegation: Can be executed via `self` or `research` subagents to perform isolated inspection across modules.

## Status Verification (2026-09-26)

Still open. Verified against the current tip of the target repository: no audit report exists and no child beans have
been spun off for `holon-coherence`.

## Status Re-audit (2026-09-27) -- unchanged, still `todo`

No audit artefact exists for `holon-coherence` either (`find apps/holon-coherence/main/docs -iname '*audit*'` is empty).
Not started.

## Resolution

Resolved via the full 5-stage Holon Flow lifecycle on `holon-coherence`:

1. **Stage 1 (Intent)**: `I-1791374885-audit-holon-coherence-architecture-bugs/_`
2. **Stage 2 (Plan)**: `P-1791374897-antigravity-agent-gemini-3.8-flash-medium` ($\text{Predicted EV}: 82.16$)
3. **Stage 3 (Execute)**: `E-1791375039-antigravity-agent-gemini-3.8-flash-medium` generated comprehensive audit report
   in `docs/audit_report.md` (34,559 bytes, 16 discrete findings across Architecture, Security, Bugs & Concurrency, and
   Testing/Tooling). Added `pythonpath = ["src"]` to `pyproject.toml` for hermetic pytest discovery.
4. **Stage 4 (PR Review Loop)**: Opened Pull Request
   [#9](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/9). All 7 GitHub Actions CI workflows passed cleanly
   across Ubuntu and macOS. 3-agent reviewer ensemble consensus review conducted with unanimous **APPROVED** verdict.
5. **Stage 5 (Calibration)**: Executed `holon calibrate` resulting in branch
   `I-1791374885-audit-holon-coherence-architecture-bugs/P-1791374897-antigravity-agent-gemini-3.8-flash-medium/E-1791375039-antigravity-agent-gemini-3.8-flash-medium/calibrated`
   and report `plans/P-1791374897-antigravity-agent-gemini-3.8-flash-medium_calibration.md` ($\text{Predicted EV}:
   88.06$, $\text{Actual EV}: 88.51$, $\Delta\text{EV}: +0.45$).
6. **Spin-Off Task Beans Created in Control Plane**:
   - [Bean 0070](holon-agentic-coder-ref-metadata-0070--harden-file-permissions-on-pki-certs-and-wire-logs.md): Harden
     file permissions on PKI certs, wire logs, and cache database (`0o700`/`0o600`).
   - [Bean 0071](holon-agentic-coder-ref-metadata-0071--fix-web-dashboard-port-forwarding-in-docker-run.md): Fix web
     dashboard port forwarding (`-p {web_port}:{web_port}`) in Docker run command.
   - [Bean 0072](holon-agentic-coder-ref-metadata-0072--harden-cache-concurrency-ttl-and-semantic-matching.md): Harden
     cache concurrency, WAL mode, TTL expiration, and semantic matching performance.
   - [Bean 0073](holon-agentic-coder-ref-metadata-0073--expand-secret-redaction-patterns-for-auth-and-credentials.md):
     Expand secret redaction patterns to prevent leaking `auth` and `credential` keys in wire logs.
   - [Bean 0074](holon-agentic-coder-ref-metadata-0074--expand-test-suite-for-sse-streaming-and-mitm-proxy-caching.md):
     Expand test suite for SSE streaming, network chunking, and proxy cache integration.
   - [Bean 0075](holon-agentic-coder-ref-metadata-0075--decouple-orphaned-modules-and-fix-documentation-path-drift.md):
     Decouple orphaned modules (`OpenBrainMemory`, `RAGCodebaseIndexer`, `RingerOrchestrator`) and fix documentation
     path drift.
