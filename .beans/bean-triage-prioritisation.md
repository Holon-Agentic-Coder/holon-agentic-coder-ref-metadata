# Holon Ecosystem Bean Triage and Prioritisation Matrix

**Last Updated:** 2026-11-09 03:30:22 UTC

## Executive Summary

Since the 2026-10-22 checkpoint, every bean that was active then and blocked on a runner has gone through the full
5-stage Holon flow and been merged by the maintainer:

- holon-agentic-coder PRs #90, #91, #93, #94, #95 and #96
- holon-coherence PR #27

Concurrent flows on overlapping files (#94, #95 and #96 all changed `flow.py` and `cli.py`) forced repeated syncs and
re-reviews: 141 review-loop passes from the first sync onward, about 10M+ tokens. Beans 0151 and 0152 address that, and
overlapping flows now run one after another.

- **Total Tracked Beans**: 257 (excluding template)
- **Completed**: 199 (77.4%)
- **Scrapped / Superseded**: 4 (1.6%)
- **Active**: 54 (21.0%), of which 4 are in progress and 50 are todo

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
calibration (`3af551d`), and merged as `72c8d36`. **Bean 0156 (beads investigation) completed:** recommended
target-native beads (`bd`) issue tracking with `hac-` and `hcoh-` prefixes, offline `refs/dolt/data` sync, migrating
only open beans (~47), and archiving the harness read-only; spawned action beans 0214-0218. Harness PR driver brief
codified in `FLOW_PR_DRIVER.md`.

**Beans 0179 and 0204 merged:** HAC PR #116 (`b746408`, Bean 0179) routed Stage 4 reviewer turns through the
`review-loop` role container via `_dispatch_role()`, eliminating host-side agent execution while preserving append-only
ledger provenance; passed 3/3 unanimous ensemble consensus review and completed Stage 5 calibration (`4f119cd`, EV
predicted 68.62 / actual 78.04, $\Delta\text{EV} = +9.42$). Coherence PR #37 (`9b001c3`, Bean 0204) split
`mitm_addon.py` (2,348 lines) into a modular `proxy/` package by concern, unblocking the concurrent decomposition lanes
(Beans 0205-0208). New beans logged: **Bean 0219** (mandatory `--agent` and `--model`, no fallback defaults), **Bean
0220** (remove PR references across flow), and **Bean 0221** (standardise Review Loop agent output with skill consensus
template).

**Bean 0188 merged:** HAC PR #117 (`76fe3ea`, Bean 0188) split `cli.py` (2,185 lines) into a modular `cli/` package of
self-registering command modules (`_role`, `init`, `flow`, `review`, `calibrate`, etc.) under
`sandbox_executor/cli/commands/`, unblocking concurrent CLI maintenance; passed 3/3 unanimous approval and completed
Stage 5 calibration (`1424a26`).

**Beans 0150 and 0205 merged:** HAC PR #118 (`e8e9a5d`, Bean 0150) eliminated hermeticity leaks where flow tests mutated
the real checkout index and guarded `.git` from sandbox mutations; passed 3/3 unanimous approval and completed Stage 5
calibration (`09ba249`). Coherence PR #38 (`e3dcc1a`, Bean 0205) decomposed `MitmproxyAddon.request` and `response`
hooks into an ordered step pipeline under `proxy/steps/`; passed 3/3 unanimous approval and completed Stage 5
calibration (`6a6ec15`).

**2026-10-31:** **Beans 0219 and 0206 merged:** HAC PR #119 (`0bb1615`, Bean 0219) made `--agent` and `--model`
mandatory CLI options across all `holon` commands, removing silent fallback defaults; passed 3/3 unanimous consensus
review and completed Stage 5 calibration (`4f20f01`). Coherence PR #39 (`ca43eb9`, Bean 0206) decomposed wire format
handling into dedicated provider modules under `proxy/providers/` conforming to `ProviderFormat` protocol; passed 3/3
unanimous consensus review and completed Stage 5 calibration (`45ff23d`). Both repositories were synchronized to
origin/main and reinstalled locally via `install-holon`.

Later on **2026-10-31:** **Beans 0220 and 0207 merged:** HAC PR #120 (`922289f`, Bean 0220) removed GitHub PR
terminology across flow CLI, report, and prompts, standardizing on platform-agnostic terms; passed 3/3 ensemble review
and completed Stage 5 calibration (`8d5e57d`, predicted EV 62.24 / actual 67.46, $\Delta\text{EV} = +5.22$). Coherence
PR #40 (`d6f1655`, Bean 0207) decomposed A/B test and metrics commands into dedicated domain packages `ab_testing/` and
`metrics/`; passed 3/3 ensemble review and completed Stage 5 calibration (`ffd6c9e`, predicted EV 7.94 / actual 8.41,
$\Delta\text{EV} = +0.47$). Both targets were synchronized to `origin/main` and reinstalled locally via `install-holon`.

**Bean 0177 (architecture research) completed:** measured `flow.py` 5,157 lines (7 of the 14 flow PRs #94-#109 touched
it), `cli.main` 1,097 lines (CC 114), `executor.main` 798 lines (CC 178), and 56 + 38 functions over CC 10. It spawned
Beans 0185-0209: lint gates first (0185, 0186), then move-only splits that remove the shared files (0187, 0188, 0203,
0204), then per-module decomposition lanes that can run in parallel. The maintainer ruled that holon-coherence owns
token reduction (Bean 0200).

**2026-11-02:** **Bean 0221 is reopened.** HAC PR #121 (`1d84c35`) is green, `MERGEABLE/CLEAN`, unanimous 3/3 at
iteration 1 and calibrated (predicted EV 73.21 / actual 78.35), but verification against the bean's own acceptance
criteria found seven gaps: the synthesis seam in `entrypoint/review_loop.py` and `flow.py` was never built, the approved
report prints five hard-coded `**Verified:**` assertions on every approval, a flag can promote a non-verdict to an
`APPROVED` heading, the findings table lost the `ID` and `Recommendation` columns, the closing notice is unchanged, and
`scaffold.py` (+320) invented a 16-role persona registry and its own output schema instead of mirroring the skill's -
growing the prompt to 288 lines where the ruling is to shorten it. Maintainer ruling: the `pr-review-loop` skill chain
is the only source of truth - and that chain documents a persona-sectioned body while the loop posts an
`Ensemble Consensus Review (n/n)` comment no harness file defines, so PR #121 had nothing to copy. Part A writes that
consensus template into the skills, condensed; part B mirrors it in the target through the flow. Part A landed the same
day: `pr_review_prompt.md` 181 to 157 lines with a new canonical Step 3a consensus comment, `pr_reviewer` 288 to 263
with the footer and trailer defined once, and `pr_review_loop` pointing at that block at all three posting points. The
part B resume then died in Stage 3 - it planned in 8.7 minutes and the executor produced no source changes at all - so
part B is re-cut as its own intent, `render-review-consensus-comment-from-reviewer-data`. **Bean 0208** is still in
flight on `holon-coherence` (PR #41, `2f30d6e`): Stage 3 pushed the `ProxyLifecycle` extraction, but both unit jobs are
red - 9 failures across `tests/commands/test_start.py`, `tests/commands/test_web_token.py` and `tests/test_cli.py`
(`SystemExit: 1` on the in-container `start` path, `stop_proxy_container` never called) - so Stage 4 has not started. No
other flow is running on either target.

**2026-11-04 to 2026-11-06:** **Bean 0221 (all 5 axes), Bean 0228, Bean 0229, Bean 0232, and Bean 0237 completed through
end-to-end flow runs.** The maintainer drove `holon flow` by hand, which surfaced and fixed a train of defects: the
sidecar readiness probe false positive (Bean 0227, hand-authored fix on `fix/0227-proxy-readiness-http-probe` under the
explicit-instruction exception), credential-design beans 0223 (flag/env audit), 0224 (claude credential auto-discovery,
no `HOLON_AGENT_KEY`), 0225 (OS-keychain only), and 0226 (PR-less e2e test on a sub-1B local model with full teardown).
PRs #121/#122 were closed as deprecated and their flow trees deleted when the maintainer expanded Bean 0221 into the
five-axis engine/skill standardisation contract. HAC PR #123 (`43f990a`) delivered axes 1-3 (one consensus template,
instructions and posted output; harness loop converged in 3 iterations, calibration ΔEV +34.21), HAC PR #124 (`bfecf0f`,
Bean 0228) delivered axis 4 (engine-owned single-shot review loop with `--iteration` label split from
`--max-iterations`; 4 iterations, calibration ΔEV +17.68), and HAC PR #125 (`baf3f8c`, Bean 0229) delivered axis 5
(native Stage 4 resolver inside the review loop with `applied`/`rejected` dispositions in `executions.jsonl`,
3-iteration `no-convergence` guard, and single exit posting; 3 iterations, calibrated `eb3302f`), closing umbrella
**Bean 0221**. **Bean 0232** (HAC PR #126, `0f80271`: bump default per-turn timeout `DEFAULT_TURN_SECONDS` from 300 s to
3600 s; calibration ΔEV +4.64) and **Bean 0237** (HAC PR #127, `6b9264c`: increase default `review_iteration` stage
budget from 15 min to 120 min; calibration ΔEV +3.80) then traversed all 5 stages hands-free and merged. **Bean 0235**
(HAC PR #128, `f8220eb`: Stage 4 CI is a post-review gate: launch reviewers immediately without waiting for pending CI;
calibration ΔEV +10.93) and **Bean 0238** (HAC PR #129, `ecec262`: Stage 4 resolver fixes CI and test failures by
synthesising first-class FindingRow for FIND-CI; calibration ΔEV +11.52) both followed and merged into `main`. **Bean
0239** (HAC PR #130, `1619cec`: Stage 5 calibration commits and pushes promoted knowledge and wisdom artifacts to
/calibrated and PR) and **Bean 0240** (HAC PR #131, `3c752e6`: fix resolver `run_turn()` argument signature and enforce
fail-closed verification defaults) both followed and merged into `main`. **Bean 0242** (HAC PR #132, `d932d48`: suppress
Docker Desktop CLI hints and Gordon suggestions via `DOCKER_CLI_HINTS=false`) followed and merged into `main`. New beans
logged: **Bean 0244** (treat knowledge and wisdom facts as immutable append-only records), **Bean 0243** (purge all
harness bean references from code and docs), **Bean 0241** (persist review loop sandbox across iterations to eliminate
repeated clone/teardown overhead), **Bean 0236** (post consensus review once per PR exit instead of duplicating via both
`gh pr comment` and `gh pr review`), **Bean 0233** (validate fail-fast that `--repo-dir` is an attached Git worktree),
and **Bean 0234** (event-driven CI check progress reporting during Stage 4 review).

