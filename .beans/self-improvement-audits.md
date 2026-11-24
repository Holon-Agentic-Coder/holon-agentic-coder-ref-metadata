# Self-Improvement Audit Log

This log is written by the self-improvement audit described in `.agents/self-improvement-audit.md`; the newest entry is
first.

## Entries

### 2026-11-24T12:59:00Z — Fifth-Merge Audit (Antigravity verification pass)

- **Trigger:** fifth merge since `2026-11-24T11:05:00Z` (`holon-coherence#53`, `holon-agentic-coder#269`,
  `holon-agentic-coder#270`, `holon-coherence#54`, `holon-coherence#55`; plus `holon-agentic-coder#274` merged at
  `12:45:46Z`, right at audit launch `12:47:33Z`). Complements the concurrent `12:58:00Z` pass (`0422`–`0425`).
- **Last merged pull requests at audit time:**
  - `holon-agentic-coder`: `#274` (`preflight-retry`, merged `2026-11-24T12:45:46Z`; `#270` at `11:31:45Z` was the 5th
    merge in the `11:05Z–12:45Z` cadence)
  - `holon-coherence`: `#55` (`coherence-module-line-budget-all`, merged `2026-11-24T12:44:47Z`)
- **Beans created or extended:**
  - Created: `0426` (slug truncation, `bean_progress` attribution & subagent intent rewrites), `0427` (`gh` stderr hints
    corrupting `pr_url` in posted consensus reviews), `0428` (2-dot vs 3-dot PR-own diff in `ci_final_head` & overlap
    inspection), `0429` (`.beans/` header ID & title uniqueness check in `pre_commit_check.py`).
  - Extended: `0404` (`hac#273` `unit (macos-latest)` `634 s > 600 s` ceiling failure at `12:17:52Z`), `0414` (`hac#273`
    `21.3 min` Stage 3 discarded at `11:07:42Z` over 18 out-of-set files).

#### 1. Per-Step Timing Table (`2026-11-24T11:05:00Z` to `12:47:33Z`)

Measured across `todo/flow-*.log` (`ci-skip-bookkeeping-only-pushes`, `ledger-temp-worktree-cleanup`,
`unit-suite-slowest-tests-speedup`), worktree checkpoints (`0376` child 4 `route-stage-4-and-stage-5`, `0399`, `0265`),
and GitHub PR/CI/commit timestamps (`coh#53`, `coh#54`, `coh#55`, `hac#269`, `hac#270`, `hac#274`):

| Step                                                                 | Count | Median (min) | Longest (min) | Longest in                          |
| :------------------------------------------------------------------- | ----: | -----------: | ------------: | :---------------------------------- |
| Pre-flight (credential probe, image check, worktree creation)        |     - | not measured |  not measured | missing wrapper timestamps (`0412`) |
| Stage 1: intent agent turn (logged/checkpoint)                       |     4 |          0.1 |           0.2 | `split-cli-init-modules` (`0265`)   |
| Stage 2: planner agent turn (logged/checkpoint)                      |     3 |          4.6 |           5.3 | `split-cli-init-modules` (`0265`)   |
| Stage 3: admission check (admitted / refused)                        |     4 |          0.0 |           0.1 | `route-stage-4-and-stage-5` (`273`) |
| Wait: stage 3 overlap refusal -> retry / still waiting               |     2 |         40.8 |          65.3 | `ci-wait-fast-poll-and-early-fail`  |
| Stage 3: executor agent turn (incl. tests)                           |     3 |         24.9 |         125.3 | `unit-suite-slowest-tests-speedup`  |
| Stage 3: re-plan after touch-set breach                              |     1 |          4.7 |           4.7 | `route-stage-4-and-stage-5` (`273`) |
| Each push & conflict probe/merge of target                           |     - | not measured |  not measured | folded into turns (`0412`)          |
| Stage 4: empty-diff guard + PR create/edit                           |     5 |          0.1 |           0.1 | `route-stage-4-and-stage-5` (`273`) |
| Stage 4: reviewer ensemble turn (3 reviewers; per-reviewer unlogged) |     7 |         25.5 |          27.9 | `ci-skip-bookkeeping-only-pushes`   |
| Stage 4: resolver turn (incl. push)                                  |     5 |         14.0 |          18.8 | `route-stage-4-and-stage-5` (`273`) |
| Stage 4: ledger commit                                               |    11 |          0.0 |           4.1 | `ci-skip-bookkeeping-only-pushes`   |
| Stage 4: review iteration (reviewers + CI/local tests)               |     9 |         13.2 |          27.9 | `ci-skip-bookkeeping-only-pushes`   |
| CI registration wait                                                 |     3 |          0.0 |           0.3 | `ledger-temp-worktree-cleanup`      |
| CI wait (tracked checks to settled)                                  |     1 |          9.9 |           9.9 | `ledger-temp-worktree-cleanup`      |
| Stage 5: calibration work + promotion + reconciliation               |     2 |          0.3 |           0.3 | `ledger-temp-worktree-cleanup`      |
| Stage 5: final-head check after CI settled                           |     1 |          0.0 |           0.0 | `ledger-temp-worktree-cleanup`      |
| Wait: PR ready (CI green + calibrated) -> maintainer merge           |     6 |         10.9 |          25.2 | `holon-coherence#55`                |
| Idle: interrupted / review halt -> resume                            |     4 |          0.7 |           2.5 | `ledger-temp-worktree-cleanup`      |
| GitHub: PR open -> merged (5 cadence merges + `hac#274`)             |     6 |         50.9 |         357.4 | `holon-agentic-coder#269`           |

