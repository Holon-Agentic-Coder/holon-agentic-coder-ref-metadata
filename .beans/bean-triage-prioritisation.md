# Holon Ecosystem Bean Triage and Prioritisation Matrix

**Last Updated:** 2026-10-22 00:34:55 UTC

## Executive Summary

Since the previous triage checkpoint on 2026-10-20, the Holon ecosystem has progressed through automated Holon flow
cycles, multi-agent consensus review loops, and infrastructure hardening.

- **Total Tracked Beans**: 133 (excluding template)
- **Completed**: 128 (96.2%)
- **Scrapped / Superseded**: 2 (1.5%)
- **Active / Todo**: 3 (2.3%)

---

## Key Milestones Completed (Beans 0080 – 0131)

1. **Holon Flow and Automation Engine**:
   - `0084`: Fixed CI check name collisions in review gates.
   - `0087`: Permitted autonomous PR creation in Holon flow stage 3.
   - `0089`: Auto-routed all flow stages through Holon Coherence proxy for token deduplication and caching.
   - `0093`: Atomic ledger locking with exponential backoff and `flock`.
   - `0094`: Checkpoint schema versioning and automated state migration.
2. **Action Knowledge Base and Wisdom (Bean 0052 / PR #78)**:
   - Full integration of the SQLite FTS5 inverted index over the canonical `executions.jsonl` ledger (the auxiliary
     `actions.jsonl` was later retired by Bean 0123).
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
7. **Makefile Alignment, PR Metadata, and Ledger Enhancements (Beans 0116, 0113, 0119, 0109 / PR #25 & PR #82)**:
   - `0116`: Added `build-images` alias, `tools`, and `lint` targets in `holon-coherence` (PR #25); added `build-image`
     alias in `holon-agentic-coder` (PR #82).
   - `0109`: Automated conventional commit PR titles (`feat(...)`, `fix(...)`) and structured Markdown bodies with
     Summary, Changes, and Beans.
   - `0119`: Dual-posting review consensus (top-level comment + official review) with HTTP 422 author self-approval
     fallback.
   - `0113`: Granular action logging in `executions.jsonl` recording evaluations, findings, resolver triggers, and
     consensus posting.
8. **Decoupled Architecture and Canonical 3-Ledger Consolidation (Beans 0122 and 0123 / PR #85)**:
   - Purged all harness-specific metadata paths (`.beans/`, `todo/`, `.agents/`) from target repositories.
   - Retired auxiliary `actions.jsonl` ledger; interleaved all discrete micro-actions (`entry_type: 'action'`) and run
     summaries (`entry_type: 'summary'`) inside `executions.jsonl` under `LedgerLock`.
   - Codified harness isolation, test execution constraints (strictly `uv run pytest`), and ledger invariants across
     ecosystem instructions.
9. **Unified Git Abstraction, Unprivileged Containers, and Hardened Locking (Beans 0124 – 0127 / PR #86)**:
   - `0124`: Implemented unified Git abstraction in `sandbox_executor.git` with custom exceptions and strict stderr
     diagnostics.
   - `0125`: Australian English spelling hygiene across documentation and codebase comments.
   - `0126`: Enforced unprivileged Docker execution via `--cap-drop=ALL` with selective capability drops.
   - `0127`: Hardened `LedgerLock` concurrency file locking with exponential backoff and timeouts.
10. **Documentation Gap Remediation and Container `gh` Availability (Beans 0128 and 0131 / PR #87 & PR #88)**:
    - `0128`: Closed documentation drift across `holon-agentic-coder` (PR #87) and the harness, so flow stage, ledger,
      and worktree instructions match the implemented behaviour.
    - `0131`: Installed the GitHub CLI into `holon-base` so every agent image and the Stage 4 review-loop container can
      post consensus reviews, plus container availability tests (PR #88, Stage 5 calibrated).
11. **Proxy Cold-Start Readiness and Agent Runner Tests (Bean 0130 / holon-coherence PR #26)**:
    - Replaced the fixed-sleep readiness probe with HTTP readiness polling, deduplicated the proxy `chmod` handling,
      routed readiness probes around the proxy, and added agent runner integration tests.
    - Traversed all 5 Holon flow stages and passed unanimous 3/3 ensemble consensus at iteration 4; residual nits were
      deferred to Beans 0132 and 0133 instead of being dropped.

---

## Active Beans Triage and Prioritisation Matrix

| Priority | Status | Impact | Sizing | Bean # | Title                                                                         | Domain              | Dependencies / Notes                                                                                                                                                                                                        |
| :------- | :----- | :----: | :----: | :----: | :---------------------------------------------------------------------------- | :------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **P1**   | todo   |  High  |   M    |  0132  | Record stage 4/5 review action entries (ACT-REV/ACT-POST) in executions.jsonl | Ledger / Provenance | Stage 4/5 never append ACT-REV/ACT-FIND/ACT-POST in holon-coherence (0 matches vs 159 in holon-agentic-coder); fix the writer or correct AGENTS.md rule 14. No backfill.                                                    |
| **P1**   | todo   | Medium |   M    |  0129  | Expose plain mitmweb web interface to inspect live requests and responses     | CLI / Telemetry     | Exposes the plain mitmweb inspection UI by default in holon-coherence start with port fallback, and prints every endpoint (proxy, Coherence dashboard, mitmweb + token) from status, metrics and holon flow --token-reduce. |
| **P2**   | todo   |  Low   |   S    |  0133  | Use a monotonic clock for the proxy readiness poll deadline                   | CLI / Reliability   | wait_for_proxy_ready() bounds its poll with a wall-clock time.time() deadline while sibling loops use time.monotonic(); NTP slew can stall or short-circuit cold-start readiness.                                           |

---

## Recommended Next Execution Sequence

1. **Record stage 4/5 review action entries (ACT-REV/ACT-POST) in executions.jsonl (Bean 0132)**:
   - Stage 4/5 never append ACT-REV/ACT-FIND/ACT-POST in holon-coherence (0 matches vs 159 in holon-agentic-coder); fix
     the writer or correct AGENTS.md rule 14. No backfill.
2. **Expose plain mitmweb web interface to inspect live requests and responses (Bean 0129)**:
   - Exposes the plain mitmweb inspection UI by default in holon-coherence start with port fallback, and prints every
     endpoint (proxy, Coherence dashboard, mitmweb + token) from status, metrics and holon flow --token-reduce.
3. **Use a monotonic clock for the proxy readiness poll deadline (Bean 0133)**:
   - wait_for_proxy_ready() bounds its poll with a wall-clock time.time() deadline while sibling loops use
     time.monotonic(); NTP slew can stall or short-circuit cold-start readiness.
