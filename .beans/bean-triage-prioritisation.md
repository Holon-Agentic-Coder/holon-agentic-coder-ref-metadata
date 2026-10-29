# Holon Ecosystem Bean Triage and Prioritisation Matrix

**Last Updated:** 2026-10-29 03:35:56 UTC

## Executive Summary

Since the 2026-10-22 checkpoint, every bean that was active then and blocked on a runner has gone through the full
5-stage Holon flow and been merged by the maintainer:

- holon-agentic-coder PRs #90, #91, #93, #94, #95 and #96
- holon-coherence PR #27

Concurrent flows on overlapping files (#94, #95 and #96 all changed `flow.py` and `cli.py`) forced repeated syncs and
re-reviews: 141 review-loop passes from the first sync onward, about 10M+ tokens. Beans 0151 and 0152 address that, and
overlapping flows now run one after another.

- **Total Tracked Beans**: 182 (excluding template)
- **Completed**: 144 (79.1%)
- **Scrapped / Superseded**: 2 (1.1%)
- **Active**: 36 (19.8%), of which 1 are in progress and 35 are todo

**2026-10-26:** the first full claude-agent `holon flow` runs (Beans 0151, 0159) exposed seven defects in the flow
itself. They are logged as Beans 0157-0162, and Bean 0144 was raised to critical after its fabricated approval reached
GitHub. Bean 0156 starts the investigation into moving issue tracking from harness beans to beads inside each target,
ahead of deprecating this harness.

**2026-10-28:** Bean 0168 (PR #99) cut CI test time through the full flow: pytest-xdist, hermetic test git and
per-worker template repositories. Real CI pytest time fell 2.5x on macOS (382 s to 153 s), 2.0x on ubuntu (242 s to 123
s) and 1.6x for Workspace survival (417 s to 258 s). It converged in 8 review iterations and was merged (`0e54457`).
New: Bean 0175 (token-scope pre-flight), Bean 0176 (pytest only) and Bean 0177 (architecture and code-principles
research that spawns action beans).

**2026-10-29:** Bean 0144 was delivered as three sequential flows (PRs #100, #101 and #102, all merged): Stage 4 now
fails closed and is decided only by a real reviewer ensemble. Bean 0179 routes those reviewer turns through the role
container. PR #103 (Bean 0180, documentation only) nests sub-intent branches under the node that decided the split; it
was merged (`e187393`) after 11 review iterations. The maintainer settled its five open questions (merge into the
deciding plan or execution branch, nested PRs automatic), which a follow-up docs PR and Bean 0161 implement. New: Bean
0178 (repeated test runs only for performance work), Bean 0179 and Bean 0181 (`/_` only on branch refs).

Later on 2026-10-29, Bean 0143 went through the full flow from `main`, with a bootstrap build of the fix branch for the
flow's own claude agents. PR #104 is approved after 3 review iterations, calibrated and awaiting merge; `holon` and
`holon-coherence` are reinstalled from `main` once it merges. New: Bean 0182, a long-running GitHub event watcher whose
CI and merge events drive harness actions at zero token cost.

---

## Key Milestones Completed (Beans 0080 – 0168)

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

14. **First claude-agent `holon flow` runs and the defects they surfaced (2026-10-26)**:
    - The claude runner fix (Bean 0143) was rebased onto `main`, installed as `holon` and baked into
      `holon/agent-claude`. Role containers run the image's code, not the host install.
    - Bean 0151 reached a sound plan (EV 19.82). Stage 3 then fabricated two placeholder sub-intents and halted for a
      human (Bean 0159). Maintainer decision: no stage before merge may halt for human review.
    - Bean 0159 ran intent -> plan -> execute -> review -> calibrate (PR #97). On the way it hit the following:
      - Bean 0157: the mitmproxy sidecar auto-starts because its image exists, and role containers cannot reach it.
      - Bean 0158: every run reorders `intents.jsonl`, which also breaks Stage 4 checkout.
      - Bean 0160: CI polling consumes review iterations and is then reported as test failures.
      - Bean 0144: the native review loop posted a fabricated "3-Agent Ensemble" approval to GitHub.
      - Bean 0162: Stage 5 commits a report that fails the `hygiene` check.
    - PR #97 then went through the real harness `pr-review-loop` (3 blind reviewers plus a resolver per iteration). Nine
      iterations applied ledger, design, test-coverage and parser fixes. Decomposed-child aggregation was deferred to
      Bean 0161.

15. **Bean 0159 merged via PR #97 after a 33-iteration harness review loop (2026-10-27)**:
    - The intent's entropy budget now reaches the executor. Sub-intents are never invented, and Stage 3 never halts for
      a human. Decomposed children run autonomously, with a depth cap and `{parent}--{n}-{slug}` branches.
    - The review loop found one Important defect late (child branches colliding when created in the same second). It
      also moved the suite-rerunning canary out of the unit job, bringing macOS unit back under 10 minutes, and swept
      the code with mutation testing until none survived.
    - It did not converge. The diff grew about 3x under review, and Nits never reached zero across three fresh
      reviewers. The maintainer merged at iteration 33 with a final COMMENT review. Residual work is in Beans 0169
      (Nits) and 0170 (loop convergence).
    - Also merged: PR #98 (Bean 0165, restoring PR #88's unpushed review ledger rows).
16. **Faster CI tests via the full flow (Bean 0168 / PR #99, 2026-10-28)**:
    - pytest-xdist, hermetic test git and per-worker template repositories: CI pytest time 2.5x faster on macOS, 2.0x on
      ubuntu and 1.6x for Workspace survival. Also closed Bean 0167 (deterministic turn-supervisor test, hostile
      `core.hooksPath`).
17. **Real, fail-closed Stage 4 review (Bean 0144 / PRs #100, #101, #102, 2026-10-28)**:
    - PR-number targets resolve to the head branch and SHA; clone, diff and post failures never approve.
      `review_ensemble.py` runs N independent reviewers with strict trailers and unanimity. Stage 4 is decided only by
      that ensemble plus mergeable and green CI; the fabricated report is gone.
    - The planner's first attempt split the intent into three dependent sub-intents that could not build on each other
      (Bean 0161). It was re-run as three sequential root flows; the split run's branches stay on `origin` for audit.

---

## Active Beans Triage and Prioritisation Matrix

| Priority | Status      | Impact | Sizing | Bean # | Title                                                                                           | Domain                   | Dependencies / Notes                                                                                                                                                                                       |
| :------- | :---------- | :----: | :----: | :----- | :---------------------------------------------------------------------------------------------- | :----------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **P0**   | todo        |  High  |   M    | 0179   | Route Stage 4 reviewer turns through the `review-loop` role container                           | Review Loop              | Follow-up to 0144 (PR #102 refuses host reviewer turns, fail closed). Until it lands, Stage 4 runs through the harness `pr-review-loop` skill.                                                             |
| **P0**   | todo        |  High  |   S    | 0158   | A flow run reorders existing rows of the append-only `intents.jsonl`                            | Ledger / Holon Flow      | Breaks Stage 4 checkout on every unattended run. Workaround: `git restore` the file, then `--from-stage review`.                                                                                           |
| **P0**   | todo        |  High  |   S    | 0160   | Review loop burns its iteration budget polling pending CI, then reports test failures           | Review Loop / CI         | Every unattended Stage 4 runs out of iterations before review. Workaround: wait for CI, then resume.                                                                                                       |
| **P0**   | todo        |  High  |   L    | 0151   | Planner estimates the touch set; overlapping concurrent flows are blocked                       | Holon Flow / Concurrency | Unblocked by 0159 (#97 merged). Re-plan on the new `main`; land 0149 first. Must handle `{parent}--{n}-{slug}` child branches.                                                                             |
| **P0**   | todo        |  High  |   M    | 0171   | Stage 3 budget breach commits the notes and ledger but discards the executor's code changes     | Holon Flow / Executor    | Lost a 45-minute Stage 3 run for Bean 0168. Salvage must keep the code diff.                                                                                                                               |
| **P1**   | todo        |  High  |   S    | 0175   | Check GitHub token scopes before Stage 3 when the plan touches workflow files                   | Holon Flow / GitHub      | A 55-minute Stage 3 for Bean 0168 was lost to a push rejected for the missing `workflow` scope. Pairs with 0171 (keep commits on a rejected push).                                                         |
| **P1**   | todo        |  High  |   S    | 0162   | Stage 5 calibration commits a report that fails the `hygiene` Prettier check                    | Calibration / CI         | Turns every flow PR red after calibration.                                                                                                                                                                 |
| **P1**   | todo        |  High  |   S    | 0157   | `holon flow` auto-enables the mitmproxy sidecar; role containers cannot reach it                | Holon Flow / Proxy       | Workaround: `HOLON_TOKEN_REDUCE=0`. Related to 0130.                                                                                                                                                       |
| **P1**   | todo        |  High  |   M    | 0161   | Decomposed sub-intents have no flow path to `main` and do not build on each other               | Holon Flow               | Deferred from #97. Implement the 2026-10-29 rulings: nest under the deciding node, merge into the deciding plan/execution branch, nested PRs automatic, sibling slugs distinct. Docs: PR #103 + follow-up. |
| **P1**   | todo        |  High  |   M    | 0149   | Plan and execution IDs collide across concurrently planned intents                              | Provenance / Planner     | #91 and #92 shared `P-1792765112`. Prerequisite for 0151.                                                                                                                                                  |
| **P1**   | todo        |  High  |   M    | 0155   | General `HOLON_*` forwarding puts credential-shaped values on the docker argv                   | Security                 | Already on main. Default fix: send every `HOLON_*` value through the 0600 env-file.                                                                                                                        |
| **P1**   | todo        |  High  |   M    | 0148   | Redact before truncating ledger `error_context`; close `CredentialRedactor` gaps                | Security / Ledger        | Route those rows through `redact_agent_secrets`.                                                                                                                                                           |
| **P1**   | todo        | Medium |   M    | 0146   | Plans-ledger correction rows; calibration picks the right predicted metrics                     | Calibration / Ledger     | Every calibration last cycle needed a manual annotation (7 PRs).                                                                                                                                           |
| **P1**   | todo        |  High  |   L    | 0156   | Investigate moving issue tracking from harness beans to beads inside each target                | Issue Tracking           | Investigation only, no target code. Can run in parallel with any flow. Precedes deprecating the harness.                                                                                                   |
| **P1**   | todo        |  High  |   M    | 0163   | CI timing regression gate: fail builds whose duration regresses beyond a tolerance              | CI / Performance         | macOS unit already over 10 min on `main` (662 s). Baseline on a rolling median; same code varies about ±20%. Both repos.                                                                                   |
| **P1**   | todo        | Medium |   S    | 0172   | Stage and turn budgets accept an explicit 'unlimited' value, distinct from unset (default)      | Holon Flow / Config      | Workaround today: `HOLON_STAGE_BUDGET_EXECUTE_MINUTES=10080` (the 7-day maximum).                                                                                                                          |
| **P1**   | todo        |  High  |   M    | 0173   | holon loads layered .env files (specific overrides broad) that every sandbox stage inherits     | Holon Flow / Config      | Project `.env` overrides the broader `.env`. Touches `cli.py`; sequence after 0155/0148.                                                                                                                   |
| **P1**   | todo        | Medium |   M    | 0174   | Document every environment variable holon reads, in one generated and CI-checked reference      | Documentation / Config   | After 0172 and 0173, so the reference includes their variables.                                                                                                                                            |
| **P1**   | todo        |  High  |   L    | 0176   | Remove every unittest reference from holon-agentic-coder; the suite is pytest only              | Tests                    | Blocked by 0168 (#99). 59 `TestCase` classes and about 60 `unittest.mock` imports in 29 files. Runs alone: it touches most test files.                                                                     |
| **P1**   | todo        |  High  |   L    | 0177   | Research the architecture and software principles for the target repos, then spawn action beans | Architecture / Research  | Research only, parallel lane. Cohesion, intention-revealing names, low complexity, parallel-agent friendly layout. Spawns one flow-sized bean per change; reshapes 0152/0153.                              |
| **P1**   | todo        |  High  |   M    | 0182   | Persistent GitHub event watcher that emits PR and CI events and drives harness actions          | Harness / Automation     | Zero-token waits: watcher container plus event log; merges trigger cleanup and installs, CI failures the next review iteration. Guardrails: no new spending, no merges.                                    |
| **P1**   | in-progress | Medium |   S    | 0180   | Document sub-intent branches nested under the node that decided the split                       | Docs / Holon Flow        | PR #103 merged (`e187393`). Remaining: the follow-up docs PR for the five rulings (hand-authored, documentation only).                                                                                     |
| **P2**   | todo        | Medium |   M    | 0181   | Use the `/_` leaf only when referencing a git branch, never on ids                              | Holon Flow / Ledger      | `intents.jsonl` `branch` and `parent_intent_id` hold refs; migrate with readers accepting both shapes.                                                                                                     |
| **P2**   | todo        | Medium |   S    | 0178   | Prompts request repeated test runs only for performance work, N runs each under xdist           | Prompts                  | Rule 19 is in the harness; the planner and executor templates still need it.                                                                                                                               |
| **P1**   | todo        |  High  |   M    | 0170   | pr-review-loop must converge: review the increment, defer Nits on unchanged code                | Review Loop / Skills     | From PR #97 (33 iterations, diff ~3x, Nits never zero). Harness-only skill change. Do before the next long review loop.                                                                                    |
| **P1**   | todo        |  High  |   M    | 0166   | Pipeline duration dashboard for CI builds                                                       | CI / Observability       | Check org Actions performance metrics first. Shares data and baseline with 0163.                                                                                                                           |
| **P1**   | todo        |  High  |   XL   | 0152   | Audit long files; decompose oversized functions (flow.py, cli.py first)                         | Refactor / Concurrency   | `cli.main` is 1062 lines; `flow.py` is 4400+. Run only while no other flow touches those files.                                                                                                            |
| **P1**   | todo        | Medium |   S    | 0154   | Fix the flaky URL fuzz leak check that can match temp-file names                                | Tests                    | Turned #97's macOS CI red on 2026-10-26 (second occurrence). Tests only; parallel with flows that don't touch the fuzz test.                                                                               |
| **P1**   | todo        | Medium |   S    | 0164   | Plain-language documentation for entropy, Expected Value, and how they relate                   | Documentation            | Documentation only, disjoint from `flow.py`/`cli.py`, so it runs in the parallel lane. Through the Holon flow on holon-agentic-coder.                                                                      |
| **P2**   | todo        | Medium |   S    | 0169   | PR #97 residual Nits: split the pasted checkpoint test; complete git_flow §1.5 list             | Tests / Docs             | Small; touches `test_flow.py` and `git_flow.md`.                                                                                                                                                           |
| **P2**   | todo        | Medium |   XL   | 0153   | Remove comments and docstrings from all code; make it self-documenting                          | Readability              | Runs with or after 0152.                                                                                                                                                                                   |
| **P2**   | todo        | Medium |   S    | 0147   | Remove harness paths tracked in the target repositories                                         | Hygiene                  | One flow per repository. The coherence part can run in parallel. Fold into 0156's plan if beads lands first.                                                                                               |
| **P2**   | todo        |  Low   |   S    | 0150   | Flow tests write the real checkout's `action_index.db`                                          | Tests                    | Unblocked.                                                                                                                                                                                                 |
| **P2**   | todo        | Medium |   S    | 0145   | Pin holon-coherence to Python 3.13                                                              | Build / coherence        | coherence only; parallel with holon-agentic-coder flows.                                                                                                                                                   |
| **P2**   | todo        |  High  |   L    | 0142   | Real-workload benchmark: Qwen3.8-27B dense vs Flash-Next MoE                                    | Model Selection          | Real data only (AGENTS.md item 10).                                                                                                                                                                        |
| **P3**   | todo        | Medium |   M    | 0141   | Tune vmlx prefill/decode levers for both Qwen3.8 models, crash-safe                             | vmlx / Performance       | Pairs with 0142.                                                                                                                                                                                           |

---

## Recommended Next Execution Sequence

**Rule (2026-10-25):** never run concurrent flows whose touched files overlap. Nearly every holon-agentic-coder bean
touches `flow.py` or `cli.py`, so those flows run **one at a time**: merge one, then plan the next on the new `main`.
Only disjoint work runs in parallel. Bean 0151 will make the flow enforce this; Bean 0152 will bring back parallelism.

**Rule (2026-10-26):** no stage before the merge may halt for human review. The PR merge is the only human step, after
consensus review and Stage 5 calibration.

**Rule (2026-10-28):** the target suites rely solely on pytest. No new code or documentation names any other test runner
(Bean 0176 removes the existing references).

**Tooling (2026-10-29):** the installed `holon`, `holon-coherence` and every image are built from `main` (`cc4bf1b`,
which includes Bean 0143). Until 0157, 0158, 0160, 0162 and 0179 land, run flows with `HOLON_TOKEN_REDUCE=0`, restore
`intents.jsonl` before Stage 4, run Stage 4 through the harness `pr-review-loop` skill, and format the calibration
report before pushing. Set `HOLON_STAGE_BUDGET_EXECUTE_MINUTES=10080` for Stage 3 until Bean 0172 adds an explicit
unlimited value.

Sequential lane, holon-agentic-coder (flow blockers first):

1. **Bean 0143** is done (PR #104 merged, `cc4bf1b`): `holon`, `holon-coherence` and every image now come from `main`,
   so claude-agent flows no longer need a fix-branch build.
2. **Bean 0171** and **Bean 0175**: Stage 3 must never lose the executor's code (budget breach, rejected push), and
   token scopes are checked before Stage 3 starts.
3. **Bean 0179**: route Stage 4 reviewer turns through the `review-loop` role container so `holon flow` reviews on its
   own. Adopt the Bean 0170 convergence rules there.
4. **Bean 0181**: `/_` only on branch refs, ids bare (ledger field migration; readers accept both shapes).
5. **Bean 0158**, **Bean 0160**, **Bean 0162**, **Bean 0157**: the remaining flow-integrity blockers, one at a time (all
   touch `flow.py`). 0158 and 0162 both recurred on #99.
6. **Bean 0149**, then **Bean 0151**: unique IDs, then touch-set admission (re-plan 0151 on the new `main`).
7. **Bean 0161**: nested sub-intent branches per the maintainer's 2026-10-29 rulings (merge into the deciding plan or
   execution branch, nested PRs automatic), chaining and resume safety.
8. **Bean 0155**, then **Bean 0148**: credential-redaction gaps (both touch `cli.py`).
9. **Bean 0172**, **Bean 0173**, then **Bean 0174**: unlimited budgets, layered `.env`, then the env-var reference.
10. **Bean 0146**: calibration reads the correct predicted metrics.
11. **Bean 0176**: pytest-only conversion of every test file (after #99; touches most test files, so it runs alone).
12. **Bean 0152**, then **Bean 0153**: decomposition and module split, then self-documenting code, shaped by the action
    beans that Bean 0177 spawns.

Parallel lane (disjoint files):

- **Bean 0177** (architecture and code-principles research, no target code). Start now; its spawned action beans re-plan
  0152/0153 and set the file layout that keeps parallel agents off the same files.
- **Bean 0170** (review-loop convergence rules, harness-only). Do it before the next long review loop.
- **Bean 0180**: the follow-up docs PR applying the five rulings (documentation only; PR #103 is merged).
- **Bean 0182** (GitHub event watcher, harness-only): replaces per-task polling loops; do it before the next long review
  loop, alongside 0170.
- **Bean 0178** (planner and executor prompt rule for repeated test runs; prompts only).
- **Bean 0163** and **Bean 0166** (CI timing gate and duration dashboard; workflows and observability only).
- **Bean 0169** (PR #97 residual Nits; small, `test_flow.py` and `git_flow.md`). Check overlap with the lane above.
- **Bean 0156** (beads investigation, no target code). Its outcome decides how 0147 and the harness retirement proceed.
- **Bean 0145** (holon-coherence) and the holon-coherence half of **Bean 0147**.
- **Bean 0154** and **Bean 0150** (tests only). Check their touch sets against the lane above first.
- **Beans 0142 and 0141** (benchmarking and tuning, no code flow).
- **Bean 0164** (plain-language entropy/EV explainer, documentation only, disjoint from `flow.py`/`cli.py`).