- **Missing timing (5/9 PRs unlogged in `todo/flow-*.log`):** `coh#53`, `coh#54`, `coh#55`, `hac#269`, and `hac#274`
  left no `todo/flow-*.log`; `0376` child 4, `0399`, and `0265` recorded logs only inside checkpoints (`0412`, `0423`).

#### 2. Churn Counts (`11:05:00Z` to `12:47:33Z`)

- **CI pipeline runs:**
  - Across the **5 cadence merges** (`coh#53`, `coh#54`, `coh#55`, `hac#269`, `hac#270`): `35` pipeline heads + `2` job
    re-runs = `37` runs total, of which **25 (68%) were churn** (`18` bookkeeping-only, `5` `main`-merge, `2` re-runs),
    and `5` failed (`hac#270` timing gate at `11:36:14Z`; `hac#269` `Workspace survival` `609 s > 600 s`).
  - Across **all 9 PRs in the window** (adding `hac#274`, `#272`, `#273`, `#275`): `49` heads + `2` re-runs = `51` runs,
    of which **31 (61%) were churn** (`23` bookkeeping-only, `6` `main`-merge, `2` re-runs), with `7` failures (all
    timing-gate ceilings: `hac#273` `unit (macos-latest)` `634 s > 600 s` at `12:17:52Z`).
- **Review & Stage 3 churn:**
  - `hac#272` (`0403`): iter 3 spent `25.6 min` on a `main`-merged head, hit 2 `APPROVED` + 1 documentation nit
    (`0/0/1`), and started full iter 4 (`12:47:53Z`); halted on `DIRTY` at `12:13:51Z`.
  - `hac#273` (`0376` child 4): Stage 3 lost `21.3 min` at `11:07:42Z` on 18 out-of-set files + `4.7 min` re-plan.
  - `hac#270` (`0387`): `9.9 min` Stage 5 calibration CI wait (`10.7 min / 10 min`) pushed past `main` merge, triggered
    a second Stage 5 CI wait (`8.1 min`), hit the `360 s > 344 s` timing gate (`0419`), withdrew consensus
    (`11:37:55Z`), and failed Stage 4 after PR #270 had already merged (`0420`).

#### 3. Ranked Suggestions (new beans `0426`–`0429` + extended `0404`, `0414`)

1. **Bean `0426` (high, Harness):** Fix `run_holon_flow.py` uncommitted slug-truncation/hardcoded `0380` patch, fix
   `bean_progress.py` truncated-slug attribution (`coh#55` showed `Bean # = —`), and forbid `flash_lite` subagents from
   rewriting `todo/intent-*.json` (`0393` overwritten, stale worktree left behind).
2. **Bean `0427` (high, Flow / Stage 4):** Strip `gh` CLI `stderr` hints (`gh event listen ...`) from `pr_url` in
   `adapter.py`/`loop.py:723` so posted consensus review Markdown links (`hac#273`, `hac#274`, `coh#55`) are not
   corrupted.
