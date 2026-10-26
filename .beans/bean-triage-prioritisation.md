# Holon Ecosystem Bean Triage and Prioritisation Matrix

**Last Updated:** 2026-10-26 02:34:36 UTC

## Executive Summary

Since the 2026-10-22 checkpoint, every bean that was active then and blocked on a runner has gone through the full
5-stage Holon flow and been merged by the maintainer:

- holon-agentic-coder PRs #90, #91, #93, #94, #95 and #96
- holon-coherence PR #27

Concurrent flows on overlapping files (#94, #95 and #96 all changed `flow.py` and `cli.py`) forced repeated syncs and
re-reviews: 141 review-loop passes from the first sync onward, about 10M+ tokens. Beans 0151 and 0152 address that, and
overlapping flows now run one after another.

- **Total Tracked Beans**: 155 (excluding template)
- **Completed**: 138 (89.0%)
- **Scrapped / Superseded**: 2 (1.3%)
- **Active**: 15 (9.7%), of which 1 is in progress and 14 are todo

---

## Key Milestones Completed (Beans 0080 – 0140)

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

13. **Five-stage flow cycle on every runner-blocked bean (2026-10-23 to 2026-10-26)**:
    - All seven PRs were driven with the `claude-agent` runner (`claude-opus-5-5`) through intent, plan, execute, the
      3-agent review loop and Stage 5 calibration. Every consensus review was posted; merging stayed with the
      maintainer.
    - `0135` (#91): a missing branch ref reports `MISSING_REF`, not a false conflict.
    - `0129` + `0133` (holon-coherence #27): mitmweb inspector, plus a monotonic proxy readiness deadline.
    - `0132` (#90): Stage 4/5 `ACT-*` rows in `executions.jsonl`, plus a calibration success gate.
    - `0137` (#93): the runner is inherited from the harness, with a pre-flight credential probe.
    - `0136` (#96, superseding #92 after a plan-ID collision): canonical redaction module; credentials off the docker
      argv through a 0600 env-file; `redact_cli_error`; URL-message fuzz tests.
    - `0134` (#95): `holon flow` dispatches role agents. Empty diffs are refused fail-closed, unmeasured tests are never
      counted as a pass, and tests have a `gh` write guard.
    - `0138` + `0139` + `0140` (#94): incremental artefacts, turn/stage budgets handed to every container, an explicit
      model envelope, a unified `holon doctor`, a validated `models.json` loader, and malformed-config and UTF-8
      hardening.
    - Every calibration report read its predicted metrics from the wrong `plans.jsonl` row. Each got an annotation
      commit (Bean 0146 has the table).

---

## Active Beans Triage and Prioritisation Matrix

| Priority | Status      | Impact | Sizing | Bean # | Title                                                                                   | Domain                   | Dependencies / Notes                                                                                                                             |
| :------- | :---------- | :----: | :----: | :----- | :-------------------------------------------------------------------------------------- | :----------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------- |
| **P0**   | todo        |  High  |   L    | 0151   | Planner estimates the touch set; overlapping concurrent flows are blocked               | Holon Flow / Concurrency | Evidence: 141 post-sync review passes (~10M+ tokens). Needs 0149 for reliable in-flight IDs. Until it lands, follow the sequential rule by hand. |
| **P1**   | todo        |  High  |   M    | 0149   | Plan and execution IDs collide across concurrently planned intents                      | Provenance / Planner     | #91 and #92 shared `P-1792765112`. Prerequisite for 0151.                                                                                        |
| **P1**   | todo        |  High  |   M    | 0155   | General `HOLON_*` forwarding puts credential-shaped values on the docker argv           | Security                 | Already on main. Default fix: send every `HOLON_*` value through the 0600 env-file.                                                              |
| **P1**   | todo        |  High  |   M    | 0148   | Redact before truncating ledger `error_context`; close `CredentialRedactor` gaps        | Security / Ledger        | #90 and #96 have merged, so it is unblocked. Route those rows through `redact_agent_secrets`.                                                    |
| **P1**   | todo        | Medium |   M    | 0146   | Plans-ledger correction rows; calibration picks the right predicted metrics             | Calibration / Ledger     | Every calibration this cycle needed a manual annotation (7 PRs).                                                                                 |
| **P1**   | todo        |  High  |   M    | 0144   | `holon review-loop <PR number>` clones a nonexistent branch and still reports consensus | Review Loop              | Also: the empty-diff guard runs only with `--auto-pr` (#95 review).                                                                              |
| **P1**   | in-progress |  High  |   S    | 0143   | Claude runner passes the permission bypass as CLI parameters                            | Agent Runner             | Maintainer's bean.                                                                                                                               |
| **P1**   | todo        |  High  |   XL   | 0152   | Audit long files; decompose oversized functions (flow.py, cli.py first)                 | Refactor / Concurrency   | `cli.main` is 1062 lines; `flow.py` is 4434. Decompose, then split. Run only while no other flow touches those files.                            |
| **P2**   | todo        | Medium |   XL   | 0153   | Remove comments and docstrings from all code; make it self-documenting                  | Readability              | Covers every language. `docs/` and READMEs are out of scope. Runs with or after 0152.                                                            |
| **P2**   | todo        | Medium |   S    | 0154   | Fix the flaky URL fuzz leak check that can match temp-file names                        | Tests                    | Tests only. Can run in parallel with any flow that doesn't touch `test_url_message_fuzz.py`.                                                     |
| **P2**   | todo        | Medium |   S    | 0147   | Remove harness paths tracked in the target repositories                                 | Hygiene                  | One flow per repository. The coherence part can run in parallel with holon-agentic-coder work.                                                   |
| **P2**   | todo        |  Low   |   S    | 0150   | Flow tests write the real checkout's `action_index.db`                                  | Tests                    | #95 has merged, so it is unblocked.                                                                                                              |
| **P2**   | todo        | Medium |   S    | 0145   | Pin holon-coherence to Python 3.13                                                      | Build / coherence        | coherence only, so it can run in parallel with holon-agentic-coder flows.                                                                        |
| **P2**   | todo        |  High  |   L    | 0142   | Real-workload benchmark: Qwen3.8-27B dense vs Flash-Next MoE                            | Model Selection          | Real data only (AGENTS.md item 10).                                                                                                              |
| **P3**   | todo        | Medium |   M    | 0141   | Tune vmlx prefill/decode levers for both Qwen3.8 models, crash-safe                     | vmlx / Performance       | Pairs with 0142.                                                                                                                                 |

---

## Recommended Next Execution Sequence

**Rule (2026-10-25):** never run concurrent flows whose touched files overlap. Nearly every holon-agentic-coder bean
touches `flow.py` or `cli.py`, so those flows run **one at a time**: merge one, then plan the next on the new `main`.
Only disjoint work runs in parallel (holon-coherence-only beans, tests-only beans, non-code benchmarking). Bean 0151
will make the flow enforce this; Bean 0152 will bring back parallelism.

**Tooling:** `holon` and `holon-coherence` were reinstalled (editable) from `main` on 2026-10-26, and all images were
rebuilt. The installed `holon` therefore includes #90–#96, and future calibrations no longer start from a stale build.
The calibration row bug itself remains until Bean 0146.

Sequential lane, holon-agentic-coder:

1. **Bean 0149**: unique plan and execution IDs. This is a prerequisite for 0151.
2. **Bean 0151**: touch-set estimation, plus the hard admission block on overlap.
3. **Bean 0155**, then **Bean 0148**: close the remaining credential-redaction gaps. Both touch `cli.py`, so run them in
   order.
4. **Bean 0146**: calibration reads the correct predicted metrics; correction rows.
5. **Bean 0144**: the review loop with PR-number targets, and the empty-diff guard regardless of `--auto-pr`.
6. **Bean 0152**, then **Bean 0153**: decomposition and module split, then self-documenting code. Land these while no
   other flow PR is open on the same files.

Parallel lane (disjoint files):

- **Bean 0145** (holon-coherence) and the holon-coherence half of **Bean 0147**.
- **Bean 0154** and **Bean 0150** (tests only). Check their touch sets against the lane above first.
- **Beans 0142 and 0141** (benchmarking and tuning, no code flow).
