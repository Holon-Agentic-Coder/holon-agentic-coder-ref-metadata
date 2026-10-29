# Holon Ecosystem Bean Triage and Prioritisation Matrix

**Last Updated:** 2026-10-29 23:29:20 UTC

## Executive Summary

Since the 2026-10-22 checkpoint, every bean that was active then and blocked on a runner has gone through the full
5-stage Holon flow and been merged by the maintainer:

- holon-agentic-coder PRs #90, #91, #93, #94, #95 and #96
- holon-coherence PR #27

Concurrent flows on overlapping files (#94, #95 and #96 all changed `flow.py` and `cli.py`) forced repeated syncs and
re-reviews: 141 review-loop passes from the first sync onward, about 10M+ tokens. Beans 0151 and 0152 address that, and
overlapping flows now run one after another.

- **Total Tracked Beans**: 210 (excluding template)
- **Completed**: 152 (72.4%)
- **Scrapped / Superseded**: 2 (1.0%)
- **Active**: 56 (26.7%), of which 3 are in progress and 53 are todo

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
flow's own claude agents. PR #104 was approved after 3 review iterations, calibrated and merged (`cc4bf1b`), and `holon`
and `holon-coherence` were reinstalled from `main`. Five further `holon-agentic-coder` flows then completed and merged:
**Bean 0178** (PR #105, `c9825b8`: repeated test runs only for performance work under xdist, plus step-by-step executor
commits), **Bean 0164** (PR #106, `956b4fd`: plain-language entropy and EV explainer), **Bean 0154** (PR #107,
`81a12ee`: URL delimiter fuzz leak check ignores random temp paths), **Bean 0171** (PR #108, `c7dfd5e`: Stage 3 failure
salvage commits partial code and resumes from `failed_partial_head`), and the `holon-agentic-coder` half of **Bean
0163** (PR #109, `993b686`: CI timing regression gate on every workflow job). On `holon-coherence`, three flows ran in
parallel: **Bean 0145** (PR #28: pin Python 3.13, 3/3 ensemble approved, calibrated and merged as `0547eb4`), the
coherence half of **Bean 0147** (PR #29: remove harness path/task-id leaks, merged as `68fdf67` before its consensus
review was posted; post-merge follow-up PR #31 merged as `b52c7e1`), and the coherence half of **Bean 0163** (PR #30: CI
timing gate, calibrated and merged as `6d9dae7` with one Important and two Nit findings still open, carried by Bean
0184). PR #108 merged before its consensus review and calibration. New: **Bean 0182** (persistent GitHub event watcher)
and **Bean 0183** (every flow stage and engine bookkeeping step runs in its own sandboxed clone with no host checkout).

Also through the flow on 2026-10-29, both reviewed and calibrated: PR #110 (Bean 0180 follow-up docs for the five
sub-intent rulings, merged as `85ef122`) and PR #111 (Bean 0158 pure-append ledger writes, merged as `8c9ff4d`). Both
beans await closure. New: **Bean 0210** (five documents PR #110 left on the old sub-intent rules).

**Bean 0177 (architecture research) completed:** measured `flow.py` 5,157 lines (7 of the 16 flow PRs #94-#109 touched
it), `cli.main` 1,097 lines (CC 114), `executor.main` 798 lines (CC 178), and 56 + 38 functions over CC 10. It spawned
Beans 0185-0209: lint gates first (0185, 0186), then move-only splits that remove the shared files (0187, 0188, 0203,
0204), then per-module decomposition lanes that can run in parallel. The maintainer ruled that holon-coherence owns
token reduction (Bean 0200).

---

## Key Milestones Completed (Beans 0080 – 0184)

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
18. **Claude permission bypass, prompt rules, entropy/EV docs, fuzz test fix, Stage 3 code salvage, and CI timing gate
    (Beans 0143, 0178, 0164, 0154, 0171, 0163 / PRs #104–#109, 2026-10-29)**:
    - `0143` (#104, `cc4bf1b`): Claude runner passes
      `--allow-dangerously-skip-permissions --permission-mode bypassPermissions` as CLI parameters and renders planner
      placeholders in a single regex pass; `holon`, `holon-coherence` and all agent images were rebuilt from `main`.
    - `0178` (#105, `c9825b8`): planner and executor prompt templates request repeated test runs only for performance
      work under `pytest-xdist` (`-n auto --dist worksteal`) and instruct executors to commit step by step.
    - `0164` (#106, `956b4fd`): added plain-language entropy and Expected Value documentation in
      `docs/metrics-explained.md` linked from `docs/metrics.md`.
    - `0154` (#107, `81a12ee`): fixed the flaky URL delimiter fuzz leak check so random `--env-file` temporary paths
      cannot trigger false-positive secret leak failures.
    - `0171` (#108, `c7dfd5e`): Stage 3 failure and budget-breach salvage now commits partial code changes to the
      execution branch, emits a redacted format-patch on a refused push (with size caps and
      private-key/credential/env-file exclusions), and resumes Stage 3 from `failed_partial_head`.
    - `0163` (`holon-agentic-coder` half, #109, `993b686`): added the CI timing regression gate across all workflow jobs
      (rolling-median baseline, per-test offender reporting, hard ceiling, and auditable override).
19. **holon-coherence flows and the architecture research (Beans 0145, 0163, 0184, 0177, 2026-10-29)**:
    - `0145` (holon-coherence #28, `0547eb4`): pinned holon-coherence to Python 3.13.
    - `0163` (`holon-coherence` half, #30, `6d9dae7`): CI timing regression gate on every holon-coherence workflow; with
      #109 this closes Bean 0163.
    - `0184` (holon-coherence #32, `cefebe3`): fixed the residual #30 review findings (blank `--pr-number`,
      range-checked `--baseline-count` and `--test-limit`); the claimed `issues: read` Important was refuted with
      evidence.
    - `0177` (research, no target code): measured the hot spots in both targets and spawned Beans 0185-0209 with a
      migration order: lint gates, move-only splits, then parallel decomposition lanes.

---

## Active Beans Triage and Prioritisation Matrix

| Priority | Status      | Impact | Sizing | Bean # | Title                                                                                            | Domain                    | Dependencies / Notes                                                                                                                                                                                                                                    |
| :------- | :---------- | :----: | :----: | :----- | :----------------------------------------------------------------------------------------------- | :------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **P0**   | todo        |  High  |   M    | 0179   | Route Stage 4 reviewer turns through the `review-loop` role container                            | Review Loop               | Follow-up to 0144 (PR #102 refuses host reviewer turns, fail closed). Until it lands, Stage 4 runs through the harness `pr-review-loop` skill.                                                                                                          |
| **P0**   | todo        |  High  |   L    | 0183   | Every flow stage works in its own sandboxed clone; `holon flow` needs no host checkout           | Holon Flow / Sandbox      | Stages 1-3 already clone in-container; move checkpoint, engine git checks and Stage 5 calibration into sandboxed clones so concurrent flows never share or require a host worktree. Pairs with 0179, 0149, 0151.                                        |
| **P0**   | in-progress |  High  |   S    | 0158   | A flow run reorders existing rows of the append-only `intents.jsonl`                             | Ledger / Holon Flow       | PR #111 merged (`8c9ff4d`) after review and calibration; close the bean. Until `holon` is reinstalled from `main`, restore `intents.jsonl` to main's rows plus the new one.                                                                             |
| **P0**   | todo        |  High  |   S    | 0160   | Review loop burns its iteration budget polling pending CI, then reports test failures            | Review Loop / CI          | Every unattended Stage 4 runs out of iterations before review. Workaround: wait for CI, then resume.                                                                                                                                                    |
| **P0**   | todo        |  High  |   L    | 0151   | Planner estimates the touch set; overlapping concurrent flows are blocked                        | Holon Flow / Concurrency  | Unblocked by 0159 (#97 merged). Re-plan on the new `main`; land 0149 first. Must handle `{parent}--{n}-{slug}` child branches.                                                                                                                          |
| **P1**   | todo        |  High  |   S    | 0175   | Check GitHub token scopes before Stage 3 when the plan touches workflow files                    | Holon Flow / GitHub       | A 55-minute Stage 3 for Bean 0168 was lost to a push rejected for the missing `workflow` scope. Complements 0171 (#108 merged, refused-push patch salvage).                                                                                             |
| **P1**   | todo        |  High  |   S    | 0162   | Stage 5 calibration commits a report that fails the `hygiene` Prettier check                     | Calibration / CI          | Turns every flow PR red after calibration (recurred on #105, #106, #107, #109).                                                                                                                                                                         |
| **P1**   | todo        |  High  |   S    | 0157   | `holon flow` auto-enables the mitmproxy sidecar; role containers cannot reach it                 | Holon Flow / Proxy        | Workaround: `HOLON_TOKEN_REDUCE=0`. Related to 0130.                                                                                                                                                                                                    |
| **P1**   | todo        |  High  |   M    | 0161   | Decomposed sub-intents have no flow path to `main` and do not build on each other                | Holon Flow                | Deferred from #97. Implement the 2026-10-29 rulings: nest under the deciding node, merge into the deciding plan/execution branch, nested PRs automatic, sibling slugs distinct. Docs: PRs #103 and #110 (merged); Bean 0210 aligns five more documents. |
| **P1**   | todo        |  High  |   M    | 0149   | Plan and execution IDs collide across concurrently planned intents                               | Provenance / Planner      | #91 and #92 shared `P-1792765112`. Prerequisite for 0151.                                                                                                                                                                                               |
| **P1**   | todo        |  High  |   M    | 0155   | General `HOLON_*` forwarding puts credential-shaped values on the docker argv                    | Security                  | Already on main. Default fix: send every `HOLON_*` value through the 0600 env-file.                                                                                                                                                                     |
| **P1**   | todo        |  High  |   M    | 0148   | Redact before truncating ledger `error_context`; close `CredentialRedactor` gaps                 | Security / Ledger         | Route those rows through `redact_agent_secrets`.                                                                                                                                                                                                        |
| **P1**   | todo        | Medium |   M    | 0146   | Plans-ledger correction rows; calibration picks the right predicted metrics                      | Calibration / Ledger      | Every calibration last cycle needed a manual annotation (7 PRs).                                                                                                                                                                                        |
| **P1**   | todo        |  High  |   L    | 0156   | Investigate moving issue tracking from harness beans to beads inside each target                 | Issue Tracking            | Investigation only, no target code. Can run in parallel with any flow. Precedes deprecating the harness.                                                                                                                                                |
| **P1**   | todo        | Medium |   S    | 0172   | Stage and turn budgets accept an explicit 'unlimited' value, distinct from unset (default)       | Holon Flow / Config       | Workaround today: `HOLON_STAGE_BUDGET_EXECUTE_MINUTES=10080` (the 7-day maximum).                                                                                                                                                                       |
| **P1**   | todo        |  High  |   M    | 0173   | holon loads layered .env files (specific overrides broad) that every sandbox stage inherits      | Holon Flow / Config       | Project `.env` overrides the broader `.env`. Touches `cli.py`; sequence after 0155/0148.                                                                                                                                                                |
| **P1**   | todo        | Medium |   M    | 0174   | Document every environment variable holon reads, in one generated and CI-checked reference       | Documentation / Config    | After 0172 and 0173, so the reference includes their variables.                                                                                                                                                                                         |
| **P1**   | todo        |  High  |   L    | 0176   | Remove every unittest reference from holon-agentic-coder; the suite is pytest only               | Tests                     | Unblocked by 0168 (#99 merged). 59 `TestCase` classes and about 60 `unittest.mock` imports in 29 files. Runs alone: it touches most test files.                                                                                                         |
| **P1**   | todo        |  High  |   M    | 0182   | Persistent GitHub event watcher that emits PR and CI events and drives harness actions           | Harness / Automation      | Zero-token waits: watcher container plus event log; merges trigger cleanup and installs, CI failures the next review iteration. Guardrails: no new spending, no merges.                                                                                 |
| **P1**   | in-progress | Medium |   S    | 0180   | Document sub-intent branches nested under the node that decided the split                        | Docs / Holon Flow         | PR #103 merged (`e187393`). Follow-up docs for the five rulings through the flow: PR #110 reviewed, calibrated and merged (`85ef122`); close the bean. Remaining five documents: Bean 0210.                                                             |
| **P1**   | todo        |  High  |   M    | 0170   | pr-review-loop must converge: review the increment, defer Nits on unchanged code                 | Review Loop / Skills      | From PR #97 (33 iterations, diff ~3x, Nits never zero). Harness-only skill change. Do before the next long review loop.                                                                                                                                 |
| **P1**   | todo        |  High  |   M    | 0166   | Pipeline duration dashboard for CI builds                                                        | CI / Observability        | Check org Actions performance metrics first. Shares data and baseline with 0163 (#109, #30).                                                                                                                                                            |
| **P1**   | todo        |  High  |   XL   | 0152   | Audit long files; decompose oversized functions (flow.py, cli.py first)                          | Refactor / Concurrency    | Umbrella for the Bean 0177 action beans 0185-0200 and 0203-0208 (proposed); its audit stays the baseline. Measured: `flow.py` 5,157 lines, `cli.main` 1,097 lines.                                                                                      |
| **P1**   | todo        |  High  |   S    | 0185   | holon-agentic-coder: ruff complexity gate (C901, PLR0911-PLR0915) with an inline `noqa` baseline | Lint / Code Quality       | Gate first (0177 order step 1): ratchet-down baseline of 56 C901 offenders. Unblocks 0187, 0188, 0195, 0198, 0201.                                                                                                                                      |
| **P1**   | todo        |  High  |   S    | 0186   | holon-coherence: ruff complexity gate (C901, PLR0911-PLR0915) with an inline `noqa` baseline     | Lint / holon-coherence    | Gate first (0177 order step 1), disjoint from 0185. Unblocks 0203 and 0204.                                                                                                                                                                             |
| **P1**   | todo        |  High  |   L    | 0187   | Split `flow.py` into a `flow/` package, one module per stage and concern (move only)             | Refactor / Architecture   | After 0185. 5,157 lines touched by 7 of 16 flow PRs; AST-verified move only. Runs alone; unblocks 0190, 0191, 0193, 0194, 0197 and, with 0188, 0189.                                                                                                    |
| **P1**   | todo        |  High  |   L    | 0188   | Split `cli.py` into a `cli/` package of self-registering command modules                         | Refactor / CLI            | After 0185; can pair with 0187 (disjoint files). `cli.main` 1,097 lines, CC 114.                                                                                                                                                                        |
| **P1**   | todo        |  High  |   M    | 0203   | holon-coherence: command modules register their own parsers; drop the `sys.modules` locator      | CLI / holon-coherence     | After 0186; parallel with 0204. Unblocks 0207 and 0208.                                                                                                                                                                                                 |
| **P1**   | todo        |  High  |   L    | 0204   | holon-coherence: split `mitm_addon.py` into a `proxy/` package by concern (move only)            | Proxy / holon-coherence   | After 0186; parallel with 0203. 2,348 lines, AST-verified move only. Unblocks 0205 and 0206.                                                                                                                                                            |
| **P1**   | todo        |  High  |   M    | 0189   | Launcher module owns container launch and role dispatch; break the `flow` -> `cli` cycle         | Refactor / Architecture   | After 0187 and 0188; unblocks 0200. Bean 0177 proposes 0183 after 0189 and 0190 (not applied; 0183 stays at step 3).                                                                                                                                    |
| **P1**   | todo        |  High  |   M    | 0190   | `FlowCheckpoint` and ledger reconciliation own their behaviour; entrypoints stop importing flow  | Ledger / Holon Flow       | After 0187; 0158 (PR #111, same code) has merged. Unblocks 0196, 0199.                                                                                                                                                                                  |
| **P1**   | todo        |  High  |   M    | 0191   | One GitHub adapter owns every `gh` call (PR, CI probe, mergeability, review posting)             | GitHub / Architecture     | After 0187. Unblocks 0192.                                                                                                                                                                                                                              |
| **P1**   | todo        |  High  |   M    | 0195   | Executor entrypoint's raw `git` subprocess calls go through a `GitRepository` adapter            | Executor / Git            | After 0185. 81 raw `git` calls. With 0190, unblocks 0196.                                                                                                                                                                                               |
| **P1**   | todo        |  High  |   L    | 0192   | `run_review_loop` and `run_review_stage` become a `ReviewLoop` object with named steps           | Review Loop / Refactor    | After 0191. 528 lines, CC 131. Sequence with 0160 and 0179 (same touch set).                                                                                                                                                                            |
| **P1**   | todo        |  High  |   L    | 0196   | Executor entrypoint `main` becomes an `ExecutionRun` with named steps; module becomes a package  | Executor / Refactor       | After 0195 and 0190. 798 lines, CC 178 (worst in the repository).                                                                                                                                                                                       |
| **P2**   | todo        | Medium |   M    | 0181   | Use the `/_` leaf only when referencing a git branch, never on ids                               | Holon Flow / Ledger       | `intents.jsonl` `branch` and `parent_intent_id` hold refs; migrate with readers accepting both shapes.                                                                                                                                                  |
| **P2**   | todo        | Medium |   S    | 0169   | PR #97 residual Nits: split the pasted checkpoint test; complete git_flow §1.5 list              | Tests / Docs              | Small; touches `test_flow.py` and `git_flow.md`.                                                                                                                                                                                                        |
| **P2**   | todo        | Medium |   XL   | 0153   | Remove comments and docstrings from all code; make it self-documenting                           | Readability               | Per package, after each split lands (0187, 0188, 0204), not as one repository-wide flow.                                                                                                                                                                |
| **P2**   | in-progress | Medium |   S    | 0147   | Remove harness paths tracked in the target repositories                                          | Hygiene                   | `holon-coherence` half merged (PR #29, `68fdf67`) before its consensus review; post-merge follow-up PR #31 merged (`b52c7e1`). `holon-agentic-coder` half pending (fold into 0156 if beads lands first).                                                |
| **P2**   | todo        | Medium |   S    | 0210   | Align the remaining holon-agentic-coder docs with the sub-intent merge rulings                   | Docs / Holon Flow         | Five documents PR #110 (Bean 0180, merged `85ef122`) left on the old rules. Documentation only, through the flow; unblocked.                                                                                                                            |
| **P2**   | todo        |  Low   |   S    | 0150   | Flow tests write the real checkout's `action_index.db`                                           | Tests                     | Unblocked.                                                                                                                                                                                                                                              |
| **P2**   | todo        | Medium |   M    | 0193   | Decompose the intent and plan stage modules                                                      | Holon Flow / Refactor     | After 0187; parallel decomposition lane.                                                                                                                                                                                                                |
| **P2**   | todo        | Medium |   M    | 0194   | `run_execute_stage` becomes an `ExecuteStage` with named steps                                   | Holon Flow / Refactor     | After 0187; parallel decomposition lane. 306 lines, CC 40.                                                                                                                                                                                              |
| **P2**   | todo        | Medium |   M    | 0197   | Split `calibration.py` into a package; decompose metrics parsing and report generation           | Calibration / Refactor    | After 0187; parallel lane. Check overlap with 0146 and 0162.                                                                                                                                                                                            |
| **P2**   | todo        | Medium |   M    | 0198   | Agent runner registry: one `RunnerSpec` module per agent                                         | Runners / Refactor        | After 0185; parallel lane.                                                                                                                                                                                                                              |
| **P2**   | todo        | Medium |   S    | 0201   | Planner, executor and reviewer prompts carry the module-layout, complexity and naming rules      | Prompts / Standards       | After 0185. Plans declare touch sets at module granularity (feeds 0151).                                                                                                                                                                                |
| **P2**   | todo        | Medium |   M    | 0200   | Remove holon-agentic-coder's diverged `token_reduction` copy; holon-coherence is the owner       | Token Reduction           | After 0189. Ownership already ruled: holon-coherence owns token reduction.                                                                                                                                                                              |
| **P2**   | todo        | Medium |   M    | 0199   | Decompose ledger query and the knowledge index                                                   | Ledger / Knowledge        | After 0190; parallel lane. Low bean priority.                                                                                                                                                                                                           |
| **P2**   | todo        | Medium |   M    | 0205   | holon-coherence: `MitmproxyAddon.request` and `response` become named pipeline steps             | Proxy / holon-coherence   | After 0204; parallel with 0206.                                                                                                                                                                                                                         |
| **P2**   | todo        | Medium |   M    | 0206   | holon-coherence: one provider module per wire format (Anthropic, OpenAI, Gemini)                 | Proxy / holon-coherence   | After 0204; parallel with 0205.                                                                                                                                                                                                                         |
| **P2**   | todo        | Medium |   M    | 0207   | holon-coherence: A/B evaluation and metrics aggregation move out of the command handlers         | Metrics / holon-coherence | After 0203; parallel with 0208.                                                                                                                                                                                                                         |
| **P2**   | todo        | Medium |   M    | 0208   | holon-coherence: a `ProxyLifecycle` class owns proxy start-up, readiness and teardown            | Proxy / holon-coherence   | After 0203; parallel with 0207.                                                                                                                                                                                                                         |
| **P2**   | todo        |  Low   |   S    | 0202   | holon-agentic-coder: the pasted CI timing-gate steps become one composite action                 | CI                        | Unblocked (0184 completed). Workflows only.                                                                                                                                                                                                             |
| **P2**   | todo        |  Low   |   S    | 0209   | holon-coherence: the pasted CI timing-gate steps become one composite action                     | CI / holon-coherence      | Unblocked (0184 completed, PR #32). Workflows only.                                                                                                                                                                                                     |
| **P2**   | todo        |  High  |   L    | 0142   | Real-workload benchmark: Qwen3.8-27B dense vs Flash-Next MoE                                     | Model Selection           | Real data only (AGENTS.md item 10).                                                                                                                                                                                                                     |
| **P3**   | todo        | Medium |   M    | 0141   | Tune vmlx prefill/decode levers for both Qwen3.8 models, crash-safe                              | vmlx / Performance        | Pairs with 0142.                                                                                                                                                                                                                                        |

---

## Recommended Next Execution Sequence

**Rule (2026-10-25):** never run concurrent flows whose touched files overlap. Nearly every holon-agentic-coder bean
touches `flow.py` or `cli.py`, so those flows run **one at a time**: merge one, then plan the next on the new `main`.
Only disjoint work runs in parallel. Bean 0151 will make the flow enforce this; Bean 0183 and Bean 0152 will bring back
parallelism.

**Rule (2026-10-26):** no stage before the merge may halt for human review. The PR merge is the only human step, after
consensus review and Stage 5 calibration.

**Rule (2026-10-28):** the target suites rely solely on pytest. No new code or documentation names any other test runner
(Bean 0176 removes the existing references).

**Tooling (2026-10-29):** `main` (`993b686`) now includes Beans 0143 (#104), 0178 (#105), 0164 (#106), 0154 (#107), 0171
(#108) and the `holon-agentic-coder` half of 0163 (#109). Reinstall `holon` and rebuild the agent images from `main` via
`install-holon` so Stage 3 partial-code salvage (#108) and the updated prompt templates (#105) are active in the
containers. `main` (`8c9ff4d`) now also includes Bean 0158 (#111, pure-append ledger writes); reinstall so flows stop
reordering `intents.jsonl`. Until 0157, 0160, 0162 and 0179 land, run flows with `HOLON_TOKEN_REDUCE=0`, run Stage 4
through the harness `pr-review-loop` skill, and format the calibration report before pushing. Set
`HOLON_STAGE_BUDGET_EXECUTE_MINUTES=10080` for Stage 3 until Bean 0172 adds an explicit unlimited value.

Sequential lane, holon-agentic-coder (flow blockers first):

1. **Bean 0162**: every one of the eight parallel flows on 2026-10-29 hit it (calibration report fails Prettier) and
   needed a manual fix. Small. Its companion Bean 0158 (`intents.jsonl` reordered) merged as PR #111.
2. **Bean 0179**: route Stage 4 reviewer turns through the `review-loop` role container so `holon flow` reviews and
   posts on its own. Three PRs (#108, coherence #29 and #30) merged before their consensus review or calibration; a flow
   that reviews itself closes that gap. Adopt the Bean 0170 convergence rules there.
3. **Bean 0183**: every flow stage and engine bookkeeping step (checkpoint, empty-diff guard, mergeability, Stage 5
   calibration) runs in its own sandboxed clone, so parallel flows need no host checkouts.
4. **Bean 0175**: check GitHub token scopes before Stage 3 starts when the plan touches workflow files.
5. **Bean 0149**, then **Bean 0151**: unique IDs across concurrently planned intents (the parallel batch relied on 90 s
   staggered starts), then touch-set admission.
6. **Bean 0181**: `/_` only on branch refs, ids bare (ledger field migration; readers accept both shapes).
7. **Bean 0160**, then **Bean 0157**: the remaining flow-integrity blockers (both touch `flow.py`).
8. **Bean 0161**: nested sub-intent branches per the maintainer's 2026-10-29 rulings (merge into the deciding plan or
   execution branch, nested PRs automatic), chaining and resume safety.
9. **The `holon-agentic-coder` half of Bean 0147** (task-id references in `flow.py`, `cli.py` and docs), unless Bean
   0156 folds it into the beads move.
10. **Bean 0155**, then **Bean 0148**: credential-redaction gaps (both touch `cli.py`).
11. **Bean 0172**, **Bean 0173**, then **Bean 0174**: unlimited budgets, layered `.env`, then the env-var reference.
12. **Bean 0146**: calibration reads the correct predicted metrics.
13. **Bean 0176**: pytest-only conversion of every test file (touches most test files, so it runs alone).
14. **holon-agentic-coder Beans 0185 and 0187-0202** in the Bean 0177 migration order (umbrella Bean 0152 tracks
    0185-0200; 0201 and 0202 sit outside it): lint gate 0185, move-only splits 0187 and 0188, then 0189, 0190, 0191 and
    0195, then the decomposition lanes, then 0200 and 0201. Bean 0202 (CI composite action) is workflow-only and can run
    any time. Bean 0153 runs per package after each split.

Parallel lane (disjoint files):

- **Merged, beans to close:** holon-agentic-coder PR #110 (Bean 0180 docs, `85ef122`) and PR #111 (Bean 0158 pure-append
  ledgers, `8c9ff4d`), both reviewed and calibrated through the flow; holon-coherence PR #31 (post-merge follow-up for
  #29, `b52c7e1`). Bean 0190 can now move the ledger code.
- **Harness branch awaiting the maintainer:** `feat/0182-0170-event-watcher-and-loop-convergence` (Beans 0182 and 0170
  implemented and tested).
- **holon-coherence decomposition lane** (Bean 0177 order, disjoint from holon-agentic-coder): lint gate 0186, then 0203
  and 0204 in parallel, then 0205-0208. Bean 0209 (CI composite action) is workflow-only.
- **Bean 0170** (review-loop convergence rules, harness-only). Do it before the next long review loop.
- **Bean 0210**: apply the five sub-intent rulings to the five documents PR #110 left on the old rules (documentation
  only, through the flow; PR #110 is merged).
- **Bean 0182** (GitHub event watcher, harness-only): replaces per-task polling loops; do it before the next long review
  loop, alongside 0170.
- **Bean 0166** (CI pipeline duration dashboard; workflows and observability only, pairs with 0163).
- **Bean 0169** (PR #97 residual Nits; small, `test_flow.py` and `git_flow.md`). Check overlap with the lane above.
- **Bean 0156** (beads investigation, no target code). Its outcome decides how the `holon-agentic-coder` half of 0147
  and the harness retirement proceed.
- **Bean 0150** (flow tests write `.index/action_index.db`; tests only).
- **Beans 0142 and 0141** (benchmarking and tuning, no code flow).