3. **Bean `0428` (medium, Flow / Diff Semantics):** Replace 2-dot `{approved}..{head}` in `ci_final_head.py:213` with
   PR-own 3-dot diff so merged-head timing-gate retries stay eligible across `main` merges, and standardize touch-set
   inspection on 3-dot `origin/main...head` (`407` vs `217` files on `#273`; `33` vs `19` on `#275`).
4. **Bean `0429` (medium, Harness / `.beans/`):** Validate `.beans/` header ID vs filename ID and title uniqueness in
   `pre_commit_check.py` (preventing silent overwrites like `907c0255` on `0417`).
5. **Extended `0404` & `0414`:** Recorded `hac#273` `unit (macos-latest)` `634 s > 600 s` failure (`12:17:52Z`) in
   `0404` and `hac#273` `21.3 min` Stage 3 touch-set discard (`11:07:42Z`) in `0414`.

### 2026-11-24T12:58:00Z: Fifth-Merge Audit

- **Trigger:** fifth merge (period `2026-11-24T11:05:00Z` to `12:58:00Z`; merges `hac#269`, `#270`, `#274`, `coh#53`,
  `#54`, `#55`). Scripts and outputs: `todo/self-improvement-audit-2026-11-24b/`.
- **Last merged pull requests at audit time:**
  - `holon-agentic-coder`: `#274` (`preflight-retry`, merged `2026-11-24T12:45:46Z`)
  - `holon-coherence`: `#55` (`coherence-module-line-budget-all`, merged `2026-11-24T12:44:47Z`)
- **Beans created or extended:**
  - Created: `0422` (sticky `--allow-overlap`), `0423` (two sessions, no shared flow registry or cap), `0424` (transient
    DNS or Docker failure ends the review stage), `0425` (Fable review iterations three times as long).
  - Extended: `0376` (pre-iteration DIRTY probe ignored; PR #273 is the hub), `0371` (ledger-only conflicts on PRs #272
    and #275), `0419` (7 of 7 failures were timing gates; forecast after PR #275), `0412` (unlogged Antigravity flows,
    checkpoint elapsed mismatch, executor turn not split), `0407` (full re-review for one nit).

#### Period timing (summary; full table in `timing-period.md`)

| Step                                       | Count | Median (min) | Longest (min) | Longest in               |
| :----------------------------------------- | ----: | -----------: | ------------: | :----------------------- |
| Stage 2 plan                               |     4 |          4.0 |           5.3 | `split-cli-init-modules` |
| Stage 3 executor turn                      |     3 |         25.2 |         125.4 | `hac#275`                |
| Stage 3 overlap wait (still waiting)       |     2 |            - |            73 | Bean 0399 on `#273`      |
| Stage 4 reviewer ensemble (`fable-5-2`)    |     3 |         26.1 |          27.9 | `hac#272`                |
| Stage 4 resolver turn                      |     3 |          4.1 |          18.5 | `hac#272`                |
| Stage 4 review on a conflicting head       |     2 |            - |          26.1 | `hac#272` iteration 2    |
| Stage 4 iteration lost to DNS / Docker 125 |     2 |            - |          12.5 | `hac#275` iteration 1    |
| Stage 5 CI wait / merged-head CI wait      |     2 |          8.9 |           9.9 | `hac#270`                |
| PR ready to maintainer merge               |     1 |         34.0 |          34.0 | `hac#274`                |
| Pre-flight, pushes, Antigravity flow steps |     - | not measured |  not measured | Beans 0412, 0423         |

#### Churn

- Pipelines: 49 heads plus 2 reruns on 9 PRs; 31 (61%) on bookkeeping-only or main-merge heads. All 7 failed runs since
  09:58Z were timing gates with every test green; main had none in 24 runs.
- Reviews: PR #272 has run 5 iterations, of which 3 were churn (one on a conflicting head, one full re-review for one
  nit, one lost to the DNS outage); PR #275 lost its first iteration to the outage and started its second on a
  conflicting head.

#### Ranked suggestions

1. Merge PR #273 first (Bean `0376`): it removes the review-on-a-conflicting-head churn and unblocks Beans 0399, 0197
   and 0216.
