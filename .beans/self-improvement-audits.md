# Self-Improvement Audit Log

This log is written by the self-improvement audit described in `.agents/self-improvement-audit.md`; the newest entry is
first.

## Entries

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
