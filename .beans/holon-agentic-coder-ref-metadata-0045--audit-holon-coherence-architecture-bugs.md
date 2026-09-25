---
# holon-agentic-coder-ref-metadata-0045
title: "Audit holon-coherence architecture, security, bugs, and improvements"
status: todo
type: task
priority: high
tags:
  - architecture
  - audit
  - security
  - bugfix
  - holon-coherence
created_at: 2026-09-26T09:26:00Z
updated_at: 2026-09-26T15:20:00Z
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