2. Bean `0419` (extended): timing gates are now the only cause of pipeline failure, on both runners.
3. Bean `0422` (new): an `--allow-overlap` override is sticky and inherited by sub-intents.
4. Bean `0423` (new): one flow registry and cap across agent sessions; every runtime logs.
5. Bean `0371` (extended): ledger-only conflicts knocked PR #272 out three times and PR #275 within six minutes.
6. Bean `0424` (new): retry transient DNS or Docker failures in place.
7. Bean `0425` (new, maintainer decision): Fable review iterations take a median 18.4 min against 5.9 on Opus.
8. Beans `0407` and `0412` (extended).

### 2026-11-24T11:05:00Z — Fifth-Merge Audit

- **Trigger:** fifth merge (first recorded audit entry; period `2026-11-21T00:00:00Z` to `2026-11-24T11:05:00Z`,
  consolidating the `2026-11-24T10:55Z` measurement pass in `todo/self-improvement-audit-2026-11-24/` with PRs and flow
  runs through `11:05Z`).
- **Last merged pull requests at audit time:**
  - `holon-agentic-coder`: `#271` (`claude-token-os-keychain-only`, merged `2026-11-24T09:55:35Z`)
  - `holon-coherence`: `#52` (`coherence-scripts-self-doc`, merged `2026-11-24T10:56:55Z`)
- **Beans created or extended:**
  - Created: `0407`, `0408`, `0409`, `0410`, `0411`, `0412`, `0413`, `0414` (from the `10:55Z` pass), `0415`, `0416`,
    `0417`, `0418` (new findings at `11:05Z`).
  - Extended: `0394`, `0395`, `0403`, `0404` (added `Workspace survival` `--ceiling 600` failure at `609 s` on
    `hac#269`).

#### 1. Per-Step Timing Table (140 runs across 35 flow logs + GitHub/checkpoint records)

| Step                                                                  | Count | Median (min) | Longest (min) | Longest in                                 |
| :-------------------------------------------------------------------- | ----: | -----------: | ------------: | :----------------------------------------- |
| Pre-flight (credential probe, image check, worktree creation)         |     - | not measured |  not measured | missing wrapper timestamps (Bean 0412)     |
| Stage 1: intent agent turn                                            |    29 |          0.1 |           0.2 | `derive-kb-index`                          |
| Stage 2: planner agent turn                                           |    34 |          4.0 |          34.3 | `unit-suite-slowest-tests-speedup`         |
| Stage 3: admission check                                              |    49 |          0.1 |           0.2 | `stale-calibration-warning-fix`            |
| Stage 3: admission refusal to exit (waiting on another flow)          |    50 |          0.0 |           0.0 | `split-calibration-package`                |
| Wait: stage 3 overlap refusal $\rightarrow$ relaunch                  |    48 |          1.1 |        1053.0 | `execute-stage-object`                     |
| Stage 3: refresh plan onto `main` after admission wait                |     8 |          0.0 |           0.0 | `unlimited-stage-budgets`                  |
| Stage 3: executor agent turn (incl. tests)                            |    39 |         10.5 |         102.5 | `name-and-seed-redaction-tests`            |
| Stage 3: re-plan after touch-set breach                               |     6 | not measured |  not measured | `approval-survives-main-merge` (+5 others) |
| Each push (execution branch, resolver, ledger rows, calibration)      |     - | not measured |  not measured | folded into surrounding turn (Bean 0412)   |
| Each conflict probe and merge of target                               |     - | not measured |  not measured | start time not logged (Bean 0412)          |
| Stage 4: empty-diff guard + PR create/edit                            |    61 |          0.1 |           0.2 | `executor-execution-run`                   |
| Stage 4: reviewer ensemble turn (3 reviewers; per-reviewer unlogged)  |   121 |          6.6 |          26.5 | `ledger-temp-worktree-cleanup`             |
| Stage 4: local test run after reviewers                               |    32 |          1.3 |           2.6 | `resolve-conflicts-in-flow`                |
| Stage 4: resolver turn (incl. push)                                   |    83 |          3.0 |          22.0 | `review-approved-and-fresh-tests`          |
| Stage 4: ledger commit                                                |   148 |          0.1 |           8.5 | `no-fallback-calibration-report`           |
| Stage 4: review iteration (reviewers + local tests/CI evidence)       |   125 |          6.7 |          26.6 | `ledger-temp-worktree-cleanup`             |
| CI registration wait                                                  |    26 |          0.0 |           0.3 | `github-issues-replace-beads`              |
| CI wait (tracked checks to settled)                                   |    35 |          7.9 |          18.0 | `ledger-temp-worktree-cleanup`             |
| Stage 5: calibration work + promotion                                 |    37 |          0.2 |           0.4 | `github-issues-replace-beads`              |
| Stage 5: reconciliation                                               |     8 |          0.2 |           0.3 | `flow-no-auto-sidecar-spawn-v2`            |
| Stage 5: final-head check after CI settled                            |    36 |          0.0 |           3.8 | `github-issues-replace-beads`              |
| Wait: PR ready at merge boundary $\rightarrow$ maintainer merge       |    10 |          1.9 |          26.8 | `claude-token-os-keychain-only`            |
| Idle: interrupted / stopped run $\rightarrow$ resume (all stop kinds) |    47 |          1.1 |         135.3 | `intent-plan-stage-decomposition`          |
| GitHub: PR open $\rightarrow$ merged (both repos)                     |    48 |          ~96 |        2428.6 | `hac#230`                                  |

