# Holon Ecosystem Bean Triage and Prioritisation Matrix

**Last Updated:** 2026-11-26 21:01:22 UTC

## Executive Summary

The harness drives every `holon-agentic-coder` change through the 5-stage Holon flow and the `pr-review-loop`, and the
maintainer merges each pull request into `main`. On 2026-11-24 the bean set was re-audited: `holon-agentic-coder` `main`
moved to PR #270 (`0387`, merge commit `bfbd9f4`), after PR #269 (`0226`, merge commit `407ad39`) earlier the same
morning. Beans `0387` and `0389` completed today, and Bean `0406` (harness, uncommitted on `docs/harness-20261123`) is
complete. Beans `0415` to `0421` were logged since the last run (`0415` and `0421` closed after the maintainer raised
Docker memory to 32 GB); `0419` is the CI timing gate failure that withdrew PR #270's consensus. Maintainer priority for
today: cutting pipeline time first, with `0403` and `0405` in flight; `0407` (P0) stops re-running the full review when
nothing reviewable changed; `0255` (P0) makes the resolver start on the first pipeline failure and fix every failure of
the run. Concurrent flows on overlapping files forced repeated syncs and re-reviews earlier on (141 review-loop passes,
about 10M+ tokens), so flows that touch the same files still run one after another; only flows with disjoint touch sets
run together.

- **Total Tracked Beans**: 539 (excluding template)
- **Completed**: 380 (70.5%)
- **Scrapped / Superseded**: 14 (2.6%)
- **Active**: 145 (26.9%), of which 20 are in progress, 123 are todo and 2 are draft

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

