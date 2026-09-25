---
# holon-agentic-coder-ref-metadata-0044
title: "Audit holon-agentic-coder architecture, security, bugs, and improvements"
status: todo
type: task
priority: high
tags:
  - architecture
  - audit
  - security
  - bugfix
  - holon-agentic-coder
created_at: 2026-09-26T09:26:00Z
updated_at: 2026-09-26T15:20:00Z
---

Conduct a comprehensive architectural, security, bug, and quality audit of the `holon-agentic-coder` codebase (located
in `apps/holon-agentic-coder/`).

Each identified inconsistency, security issue, bug, or improvement **must spin off its own dedicated,
sequentially-numbered task bean** in `.beans/` so they can be tracked, prioritized, and executed individually.

## Audit Scope

1. **Architectural Inconsistencies & Cohesion**:
   - CLI design and entrypoint consistency across `apps/sandbox-executor/`, `apps/agent-runner/`, and root tooling.
   - Project configuration management, environment variable precedence (`HOLON_*`), and state directory conventions
     (`holon-config/`, `holon-knowledge/`).
   - Packaging structure (`pyproject.toml`, workspace members, console script definitions).
   - Alignment with `apps/holon-coherence` interfaces and metadata repository conventions.

2. **Security & Isolation**:
   - Container isolation, Docker socket mounting, and host privilege boundary enforcement in `apps/sandbox-executor/`.
   - Credential and token hygiene (handling of `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, `GITHUB_TOKEN`).
   - Shell command construction, escaping, and prevention of injection vulnerabilities in script execution harnesses.
   - Safe defaults for network egress and proxy redirection inside sandbox environments.

3. **Bugs & Edge Cases**:
   - Cross-platform path handling (macOS vs Linux differences in `find`, `sed`, `date`, `stat`).
   - Unhandled exceptions, process exit codes, and failure cascade handling during sandbox runs.
   - Git worktree, commit, and branch manipulation edge cases (dirty state, detached HEADs, tag conflicts).
   - Dependency locking and environment drift (`uv lock`, virtualenv isolation).

4. **Reliability & Performance Improvements**:
   - Container image build times, layering, and caching mechanisms.
   - Parallel test execution, test hygiene, and mock fidelity.
   - Telemetry, logging consistency, and structured error reporting.

## Requirements & Spin-Off Mandate

- Perform a rigorous deep-dive code review and static analysis across all files in `apps/holon-agentic-coder/`.
- Document all findings systematically in an audit report.
- **Spin Off Individual Beans**: For every distinct actionable finding (whether an architectural refactoring, bug fix,
  security patch, or feature improvement), create a dedicated bean in `.beans/` using the strict sequential numbering
  format (`0046`, `0047`, etc.).
- Each spin-off bean must include:
  - Exact file references and line numbers.
  - Clear explanation of the issue/improvement and its architectural impact.
  - Concrete step-by-step remediation plan and verification criteria.

## Notes

- Target Repository: `apps/holon-agentic-coder` (bare repo `apps/holon-agentic-coder/.git`, feature worktrees).
- Subagent delegation: Can be executed via `self` or `research` subagents to perform isolated inspection across modules.

## Status Verification (2026-09-26)

Still open. Verified against the current tip of the target repository: no audit report exists and no child beans have
been spun off; the highest bean id is still the audit batch itself, so no finding has been tracked yet.