Stage totals across the measured logs:

| Stage     | Total (h) | Working (h) | Waiting on CI (h) | Waiting on another flow (h) | Waiting on human (h) | Idle (h) |
| :-------- | --------: | ----------: | ----------------: | --------------------------: | -------------------: | -------: |
| intent    |      0.11 |        0.07 |              0.00 |                        0.00 |                 0.00 |     0.00 |
| plan      |      3.74 |        3.56 |              0.00 |                        0.00 |                 0.00 |     0.00 |
| execute   |     10.60 |        9.72 |              0.00 |                       39.81 |                 0.00 |     1.63 |
| review    |     20.90 |       20.87 |              0.44 |                        0.00 |                 0.00 |     9.20 |
| calibrate |      5.81 |        0.16 |              5.10 |                        0.00 |                 0.75 |     0.00 |

#### 2. Churn Counts

- **CI pipeline runs across 48 merged PRs (`hac` 39 + `coh` #44–#52):** 426 pipeline head runs total, of which **305
  (72%) were churn** (233 bookkeeping-only heads, 57 `main`-merge heads, 15 job re-runs); 20 pipeline runs failed on
  churn heads. Recent spotlights: `hac#263` (16/18 churn, 3 failed), `hac#267` (16/17 churn, 2 failed), `hac#268` (11/12
  churn, 5 failed), `coh#44`–`#52` (24/33 churn across 9 PRs, 1 failed).
- **Review iterations across 26 logged `holon-agentic-coder` flows:** 126 full review iterations (934 min; median 6.7
  min, longest 26.6 min on `hac#270`), of which 26 were first iterations, 52 fixed reviewer findings (406 min), and **48
  (38%, 339 min) were churn**: 17 `main`-merge/conflict iterations (127 min), 18 after a resolver pass pushed no new
  head (160 min together with 8 stop/resume churn iterations), 2 after approval withdrawal on CI failure/unknown CI (30
  min), and 3 on infrastructure failures (22 min). Additionally, 7 iterations ended with all 3 reviewers
  `APPROVED (0/0/0)` while the container verdict reported `CHANGES_REQUESTED` due to `DIRTY`/conflicting PR state
  (including `hac#269` iteration 10 at `10:28:57Z`).
- **Additional churn observed since `10:55Z`:**
  - `flow-ci-skip-bookkeeping-only-pushes` (`0403`): 30.5 min Stage 3 lost to container `exit code -9` (OOM under
    `-n auto`) at `10:48:42Z`; resumed at `10:54:28Z` and passed in `5.7 min`.
  - `hac#269` (`0226` / `flow-e2e-test-teardown`): `Workspace survival (ubuntu-latest)` failed at `10:59:27Z`
    (`609 s > 600 s` ceiling, 0% per-test regression).
  - `coh#52` (`0153`): 4 pipeline heads (3 bookkeeping-only, 1 code), 2 review iterations, merged `10:56:55Z` (no flow
    log kept).

#### 3. Ranked Suggestions

1. **Bean `0407` (critical, Flow / Stage 4):** Stop re-running the full review ensemble when nothing reviewable changed;
   decouple consensus on diff D from CI on head H and use scoped delta re-reviews (saves ~339 min / 48 churn review
   iterations).
2. **Bean `0403` (high, Pipeline — extended):** Skip full CI on bookkeeping-only pushes (`plans/`, `executions/`,
   `holon-knowledge/`), avoiding 233/426 (55%) of pipeline runs (~8 min each).
3. **Bean `0408` (high, Flow / Pipeline):** Run CI's hygiene, ruff, Prettier, `jq`, and file-growth checks locally
   before any push leaves the machine (prevents 17 `hygiene` CI failures + 10 lint + 25 file-growth findings).
4. **Bean `0404` (high, Pipeline — extended):** Fix `--ceiling 600` timing-gate failures on runner variance across both
   `unit (macos-latest)` (`hac#267`, `#270`, `#271`) and `Workspace survival (ubuntu-latest)` (`hac#269` at `609 s` with
   0% per-test regression).
5. **Bean `0415` (high, Flow / Stage 3 — new):** Cap pytest workers inside role containers instead of unbounded
   `-n auto` to stop `exit code -9` OOM kills under concurrent 4-flow runs (`flow-ci-skip-bookkeeping-only-pushes`, 30.5
   min lost).
6. **Bean `0410` (high, Architecture):** Replace hand-edited conflict magnets (`apps/sandbox-executor/README.md`,
   `docs/environment_variables.md`, shared `flow_module_budgets.json`, `flow/__init__.py` re-exports) to cut the 39.8 h
   of Stage 3 overlap waits.
7. **Bean `0409` (high, Flow / Stage 4):** Do not re-run a full review when a resolver pushes no new head (18 churn
   iterations) and adjudicate rejected findings once.
8. **Bean `0417` (high, Harness — new):** Make `run_holon_flow.py`'s `verify_pr_and_calibration` fail non-zero on
   missing PR/calibration/conflicting PR and write `.subagent/flow_<slug>_state.json` deterministically instead of
   trusting `flash_lite` prose.
9. **Bean `0416` (high, Harness — new):** Scan only the tail and last reset match in `parse_limit_reset`, parse seconds
   (`s`) in `limit_reset.py`, and use OS-keychain lookup + `antigravity-agent` relaunch in `watch_limits.py`.
10. **Bean `0411` (high, Harness):** Remove harness instruction contradictions (runner switching, 8 duplicated model
    ladders, default runner, 3 conflicting file-size limits).
11. **Bean `0413` (medium, Coding Standards):** Feed recurring reviewer findings (1,000-line growth, allow-lists vs
    deny-lists, helper reuse, generated docs, PR evidence) to planner/executor upfront (~120 of 249 findings).
12. **Bean `0414` (medium, Flow / Stage 3):** Enforce the plan's touch set during the executor turn instead of
    discarding finished executions after the turn (~102 min discarded across 6 flows).
13. **Bean `0418` (medium, Flow / Stage 2–3 — new):** Preserve passing execution branches on companion touch-set
    expansion and keep decomposed parent flows resumable per sub-intent (`flow-claude-code-mode-default-on`,
    `flow-resolve-conflicts-in-flow`).
14. **Bean `0412` (medium, Flow / Harness):** Record start/end timestamps for pre-flight, pushes, conflict
    probes/merges, individual reviewers, overlap waits, and ensure every flow (including `holon-coherence`) writes
    `todo/flow-<slug>.log`.

#### 4. Examined and Found in Order

- `holon-coherence` PRs `#44`–`#52` all reached 3/3 `APPROVED` in 1–3 review iterations with clean calibration reports
  in the PR diff and 0 CI failures on `#44`–`#46`, `#48`–`#52` (only 1 CI failure on `#47`), showing that small,
  single-package slices avoid the multi-hour churn seen on large `holon-agentic-coder` PRs.
- Bean `0406` (`flow_env.py` OS-keychain lookup) resolved the `09:56Z` credential outage for `run_holon_flow.py` with 22
  passing unit tests in `tests/test_flow_env.py`.
- Commit `465da5f` added `parse_relative_limit_reset` to `run_holon_flow.py` and updated `tests/test_flow_fallback.py`
  for `gemini-4-neon` default and relative reset durations.
