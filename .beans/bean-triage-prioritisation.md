# Holon Ecosystem Bean Triage and Prioritisation Matrix

**Last Updated:** 2026-10-22 00:34:55 UTC

## Executive Summary

Since the previous triage checkpoint on 2026-10-20, the Holon ecosystem has progressed through automated Holon flow
cycles, multi-agent consensus review loops, and infrastructure hardening.

- **Total Tracked Beans**: 140 (excluding template)
- **Completed**: 128 (91.4%)
- **Scrapped / Superseded**: 2 (1.5%)
- **Active / Todo**: 10 (7.1%)

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

| Priority | Status      | Impact | Sizing | Bean # | Title                                                                         | Domain              | Dependencies / Notes                                                                                                                                                                                  |
| :------- | :---------- | :----: | :----: | :----: | :---------------------------------------------------------------------------- | :------------------ | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **P1**   | in-progress |  High  |   M    |  0132  | Record stage 4/5 review action entries (ACT-REV/ACT-POST) in executions.jsonl | Ledger / Provenance | Stage 1 done (`I-1792635019-.../_` pushed). Stage 2 blocked: no agent runner on this host has usable credentials.                                                                                     |
| **P1**   | todo        |  High  |   M    |  0134  | `holon flow` dispatches no role agent and produces empty-diff PRs             | Holon Flow / CLI    | Runner orchestrates branches/ledger/PR/review/calibration but authors nothing (stub plan, empty execute commit). Caused empty PR #89 (closed). Blocks the documented runner equivalence in AGENTS.md. |
| **P1**   | todo        |  High  |   S    |  0136  | Redact the GitHub token printed in CLI command echoes                         | Security / Logs     | `holon plan`/`execute` echo `GITHUB_TOKEN` and `git clone https://x-access-token:<tok>@...`. Rotate the exposed `gho_...` token first; then reuse `redact_text()`.                                    |
| **P1**   | todo        |  High  |   M    |  0129  | Expose plain mitmweb web interface to inspect live requests and responses     | CLI / Telemetry     | Bundled with 0133 in `todo/intent-0129-0133-coherence-mitmweb-monotonic.json`; worktree prepared. Blocked on runner credentials.                                                                      |
| **P2**   | todo        |  Low   |   S    |  0133  | Use a monotonic clock for the proxy readiness poll deadline                   | CLI / Reliability   | Bundled with 0129. `start.py:154`/`:159` still use `time.time()` on `origin/main` (`29b7e50`).                                                                                                        |
| **P2**   | todo        | Medium |   S    |  0135  | `check_pr_mergeability` reports CONFLICTING/DIRTY for a missing branch ref    | Review Loop / Git   | `git merge-tree --write-tree <missing>` exits 1 and is read as a conflict, producing a false "CI SIGNAL SUPPRESSED" halt.                                                                             |

---

## Recommended Next Execution Sequence

**Gate for all flow work:** no agent runner on this host can currently execute a flow stage -- `antigravity-agent` is at
individual quota (resets ~2026-10-24), `claude` is not logged in, `codex` has a used refresh token, `opencode` has an
expired key, and `pi-agent` on the host-local vMLX gateway died on a single-response output cap (Bean 0138/0140). The
`maxTokens` field is now declared explicitly in `~/.pi/agent/models.json`, which makes the cap visible but does not
raise it, so the runner choice still has to come from a re-authenticated or non-exhausted credential.

1. **Rotate and re-authenticate (maintainer)**: `gh auth refresh --scopes repo,read:org,gist` to rotate the token that
   Bean 0136 leaked and to drop `admin:public_key`, then re-auth one coding-agent runner.
2. **Bean 0137**: inherit the runner from the harness agent and add the pre-flight credential probe, so an unusable
   runner fails in seconds instead of minutes and the ledger names the runner that actually authored the work.
3. **Beans 0138 + 0139 + 0140** (one coherence-independent package on `holon-agentic-coder`): incremental artifact
   writes, turn/stage budgets with stall detection, and an explicit `maxTokens` in the generated sandbox config.
   Together they make the local-model route usable rather than heroic.
4. **Bean 0132**: resume at Stage 2 in `apps/holon-agentic-coder/flow-0132-stage-4-5-ledger-actions` against
   `I-1792635019-flow-stage-4-5-ledger-action-entries/_`.
5. **Bean 0134**: make `holon flow` dispatch role agents or refuse to author, and fail an empty execution diff instead
   of recording success.
6. **Beans 0129 + 0133**: run the prepared combined coherence intent; its ledger diff also supplies the empirical
   coherence-side verification Bean 0132 asks for.
7. **Bean 0135**: fix the missing-ref mergeability verdict so review-loop halts name the real cause.
