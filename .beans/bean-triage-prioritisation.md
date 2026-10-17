# Holon Ecosystem Bean Triage and Prioritisation Matrix

**Last Updated:** 2026-10-17 14:12:33 UTC

## Executive Summary

Since the previous triage checkpoint on 2026-10-03, the Holon ecosystem has progressed through automated Holon flow
cycles, multi-agent consensus review loops, and infrastructure hardening.

- **Total Tracked Beans**: 121 (excluding template)
- **Completed**: 112 (92.6%)
- **Scrapped / Superseded**: 2 (1.7%)
- **Active / Todo**: 7 (5.8%)

---

## Key Milestones Completed (Beans 0080 – 0118)

1. **Holon Flow and Automation Engine**:
   - `0084`: Fixed CI check name collisions in review gates.
   - `0087`: Permitted autonomous PR creation in Holon flow stage 3.
   - `0089`: Auto-routed all flow stages through Holon Coherence proxy for token deduplication and caching.
   - `0093`: Atomic ledger locking with exponential backoff and `flock`.
   - `0094`: Checkpoint schema versioning and automated state migration.
2. **Action Knowledge Base and Wisdom (Bean 0052 / PR #78)**:
   - Full integration of SQLite FTS5 inverted index and discrete action ledger (`actions.jsonl`).
   - Pre-action wisdom consult (`holon consult`) across intent, planning, execution, and review stages.
   - Statistical Wilson score promotion ladder and deterministic failure veto engine.
3. **Multi-Agent Review Loop and Hygiene (PR #52)**:
   - `0099`: Write-capable children and nested Prettier formatting guards.
   - `0103`: Implemented `clean-workspace` skill and Python automation (`clean_workspace.py`) covering worktrees,
     branches, orphan directories, `.subagent/` review caches, and `todo/` scratchpads.
   - Passed 100% unanimous 3/3 ensemble consensus approval on PR #52.
4. **Agent Container Modernisation and Buildx Bake Integration (Beans 0112 and 0114 / PR #80)**:
   - Upgraded all container images (`@anthropic-ai/claude-code@2.1.302`, `@openai/codex@0.163.0`,
     `@google/gemini-cli@0.64.0`, `opencode-ai@1.19.3`, `@earendil-works/pi-coding-agent@1.3.0`).
   - Added hardened writable tmpfs overlays for Antigravity and Codex session logs and caches.
   - Fully automated Buildx Bake builds across all 8 role/orchestrator images with layer caching.
5. **Ecosystem Build and Installation Automation (Bean 0117)**:
   - Implemented `install-holon` and `install-coherence` skills (`.agents/skills/install_holon/SKILL.md`,
     `.agents/skills/install_coherence/SKILL.md`) and companion Python orchestrators (`install_holon.py`,
     `install_coherence.py`).
   - Automates building Docker images via Buildx Bake and installing/updating `holon` and `holon-coherence` via
     `uv tool install`.
6. **Native Review Loop and Metrics Alignment (Beans 0115 and 0118 / PR #23 & PR #81)**:
   - `0115`: Stripped all emojis from `holon-coherence metrics` terminal table and aligned colon spacing at column 31.
     Raised PR #23 on `holon-coherence`, passed 3-agent ensemble review.
   - `0118`: Implemented explicit native `holon review-loop` CLI step (Stage 4) in `holon-agentic-coder`. Raised PR #81,
     resolved findings in iteration 1, passed 3-agent ensemble review, and completed Stage 5 calibration.
7. **Makefile Alignment, PR Metadata, and Ledger Enhancements (Beans 0116, 0113, 0119, 0109 / PR #24 & PR #82)**:
   - `0116`: Added `build-images` alias, `tools`, and `lint` targets in `holon-coherence` (PR #24); added `build-image`
     alias in `holon-agentic-coder` (PR #82).
   - `0109`: Automated conventional commit PR titles (`feat(...)`, `fix(...)`) and structured Markdown bodies with
     Summary, Changes, and Beans.
   - `0119`: Dual-posting review consensus (top-level comment + official review) with HTTP 422 author self-approval
     fallback.
   - `0113`: Granular action logging in `executions.jsonl` recording evaluations, findings, resolver triggers, and
     consensus posting.

---

## Active Beans Triage and Prioritisation Matrix

| Priority | Status | Impact | Sizing | Bean # | Title                                                                                              | Domain                 | Dependencies / Notes                                                                                |
| :------- | :----- | :----: | :----: | :----: | :------------------------------------------------------------------------------------------------- | :--------------------- | :-------------------------------------------------------------------------------------------------- |
| **P1**   | todo   |  High  |   M    |  0121  | Detect and resolve conflicts proactively across all Holon flow stages                              | Flow / Concurrency     | Proactive conflict detection and automated resolution across all 5 Holon flow stages.               |
| **P1**   | todo   |  High  |   M    |  0110  | Implement pre-commit credential leakage and ephemeral scratch file detection                       | Security / Git Hooks   | Prevents API keys (Google AI, GitHub PATs) and ephemeral scratch paths from being staged.           |
| **P1**   | todo   | Medium |   S    |  0107  | Add Python unit test and lint workflow to CI for metadata repository                               | CI / Testing           | Integrates pytest tests/ and ruff check into GitHub Actions for holon-agentic-coder-ref-metadata.   |
| **P1**   | todo   |  High  |   L    |  0106  | Audit quality in source code and architecture, security, devex, and system integrity               | Architecture / Quality | Holistic multi-dimensional audit of architecture, hermeticity, error handling, and test boundaries. |
| **P1**   | todo   |  Low   |   S    |  0105  | Adopt Australian English spelling across all documentation, guidelines, and user-facing copy       | Standards / Style      | Standardised in holon-agentic-coder (PR #79); ongoing enforcement across ecosystem docs.            |
| **P2**   | todo   | Medium |   M    |  0111  | Overhaul repository documentation with slimmed-down README, build badges, and structured reference | Documentation / DevEx  | Slims root README.md to under 60-second read; moves deep specs to docs/architecture-overview.md.    |
| **P2**   | todo   |  Low   |   S    |  0108  | Implement automated subagent artifact archiving and retention policy                               | Hygiene / Tooling      | Relocates completed PR review intermediates into _archive/ with 30-day retention pruning.           |

---

## Recommended Next Execution Sequence

1. **Proactive Flow Conflict Detection & Resolution (Bean 0121)**:
   - Detect branch divergence against `origin/main` proactively across all 5 Holon flow stages (intent -> plan ->
     execute -> review -> calibrate).
   - Automatically rebase or merge upstream updates early to prevent PR merge conflicts.
2. **Pre-Commit Credential Leakage & Scratch File Detection (Bean 0110)**:
   - Pre-commit hook preventing secret tokens and ephemeral scratchpad files from staging.
3. **Python Test & Lint CI Workflow for Metadata Repo (Bean 0107)**:
   - Integrate pytest and Ruff checking into GitHub Actions CI for `holon-agentic-coder-ref-metadata`.
4. **Holistic Architecture & Quality Audit (Bean 0106)**:
   - Comprehensive audit of architecture, hermetic boundaries, error handling, and test suites.
5. **Ecosystem Australian English Spelling Enforcement (Bean 0105)**:
   - Standardise copy, guidelines, and documentation across the ecosystem.
