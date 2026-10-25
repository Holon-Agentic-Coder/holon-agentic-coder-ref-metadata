# Holon Ecosystem Bean Triage and Prioritisation Matrix

**Last Updated:** 2026-10-22 15:15:00 UTC

## Executive Summary

Since the previous triage checkpoint on 2026-10-20, the Holon ecosystem has progressed through automated Holon flow
cycles, multi-agent consensus review loops, and infrastructure hardening.

- **Total Tracked Beans**: 142 (excluding template)
- **Completed**: 128 (89.9%)
- **Scrapped / Superseded**: 2 (1.4%)
- **Active / Todo**: 12 (8.5%)

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
12. **Ecosystem install refresh and flow-integrity audit (2026-10-22)**:
    - Rebuilt all nine container images via Buildx Bake and reinstalled `holon` / `holon-coherence` editable from
      `origin/main` (`holon-agentic-coder` `3bef6f7`, `holon-coherence` `29b7e50`).
    - Attempted the three remaining beans through the Holon flow and recorded why they could not complete: Bean 0134
      (the unified `holon flow` runner dispatches no role agent and opened the now-closed empty PR #89), Bean 0135
      (mergeability verdict fabricated from a missing ref), and a full inventory of unusable agent runners.
    - Logged Beans 0137-0140 against the root causes: hard-coded default runner, single-response artifact authoring,
      absent turn/stage budgets, and an undisclosed sandbox output ceiling. Declared `maxTokens` explicitly in the host
      pi config so the cap is visible.
    - Contained the credential leak in CLI command echoes (Bean 0136): token rotated, old value verified rejected.

---

## Active Beans Triage and Prioritisation Matrix

| Priority | Status      | Impact | Sizing | Bean # | Title                                                                                               | Domain                      | Dependencies / Notes                                                                                                                                                                  |
| :------- | :---------- | :----: | :----: | :----- | :-------------------------------------------------------------------------------------------------- | :-------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **P1**   | in-progress |  High  |   M    | 0132   | Record stage 4/5 review action entries (ACT-REV/ACT-POST) in executions.jsonl                       | Ledger / Provenance         | Stage 1 pushed (`I-1792635019-.../_`); Stage 2 blocked purely on a coding-agent credential -- GitHub side verified working after the Bean 0136 rotation.                              |
| **P1**   | todo        |  High  |   M    | 0134   | `holon flow` dispatches no role agent and produces empty-diff PRs                                   | Holon Flow / CLI            | Stub plan + empty execute commit; opened empty PR #89 (closed). Breaks the runner/manual equivalence AGENTS.md advertises.                                                            |
| **P1**   | todo        |  High  |   S    | 0136   | Redact the GitHub token printed in CLI command echoes                                               | Security / Logs             | Token rotated and old value verified `401` on 2026-10-22; **code fix outstanding** -- every `holon plan`/`execute` re-leaks the current token.                                        |
| **P1**   | todo        |  High  |   M    | 0137   | Default runner must be inherited from the harness agent                                             | CLI / Agent Runner          | `antigravity-agent` hard-coded at `cli.py:1159/1189/1391/1777` and `flow.py:164/232/305`; needs precedence + `HOLON_AGENT` + pre-flight credential probe.                             |
| **P1**   | todo        |  High  |   M    | 0138   | Write plans/ and execution artifacts incrementally, not in one final response                       | Planner / Prompts           | `planner.py` captures one `pi -p` stdout; a `stopReason=length` final message (cap measured at 16384 output tokens) discarded a 17-minute run.                                        |
| **P1**   | todo        |  High  |   M    | 0139   | Per-turn and per-stage wall-clock budgets with stall detection                                      | Reliability                 | Proposal: turn `X=5 min`, stall 90s; stage ceilings 10/35/45/15/10 min sized from merged-run commit archaeology.                                                                      |
| **P1**   | todo        |  High  |   M    | 0129   | Expose plain mitmweb web interface to inspect live requests and responses                           | CLI / Telemetry             | Bundled with 0133 in `todo/intent-0129-0133-coherence-mitmweb-monotonic.json`; worktree `flow-0129-0133-coherence-mitmweb-monotonic-clock` prepared.                                  |
| **P1**   | todo        |  High  |   L    | 0142   | Benchmark Qwen3.8-27B-JANG_4D (dense) vs Qwen3.8-Flash-Next-JANG_4M (MoE) on real agentic workloads | Model Selection / Benchmark | Quality gate before any speed quote; workloads from real ledger/intents/plans/merged PRs (zero synthetic data, AGENTS.md item 10); picks the flow's default model for 0132/0129/0133. |
| **P2**   | todo        | Medium |   S    | 0140   | `local_llm` must carry an explicit `maxTokens` into the sandbox config                              | Sandbox / Local LLM         | The generator copies host entries verbatim, so an omitted `maxTokens` becomes an undisclosed cap in the container. Host config now declares 16384.                                    |
| **P2**   | todo        | Medium |   S    | 0135   | `check_pr_mergeability` reports CONFLICTING/DIRTY for a missing branch ref                          | Review Loop / Git           | `git merge-tree --write-tree <missing>` exits 1 and is read as a conflict, producing a false "CI SIGNAL SUPPRESSED" halt.                                                             |
| **P2**   | todo        | Medium |   M    | 0141   | Tune vmlx prefill and decode levers for both Qwen3.8 models, crash-safe                             | vmlx / Performance          | Engine launch flags (prefill step/batch, completion batch, timeout); crash-safe procedure. 0142 holds these constant or varies them deliberately.                                     |
| **P2**   | todo        |  Low   |   S    | 0133   | Use a monotonic clock for the proxy readiness poll deadline                                         | CLI / Reliability           | Bundled with 0129; `start.py:154`/`:159` still use `time.time()` at `29b7e50`.                                                                                                        |

---

## Recommended Next Execution Sequence

**GitHub side is healthy as of 2026-10-22 09:30 UTC.** The `gh` token Bean 0136 leaked was rotated by the maintainer and
verified superseded (old value now returns `401 Bad credentials`; `gh api user` and repository reads succeed), PR #89 is
`CLOSED`, and `holon` needs no reconfiguration since `find_github_token()` (`cli.py:125-138`) calls `gh auth token` per
run. Only the scopes were left as-is (`admin:public_key` still present -- optional next refresh:
`gh auth refresh --scopes repo,read:org,gist`).

**Remaining gate:** no agent runner on this host can execute a flow stage -- `antigravity-agent` is at individual quota
(resets ~2026-10-24), `claude` is not logged in, `codex` has a used refresh token, `opencode` has an expired key, and
`pi-agent` on the host-local vMLX gateway died on a single-response output cap (Beans 0138/0140). `maxTokens` is now
declared explicitly in `~/.pi/agent/models.json` (16384, the value pi already sent), which makes the cap visible but
does not raise it, so the runner choice must still come from a re-authenticated or non-exhausted credential.

1. **Re-authenticate one coding-agent runner (maintainer)**: `claude` login, or `codex` logout/login to clear the
   us/mode1l refresh token, or a fresh OpenCode key -- any one of these unblocks Bean 0132 immediately. The `gh` token
   step is already complete.
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
