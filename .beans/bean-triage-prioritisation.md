# Holon Ecosystem Bean Triage and Prioritisation Matrix

**Last Updated:** 2026-10-30 09:06:52 UTC

## Executive Summary

Since the 2026-10-22 checkpoint, every bean that was active then and blocked on a runner has gone through the full
5-stage Holon flow and been merged by the maintainer:

- holon-agentic-coder PRs #90, #91, #93, #94, #95 and #96
- holon-coherence PR #27

Concurrent flows on overlapping files (#94, #95 and #96 all changed `flow.py` and `cli.py`) forced repeated syncs and
re-reviews: 141 review-loop passes from the first sync onward, about 10M+ tokens. Beans 0151 and 0152 address that, and
overlapping flows now run one after another.

- **Total Tracked Beans**: 220 (excluding template)
- **Completed**: 165 (75.0%)
- **Scrapped / Superseded**: 2 (0.9%)
- **Active**: 53 (24.1%), of which 6 are in progress and 47 are todo

Dates below are UTC, as in `gh`, the bean timestamps and the milestones.

**2026-10-26:** the first full claude-agent `holon flow` runs (Beans 0151, 0159) exposed seven defects in the flow
itself. They are logged as Beans 0157-0162, and Bean 0144 was raised to critical after its fabricated approval reached
GitHub. Bean 0156 starts the investigation into moving issue tracking from harness beans to beads inside each target,
ahead of deprecating this harness.

**2026-10-28:** Bean 0168 (PR #99) cut CI test time through the full flow: pytest-xdist, hermetic test git and
per-worker template repositories. Real CI pytest time fell 2.5x on macOS (382 s to 153 s), 2.0x on ubuntu (242 s to 123
s) and 1.6x for Workspace survival (417 s to 258 s). It converged in 8 review iterations and was merged (`0e54457`).
Bean 0144 was then delivered as three sequential flows (PRs #100, #101 and #102, all merged): Stage 4 now fails closed
and is decided only by a real reviewer ensemble. New: Bean 0175 (token-scope pre-flight, logged on 2026-10-27), Bean
0176 (pytest only), Bean 0177 (architecture and code-principles research that spawns action beans), Bean 0178 (repeated
test runs only for performance work) and Bean 0179 (routes the Stage 4 reviewer turns through the role container).

**2026-10-29:** PR #103 (Bean 0180, documentation only) nests sub-intent branches under the node that decided the split;
it was merged (`e187393`) after 11 review iterations. The maintainer settled its five open questions (merge into the
deciding plan or execution branch, nested PRs automatic), which a follow-up docs PR and Bean 0161 implement. New: Bean
0181 (`/_` only on branch refs).

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
beans are now closed. New on 2026-10-29: **Bean 0211** (two holon-coherence A/B recipe doc fixes PR #31 left open). On
2026-10-30, **Bean 0210** (five documents PR #110 left on the old sub-intent rules) traversed the full flow, passed 3/3
ensemble review in 5 iterations, was calibrated and merged as PR #113 (`760ee87`), and harness PR #56 (`2399680`) merged
after 14 review iterations. New on 2026-10-30: **Bean 0212** (`pr-review-loop` delegates loop orchestration to a
background subagent so the main agent stays free).

Later on 2026-10-30, five flow PRs traversed the full 5-stage Holon flow and merged across both targets: **Bean 0162**
(HAC PR #112, `d1bdf6b`: calibration report Prettier hygiene), **Bean 0202** (HAC PR #114, `6370428`: CI timing gate
composite action), **Bean 0211** (Coherence PR #33, `e475e6d`: A/B test recipe doc fixes), **Bean 0209** (Coherence PR
#34, `a6912ac`: CI timing gate composite action), and **Bean 0186** (Coherence PR #35, `f7e4aa6`: Ruff complexity gate
with inline noqa baseline). In addition, **Bean 0213** was logged to reflect review-loop skill rules into the native
Review Loop Holon Agent.

**Bean 0185** then completed the lint-gate pair: HAC PR #115 merged as `0e71262` (frozen 91-entry inline noqa identity
baseline, `PGH004` guard against bare `# noqa`, swap-rejection test; 2 review iterations, EV 72.07 predicted / 77.27
actual, and the first calibration report to pass Prettier with no follow-up commit). **Bean 0203** (Coherence PR #36,
commands register their own parsers) passed 3/3 unanimous ensemble consensus review in 4 iterations, completed Stage 5
calibration (`3af551d`), and is awaiting maintainer merge. **Bean 0156 (beads investigation) completed:** recommended
target-native beads (`bd`) issue tracking with `hac-` and `hcoh-` prefixes, offline `refs/dolt/data` sync, migrating
only open beans (~47), and archiving the harness read-only; spawned action beans 0214-0218. Harness PR driver brief
codified in `FLOW_PR_DRIVER.md`.

**Bean 0177 (architecture research) completed:** measured `flow.py` 5,157 lines (7 of the 14 flow PRs #94-#109 touched
it), `cli.main` 1,097 lines (CC 114), `executor.main` 798 lines (CC 178), and 56 + 38 functions over CC 10. It spawned
Beans 0185-0209: lint gates first (0185, 0186), then move-only splits that remove the shared files (0187, 0188, 0203,
0204), then per-module decomposition lanes that can run in parallel. The maintainer ruled that holon-coherence owns
token reduction (Bean 0200).

---

## Key Milestones Completed (Beans 0080 – 0218)

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
20. **Nested sub-intent docs and pure-append ledgers (Beans 0180, 0158, 0210 / PRs #103, #110, #111, #113, 2026-10-29 to
    2026-10-30)**:
    - `0180` (#103, `e187393`, hand-authored docs): sub-intent branches nest under their deciding plan. Flow PR #110
      (`85ef122`) then documented the five maintainer rulings: merge into the deciding plan or execution branch,
      automatic nested PRs, distinct sibling slugs, keep `deciding_branch`, and review-decided splits under the plan or
      execution. Flow PR #113 (`0210`, `760ee87`, 5 review iterations, calibrated) applied those rulings to the
      remaining five documents (`agent_design.md`, `architecture.md`, `faq.md`, `safety.md`,
      `planning_architecture_specification.md`) plus `planning_and_evaluation.md`.
    - `0158` (#111, `8c9ff4d`): every ledger write is a pure append guarded by a fail-closed prefix check; conflict
      detection no longer mistakes the `|||||||` inside an `intents.jsonl` row for a conflict marker, so flows stop
      reordering `intents.jsonl` (resolving milestone 14's defect).
21. **Calibration Prettier Hygiene, Timing-Gate Composite Actions, and Complexity Gate (Beans 0162, 0202, 0209, 0211,
    0186 / HAC PRs #112, #114 and Coherence PRs #33, #34, #35, 2026-10-30)**:
    - `0162` (HAC #112, `d1bdf6b`): Stage 5 calibration report matches repository Prettier formatting and passes CI
      hygiene cleanly.
    - `0202` (HAC #114, `6370428`) + `0209` (Coherence #34, `a6912ac`): deduplicated CI timing gate steps into shared
      local `.github/actions/ci-timing-gate/action.yml` composite actions across all workflow jobs.
    - `0211` (Coherence #33, `e475e6d`): updated A/B test documentation recipes for background proxy startup and
      combined pass metrics.
    - `0186` (Coherence #35, `f7e4aa6`): enforced Ruff complexity gates (C901, PLR0911-PLR0915) with an inline `# noqa`
      baseline and monotonic ratchet pytest, unblocking 0203, 0204, 0207, and 0208.
22. **HAC Complexity Gate, Coherence Command Self-Registration, and Beads Adoption Design (Beans 0185, 0203, 0156 / HAC
    PR #115 & Coherence PR #36, 2026-10-30)**:
    - `0185` (HAC #115, `0e71262`): enforced Ruff complexity gates (C901, PLR0911-PLR0915) on holon-agentic-coder with
      frozen 91-entry inline noqa baseline, PGH004 guard against bare `# noqa`, and swap-rejection test; first
      calibration report to pass Prettier with no follow-up commit.
    - `0203` (Coherence #36, `3af551d`): refactored command modules to self-register parsers and handlers, removed
      `_dispatch.py` `sys.modules` locator in favor of explicit `*_fn` dependency injection, split `test_cli.py` (327
      tests), passed 3/3 ensemble consensus review, and completed Stage 5 calibration.
    - `0156` (research): evaluated beads (`bd`, v1.3.2, Dolt-backed) for target-native issue tracking. Mapped 213
      existing beans, recommended per-target trackers (`hac-` and `hcoh-`), offline `refs/dolt/data` sync, migrating ~47
      open beans, and freezing closed history in the read-only harness. Spawned Beans 0214-0218 and codified
      `FLOW_PR_DRIVER.md`.

---

## Active Beans Triage and Prioritisation Matrix

| Priority | Status      | Impact | Sizing | Bean # | Title                                                                                           | Domain                     | Dependencies / Notes                                                                                                                                                                                                        |
| :------- | :---------- | :----: | :----: | :----- | :---------------------------------------------------------------------------------------------- | :------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **P0**   | in-progress |  High  |   M    | 0179   | Route Stage 4 reviewer turns through the `review-loop` role container                           | Review Loop                | Follow-up to 0144 (PR #102 refuses host reviewer turns, fail closed). Until it lands, Stage 4 runs through the harness `pr-review-loop` skill.                                                                              |
| **P0**   | todo        |  High  |   L    | 0183   | Every flow stage works in its own sandboxed clone; `holon flow` needs no host checkout          | Holon Flow / Sandbox       | Stages 1-3 already clone in-container; move checkpoint, engine git checks and Stage 5 calibration into sandboxed clones so concurrent flows never share or require a host worktree. Pairs with 0179, 0149, 0151.            |
| **P0**   | todo        |  High  |   S    | 0160   | Review loop burns its iteration budget polling pending CI, then reports test failures           | Review Loop / CI           | Every unattended Stage 4 runs out of iterations before review. Workaround: wait for CI, then resume.                                                                                                                        |
| **P0**   | todo        |  High  |   L    | 0151   | Planner estimates the touch set; overlapping concurrent flows are blocked                       | Holon Flow / Concurrency   | Unblocked by 0159 (#97 merged). Re-plan on the new `main`; land 0149 first. Must handle `{parent}--{n}-{slug}` child branches.                                                                                              |
| **P1**   | todo        |  High  |   S    | 0175   | Check GitHub token scopes before Stage 3 when the plan touches workflow files                   | Holon Flow / GitHub        | A 55-minute Stage 3 for Bean 0168 was lost to a push rejected for the missing `workflow` scope. Complements 0171 (#108 merged, refused-push patch salvage).                                                                 |
| **P1**   | todo        |  High  |   S    | 0157   | `holon flow` auto-enables the mitmproxy sidecar; role containers cannot reach it                | Holon Flow / Proxy         | Workaround: `HOLON_TOKEN_REDUCE=0`. Related to 0130.                                                                                                                                                                        |
| **P1**   | todo        |  High  |   M    | 0161   | Decomposed sub-intents have no flow path to `main` and do not build on each other               | Holon Flow                 | Deferred from #97. Implement the 2026-10-29 rulings: nest under the deciding node, merge into the deciding plan/execution branch, nested PRs automatic, sibling slugs distinct. Docs: PRs #103, #110 and #113 (all merged). |
| **P1**   | todo        |  High  |   M    | 0149   | Plan and execution IDs collide across concurrently planned intents                              | Provenance / Planner       | #91 and #92 shared `P-1792765112`. Prerequisite for 0151.                                                                                                                                                                   |
| **P1**   | todo        |  High  |   M    | 0155   | General `HOLON_*` forwarding puts credential-shaped values on the docker argv                   | Security                   | Already on main. Default fix: send every `HOLON_*` value through the 0600 env-file.                                                                                                                                         |
| **P1**   | todo        |  High  |   M    | 0148   | Redact before truncating ledger `error_context`; close `CredentialRedactor` gaps                | Security / Ledger          | Route those rows through `redact_agent_secrets`.                                                                                                                                                                            |
| **P1**   | todo        | Medium |   M    | 0146   | Plans-ledger correction rows; calibration picks the right predicted metrics                     | Calibration / Ledger       | Every calibration last cycle needed a manual annotation (7 PRs). Runs before 0197 (same parser).                                                                                                                            |
| **P1**   | todo        |  High  |   M    | 0214   | Pilot beads (bd) issue tracking inside holon-agentic-coder                                      | Issue Tracking / Pilot     | Holon flow against holon-agentic-coder. `bd init` prefix `hac-`, offline config, pin `bd` in image, import open beans, fold in 0147 hac half. Precursor to 0215-0218.                                                       |
| **P1**   | todo        |  High  |   S    | 0215   | Deterministic beans-to-beads JSONL converter and real-data dry run                              | Issue Tracking / Migration | Harness work. Converts bean frontmatter + body to beads JSONL for `bd import`; verified on all ~47 open beans per rule 10. Unblocks 0217.                                                                                   |
| **P1**   | todo        |  High  |   S    | 0219   | Remove fallback defaults for agent runner and model resolution                                  | CLI / Safety               | Remove FALLBACK_AGENT and table default model resolution; fail closed if --agent and --model are not explicitly specified (preserve checkpoint resumption values).                                                          |
| **P1**   | todo        | Medium |   S    | 0172   | Stage and turn budgets accept an explicit 'unlimited' value, distinct from unset (default)      | Holon Flow / Config        | Workaround today: `HOLON_STAGE_BUDGET_EXECUTE_MINUTES=10080` (the 7-day maximum).                                                                                                                                           |
| **P1**   | todo        |  High  |   M    | 0173   | holon loads layered .env files (specific overrides broad) that every sandbox stage inherits     | Holon Flow / Config        | Project `.env` overrides the broader `.env`. Touches `cli.py`; sequence after 0155/0148 and 0174.                                                                                                                           |
| **P1**   | todo        | Medium |   M    | 0174   | Document every environment variable holon reads, in one generated and CI-checked reference      | Documentation / Config     | After 0172; precursor to 0173, whose layered `.env` needs this reference's allow-list and secret flags.                                                                                                                     |
| **P1**   | todo        |  High  |   L    | 0176   | Remove every unittest reference from holon-agentic-coder; the suite is pytest only              | Tests                      | Unblocked by 0168 (#99 merged). 59 `TestCase` classes and about 60 `unittest.mock` imports in 29 files. Runs alone: it touches most test files.                                                                             |
| **P1**   | todo        |  High  |   M    | 0213   | Reflect review-loop skill rules into native Review Loop Holon Agent                             | Review Loop / Prompts      | Target: `holon-agentic-coder`. Reflects mandatory target-branch conflict checks, ledger-only fast resolution, incremental reviews, and model fallback into `review_loop.template.md` and `sandbox_executor`.                |
| **P1**   | todo        |  High  |   M    | 0166   | Pipeline duration dashboard for CI builds                                                       | CI / Observability         | Check org Actions performance metrics first. Shares data and baseline with 0163 (#109, #30).                                                                                                                                |
| **P1**   | todo        |  High  |   XL   | 0152   | Audit long files; decompose oversized functions (flow.py, cli.py first)                         | Refactor / Concurrency     | Umbrella for the Bean 0177 action beans 0185-0200 and 0203-0208 (proposed); its audit stays the baseline. Measured: `flow.py` 5,157 lines, `cli.main` 1,097 lines.                                                          |
| **P1**   | todo        |  High  |   L    | 0187   | Split `flow.py` into a `flow/` package, one module per stage and concern (move only)            | Refactor / Architecture    | After 0185. 5,157 lines touched by 7 of 14 flow PRs; AST-verified move only. Runs alone among `flow.py` PRs (parallel-safe with 0188); unblocks 0190, 0191, 0193, 0194, 0197 and, with 0188, 0189.                          |
| **P1**   | in-progress |  High  |   L    | 0188   | Split `cli.py` into a `cli/` package of self-registering command modules                        | Refactor / CLI             | After 0185; can pair with 0187 (disjoint files). `cli.main` 1,097 lines, CC 114.                                                                                                                                            |
| **P1**   | in-progress |  High  |   M    | 0203   | holon-coherence: command modules register their own parsers; drop the `sys.modules` locator     | CLI / holon-coherence      | After 0186; parallel with 0204. Unblocks 0207 and 0208.                                                                                                                                                                     |
| **P1**   | in-progress |  High  |   L    | 0204   | holon-coherence: split `mitm_addon.py` into a `proxy/` package by concern (move only)           | Proxy / holon-coherence    | After 0186; parallel with 0203. 2,348 lines, AST-verified move only. Unblocks 0205 and 0206.                                                                                                                                |
| **P1**   | todo        |  High  |   M    | 0189   | Launcher module owns container launch and role dispatch; break the `flow` -> `cli` cycle        | Refactor / Architecture    | After 0187 and 0188; unblocks 0200. With 0190 (both item 4), precedes 0183 (item 5), as Bean 0177 proposes.                                                                                                                 |
| **P1**   | todo        |  High  |   M    | 0190   | `FlowCheckpoint` and ledger reconciliation own their behaviour; entrypoints stop importing flow | Ledger / Holon Flow        | After 0187; 0158 (PR #111, same code) has merged. Precedes 0183. Unblocks 0196, 0199.                                                                                                                                       |
| **P1**   | todo        |  High  |   M    | 0191   | One GitHub adapter owns every `gh` call (PR, CI probe, mergeability, review posting)            | GitHub / Architecture      | After 0187. Unblocks 0192.                                                                                                                                                                                                  |
| **P1**   | todo        |  High  |   M    | 0195   | Executor entrypoint's raw `git` subprocess calls go through a `GitRepository` adapter           | Executor / Git             | After 0185. 81 raw `git` calls. With 0190, unblocks 0196.                                                                                                                                                                   |
| **P1**   | todo        |  High  |   L    | 0192   | `run_review_loop` and `run_review_stage` become a `ReviewLoop` object with named steps          | Review Loop / Refactor     | After 0191. 528 lines, CC 131. Sequence with 0160 and 0179 (same touch set).                                                                                                                                                |
| **P1**   | todo        |  High  |   L    | 0196   | Executor entrypoint `main` becomes an `ExecutionRun` with named steps; module becomes a package | Executor / Refactor        | After 0195 and 0190. 798 lines, CC 178 (worst in the repository).                                                                                                                                                           |
| **P2**   | todo        | Medium |   S    | 0220   | Remove GitHub-specific PR wording; standardize on Review Loop and Change Diff                   | Flow / Terminology         | Replace 'PR review loop' with 'review loop' in CLI help (--skip-review), flow logs, and prompt scaffolding. Decouple core engine from platform-specific PR terms.                                                           |
| **P2**   | todo        | Medium |   M    | 0181   | Use the `/_` leaf only when referencing a git branch, never on ids                              | Holon Flow / Ledger        | `intents.jsonl` `branch` and `parent_intent_id` hold refs; migrate with readers accepting both shapes. After 0161 and 0179 (both overlap `flow.py`).                                                                        |
| **P2**   | todo        | Medium |   S    | 0169   | PR #97 residual Nits: split the pasted checkpoint test; complete git_flow §1.5 list             | Tests / Docs               | Small; touches `test_flow.py` and `git_flow.md`. Not beside #112, 0187 or 0150 (all edit `test_flow.py`); see sequence item 2.                                                                                              |
| **P2**   | todo        | Medium |   XL   | 0153   | Remove comments and docstrings from all code; make it self-documenting                          | Readability                | Per package, with or right after that package's decomposition (which follows its split: 0187, 0188, 0204), not as one repository-wide flow.                                                                                 |
| **P2**   | in-progress | Medium |   S    | 0147   | Remove harness paths tracked in the target repositories                                         | Hygiene                    | `holon-coherence` half merged (PR #29, `68fdf67`) before its consensus review; post-merge follow-up PR #31 merged (`b52c7e1`). `holon-agentic-coder` half pending (fold into 0156 if beads lands first).                    |
| **P2**   | in-progress |  Low   |   S    | 0150   | Flow tests write the real checkout's `action_index.db`                                          | Tests                      | Unblocked; tests are in `test_flow.py`, so not beside #112, 0187 or 0169; see sequence item 2.                                                                                                                              |
| **P2**   | todo        | Medium |   M    | 0193   | Decompose the intent and plan stage modules                                                     | Holon Flow / Refactor      | After 0187; parallel decomposition lane.                                                                                                                                                                                    |
| **P2**   | todo        | Medium |   M    | 0194   | `run_execute_stage` becomes an `ExecuteStage` with named steps                                  | Holon Flow / Refactor      | After 0187; parallel decomposition lane. 306 lines, CC 40.                                                                                                                                                                  |
| **P2**   | todo        | Medium |   M    | 0197   | Split `calibration.py` into a package; decompose metrics parsing and report generation          | Calibration / Refactor     | After 0187, 0146 and 0162 (same predicted-metrics parser); parallel lane otherwise.                                                                                                                                         |
| **P2**   | todo        | Medium |   M    | 0198   | Agent runner registry: one `RunnerSpec` module per agent                                        | Runners / Refactor         | After 0185; parallel lane.                                                                                                                                                                                                  |
| **P2**   | todo        | Medium |   S    | 0201   | Planner, executor and reviewer prompts carry the module-layout, complexity and naming rules     | Prompts / Standards        | After 0185. Plans declare touch sets at module granularity (feeds 0151).                                                                                                                                                    |
| **P2**   | todo        | Medium |   M    | 0200   | Remove holon-agentic-coder's diverged `token_reduction` copy; holon-coherence is the owner      | Token Reduction            | After 0189. Ownership already ruled: holon-coherence owns token reduction.                                                                                                                                                  |
| **P2**   | todo        | Medium |   M    | 0199   | Decompose ledger query and the knowledge index                                                  | Ledger / Knowledge         | After 0190; parallel lane. Low bean priority.                                                                                                                                                                               |
| **P2**   | todo        | Medium |   M    | 0205   | holon-coherence: `MitmproxyAddon.request` and `response` become named pipeline steps            | Proxy / holon-coherence    | After 0204; parallel with 0206.                                                                                                                                                                                             |
| **P2**   | todo        | Medium |   M    | 0206   | holon-coherence: one provider module per wire format (Anthropic, OpenAI, Gemini)                | Proxy / holon-coherence    | After 0204; parallel with 0205. With or after 0200 (holon-agentic-coder's copy goes first).                                                                                                                                 |
| **P2**   | todo        | Medium |   M    | 0207   | holon-coherence: A/B evaluation and metrics aggregation move out of the command handlers        | Metrics / holon-coherence  | After 0203; parallel with 0208.                                                                                                                                                                                             |
| **P2**   | todo        | Medium |   M    | 0208   | holon-coherence: a `ProxyLifecycle` class owns proxy start-up, readiness and teardown           | Proxy / holon-coherence    | After 0203; parallel with 0207.                                                                                                                                                                                             |
| **P2**   | todo        | Medium |   M    | 0216   | Holon flow references and drives beads work items (claim on intent, close on merge)             | Holon Flow / Beads         | Holon flow against holon-agentic-coder. Intent `work_item` field, `holon intent` claims issue, calibration/merge closes with PR URL. Sequence after 0214.                                                                   |
| **P2**   | todo        | Medium |   S    | 0217   | Adopt beads (bd) issue tracking inside holon-coherence                                          | Issue Tracking / Coherence | Holon flow against holon-coherence. `bd init` prefix `hcoh-`, import open coherence beans from 0215 converter. Sequence after 0214 and 0215.                                                                                |
| **P2**   | todo        | Medium |   M    | 0218   | Port harness skills and guidance to bd and sequence the harness retirement                      | Harness Deprecation        | Harness work. Retire triage matrix / `prioritise-beans` for `bd ready --json`; port guidance; archive harness read-only after pilots succeed.                                                                               |
| **P2**   | todo        |  High  |   L    | 0142   | Real-workload benchmark: Qwen3.8-27B dense vs Flash-Next MoE                                    | Model Selection            | Real data only (AGENTS.md item 10).                                                                                                                                                                                         |
| **P3**   | todo        | Medium |   M    | 0141   | Tune vmlx prefill/decode levers for both Qwen3.8 models, crash-safe                             | vmlx / Performance         | Pairs with 0142.                                                                                                                                                                                                            |

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

1. **Bean 0150** (flow tests write `.index/action_index.db`) and **Bean 0169** (PR #97 residual Nits, plus
   `git_flow.md`), one after the other: both edit `test_flow.py`, which 0187 splits. Whichever misses that window runs
   after 0187 on the split `tests/flow/` layout. Bean 0185 is done (PR #115, `0e71262`), so both lint gates now guard
   new code.
2. **Bean 0203** (holon-coherence: commands register their own parsers; PR #36 calibrated, awaiting maintainer merge),
   then **Bean 0204** (holon-coherence: split `mitm_addon.py` into a `proxy/` package) once #36 merges — both touch the
   command/CLI seam, so they run one after the other.
3. **Bean 0213** (reflect review-loop skill rules into native Review Loop Holon Agent) to bring containerised
   review-loop prompts and conflict gates into parity with the harness.
4. **Bean 0187** (split `flow.py` into a `flow/` package, move only) and, in parallel, **Bean 0188** (split `cli.py`
   into self-registering command modules). Their files are disjoint: 0188 touches `cli.py`, `test_cli.py` and the entry
   point, none of the `flow.py` and `test_flow.py` files 0187 holds alone. Bean 0177 measured `flow.py` in 7 of the 14
   flow PRs #94-#109; landing the move-only splits before the next `flow.py` features stops those features colliding.
5. **Bean 0189** (launcher module for container launch; breaks the `flow`-`cli` import cycle), then **Bean 0190**
   (checkpoint and ledger reconciliation; entrypoints stop importing flow). Both beans ask to precede 0183 (item 6), as
   in Bean 0177's migration step 3.
6. **Bean 0179** (Stage 4 reviewers in the role container), then **Bean 0183** (every stage and engine bookkeeping step
   sandboxed), on the new layout. Three PRs merged before their review or calibration; 0179 lets `holon flow` review and
   post on its own.
7. **Bean 0175** (check GitHub token scopes before Stage 3 starts when the plan touches workflow files), then **Bean
   0146** (plans-ledger correction rows; calibration picks the right predicted metrics). Bean 0197 (item 9) follows 0146
   because both edit the predicted-metrics parser.
8. **Bean 0149**, then **Bean 0151**: unique IDs across concurrently planned intents (parallel batches still rely on
   staggered starts), then touch-set admission.
9. **Decomposition lanes from Bean 0177** once the splits land, in parallel where their packages differ: 0191 then 0192
   (GitHub adapter, `ReviewLoop`), 0193, 0194, 0195 then 0196, 0197 (after 0146 and 0162, as Bean 0197 asks), 0198 and
   0199 (all tracked by umbrella Bean 0152, with 0190 from item 5), and 0201 (outside the umbrella). Bean 0153 runs per
   package with, or right after, that package's decomposition.
10. **Bean 0160**, then **Bean 0157**: the remaining flow-integrity blockers.
11. **Bean 0161**: nested sub-intent branches per the maintainer's rulings (now documented by PRs #103, #110 and #113),
    chaining and resume safety.
12. **Bean 0181**: `/_` only on branch refs, ids bare (ledger field migration; readers accept both shapes). After 0161
    and 0179, which overlap `flow.py`, as Bean 0181 asks.
13. **The `holon-agentic-coder` half of Bean 0147**, **Bean 0155** then **Bean 0148** (redaction), **Beans 0172, 0174,
    0173** (budgets, the environment-variable reference, then the layered `.env` that needs the reference's allow-list
    and secret flags), **Bean 0200** (holon-coherence owns token reduction; after 0189).
14. **Bean 0176**: pytest-only conversion of every test file (touches most test files, so it runs alone).

Parallel lane (disjoint files):

- **Harness PR #58 (`docs/harness-20261030`):** consolidates Beans 0170, 0182, 0210, 0212, and 0213, with green CI
  checks, awaiting maintainer review/merge.
- **holon-coherence decomposition lane** (Bean 0177 order, disjoint from holon-agentic-coder): after lint gate 0186 (PR
  #35 merged), 0203 and 0204 in parallel, then 0205-0208. 0206 starts with or after Bean 0200 (item 13), as Bean 0206
  asks, so the duplicate is not refactored twice. Bean 0209 (CI composite action) is merged via PR #33.
- **Bean 0166** (CI pipeline duration dashboard; workflows and observability only, pairs with 0163). If it edits a
  target repository's workflow files, it does not run beside 0202 or 0209 (both already merged).
- **Beads adoption lane (from Bean 0156):** **Bean 0214** (pilot beads in holon-agentic-coder, folding in the 0147 hac
  half) and **Bean 0215** (deterministic beans-to-beads JSONL converter and real-data dry run, harness work) in
  parallel, followed by **Bean 0216** (flow integration), **Bean 0217** (adopt in coherence), and **Bean 0218** (port
  harness skills to `bd` and archive harness).
- **Beans 0142 and 0141** (benchmarking and tuning, no code flow).