**2026-11-06 to 2026-11-09:** Twelve further `holon-agentic-coder` flow PRs merged: **Bean 0244** (PR #133, `2a56a89`,
merged 2026-11-06: immutable append-only KB/WB fact records in `wisdom.py` with hermetic no-touch assertions), **Bean
0245** (PR #134, `4113f0d`: fix resolver runner build command), **Bean 0247** (PR #135: flow auto-creates the target
worktree), **Bean 0248** (PR #136: `holon models` command), **Bean 0249** (PR #137: replace `--repo-dir` with canonical
`--target-worktree`), **Bean 0251** (PR #138: pass prompts to agent runners via files), **Bean 0236** (PR #139,
`d0c1334`: post the Stage 4 consensus review exactly once via `gh pr review` with a single `--comment` fallback on the
HTTP 422 self-review restriction, retiring the duplicate unconditional `gh pr comment`; 3/3 consensus on iteration 1
with zero findings, calibration ΔEV +10.37 on claude-agent/claude-fable-5), **Bean 0250** (PR #140, `be6cd7b`: surface
agent returncode, stderr diagnostics, and command lines in `review_ensemble.py` when reviewers fail; calibration ΔEV
+4.37 on antigravity-agent/gemini-3.8-flash-medium), **Bean 0243** (PR #141, `e130dfb`: purge harness bean references
and rename `[BEAN 0034 SAFETY HALT]` to `[SAFETY HALT]` across code, tests and docs; 3/3 consensus on iteration 1 with
zero findings, calibration ΔEV +6.84 on claude-agent/claude-fable-5), **Bean 0201** (PR #142, `e10b4d4`: planner,
executor, and reviewer prompts carry module-layout and complexity rules; 3/3 consensus on iteration 2, calibration ΔEV
+6.27), **Bean 0241** (PR #143, `a17a854`: persist the Stage 4 review loop sandbox across iterations with incremental
git sync; converged at iteration 10, calibration ΔEV +18.97), **Bean 0195** (PR #144, `cc2ed3e`: `GitRepository` adapter
in `sandbox_executor.git` routing all executor git calls; 3/3 consensus on iteration 1, calibration ΔEV +7.10), **Bean
0233** (PR #145, `8b1e668`: fail fast when the resolved `--target-worktree` or a checkpoint's recorded worktree is not
an attached git working tree; 3/3 consensus at iteration 4 on claude-agent/claude-opus-5-5, calibration ΔEV +14.85), and
**Bean 0149** (PR #146, `4682449`: globally unique `P-...` and `E-...` stage IDs with 8-char hex disambiguators and
ledger duplicate validation; 3/3 consensus at iteration 5). **Bean 0254** (split `flow.py` into a `flow/` package,
move-only) is currently in progress. New beans logged: **Bean 0252** (resolver preserves its rejected diff and full test
output on pre-push failure), **Bean 0253** (calibration branches from the origin PR head, not a stale local ref), **Bean
0255** (streaming per-issue resolvers during Stage 4 CI & review with a single consolidated commit), **Bean 0256**
(resolver agent committing locally causes `_commit_and_push_resolution` to skip verification and `git push`), and **Bean
0257** (dual Actual EV in Stage 5 calibration: report both Clean/Intrinsic EV without bugs and Observed EV with bugs
included).