**2026-11-06 to 2026-11-09:** Seventeen further `holon-agentic-coder` flow PRs merged: **Bean 0244** (PR #133,
`2a56a89`, merged 2026-11-06: immutable append-only KB/WB fact records in `wisdom.py` with hermetic no-touch
assertions), **Bean 0245** (PR #134, `4113f0d`: fix resolver runner build command), **Bean 0247** (PR #135: flow
auto-creates the target worktree), **Bean 0248** (PR #136: `holon models` command), **Bean 0249** (PR #137: replace
`--repo-dir` with canonical `--target-worktree`), **Bean 0251** (PR #138: pass prompts to agent runners via files),
**Bean 0236** (PR #139, `d0c1334`: post the Stage 4 consensus review exactly once via `gh pr review` with a single
`--comment` fallback on the HTTP 422 self-review restriction, retiring the duplicate unconditional `gh pr comment`; 3/3
consensus on iteration 1 with zero findings, calibration ΔEV +10.37 on claude-agent/claude-fable-5), **Bean 0250** (PR
#140, `be6cd7b`: surface agent returncode, stderr diagnostics, and command lines in `review_ensemble.py` when reviewers
fail; calibration ΔEV +4.37 on antigravity-agent/gemini-3.8-flash-medium), **Bean 0243** (PR #141, `e130dfb`: purge
harness bean references and rename `[BEAN 0034 SAFETY HALT]` to `[SAFETY HALT]` across code, tests and docs; 3/3
consensus on iteration 1 with zero findings, calibration ΔEV +6.84 on claude-agent/claude-fable-5), **Bean 0201** (PR
#142, `e10b4d4`: planner, executor, and reviewer prompts carry module-layout and complexity rules; 3/3 consensus on
iteration 2, calibration ΔEV +6.27), **Bean 0241** (PR #143, `a17a854`: persist the Stage 4 review loop sandbox across
iterations with incremental git sync; converged at iteration 10, calibration ΔEV +18.97), **Bean 0195** (PR #144,
`cc2ed3e`: `GitRepository` adapter in `sandbox_executor.git` routing all executor git calls; 3/3 consensus on iteration
1, calibration ΔEV +7.10), **Bean 0233** (PR #145, `8b1e668`: fail fast when the resolved `--target-worktree` or a
checkpoint's recorded worktree is not an attached git working tree; 3/3 consensus at iteration 4 on
claude-agent/claude-opus-5-5, calibration ΔEV +14.85), **Bean 0149** (PR #146, `4682449`: globally unique `P-...` and
`E-...` stage IDs with 8-char hex disambiguators and ledger duplicate validation; 3/3 consensus at iteration 5), **Bean
0254** (PR #147, `7258f61`: `flow.py` split into a `flow/` package, move-only, AST-verified, with a per-module size
ratchet; 3/3 consensus at iteration 5 on claude-agent/claude-opus-5-5, calibration ΔEV −59.40, distorted by Beans 0257
and 0253), **Bean 0258** (PR #148, `b6cd9a6`: pinned `uv` 0.13.7 in the `holon-base` image with a build-time smoke
check; a resolver that cannot run its checks or whose container fails now halts the review loop; the consensus post
reports the real approval fraction and open findings; 3/3 consensus at iteration 5 on claude-agent/claude-opus-5-5,
calibration ΔEV −65.23, distorted by Beans 0257 and 0253), **Bean 0257** (PR #149, `c554e8e`: dual Actual EV in Stage 5
calibration via `calibration_ev.py` and `calibration.py` reporting both Clean/Intrinsic EV without bugs and Observed EV
with bugs included plus Bug EV Drag; 3/3 consensus at iteration 4 on antigravity-agent/gemini-3.8-flash-medium,
predicted EV +6.24, Clean EV +6.07 / ΔEV_clean −0.17, Observed EV −2.43, Bug EV Drag +8.50), **Bean 0259** (PR #150,
`8000794`: `holon flow` redirects a `main` target to a `flow-<slug>` worktree off `origin/main` and never mutates the
`main` worktree; default-branch checkpoints and the direct `review`, `review-loop` and `calibrate` commands are refused;
3/3 consensus at iteration 3 on claude-agent/claude-opus-5-5, calibration ΔEV +29.58), **Bean 0256** (PR #151,
`61796c6`: resolver captures `pre_resolver_head` before `_run_resolver_agent` and soft-resets any local agent commits in
`_commit_and_push_resolution`, ensuring pre-push verification, canonical review trailers, and git push are never
skipped; 3/3 consensus at iteration 5, calibrated ΔEV +0.53), **Bean 0266** (PR #153, `fe3b540`: the six CI workflows
run on pull requests into any base branch so stacked sub-intent PRs are tested; 3/3 consensus at iteration 5 on
claude-agent/claude-opus-5-5, calibration ΔEV +20.60), **Bean 0268** (PR #154, `b63fce7`: carry unmerged calibration
reports into `main`), and **Bean 0161** (PR #158, `14886b8`: the plan decides decomposition; children nest under and
merge into the plan branch; combined PR reaches `main`; unanimous 3/3 consensus at iteration 6 on
claude-agent/claude-opus-5-5, closing Bean 0161). New beans logged: **Bean 0252** (resolver preserves its rejected diff
and full test output on pre-push failure), **Bean 0253** (calibration branches from the origin PR head, not a stale
local ref), **Bean 0255** (streaming per-issue resolvers during Stage 4 CI & review with a single consolidated commit),
**Bean 0260** (never post intermediate review iterations or aborted review passes to PR), **Bean 0261** (deduplicate and
streamline PR review evaluation line in consensus report), **Bean 0262** (mount host-provisioned worktree into sandbox
containers to eliminate in-container git cloning and mid-crash state loss), **Bean 0263** (retire flow.py move-proof
snapshot and its test), **Bean 0264** (read module size budgets from configuration not code), **Bean 0265** (split
cli/**init**.py into focused modules), **Bean 0267** (Stage 3 measured test pass rate), and **Bean 0269** (deferred nits
from PR 158 review loop).

**2026-11-10 to 2026-11-11:** **Bean 0262** (host-provisioned worktree mounted into the role containers) first merged as
PR #159 (`80b844d`) after the flow posted `APPROVED (3/3)`, although reviewer 3's final verdict was CHANGES_REQUESTED
with a critical Security finding: the shared git directory let a sandbox write a sibling worktree's admin files and so
run code on the host. **Bean 0272** reverted it (PR #160, `2faa325`). **Bean 0273** (PR #161, `7837fa4`) fixed the
cause: the consensus verdict now comes only from what the reviewers returned, adjudication suppression covers nits only,
critical, important and Security findings are never filtered, the posted review reports each verdict exactly, and a
rejection of an important or higher finding needs evidence. **Bean 0262** was re-landed as PR #162 (`dd00fb9`): a
read-only overlay of the git directory's `worktrees/` area, with the mounted worktree's own admin directory writable,
plus `rr-cache` and `MERGE_RR` protection. A hand-assembled PR run through the repaired `pr-review-loop`, it reached a
genuine unanimous 3/3 with zero findings at iteration 16 of 25, CI 11/11. **Bean 0183** was scrapped as superseded by
per-flow worktrees. Usage-limit handling now waits out a named reset and resumes automatically (flow runner and review
loop), and the flow runner sends a push notification when it ends. New beans: **0263** to **0265**, **0267**, **0269**,
**0271**.

**2026-11-11 to 2026-11-12:** the merge train landed in order: **Bean 0160** (PR #164, `97731e2`, review loop waits for
CI outside its iteration budget), **Bean 0274** (PR #165, `660c50b`, every flow stage uses the host worktree) and **Bean
0275** (PR #166, `0528a63`, decomposed flow branch names stay under GitHub's 255-character full-ref limit). #165 then
broke every new flow at Stage 1: the intent and plan containers wrote `git config --local` into the shared repository
(**Bean 0276**, hand-authored fix, PR #168, `56f53dd`, merged after a 3/3 review-loop approval). The first flows then
showed that Stage 4 cannot run in the review-loop container, which has no ssh: **Bean 0282** (PR #171, `5d30bda`, no
in-container fetch in the review target) merged after a host-driven review loop, **Bean 0224** (PR #170, `0990f34`,
claude credential auto-discovery by token type) merged on a host-driven review loop and calibration, and **Bean 0284**
(PR #172, `0181186`, the execution-diff check no longer fetched in the container) closed the remaining fetch site.
**Bean 0283** logs that the token-reduction proxy's `cache_control` injection makes sonnet planner calls fail with an
API error that the engine writes as the plan (`HOLON_TOKEN_REDUCE=0` is the workaround). The train also exposed four
flow-engine defects, logged as **Beans 0277** (executor commits carry a `Co-Authored-By` trailer), **0278** (concurrent
flows collide on plan file and review ids), **0279** (executor loses its push on a non-ledger sync conflict) and
**0280** (no CI re-check after the calibration push), plus **Bean 0281** (carry the one calibration report that missed
`main`). New beans: **0276** to **0284**. **2026-11-12 (later):** **Bean 0285** (PR #175, `f02a826`, a failed resolver
pre-push gate names the failed tests, keeps the tail and writes the full output to a git-ignored file) merged after a
host-driven review loop and calibration, with the in-container test skipped and CI supplying results. The run also
logged **Beans 0286** (children test fetches origin), **0287** (interrupted Stage 3 leftovers block the resume) and
**0288** (Stage 4 posts a changes-requested review before consensus). **Bean 0289** (PR #176, `7464836`, the suite
isolation fixture scrubs `CLAUDE_CODE_OAUTH_TOKEN` and `ANTHROPIC_API_KEY`, which had failed four `test_cli.py` tests
inside the credentialed review container) merged after the review loop and calibration. **Bean 0280** (PR #173,
`37c59e5`, Stage 5 reports CI on the final head after the calibration push) then merged; its container pre-push gate
passed. **Bean 0286** (PR #174, `a5550b5`, the children test is hermetic and a network guard fails any test that reaches
a remote) closed the run. **Bean 0288** (PR #177, `89b2530`, Stage 4 posts its review only on a clean approval or at the
iteration cap) merged next, then **Bean 0287** (PR #178, `ebfa3bb`, a Stage 3 resume commits interrupted leftovers as
partial work) completed the chain.

**2026-11-17 to 2026-11-18:** Bean 0297 (Stage 5 reruns when the pull request head moves after calibration) went in
progress with PR #203 open on `holon-agentic-coder`, and Bean 0320 (NVM storage, Homebrew path precedence and the
Makefile bootstrap message) is in progress. New beans: **Bean 0321** (short flow branch names: three-letter agent
tickers, rule-based model codes, no hex, plans keyed by intent; decided with the maintainer on 2026-11-18) and **Bean
0322** (remove the `gemini-agent` runner, made redundant by `antigravity-agent`).

**2026-11-18 (later):** **Bean 0297** merged as HAC PR #203 (`d5fbd14`), so Stage 5 now reruns when the pull request
head moves after calibration. The PR merged with two iteration-3 nits still open, and Bean 0323 carries them. **Beans
0320, 0324 and 0326** completed (dev-env PRs #21, #22 and #24), and **Bean 0325** was scrapped. **Bean 0328** (dev-env:
Neovim plugins, tmux navigation, Homebrew Go toolchain) is in progress. New bean: **Bean 0323** (crashed resolver turn
records findings as rejected).

**2026-11-19:** **Bean 0316** merged as HAC PR #205 (`3d10c28`, flow slug `macgate`). The macOS unit timing gate now
compares the pull request's test step with the base branch's time on the same runner class, under a 600 s ceiling, and a
timing failure on a head that adds only bookkeeping files gets one automatic rerun before the approval is withdrawn.
Review approved 3/3 at iteration 3, and calibration predicted 34.25 against an actual 60.61 (delta +26.36). **Beans 0327
– 0330** and **Bean 0332** (dev-env PR #29) completed. The `holon` CLI and its images were rebuilt from `main` the same
day. **Bean 0331** (an overlap override moves the plan tip) is in progress; its harness half is done. The Bean 0321
`shortref` flow finished Stage 3 locally after #205 merged; it is unpushed and waits for a resume into Stage 4. Merged
branches, worktrees, review artifacts and scratch files were cleaned up the same day.

**2026-11-20:** **Bean 0321** merged as HAC PR #206 (`cac463b`, flow slug `shortref`) and is completed: flow branches
drop the hex and use runner tickers and derived model codes, and plan files are keyed by intent. Review approved 3/3 at
iteration 4; calibration predicted 33.50 against an actual -37.51. **Bean 0331**'s target half is unblocked. New beans:
**Bean 0335** (a Stage 3 resume ignores commits on the execution branch tip) and **Bean 0336** (a Stage 4 review
container leaves the flow worktree on a detached HEAD). Bean 0323's `rescrash` flow is paused at Stage 3 admission,
refused by the `shortref` overlap. The `shortref` worktree and local branches were removed, and the stray pushed
execution branch `E-1795130302-4856d0ac` was deleted.

**2026-11-20 (later):** **Bean 0323** merged as HAC PR #207 (`d0b3e23`, flow slug `rescrash`) and is completed: a
resolver turn that fails writes no adjudication rows and leaves its findings open, a rejection needs a reason, and a
review resume sends open findings to the resolver first. Review approved 3/3 at iteration 3; calibration predicted 61.85
against an actual 77.72 (delta +15.87). **Bean 0337** is new (a flow refused at Stage 3 admission still counts as in
flight). Beans 0331 and 0335 merged as PR #208 (`00fa535`) and are completed. **Bean 0337** merged as PR #209
(`7dc0342`) and is completed. **Bean 0283** merged as PR #210 (`30d7c77`) and is completed.

**2026-11-21:** every active bean was audited against `origin/main`. Locations moved by the `flow/` and `cli/` package
splits were corrected in Beans 0157, 0175, 0181, 0191-0194, 0200, 0231, 0255 and 0269; Bean 0146 and Bean 0197 were
narrowed to what remains after PR #213; the blocked-by links to completed or scrapped Beans 0168, 0185, 0187 and 0195
were cleared. New: **Bean 0347** (Stage 4 says halted for human review although consensus approval was reached and the
flow carries on to Stage 5). The audit found no bean already done by PRs #209 to #220 beyond those already completed.

**2026-11-22 to 2026-11-23:** twenty-one target PRs merged across `holon-agentic-coder` and `dev-env`: **Bean 0322**
(HAC #222, `e2ba3c2`: complete removal of `gemini-agent`), **Bean 0172** (HAC #225, `4811599`: `unlimited` stage and
turn budgets), **Bean 0348** (HAC #226, `3ee9c4e`: admission uses actual PR files), **Bean 0199** (HAC #227, `43d278c`:
ledger query and knowledge index decomposed), **Bean 0193** (HAC #228, `5fbd2d0`: intent and plan stages decomposed),
**Bean 0349** (HAC #229, `ccb7a6f`: Antigravity writable `brain`/`conversations` tmpfs and `empty_diff` excerpt), **Bean
0196** (HAC #234, `2ec094e`, plus children #231–#233: `ExecutionRun`), **Bean 0194** (HAC #236, `b22258d`:
`ExecuteStage`), **Bean 0358** (HAC #235 `134e333` and #237 `032d9d44`: resolver honours turn budgets, foreground test
prompts, and supervisor live-child-process stall guard), **Bean 0357** (HAC #238, `8afc215a`: `--skip-review` removed),
**Bean 0355** (HAC #240, `192c6e8`: `holon calibrate` runs full Stage 5), **Bean 0356** (HAC #239, `4e1e761`: resume
flags override checkpoint), **Beans 0347 & 0354** (HAC #230, `f17f4b8`: Stage 4 `review: approved` status & fresh local
test gate), **Bean 0189** (HAC #241, `0f0089d`: `launcher/` package breaks `flow` -> `cli` cycle), plus `dev-env` PRs
#31 (**Bean 0344**, `0ba3e94`), #32 (**Bean 0346**, `d6b07de`), #33 (**Bean 0361**, `425ff6fe`: Fish Conda/Homebrew
hooks & clean-env multi-shell tests), #36 (**Bean 0351**, `a9dacf46`: Ansible `deb822_repository` & task hygiene,
unconditional WSL exclusion of Ghostty/Warp, and `tmux` `set -g mouse on`), #37 (**Bean 0364**, `4b1391c3`: define
`devenv_user`, skip WSL GUI terminal wizard prompt, and audit Ansible Jinja2 variables in tests), #38 (**Bean 0365**,
`68ddec98`: disable `expand_argument_vars` on Conda clean-shell command tasks, enforce static `$VAR` command hygiene,
and add hermetic `ansible-playbook` verification test), #39 (**Bean 0366**, `eeb2032d`: install `zsh` on Linux/WSL,
unify NVM storage strictly under `versions/node`, eliminate `versions/node/versions` symlink loop, and add hermetic Fish
migration tests), and #40 (**Bean 0370**, `22ca3862`: add tracked `dotfiles/zsh/.zprofile`, isolate `node` shell checks,
fix Fish `follow: true` & Homebrew `path` dirs, and add real Ubuntu/WSL converge CI + Docker `make test-ubuntu`). Those
PRs (#243, #244 and #245) were open at the morning checkpoint and merged on 2026-11-23,(`0191`) are merged, and new
**Bean 0360** logs duplicate `P-` branch creation after an interrupted Stage 2. Pre-triage audit (2026-11-23): **Bean
0353** scrapped as a duplicate of `0354`; stale blockers cleared on `0189`, `0197`, `0198`, `0265`, `0270`, `0333`;
`0176` re-measured at 144 files; `0181` re-pointed to `entrypoint/executor/run.py`; new beans `0350`–`0352` and
`0354`–`0361` triaged.

**2026-11-23 (post-#266):** PR #266 (Bean `0374`, sidecar scratch outside worktrees) merged to `main` (`e0251206`),
bringing merged HAC PRs today to 24 and completed beans in this wave to 18. Open HAC PRs: #263 (`0378`) and #267
(`0382`) refreshing ledger conflicts via `--from-stage calibrate`, plus #265 (`0376` child 3, waiting on the 600 s macOS
CI timing ceiling decision). Backfilled Bean `0381` across both `holon-coherence` and `holon-agentic-coder`. Newly
logged beans `0389` and `0390` added to triage.

---

## Key Milestones Completed (Beans 0080 – 0406, plus 0360, 0374)

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
    Rules, Executor GitRepository Adapter, Globally Unique Stage IDs, `flow/` Package Split, Pinned Container `uv`,
    Dual-EV Calibration, Main Worktree Guard, Resolver Commit Normalisation, All-Branch CI, and Plan-Owned Decomposition
    (Beans 0242, 0244, 0245, 0247–0251, 0236, 0243, 0201, 0241, 0195, 0233, 0149, 0254, 0258, 0257, 0259, 0256, 0266,
    0268, 0161 / HAC PRs #132–#151, #153, #154, #158, 2026-11-06 to 2026-11-10)**:
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
    - `0254` (#147, `7258f61`): decomposed monolithic `flow.py` (6,159 lines) into the modular `sandbox_executor/flow/`
      package (`stages/`, `git_refs.py`, `ci_gate.py`, `review_consensus.py`, etc.) with AST-verified move-only parity
      and per-module size ratchets.
    - `0258` (#148, `b6cd9a6`): pinned `uv` 0.13.7 in `holon-base` with a build-time smoke check and made resolver
      check/container failures fail-closed in Stage 4.
    - `0257` (#149, `c554e8e`): implemented Dual Actual EV in Stage 5 calibration (`calibration_ev.py` and
      `calibration.py`), reporting both Intrinsic/Clean EV (`ev_clean`, without bugs) and Observed EV (`ev_with_bugs`,
      with bugs included) plus `bug_ev_drag` (predicted EV `+6.24`, Clean EV `+6.07` / $\Delta\text{EV}_{\text{clean}} =
      -0.17$, Observed EV `-2.43`, Bug EV Drag `+8.50`).
    - `0259` (#150, `8000794`): `holon flow` now runs a `main` target in a dedicated `flow-<slug>` worktree off
      `origin/main`, never mutating the `main` worktree, and refuses default-branch checkpoints and direct stage
      commands.
    - `0256` (#151, `61796c6`): resolver captures `pre_resolver_head` before `_run_resolver_agent` and soft-resets any
      local agent commits in `_commit_and_push_resolution`, ensuring pre-push verification, canonical review trailers,
      and git push are never skipped (calibrated $\Delta\text{EV} = +0.53$).
    - `0266` (#153, `fe3b540`): the six CI workflows run on pull requests into any base branch so stacked sub-intent PRs
      are tested (calibrated $\Delta\text{EV} = +20.60$).
    - `0268` (#154, `b63fce7`): carried unmerged calibration reports into `main` in one pull request.
    - `0161` (#158, `14886b8`): the plan decides decomposition; children nest under and merge into the plan branch;
      combined integration PR reaches `main`.
30. **Sandbox Escape Revert, Honest Review Consensus, and Host-Worktree Mount Re-land (Beans 0272, 0273, 0262 / HAC PRs
    #159–#162, 2026-11-10 to 2026-11-11)**:
    - `0262` (#159, `80b844d`) merged on a false `APPROVED (3/3)` with an open critical sandbox escape; `0272` (#160,
      `2faa325`) reverted it.
    - `0273` (#161, `7837fa4`): consensus comes only from the reviewers' returned verdicts; adjudication suppression
      applies to nits only; the posted review is exact; evidence is required to reject an important or higher finding.
    - `0262` (#162, `dd00fb9`): host worktree mounted into the role containers with the git directory's `worktrees/`
      area read-only; unanimous 3/3 with zero findings at iteration 16, CI 11/11 green.
31. **Stage 5 Calibration Freshness, Harness Test Isolation, Lockfile and Sleep Fixes, and Measured Test Pass Rate
    (Beans 0267, 0290, 0292, 0293, 0294, 0295 / HAC PRs #186–#190, 2026-11-12 to 2026-11-13)**:
    - `0290` (harness, no PR): the flow wrapper exports the Claude auth route from `CLAUDE_CODE_OAUTH_TOKEN` or the
      secrets file, or stops before dispatch naming what is missing.
    - `0292` (#186, `9f2187e`): a red CI check, including a timing gate, blocks the approval and the merge-ready report
      on the final head.
    - `0293` (#188, `54bfd55`): tests that patch `time.sleep` patch only the module under test, so unrelated
      subprocesses cannot trip them.
    - `0294` (#190, `efff3ed`): the committed `uv.lock` matches the project and container Python, so flows stop
      producing lockfile churn. Its calibration report predates the conflict merge, and Stage 5 stopped on the stale
      calibrated branch; Bean 0296 fixed it (PR #193).
    - `0295` (#189, `bde4934`): a rejected resolver diff is saved as a patch the host can read.
    - `0267` (#187, `7a8f086`): Stage 3 records a measured `test_pass_rate`, and the review loop measures tests itself
      when no CI registers. A hand edit outside the flow (`deb5026`, explicit maintainer instruction) fixed the CI wait
      tests' head lookup.
32. **Stage 5 Calibration Rebuild and Review-Loop Posting Honesty (Beans 0260, 0296 / HAC PRs #192–#193, 2026-11-13 to
    2026-11-14)**:
    - `0260` (#192, `3b6c3d7`): the review consensus is posted to the PR only on unanimous approval or when the review
      iteration budget is exhausted; halted iterations (failed verdict, infrastructure error, reviewer crash or timeout)
      stay local in the ledgers. Final review iteration APPROVED 3/3 at head `edb49fd` (predicted EV 50.68, actual
      61.89, calibration delta +11.21).
    - `0296` (#193, `291727e`, merged 2026-11-14): Stage 5 deletes and rebuilds a stale `calibrated` branch that holds
      only the flow's own calibration commits, logs what it replaced, and still fails loudly on foreign commits; the
      final report names the head the calibration report covers. The report covers `cb55140`, not the merged head
      `0e183d8`, which is why Bean 0297 was logged.
    - New: `0297` (todo, P1): Stage 5 reruns automatically when the pull request head moves after calibration, so the
      merged head carries a current report.
33. **Beads pilot and the dev-env wave (Bean 0214 / PR #204, Beans 0291, 0302 – 0315, 2026-11-13 to 2026-11-17)**:
    - `0214` (PR #204, `d09df71`, merged 2026-11-17): `bd` (beads) is piloted inside holon-agentic-coder, pinned in the
      role images, with `hac-` ids and agent guidance for `bd ready`, `--claim` and `bd close`. The 0147 hac half was
      already done on `main` (PR #199). Calibration: expected value predicted 39.65, actual 62.59. The `bd` tarball
      digest pin was left as a follow-up patch.
    - `0291` (completed 2026-11-13): a failed Stage 4 reviewer logs its runner stderr and a real stop reason instead of
      `unknown`.
    - `0302` – `0307` (2026-11-16 to 2026-11-17, dev-env harness): GNU Stow for dotfiles, a host interactive wizard for
      dotfile merge and variants, curl-only bootstrap, uv as a standard toolset package, and a reset of dotfiles, tmux
      and nvim to factory defaults.
    - `0308` – `0315` (2026-11-17, dev-env harness): robust Conda and Ansible detection, collection skips with a
      side-by-side diff, the Node 26 LTS default, Ansible symlink syntax fix, nvm ahead of Homebrew in fish PATH,
      centralised package versions, a single Python prompt, and a reset to pure OS defaults with modular shell snippets.
    - New: `0316` (todo, P1): the macOS unit CI timing gate trips on runner noise and blocks Stage 5. `0317` (todo, P2):
      a GitHub Projects kanban board fed by beads issues.
34. **Stage 5 reruns when the pull request head moves after calibration, and the dev-env wave closes (Bean 0297 / HAC PR
    #203, Beans 0320, 0324, 0326, 2026-11-18)**:
    - `0297` (PR #203, `d5fbd14`, merged 2026-11-18): a calibration report is rechecked against the pull request head,
      and Stage 5 reruns automatically when the head has moved, so the merged head carries a current report. Review
      approved 3/3 at iteration 4. Calibration: expected value predicted 19.15, actual 47.23 (delta +28.08). The PR
      merged with two iteration-3 nits open; they are carried by `0323`.
    - `0320` (dev-env PR #21, `ba7204c`), `0324` (dev-env PR #22, `1063b69`) and `0326` (dev-env PR #24, `b576654`)
      completed. `0325` (corporate proxy SSL certificates for Ansible Galaxy and Conda) was scrapped.
    - New: `0323` (todo, P1): a resolver turn that crashes records its findings as rejected, and a resume never
      adjudicates them. The carried PR #203 nits are part of its action.
35. **The macOS timing gate compares against the base branch, and the dev-env wave completes (Bean 0316 / HAC PR #205,
    Beans 0327 – 0330 and 0332, 2026-11-18 to 2026-11-19)**:
    - `0316` (PR #205, `3d10c28`, merged 2026-11-19): the `unit (macos-latest)` timing gate compares the pull request's
      test step with the base branch's time on the same runner class, under a 600 s ceiling, instead of a fixed 300 s
      budget. A timing failure on a head that adds only ledger, plan and knowledge-base files gets one automatic rerun
      of the failed job before the approval or the final-head check is withdrawn. Review approved 3/3 at iteration 3.
      Calibration: expected value predicted 34.25, actual 60.61 (delta +26.36). The PR also changed
      `flow_module_budgets.json`, outside the bean's stated scope.
    - `0327` (dev-env PR #25), `0328` (dev-env PR #26), `0329` (dev-env PR #27, `12e4831`) and `0330` (dev-env PR #28)
      completed: Neovim through Homebrew with Ansible run in CI, Neovim plugins, seamless tmux navigation, the Homebrew
      Go toolchain, the tmux Stow package moved to `~/.tmux.conf`, and markdownlint installed on Neovim startup.
    - `0332` (dev-env PR #29, `4aeb1c2`, merged 2026-11-19): the Ansible `node` role folds
      `/usr/local/share/ca-certificates` into `~/.config/node/node-extra-ca.pem`, and the managed shells export
      `NODE_EXTRA_CA_CERTS` when that file exists.
    - Tooling: `holon` and its images were reinstalled from `main` at `3d10c28`; `holon-coherence` was not rebuilt.
    - New: `0331` (in progress, P1): each `--allow-overlap` resume moves the plan tip, so Stage 3 partial work is never
      continued. Its harness half is done; the target half was unblocked by the Bean 0321 merge on 2026-11-20.
36. **Short flow branch names: runner tickers, derived model codes, no hex, plans keyed by intent (Bean 0321 / HAC PR
    #206, 2026-11-20)**:
    - `0321` (PR #206, `cac463b`, merged 2026-11-20): flow branches drop the hex and use the runner tickers (`CLA`,
      `ANA`, `PIA`) and derived model codes (`P-{epoch}-CLA-CS5.5`). Plan and calibration files follow the branch name
      under `plans/{intent}/`, with a one-off migration, and slugs are capped at 32 characters. Review approved 3/3 at
      iteration 4. Calibration: expected value predicted 33.50, actual -37.51. The stray pushed branch
      `E-1795130302-4856d0ac` (no ledger row) was deleted; this flow's calibration report still sits at the flat
      `plans/` path and needs moving by a later flow.
    - New: `0335` (todo, P2): a Stage 3 resume ignores commits added to the execution branch tip. `0336` (todo, P2): a
      Stage 4 review container leaves the shared flow worktree on a detached HEAD.
37. **New tmux panes and windows open in the current directory (Bean 0334 / dev-env PR #30, 2026-11-20)**:
    - `0334` (dev-env PR #30, `2a157c4`): `"`, `%` and `c` bind with `-c "#{pane_current_path}"` in
      `dotfiles/tmux/.tmux.conf`. Audit on 2026-11-20 of the other active beans found none solved; partly done and
      stale-blocker beans (0152, 0155, 0190, 0191, 0194, 0197, 0213, 0234, 0246) gained an Audit note.

38. **A resolver crash no longer records findings as rejected, and a resume adjudicates them first (Bean 0323 / HAC PR
    #207, 2026-11-20)**:
    - `0323` (PR #207, `d0b3e23`, merged 2026-11-20): a resolver turn that fails writes no `ACT-RES` rows and its
      findings stay open; a rejection requires a resolver-supplied reason; the checkpoint keeps a halted iteration's
      findings open, and a review resume sends them to the resolver before any new iteration. The PR carries correction
      rows for the two false PR #203 rows and disposes of the two nits PR #203 left open. Review approved 3/3 at
      iteration 3. Calibration: expected value predicted 61.85, actual 77.72 (delta +15.87). Stage 5 was first blocked
      by a macOS timing-gate miss and resumed green after a job rerun.
    - New: `0337` (todo, P1): a flow refused at Stage 3 admission counts as in flight, so two waiting flows can block
      each other.
39. **Stage 3 resume keeps partial work and the branch tip (Beans 0331 and 0335 / HAC PR #208, 2026-11-20)**:
    - `0331` (PR #208, `00fa535`, merged 2026-11-20): the `--allow-overlap` override is recorded once per plan, and a
      partial head that descends from any earlier plan tip is accepted, so Stage 3 partial work is continued. Review
      approved 3/3 at iteration 2. Calibration: expected value predicted 39.61, actual -19.01 (delta -58.62).
    - `0335` (PR #208): a resume continues from the execution branch tip when it descends from the recorded
      `partial_head`, keeping commits added after the failure, and an execution branch is not pushed before its ledger
      row exists.
40. **Blocked admission state (Bean 0337 / HAC PR #209, 2026-11-20)**:
    - `0337` (PR #209, `7dc0342`, merged 2026-11-20): a Stage 3 admission refusal for a touch-set overlap records a
      `blocked` admission state with `blocked_by` and `blocked_since`. Blocked flows are not in flight for anyone else's
      admission, and admission runs under a per-repository lock, oldest `blocked_since` first.
41. **Planner API-error handling (Bean 0283 / HAC PR #210, 2026-11-20)**:
    - `0283` (PR #210, `30d7c77`, merged 2026-11-20): the planner fails the stage on agent API error output instead of
      writing it as the plan, a failed plan attempt leaves no untracked plan file, and `payload_cleaner` leaves existing
      `cache_control` blocks alone and injects only consistent ones. Review approved 3/3 at iteration 1. Calibration:
      expected value predicted 53.40, actual 73.52 (delta +20.12).
42. **Plan refresh after an overlap wait (Bean 0338 / HAC PR #211, 2026-11-20)**:
    - `0338` (PR #211, `1610809`, merged 2026-11-20): a flow admitted after a blocked overlap wait merges `origin/main`
      into its plan branch before Stage 3 executes. Ledger-only conflicts are interleaved by `created_at`; any other
      conflict stops Stage 3 before dispatch with a resumable checkpoint, and the refreshed commit is recorded. Review
      approved 3/3 at iteration 2. Its calibration EV (44.16 predicted, -18.21 actual) is wrong because of Bean 0339.
43. **Review keeps the execution branch (Bean 0336 / HAC PR #212, 2026-11-20)**:
    - `0336` (PR #212, `b6e46e0b`, merged 2026-11-20): new `worktree_head.py` with `reattach_branch`/`restore_branch`,
      wired into the review stage and the review loop. The review restores the execution branch on exit and re-attaches
      a HEAD detached at the branch tip, instead of refusing the resolver. Review approved 3/3 at iteration 3.
      Calibration: expected value predicted 55.50, actual 71.68 (delta +16.18). First flow whose plan branch was
      refreshed onto `main` after an overlap wait, with no merge conflict.
44. **Calibration final outcome by time (Bean 0339 / HAC PR #213, 2026-11-20)**:
    - `0339` (PR #213, `a450005`, merged 2026-11-20): calibration orders a flow's summary rows by parsed `created_at`,
      with `ledger_revision` only as a tie-break, so a Stage 4 consensus row after a Stage 3 `sync_conflict` row is the
      final outcome. A `sync_conflict` that a later row supersedes is not a failure for the observed EV. The logic lives
      in a new `calibration_outcome.py` outside the flow package. Review approved 3/3 at iteration 2. Calibration:
      expected value predicted 52.10, actual 63.28 (delta +11.18).
45. **Module budgets frozen (Bean 0264 / HAC PR #214, 2026-11-20)**:
    - `0264` (PR #214, `bea601e`, merged 2026-11-20): the budgets move to `holon-config/hygiene/module_budgets.json`
      (default ceiling 200 lines; the 22 existing overrides copied unchanged). The budget configuration is frozen: any
      change fails `scripts/check_module_budgets.py` unless authorised by the intent's `module_budget_change` field or
      the maintainer-only `module-budget-change` PR label. Over-budget modules are split. Review approved 3/3 on
      re-review. Calibration: expected value predicted 36.32, actual 70.68 (delta +34.36). Bean 0340 is new: it revisits
      the default and overrides.
46. **Tests never write to the real worktree (Bean 0343 / HAC PR #215, 2026-11-20)**:
    - `0343` (PR #215, `c3c0471`, merged 2026-11-20): decomposition tests write under `tmp_path` through
      `tests/flow/decomposition_fakes.py`. `tests/holon_dir_guard.py`, hooked in `conftest.py`, fails the session on any
      write under `.holon/`. Rules in `docs/hermetic_testing.md`. Review approved 3/3 at iteration 2. Calibration:
      expected value predicted 46.57, actual 62.39 (delta +15.82).
47. **Promoted count is this run only (Bean 0342 / HAC PR #216, 2026-11-20)**:
    - `0342` (PR #216, `eaaabaa`, merged 2026-11-20): Stage 5 logs only the candidates this run newly promoted.
      Promotion skips already promoted candidates instead of re-evaluating them on every run. The new
      `flow/calibrate_promotion.py` keeps the promotion budgets unchanged. Review approved 3/3 at iteration 6.
      Calibration: expected value predicted 40.70, actual 53.52 (delta +12.82).
48. **Review report, review-loop rules, CI progress and ledger redaction (Beans 0261, 0213, 0234 and 0148 / HAC PR #220,
    2026-11-20)**:
    - `0261`: the evaluation line takes its subject from intent `title`, then `slug`, then the target, and no longer
      repeats the branch ref. `0213`: the native review-loop template carries the CONFLICTING/DIRTY gate, ledger-only
      fast resolution, increment-scoped reviews and pre-merge Stage 5 calibration. `0234`: CI wait logs check
      transitions and one final summary, with no heartbeat. `0148`: executor `error_context` redacts before truncation,
      with the wider secret classes. Merged as `9a5454bf`; calibration predicted EV 39.45, actual 59.09.
49. **Plans-ledger correction rows and predicted-metric selection (Bean 0146 / HAC PR #221, 2026-11-20)**:
    - `0146` (PR #221, `68ec164`, merged 2026-11-20): new `calibration_predicted.py` selects the predicted metrics for
      calibration (the highest-revision plans row, cross-checked against the plan's Overall table and the execution's
      `predicted_metrics`, with a warning on mismatch). `docs/ledger_schema.md` defines the plans correction row. Review
      approved 3/3 at iteration 1. Calibration: expected value predicted 41.85, actual 53.76 (delta +11.91).
50. **CI pipeline duration dashboard (Bean 0166 / HAC PR #223, 2026-11-21)**:
    - `0166` (PR #223, `6e93f5e`, merged 2026-11-21): `scripts/ci_durations.py` with the helper modules
      `ci_durations_api`, `_collect`, `_stats`, `_html` and `_svg`, and `.github/workflows/ci-durations.yml` (daily and
      `workflow_dispatch`) publish a self-contained HTML dashboard and JSON as an artifact plus a job summary. Covers
      `holon-agentic-coder` only; `holon-coherence` is not covered. Predicted EV 46.65, actual 62.09 (delta +15.44).
51. **Review ledger rows committed per iteration (Bean 0345 / HAC PR #224, 2026-11-21)**:
    - `0345` (PR #224, `c38a883`, merged 2026-11-21): new `review/ledger_commit.py` and `review/git_identity.py`. The
      review loop commits its executions ledger rows each iteration and before the conflict merge and Stage 5, so no
      ledger row is left uncommitted in the flow worktree. Review approved 3/3 at iteration 5. Calibration (predicted EV
      63.70, reported actual -7.11) is known wrong: it read the ledger at `95a45bc`, which held the earlier 'failed'
      review summary row but not the final approved row, still uncommitted; this PR closes that gap.
52. **Checkpoint and ledger ownership (Bean 0190 / HAC PR #219, 2026-11-21)**:
    - `0190` (PR #219, `df3b0d1`, merged 2026-11-21): `FlowCheckpoint` owns save, load, migrate and its path policy
      behind a `CheckpointStore` port; ledger reconciliation moves into the `ledger/` package as `LedgerReconciler`;
      container entrypoints stop importing the host flow engine for these. Plan and execution ran on `antigravity-agent`
      / `gemini-3.8-flash`. The review was resumed on `claude-agent` / `claude-opus-5-5` at the maintainer's request
      after an antigravity resolver defect. Consensus 3/3 APPROVED in iterations 13-19, never auto-posted because of the
      stale local test gate (Bean 0354); the approval was posted by hand as a PR comment. Stage 5 was run by hand with
      `holon calibrate` (report only): predicted EV 66.11, reported actual -9.11, which is misleading because it
      reflects the stalled review. The Stage 5 reconciliation and knowledge promotion did not run; follow-up Bean 0355.
53. **Unlimited stage and turn budgets (Bean 0172 / HAC PR #225, 2026-11-21)**:
    - `0172` (PR #225, `4811599`, merged 2026-11-21): an explicit `unlimited` sentinel for the stage budget variables
      and `HOLON_TURN_TIMEOUT_SECONDS`, distinct from unset (default). Internally `None`, never `inf`; the container env
      round-trips it; `holon doctor` and the flow summary show `unlimited`. Review approved 3/3 at iteration 2.
      Calibration: expected value predicted 41.00, actual 59.32 (delta +18.32).
54. **Admission uses actual PR files (Bean 0348 / HAC PR #226, 2026-11-21)**:
    - `0348` (PR #226, `3ee9c4e2`, merged 2026-11-21): Stage 3 admission compares an open PR by its actual changed
      files, not its declared touch set. A path absent on the base branch never overlaps a folder or wildcard entry, and
      the refusal lists the concrete overlapping files. Review approved 3/3 at iteration 3. Calibration: expected value
      predicted 43.32, actual 61.30 (delta +17.98).
55. **Ledger query and knowledge index decomposed (Bean 0199 / HAC PR #227, 2026-11-21)**:
    - `0199` (PR #227, `43d278cb`, merged 2026-11-21): `LedgerQuery` is built from composable filters in
      `ledger/query.py`, and `sync_ledger_incremental` splits into read, index and persist steps with the promotion
      rules as a table. Review approved 3/3 at iteration 1. Calibration: expected value predicted 37.20, actual 57.92
      (delta +20.72).
56. **Intent and plan stages decomposed (Bean 0193 / HAC PR #228, 2026-11-21)**:
    - `0193` (PR #228, `5fbd2d06`, merged 2026-11-21): the intent and plan stages split into per-stage modules
      (`flow/stages/intent.py`, `plan.py`, `decomposition.py`, `plan_decision.py`, `plan_support.py`,
      `stage_support.py`, `decomposition_summary.py`) and `flow/stage_conflict_resolution.py`;
      `validate_intent_questions` is a table of named checks; behaviour and messages unchanged. The first run skipped
      Stage 4: an antigravity run had saved `skip_review` into the checkpoint, so a resume went straight to Stage 5. The
      review was rerun on claude-opus-5-5 (3/3 approved at iteration 4) and recalibrated. Predicted EV 33.19, actual
      58.66 (delta +25.47). Bean 0356 fixes the checkpoint inheritance.
57. **Antigravity writable tmpfs and empty_diff excerpt (Bean 0349 / HAC PR #229, 2026-11-21)**:
    - `0349` (PR #229, `ccb7a6f`, merged 2026-11-21): `brain` and `conversations` are writable tmpfs overlays on the
      read-only Antigravity mount (shared helper `cli/antigravity_mounts.py`), so background-task wakeups survive;
      exit-0 `empty_diff` failures print a bounded, redacted excerpt of the agent output to stderr. Review and
      calibration were resumed on claude-agent / claude-opus-5-5 after the antigravity resolver failed. Calibration:
      expected value predicted 46.80, actual 54.94 (delta +8.14).
58. **Executor entrypoint `main` becomes an `ExecutionRun` (Bean 0196 / HAC PR #234, 2026-11-22)**:
    - `0196` (PR #234, `2ec094e`, merged 2026-11-21): `entrypoint/executor.py` (798-line `main`, CC 178) becomes the
      `entrypoint/executor/` package. `ExecutionRun` in `run.py` runs the named steps, and `main` parses arguments and
      calls `ExecutionRun(...).run()`. Child PRs #231, #232 and #233 landed first. Calibration: expected value predicted
      7.55, actual 47.72 (delta +40.17).
59. **ExecuteStage (Bean 0194 / HAC PR #236, 2026-11-22)**:
    - `0194` (PR #236, `b22258d`, merged 2026-11-22): `run_execute_stage` becomes `ExecuteStage` in
      `flow/stages/execute.py` with named steps (resume point, executor dispatch, empty-diff guard, partial salvage,
      execution record); `run_execute_stage` stays as a thin wrapper and behaviour is unchanged. Review approved 3/3.
      Calibration: expected value predicted 52.85, actual 67.22 (delta +14.37).
60. **Coherence ProxyLifecycle, checkpoint resume guard, gemini-agent removal, and dev-env Ghostty/Stow upgrades (Beans
    0208, 0341, 0322, 0344, 0346 / Coherence PR #42, HAC PRs #217 & #222, dev-env PRs #31 & #32, 2026-11-14 to
    2026-11-21)**:
    - `0208` (Coherence PR #42, `baf5c65`, merged 2026-11-14): `ProxyLifecycle` owns start-up, readiness and teardown
      (`container/lifecycle.py`), superseding closed PR #41. Consensus 3/3 at iter 5; EV predicted 8.05 / actual 8.45.
    - `0341` (HAC PR #217, `e80b00c`, merged 2026-11-20): `--from-stage` without `--checkpoint` discovers the slug's
      checkpoint (`checkpoint_discovery.py`), failed pre-stage runs never clobber an existing checkpoint
      (`resume_guard.py`), and resumed runs keep completed stages. Consensus 3/3 at iter 1; EV predicted 43.47 / actual
      59.47 (+16.00).
    - `0322` (HAC PR #222, `e2ba3c2`, merged 2026-11-21): completely removed `gemini-agent` runner, `agent-gemini`
      Docker target, and all `gemini` runner special-cases. Consensus 3/3; clean EV predicted 72.94 / actual 78.21
      (+5.27; observed -6.79 due to the stale Stage 4 local test gate, tracked in Bean 0354).
    - `0344` (dev-env PR #31, `0ba3e94`, merged 2026-11-20) and `0346` (dev-env PR #32, `d6b07de`, merged 2026-11-21):
      Ghostty and Warp casks / Linux APT tasks, Stow-managed Ghostty config, Zsh word-jump bindings (EV predicted 89.36
      / actual 91.04), and unioning repo `devenv_stow_packages` with stale `~/.config/dev-env/choices.yml` plus
      Ansible/Stow upgrade regression tests.
61. **Resolver turn budgets, foreground test prompts, and supervisor stall guard (Bean 0358 / HAC PRs #235 & #237,
    2026-11-22 to 2026-11-23)**:
    - `0358` Part 1 (HAC PR #235, `134e333`, merged 2026-11-22): `_run_resolver_agent` in `entrypoint/review_loop.py`
      loads `load_budgets(os.environ).turn` and passes `turn_budgets` to `run_turn(...)`, matching executor, planner and
      reviewer turns, with hermetic tests (`test_review_resolver_turn_budgets.py`). Consensus 3/3 at iter 3; calibration
      EV predicted 46.78 / actual 54.55 (delta +7.77).
    - `0358` Part 2 (HAC PR #237, `032d9d44`, merged 2026-11-23): resolver and executor prompt templates require running
      tests and lint in the foreground within the same turn, the turn supervisor suppresses the stall budget while a
      child test/lint process is live, and turns ending with live background work log the command clearly, backed by
      hermetic tests. Consensus 3/3 APPROVED at iteration 2 with 0 findings, closing Bean `0358`.
62. **Remove `--skip-review` flag from `holon flow` (Bean 0357 / HAC PR #238, 2026-11-23)**:
    - `0357` (HAC PR #238, `8afc215a`, merged 2026-11-23): removed `--skip-review` from `holon flow`
      (`cli/commands/flow.py`), dropped `skip_review` from flow context and checkpoint while loading legacy checkpoints
      cleanly, removed skip branches from `flow/pipeline.py`, `flow/resume_guard.py`, `flow/stages/children.py` and
      `flow/stages/review.py`, updated `docs/git_flow.md`, with hermetic tests and calibration included in the PR.
63. **`holon calibrate` runs full Stage 5 (Bean 0355 / HAC PR #240, 2026-11-23)**:
    - `0355` (HAC PR #240, `192c6e8`, merged 2026-11-23): unified Stage 5 in `flow/stage5.py` so `holon calibrate` runs
      report generation, ledger reconciliation, and knowledge promotion by default (`--report-only`, `--no-commit`,
      `--json`, idempotent reruns), backed by hermetic `tests/test_calibrate_full_stage5.py`; consensus 3/3 APPROVED and
      calibrated.
64. **Resume flags override checkpoint (Bean 0356 / HAC PR #239, 2026-11-23)**:
    - `0356` (HAC PR #239, `4e1e761`, merged 2026-11-23): per-run switches (`skip_review`, `skip_calibrate`,
      `skip_push`, `dry_run`) apply only to the run that passes them and are no longer inherited from the checkpoint;
      `--agent` and `--model` on resume override checkpoint values; Stage 4 approved at iter 4 and Stage 5 calibrated.
65. **Fish Conda/Homebrew shell hooks and clean-env multi-shell runtime tests (Bean 0361 / dev-env PR #33,
    2026-11-23)**:
    - `0361` (dev-env PR #33, `425ff6fe`, merged 2026-11-23): restored OS-guarded Homebrew `brew shellenv` and
      Conda/Miniforge `conda shell.fish hook | source` (with guarded `micromamba` fallback) in `00-devenv.fish`,
      enforced NVM-over-Conda PATH ordering across Fish/Bash/Zsh, added `env -i` Ansible Conda shell probes, added
      `tests/test_shell_hooks.py` (3-shell static parity + hermetic `env -i` runtime tests reproducing the Homebrew
      symlink masking bug + CI fail-closed guard), and updated `.github/workflows/test-unit.yml` to install `fish` and
      `zsh`. Consensus 3/3 APPROVED; calibration EV predicted 92.88 / actual 94.53 (delta +1.65).
66. **Stage 4 approved status and fresh local test gate (Beans 0347 & 0354 / HAC PR #230, 2026-11-23)**:
    - `0347` & `0354` (HAC PR #230, `f17f4b8`, merged 2026-11-23): consensus approval reports `review: approved` instead
      of `halted_for_human` while preserving legacy checkpoint/ledger compatibility, and the review-loop local test gate
      evaluates the current head instead of reusing stale Stage 3 failures; hermetic tests added and Stage 5 calibration
      included.
67. **Launcher package breaks `flow` -> `cli` import cycle (Bean 0189 / HAC PR #241, 2026-11-23)**:
    - `0189` (HAC PR #241, `0f0089d`, merged 2026-11-23): new `launcher/` package owns container launch, role dispatch,
      and proxy/sidecar plumbing, removing all four lazy `flow` -> `cli` imports, enforced by AST import-cycle test
      `tests/test_import_cycle.py`; consensus approved at iter 5 and calibrated.
68. **dev-env Ansible cleanup, `deb822_repository`, WSL Ghostty/Warp exclusion, and `tmux` mouse (Bean 0351 / dev-env PR
    #36, 2026-11-23)**:
    - `0351` (dev-env PR #36, `a9dacf46`, merged 2026-11-23): replaced deprecated `apt_repository` with
      `deb822_repository`, standardised Ansible `command` `cmd:` / `changed_when` / `check_mode: false` hygiene across
      roles and `unlink.yml`, added `devenv_is_wsl` detection to unconditionally exclude all 12 Linux Ghostty and Warp
      tasks on WSL, enabled `set -g mouse on` in `.tmux.conf`, and added hygiene, WSL templating, and zero-deprecation
      `--syntax-check` tests. Consensus 3/3 APPROVED at iter 2; calibration EV predicted 92.83 / actual 94.64 (delta
      +1.81); 6/6 CI green.
69. **dev-env `devenv_user`, WSL wizard prompt skip, and Ansible Jinja2 variable audit (Bean 0364 / dev-env PR #37,
    2026-11-23)**:
    - `0364` (dev-env PR #37, `4b1391c3`, merged 2026-11-23): defined `devenv_user` in `ansible/group_vars/all.yml`,
      added `is_wsl()` in `scripts/devenv_wizard.py` to skip the Ghostty/Warp prompt and persist
      `devenv_install_gui_casks: false` on WSL, and added Conda command templating plus repo-wide Jinja2 AST
      variable-audit tests in `tests/test_templating.py` and WSL wizard tests in `tests/test_wizard.py`. Consensus 3/3
      APPROVED; calibration EV predicted 95.02 / actual 95.95 (delta +0.93); 6/6 CI green.
70. **dev-env disable `expand_argument_vars` on Conda clean-shell checks and `ansible-playbook` test (Bean 0365 /
    dev-env PR #38, 2026-11-23)**:
    - `0365` (dev-env PR #38, `68ddec98`, merged 2026-11-23): set `expand_argument_vars: false` on all three clean-shell
      Conda verification `ansible.builtin.command` tasks in `ansible/roles/conda/tasks/main.yml` and switched Fish to
      `string join : -- $PATH`, enforced static `expand_argument_vars: false` hygiene for shell `$VAR` command tasks in
      `tests/test_toolchain.py`, and added a real hermetic `ansible-playbook` verification test under polluted parent
      `PATH` / `CONDA_DEFAULT_ENV` in `tests/test_shell_hooks.py`. Consensus 3/3 APPROVED; calibration EV predicted
      96.27 / actual 97.28 (delta +1.01); 6/6 CI green.
71. **dev-env Linux/WSL `zsh` installation and unified NVM `versions/node` storage (Bean 0366 / dev-env PR #39,
    2026-11-23)**:
    - `0366` (dev-env PR #39, `eeb2032d`, merged 2026-11-23): added `zsh` to `devenv_packages_core` and `pkg_apt.yml`
      (skipped as OS-provided in `os_Darwin.yml`), pointed `ansible/roles/node` `creates` and `current` symlink at
      `~/.local/share/nvm/versions/node/v{{ devenv_node_version }}`, replaced bi-directional `-name "v*"` symlinking in
      `00-devenv.fish` with one-way `v[0-9]*` migration plus `versions/node/versions` loop cleanup and `current` repair,
      and added static and hermetic Fish migration tests. Consensus 3/3 APPROVED; calibration EV predicted 96.27 /
      actual 97.16 (delta +0.89); 6/6 CI green.
72. **dev-env Zsh `.zprofile`, Node/Fish/Homebrew converge fixes, hermetic Ansible/Stow integration tests, and
    Ubuntu/Docker E2E converge testing (Bean 0370 / dev-env PR #40, 2026-11-23)**:
    - `0370` (dev-env PR #40, `22ca3862`, merged 2026-11-23): added tracked `dotfiles/zsh/.zprofile` (non-interactive
      `.zshrc` sourcing without double-sourcing `zsh -lic`) in `devenv_links`, isolated `ansible/roles/node`
      Bash/Zsh/Fish shell verification under `env -i` + `expand_argument_vars: false` accepting canonical
      `versions/node/v{{ devenv_node_version }}/bin/node`, added `follow: true` in `ansible/roles/fish` symlink
      discovery and `devenv_brew_bin | dirname` on Homebrew module `path:`, removed the fake `.zprofile` shim from
      `tests/test_shell_hooks.py`, added real `ansible-playbook` Stow/Node/Fish integration tests in
      `tests/test_converge_integration.py`, installed `stow` in `.github/workflows/test-unit.yml`, and added real
      Ubuntu/WSL converge CI (`.github/workflows/test-converge.yml`) plus `tests/docker/ubuntu.Dockerfile` and
      `make test-ubuntu`. Consensus APPROVED; calibration EV predicted 97.60 / actual 99.09 (delta +1.49); 7/7 CI green
      (including `Ubuntu Converge E2E` in 5m25s).
73. **Ledger-only merges, one GitHub adapter, token scopes and flow fixes (2026-11-23, later):**

- `0191` (HAC PR #260, `7225685`, parent; children #242 `96ecf25`, #245 `9d93e1b`, #255 `a9fe10c`): one `GitHubAdapter`
  owns every `gh` call.
- `0155` (PR #243, `2cf1869`): general `HOLON_*` forwarding no longer puts credential-shaped values on the docker argv.
- `0175` (PR #244, `252004a`): GitHub token scopes are checked before Stage 3 when the plan touches workflows.
- `0157` (PR #248, `d369f2f`): `holon flow` enables the mitmproxy sidecar when its image exists.
- `0200` (PR #249, `c905a98`): the diverged `token_reduction` copy is removed; `holon-coherence` is the single source.
- `0173` (PR #251, `e4f34ca`): layered `.env` files; `0174` (PR #256, `c941d78`): one generated environment variable
  reference.
- `0363` (PR #250, `582c4ab`): after merging `main`, the flow waits for CI before calibrating.
- `0372` (PR #254, `84b70c1a`): an approval survives a merge of `main` that leaves the PR's own diff unchanged.
- `0369` (PR #253, `606978f`) and `0359` (PR #246, `16f4f62`): calibration report correctness and report-outcome halt
  consistency. `0362` (PR #247, `79555f8`): a fresh calibration clears the stale-calibration warning.
- `0373` (PR #252, `a154244`): the KB and wisdom index is derived, not committed. `0367` (PR #257, `ff98e7e`): no
  fallback calibration report when Stage 5 fails.
- `0333` (PR #258, `b01c2da`): GitHub Issues replace beads as the target tracker. `0377` (PR #261, `7ab455c`): fuzz
  tests renamed after what they protect.
- `0376` child PRs #259 (`d98e518`, shared `sync_with_target` routine) and #262 (`d6dabb0`, containerised
  conflict-resolver role) merged into its plan branch; the parent flow is still running.
- Open: PR #263 (`0378`), PR #265 (`0376` child 3), PR #266 (`0374`). Logged earlier: `0368`, `0371`, `0374` to `0388`.

74. **Interrupt-safe Stage 2 plan resume (Bean 0360 / HAC PR #264, `f49340f9`, merged 2026-11-23):**
    - `0360` (PR #264, `f49340f9`): Stage 2 records pushed plan branches reliably and resumes adopt existing pushed
      `P-.../_` branches instead of duplicating plans (`flow/stages/plan_resume.py`). Consensus 3/3 APPROVED; 11/11 CI
      green; Stage 5 calibration EV predicted `42.34` / actual `58.86` (delta `+16.52`, Bug EV Drag `0.00`). Post-merge
      rebuilt Docker images, reinstalled `holon`, pruned `flow-resume-adopts-pushed-plan-branch`, refreshed PR #266
      (`0374`) calibration, and backfilled slot #4 with `0382`.
75. **Sidecar scratch stays outside worktrees (Bean 0374 / HAC PR #266, `e0251206`, merged 2026-11-23):**
    - `0374` (PR #266, `e0251206`): moved sidecar wire-log and LLM cache defaults to per-user state directories under
      `~/.holon/` (`launcher/proxy_paths.py`, `launcher/sidecar_plan.py`) and hardened Stage 3 salvage and completion
      commits against staging scratch files (`flow/partial_salvage.py`, `entrypoint/execution_workspace.py`,
      `entrypoint/executor/run.py`, `outcome.py`). Consensus 3/3 APPROVED; 11/11 CI green; Stage 5 calibration EV
      predicted `68.51` / actual `79.55` (delta `+11.04`). Post-merge synced `apps/holon-agentic-coder/main`, rebuilt
      Docker images and `holon`, pruned `flow-sidecar-scratch-outside-worktree`, refreshed PR #263 (`0378`) and PR #267
      (`0382`), and backfilled Bean `0381` across `holon-coherence` and `holon-agentic-coder`.
76. **Calibrate stale warnings and the Fable 5.2 registry entry (Beans 0378, 0382 / HAC PRs #263 and #267, `e563254e`
    and `9f57492d`):**
    - `0378` (PR #263, `e563254e`): PR-own diff fingerprint for staleness checks, stale-warning suppression while Stage
      5 regenerates, and hermetic tests. Consensus 3/3 APPROVED; 11/11 CI green.
    - `0382` (PR #267, `9f57492d`): added the `claude-fable-5-2` registry entry with aliases `fable` and `claude-fable`
      (removed from Opus), canonical model IDs in `holon doctor`, and alias-family regression tests. Consensus 3/3
      APPROVED; 11/11 CI green.
    - `0406` (harness, uncommitted on `docs/harness-20261123`): `flow_env.py` falls back to the OS secret store for the
      Claude token; 22 tests pass in `tests/test_flow_env.py`.
77. **Flow ledger worktree cleanup, end-to-end test teardown and bean-progress test refresh (Beans 0387, 0226, 0389 /
    HAC PRs #270 and #269, 2026-11-24):**

- `0387` (PR #270, `bfbd9f4`, merged 2026-11-24): the ledger step removes its temporary `holon-flow-ledger-*` worktree
  in a `finally`, and a new `flow/ledger_worktree.py` prunes stale ledger worktrees at the start of each step.
- `0226` (PR #269, `407ad39`, merged 2026-11-24 11:28Z): the flow's end-to-end test teardown landed cleanly after
  iteration 13 consensus.
- `0389` (harness, 2026-11-24): `tests/test_bean_progress.py` expectations aligned with the current bean-progress
  output; the script itself was unchanged.

---

## Active Beans Triage and Prioritisation Matrix

| Priority | Status      | Impact |          Sizing           | Bean # | Title                                                                                                                                                         | Domain                           | Dependencies / Notes                                                                                                                                                                                                                                  |
| :------- | :---------- | :----: | :-----------------------: | :----- | :------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **P0**   | todo        |  High  |             L             | 0255   | "Streaming per-issue resolvers during Stage 4 CI & review with single consolidated commit"                                                                    | Review Loop / Concurrency        | Maintainer 2026-11-24: the resolver starts on the first pipeline failure and fixes every failure of the run. Changes the review loop with 0376 and 0407, so run in sequence, never together; also overlaps 0192 on `flow/review/loop.py`.             |
| **P1**   | todo        |  High  |             M             | 0391   | Stage 3 stops after an overlap wait when merging main into the plan branch conflicts only in the ledgers                                                      | Ledger / Observability           | Stage 3 stops after an overlap wait when merging main into the plan branch conflicts only in the ledgers. Settle ledger conflicts mechanically; overlaps 0376.                                                                                        |
| **P1**   | todo        | Medium |             M             | 0392   | Stage 4 resolver runs repo-wide Prettier and mutates untouched historical plans/ files                                                                        | Build / DevEx                    | Stage 4 resolver runs repo-wide Prettier and mutates untouched historical plans; scope formatting to the touched files.                                                                                                                               |
| **P1**   | todo        |  High  |             M             | 0394   | No unnecessary waiting anywhere in the holon flow: recommendations                                                                                            | Build / DevEx                    | Umbrella epic: ranked recommendations for removing unnecessary waits, ordered by time saved; concrete items are 0395, 0399, 0400 and 0403.                                                                                                            |
| **P1**   | todo        |  High  |             L             | 0395   | Stage 3 works during an overlap wait instead of idling until the blocking pull request merges                                                                 | Flow / Architecture              | Stage 3 works during an overlap wait instead of idling until the blocking pull request merges. Large; queue after the live flows on the same stage files.                                                                                             |
| **P1**   | todo        | Medium |             M             | 0396   | A flow run survives the agent session that started it                                                                                                         | Skills / Tooling                 | A flow run should survive the agent session that started it; detach the run from the session.                                                                                                                                                         |
| **P1**   | todo        |  High  |             M             | 0397   | A resume adopts a completed, pushed execution branch instead of executing Stage 3 again                                                                       | Ledger / Observability           | Resume adopts a completed, pushed execution branch instead of executing Stage 3 again. Related to 0375 and 0360.                                                                                                                                      |
| **P1**   | in-progress |  High  |             L             | 0403   | No full CI run for commits that only touch bookkeeping files                                                                                                  | Build / DevEx                    | In progress. No full CI run for commits that only touch bookkeeping files.                                                                                                                                                                            |
| **P1**   | in-progress |  High  |             M             | 0404   | The 600 s timing ceiling on the macOS unit job fails pull requests on runner variance                                                                         | Build / DevEx                    | The 600 s timing ceiling on the macOS unit job fails pull requests on runner variance; fix the ceiling or shrink the suite (0405).                                                                                                                    |
| **P1**   | in-progress | Medium |             M             | 0405   | Clean up unnecessary unit tests: the suite has outgrown the pipeline                                                                                          | Build / DevEx                    | In progress. Remove unnecessary unit tests: ubuntu about 4 min, workspace survival about 7 min, macOS over 8 min.                                                                                                                                     |
| **P1**   | todo        | Medium |             M             | 0408   | Every push passes the CI hygiene and lint checks locally before it leaves the machine                                                                         | Build / DevEx                    | Run the CI hygiene and lint checks (Prettier, ruff, JSON and JSONL validity, file growth) locally before every push; a CI-caught failure costs a full pipeline.                                                                                       |
| **P1**   | todo        |  High  |             L             | 0409   | A finding the resolver rejected, or a resolver pass that changed nothing, does not start another full review                                                  | Flow / Architecture              | A finding the resolver rejected, or a resolver pass that changed nothing, must not start another full review.                                                                                                                                         |
| **P1**   | todo        |  High  |             M             | 0410   | Remove the conflict magnets: generated README and env docs, and a module budget file that does not serialise flows                                            | Flow / Architecture              | Remove the conflict magnets: generated README and env docs, and a module budget file that does not serialise flows. Flows waited 39.8 hours on each other in the period.                                                                              |
| **P1**   | todo        |  High  |             M             | 0411   | Harness instructions contradict each other on runner switching, model ladders and file size                                                                   | Flow / Architecture              | Harness instructions contradict each other on runner switching, model ladders and file size; subagents get different answers.                                                                                                                         |
| **P1**   | in-progress |  High  |             S             | 0215   | "Deterministic beans-to-GitHub-Issues importer and real-data dry run"                                                                                         | Issue Tracking / Migration       | Ready now: Bean 0333 completed (PR #258), so no blocker remains. Harness-side importer only, no target flow. Unblocks 0217, 0218 and the 0317 import.                                                                                                 |
| **P1**   | todo        |  High  |             S             | 0384   | The 90 s stall budget cuts long-thinking models: every Fable 5.2 reviewer failed and the loop retried unchanged                                               | Flow / Budgets / Stage 4         | Ready, but overlaps 0376 on the review loop: start after 0376 lands. `HOLON_TURN_STALL_SECONDS` defaults to 90 s; long-thinking models such as Fable 5.2 stream nothing for longer than that.                                                         |
| **P1**   | in-progress |  High  |             M             | 0350   | "Enable Claude Code code mode (CLAUDE_CODE_EXPERIMENTAL_CODE_MODE=1) for every Claude run"                                                                    | Claude / Config                  | In progress in parallel Claude Code session (`flow-claude-code-mode-default-on`). Harness edit (`flow_env.py`, `.claude/settings.json`) plus HAC `agent_runner.py` / `agent_defaults.py`. Sequence with `0382` on `agent_defaults.py`, before `0270`. |
| **P1**   | todo        |  High  |             M             | 0270   | "Discover runner models dynamically through each harness instead of the hardcoded model table"                                                                | Flow / Architecture              | Ready after 0382 and 0350 (same `agent_defaults.py`). Replaces hardcoded `RUNNER_CAPABILITIES` with per-harness discovery.                                                                                                                            |
| **P1**   | todo        |  High  |             M             | 0381   | Bare holon flow resume keeps token reduction on: every reviewer fails with cache_control.ttl 400                                                              | Flow / Token reduction / Stage 4 | In progress across both repos (backfilled after PR #266 merged): `holon-coherence` (`fix-cache-control-ttl-order`) and `holon-agentic-coder` (`token-reduce-opt-in-resume`), disjoint from `0376`, `0378`, `0382`, and `0350`.                        |
| **P1**   | in-progress |  High  |             S             | 0390   | Two runners can drive the same flow checkpoint at once; nothing locks a flow or a bean against a second launch                                                | Flow / Concurrency               | Queued after `0381` (`flow/checkpoint.py`) and `0376`. Exclusive checkpoint/worktree lock in `holon flow` plus atomic bean claim and duplicate-launch guard in `run_holon_flow.py`.                                                                   |
| **P1**   | todo        |  High  |             M             | 0368   | Submodule gitfile left with container paths breaks host-side git in the flow worktree                                                                         | Flow / Git / Stage 5             | Ready, but overlaps 0376 on `flow/stages/calibrate.py`: start after 0376 lands. Repair or reject a submodule gitfile that points at container paths before host-side git runs.                                                                        |
| **P1**   | todo        |  High  |             M             | 0383   | Stage 5 waits for CI twice and overruns its 10-minute budget; no per-step timing breakdown                                                                    | Flow / Stage 5 / CI              | Ready, but overlaps 0376 and 0378 on `flow/stages/calibrate.py`: start after both land. Stage 5 waits for CI twice (11 min 57 s and 9 min 54 s on PR #260); add a per-step timing breakdown.                                                          |
| **P1**   | todo        |  High  |             L             | 0176   | "Remove every unittest reference from holon-agentic-coder; the suite is pytest only"                                                                          | Tests                            | Ready; run alone with no other HAC flow or PR in flight. Re-measured on `main` (`7225685`) at 144 tracked files; touches nearly every test file.                                                                                                      |
| **P1**   | todo        |  High  |             L             | 0192   | "`run_review_loop` and `run_review_stage` become a `ReviewLoop` object with named steps"                                                                      | Review Loop / Refactor           | Unblocked: 0191 completed (PR #260). Overlaps 0376 on `flow/review/loop.py`: start after 0376 lands.                                                                                                                                                  |
| **P1**   | todo        |  High  |            XL             | 0152   | "Audit long files; decompose oversized functions (flow.py, cli.py first)"                                                                                     | Refactor / Concurrency           | Umbrella. Coherence (0186, 0203 to 0208) and HAC (0185, 0188, 0190, 0193 to 0196, 0199, 0254) children merged. Remaining: 0265, 0192, 0197, 0198 and a re-audit of `planner.py`.                                                                      |
| **P1**   | todo        |  High  |             M             | 0379   | No logic in **init**.py: package files only expose public names                                                                                               | Architecture / Hygiene           | Queued behind 0265: `cli/__init__.py`, `cli/commands/__init__.py`, `flow/__init__.py` and `entrypoint/executor/__init__.py` are edited by both. Four package `__init__.py` files hold logic.                                                          |
| **P1**   | todo        | Medium |             S             | 0416   | Fix relative quota reset tail scanning, seconds parsing, and watcher keychain lookup                                                                          | Harness / Run 247 / Credentials  | Quota reset parsing scans the full output in one place and the tail in another, and drops seconds; `watch_limits.py` still reads the deleted plaintext token file. Harness only.                                                                      |
| **P1**   | todo        |  High  |             M             | 0420   | A flow whose pull request is merged while it is running fails instead of finishing cleanly                                                                    | Flow / Review                    | PR #270 merged while its flow waited on merged-head CI, and the flow exited 1 on an unverifiable diff. It should finish cleanly.                                                                                                                      |
| **P2**   | in-progress | Medium |             M             | 0400   | Shorten the CI pipeline: the slowest jobs set every wait in the flow                                                                                          | Build / DevEx                    | Shorten the CI pipeline: the slowest jobs set every wait in the flow. Overlaps 0404 and 0405 (test suite).                                                                                                                                            |
| **P2**   | todo        | Medium |             M             | 0412   | Every flow step is timed and every flow keeps its log: the steps the audit could not measure                                                                  | Ledger / Observability           | Every flow step is timed and keeps its log, so the self-improvement audit can measure each step.                                                                                                                                                      |
| **P2**   | todo        | Medium |             L             | 0413   | Coding rules from what the reviewers keep finding, given to the planner and executor up front                                                                 | Architecture / Quality           | Coding rules drawn from recurring reviewer findings, given to the planner and executor up front.                                                                                                                                                      |
| **P2**   | todo        |  High  |             L             | 0414   | An edit outside the plan's touch set is caught during the executor turn, not after it                                                                         | Architecture / Quality           | An edit outside the plan's touch set should be caught during the executor turn, not after it.                                                                                                                                                         |
| **P2**   | todo        | Medium |             M             | 0402   | A post-merge image rebuild does not disturb flows that are running or starting                                                                                | Build / DevEx                    | A post-merge image rebuild must not disturb flows that are running or starting.                                                                                                                                                                       |
| **P2**   | todo        | Medium |             M             | 0386   | Review tests fail when run together serially, and test_backgrounded_sleep hangs with redirected output                                                        | Tests / Hygiene                  | Ready; run alone. Order-dependent review tests, and `test_backgrounded_sleep` hangs when output is redirected, so a serial run takes about 25 minutes.                                                                                                |
| **P2**   | todo        | Medium |             S             | 0388   | Bean progress shows a stale 'Halted' stage while a role is live, and the triage narrative goes stale                                                          | Harness / Reporting              | Ready. Harness-only: the bean_progress stale 'Halted' cell and this matrix's hand-written narrative, which goes stale after a day of merges.                                                                                                          |
| **P2**   | todo        | Medium |             M             | 0352   | "Push GitHub PR events through `gh webhook forward`, with cheap polling as the fallback"                                                                      | GitHub / Efficiency              | Queued behind 0376 (review-loop CI and conflict polling, `run_holon_flow.py`, skills). Needs `cli/gh-webhook` and `admin:repo_hook` scope on maintainer `gh`; stopgap until `gh event listen` is enabled.                                             |
| **P2**   | todo        | Medium |             M             | 0181   | "Use the `/_` leaf only when referencing a git branch, never on ids"                                                                                          | Holon Flow / Ledger              | Queued behind 0376 (overlaps `docs/git_flow.md` and `docs/ledger_schema.md`). `entrypoint/executor/run.py`, `calibration.py`, `cli/commands/` and `entrypoint/` still strip or re-add `/_`; sequence with 0197.                                       |
| **P2**   | todo        | Medium |             L             | 0223   | "Audit CLI flags vs `HOLON_*` env vars: four-kind decision rule, flag>env precedence"                                                                         | CLI / Config                     | Wait for `0265` (`cli/` split) and `0357` (drops `--skip-review`). Exhaustive inventory of every `add_argument` and `os.getenv`, unified resolution helper, logged source, auto-derived `--help`.                                                     |
| **P2**   | in-progress | Medium |             M             | 0216   | "Holon flow references and drives GitHub Issues (assign on intent, close on merge)"                                                                           | Holon Flow / Issue Tracking      | Ready now (0333 completed, PR #258). Adds optional `work_item` to the intent schema, marks the issue in progress and adds `Closes #N` to the PR body; sequence with 0191's `flow/github/` layout.                                                     |
| **P2**   | todo        | Medium |             S             | 0217   | "GitHub Issues tracking for holon-coherence: labels, guidance and import"                                                                                     | Issue Tracking / Coherence       | Blocked by `0215`. Creates labels and imports coherence beans after `0215`; guidance change runs via Holon flow on `holon-coherence`.                                                                                                                 |
| **P2**   | todo        | Medium |             M             | 0218   | "Port harness skills and guidance to GitHub Issues and sequence the harness retirement"                                                                       | Harness Deprecation              | Harness work. Blocked by `0215`, `0216`, and `0217`. Replaces triage matrix and bean-closing steps, then archives harness read-only.                                                                                                                  |
| **P2**   | todo        | Medium |             M             | 0317   | "GitHub Projects kanban board over the target repositories' issues"                                                                                           | Issue Tracking / Projects        | Blocked by `0215` (and maintainer `gh auth refresh -s project`). Organisation Project v2 over `holon-agentic-coder` and `holon-coherence`.                                                                                                            |
| **P2**   | todo        | Medium |            XL             | 0153   | "Remove comments and docstrings from all code; make it self-documenting"                                                                                      | Readability                      | Per package after its decomposition (`holon-coherence` decompositions are complete and ready; on HAC, run only on settled packages).                                                                                                                  |
| **P2**   | todo        |  High  |             L             | 0142   | "Real-workload benchmark: Qwen3.8-27B dense vs Flash-Next MoE"                                                                                                | Model Selection                  | Ready (operator/host-run; real data only). Blocked beans `0129`, `0132`, `0133` are completed; benchmark itself has not run.                                                                                                                          |
| **P2**   | draft       |  High  | S (analysis) + L (splits) | 0340   | "Revisit the module budget: implications of a strict 200-line default with no overrides"                                                                      | Lint / Refactoring               | Draft (unblocked since PR #214 froze `module_budgets.json`, awaits maintainer decision). Decide ceiling, line counting, covered packages, and split order; each override removal needs explicit authorisation.                                        |
| **P2**   | todo        | Medium |             M             | 0418   | Preserve passing executions on touch-set expansion and decompose re-plan failures                                                                             | Flow / Touch Sets                | A passing Stage 3 run is discarded when a small out-of-touch-set companion edit trips the guard. Keep the passing branch and re-plan only the expansion. Complements 0414.                                                                            |
| **P3**   | draft       | Medium |             M             | 0398   | A flow blocked only by an approved pull request can start from that pull request's head                                                                       | Flow / Architecture              | Draft, low priority: a flow blocked only by an approved pull request can start from that pull request's head. Waits on a maintainer decision.                                                                                                         |
| **P3**   | todo        | Medium |             M             | 0141   | "Tune vmlx prefill/decode levers for both Qwen3.8 models, crash-safe"                                                                                         | vmlx / Performance               | Ready (host-level vMLX tuning on Mac; not a target-repo change). Pairs with `0142`.                                                                                                                                                                   |
| **P3**   | todo        |  Low   |            XS             | 0231   | "Exhausted-budget error string interpolates raw count while payload reports clamped 0"                                                                        | Flow Engine / Cosmetic           | Queued behind 0376 (overlaps `flow/review/loop.py`). Cosmetic; bundle with a review-loop flow.                                                                                                                                                        |
| **P3**   | todo        |  Low   |            XS             | 0269   | "Deferred nits from the holon-agentic-coder PR 158 review loop"                                                                                               | Review Loop / Housekeeping       | Wait for 0376 (overlaps `docs/git_flow.md`) and 0197 (`calibration.py`). Item 2 obsolete; remaining: fold `parse_actual_metrics` exit-code logic onto `record_exit_code` and fix `docs/git_flow.md` checkpoint wording.                               |
| **P0**   | todo        |  High  |             L             | 0525   | Harden /holon/* dashboard Host validation, /holon/api/mode auth, CORS, and wire_log_dir                                                                       | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P0**   | todo        |  High  |             L             | 0524   | Fix world-writable Root CA key permissions, web password leaks, and unscrubbed cache                                                                          | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0541   | Planner touch set exceeds the intent scope (no check between intent scope and plan touch set)                                                                 | Ledger / Observability           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0540   | Split conftest.py: each test module owns its setup                                                                                                            | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        | Medium |             M             | 0539   | Add 2026-11 architecture audit patterns and failure modes to holon-coherence KB                                                                               | CLI / Telemetry                  |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0538   | Add 2026-11 architecture audit patterns and failure modes to holon-agentic-coder KB                                                                           | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0537   | Retire legacy re-export shims, stale budget overrides, conftest allowlist, and allow # WHY comments                                                           | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0536   | Unify structured logging, bound checkpoint context.logs, and remove FlowCheckpoint dual-writes                                                                | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0535   | Make RunnerSpec single-source runner registration and add GitForge Protocol + stage registry                                                                  | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0534   | Eliminate silent except-pass catches, library sys.exit calls, and GitHub/Git adapter error gaps                                                               | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0533   | Add mypy/pyright to CI, unify agent-ID and numstat helpers, and drive runtime env from env_registry                                                           | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0532   | Add Docker resource limits, read-only intent mount, 0o600 secret permissions, and Dockerfile pinning                                                          | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0531   | Break flow/entrypoint and ledger/knowledge import cycles and decompose ExecutionRun, planner, turns                                                           | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        | Medium |             M             | 0530   | Add static type checker to CI, prune redundant self-doc tests, legacy shims, and root clutter                                                                 | CLI / Telemetry                  |                                                                                                                                                                                                                                                       |
| **P1**   | todo        | Medium |             M             | 0529   | Centralize typed CoherenceSettings, bound wire-log queues, and align Docker/wheel packaging                                                                   | Build / DevEx                    |                                                                                                                                                                                                                                                       |
| **P1**   | todo        | Medium |             M             | 0528   | Eliminate request hot-path deepcopies, duplicate parsers, metric drift, and ab_test leaks                                                                     | CLI / Telemetry                  |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0527   | Unify provider detection, make ProviderFormat extensible, and break import cycles                                                                             | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0526   | Fix SSE chunk fragmentation bugs and add real mitmproxy tflow wire-level tests                                                                                | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0523   | A flow parked at Stage 3 is resumed by hand when its blocker merges; record the blocker and resume on its state change                                        | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0522   | A rerun after a post-approval conflict restarts a full review from the review stage and keeps running after the PR merges                                     | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0521   | Main-push gate runs the full suite when the merged PR head job is still running; wait for it instead                                                          | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0520   | Stage 3 admission blocks on shared file paths, not on a real merge conflict; one open PR parks several flows                                                  | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | in-progress |  High  |             M             | 0519   | Flow worktree, checkpoint and intent/plan branches vanish after a Stage 3 overlap refusal                                                                     | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | in-progress |  High  |             L             | 0518   | Review loop writes its git identity into the shared repository config, so host-side commits are authored by the agent                                         | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | in-progress |  High  |             L             | 0517   | Concurrent flows add the same knowledge-base or wisdom file, so their PRs conflict add/add                                                                    | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        | Medium |             M             | 0516   | Review ensemble fails with 'Prompt is too long' on a pull request that deletes thousands of files                                                             | Build / DevEx                    |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0515   | Ledger reorder (0436) conflicts with every merge to main and the resolvers keep main order, silently undoing it                                               | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        | Medium |             M             | 0514   | Main-push tree gate skips nothing when merges arrive back to back; coalesce a burst to the newest tip                                                         | Build / DevEx                    |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0513   | Stage 5 restore of the starting branch fails on pending ledger rows and withdraws a fresh approval on a bookkeeping-only head                                 | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0512   | Push PR-merged events to wake the agent and automatically run post-pr-merge                                                                                   | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0509   | Verify a performance flow CI saving on main after it merges and record it                                                                                     | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | in-progress |  High  |             L             | 0508   | Intent scope is hand-guessed: 3 of 6 flows changed files they did not list                                                                                    | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        | Medium |             M             | 0507   | install-holon fails its main-worktree pull when a concurrent fetch rewrites the shared FETCH_HEAD                                                             | General                          |                                                                                                                                                                                                                                                       |
| **P1**   | in-progress | Medium |             M             | 0506   | Prune the existing single-flow Stage 4 KB-failure clutter from holon-knowledge                                                                                | Build / DevEx                    |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0505   | Child PRs of a decomposed plan run CI against the plan branch's stale copy of main                                                                            | Ledger / Observability           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0503   | Review loop approves a flow PR whose measured acceptance criteria are not met                                                                                 | Ledger / Observability           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0502   | Planner touch set adds files outside the intent scope and blocks admission on a sibling flow                                                                  | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        | Medium |             M             | 0499   | Calibration report records, per flow, CI runs, review iterations and how many were churn                                                                      | Build / DevEx                    |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0498   | A unit test measures the live tree against the live budget file, so it duplicates the hygiene gate in three jobs and fails every open PR after a budget merge | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0497   | Review loop re-runs the full ensemble 9 times on a CI failure the resolver reported as not fixable in code                                                    | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        | Medium |             M             | 0495   | Resumed flow wrote no progress to its log, and Stage 5 overran its budget by counting the CI wait                                                             | General                          |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0494   | A fresh iteration-4 approval was withdrawn at the merged-head gate on a stale fingerprint and then re-reported                                                | Ledger / Observability           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0493   | An approved PR shows CLEAN but breaks main's hygiene after a budget-tightening merge                                                                          | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0492   | A flow edited a file outside its intent scope and the review passed it                                                                                        | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0491   | Running a subset of unit test files loses the flow_repos fixture                                                                                              | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0490   | holon flow resume with --checkpoint silently ignores an amended intent file                                                                                   | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | in-progress |  High  |             M             | 0489   | Module line budget: default 400 for now, then step down by 50 per pull request to 250, decomposing at each step                                               | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0487   | Overlap wait is silent in the flow log: the wrapper prints only 'exited with non-zero code 1' while it waits                                                  | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        | Medium |             M             | 0485   | A flow's module_budget_change intent field does not clear the CI hygiene budget gate                                                                          | Build / DevEx                    |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0483   | Measure runner and model wall time on comparable flows to choose the default                                                                                  | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0482   | Estimate a performance change's saving from history before launching its flow                                                                                 | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0481   | A flow whose intent scope overlaps a flow in flight is launched anyway and holds a concurrency slot while it waits                                            | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | in-progress |  High  |             M             | 0480   | A network outage at pre-flight ends the flow wrapper and the flow idles until someone relaunches it                                                           | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0479   | Parent pull request of a decomposed plan is re-reviewed in full after every child was approved                                                                | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0478   | Reviewers wait for CI inside their own turn although the engine already gates on CI                                                                           | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0477   | Overlap-exit relaunch without --checkpoint restarts split-calibration-package from intent four times                                                          | Ledger / Observability           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0476   | Local-flow overlap polling relaunches holon flow every minute, logs false clear, and bloats checkpoint logs                                                   | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0474   | Flow integration of a plan branch into its execution branch refuses an append-only executions.jsonl merge as 'not a pure ledger append'                       | Ledger / Observability           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0473   | Flow push of a parent branch is rejected after a child PR merges into it (stale local parent, no fetch before push)                                           | Ledger / Observability           |                                                                                                                                                                                                                                                       |
| **P1**   | in-progress |  High  |             L             | 0472   | Flow runner does not refuse a second run on the same intent and does not reap its children after a halt                                                       | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        | Medium |             M             | 0469   | test_conflict_gate code-conflict test reaches the real launcher and exits on macOS when docker is on PATH                                                     | General                          |                                                                                                                                                                                                                                                       |
| **P1**   | todo        | Medium |             M             | 0468   | run_holon_flow.py exits on a Stage 3 overlap refusal instead of waiting it out                                                                                | Skills / Tooling                 |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0467   | Per-merge record commits make up 60 of the last 92 harness commits                                                                                            | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        | Medium |             M             | 0466   | A flow stage that needs Docker aborts the moment the daemon is down instead of waiting                                                                        | Build / DevEx                    |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0465   | Harness beans, skills and the audit instruction sit uncommitted in the working tree                                                                           | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0463   | Stage 2 planner collapses file-scoped intents into directory touch-set entries that broaden Stage 3 overlap                                                   | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | in-progress |  High  |             M             | 0462   | Epoch-second stage and plan IDs collide across concurrent flows                                                                                               | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0460   | Stage 4 resolver runs full 7,800+ pytest suite twice and even on Markdown/bookkeeping-only fixes                                                              | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0458   | Ready pull requests are hand-synced before each merge and merged before that pipeline ends                                                                    | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        | Medium |             M             | 0455   | post-pr-merge rebuilds holon-coherence on hac merges, collides on burst merges, and skips triage                                                              | Build / DevEx                    | Three operational defects in `.agents/skills/post_pr_merge/SKILL.md` and                                                                                                                                                                              |
| **P1**   | in-progress | Medium |             M             | 0454   | ci_bookkeeping_gate triggers full 7-workflow CI on mechanical Merge origin/main PR pushes                                                                     | Build / DevEx                    | `scripts/ci_bookkeeping_gate.py:114-148` uses `compare(client, base, head_sha)` (`2-dot` `before..head_sha` GitHub                                                                                                                                    |
| **P1**   | todo        |  High  |             L             | 0451   | dev-env CI lacks ci_bookkeeping_gate and runs test-unit (macos-latest) serially, causing 15+ min Stage 5 overruns                                             | Architecture / Quality           | `thomashan/dev-env` GitHub Actions workflows lack a bookkeeping-only path gate (`ci_bookkeeping_gate`, equivalent to                                                                                                                                  |
| **P1**   | todo        |  High  |             M             | 0450   | Stage 4 review_local drops TestMeasurement.output_excerpt and preempts pending GitHub CI with slow host test runs                                             | Flow / Architecture              | When any reviewer objects in Stage 4 (`flow/review/loop.py:374-386`), the review loop probes GitHub CI once without                                                                                                                                   |
| **P1**   | todo        |  High  |             M             | 0449   | Stage 4 unchanged_streak keys on raw head_sha and ignores open findings, letting target sync / doc-only commits loop indefinitely                             | Flow / Architecture              | Stage 4 convergence detection (`unchanged_streak` in `flow/review/loop.py:568-578`) requires                                                                                                                                                          |
| **P1**   | todo        |  High  |             M             | 0448   | end_of_flow_sync._reenter_review_and_calibrate leaves stale calibrate=SUCCESS, causing nested Stage 5 rerun and bogus consensus withdrawal                    | Flow / Architecture              | When `end_of_flow_sync._reenter_review_and_calibrate` re-enters Stage 4 (`FlowStage.REVIEW`) after an end-of-flow target                                                                                                                              |
| **P1**   | todo        |  High  |             L             | 0447   | Run Workspace survival via one shared child unit pass or separate CI jobs                                                                                     | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0446   | Stage 3 admission blocks SPLIT parent plans on union touch set before decomposition                                                                           | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0445   | End-of-flow sync leaves checkpoint stuck at completed during Stage 4/5 re-entry                                                                               | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0443   | Stage 4 pushes review ledger rows seconds after resolver or conflict merge, cancelling CI                                                                     | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0442   | Stage 5 calibration invokes npx prettier twice instead of local binary                                                                                        | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0441   | Stage 5 final_head_ci reports unknown on bookkeeping-gated or transient-probe heads                                                                           | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        | Medium |             M             | 0440   | Harness pre-commit Prettier check blocks commits on unstaged files from parallel sessions                                                                     | General                          |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0439   | Stage 4 resolver edits out-of-scope files and reacts to timing-gate CI failures                                                                               | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | in-progress | Medium |             M             | 0436   | Sort the three ledgers into chronological order once, and keep them sorted                                                                                    | Skills / Tooling                 |                                                                                                                                                                                                                                                       |
| **P1**   | in-progress | Medium |             M             | 0435   | dev-env improvements and cross-platform fixes                                                                                                                 | General                          |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0432   | A resolver turn aborted with code -6 leaves unsalvaged edits and an error that blames a harmless warning                                                      | Ledger / Observability           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0430   | The review-loop resolver turn has no turn budget, and a spinning test run defeats the stall budget                                                            | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0429   | Validate .beans/ header ID, title uniqueness, and filename consistency in pre_commit_check.py                                                                 | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0428   | Use PR-own 3-dot diff instead of 2-dot diff in ci_final_head and touch-set inspection                                                                         | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             M             | 0426   | Fix run_holon_flow slug truncation, bean-progress truncated-slug attribution, and subagent intent rewrites                                                    | Flow / Architecture              |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0425   | Review iterations on claude-fable-5-2 take three times as long as on claude-opus-5-5                                                                          | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0424   | A transient DNS or Docker failure ends the review stage and throws away finished reviewer work                                                                | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0423   | Two agent sessions launch flows into one workspace with no shared registry, cap or log                                                                        | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P1**   | todo        |  High  |             L             | 0422   | An --allow-overlap override is sticky: kept in the checkpoint and inherited by every later sub-intent and resume                                              | Architecture / Quality           |                                                                                                                                                                                                                                                       |
| **P2**   | todo        |  High  |             L             | 0488   | bean-progress lists a non-flow worktree as a bean row                                                                                                         | Architecture / Quality           |                                                                                                                                                                                                                                                       |

---

## Recommended Next Execution Sequence

**Checkpoint (2026-11-24):** pipeline time is the first priority: `0403` and `0405` are in flight to cut it, and nothing
that changes the review loop starts until they land. Run one flow at a time within a lane; lanes run together only when
their touch sets are disjoint.

**Ordered sequence (one line of reasoning each):**

1. **0403 and 0405** (in flight, P1): cut pipeline time first, because every flow waits on CI and the bookkeeping-only
   skip and test trim shorten all of them.
2. **0404 with 0419** (P1, fix together): the timing gates fail green jobs on slow runners, which forces re-runs and
   withdrawn consensus, so they cost pipeline time directly.
3. **0371** (P0, needs the maintainer's bot token or GitHub App first): ledger conflicts drive most churn, and it
   touches only ledgers, so it can run in its own lane beside the review-loop work.
4. **0376** (P0, in progress): it is already running and owns the in-flow conflict resolver, so it finishes before any
   other review-loop change.
5. **0407** (P0): stop re-running the full ensemble when nothing reviewable changed; it changes the review loop, so it
   runs alone after 0376 lands and not together with 0255.
6. **0255** (P0): the resolver starts on the first pipeline failure and fixes every failure of the run; it goes after
   0407 so the skip rule is in place before the resolver changes the loop.
7. **0409** (P1): a rejected finding or a no-change resolver pass should not start another full review; it builds on
   0407 and 0255, so it follows them.
8. **0197 and 0216** (in progress, P2): held behind the pipeline-time flows, so they start only after 0403, 0404, 0405
   and 0419 land and the faster pipeline is live.
