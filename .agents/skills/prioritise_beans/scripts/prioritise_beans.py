#!/usr/bin/env python3
"""
prioritise_beans.py - Triage and prioritise beans across the Holon ecosystem.

Parses all bean markdown files in .beans/, excludes completed and scrapped beans,
computes progress statistics, and generates/updates the standardized Active Beans
Triage and Prioritisation Matrix in .beans/bean-triage-prioritisation.md.

The Executive Summary narrative, the Key Milestones Completed items, the
Recommended Next Execution Sequence, and the per-bean triage overrides are
carried as inline data below. Per the skill's "Generator Maintenance" rule,
every run MUST refresh them so the generated document and the committed
document never diverge. Prose is stored unwrapped; the post-generation
`npx prettier --write` pass (proseWrap: always, printWidth 120) produces the
canonical hard-wrapped form.
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from datetime import UTC, datetime
from typing import Any

# Narrative lead-in of the Executive Summary (before the statistics bullets).
# Inline data: update it at every checkpoint. When empty, a generic lead-in
# built from the previous checkpoint date is used instead.
EXECUTIVE_SUMMARY_NARRATIVE: list[str] = [
    (
        "The harness now drives every `holon-agentic-coder` change through the 5-stage Holon flow and the "
        "`pr-review-loop`, and the maintainer merges each pull request into `main`. The most recent stretch "
        "(2026-11-10 to 2026-11-11) was dominated by one incident and its repair, described in the last paragraph "
        "below: a sandbox escape reached `main` behind a review that said `APPROVED (3/3)` while a reviewer still "
        "held an open critical finding. It was reverted, the review loop's consensus decision was fixed, and the "
        "change was re-landed with the escape closed."
    ),
    "",
    (
        "Concurrent flows on overlapping files forced repeated syncs and re-reviews earlier on (141 review-loop "
        "passes, about 10M+ tokens), so flows that touch the same files still run one after another; only flows "
        "with disjoint touch sets run together."
    ),
]

# Closing paragraph(s) of the Executive Summary (after the statistics bullets).
EXECUTIVE_SUMMARY_UPDATE: list[str] = [
    "Dates below are UTC, as in `gh`, the bean timestamps and the milestones.",
    "",
    (
        "**2026-10-26:** the first full claude-agent `holon flow` runs (Beans 0151, 0159) exposed seven defects in "
        "the flow itself. They are logged as Beans 0157-0162, and Bean 0144 was raised to critical after its "
        "fabricated approval reached GitHub. Bean 0156 starts the investigation into moving issue tracking from "
        "harness beans to beads inside each target, ahead of deprecating this harness."
    ),
    "",
    (
        "**2026-10-28:** Bean 0168 (PR #99) cut CI test time through the full flow: pytest-xdist, "
        "hermetic test git and per-worker template repositories. Real CI pytest time fell 2.5x on macOS "
        "(382 s to 153 s), 2.0x on ubuntu (242 s to 123 s) and 1.6x for Workspace survival (417 s to 258 s). "
        "It converged in 8 review iterations and was merged (`0e54457`). Bean 0144 was then delivered as three "
        "sequential flows (PRs #100, #101 and #102, all merged): Stage 4 now fails closed and is decided only by a "
        "real reviewer ensemble. New: Bean 0175 (token-scope pre-flight, logged on 2026-10-27), Bean 0176 (pytest "
        "only), Bean 0177 (architecture and code-principles research that spawns action beans), Bean 0178 "
        "(repeated test runs only for performance work) and Bean 0179 (routes the Stage 4 reviewer turns through "
        "the role container)."
    ),
    "",
    (
        "**2026-10-29:** PR #103 (Bean 0180, documentation only) nests sub-intent branches under the node that "
        "decided the split; it was merged (`e187393`) after 11 review iterations. The maintainer settled its five "
        "open questions (merge into the deciding plan or execution branch, nested PRs automatic), which a follow-up "
        "docs PR and Bean 0161 implement. New: Bean 0181 (`/_` only on branch refs)."
    ),
    "",
    (
        "Later on 2026-10-29, Bean 0143 went through the full flow from `main`, with a bootstrap build of the fix "
        "branch for the flow's own claude agents. PR #104 was approved after 3 review iterations, calibrated and "
        "merged (`cc4bf1b`), and `holon` and `holon-coherence` were reinstalled from `main`. Five further "
        "`holon-agentic-coder` flows then completed and merged: **Bean 0178** (PR #105, `c9825b8`: repeated test "
        "runs only for performance work under xdist, plus step-by-step executor commits), **Bean 0164** (PR #106, "
        "`956b4fd`: plain-language entropy and EV explainer), **Bean 0154** (PR #107, `81a12ee`: URL delimiter fuzz "
        "leak check ignores random temp paths), **Bean 0171** (PR #108, `c7dfd5e`: Stage 3 failure salvage commits "
        "partial code and resumes from `failed_partial_head`), and the `holon-agentic-coder` half of **Bean 0163** "
        "(PR #109, `993b686`: CI timing regression gate on every workflow job). On `holon-coherence`, three flows "
        "ran in parallel: **Bean 0145** (PR #28: pin Python 3.13, 3/3 ensemble approved, calibrated and merged as "
        "`0547eb4`), the coherence half of **Bean 0147** (PR #29: remove harness path/task-id leaks, merged as "
        "`68fdf67` before its consensus review was posted; post-merge follow-up PR #31 merged as `b52c7e1`), and the "
        "coherence half of "
        "**Bean 0163** (PR #30: CI timing gate, calibrated and merged as `6d9dae7` with one Important and two Nit "
        "findings still open, carried by Bean 0184). PR #108 merged before its consensus review and calibration. "
        "New: **Bean 0182** (persistent GitHub event watcher) and **Bean 0183** (every flow stage "
        "and engine bookkeeping step runs in its own sandboxed clone with no host checkout)."
    ),
    "",
    (
        "Also through the flow on 2026-10-29, both reviewed and calibrated: PR #110 (Bean 0180 follow-up docs for "
        "the five sub-intent rulings, merged as `85ef122`) and PR #111 (Bean 0158 pure-append ledger writes, merged "
        "as `8c9ff4d`). Both beans are now closed. New on 2026-10-29: **Bean 0211** (two holon-coherence A/B recipe "
        "doc fixes PR #31 left open). On 2026-10-30, **Bean 0210** (five documents PR #110 left on the old "
        "sub-intent rules) traversed the full flow, passed 3/3 ensemble review in 5 iterations, was calibrated and "
        "merged as PR #113 (`760ee87`), and harness PR #56 (`2399680`) merged after 14 review iterations. New on "
        "2026-10-30: **Bean 0212** (`pr-review-loop` delegates loop orchestration to a background subagent so the "
        "main agent stays free)."
    ),
    "",
    (
        "Later on 2026-10-30, five flow PRs traversed the full 5-stage Holon flow and merged across both targets: "
        "**Bean 0162** (HAC PR #112, `d1bdf6b`: calibration report Prettier hygiene), **Bean 0202** (HAC PR #114, "
        "`6370428`: CI timing gate composite action), **Bean 0211** (Coherence PR #33, `e475e6d`: A/B test recipe doc "
        "fixes), **Bean 0209** (Coherence PR #34, `a6912ac`: CI timing gate composite action), and **Bean 0186** "
        "(Coherence PR #35, `f7e4aa6`: Ruff complexity gate with inline noqa baseline). In addition, **Bean 0213** was "
        "logged to reflect review-loop skill rules into the native Review Loop Holon Agent."
    ),
    "",
    (
        "**Bean 0185** then completed the lint-gate pair: HAC PR #115 merged as `0e71262` (frozen 91-entry inline "
        "noqa identity baseline, `PGH004` guard against bare `# noqa`, swap-rejection test; 2 review iterations, EV "
        "72.07 predicted / 77.27 actual, and the first calibration report to pass Prettier with no follow-up commit). "
        "**Bean 0203** (Coherence PR #36, commands register their own parsers) passed 3/3 unanimous ensemble consensus "
        "review in 4 iterations, completed Stage 5 calibration (`3af551d`), and merged as `72c8d36`. "
        "**Bean 0156 (beads investigation) completed:** recommended target-native beads (`bd`) issue tracking with "
        "`hac-` and `hcoh-` prefixes, offline `refs/dolt/data` sync, migrating only open beans (~47), and archiving "
        "the harness read-only; spawned action beans 0214-0218. Harness PR driver brief codified in "
        "`FLOW_PR_DRIVER.md`."
    ),
    "",
    (
        "**Beans 0179 and 0204 merged:** HAC PR #116 (`b746408`, Bean 0179) routed Stage 4 reviewer turns through the "
        "`review-loop` role container via `_dispatch_role()`, eliminating host-side agent execution while "
        "preserving append-only ledger provenance; passed 3/3 unanimous ensemble consensus review and completed "
        "Stage 5 calibration (`4f119cd`, EV predicted 68.62 / actual 78.04, $\\Delta\\text{EV} = +9.42$). Coherence "
        "PR #37 (`9b001c3`, Bean 0204) split `mitm_addon.py` (2,348 lines) into a modular `proxy/` package by concern, "
        "unblocking the concurrent decomposition lanes (Beans 0205-0208). New beans logged: **Bean 0219** (mandatory "
        "`--agent` and `--model`, no fallback defaults), **Bean 0220** (remove PR references across flow), and "
        "**Bean 0221** (standardise Review Loop agent output with skill consensus template)."
    ),
    "",
    (
        "**Bean 0188 merged:** HAC PR #117 (`76fe3ea`, Bean 0188) split `cli.py` (2,185 lines) into a modular `cli/` "
        "package of self-registering command modules (`_role`, `init`, `flow`, `review`, `calibrate`, etc.) under "
        "`sandbox_executor/cli/commands/`, unblocking concurrent CLI maintenance; passed 3/3 unanimous approval and "
        "completed Stage 5 calibration (`1424a26`)."
    ),
    "",
    (
        "**Beans 0150 and 0205 merged:** HAC PR #118 (`e8e9a5d`, Bean 0150) eliminated hermeticity leaks where flow "
        "tests mutated the real checkout index and guarded `.git` from sandbox mutations; passed 3/3 unanimous "
        "approval and completed Stage 5 calibration (`09ba249`). Coherence PR #38 (`e3dcc1a`, Bean 0205) decomposed "
        "`MitmproxyAddon.request` and `response` hooks into an ordered step pipeline under `proxy/steps/`; passed 3/3 "
        "unanimous approval and completed Stage 5 calibration (`6a6ec15`)."
    ),
    "",
    (
        "**2026-10-31:** **Beans 0219 and 0206 merged:** HAC PR #119 (`0bb1615`, Bean 0219) made `--agent` and "
        "`--model` mandatory CLI options across all `holon` commands, removing silent fallback defaults; passed 3/3 "
        "unanimous consensus review and completed Stage 5 calibration (`4f20f01`). Coherence PR #39 (`ca43eb9`, "
        "Bean 0206) decomposed wire format handling into dedicated provider modules under `proxy/providers/` "
        "conforming to `ProviderFormat` protocol; passed 3/3 unanimous consensus review and completed Stage 5 "
        "calibration (`45ff23d`). Both repositories were synchronized to origin/main and reinstalled locally via "
        "`install-holon`."
    ),
    "",
    (
        "Later on **2026-10-31:** **Beans 0220 and 0207 merged:** HAC PR #120 (`922289f`, Bean 0220) removed GitHub "
        "PR terminology across flow CLI, report, and prompts, standardizing on platform-agnostic terms; passed 3/3 "
        "ensemble review and completed Stage 5 calibration (`8d5e57d`, predicted EV 62.24 / actual 67.46, "
        "$\\Delta\\text{EV} = +5.22$). Coherence PR #40 (`d6f1655`, Bean 0207) decomposed A/B test and metrics "
        "commands into dedicated domain packages `ab_testing/` and `metrics/`; passed 3/3 ensemble review and "
        "completed Stage 5 calibration (`ffd6c9e`, predicted EV 7.94 / actual 8.41, $\\Delta\\text{EV} = +0.47$). "
        "Both targets were synchronized to `origin/main` and reinstalled locally via `install-holon`."
    ),
    "",
    (
        "**Bean 0177 (architecture research) completed:** measured `flow.py` 5,157 lines (7 of the 14 flow PRs "
        "#94-#109 touched it), `cli.main` 1,097 lines (CC 114), `executor.main` 798 lines (CC 178), and 56 + 38 "
        "functions over CC 10. It spawned Beans 0185-0209: lint gates first (0185, 0186), then move-only splits that "
        "remove the shared files (0187, 0188, 0203, 0204), then per-module decomposition lanes that can run in "
        "parallel. The maintainer ruled that holon-coherence owns token reduction (Bean 0200)."
    ),
    "",
    (
        "**2026-11-02:** **Bean 0221 is reopened.** HAC PR #121 (`1d84c35`) is green, `MERGEABLE/CLEAN`, unanimous "
        "3/3 at iteration 1 and calibrated (predicted EV 73.21 / actual 78.35), but verification against the bean's "
        "own acceptance criteria found seven gaps: the synthesis seam in `entrypoint/review_loop.py` and `flow.py` "
        "was never built, the approved report prints five hard-coded `**Verified:**` assertions on every approval, a "
        "flag can promote a non-verdict to an `APPROVED` heading, the findings table lost the `ID` and "
        "`Recommendation` columns, the closing notice is unchanged, and `scaffold.py` (+320) invented a 16-role "
        "persona registry and its own output schema instead of mirroring the skill's - growing the prompt to 288 "
        "lines where the ruling is to shorten it. Maintainer ruling: the `pr-review-loop` skill chain is the only "
        "source of truth - and that chain documents a persona-sectioned body while the loop posts an `Ensemble "
        "Consensus Review (n/n)` comment no harness file defines, so PR #121 had nothing to copy. Part A writes that "
        "consensus template into the skills, condensed; part B mirrors it in the target through the flow. Part A "
        "landed the same day: `pr_review_prompt.md` 181 to 157 lines with a new canonical Step 3a consensus comment, "
        "`pr_reviewer` 288 to 263 with the footer and trailer defined once, and `pr_review_loop` pointing at that "
        "block at all three posting points. The part B resume then died in Stage 3 - it planned in 8.7 minutes and "
        "the executor produced no source changes at all - so part B is re-cut as its own intent, "
        "`render-review-consensus-comment-from-reviewer-data`. "
        "**Bean 0208** "
        "is still in flight on `holon-coherence` (PR #41, `2f30d6e`): Stage 3 pushed the `ProxyLifecycle` "
        "extraction, but both unit jobs are red - 9 failures across `tests/commands/test_start.py`, "
        "`tests/commands/test_web_token.py` and `tests/test_cli.py` (`SystemExit: 1` on the in-container `start` "
        "path, `stop_proxy_container` never called) - so Stage 4 has not started. No other flow is running on "
        "either target."
    ),
    "",
    (
        "**2026-11-04 to 2026-11-06:** **Bean 0221 (all 5 axes), Bean 0228, Bean 0229, Bean 0232, and Bean 0237 "
        "completed through end-to-end flow runs.** The maintainer drove `holon flow` by hand, which surfaced and fixed "
        "a train of defects: the sidecar readiness probe false positive (Bean 0227, hand-authored fix on "
        "`fix/0227-proxy-readiness-http-probe` under the explicit-instruction exception), credential-design beans "
        "0223 (flag/env audit), 0224 (claude credential auto-discovery, no `HOLON_AGENT_KEY`), 0225 (OS-keychain "
        "only), and 0226 (PR-less e2e test on a sub-1B local model with full teardown). PRs #121/#122 were closed as "
        "deprecated and their flow trees deleted when the maintainer expanded Bean 0221 into the five-axis "
        "engine/skill standardisation contract. HAC PR #123 (`43f990a`) delivered axes 1-3 (one consensus "
        "template, instructions and posted output; harness loop converged in 3 iterations, calibration ΔEV +34.21), "
        "HAC PR #124 (`bfecf0f`, Bean 0228) delivered axis 4 (engine-owned single-shot review loop with `--iteration` "
        "label split from `--max-iterations`; 4 iterations, calibration ΔEV +17.68), and HAC PR #125 (`baf3f8c`, "
        "Bean 0229) delivered axis 5 (native Stage 4 resolver inside the review loop with `applied`/`rejected` "
        "dispositions in `executions.jsonl`, 3-iteration `no-convergence` guard, and single exit posting; 3 "
        "iterations, calibrated `eb3302f`), closing umbrella **Bean 0221**. **Bean 0232** (HAC PR #126, `0f80271`: "
        "bump default per-turn timeout `DEFAULT_TURN_SECONDS` from 300 s to 3600 s; calibration ΔEV +4.64) and "
        "**Bean 0237** (HAC PR #127, `6b9264c`: increase default `review_iteration` stage budget from 15 min to "
        "120 min; calibration ΔEV +3.80) then traversed all 5 stages hands-free and merged. **Bean 0235** (HAC PR "
        "#128, `f8220eb`: Stage 4 CI is a post-review gate: launch reviewers immediately without waiting for pending "
        "CI; calibration ΔEV +10.93) and **Bean 0238** (HAC PR #129, `ecec262`: Stage 4 resolver fixes CI and test "
        "failures by synthesising first-class FindingRow for FIND-CI; calibration ΔEV +11.52) both followed and "
        "merged into `main`. **Bean 0239** (HAC PR #130, `1619cec`: Stage 5 calibration commits and pushes promoted "
        "knowledge and wisdom artifacts to /calibrated and PR) and **Bean 0240** (HAC PR #131, `3c752e6`: fix resolver "
        "`run_turn()` argument signature and enforce fail-closed verification defaults) both followed and merged into "
        "`main`. **Bean 0242** (HAC PR #132, `d932d48`: suppress Docker Desktop CLI hints and Gordon suggestions via "
        "`DOCKER_CLI_HINTS=false`) followed and merged into `main`. New beans logged: **Bean 0244** (treat knowledge "
        "and wisdom facts as immutable append-only records), **Bean 0243** (purge all harness bean references from "
        "code and docs), **Bean 0241** (persist review loop sandbox across iterations to eliminate repeated "
        "clone/teardown overhead), **Bean 0236** (post consensus review once per PR exit instead of duplicating via "
        "both `gh pr comment` and `gh pr review`), **Bean 0233** (validate fail-fast that `--repo-dir` is an attached "
        "Git worktree), and **Bean 0234** (event-driven CI check progress reporting during Stage 4 review)."
    ),
    "",
    (
        "**2026-11-06 to 2026-11-09:** Seventeen further `holon-agentic-coder` flow PRs merged: "
        "**Bean 0244** (PR #133, `2a56a89`, merged 2026-11-06: immutable append-only KB/WB fact records in "
        "`wisdom.py` with hermetic no-touch assertions), **Bean 0245** (PR #134, `4113f0d`: fix resolver runner "
        "build command), **Bean 0247** (PR #135: flow auto-creates the target worktree), **Bean 0248** (PR #136: "
        "`holon models` command), **Bean 0249** (PR #137: replace `--repo-dir` with canonical `--target-worktree`), "
        "**Bean 0251** (PR #138: pass prompts to agent runners via files), **Bean 0236** (PR #139, `d0c1334`: post "
        "the Stage 4 consensus review exactly once via `gh pr review` with a single `--comment` fallback on the "
        "HTTP 422 self-review restriction, retiring the duplicate unconditional `gh pr comment`; 3/3 consensus on "
        "iteration 1 with zero findings, calibration ΔEV +10.37 on claude-agent/claude-fable-5), **Bean 0250** "
        "(PR #140, `be6cd7b`: surface agent returncode, stderr diagnostics, and command lines in "
        "`review_ensemble.py` when reviewers fail; calibration ΔEV +4.37 on "
        "antigravity-agent/gemini-3.8-flash-medium), **Bean 0243** (PR #141, `e130dfb`: purge harness bean "
        "references and rename `[BEAN 0034 SAFETY HALT]` to `[SAFETY HALT]` across code, tests and docs; 3/3 "
        "consensus on iteration 1 with zero findings, calibration ΔEV +6.84 on claude-agent/claude-fable-5), "
        "**Bean 0201** (PR #142, `e10b4d4`: planner, executor, and reviewer prompts carry module-layout and "
        "complexity rules; 3/3 consensus on iteration 2, calibration ΔEV +6.27), **Bean 0241** (PR #143, `a17a854`: "
        "persist the Stage 4 review loop sandbox across iterations with incremental git sync; converged at "
        "iteration 10, calibration ΔEV +18.97), **Bean 0195** (PR #144, `cc2ed3e`: `GitRepository` adapter in "
        "`sandbox_executor.git` routing all executor git calls; 3/3 consensus on iteration 1, calibration "
        "ΔEV +7.10), **Bean 0233** (PR #145, `8b1e668`: fail fast when the resolved `--target-worktree` or a "
        "checkpoint's recorded worktree is not an attached git working tree; 3/3 consensus at iteration 4 on "
        "claude-agent/claude-opus-5-5, calibration ΔEV +14.85), **Bean 0149** (PR #146, `4682449`: globally unique "
        "`P-...` and `E-...` stage IDs with 8-char hex disambiguators and ledger duplicate validation; 3/3 "
        "consensus at iteration 5), **Bean 0254** (PR #147, `7258f61`: `flow.py` split into a `flow/` package, "
        "move-only, AST-verified, with a per-module size ratchet; 3/3 consensus at iteration 5 on "
        "claude-agent/claude-opus-5-5, calibration ΔEV −59.40, distorted by Beans 0257 and 0253), **Bean 0258** "
        "(PR #148, `b6cd9a6`: pinned `uv` 0.13.7 in the `holon-base` image with a build-time smoke check; a "
        "resolver that cannot run its checks or whose container fails now halts the review loop; the consensus "
        "post reports the real approval fraction and open findings; 3/3 consensus at iteration 5 on "
        "claude-agent/claude-opus-5-5, calibration ΔEV −65.23, distorted by Beans 0257 and 0253), **Bean 0257** "
        "(PR #149, `c554e8e`: dual Actual EV in Stage 5 calibration via `calibration_ev.py` and `calibration.py` "
        "reporting both Clean/Intrinsic EV without bugs and Observed EV with bugs included plus Bug EV Drag; 3/3 "
        "consensus at iteration 4 on antigravity-agent/gemini-3.8-flash-medium, predicted EV +6.24, Clean EV +6.07 / "
        "ΔEV_clean −0.17, Observed EV −2.43, Bug EV Drag +8.50), **Bean 0259** (PR #150, `8000794`: `holon flow` "
        "redirects a `main` target to a `flow-<slug>` worktree off `origin/main` and never mutates the `main` "
        "worktree; default-branch checkpoints and the direct `review`, `review-loop` and `calibrate` commands are "
        "refused; 3/3 consensus at iteration 3 on claude-agent/claude-opus-5-5, calibration ΔEV +29.58), "
        "**Bean 0256** (PR #151, `61796c6`: resolver captures `pre_resolver_head` before `_run_resolver_agent` and "
        "soft-resets any local agent commits in `_commit_and_push_resolution`, ensuring pre-push verification, "
        "canonical review trailers, and git push are never skipped; 3/3 consensus at iteration 5, "
        "calibrated ΔEV +0.53), **Bean 0266** (PR #153, `fe3b540`: the six CI workflows run on pull requests "
        "into any base branch so stacked sub-intent PRs are tested; 3/3 consensus at iteration 5 on "
        "claude-agent/claude-opus-5-5, calibration ΔEV +20.60), **Bean 0268** (PR #154, `b63fce7`: carry "
        "unmerged calibration reports into `main`), and **Bean 0161** (PR #158, `14886b8`: the plan decides "
        "decomposition; children nest under and merge into the plan branch; combined PR reaches `main`; unanimous "
        "3/3 consensus at iteration 6 on claude-agent/claude-opus-5-5, closing Bean 0161). "
        "New beans logged: **Bean 0252** (resolver preserves its rejected diff and full test output on pre-push "
        "failure), **Bean 0253** (calibration branches from the origin PR head, not a stale local ref), "
        "**Bean 0255** (streaming per-issue resolvers during Stage 4 CI & review with a single consolidated commit), "
        "**Bean 0260** (never post intermediate review iterations or aborted review passes to PR), **Bean 0261** "
        "(deduplicate and streamline PR review evaluation line in consensus report), **Bean 0262** (mount "
        "host-provisioned worktree into sandbox containers to eliminate in-container git cloning and mid-crash state "
        "loss), **Bean 0263** (retire flow.py move-proof snapshot and its test), **Bean 0264** (read module size "
        "budgets from configuration not code), **Bean 0265** (split cli/__init__.py into focused modules), "
        "**Bean 0267** (Stage 3 measured test pass rate), and **Bean 0269** (deferred nits from PR 158 review loop)."
    ),
    "",
    (
        "**2026-11-10 to 2026-11-11:** **Bean 0262** (host-provisioned worktree mounted into the role containers) "
        "first merged as PR #159 (`80b844d`) after the flow posted `APPROVED (3/3)`, although reviewer 3's final "
        "verdict was CHANGES_REQUESTED with a critical Security finding: the shared git directory let a sandbox write "
        "a sibling worktree's admin files and so run code on the host. **Bean 0272** reverted it (PR #160, "
        "`2faa325`). **Bean 0273** (PR #161, `7837fa4`) fixed the cause: the consensus verdict now comes only from "
        "what the reviewers returned, adjudication suppression covers nits only, critical, important and Security "
        "findings are never filtered, the posted review reports each verdict exactly, and a rejection of an "
        "important or higher finding needs evidence. **Bean 0262** was re-landed as PR #162 (`dd00fb9`): a "
        "read-only overlay of the git directory's `worktrees/` area, with the mounted worktree's own admin directory "
        "writable, plus `rr-cache` and `MERGE_RR` protection. A hand-assembled PR run through the repaired "
        "`pr-review-loop`, it reached a genuine unanimous 3/3 with zero findings at iteration 16 of 25, CI 11/11. "
        "**Bean 0183** was scrapped as superseded by per-flow worktrees. Usage-limit handling now waits out a named "
        "reset and resumes automatically (flow runner and review loop), and the flow runner sends a push "
        "notification when it ends. New beans: **0263** to **0265**, **0267**, **0269**, **0271**."
    ),
    "",
    (
        "**2026-11-11 to 2026-11-12:** the merge train landed in order: **Bean 0160** (PR #164, `97731e2`, review "
        "loop waits for CI outside its iteration budget), **Bean 0274** (PR #165, `660c50b`, every flow stage uses "
        "the host worktree) and **Bean 0275** (PR #166, `0528a63`, decomposed flow branch names stay under GitHub's "
        "255-character full-ref limit). #165 then broke every new flow at Stage 1: the intent and plan containers "
        "wrote `git config --local` into the shared repository (**Bean 0276**, hand-authored fix, PR #168, "
        "`56f53dd`, merged after a 3/3 review-loop approval). The first flows then showed that Stage 4 cannot run in the "
        "review-loop container, which has no ssh: **Bean 0282** (PR #171, `5d30bda`, no in-container fetch in the review "
        "target) merged after a host-driven review loop, **Bean 0224** (PR #170, `0990f34`, claude credential "
        "auto-discovery by token type) merged on a host-driven review loop and calibration, and **Bean 0284** (PR #172, "
        "`0181186`, the execution-diff check no longer fetched in the container) closed the remaining fetch site. **Bean 0283** logs that the "
        "token-reduction proxy's `cache_control` injection makes sonnet planner calls fail with an API error that the "
        "engine writes as the plan (`HOLON_TOKEN_REDUCE=0` is the workaround). The train also exposed four flow-engine defects, logged as **Beans 0277** "
        "(executor commits carry a `Co-Authored-By` trailer), **0278** (concurrent flows collide on plan file and "
        "review ids), **0279** (executor loses its push on a non-ledger sync conflict) and **0280** (no CI re-check "
        "after the calibration push), plus **Bean 0281** (carry the one calibration report that missed `main`). New "
        "beans: **0276** to **0284**. **2026-11-12 (later):** **Bean 0285** (PR #175, `f02a826`, a failed resolver pre-push gate names the failed tests, keeps the tail and writes the full output to a git-ignored file) merged after a host-driven review loop and calibration, with the in-container test skipped and CI supplying results. The run also logged **Beans 0286** (children test fetches origin), **0287** (interrupted Stage 3 leftovers block the resume) and **0288** (Stage 4 posts a changes-requested review before consensus). **Bean 0289** (PR #176, `7464836`, the suite isolation fixture scrubs `CLAUDE_CODE_OAUTH_TOKEN` and `ANTHROPIC_API_KEY`, which had failed four `test_cli.py` tests inside the credentialed review container) merged after the review loop and calibration. **Bean 0280** (PR #173, `37c59e5`, Stage 5 reports CI on the final head after the calibration push) then merged; its container pre-push gate passed. **Bean 0286** (PR #174, `a5550b5`, the children test is hermetic and a network guard fails any test that reaches a remote) closed the run. **Bean 0288** (PR #177, `89b2530`, Stage 4 posts its review only on a clean approval or at the iteration cap) merged next, then **Bean 0287** (PR #178, `ebfa3bb`, a Stage 3 resume commits interrupted leftovers as partial work) completed the chain."
    ),
]

MILESTONES_HEADING = "## Key Milestones Completed (Beans 0080 – 0296)"

# Hand-authored replacement for the generated "Recommended Next Execution
# Sequence" section, used whenever active beans exist. Inline data: keep it in
# step with the matrix at every checkpoint.
NEXT_EXECUTION_SEQUENCE: list[str] = [
    (
        "**Rule (2026-10-25):** never run concurrent flows whose touched files overlap. Nearly every "
        "holon-agentic-coder bean touches `flow.py` or `cli.py`, so those flows run **one at a time**: merge one, "
        "then plan the next on the new `main`. Only disjoint work runs in parallel. Bean 0151 will make the flow "
        "enforce this; per-flow worktrees (Beans 0259 and 0262) and Bean 0152 bring back parallelism."
    ),
    "",
    (
        "**Rule (2026-10-26):** no stage before the merge may halt for human review. The PR merge is the only human "
        "step, after consensus review and Stage 5 calibration."
    ),
    "",
    (
        "**Rule (2026-10-28):** the target suites rely solely on pytest. No new code or documentation names any other "
        "test runner (Bean 0176 removes the existing references)."
    ),
    "",
    (
        "**Tooling (2026-11-14):** `holon-agentic-coder` `main` is `291727e` (PR #193 merged) and `holon` is reinstalled "
        "from it via `install-holon`."
    ),
    "",
    (
        "**Tooling (2026-11-11):** `holon-agentic-coder` `main` (`0528a63`) and `holon-coherence` `main` (`d6f1655`) "
        "are installed editable and all agent images were rebuilt via `install-holon`, so Stage 3 partial-code "
        "salvage (#108), pure-append ledgers (#111), the calibration-report Prettier fix (#112), Stage 4 in the "
        "`review-loop` container (#116), the modular `cli/` package (#117), mandatory `--agent` / `--model` "
        "(#119), the standardised consensus review template (#123), the engine-owned single-shot review loop (#124), "
        "the native Stage 4 resolver (#125), the 3600 s default per-turn timeout (#126), the 120-minute default "
        "`review_iteration` stage budget (#127), post-review CI gating (#128), resolver CI failure repair (#129), "
        "Stage 5 calibration knowledge/wisdom artifact commits (#130), resolver command execution & fail-closed "
        "verification defaults (#131), resolver commit soft-reset (#151), all-branch CI for stacked PRs (#153), "
        "missed calibration report catch-up (#154), and plan-owned decomposition with plan-branch child nesting & "
        "autonomous merges (#158), the review-consensus honesty fix (#161) and the host-worktree sandbox mount with sibling-worktree protection (#162) are all live. `HOLON_TOKEN_REDUCE=0` stays the workaround until Beans 0227 and "
        "0157 land. Set `HOLON_STAGE_BUDGET_EXECUTE_MINUTES=10080` until Bean 0172 lands."
    ),
    "",
    (
        "**Merge / In-Flight State (2026-11-12):** `holon-agentic-coder` PRs #133–#151, #153, #154, #158, #159–#166, #168, #170, #171, #172 and #175 "
        "all merged (Beans 0244, 0245, 0247, 0248, 0249, 0251, 0236, 0250, 0243, 0201, 0241, 0195, 0233, 0149, "
        "0257, 0259, 0256, 0266, 0268, 0161, 0272, 0273, 0262, 0263, 0160, 0274, 0275, 0276, 0282, 0224, 0284, 0285, 0289, 0280, 0286, 0288, 0287); trunk is at `ebfa3bb`, installed editable, and images rebuilt via "
        "`install-holon` with `uv` 0.13.7 in the base image, Dual-EV calibration in `holon/orchestrator`, and "
        "plan-owned child nesting in `sandbox_executor/flow/`. `flow.py` is now the `flow/` package, so beans "
        "touching different `flow/` submodules can run in parallel. Harness PR #58 merged into `main` and operational "
        "tracking PR #59 is open on `docs/harness-20261106`. `fix/0227-proxy-readiness-http-probe` (`36c9765`, "
        "Bean 0227) has a green test suite and awaits the maintainer's call on PR creation. Coherence PR #41 "
        "(Bean 0208, `2f30d6e`) needs its 9 unit test failures resolved on its execution branch before Stage 4 "
        "review and Stage 5 calibration. **Worktree rule (2026-11-09):** a flow never runs in the `main` worktree; "
        "naming `main` as the target selects the repository and base branch only, and the flow runs in a "
        "`flow-<slug>` worktree off `origin/main` (Bean 0259, PR #150). Standalone external PR reviews provision "
        "`pr<N>-<slug>` only when no local worktree exists; otherwise `flow-<slug>` is reused directly across all "
        "stages. Image builds use a temporary `build-images-<sha>` worktree, and the `main` worktrees stay on `main`, "
        "identical to `origin/main`."
    ),
    "",
    (
        "**Start here (2026-11-14):** Beans 0299, 0227 and 0208 are completed. Bean 0299 landed via PR #197 (`78a8630`: "
        "Stage 5 calibrate `git diff` uses fully qualified refs and a path separator on nested sub-intent branch names; EV "
        "predicted 44.50 / actual -19.81). Bean 0227 landed via PR #198 (`40dbcc9`: `_wait_for_proxy` is an HTTP-level "
        "probe that requires real `HTTP/` response bytes; EV predicted 51.90 / actual 62.84). Bean 0208 landed via "
        "holon-coherence PR #42 (`baf5c65`, which supersedes PR #41: `ProxyLifecycle` in `container/lifecycle.py` owns "
        "`ensure_ca`, `start`, `wait_until_ready` and `stop`; EV predicted 8.05 / actual 8.45). **Bean 0151** (P0, planner "
        "touch-set estimation and overlap blocking) is in progress: resolving the plan-branch conflict, then resuming "
        "review. **Bean 0147** is in progress: PR #199 is open and its CI repair is in flight. Beans 0151 and 0147 stay "
        "in-progress. Candidate beans from the Bean 0208 run: (a) the sticky `skip_review`/`skip_calibrate` checkpoint "
        "flags across resumes; (b) the halt for human review after consensus approval, which skipped Stage 5 and needed a "
        "calibrate-only resume (a halt before merge is a bug under the no-halt-before-merge rule). The hygiene test must "
        "exempt engine-written knowledge-base records. Bean 0297 stays todo on the Stage 5 lane. "
        "Keep `HOLON_TOKEN_REDUCE=0` until Bean 0283."
    ),
    "",
    (
        "**Start here (2026-11-13):** Beans 0267, 0290, 0292, 0293, 0294 and 0295 are completed (PRs #187, #186, #188, "
        "#190 and #189; Bean 0290 is harness-only), and Bean 0281 is completed by PR #191 (`ff25d77`, which carried the "
        "calibration report and 192 ledger rows into `main`). No holon-agentic-coder PR is open. Bean 0296 is new "
        "(todo, P1: Stage 5 rebuilds a stale calibrated branch itself instead of stopping after a conflict merge, found "
        "on PR #190). The next beans to run concurrently are **Bean 0296** "
        "(`calibrate_sync.py` and `calibrate.py`) and **Bean 0260** (`flow/review/loop.py`: never post intermediate "
        "review iterations to GitHub), which touch disjoint files. Keep `HOLON_TOKEN_REDUCE=0` until Bean 0283."
    ),
    "",
    (
        "Sequential & Disjoint Lanes, holon-agentic-coder (Bean 0254 landed: lanes are now per `flow/` submodule; "
        "items 1–3 touch pairwise-disjoint files and can run concurrently):"
    ),
    "",
    (
        "1. **Review loop hygiene & reporting lane (`flow/review/` & `review_report.py`, disjoint from resolver):** "
        "**Bean 0260** (DONE, PR #192) first, then **Bean 0261**."
    ),
    (
        "   - **Bean 0260** (DONE: PR #192, merged `3b6c3d7` on 2026-11-13; `flow/review/loop.py`): never post intermediate review iterations or aborted review "
        "passes to GitHub PR; only post consensus review comments when `consensus_reached` is True or the 25-iteration "
        "budget is fully exhausted."
    ),
    (
        "   - **Bean 0261** (`review_report.py`): deduplicate and streamline the evaluation header line in consensus "
        "reports to print a single clean summary line matching canonical skill output."
    ),
    (
        "2. **Sandbox worktree mount & dead git code eradication lane (`flow/review/workspace.py` & "
        "`entrypoint/review_loop.py`):**"
    ),
    (
        "   - **Bean 0262** (DONE: re-landed as PR #162, merged `dd00fb9` on 2026-11-11 after a 16-iteration review "
        "loop; PRs #152 and #155 and their `I-1794214501-…` branches remain open as reference only): host worktree "
        "bind-mounted into the role containers with the shared git directory's `worktrees/` area read-only, so a "
        "sandbox cannot reach a sibling worktree."
    ),
    (
        "   - **Bean 0267** (`entrypoint/executor.py` + `flow/stages/` + `flow/review/loop.py` + docs; DONE: PR #187, merged `7a8f086` on 2026-11-13**"
        "): Stage 3 runs the test task and records a measured `test_pass_rate`, and the review loop "
        "measures tests itself when no CI registers, so the flow no longer depends on CI alone."
    ),
    (
        "   - **Bean 0263** (DONE: PR #163, merged `f905040` on 2026-11-11): the `flow.py` move-proof snapshot, `move_proof.py` and "
        "`test_move_proof.py` are retired and `test_package_exports.py` reads the package itself."
    ),
    (
        "   - **Bean 0265** (`cli/` + `tests/test_cli.py` + `docs/architecture.md`; **hold until Beans 0263 "
        "and 0264 merge**): move-only split of the 2,026-line `cli/__init__.py` into focused modules with re-exports, "
        "patch targets moved, and `tests/test_cli.py` split into `tests/cli/`; runs alone on `cli/`. It makes Bean "
        "0189 (launcher module) a much smaller move."
    ),
    (
        "   - **Bean 0264** (`holon-config/hygiene/` + `scripts/` + `tests/`; **hold until Bean 0263 "
        "merges**): move the `flow/` module size budgets out of `flow_module_budgets.json` and the check script's "
        "constants into `holon-config/hygiene/module_budgets.json` configuration read by a generic "
        "`check_module_budgets.py`; agents may change it, and raised limits warn instead of failing."
    ),
    ("3. **Calibration & resolver lane (`flow/stages/calibrate.py` & `entrypoint/review_loop.py`):**"),
    (
        "   - **Bean 0296** (DONE: PR #193, merged `291727e` on 2026-11-14; `calibrate_sync.py` + `calibrate.py`): Stage 5 "
        "rebuilds a stale `calibrated` branch itself instead of stopping after a conflict merge (found on PR #190)."
    ),
    (
        "   - **Bean 0297** (new, todo, P1; `flow/stages/calibrate.py` + review loop, builds on 0296): Stage 5 reruns "
        "automatically when the pull request head moves after calibration, so the merged head carries a current report."
    ),
    (
        "   - **Bean 0253** (`flow/stages/calibrate.py` + `flow/git_refs.py`): calibration branches from "
        "`origin/<E>/_` so `/calibrated` fast-forwards into the PR (recurred on PRs #147 and #148)."
    ),
    (
        "   - **Bean 0252** (`entrypoint/review_loop.py`): resolver preserves its rejected diff and full pytest output "
        "on pre-push verification failure."
    ),
    (
        "   - **Bean 0255** (streaming per-issue resolvers during Stage 4 CI & review with a single consolidated "
        "commit, paired with **Bean 0234** + **Bean 0160**), and **Bean 0151** (planner touch-set estimation)."
    ),
    ("4. **Bean 0231** (exhausted-budget error string interpolates raw count while payload reports clamped 0)."),
    (
        "5. **Bean 0189** (launcher module for container launch; breaks the `flow`-`cli` import cycle), then **Bean "
        "0190** (checkpoint and ledger reconciliation; entrypoints stop importing flow). Bean 0183 is scrapped: "
        "per-flow worktrees mounted into the containers replaced it."
    ),
    (
        "6. **Bean 0175** (check GitHub token scopes before Stage 3 starts when the plan touches workflow files), "
        "then **Bean 0146** (plans-ledger correction rows; calibration picks the right predicted metrics). Bean 0197 "
        "follows 0146 because both touch `calibration.py`."
    ),
    (
        "7. **Decomposition lanes from Bean 0177** once `0254` lands, in parallel where packages differ: "
        "0191 then 0192 (GitHub adapter, `ReviewLoop`), 0193, 0194, 0196 (now unblocked by 0195 PR #144 once 0190 "
        "lands), 0197 (after 0146), 0198 and 0199 (all tracked by umbrella Bean 0152). Bean 0153 runs per "
        "package with or right after that package's decomposition. **Bean 0213** (reflect remaining skill rules into "
        "native review-loop agent) is unblocked now that 0221 is complete."
    ),
    (
        "8. **Bean 0157** (mitmproxy sidecar reachability, alongside **Bean 0227**), **Bean 0181** (`/_` only on "
        "branch refs), **Bean 0155** then **Bean 0148** (redaction), **Beans 0172, 0174, 0173, 0223** (budgets, "
        "env-var reference, layered `.env`, CLI flag vs env audit), **Bean 0200** (holon-coherence owns token "
        "reduction; after 0189), and **Bean 0176** (pytest-only conversion of every test file; runs alone)."
    ),
    "",
    "Parallel lanes (disjoint files / repositories):",
    "",
    (
        "- **Agent Runner / Credentials lane (`holon-agentic-coder`, disjoint from `flow.py`):** **Bean 0224** (DONE, PR #170) "
        "(auto-discover `~/.holon/secrets/claude-oauth-token`, map by credential type, kill `HOLON_AGENT_KEY` and "
        "the echo-pad tunnel; touches `agent_runner.py`/pre-flight only), followed by **Bean 0225** (OS keychain "
        "storage) and **Bean 0222** (writable `~/.pi/agent` tmpfs mount so `pi-agent` flows pass pre-flight)."
    ),
    (
        "- **holon-coherence decomposition lane** (disjoint repository): PRs #36 (Bean 0203), #37 (Bean 0204), #38 "
        "(Bean 0205), #39 (Bean 0206) and #40 (Bean 0207, `d6f1655`) are merged. **Bean 0208** (`ProxyLifecycle`) is "
        "in progress as PR #41 (`2f30d6e`): fix the 9 unit test failures on the existing `E-1793439253-...` branch, "
        "then run Stage 4 review and Stage 5 calibration. Once PR #41 merges, the coherence refactoring lane is "
        "complete."
    ),
    (
        "- **Beads adoption lane (from Bean 0156):** **Bean 0214** (pilot beads in holon-agentic-coder, folding in "
        "the 0147 hac half) and **Bean 0215** (deterministic beans-to-beads JSONL converter and real-data dry run, "
        "harness work) in parallel, followed by **Bean 0216** (flow integration), **Bean 0217** (adopt in coherence), "
        "and **Bean 0218** (port harness skills to `bd` and archive harness)."
    ),
    (
        "- **E2E testing, CI observability, and local model benchmarking:** **Bean 0226** (`test-e2e` on a sub-1B "
        "local model with full teardown), **Bean 0166** (CI pipeline duration dashboard), and **Beans 0142 / 0141** "
        "(Qwen3.8 benchmarking and vmlx tuning)."
    ),
]

# Manual triage overrides for every active bean: display title, priority,
# impact, sizing, domain and notes, so each matrix cell reads as a triage
# judgement rather than a truncated first paragraph. Insertion order is the
# matrix row order (priority blocks, hand-curated within each block).
OVERRIDES: dict[str, dict[str, str]] = {
    "0280": {
        "title": "The flow does not re-check CI after the calibration push; the macOS timing gate is flaky near 300 s",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "M",
        "domain": "Calibration / CI",
        "notes": (
            "Wait for CI on the final head after Stage 5 and name failed checks. The 300 s gate headroom is a "
            "maintainer decision. Touches `flow/stages/calibrate.py`."
        ),
    },
    "0160": {
        "title": "Review loop burns its iteration budget polling pending CI, then reports test failures",
        "priority": "**P0**",
        "impact": "High",
        "sizing": "S",
        "domain": "Review Loop / CI",
        "notes": (
            "PR #101 added bounded CI waiting within the iteration budget; remaining: separate "
            "`HOLON_REVIEW_CI_WAIT_SECONDS` budget and pending-vs-failed error reporting. Pair with 0234."
        ),
    },
    "0151": {
        "title": "Planner estimates the touch set; overlapping concurrent flows are blocked",
        "priority": "**P0**",
        "impact": "High",
        "sizing": "L",
        "domain": "Holon Flow / Concurrency",
        "notes": (
            "Unblocked by 0159 (#97 merged), 0201 (#142 merged), and 0149 (#146 merged). Sequence after 0254 "
            "(`flow/` package split). Must handle `{parent}--{n}-{slug}` child branches."
        ),
    },
    "0297": {
        "title": "Stage 5 reruns automatically when the pull request head moves after calibration",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "M",
        "domain": "Holon Flow / Calibration",
        "notes": (
            "Builds on 0296 (rebuilds a stale `calibrated` branch; landed in PR #193). Related to 0253, 0292 and 0182. "
            "A head move after calibration, from a conflict merge, a resolver push or a review-loop rerun, reruns "
            "Stage 5 and marks the report stale until then."
        ),
    },
    "0299": {
        "title": "Stage 5 calibrate no longer fails with git diff 'ambiguous argument' on nested sub-intent branch names",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "S",
        "domain": "Stage 5 / Calibration",
        "notes": (
            "Open as PR #197 (`calbrnch`). Blocks Bean 0151, which needs the decomposed flow's calibration to run. "
            "Disjoint from Bean 0298 (merged as `721cd36`)."
        ),
    },
    "0300": {
        "title": "CI runs once per change, on the pull request only, not also on push",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "M",
        "domain": "CI / Token cost",
        "notes": (
            "Drop the `push` trigger from every workflow. The timing baselines on `main` must move to a "
            "`pull_request: closed` (merged) job or a schedule, so the timing gate keeps updating."
        ),
    },
    "0265": {
        "title": "Split `cli/__init__.py` into focused modules (move only), like the `flow/` package",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "L",
        "domain": "Refactor / Architecture",
        "notes": (
            "Splits the 2,026-line `cli/__init__.py` (80 definitions, 96 `mock.patch` targets, 63 importers) into "
            "`cli/{log,constants,network,credentials,repo_resolution,mounts,proxy_sidecar,env_files,containers,doctor,"
            "role_dispatch,parser}.py` with re-exports and a throwaway AST verification, no committed snapshot. Hold "
            "until PR #152 (Bean 0262) and Beans 0263 and 0264 merge. Unblocks Bean 0189."
        ),
    },
    "0264": {
        "title": "Read module size budgets from configuration instead of hardcoding paths and numbers in the check",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "M",
        "domain": "Lint / Configuration",
        "notes": (
            "Moves the `flow/` size budgets into `holon-config/hygiene/module_budgets.json` (packages, default "
            "ceiling, overrides with reasons) read by a generic `check_module_budgets.py`, deleting "
            "`flow_module_budgets.json`. Agents may change the configuration; raised limits warn instead of failing. "
            "Hold until Bean 0263 merges."
        ),
    },
    "0263": {
        "title": (
            "Retire the `flow.py` move-proof snapshot and its test: it now blocks every change to a moved function"
        ),
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "S",
        "domain": "Tests / Flow Package",
        "notes": (
            "Touches `tests/flow/` and `docs/architecture.md` only. Deletes `flow_py_definitions.json`, "
            "`move_proof.py` and `test_move_proof.py`, and reworks `test_package_exports.py` to read the package "
            "itself. Ready now that Bean 0262 has merged."
        ),
    },
    "0256": {
        "title": (
            "Resolver agent committing locally causes `_commit_and_push_resolution` to skip verification and "
            "`git push`, losing all fixes"
        ),
        "priority": "**P1**",
        "impact": "High",
        "sizing": "S",
        "domain": "Review Loop / Resolver",
        "notes": (
            "Disjoint from `flow/` (touches `entrypoint/review_loop.py` and `test_review_loop.py`). Capture "
            "`pre_resolver_head` before `_run_resolver_agent` and `git reset --soft <pre_resolver_head>` if `HEAD` "
            "moved, so `_commit_and_push_resolution` always verifies, attaches trailers, commits, and pushes."
        ),
    },
    "0260": {
        "title": "Never post intermediate review iterations or aborted review passes to GitHub PR",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "S",
        "domain": "Review Loop / Observability",
        "notes": (
            "Only post consensus review comments when `consensus_reached` is True or the 25-iteration budget is "
            "fully exhausted. Aborted, timed-out, or failed review passes remain local in `.subagent/` and are never "
            "posted to GitHub. Prevents intermediate spam on GitHub PRs."
        ),
    },
    "0261": {
        "title": "Deduplicate and streamline PR review evaluation line in consensus report",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "XS",
        "domain": "Review Loop / Report",
        "notes": (
            "Streamline redundant evaluation header text in `review_report.py` to print a single clean summary line "
            "matching canonical skill output and avoiding duplicated PR/iteration metadata."
        ),
    },
    "0262": {
        "title": (
            "Mount host-provisioned worktree into sandbox containers to eliminate in-container git cloning and "
            "mid-crash state loss"
        ),
        "priority": "**P1**",
        "impact": "High",
        "sizing": "M",
        "domain": "Flow / Sandbox / Worktree",
        "notes": (
            "Bind-mount host worktree (`flow-<slug>`) directly to `/home/holon/.holon-sandbox/workspace`. Completely "
            "purge in-container git cloning and volume resets (`_clone_or_fetch`, `_reset_reused_checkout`), named "
            "volume machinery, and associated mock tests. Unify intermediate review artifacts under "
            "`<worktree>/.subagent/`."
        ),
    },
    "0255": {
        "title": "Streaming per-issue resolvers during Stage 4 CI & review with single consolidated commit",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "L",
        "domain": "Review Loop / Concurrency",
        "notes": (
            "Spin up isolated resolvers immediately as each CI pipeline fails (e.g. `Test - Hygiene` at 10 s) while "
            "continuing to wait for remaining pipelines, then merge all resolver fixes and push a single commit per "
            "iteration. Sequence after 0254 and 0256; pairs with 0234."
        ),
    },
    "0246": {
        "title": "Eliminate duplicate review comments in harness `pr-review-loop` skill",
        "priority": "**P2**",
        "impact": "Low",
        "sizing": "XS",
        "domain": "Skills / Harness",
        "notes": "Target-side fix landed in PR #139 (Bean 0236); verify/close remaining harness skill doc wording.",
    },
    "0239": {
        "title": (
            "Stage 5 calibration commits and pushes promoted knowledge and wisdom artifacts to /calibrated and PR"
        ),
        "priority": "**P1**",
        "impact": "High",
        "sizing": "S",
        "domain": "Stage 5 / Calibration",
        "notes": (
            "Stage and commit `holon-knowledge/kb/` and `holon-knowledge/wisdom/` in `run_calibration_stage()` so "
            "promoted failure modes, patterns, and heuristics are included on `/calibrated` and in the PR. Intent "
            "in `todo/`."
        ),
    },
    "0236": {
        "title": (
            "Post consensus review once per PR exit instead of duplicating via both gh pr comment and gh pr review"
        ),
        "priority": "**P1**",
        "impact": "High",
        "sizing": "S",
        "domain": "Review Loop / GitHub",
        "notes": (
            "`post_pr_review_consensus()` currently calls both `gh pr comment` and `gh pr review` (which falls back "
            "to `gh pr review --comment` on HTTP 422), producing 2 identical posts on PR #126. Submit once via `gh "
            "pr review`. Intent in `todo/`."
        ),
    },
    "0233": {
        "title": "Validate that `--repo-dir` is an attached git worktree",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "S",
        "domain": "CLI / Flow Validation",
        "notes": (
            "Fail fast before Stage 1 or checkpoint resume if `--repo-dir` is a bare repo or non-worktree directory "
            "(`git rev-parse --is-inside-work-tree`), preventing hours-in Stage 4/5 host checkout crashes. Intent in "
            "`todo/`."
        ),
    },
    "0234": {
        "title": "Event-driven CI check progress reporting during Stage 4 review",
        "priority": "**P1**",
        "impact": "Medium",
        "sizing": "S",
        "domain": "Review Loop / Logging",
        "notes": (
            "Log total CI pipelines once at start (`Tracking N GitHub CI check(s)...`) and emit a log line only "
            "when a check completes or changes state, suppressing 15 s polling noise. Intent in `todo/`; pair with "
            "0160."
        ),
    },
    "0227": {
        "title": "Sidecar readiness probe false positive (docker-proxy accepts before mitmproxy binds)",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "S",
        "domain": "Token Reduce / Proxy",
        "notes": (
            "Fix complete on `fix/0227-proxy-readiness-http-probe` (`36c9765`), suite green; hand-authored under "
            "the explicit-instruction exception. Awaiting maintainer call on PR creation."
        ),
    },
    "0187": {
        "title": "Split `flow.py` into a `flow/` package, one module per stage and concern (move only)",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "L",
        "domain": "Refactor / Architecture",
        "notes": (
            "After 0185 (#115 merged) and 0188 (#117 merged). >5,500 lines; AST-verified move only. Runs alone among "
            "`flow.py` PRs; unblocks 0189, 0190, 0191, 0193, 0194, 0197."
        ),
    },
    "0189": {
        "title": "Launcher module owns container launch and role dispatch; break the `flow` -> `cli` cycle",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "M",
        "domain": "Refactor / Architecture",
        "notes": "After 0187 (0188 is merged as #117); unblocks 0200. Runs with 0190 and precedes 0183.",
    },
    "0190": {
        "title": "`FlowCheckpoint` and ledger reconciliation own their behaviour; entrypoints stop importing flow",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "M",
        "domain": "Ledger / Holon Flow",
        "notes": "After 0187; 0158 (PR #111, same code) has merged. Precedes 0183. Unblocks 0196, 0199.",
    },
    "0191": {
        "title": "One GitHub adapter owns every `gh` call (PR, CI probe, mergeability, review posting)",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "M",
        "domain": "GitHub / Architecture",
        "notes": "After 0187. Unblocks 0192.",
    },
    "0195": {
        "title": "Executor entrypoint's raw `git` subprocess calls go through a `GitRepository` adapter",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "M",
        "domain": "Executor / Git",
        "notes": "After 0185 (#115 merged). 81 raw `git` calls; disjoint from `flow.py`. With 0190, unblocks 0196.",
    },
    "0192": {
        "title": "`run_review_loop` and `run_review_stage` become a `ReviewLoop` object with named steps",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "L",
        "domain": "Review Loop / Refactor",
        "notes": "After 0191. 528 lines, CC 131. Sequence after 0160/0234 (same touch set).",
    },
    "0196": {
        "title": "Executor entrypoint `main` becomes an `ExecutionRun` with named steps; module becomes a package",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "L",
        "domain": "Executor / Refactor",
        "notes": "After 0195 and 0190. 798 lines, CC 178 (worst in the repository).",
    },
    "0175": {
        "title": "Check GitHub token scopes before Stage 3 when the plan touches workflow files",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "S",
        "domain": "Holon Flow / GitHub",
        "notes": (
            "A 55-minute Stage 3 for Bean 0168 was lost to a push rejected for the missing `workflow` scope. "
            "Complements 0171 (#108 merged, refused-push patch salvage)."
        ),
    },
    "0157": {
        "title": "`holon flow` auto-enables the mitmproxy sidecar; role containers cannot reach it",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "S",
        "domain": "Holon Flow / Proxy",
        "notes": "Workaround: `HOLON_TOKEN_REDUCE=0`. Pairs with 0227 (`fix/0227-proxy-readiness-http-probe`).",
    },
    "0161": {
        "title": "Decomposed sub-intents have no flow path to `main` and do not build on each other",
        "priority": "**P0**",
        "impact": "High",
        "sizing": "L",
        "domain": "Holon Flow",
        "notes": (
            "Blocks Bean 0262 (PRs #152 and #155). Corrected design 2026-11-09: Stage 2 records the split decision on "
            "the plan; Stage 3 only executes the children; children are cut from and target the plan branch; a "
            "combined PR carrying the parent plan and every child reaches `main`; resume continues an existing child "
            "instead of re-running it. Open decision: who merges a child PR into the plan branch. "
            "Docs: PRs #103, #110 and #113 (all merged)."
        ),
    },
    "0149": {
        "title": "Plan and execution IDs collide across concurrently planned intents",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "M",
        "domain": "Provenance / Planner",
        "notes": "#91 and #92 shared `P-1792765112`. Prerequisite for 0151.",
    },
    "0155": {
        "title": "General `HOLON_*` forwarding puts credential-shaped values on the docker argv",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "M",
        "domain": "Security",
        "notes": "Already on main. Default fix: send every `HOLON_*` value through the 0600 env-file.",
    },
    "0148": {
        "title": "Redact before truncating ledger `error_context`; close `CredentialRedactor` gaps",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "M",
        "domain": "Security / Ledger",
        "notes": "Route those rows through `redact_agent_secrets`.",
    },
    "0146": {
        "title": "Plans-ledger correction rows; calibration picks the right predicted metrics",
        "priority": "**P1**",
        "impact": "Medium",
        "sizing": "M",
        "domain": "Calibration / Ledger",
        "notes": (
            "Every calibration in the 2026-10-26 batch needed a manual annotation. Runs before 0197 (same parser)."
        ),
    },
    "0213": {
        "title": "Reflect review-loop skill rules into native Review Loop Holon Agent",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "M",
        "domain": "Review Loop / Prompts",
        "notes": (
            "Target: `holon-agentic-coder`. Unblocked now that 0221/0228/0229 are merged: reflects target-branch "
            "conflict checks, ledger-only fast resolution, and model fallback into `review_loop.template.md`."
        ),
    },
    "0214": {
        "title": "Pilot beads (bd) issue tracking inside holon-agentic-coder",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "M",
        "domain": "Issue Tracking / Pilot",
        "notes": (
            "Holon flow against holon-agentic-coder. `bd init` prefix `hac-`, offline config, pin `bd` in image, "
            "import open beans, fold in 0147 hac half. Precursor to 0215-0218."
        ),
    },
    "0215": {
        "title": "Deterministic beans-to-beads JSONL converter and real-data dry run",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "S",
        "domain": "Issue Tracking / Migration",
        "notes": (
            "Harness work. Converts bean frontmatter + body to beads JSONL for `bd import`; verified on all open "
            "beans per rule 10. Unblocks 0217."
        ),
    },
    "0172": {
        "title": "Stage and turn budgets accept an explicit 'unlimited' value, distinct from unset (default)",
        "priority": "**P1**",
        "impact": "Medium",
        "sizing": "S",
        "domain": "Holon Flow / Config",
        "notes": "Workaround today: `HOLON_STAGE_BUDGET_EXECUTE_MINUTES=10080`. Pair with or follow 0232.",
    },
    "0173": {
        "title": "holon loads layered .env files (specific overrides broad) that every sandbox stage inherits",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "M",
        "domain": "Holon Flow / Config",
        "notes": "Project `.env` overrides the broader `.env`. Touches `cli/`; sequence after 0155/0148 and 0174.",
    },
    "0174": {
        "title": "Document every environment variable holon reads, in one generated and CI-checked reference",
        "priority": "**P1**",
        "impact": "Medium",
        "sizing": "M",
        "domain": "Documentation / Config",
        "notes": (
            "After 0172; precursor to 0173, whose layered `.env` needs this reference's allow-list and secret flags."
        ),
    },
    "0176": {
        "title": "Remove every unittest reference from holon-agentic-coder; the suite is pytest only",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "L",
        "domain": "Tests",
        "notes": (
            "Unblocked by 0168 (#99 merged). 59 `TestCase` classes and about 60 `unittest.mock` imports in 29 files. "
            "Runs alone: it touches most test files."
        ),
    },
    "0166": {
        "title": "Pipeline duration dashboard for CI builds",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "M",
        "domain": "CI / Observability",
        "notes": "Check org Actions performance metrics first. Shares data and baseline with 0163 (#109, #30).",
    },
    "0152": {
        "title": "Audit long files; decompose oversized functions (flow.py, cli.py first)",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "XL",
        "domain": "Refactor / Concurrency",
        "notes": (
            "Umbrella for the Bean 0177 action beans 0185-0200 and 0203-0208; 0185, 0186, 0188, and 0203-0207 are "
            "merged. Remaining: `flow.py` split (0187) and per-module lanes."
        ),
    },
    "0208": {
        "title": "holon-coherence: a `ProxyLifecycle` class owns proxy start-up, readiness and teardown",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "M",
        "domain": "Proxy / holon-coherence",
        "notes": (
            "In progress as coherence PR #41 (`2f30d6e`): Stage 3 pushed, but both unit jobs are red (9 failures in "
            "`test_start.py`, `test_web_token.py`, `test_cli.py`), so Stage 4 has not started. Resume from the "
            "existing execution branch; 0203-0207 are merged."
        ),
    },
    "0225": {
        "title": "Claude token lives only in the OS keychain; retire the plaintext secrets file",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "M",
        "domain": "Agent Runner / Credentials",
        "notes": "After 0224 (extends its discovery seam). Keychain-only; one-time migration deletes the file.",
    },
    "0223": {
        "title": "Audit CLI flags vs HOLON_* env vars: four-kind decision rule, flag>env precedence",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "L",
        "domain": "CLI / Config",
        "notes": (
            "Exhaustive inventory of every add_argument and os.getenv; boundary-crossing=both, "
            "per-invocation=flag, ambient=env-primary, secrets=env-only."
        ),
    },
    "0226": {
        "title": "End-to-end test for the holon flow commands with full teardown",
        "priority": "**P2**",
        "impact": "High",
        "sizing": "L",
        "domain": "Testing / E2E",
        "notes": (
            "Runs on a sub-1B local model via the `local_llm` envelope (no cloud secrets); never opens a PR; "
            "unconditional teardown of worktrees and remote `I-…` trees; invariant assertions + bounded whole-run "
            "retries. Operator-run `test-e2e` task, excluded from CI."
        ),
    },
    "0230": {
        "title": "Purge residual harness bean ids from target sources",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "S",
        "domain": "Hygiene / Rule 12",
        "notes": "PR #123 loop deferral (out-of-increment). Touches `flow.py` - unblocked now that 0229 is merged.",
    },
    "0181": {
        "title": "Use the `/_` leaf only when referencing a git branch, never on ids",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "M",
        "domain": "Holon Flow / Ledger",
        "notes": (
            "`intents.jsonl` `branch` and `parent_intent_id` hold refs; migrate with readers accepting both shapes. "
            "After 0161 (overlaps `flow.py`; 0179 is merged)."
        ),
    },
    "0296": {
        "title": "Stage 5 rebuilds a stale calibrated branch itself instead of stopping after a conflict merge",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "S",
        "domain": "Stage 5 / Calibration",
        "notes": "Found on PR #190: the flow ended with a failed Stage 5 after a conflict merge. Touches calibrate_sync.py and calibrate.py.",
    },
    "0153": {
        "title": "Remove comments and docstrings from all code; make it self-documenting",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "XL",
        "domain": "Readability",
        "notes": (
            "Per package, with or right after that package's decomposition (which follows its split: 0187, 0188, "
            "0204), not as one repository-wide flow."
        ),
    },
    "0147": {
        "title": "Remove harness paths tracked in the target repositories",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "S",
        "domain": "Hygiene",
        "notes": (
            "`holon-coherence` half merged (PR #29, `68fdf67`; follow-up PR #31, `b52c7e1`). `holon-agentic-coder` "
            "half pending (fold into 0214 when beads lands)."
        ),
    },
    "0193": {
        "title": "Decompose the intent and plan stage modules",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "M",
        "domain": "Holon Flow / Refactor",
        "notes": "After 0187; parallel decomposition lane.",
    },
    "0194": {
        "title": "`run_execute_stage` becomes an `ExecuteStage` with named steps",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "M",
        "domain": "Holon Flow / Refactor",
        "notes": "After 0187; parallel decomposition lane. 306 lines, CC 40.",
    },
    "0197": {
        "title": "Split `calibration.py` into a package; decompose metrics parsing and report generation",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "M",
        "domain": "Calibration / Refactor",
        "notes": "After 0187 and 0146 (0162 is merged as #112); parallel lane otherwise.",
    },
    "0198": {
        "title": "Agent runner registry: one `RunnerSpec` module per agent",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "M",
        "domain": "Runners / Refactor",
        "notes": "After 0185 (#115 merged); parallel lane.",
    },
    "0201": {
        "title": "Planner, executor and reviewer prompts carry the module-layout, complexity and naming rules",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "S",
        "domain": "Prompts / Standards",
        "notes": "After 0185 (#115 merged). Plans declare touch sets at module granularity (feeds 0151).",
    },
    "0200": {
        "title": "Remove holon-agentic-coder's diverged `token_reduction` copy; holon-coherence is the owner",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "M",
        "domain": "Token Reduction",
        "notes": "After 0189. Ownership already ruled: holon-coherence owns token reduction.",
    },
    "0199": {
        "title": "Decompose ledger query and the knowledge index",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "M",
        "domain": "Ledger / Knowledge",
        "notes": "After 0190; parallel lane. Low bean priority.",
    },
    "0216": {
        "title": "Holon flow references and drives beads work items (claim on intent, close on merge)",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "M",
        "domain": "Holon Flow / Beads",
        "notes": (
            "Holon flow against holon-agentic-coder. Intent `work_item` field, `holon intent` claims issue, "
            "calibration/merge closes with PR URL. Sequence after 0214."
        ),
    },
    "0217": {
        "title": "Adopt beads (bd) issue tracking inside holon-coherence",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "S",
        "domain": "Issue Tracking / Coherence",
        "notes": (
            "Holon flow against holon-coherence. `bd init` prefix `hcoh-`, import open coherence beans from 0215 "
            "converter. Sequence after 0214 and 0215."
        ),
    },
    "0218": {
        "title": "Port harness skills and guidance to bd and sequence the harness retirement",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "M",
        "domain": "Harness Deprecation",
        "notes": (
            "Harness work. Retire triage matrix / `prioritise-beans` for `bd ready --json`; port guidance; archive "
            "harness read-only after pilots succeed."
        ),
    },
    "0142": {
        "title": "Real-workload benchmark: Qwen3.8-27B dense vs Flash-Next MoE",
        "priority": "**P2**",
        "impact": "High",
        "sizing": "L",
        "domain": "Model Selection",
        "notes": "Real data only (AGENTS.md item 10).",
    },
    "0231": {
        "title": "Exhausted-budget error string interpolates raw count while payload reports clamped 0",
        "priority": "**P3**",
        "impact": "Low",
        "sizing": "XS",
        "domain": "Flow Engine / Cosmetic",
        "notes": "PR #124 loop deferral (cosmetic, out-of-increment). Touches `flow.py` - bundle with 0230.",
    },
    "0269": {
        "title": "Deferred nits from the holon-agentic-coder PR 158 review loop",
        "priority": "**P3**",
        "impact": "Low",
        "sizing": "XS",
        "domain": "Review Loop / Housekeeping",
        "notes": (
            "Three deferred nits from PR #158: fold `parse_actual_metrics` onto `_record_exit_code`, "
            "removed-definitions test proof, and `docs/git_flow.md` checkpoint wording."
        ),
    },
    "0141": {
        "title": "Tune vmlx prefill/decode levers for both Qwen3.8 models, crash-safe",
        "priority": "**P3**",
        "impact": "Medium",
        "sizing": "M",
        "domain": "vmlx / Performance",
        "notes": "Pairs with 0142.",
    },
}


def parse_frontmatter(content: str) -> dict[str, Any]:
    """Parse YAML frontmatter using standard library regex.

    Supports plain single-line scalars and quoted scalars folded onto the
    following indented line(s), e.g.::

        title:
          "A long title that continues
          on the next line"
    """
    parts = content.split("---")
    if len(parts) < 3:
        return {}
    fm_text = parts[1]
    res: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in fm_text.splitlines():
        if raw_line[:1] in (" ", "\t") and current_key is not None:
            cont = raw_line.strip()
            if not cont or cont.startswith("- "):
                # Blank line or list item: not a scalar continuation.
                current_key = None
                continue
            prev = res[current_key]
            res[current_key] = f"{prev} {cont}" if prev else cont
            continue
        current_key = None
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([a-zA-Z0-9_-]+):\s*(.*?)\s*$", line)
        if m:
            key, val = m.group(1), m.group(2)
            res[key] = val
            current_key = key
    for key, val in list(res.items()):
        # Strip paired quotes once the full (possibly folded) scalar is joined.
        quoted = len(val) >= 2 and (
            (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'"))
        )
        if quoted:
            res[key] = val[1:-1]
    return res


def extract_bean_metadata(filepath: str) -> dict[str, Any] | None:
    """Extract bean ID, frontmatter, and contextual metadata from file."""
    basename = os.path.basename(filepath)
    if basename == "template.md" or not basename.endswith(".md"):
        return None

    # Match ID: e.g. holon-agentic-coder-ref-metadata-0118--...
    m = re.search(r"(\d{4})--", basename)
    if not m:
        return None
    bean_num = m.group(1)

    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    fm = parse_frontmatter(content)
    status = fm.get("status", "todo").lower()
    priority = fm.get("priority", "normal").lower()
    title = fm.get("title", "")

    # Priority mapping
    priority_level = "P1"
    if priority == "critical":
        priority_level = "P0"
    elif priority in ("high", "normal", "medium"):
        priority_level = "P1"
    elif priority in ("low", "minor"):
        priority_level = "P2"

    # Known domain and sizing heuristics
    impact = "Medium"
    sizing = "M"
    domain = "General"
    notes = ""

    # Determine domain from tags or content
    content_lower = content.lower()
    if "holon-flow" in content_lower or "sandbox_executor" in content_lower:
        domain = "Flow / Architecture"
        impact = "High"
    elif "metrics" in content_lower or "telemetry" in content_lower:
        domain = "CLI / Telemetry"
    elif "makefile" in content_lower or "build" in content_lower:
        domain = "Build / DevEx"
    elif "license" in content_lower:
        domain = "Legal / Governance"
        impact = "Medium"
        sizing = "S"
    elif "spelling" in content_lower:
        domain = "Standards / Style"
        impact = "Low"
        sizing = "S"
    elif "audit" in content_lower:
        domain = "Architecture / Quality"
        impact = "High"
        sizing = "L"
    elif "skill" in content_lower:
        domain = "Skills / Tooling"
    elif "ledger" in content_lower or "executions.jsonl" in content_lower:
        domain = "Ledger / Observability"
        impact = "High"

    # Extract summary sentence for notes if available (with fallback to ## Context)
    summary_m = re.search(r"## Summary\s*\n+([^\n#]+)", content)
    if not summary_m:
        summary_m = re.search(r"## Context\s*\n+([^\n#]+)", content)
    if summary_m:
        notes = summary_m.group(1).strip()
        # Truncate if too long for clean table display
        if len(notes) > 130:
            notes = notes[:127].rsplit(" ", 1)[0] + "..."

    return {
        "bean_num": bean_num,
        "title": title,
        "status": status,
        "priority_raw": priority,
        "priority_level": priority_level,
        "impact": impact,
        "sizing": sizing,
        "domain": domain,
        "notes": notes,
        "filepath": filepath,
    }


def read_previous_checkpoint(output_path: str) -> str | None:
    """Read the ``**Last Updated:**`` date from an existing triage document, if present."""
    try:
        with open(output_path, encoding="utf-8") as f:
            head = f.read(4096)
    except OSError:
        return None
    m = re.search(r"\*\*Last Updated:\*\*\s*(\d{4}-\d{2}-\d{2})", head)
    return m.group(1) if m else None


def scan_beans(beans_dir: str) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Scan all beans in directory, returning active list and count statistics."""
    files = sorted(glob.glob(os.path.join(beans_dir, "holon-agentic-coder-ref-metadata-*.md")))
    total_tracked = 0
    completed_count = 0
    scrapped_count = 0
    in_progress_count = 0
    draft_count = 0
    active_beans: list[dict[str, Any]] = []

    for fpath in files:
        b = extract_bean_metadata(fpath)
        if not b:
            continue
        total_tracked += 1
        status = b["status"]
        if status in ("completed", "done"):
            completed_count += 1
        elif status == "scrapped":
            scrapped_count += 1
        else:
            # Active bean (todo, in-progress, draft)
            if status == "in-progress":
                in_progress_count += 1
            elif status == "draft":
                draft_count += 1
            bnum = b["bean_num"]
            if bnum in OVERRIDES:
                ov = OVERRIDES[bnum]
                b["title"] = ov.get("title", b["title"])
                b["priority_display"] = ov["priority"]
                b["impact"] = ov["impact"]
                b["sizing"] = ov["sizing"]
                b["domain"] = ov["domain"]
                b["notes"] = ov["notes"]
            else:
                b["priority_display"] = f"**{b['priority_level']}**"
            active_beans.append(b)

    # Sort active beans: curated OVERRIDES order first (its insertion order is
    # the matrix row order), then any bean without an override by priority
    # (P0 -> P1 -> P2 -> P3) and bean number descending.
    override_order = {bnum: i for i, bnum in enumerate(OVERRIDES)}
    priority_order = {"**P0**": 0, "**P1**": 1, "**P2**": 2, "**P3**": 3}
    active_beans.sort(
        key=lambda x: (
            0 if x["bean_num"] in override_order else 1,
            override_order.get(x["bean_num"], 0),
            priority_order.get(x["priority_display"], 9),
            -int(x["bean_num"]),
        )
    )

    stats = {
        "total_tracked": total_tracked,
        "completed": completed_count,
        "scrapped": scrapped_count,
        "active": len(active_beans),
        "in_progress": in_progress_count,
        "draft": draft_count,
    }
    return active_beans, stats