---

## Key Milestones Completed (Beans 0080 – 0251)

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
      tests), passed 3/3 ensemble consensus review, completed Stage 5 calibration, and merged as `72c8d36`.
    - `0156` (research): evaluated beads (`bd`, v1.3.2, Dolt-backed) for target-native issue tracking. Mapped 213
      existing beans, recommended per-target trackers (`hac-` and `hcoh-`), offline `refs/dolt/data` sync, migrating ~47
      open beans, and freezing closed history in the read-only harness. Spawned Beans 0214-0218 and codified
      `FLOW_PR_DRIVER.md`.
23. **Stage 4 Role Container Review Dispatch, and Coherence Proxy Package Decomposition (Beans 0179, 0204 / HAC PR #116
    & Coherence PR #37, 2026-10-30)**:
    - `0179` (HAC #116, `b746408`): routed Stage 4 reviewer turns through the `review-loop` role container via
      `_dispatch_role()`, eliminating host-side agent execution while preserving append-only ledger provenance; passed
      3/3 unanimous ensemble consensus review and completed Stage 5 calibration (`4f119cd`, EV predicted 68.62 / actual
      78.04, $\Delta\text{EV} = +9.42$).
    - `0204` (Coherence #37, `9b001c3`): decomposed monolithic `mitm_addon.py` (2,348 lines) into modular `proxy/`
      package by concern (`scrubbing.py`, `wire_log.py`, `timing.py`, `metrics.py`, `routing.py`, `dashboard.py`,
      `normalise/anthropic.py`, `translation/gemini_openai.py`, and `addon.py`), preserving backwards-compatibility
      re-exports; passed 3/3 unanimous ensemble consensus review and completed Stage 5 calibration.
24. **HAC CLI Modular Package Decomposition (Bean 0188 / HAC PR #117, 2026-10-30)**:
    - `0188` (HAC #117, `76fe3ea`): split monolithic `cli.py` (2,185 lines) into a modular `cli/` package of
      self-registering command modules under `sandbox_executor/cli/commands/`, unblocking concurrent CLI maintenance and
      option refactoring; passed 3/3 unanimous approval and completed Stage 5 calibration (`1424a26`).
25. **Hermetic Index Test Guard and Coherence Addon Hook Pipeline Decomposition (Beans 0150, 0205 / HAC PR #118 &
    Coherence PR #38, 2026-10-30)**:
    - `0150` (HAC #118, `e8e9a5d`): eliminated hermeticity leaks where flow tests mutated the real checkout index
      (`holon-knowledge/.index/action_index.db`) and guarded `.git` from sandbox mutations; passed 3/3 unanimous
      consensus review, completed Stage 5 calibration (`09ba249`), and merged into `main`.
    - `0205` (Coherence #38, `e3dcc1a`): decomposed `MitmproxyAddon.request` (209 lines, CC 65) and `response` (187
      lines, CC 43) hooks into an ordered step pipeline under `proxy/steps/`; passed 3/3 unanimous ensemble consensus
      review, completed Stage 5 calibration (`6a6ec15`), and merged into `main`.
26. **Mandatory CLI Agent & Model Options and Coherence Dedicated Provider Modules (Beans 0219, 0206 / HAC PR #119 &
    Coherence PR #39, 2026-10-31)**:
    - `0219` (HAC #119, `0bb1615`): made `--agent` and `--model` mandatory CLI options across all `holon` commands
      (`flow`, `intent`, `plan`, `execute`, `review`, `calibrate`), eliminating silent fallback defaults to deprecated
      or unavailable model tiers; passed 3/3 unanimous ensemble consensus review, completed Stage 5 calibration
      (`4f20f01`), and merged into `main`.
    - `0206` (Coherence #39, `ca43eb9`): decomposed wire format handling into dedicated provider modules under
      `proxy/providers/` (`base.py`, `anthropic.py`, `openai.py`, `gemini.py`, `translation.py`) conforming to
      `ProviderFormat` protocol; passed 3/3 unanimous ensemble consensus review, completed Stage 5 calibration
      (`45ff23d`), and merged into `main`.
27. **Platform-Agnostic Review Terminology and Coherence A/B & Metrics Domain Decomposition (Beans 0220, 0207 / HAC PR
    #120 & Coherence PR #40, 2026-10-31)**:
    - `0220` (HAC #120, `922289f`): removed GitHub-specific PR wording across CLI help, engine logging, consensus report
      generator, and prompt templates, standardizing on platform-agnostic terms like 'Review Loop' and 'Change Diff';
      passed 3/3 unanimous ensemble consensus review, completed Stage 5 calibration (`8d5e57d`), and merged into `main`.
    - `0207` (Coherence #40, `d6f1655`): moved A/B evaluation and offline metrics aggregation domain logic out of CLI
      command handlers into dedicated domain packages `ab_testing/` and `metrics/`; passed 3/3 unanimous ensemble
      consensus review, completed Stage 5 calibration (`ffd6c9e`), and merged into `main`.
28. **Engine/Skill Review-Loop Standardisation, Engine-Owned Single-Shot Loop, Native Stage 4 Resolver, 1-Hour Default
    Turn Timeout, 2-Hour Review Iteration Budget, Post-Review CI Gating, Resolver CI Repair, Continuous Learning
    Commits, and Resolver Execution / Fail-Closed Verification (Beans 0221, 0228, 0229, 0232, 0237, 0235, 0238, 0239,
    0240 / HAC PRs #123–#131, 2026-11-05 to 2026-11-06)**:
    - `0221` axes 1-3 (HAC #123, `43f990a`): unified the consensus review comment template across the harness
      `pr-review-loop` skill and `sandbox_executor.review_report`, `review_loop.template.md`, and `scaffold.py`; passed
      3/3 consensus review, calibrated (`c680406`, $\Delta\text{EV} = +34.21$), and merged into `main`.
    - `0228` (HAC #124, `bfecf0f`): made the flow engine the sole owner of the 25-iteration review budget and
      checkpointed counter, dispatching single-shot review containers with a separate `--iteration` label; passed 3/3
      consensus review, calibrated (`9be1724`, $\Delta\text{EV} = +17.68$), and merged into `main`.
    - `0229` (HAC #125, `baf3f8c`): implemented the native Stage 4 resolver inside the review loop (review and resolve
      per engine iteration, `applied`/`rejected` dispositions in `executions.jsonl`, 3-iteration `no-convergence` guard,
      single exit posting), closing all five standardisation axes of `0221`; passed 3/3 consensus review, calibrated
      (`eb3302f`), and merged into `main`.
    - `0232` (HAC #126, `0f80271`): bumped `DEFAULT_TURN_SECONDS` from 300.0 s to 3600.0 s (1 hour) in
      `sandbox_executor.budgets` alongside unit/CLI tests and documentation; traversed all 5 stages hands-free (1 review
      iteration, calibrated $\Delta\text{EV} = +4.64$) and merged into `main`.
    - `0237` (HAC #127, `6b9264c`): increased `StageBudgets.review_iteration` from 900.0 s (15 min) to 7200.0 s (120
      min) in `sandbox_executor.budgets` alongside unit and flow tests; traversed all 5 stages hands-free (calibrated
      $\Delta\text{EV} = +3.80$) and merged into `main`.
    - `0235` (HAC #128, `f8220eb`): made Stage 4 GitHub CI a post-review gate in `sandbox_executor.flow`, launching the
      reviewer ensemble immediately while CI runs in parallel and bypassing pending CI waits when reviewers object;
      traversed all 5 stages (calibrated $\Delta\text{EV} = +10.93$) and merged into `main`.
    - `0238` (HAC #129, `ecec262`): synthesised first-class `FindingRow` for `FIND-CI` in `sandbox_executor.flow` and
      updated `entrypoint/review_loop.py` so the resolver automatically repairs CI and test failures even when code
      reviewers approve; traversed all 5 stages (calibrated $\Delta\text{EV} = +11.52$) and merged into `main`.
    - `0239` (HAC #130, `1619cec`): added `_commit_stage5_promoted_artifacts()` in `flow.py` to stage and commit
      promoted `holon-knowledge/kb/` and `holon-knowledge/wisdom/` files to `/calibrated` and fast-forward into the PR
      head branch and diff; traversed all 5 stages hands-free and merged into `main`.
    - `0240` (HAC #131, `3c752e6`): constructed runner CLI command list via `runner.build_command()` before invoking
      `run_turn(cmd, cwd=repo_dir)` in `entrypoint/review_loop.py` to fix `TypeError`, and enforced fail-closed
      verification defaults (`lint_passed`/`tests_passed` default to `False`); traversed all 5 stages and merged into
      `main`.
29. **Immutable KB/WB Facts, Worktree Auto-Provisioning & Validation, Persistent Review Sandbox, Prompt Complexity
    Rules, Executor GitRepository Adapter, and Globally Unique Stage IDs (Beans 0242, 0244, 0245, 0247–0251, 0236, 0243,
    0201, 0241, 0195, 0233, 0149 / HAC PRs #132–#146, 2026-11-06 to 2026-11-09)**:
    - `0242` (#132, `d932d48`), `0244` (#133, `2a56a89`), `0245` (#134, `4113f0d`), `0247` (#135), `0248` (#136), `0249`
      (#137), `0251` (#138), `0236` (#139, `d0c1334`, single consensus review post), `0250` (#140, `be6cd7b`, reviewer
      failure observability), and `0243` (#141, `e130dfb`, zero harness bean references) all traversed the 5-stage flow
      and merged.
    - `0201` (#142, `e10b4d4`): planner, executor, and reviewer prompts carry the module-layout, complexity,
      and >1,000-line growth rules (calibrated $\Delta\text{EV} = +6.27$).
    - `0241` (#143, `a17a854`): persisted the Stage 4 review loop sandbox volume across iterations with incremental git
      sync (calibrated $\Delta\text{EV} = +18.97$).
    - `0195` (#144, `cc2ed3e`): added `GitRepository` adapter in `sandbox_executor.git` and routed executor git calls
      through it (calibrated $\Delta\text{EV} = +7.10$).
    - `0233` (#145, `8b1e668`): fail-fast validation that `--target-worktree` and checkpoint `repo_dir` are attached git
      worktrees (calibrated $\Delta\text{EV} = +14.85$).
    - `0149` (#146, `4682449`): globally unique `P-...` and `E-...` stage IDs with 8-character hex disambiguators and
      ledger duplicate validation across concurrent intents.

---

## Active Beans Triage and Prioritisation Matrix

| Priority | Status      | Impact | Sizing | Bean # | Title                                                                                                                        | Domain                     | Dependencies / Notes                                                                                                                                                                                                                                                                                    |
| :------- | :---------- | :----: | :----: | :----- | :--------------------------------------------------------------------------------------------------------------------------- | :------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **P0**   | todo        |  High  |   L    | 0183   | Every flow stage works in its own sandboxed clone; `holon flow` needs no host checkout                                       | Holon Flow / Sandbox       | Stages 1-3 already clone in-container; move checkpoint, engine git checks and Stage 5 calibration into sandboxed clones so concurrent flows never share or require a host worktree. Pairs with 0179, 0149, 0151.                                                                                        |
| **P0**   | todo        |  High  |   S    | 0160   | Review loop burns its iteration budget polling pending CI, then reports test failures                                        | Review Loop / CI           | PR #101 added bounded CI waiting within the iteration budget; remaining: separate `HOLON_REVIEW_CI_WAIT_SECONDS` budget and pending-vs-failed error reporting. Pair with 0234.                                                                                                                          |
| **P0**   | todo        |  High  |   L    | 0151   | Planner estimates the touch set; overlapping concurrent flows are blocked                                                    | Holon Flow / Concurrency   | Unblocked by 0159 (#97 merged), 0201 (#142 merged), and 0149 (#146 merged). Sequence after 0254 (`flow/` package split). Must handle `{parent}--{n}-{slug}` child branches.                                                                                                                             |
| **P1**   | in-progress |  High  |   L    | 0254   | Split `flow.py` into a `flow/` package of focused modules (move only, AST-verified)                                          | Refactor / Architecture    | In progress via `claude-agent`. Supersedes 0187. Splits 5,950-line `flow.py` into focused `flow/` submodules with AST equivalence test and size ratchet, unblocking parallel `flow/` lanes.                                                                                                             |
| **P1**   | todo        |  High  |   S    | 0256   | Resolver agent committing locally causes `_commit_and_push_resolution` to skip verification and `git push`, losing all fixes | Review Loop / Resolver     | Disjoint from `flow.py` (touches `entrypoint/review_loop.py` and `test_review_loop.py`). Capture `pre_resolver_head` before `_run_resolver_agent` and `git reset --soft <pre_resolver_head>` if `HEAD` moved, so `_commit_and_push_resolution` always verifies, attaches trailers, commits, and pushes. |
| **P1**   | todo        |  High  |   M    | 0257   | Dual Actual EV in Stage 5 calibration: report both Intrinsic EV (without bugs) and Observed EV (with bugs included)          | Stage 5 / Calibration      | Disjoint from `flow.py` (touches `calibration.py` + new helper module). Separates `E-...` and converged `REV-...` (`halted_for_human`) outcomes (`ev_clean`) from intermediate bug/failure rows (`ev_with_bugs`) and reports `bug_ev_drag`.                                                             |
| **P1**   | todo        |  High  |   L    | 0255   | Streaming per-issue resolvers during Stage 4 CI & review with single consolidated commit                                     | Review Loop / Concurrency  | Spin up isolated resolvers immediately as each CI pipeline fails (e.g. `Test - Hygiene` at 10 s) while continuing to wait for remaining pipelines, then merge all resolver fixes and push a single commit per iteration. Sequence after 0254 and 0256; pairs with 0234.                                 |
| **P1**   | todo        |  High  |   S    | 0252   | Resolver preserves its rejected diff and full test output on pre-push verification failure                                   | Review Loop / Resolver     | Touches `entrypoint/review_loop.py` (disjoint from `flow.py`; pair with or right after 0256). Saves `.holon/review/iter-N/rejected.patch` and full pytest failure output when `_verify_before_push` fails.                                                                                              |
| **P1**   | todo        |  High  |   S    | 0253   | Stage 5 calibration branches from `origin` PR head, not stale local execution ref                                            | Stage 5 / Calibration      | Fetches and resets local `<execution_branch>` to `origin/<execution_branch>` after Stage 4 resolver pushes so `/calibrated` is always a fast-forward descendant of the PR head. Sequence after 0254.                                                                                                    |
| **P2**   | todo        |  Low   |   XS   | 0246   | Eliminate duplicate review comments in harness `pr-review-loop` skill                                                        | Skills / Harness           | Target-side fix landed in PR #139 (Bean 0236); verify/close remaining harness skill doc wording.                                                                                                                                                                                                        |
| **P1**   | todo        | Medium |   S    | 0234   | Event-driven CI check progress reporting during Stage 4 review                                                               | Review Loop / Logging      | Log total CI pipelines once at start (`Tracking N GitHub CI check(s)...`) and emit a log line only when a check completes or changes state, suppressing 15 s polling noise. Intent in `todo/`; pair with 0160.                                                                                          |
| **P1**   | todo        |  High  |   M    | 0224   | Claude credentials just work: auto-discover the secrets file, map by type, no HOLON_AGENT_KEY                                | Agent Runner / Credentials | Touches `agent_runner.py`/pre-flight only - disjoint from `flow.py`. Kills the `HOLON_AGENT_SETTINGS` echo-pad tunnel; `--settings` value redacted in command echoes. Before 0225.                                                                                                                      |
| **P1**   | in-progress |  High  |   S    | 0227   | Sidecar readiness probe false positive (docker-proxy accepts before mitmproxy binds)                                         | Token Reduce / Proxy       | Fix complete on `fix/0227-proxy-readiness-http-probe` (`36c9765`), suite green; hand-authored under the explicit-instruction exception. Awaiting maintainer call on PR creation.                                                                                                                        |
| **P1**   | todo        | Medium |   S    | 0222   | pi-agent sandbox cannot create `~/.pi/agent/sessions`, so pi-runner flows die at pre-flight                                  | Agent Runner / Sandbox     | Mounting only `~/.pi/agent/models.json` makes Docker pre-create `/home/holon/.pi/agent` as root (EACCES for uid 1000). Add a writable tmpfs overlay for pi sessions/state in `get_agent_session_mounts`.                                                                                                |
| **P1**   | todo        |  High  |   M    | 0189   | Launcher module owns container launch and role dispatch; break the `flow` -> `cli` cycle                                     | Refactor / Architecture    | After 0187 (0188 is merged as #117); unblocks 0200. Runs with 0190 and precedes 0183.                                                                                                                                                                                                                   |
| **P1**   | todo        |  High  |   M    | 0190   | `FlowCheckpoint` and ledger reconciliation own their behaviour; entrypoints stop importing flow                              | Ledger / Holon Flow        | After 0187; 0158 (PR #111, same code) has merged. Precedes 0183. Unblocks 0196, 0199.                                                                                                                                                                                                                   |
| **P1**   | todo        |  High  |   M    | 0191   | One GitHub adapter owns every `gh` call (PR, CI probe, mergeability, review posting)                                         | GitHub / Architecture      | After 0187. Unblocks 0192.                                                                                                                                                                                                                                                                              |
| **P1**   | todo        |  High  |   L    | 0192   | `run_review_loop` and `run_review_stage` become a `ReviewLoop` object with named steps                                       | Review Loop / Refactor     | After 0191. 528 lines, CC 131. Sequence after 0160/0234 (same touch set).                                                                                                                                                                                                                               |
| **P1**   | todo        |  High  |   L    | 0196   | Executor entrypoint `main` becomes an `ExecutionRun` with named steps; module becomes a package                              | Executor / Refactor        | After 0195 and 0190. 798 lines, CC 178 (worst in the repository).                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |   S    | 0175   | Check GitHub token scopes before Stage 3 when the plan touches workflow files                                                | Holon Flow / GitHub        | A 55-minute Stage 3 for Bean 0168 was lost to a push rejected for the missing `workflow` scope. Complements 0171 (#108 merged, refused-push patch salvage).                                                                                                                                             |
| **P1**   | todo        |  High  |   S    | 0157   | `holon flow` auto-enables the mitmproxy sidecar; role containers cannot reach it                                             | Holon Flow / Proxy         | Workaround: `HOLON_TOKEN_REDUCE=0`. Pairs with 0227 (`fix/0227-proxy-readiness-http-probe`).                                                                                                                                                                                                            |
| **P1**   | todo        |  High  |   M    | 0161   | Decomposed sub-intents have no flow path to `main` and do not build on each other                                            | Holon Flow                 | Deferred from #97. Implement the 2026-10-29 rulings: nest under the deciding node, merge into the deciding plan/execution branch, nested PRs automatic, sibling slugs distinct. Docs: PRs #103, #110 and #113 (all merged).                                                                             |
| **P1**   | todo        |  High  |   M    | 0155   | General `HOLON_*` forwarding puts credential-shaped values on the docker argv                                                | Security                   | Already on main. Default fix: send every `HOLON_*` value through the 0600 env-file.                                                                                                                                                                                                                     |
| **P1**   | todo        |  High  |   M    | 0148   | Redact before truncating ledger `error_context`; close `CredentialRedactor` gaps                                             | Security / Ledger          | Route those rows through `redact_agent_secrets`.                                                                                                                                                                                                                                                        |
| **P1**   | todo        | Medium |   M    | 0146   | Plans-ledger correction rows; calibration picks the right predicted metrics                                                  | Calibration / Ledger       | Every calibration in the 2026-10-26 batch needed a manual annotation. Runs before 0197 (same parser).                                                                                                                                                                                                   |
| **P1**   | todo        |  High  |   M    | 0213   | Reflect review-loop skill rules into native Review Loop Holon Agent                                                          | Review Loop / Prompts      | Target: `holon-agentic-coder`. Unblocked now that 0221/0228/0229 are merged: reflects target-branch conflict checks, ledger-only fast resolution, and model fallback into `review_loop.template.md`.                                                                                                    |
| **P1**   | todo        |  High  |   M    | 0214   | Pilot beads (bd) issue tracking inside holon-agentic-coder                                                                   | Issue Tracking / Pilot     | Holon flow against holon-agentic-coder. `bd init` prefix `hac-`, offline config, pin `bd` in image, import open beans, fold in 0147 hac half. Precursor to 0215-0218.                                                                                                                                   |
| **P1**   | todo        |  High  |   S    | 0215   | Deterministic beans-to-beads JSONL converter and real-data dry run                                                           | Issue Tracking / Migration | Harness work. Converts bean frontmatter + body to beads JSONL for `bd import`; verified on all open beans per rule 10. Unblocks 0217.                                                                                                                                                                   |
| **P1**   | todo        | Medium |   S    | 0172   | Stage and turn budgets accept an explicit 'unlimited' value, distinct from unset (default)                                   | Holon Flow / Config        | Workaround today: `HOLON_STAGE_BUDGET_EXECUTE_MINUTES=10080`. Pair with or follow 0232.                                                                                                                                                                                                                 |
| **P1**   | todo        |  High  |   M    | 0173   | holon loads layered .env files (specific overrides broad) that every sandbox stage inherits                                  | Holon Flow / Config        | Project `.env` overrides the broader `.env`. Touches `cli/`; sequence after 0155/0148 and 0174.                                                                                                                                                                                                         |
| **P1**   | todo        | Medium |   M    | 0174   | Document every environment variable holon reads, in one generated and CI-checked reference                                   | Documentation / Config     | After 0172; precursor to 0173, whose layered `.env` needs this reference's allow-list and secret flags.                                                                                                                                                                                                 |
| **P1**   | todo        |  High  |   L    | 0176   | Remove every unittest reference from holon-agentic-coder; the suite is pytest only                                           | Tests                      | Unblocked by 0168 (#99 merged). 59 `TestCase` classes and about 60 `unittest.mock` imports in 29 files. Runs alone: it touches most test files.                                                                                                                                                         |
| **P1**   | todo        |  High  |   M    | 0166   | Pipeline duration dashboard for CI builds                                                                                    | CI / Observability         | Check org Actions performance metrics first. Shares data and baseline with 0163 (#109, #30).                                                                                                                                                                                                            |
| **P1**   | todo        |  High  |   XL   | 0152   | Audit long files; decompose oversized functions (flow.py, cli.py first)                                                      | Refactor / Concurrency     | Umbrella for the Bean 0177 action beans 0185-0200 and 0203-0208; 0185, 0186, 0188, and 0203-0207 are merged. Remaining: `flow.py` split (0187) and per-module lanes.                                                                                                                                    |
| **P2**   | in-progress | Medium |   M    | 0208   | holon-coherence: a `ProxyLifecycle` class owns proxy start-up, readiness and teardown                                        | Proxy / holon-coherence    | In progress as coherence PR #41 (`2f30d6e`): Stage 3 pushed, but both unit jobs are red (9 failures in `test_start.py`, `test_web_token.py`, `test_cli.py`), so Stage 4 has not started. Resume from the existing execution branch; 0203-0207 are merged.                                               |
| **P2**   | todo        | Medium |   M    | 0225   | Claude token lives only in the OS keychain; retire the plaintext secrets file                                                | Agent Runner / Credentials | After 0224 (extends its discovery seam). Keychain-only; one-time migration deletes the file.                                                                                                                                                                                                            |
| **P2**   | todo        | Medium |   L    | 0223   | Audit CLI flags vs HOLON_* env vars: four-kind decision rule, flag>env precedence                                            | CLI / Config               | Exhaustive inventory of every add_argument and os.getenv; boundary-crossing=both, per-invocation=flag, ambient=env-primary, secrets=env-only.                                                                                                                                                           |
| **P2**   | todo        |  High  |   L    | 0226   | End-to-end test for the holon flow commands with full teardown                                                               | Testing / E2E              | Runs on a sub-1B local model via the `local_llm` envelope (no cloud secrets); never opens a PR; unconditional teardown of worktrees and remote `I-…` trees; invariant assertions + bounded whole-run retries. Operator-run `test-e2e` task, excluded from CI.                                           |
| **P2**   | todo        | Medium |   M    | 0181   | Use the `/_` leaf only when referencing a git branch, never on ids                                                           | Holon Flow / Ledger        | `intents.jsonl` `branch` and `parent_intent_id` hold refs; migrate with readers accepting both shapes. After 0161 (overlaps `flow.py`; 0179 is merged).                                                                                                                                                 |
| **P2**   | todo        | Medium |   S    | 0169   | PR #97 residual Nits: split the pasted checkpoint test; complete git_flow §1.5 list                                          | Tests / Docs               | Small; touches `test_flow.py` and `git_flow.md`. Not beside 0187 (both edit `test_flow.py`).                                                                                                                                                                                                            |
| **P2**   | todo        | Medium |   XL   | 0153   | Remove comments and docstrings from all code; make it self-documenting                                                       | Readability                | Per package, with or right after that package's decomposition (which follows its split: 0187, 0188, 0204), not as one repository-wide flow.                                                                                                                                                             |
| **P2**   | in-progress | Medium |   S    | 0147   | Remove harness paths tracked in the target repositories                                                                      | Hygiene                    | `holon-coherence` half merged (PR #29, `68fdf67`; follow-up PR #31, `b52c7e1`). `holon-agentic-coder` half pending (fold into 0214 when beads lands).                                                                                                                                                   |
| **P2**   | todo        | Medium |   M    | 0193   | Decompose the intent and plan stage modules                                                                                  | Holon Flow / Refactor      | After 0187; parallel decomposition lane.                                                                                                                                                                                                                                                                |
| **P2**   | todo        | Medium |   M    | 0194   | `run_execute_stage` becomes an `ExecuteStage` with named steps                                                               | Holon Flow / Refactor      | After 0187; parallel decomposition lane. 306 lines, CC 40.                                                                                                                                                                                                                                              |
| **P2**   | todo        | Medium |   M    | 0197   | Split `calibration.py` into a package; decompose metrics parsing and report generation                                       | Calibration / Refactor     | After 0187 and 0146 (0162 is merged as #112); parallel lane otherwise.                                                                                                                                                                                                                                  |
| **P2**   | todo        | Medium |   M    | 0198   | Agent runner registry: one `RunnerSpec` module per agent                                                                     | Runners / Refactor         | After 0185 (#115 merged); parallel lane.                                                                                                                                                                                                                                                                |
| **P2**   | todo        | Medium |   M    | 0200   | Remove holon-agentic-coder's diverged `token_reduction` copy; holon-coherence is the owner                                   | Token Reduction            | After 0189. Ownership already ruled: holon-coherence owns token reduction.                                                                                                                                                                                                                              |
| **P2**   | todo        | Medium |   M    | 0199   | Decompose ledger query and the knowledge index                                                                               | Ledger / Knowledge         | After 0190; parallel lane. Low bean priority.                                                                                                                                                                                                                                                           |
| **P2**   | todo        | Medium |   M    | 0216   | Holon flow references and drives beads work items (claim on intent, close on merge)                                          | Holon Flow / Beads         | Holon flow against holon-agentic-coder. Intent `work_item` field, `holon intent` claims issue, calibration/merge closes with PR URL. Sequence after 0214.                                                                                                                                               |
| **P2**   | todo        | Medium |   S    | 0217   | Adopt beads (bd) issue tracking inside holon-coherence                                                                       | Issue Tracking / Coherence | Holon flow against holon-coherence. `bd init` prefix `hcoh-`, import open coherence beans from 0215 converter. Sequence after 0214 and 0215.                                                                                                                                                            |
| **P2**   | todo        | Medium |   M    | 0218   | Port harness skills and guidance to bd and sequence the harness retirement                                                   | Harness Deprecation        | Harness work. Retire triage matrix / `prioritise-beans` for `bd ready --json`; port guidance; archive harness read-only after pilots succeed.                                                                                                                                                           |
| **P2**   | todo        |  High  |   L    | 0142   | Real-workload benchmark: Qwen3.8-27B dense vs Flash-Next MoE                                                                 | Model Selection            | Real data only (AGENTS.md item 10).                                                                                                                                                                                                                                                                     |
| **P3**   | todo        |  Low   |   XS   | 0231   | Exhausted-budget error string interpolates raw count while payload reports clamped 0                                         | Flow Engine / Cosmetic     | PR #124 loop deferral (cosmetic, out-of-increment). Touches `flow.py` - bundle with 0230.                                                                                                                                                                                                               |
| **P3**   | todo        | Medium |   M    | 0141   | Tune vmlx prefill/decode levers for both Qwen3.8 models, crash-safe                                                          | vmlx / Performance         | Pairs with 0142.                                                                                                                                                                                                                                                                                        |

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

**Tooling (2026-11-06):** `holon-agentic-coder` `main` (`3c752e6`) and `holon-coherence` `main` (`d6f1655`) are
installed editable and all agent images were rebuilt via `install-holon`, so Stage 3 partial-code salvage (#108),
pure-append ledgers (#111), the calibration-report Prettier fix (#112), Stage 4 in the `review-loop` container (#116),
the modular `cli/` package (#117), mandatory `--agent` / `--model` (#119), the standardised consensus review template
(#123), the engine-owned single-shot review loop (#124), the native Stage 4 resolver (#125), the 3600 s default per-turn
timeout (#126), the 120-minute default `review_iteration` stage budget (#127), post-review CI gating (#128), resolver CI
failure repair (#129), Stage 5 calibration knowledge/wisdom artifact commits (#130), and resolver command execution &
fail-closed verification defaults (#131) are all live. `HOLON_TOKEN_REDUCE=0` stays the workaround until Beans 0227 and
0157 land. Set `HOLON_STAGE_BUDGET_EXECUTE_MINUTES=10080` until Bean 0172 lands.

**Merge / In-Flight State (2026-11-09):** `holon-agentic-coder` PRs #133–#146 all merged (Beans 0244, 0245, 0247, 0248,
0249, 0251, 0236, 0250, 0243, 0201, 0241, 0195, 0233, 0149); trunk is at `4682449`, installed editable with images
rebuilt via `install-holon`. **Bean 0254** (split `flow.py` into a `flow/` package, move-only) is currently in flight
via `claude-agent`. Harness PR #58 merged into `main` and operational tracking PR #59 is open on
`docs/harness-20261106`. `fix/0227-proxy-readiness-http-probe` (`36c9765`, Bean 0227) has a green test suite and awaits
the maintainer's call on PR creation. Coherence PR #41 (Bean 0208, `2f30d6e`) needs its 9 unit test failures resolved on
its execution branch before Stage 4 review and Stage 5 calibration.

Sequential & Disjoint Lanes, holon-agentic-coder (while **Bean 0254** splits `flow.py`, run disjoint modules first):

1. **Bean 0256** (`entrypoint/review_loop.py` + `tests/test_review_loop.py` — **disjoint from `flow.py`**): capture
   `pre_resolver_head` before `_run_resolver_agent()` and `git reset --soft <pre_resolver_head>` if the resolver agent
   committed locally during its turn, preventing `_commit_and_push_resolution()` from seeing a clean working tree and
   skipping verification and `git push`. Can also pair with **Bean 0252** (preserve rejected diff and full pytest output
   on pre-push failure in `entrypoint/review_loop.py`).
2. **Bean 0257** (`calibration.py` + `calibration_ev.py` — **disjoint from `flow.py`**): compute and report **Dual
   Actual EV** in Stage 5 calibration — both `Actual EV — Clean` (`ev_clean`, intrinsic value without
   pre-existing/pipeline bugs, treating `halted_for_human` consensus and `E-...` success as `p_success=1.0`) and
   `Actual EV — Observed` (`ev_with_bugs`, raw end-to-end EV with intermediate failures included), plus `bug_ev_drag`.
3. **Bean 0254** (in-progress on `claude-agent`: split `flow.py` into a `flow/` package of focused modules, move-only,
   proved by an AST comparison, with a size ratchet; supersedes Bean 0187). Once Bean 0254 merges, the `flow/`
   sub-module lanes unlock in parallel:
   - **Bean 0253** (calibration branches from `origin/<E>/_` so `/calibrated` fast-forwards into the PR).
   - **Bean 0255** (streaming per-issue resolvers during Stage 4 CI & review with a single consolidated commit at the
     end of the iteration, paired with **Bean 0234** + **Bean 0160** event-driven CI check progress reporting).
   - **Bean 0151** (planner estimates the touch set and blocks overlapping concurrent flows — now unblocked by Bean 0149
     PR #146 and Bean 0201 PR #142).
4. **Bean 0231** (exhausted-budget error string interpolates raw count while payload reports clamped 0).
5. **Bean 0189** (launcher module for container launch; breaks the `flow`-`cli` import cycle), then **Bean 0190**
   (checkpoint and ledger reconciliation; entrypoints stop importing flow). Both precede **Bean 0183** (every stage and
   engine bookkeeping step sandboxed in its own clone).
6. **Bean 0175** (check GitHub token scopes before Stage 3 starts when the plan touches workflow files), then **Bean
   0146** (plans-ledger correction rows; calibration picks the right predicted metrics). Bean 0197 follows 0146 and 0257
   because they touch `calibration.py`.
7. **Decomposition lanes from Bean 0177** once `0254` lands, in parallel where packages differ: 0191 then 0192 (GitHub
   adapter, `ReviewLoop`), 0193, 0194, 0196 (now unblocked by 0195 PR #144 once 0190 lands), 0197 (after 0146/0257),
   0198 and 0199 (all tracked by umbrella Bean 0152). Bean 0153 runs per package with or right after that package's
   decomposition. **Bean 0213** (reflect remaining skill rules into native review-loop agent) is unblocked now that 0221
   is complete.
8. **Bean 0157** (mitmproxy sidecar reachability, alongside **Bean 0227**), **Bean 0161** (nested sub-intent branches),
   **Bean 0181** (`/_` only on branch refs), **Bean 0155** then **Bean 0148** (redaction), **Beans 0172, 0174, 0173,
   0223** (budgets, env-var reference, layered `.env`, CLI flag vs env audit), **Bean 0200** (holon-coherence owns token
   reduction; after 0189), and **Bean 0176** (pytest-only conversion of every test file; runs alone).

Parallel lanes (disjoint files / repositories):

- **Agent Runner / Credentials lane (`holon-agentic-coder`, disjoint from `flow.py`):** **Bean 0224** (auto-discover
  `~/.holon/secrets/claude-oauth-token`, map by credential type, kill `HOLON_AGENT_KEY` and the echo-pad tunnel; touches
  `agent_runner.py`/pre-flight only), followed by **Bean 0225** (OS keychain storage) and **Bean 0222** (writable
  `~/.pi/agent` tmpfs mount so `pi-agent` flows pass pre-flight).
- **holon-coherence decomposition lane** (disjoint repository): PRs #36 (Bean 0203), #37 (Bean 0204), #38 (Bean 0205),
  #39 (Bean 0206) and #40 (Bean 0207, `d6f1655`) are merged. **Bean 0208** (`ProxyLifecycle`) is in progress as PR #41
  (`2f30d6e`): fix the 9 unit test failures on the existing `E-1793439253-...` branch, then run Stage 4 review and Stage
  5 calibration. Once PR #41 merges, the coherence refactoring lane is complete.
- **Beads adoption lane (from Bean 0156):** **Bean 0214** (pilot beads in holon-agentic-coder, folding in the 0147 hac
  half) and **Bean 0215** (deterministic beans-to-beads JSONL converter and real-data dry run, harness work) in
  parallel, followed by **Bean 0216** (flow integration), **Bean 0217** (adopt in coherence), and **Bean 0218** (port
  harness skills to `bd` and archive harness).
- **E2E testing, CI observability, and local model benchmarking:** **Bean 0226** (`test-e2e` on a sub-1B local model
  with full teardown), **Bean 0166** (CI pipeline duration dashboard), and **Beans 0142 / 0141** (Qwen3.8 benchmarking
  and vmlx tuning).