def generate_triage_document(
    active_beans: list[dict[str, Any]],
    stats: dict[str, int],
    timestamp_str: str | None = None,
    previous_checkpoint: str | None = None,
) -> str:
    """Generate Markdown document adhering strictly to the ecosystem triage format."""
    total = stats["total_tracked"]
    completed = stats["completed"]
    scrapped = stats["scrapped"]
    active = stats["active"]
    in_progress = stats.get("in_progress", 0)
    draft = stats.get("draft", 0)
    todo = active - in_progress - draft

    completed_pct = (completed / total * 100) if total else 0
    scrapped_pct = (scrapped / total * 100) if total else 0
    active_pct = (active / total * 100) if total else 0

    ts = timestamp_str or datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines: list[str] = [
        "# Holon Ecosystem Bean Triage and Prioritisation Matrix",
        "",
        f"**Last Updated:** {ts}",
        "",
        "## Executive Summary",
        "",
    ]
    if EXECUTIVE_SUMMARY_NARRATIVE:
        lines.extend(EXECUTIVE_SUMMARY_NARRATIVE)
    else:
        lines.append(
            f"Since the previous triage checkpoint on {previous_checkpoint}, the Holon ecosystem has progressed "
            "through automated Holon flow cycles, multi-agent consensus review loops, and infrastructure hardening."
            if previous_checkpoint
            else (
                "As of this checkpoint, the Holon ecosystem has progressed through automated Holon flow cycles, "
                "multi-agent consensus review loops, and infrastructure hardening."
            )
        )
    lines.extend(
        [
            "",
            f"- **Total Tracked Beans**: {total} (excluding template)",
            f"- **Completed**: {completed} ({completed_pct:.1f}%)",
            f"- **Scrapped / Superseded**: {scrapped} ({scrapped_pct:.1f}%)",
            f"- **Active**: {active} ({active_pct:.1f}%), of which {in_progress} are in progress"
            + (f", {todo} are todo and {draft} are draft" if draft else f" and {todo} are todo"),
        ]
    )
    if EXECUTIVE_SUMMARY_UPDATE:
        lines.append("")
        lines.extend(EXECUTIVE_SUMMARY_UPDATE)
    lines.extend(
        [
            "",
            "---",
            "",
            MILESTONES_HEADING,
            "",
            "1. **Holon Flow and Automation Engine**:",
            "   - `0084`: Fixed CI check name collisions in review gates.",
            "   - `0087`: Permitted autonomous PR creation in Holon flow stage 3.",
            (
                "   - `0089`: Auto-routed all flow stages through Holon Coherence proxy for token deduplication "
                "and caching."
            ),
            "   - `0093`: Atomic ledger locking with exponential backoff and `flock`.",
            "   - `0094`: Checkpoint schema versioning and automated state migration.",
            "2. **Action Knowledge Base and Wisdom (Bean 0052 / PR #78)**:",
            (
                "   - Full integration of the SQLite FTS5 inverted index over the canonical `executions.jsonl` ledger "
                "(the auxiliary `actions.jsonl` was later retired by Bean 0123)."
            ),
            "   - Pre-action wisdom consult (`holon consult`) across intent, planning, execution, and review stages.",
            "   - Statistical Wilson score promotion ladder and deterministic failure veto engine.",
            "3. **Multi-Agent Review Loop and Hygiene (PR #52)**:",
            "   - `0099`: Write-capable children and nested Prettier formatting guards.",
            (
                "   - `0103`: Implemented `clean-workspace` skill and Python automation (`clean_workspace.py`) "
                "covering worktrees, branches, orphan directories, `.subagent/` review caches, and `todo/` scratchpads."
            ),
            "   - Passed 100% unanimous 3/3 ensemble consensus approval on PR #52.",
            "4. **Agent Container Modernisation and Buildx Bake Integration (Beans 0112 and 0114 / PR #80)**:",
            (
                "   - Upgraded all container images (`@anthropic-ai/claude-code@2.1.302`, `@openai/codex@0.163.0`, "
                "`@google/gemini-cli@0.64.0`, `opencode-ai@1.19.3`, `@earendil-works/pi-coding-agent@1.3.0`)."
            ),
            "   - Added hardened writable tmpfs overlays for Antigravity and Codex session logs and caches.",
            "   - Fully automated Buildx Bake builds across all 8 role/orchestrator images with layer caching.",
            "5. **Ecosystem Build and Installation Automation (Bean 0117)**:",
            (
                "   - Implemented `install-holon` and `install-coherence` skills "
                "(`.agents/skills/install_holon/SKILL.md`, "
                "`.agents/skills/install_coherence/SKILL.md`) and companion Python orchestrators (`install_holon.py`, "
                "`install_coherence.py`)."
            ),
            (
                "   - Automates building Docker images via Buildx Bake and installing/updating `holon` and "
                "`holon-coherence` via `uv tool install`."
            ),
            "6. **Native Review Loop and Metrics Alignment (Beans 0115 and 0118 / PR #23 & PR #81)**:",
            (
                "   - `0115`: Stripped all emojis from `holon-coherence metrics` terminal table and aligned colon "
                "spacing at column 31. Raised PR #23 on `holon-coherence`, passed 3-agent ensemble review."
            ),
            (
                "   - `0118`: Implemented explicit native `holon review-loop` CLI step (Stage 4) in "
                "`holon-agentic-coder`. "
                "Raised PR #81, resolved findings in iteration 1, passed 3-agent ensemble review, "
                "and completed Stage 5 calibration."
            ),
            (
                "7. **Makefile Alignment, PR Metadata, and Ledger Enhancements (Beans 0116, 0113, 0119, 0109 / "
                "PR #25 & PR #82)**:"
            ),
            (
                "   - `0116`: Added `build-images` alias, `tools`, and `lint` targets in `holon-coherence` (PR #25); "
                "added `build-image` alias in `holon-agentic-coder` (PR #82)."
            ),
            (
                "   - `0109`: Automated conventional commit PR titles (`feat(...)`, `fix(...)`) and structured "
                "Markdown "
                "bodies with Summary, Changes, and Beans."
            ),
            (
                "   - `0119`: Dual-posting review consensus (top-level comment + official review) with HTTP 422 author "
                "self-approval fallback."
            ),
            (
                "   - `0113`: Granular action logging in `executions.jsonl` recording evaluations, findings, resolver "
                "triggers, and consensus posting."
            ),
            "8. **Decoupled Architecture and Canonical 3-Ledger Consolidation (Beans 0122 and 0123 / PR #85)**:",
            (
                "   - Purged all harness-specific metadata paths (`.beans/`, `todo/`, `.agents/`) from target "
                "repositories."
            ),
            (
                "   - Retired auxiliary `actions.jsonl` ledger; interleaved all discrete micro-actions "
                "(`entry_type: 'action'`) "
                "and run summaries (`entry_type: 'summary'`) inside `executions.jsonl` under `LedgerLock`."
            ),
            (
                "   - Codified harness isolation, test execution constraints (strictly `uv run pytest`), "
                "and ledger invariants "
                "across ecosystem instructions."
            ),
            (
                "9. **Unified Git Abstraction, Unprivileged Containers, and Hardened Locking (Beans 0124 – 0127 / "
                "PR #86)**:"
            ),
            (
                "   - `0124`: Implemented unified Git abstraction in `sandbox_executor.git` with custom "
                "exceptions and strict stderr diagnostics."
            ),
            "   - `0125`: Australian English spelling hygiene across documentation and codebase comments.",
            "   - `0126`: Enforced unprivileged Docker execution via `--cap-drop=ALL` with selective capability drops.",
            "   - `0127`: Hardened `LedgerLock` concurrency file locking with exponential backoff and timeouts.",
            (
                "10. **Documentation Gap Remediation and Container `gh` Availability (Beans 0128 and 0131 / PR #87 & "
                "PR #88)**:"
            ),
            (
                "    - `0128`: Closed documentation drift across `holon-agentic-coder` (PR #87) and the harness, "
                "so flow "
                "stage, ledger, and worktree instructions match the implemented behaviour."
            ),
            (
                "    - `0131`: Installed the GitHub CLI into `holon-base` so every agent image and the Stage 4 "
                "review-loop "
                "container can post consensus reviews, plus container availability tests (PR #88, Stage 5 calibrated)."
            ),
            "11. **Proxy Cold-Start Readiness and Agent Runner Tests (Bean 0130 / holon-coherence PR #26)**:",
            (
                "    - Replaced the fixed-sleep readiness probe with HTTP readiness polling, deduplicated the proxy "
                "`chmod` handling, routed readiness probes around the proxy, and added agent runner integration tests."
            ),
            (
                "    - Traversed all 5 Holon flow stages and passed unanimous 3/3 ensemble consensus at iteration 4; "
                "residual nits were deferred to Beans 0132 and 0133 instead of being dropped."
            ),
            "12. **Ecosystem install refresh and flow-integrity audit (2026-10-22)**:",
            (
                "    - Rebuilt all nine container images via Buildx Bake and reinstalled `holon` / `holon-coherence` "
                "editable from `origin/main` (`holon-agentic-coder` `3bef6f7`, `holon-coherence` `29b7e50`)."
            ),
            (
                "    - Attempted the three remaining beans through the Holon flow and recorded why they could not "
                "complete: Bean 0134 (the unified `holon flow` runner dispatches no role agent and opened the "
                "now-closed empty PR #89), Bean 0135 (mergeability verdict fabricated from a missing ref), and a "
                "full inventory of unusable agent runners."
            ),
            (
                "    - Logged Beans 0137-0140 against the root causes: hard-coded default runner, single-response "
                "artifact authoring, absent turn/stage budgets, and an undisclosed sandbox output ceiling. Declared "
                "`maxTokens` explicitly in the host pi config so the cap is visible."
            ),
            (
                "    - Contained the credential leak in CLI command echoes (Bean 0136): token rotated, old value "
                "verified rejected."
            ),
            "",
            "13. **Five-stage flow cycle on every runner-blocked bean (2026-10-23 to 2026-10-26)**:",
            (
                "    - All seven PRs were driven with the `claude-agent` runner (`claude-opus-5-5`) through intent, "
                "plan, execute, the 3-agent review loop and Stage 5 calibration. Every consensus review was posted; "
                "merging stayed with the maintainer."
            ),
            "    - `0135` (#91): a missing branch ref reports `MISSING_REF`, not a false conflict.",
            (
                "    - `0129` + `0133` (holon-coherence #27): mitmweb inspector, plus a monotonic proxy readiness "
                "deadline."
            ),
            "    - `0132` (#90): Stage 4/5 `ACT-*` rows in `executions.jsonl`, plus a calibration success gate.",
            "    - `0137` (#93): the runner is inherited from the harness, with a pre-flight credential probe.",
            (
                "    - `0136` (#96, superseding #92 after a plan-ID collision): canonical redaction module; "
                "credentials off the docker argv through a 0600 env-file; `redact_cli_error`; URL-message fuzz tests."
            ),
            (
                "    - `0134` (#95): `holon flow` dispatches role agents. Empty diffs are refused fail-closed, "
                "unmeasured tests are never counted as a pass, and tests have a `gh` write guard."
            ),
            (
                "    - `0138` + `0139` + `0140` (#94): incremental artefacts, turn/stage budgets handed to every "
                "container, an explicit model envelope, a unified `holon doctor`, a validated `models.json` loader, "
                "and malformed-config and UTF-8 hardening."
            ),
            (
                "    - Every calibration report read its predicted metrics from the wrong `plans.jsonl` row. Each "
                "got an annotation commit (Bean 0146 has the table)."
            ),
            "",
            "14. **First claude-agent `holon flow` runs and the defects they surfaced (2026-10-26)**:",
            (
                "    - The claude runner fix (Bean 0143) was rebased onto `main`, installed as `holon` and baked into "
                "`holon/agent-claude`. Role containers run the image's code, not the host install."
            ),
            (
                "    - Bean 0151 reached a sound plan (EV 19.82). Stage 3 then fabricated two placeholder sub-intents "
                "and halted for a human (Bean 0159). Maintainer decision: no stage before merge may halt for human "
                "review."
            ),
            (
                "    - Bean 0159 ran intent -> plan -> execute -> review -> calibrate (PR #97). On the way it hit "
                "the following:"
            ),
            (
                "      - Bean 0157: the mitmproxy sidecar auto-starts because its image exists, and role containers "
                "cannot reach it."
            ),
            "      - Bean 0158: every run reorders `intents.jsonl`, which also breaks Stage 4 checkout.",
            "      - Bean 0160: CI polling consumes review iterations and is then reported as test failures.",
            '      - Bean 0144: the native review loop posted a fabricated "3-Agent Ensemble" approval to GitHub.',
            "      - Bean 0162: Stage 5 commits a report that fails the `hygiene` check.",
            (
                "    - PR #97 then went through the real harness `pr-review-loop` (3 blind reviewers plus a resolver "
                "per iteration). Nine iterations applied ledger, design, test-coverage and parser fixes. "
                "Decomposed-child aggregation was deferred to Bean 0161."
            ),
            "",
            "15. **Bean 0159 merged via PR #97 after a 33-iteration harness review loop (2026-10-27)**:",
            (
                "    - The intent's entropy budget now reaches the executor. Sub-intents are never invented, and "
                "Stage 3 never halts for a human. Decomposed children run autonomously, with a depth cap and "
                "`{parent}--{n}-{slug}` branches."
            ),
            (
                "    - The review loop found one Important defect late (child branches colliding when created in the "
                "same second). It also moved the suite-rerunning canary out of the unit job, bringing macOS unit back "
                "under 10 minutes, and swept the code with mutation testing until none survived."
            ),
            (
                "    - It did not converge. The diff grew about 3x under review, and Nits never reached zero across "
                "three fresh reviewers. The maintainer merged at iteration 33 with a final COMMENT review. Residual "
                "work is in Beans 0169 (Nits) and 0170 (loop convergence)."
            ),
            "    - Also merged: PR #98 (Bean 0165, restoring PR #88's unpushed review ledger rows).",
            "16. **Faster CI tests via the full flow (Bean 0168 / PR #99, 2026-10-28)**:",
            (
                "    - pytest-xdist, hermetic test git and per-worker template repositories: CI pytest time 2.5x "
                "faster on macOS, 2.0x on ubuntu and 1.6x for Workspace survival. Also closed Bean 0167 (deterministic "
                "turn-supervisor test, hostile `core.hooksPath`)."
            ),
            "17. **Real, fail-closed Stage 4 review (Bean 0144 / PRs #100, #101, #102, 2026-10-28)**:",
            (
                "    - PR-number targets resolve to the head branch and SHA; clone, diff and post failures never "
                "approve. `review_ensemble.py` runs N independent reviewers with strict trailers and unanimity. "
                "Stage 4 is decided only by that ensemble plus mergeable and green CI; the fabricated report is gone."
            ),
            (
                "    - The planner's first attempt split the intent into three dependent sub-intents that could not "
                "build on each other (Bean 0161). It was re-run as three sequential root flows; the split run's "
                "branches stay on `origin` for audit."
            ),
            (
                "18. **Claude permission bypass, prompt rules, entropy/EV docs, fuzz test fix, Stage 3 code salvage, "
                "and CI timing gate (Beans 0143, 0178, 0164, 0154, 0171, 0163 / PRs #104–#109, 2026-10-29)**:"
            ),
            (
                "    - `0143` (#104, `cc4bf1b`): Claude runner passes `--allow-dangerously-skip-permissions "
                "--permission-mode bypassPermissions` as CLI parameters and renders planner placeholders in a single "
                "regex pass; `holon`, `holon-coherence` and all agent images were rebuilt from `main`."
            ),
            (
                "    - `0178` (#105, `c9825b8`): planner and executor prompt templates request repeated test runs "
                "only for performance work under `pytest-xdist` (`-n auto --dist worksteal`) and instruct executors "
                "to commit step by step."
            ),
            (
                "    - `0164` (#106, `956b4fd`): added plain-language entropy and Expected Value documentation in "
                "`docs/metrics-explained.md` linked from `docs/metrics.md`."
            ),
            (
                "    - `0154` (#107, `81a12ee`): fixed the flaky URL delimiter fuzz leak check so random `--env-file` "
                "temporary paths cannot trigger false-positive secret leak failures."
            ),
            (
                "    - `0171` (#108, `c7dfd5e`): Stage 3 failure and budget-breach salvage now commits partial code "
                "changes to the execution branch, emits a redacted format-patch on a refused push (with size caps "
                "and private-key/credential/env-file exclusions), and resumes Stage 3 from `failed_partial_head`."
            ),
            (
                "    - `0163` (`holon-agentic-coder` half, #109, `993b686`): added the CI timing regression gate "
                "across all workflow jobs (rolling-median baseline, per-test offender reporting, hard ceiling, and "
                "auditable override)."
            ),
            ("19. **holon-coherence flows and the architecture research (Beans 0145, 0163, 0184, 0177, 2026-10-29)**:"),
            "    - `0145` (holon-coherence #28, `0547eb4`): pinned holon-coherence to Python 3.13.",
            (
                "    - `0163` (`holon-coherence` half, #30, `6d9dae7`): CI timing regression gate on every "
                "holon-coherence workflow; with #109 this closes Bean 0163."
            ),
            (
                "    - `0184` (holon-coherence #32, `cefebe3`): fixed the residual #30 review findings (blank "
                "`--pr-number`, range-checked `--baseline-count` and `--test-limit`); the claimed `issues: read` "
                "Important was refuted with evidence."
            ),
            (
                "    - `0177` (research, no target code): measured the hot spots in both targets and spawned Beans "
                "0185-0209 with a migration order: lint gates, move-only splits, then parallel decomposition lanes."
            ),
            (
                "20. **Nested sub-intent docs and pure-append ledgers (Beans 0180, 0158, 0210 / PRs #103, #110, #111, "
                "#113, 2026-10-29 to 2026-10-30)**:"
            ),
            (
                "    - `0180` (#103, `e187393`, hand-authored docs): sub-intent branches nest under their deciding "
                "plan. Flow PR #110 (`85ef122`) then documented the five maintainer rulings: merge into the deciding "
                "plan or execution branch, automatic nested PRs, distinct sibling slugs, keep `deciding_branch`, and "
                "review-decided splits under the plan or execution. Flow PR #113 (`0210`, `760ee87`, 5 review "
                "iterations, calibrated) applied those rulings to the remaining five documents (`agent_design.md`, "
                "`architecture.md`, `faq.md`, `safety.md`, `planning_architecture_specification.md`) plus "
                "`planning_and_evaluation.md`."
            ),
            (
                "    - `0158` (#111, `8c9ff4d`): every ledger write is a pure append guarded by a fail-closed prefix "
                "check; conflict detection no longer mistakes the `|||||||` inside an `intents.jsonl` row for a "
                "conflict marker, so flows stop reordering `intents.jsonl` (resolving milestone 14's defect)."
            ),
            (
                "21. **Calibration Prettier Hygiene, Timing-Gate Composite Actions, and Complexity Gate (Beans 0162, "
                "0202, 0209, 0211, 0186 / HAC PRs #112, #114 and Coherence PRs #33, #34, #35, 2026-10-30)**:"
            ),
            (
                "    - `0162` (HAC #112, `d1bdf6b`): Stage 5 calibration report matches repository Prettier formatting "
                "and passes CI hygiene cleanly."
            ),
            (
                "    - `0202` (HAC #114, `6370428`) + `0209` (Coherence #34, `a6912ac`): deduplicated CI timing "
                "gate steps into shared local `.github/actions/ci-timing-gate/action.yml` composite actions "
                "across all workflow jobs."
            ),
            (
                "    - `0211` (Coherence #33, `e475e6d`): updated A/B test documentation recipes for background "
                "proxy startup and combined pass metrics."
            ),
            (
                "    - `0186` (Coherence #35, `f7e4aa6`): enforced Ruff complexity gates (C901, PLR0911-PLR0915) "
                "with an inline `# noqa` baseline and monotonic ratchet pytest, unblocking 0203, 0204, 0207, and 0208."
            ),
            (
                "22. **HAC Complexity Gate, Coherence Command Self-Registration, and Beads Adoption Design "
                "(Beans 0185, 0203, 0156 / HAC PR #115 & Coherence PR #36, 2026-10-30)**:"
            ),
            (
                "    - `0185` (HAC #115, `0e71262`): enforced Ruff complexity gates (C901, PLR0911-PLR0915) on "
                "holon-agentic-coder with frozen 91-entry inline noqa baseline, PGH004 guard against bare `# noqa`, "
                "and swap-rejection test; first calibration report to pass Prettier with no follow-up commit."
            ),
            (
                "    - `0203` (Coherence #36, `3af551d`): refactored command modules to self-register parsers and "
                "handlers, removed `_dispatch.py` `sys.modules` locator in favor of explicit `*_fn` dependency "
                "injection, split `test_cli.py` (327 tests), passed 3/3 ensemble consensus review, "
                "completed Stage 5 calibration, and merged as `72c8d36`."
            ),
            (
                "    - `0156` (research): evaluated beads (`bd`, v1.3.2, Dolt-backed) for target-native issue "
                "tracking. Mapped 213 existing beans, recommended per-target trackers (`hac-` and `hcoh-`), offline "
                "`refs/dolt/data` sync, migrating ~47 open beans, and freezing closed history in the read-only "
                "harness. Spawned Beans 0214-0218 and codified `FLOW_PR_DRIVER.md`."
            ),
            (
                "23. **Stage 4 Role Container Review Dispatch, and Coherence Proxy Package Decomposition "
                "(Beans 0179, 0204 / HAC PR #116 & Coherence PR #37, 2026-10-30)**:"
            ),
            (
                "    - `0179` (HAC #116, `b746408`): routed Stage 4 reviewer turns through the `review-loop` role "
                "container via `_dispatch_role()`, eliminating host-side agent execution while preserving append-only "
                "ledger provenance; passed 3/3 unanimous ensemble consensus review and completed Stage 5 calibration "
                "(`4f119cd`, EV predicted 68.62 / actual 78.04, $\\Delta\\text{EV} = +9.42$)."
            ),
            (
                "    - `0204` (Coherence #37, `9b001c3`): decomposed monolithic `mitm_addon.py` (2,348 lines) into "
                "modular `proxy/` package by concern (`scrubbing.py`, `wire_log.py`, `timing.py`, `metrics.py`, "
                "`routing.py`, `dashboard.py`, `normalise/anthropic.py`, `translation/gemini_openai.py`, and "
                "`addon.py`), preserving backwards-compatibility re-exports; passed 3/3 unanimous ensemble consensus "
                "review and completed Stage 5 calibration."
            ),
            ("24. **HAC CLI Modular Package Decomposition (Bean 0188 / HAC PR #117, 2026-10-30)**:"),
            (
                "    - `0188` (HAC #117, `76fe3ea`): split monolithic `cli.py` (2,185 lines) into a modular `cli/` "
                "package of self-registering command modules under `sandbox_executor/cli/commands/`, unblocking "
                "concurrent CLI maintenance and option refactoring; passed 3/3 unanimous approval and completed "
                "Stage 5 calibration (`1424a26`)."
            ),
            (
                "25. **Hermetic Index Test Guard and Coherence Addon Hook Pipeline Decomposition "
                "(Beans 0150, 0205 / HAC PR #118 & Coherence PR #38, 2026-10-30)**:"
            ),
            (
                "    - `0150` (HAC #118, `e8e9a5d`): eliminated hermeticity leaks where flow tests mutated the real "
                "checkout index (`holon-knowledge/.index/action_index.db`) and guarded `.git` from sandbox mutations; "
                "passed 3/3 unanimous consensus review, completed Stage 5 calibration (`09ba249`), and merged "
                "into `main`."
            ),
            (
                "    - `0205` (Coherence #38, `e3dcc1a`): decomposed `MitmproxyAddon.request` (209 lines, CC 65) and "
                "`response` (187 lines, CC 43) hooks into an ordered step pipeline under `proxy/steps/`; passed 3/3 "
                "unanimous ensemble consensus review, completed Stage 5 calibration (`6a6ec15`), and merged "
                "into `main`."
            ),
            (
                "26. **Mandatory CLI Agent & Model Options and Coherence Dedicated Provider Modules "
                "(Beans 0219, 0206 / HAC PR #119 & Coherence PR #39, 2026-10-31)**:"
            ),
            (
                "    - `0219` (HAC #119, `0bb1615`): made `--agent` and `--model` mandatory CLI options across all "
                "`holon` commands (`flow`, `intent`, `plan`, `execute`, `review`, `calibrate`), eliminating silent "
                "fallback defaults to deprecated or unavailable model tiers; passed 3/3 unanimous ensemble consensus "
                "review, completed Stage 5 calibration (`4f20f01`), and merged into `main`."
            ),
            (
                "    - `0206` (Coherence #39, `ca43eb9`): decomposed wire format handling into dedicated provider "
                "modules under `proxy/providers/` (`base.py`, `anthropic.py`, `openai.py`, `gemini.py`, "
                "`translation.py`) conforming to `ProviderFormat` protocol; passed 3/3 unanimous ensemble consensus "
                "review, completed Stage 5 calibration (`45ff23d`), and merged into `main`."
            ),
            (
                "27. **Platform-Agnostic Review Terminology and Coherence A/B & Metrics Domain Decomposition "
                "(Beans 0220, 0207 / HAC PR #120 & Coherence PR #40, 2026-10-31)**:"
            ),
            (
                "    - `0220` (HAC #120, `922289f`): removed GitHub-specific PR wording across CLI help, engine "
                "logging, consensus report generator, and prompt templates, standardizing on platform-agnostic terms "
                "like 'Review Loop' and 'Change Diff'; passed 3/3 unanimous ensemble consensus review, completed "
                "Stage 5 calibration (`8d5e57d`), and merged into `main`."
            ),
            (
                "    - `0207` (Coherence #40, `d6f1655`): moved A/B evaluation and offline metrics aggregation domain "
                "logic out of CLI command handlers into dedicated domain packages `ab_testing/` and `metrics/`; "
                "passed 3/3 unanimous ensemble consensus review, completed Stage 5 calibration (`ffd6c9e`), and "
                "merged into `main`."
            ),
            (
                "28. **Engine/Skill Review-Loop Standardisation, Engine-Owned Single-Shot Loop, Native Stage 4 "
                "Resolver, 1-Hour Default Turn Timeout, 2-Hour Review Iteration Budget, Post-Review CI Gating, "
                "Resolver CI Repair, Continuous Learning Commits, and Resolver Execution / Fail-Closed Verification "
                "(Beans 0221, 0228, 0229, 0232, 0237, 0235, 0238, 0239, 0240 / HAC PRs #123–#131, "
                "2026-11-05 to 2026-11-06)**:"
            ),
            (
                "    - `0221` axes 1-3 (HAC #123, `43f990a`): unified the consensus review comment template across "
                "the harness `pr-review-loop` skill and `sandbox_executor.review_report`, `review_loop.template.md`, "
                "and `scaffold.py`; passed 3/3 consensus review, calibrated (`c680406`, $\\Delta\\text{EV} = +34.21$), "
                "and merged into `main`."
            ),
            (
                "    - `0228` (HAC #124, `bfecf0f`): made the flow engine the sole owner of the 25-iteration review "
                "budget and checkpointed counter, dispatching single-shot review containers with a separate "
                "`--iteration` label; passed 3/3 consensus review, calibrated (`9be1724`, "
                "$\\Delta\\text{EV} = +17.68$), and merged into `main`."
            ),
            (
                "    - `0229` (HAC #125, `baf3f8c`): implemented the native Stage 4 resolver inside the review loop "
                "(review and resolve per engine iteration, `applied`/`rejected` dispositions in `executions.jsonl`, "
                "3-iteration `no-convergence` guard, single exit posting), closing all five standardisation axes of "
                "`0221`; passed 3/3 consensus review, calibrated (`eb3302f`), and merged into `main`."
            ),
            (
                "    - `0232` (HAC #126, `0f80271`): bumped `DEFAULT_TURN_SECONDS` from 300.0 s to 3600.0 s (1 hour) "
                "in `sandbox_executor.budgets` alongside unit/CLI tests and documentation; traversed all 5 stages "
                "hands-free (1 review iteration, calibrated $\\Delta\\text{EV} = +4.64$) and merged into `main`."
            ),
            (
                "    - `0237` (HAC #127, `6b9264c`): increased `StageBudgets.review_iteration` from 900.0 s (15 min) "
                "to 7200.0 s (120 min) in `sandbox_executor.budgets` alongside unit and flow tests; traversed all "
                "5 stages hands-free (calibrated $\\Delta\\text{EV} = +3.80$) and merged into `main`."
            ),
            (
                "    - `0235` (HAC #128, `f8220eb`): made Stage 4 GitHub CI a post-review gate in "
                "`sandbox_executor.flow`, launching the reviewer ensemble immediately while CI runs in parallel and "
                "bypassing pending CI waits when reviewers object; traversed all 5 stages (calibrated "
                "$\\Delta\\text{EV} = +10.93$) and merged into `main`."
            ),
            (
                "    - `0238` (HAC #129, `ecec262`): synthesised first-class `FindingRow` for `FIND-CI` in "
                "`sandbox_executor.flow` and updated `entrypoint/review_loop.py` so the resolver automatically repairs "
                "CI and test failures even when code reviewers approve; traversed all 5 stages (calibrated "
                "$\\Delta\\text{EV} = +11.52$) and merged into `main`."
            ),
            (
                "    - `0239` (HAC #130, `1619cec`): added `_commit_stage5_promoted_artifacts()` in `flow.py` to "
                "stage and commit promoted `holon-knowledge/kb/` and `holon-knowledge/wisdom/` files to `/calibrated` "
                "and fast-forward into the PR head branch and diff; traversed all 5 stages hands-free and merged "
                "into `main`."
            ),
            (
                "    - `0240` (HAC #131, `3c752e6`): constructed runner CLI command list via `runner.build_command()` "
                "before invoking `run_turn(cmd, cwd=repo_dir)` in `entrypoint/review_loop.py` to fix `TypeError`, and "
                "enforced fail-closed verification defaults (`lint_passed`/`tests_passed` default to `False`); "
                "traversed all 5 stages and merged into `main`."
            ),
            (
                "29. **Immutable KB/WB Facts, Worktree Auto-Provisioning & Validation, Persistent Review Sandbox, "
                "Prompt Complexity Rules, Executor GitRepository Adapter, Globally Unique Stage IDs, `flow/` Package "
                "Split, Pinned Container `uv`, Dual-EV Calibration, Main Worktree Guard, Resolver Commit "
                "Normalisation, All-Branch CI, and Plan-Owned Decomposition (Beans 0242, 0244, 0245, 0247–0251, "
                "0236, 0243, 0201, 0241, 0195, 0233, 0149, 0254, 0258, 0257, 0259, 0256, 0266, 0268, 0161 / "
                "HAC PRs #132–#151, #153, #154, #158, 2026-11-06 to 2026-11-10)**:"
            ),
            (
                "    - `0242` (#132, `d932d48`), `0244` (#133, `2a56a89`), `0245` (#134, `4113f0d`), `0247` (#135), "
                "`0248` (#136), `0249` (#137), `0251` (#138), `0236` (#139, `d0c1334`, single consensus review post), "
                "`0250` (#140, `be6cd7b`, reviewer failure observability), and `0243` (#141, `e130dfb`, zero harness "
                "bean references) all traversed the 5-stage flow and merged."
            ),
            (
                "    - `0201` (#142, `e10b4d4`): planner, executor, and reviewer prompts carry the module-layout, "
                "complexity, and >1,000-line growth rules (calibrated $\\Delta\\text{EV} = +6.27$)."
            ),
            (
                "    - `0241` (#143, `a17a854`): persisted the Stage 4 review loop sandbox volume across iterations "
                "with incremental git sync (calibrated $\\Delta\\text{EV} = +18.97$)."
            ),
            (
                "    - `0195` (#144, `cc2ed3e`): added `GitRepository` adapter in `sandbox_executor.git` and routed "
                "executor git calls through it (calibrated $\\Delta\\text{EV} = +7.10$)."
            ),
            (
                "    - `0233` (#145, `8b1e668`): fail-fast validation that `--target-worktree` and checkpoint "
                "`repo_dir` are attached git worktrees (calibrated $\\Delta\\text{EV} = +14.85$)."
            ),
            (
                "    - `0149` (#146, `4682449`): globally unique `P-...` and `E-...` stage IDs with 8-character hex "
                "disambiguators and ledger duplicate validation across concurrent intents."
            ),
            (
                "    - `0254` (#147, `7258f61`): decomposed monolithic `flow.py` (6,159 lines) into the modular "
                "`sandbox_executor/flow/` package (`stages/`, `git_refs.py`, `ci_gate.py`, `review_consensus.py`, "
                "etc.) with AST-verified move-only parity and per-module size ratchets."
            ),
            (
                "    - `0258` (#148, `b6cd9a6`): pinned `uv` 0.13.7 in `holon-base` with a build-time smoke check and "
                "made resolver check/container failures fail-closed in Stage 4."
            ),
            (
                "    - `0257` (#149, `c554e8e`): implemented Dual Actual EV in Stage 5 calibration "
                "(`calibration_ev.py` and `calibration.py`), reporting both Intrinsic/Clean EV (`ev_clean`, without "
                "bugs) and Observed EV (`ev_with_bugs`, with bugs included) plus `bug_ev_drag` (predicted EV `+6.24`, "
                "Clean EV `+6.07` / $\\Delta\\text{EV}_{\\text{clean}} = -0.17$, Observed EV `-2.43`, Bug EV Drag "
                "`+8.50`)."
            ),
            (
                "    - `0259` (#150, `8000794`): `holon flow` now runs a `main` target in a dedicated `flow-<slug>` "
                "worktree off `origin/main`, never mutating the `main` worktree, and refuses default-branch "
                "checkpoints and direct stage commands."
            ),
            (
                "    - `0256` (#151, `61796c6`): resolver captures `pre_resolver_head` before `_run_resolver_agent` "
                "and soft-resets any local agent commits in `_commit_and_push_resolution`, ensuring pre-push "
                "verification, canonical review trailers, and git push are never skipped "
                "(calibrated $\\Delta\\text{EV} = +0.53$)."
            ),
            (
                "    - `0266` (#153, `fe3b540`): the six CI workflows run on pull requests into any base branch so "
                "stacked sub-intent PRs are tested (calibrated $\\Delta\\text{EV} = +20.60$)."
            ),
            ("    - `0268` (#154, `b63fce7`): carried unmerged calibration reports into `main` in one pull request."),
            (
                "    - `0161` (#158, `14886b8`): the plan decides decomposition; children nest under and merge into "
                "the plan branch; combined integration PR reaches `main`."
            ),
            (
                "30. **Sandbox Escape Revert, Honest Review Consensus, and Host-Worktree Mount Re-land (Beans 0272, "
                "0273, 0262 / HAC PRs #159–#162, 2026-11-10 to 2026-11-11)**:"
            ),
            (
                "    - `0262` (#159, `80b844d`) merged on a false `APPROVED (3/3)` with an open critical sandbox "
                "escape; `0272` (#160, `2faa325`) reverted it."
            ),
            (
                "    - `0273` (#161, `7837fa4`): consensus comes only from the reviewers' returned verdicts; "
                "adjudication suppression applies to nits only; the posted review is exact; evidence is required to "
                "reject an important or higher finding."
            ),
            (
                "    - `0262` (#162, `dd00fb9`): host worktree mounted into the role containers with the git "
                "directory's `worktrees/` area read-only; unanimous 3/3 with zero findings at iteration 16, CI "
                "11/11 green."
            ),
            (
                "31. **Stage 5 Calibration Freshness, Harness Test Isolation, Lockfile and Sleep Fixes, and Measured "
                "Test Pass Rate (Beans 0267, 0290, 0292, 0293, 0294, 0295 / HAC PRs #186–#190, 2026-11-12 to "
                "2026-11-13)**:"
            ),
            (
                "    - `0290` (harness, no PR): the flow wrapper exports the Claude auth route from "
                "`CLAUDE_CODE_OAUTH_TOKEN` or the secrets file, or stops before dispatch naming what is missing."
            ),
            (
                "    - `0292` (#186, `9f2187e`): a red CI check, including a timing gate, blocks the approval and the "
                "merge-ready report on the final head."
            ),
            (
                "    - `0293` (#188, `54bfd55`): tests that patch `time.sleep` patch only the module under test, so "
                "unrelated subprocesses cannot trip them."
            ),
            (
                "    - `0294` (#190, `efff3ed`): the committed `uv.lock` matches the project and container Python, so "
                "flows stop producing lockfile churn. Its calibration report predates the conflict merge, and Stage 5 "
                "stopped on the stale calibrated branch; Bean 0296 fixed it (PR #193)."
            ),
            ("    - `0295` (#189, `bde4934`): a rejected resolver diff is saved as a patch the host can read."),
            (
                "    - `0267` (#187, `7a8f086`): Stage 3 records a measured `test_pass_rate`, and the review loop "
                "measures tests itself when no CI registers. A hand edit outside the flow (`deb5026`, explicit "
                "maintainer instruction) fixed the CI wait tests' head lookup."
            ),
            (
                "32. **Stage 5 Calibration Rebuild and Review-Loop Posting Honesty (Beans 0260, 0296 / HAC PRs #192–#193, "
                "2026-11-13 to 2026-11-14)**:"
            ),
            (
                "    - `0260` (#192, `3b6c3d7`): the review consensus is posted to the PR only on unanimous approval or "
                "when the review iteration budget is exhausted; halted iterations (failed verdict, infrastructure error, "
                "reviewer crash or timeout) stay local in the ledgers. Final review iteration APPROVED 3/3 at head "
                "`edb49fd` (predicted EV 50.68, actual 61.89, calibration delta +11.21)."
            ),
            (
                "    - `0296` (#193, `291727e`, merged 2026-11-14): Stage 5 deletes and rebuilds a stale `calibrated` "
                "branch that holds only the flow's own calibration commits, logs what it replaced, and still fails "
                "loudly on foreign commits; the final report names the head the calibration report covers. The report "
                "covers `cb55140`, not the merged head `0e183d8`, which is why Bean 0297 was logged."
            ),
            (
                "    - New: `0297` (todo, P1): Stage 5 reruns automatically when the pull request head moves after "
                "calibration, so the merged head carries a current report."
            ),
            "",
            "---",
            "",
            "## Active Beans Triage and Prioritisation Matrix",
            "",
            "| Priority | Status | Impact | Sizing | Bean # | Title | Domain | Dependencies / Notes |",
            "| :--- | :--- | :---: | :---: | :--- | :--- | :--- | :--- |",
        ]
    )

    for b in active_beans:
        row = (
            f"| {b['priority_display']} | {b['status']} | {b['impact']} | {b['sizing']} "
            f"| {b['bean_num']} | {b['title']} | {b['domain']} | {b['notes']} |"
        )
        lines.append(row)

    lines.extend(
        [
            "",
            "---",
            "",
            "## Recommended Next Execution Sequence",
            "",
        ]
    )
    if not active_beans:
        total = stats.get("total_tracked", 0)
        lines.extend(
            [
                (
                    f"All tracked beans in the active backlog (Beans 0001 – {total:04d}) have been completed "
                    "across all managed repositories:"
                ),
                "",
                (
                    "- `holon-agentic-coder` and `holon-coherence`: the most recent flow pull requests have traversed "
                    "all 5 Holon flow stages (Stage 4 consensus APPROVED, Stage 5 calibration report included in the "
                    "PR diff); see the Key Milestones section above for the current PR numbers."
                ),
                (
                    f"- `holon-agentic-coder-ref-metadata`: All beans up to Bean {total:04d} are "
                    "finalised and marked completed."
                ),
                "",
                (
                    "The ecosystem backlog is empty and any open pull request awaits manual human maintainer review "
                    "and merge; agents never merge (AGENTS.md, PR Merging — Human-Only)."
                ),
                "",
            ]
        )
    else:
        lines.extend(NEXT_EXECUTION_SEQUENCE)
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Triage and prioritise beans across the Holon ecosystem.")
    parser.add_argument("--beans-dir", default=".beans", help="Path to .beans/ directory")
    parser.add_argument("--output", help="Explicit output file path")
    parser.add_argument("--dry-run", action="store_true", help="Print output to stdout without writing to disk")
    args = parser.parse_args()

    active_beans, stats = scan_beans(args.beans_dir)

    output_path = args.output or os.path.join(args.beans_dir, "bean-triage-prioritisation.md")
    previous_checkpoint = read_previous_checkpoint(output_path)
    doc = generate_triage_document(active_beans, stats, previous_checkpoint=previous_checkpoint)

    if args.dry_run:
        print(doc)
        return 0

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(doc)

    if previous_checkpoint:
        print(f"Previous triage checkpoint: {previous_checkpoint}")
    print(f"✅ Generated triage document with {len(active_beans)} active beans at: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
