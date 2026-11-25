# Self-Improvement Audit Log

This log is written by the self-improvement audit described in `.agents/self-improvement-audit.md`; the newest entry is
first.

## Entries

### 2026-11-25T05:41:00Z — Fifth-Merge Audit

- **Trigger:** fifth target-repo merge since `2026-11-25T05:07:00Z` (`holon-agentic-coder` PRs `#295`, `#296`, `#297`,
  `#298`, `#299`; `holon-coherence` unchanged at `#55` merged `2026-11-24T12:44:47Z` with `#56` open;
  `thomashan/dev-env` unchanged at `#41` with `#42` open). Note: `hac#300` (`05:31:18Z`) and `hac#301` (`05:38:33Z`)
  also merged while this audit was running (`05:22:44Z–05:41:00Z`).
- **Last merged pull requests at audit time:**
  - `holon-agentic-coder`: `#299` at trigger (`in-flight-pr-files-fallback`, merged `2026-11-25T05:20:56Z`; `#300`
    `05:31:18Z` and `#301` `05:38:33Z` merged during audit)
  - `holon-coherence`: `#55` (`coherence-module-line-budget-all`, merged `2026-11-24T12:44:47Z`)
  - `thomashan/dev-env`: `#41` (`tmux-shift-enter-extkeys`, merged `2026-11-25T04:03:06Z`)
- **Beans created or extended:**
  - Created: `0452` (Stage 5 KB promotion persists single-flow Stage 4 review chatter as `KB-failure-*.json` — `2,896`
    of `3,205` files `< 1 h` apart; `#296` added `21`, `#297` `4`, `#300` `3`, `#308` `6`), `0453` (consolidate `19`
    duplicated `test_*_self_doc.py` files / `2,199` lines on `main` + `7` open PR copies / `932` lines into one
    parameterized check), `0454` (`ci_bookkeeping_gate.py` `2-dot` `before..head_sha` compare forces full `7–9 min` CI
    on mechanical `Merge origin/main` pushes across `#295–#301`), `0455` (`post-pr-merge` calls `install_holon.py`
    without `--holon-only`, collides across burst merges, and left `bean-triage-prioritisation.md` stale since
    `02:29:34Z` across `7+` merges).
  - Extended: `0442` (`formatting.py` Stage 2 `prettier@3.8.4` timed out `2x 30 s` in both `0371` and `0438`/`#309`,
    leaving `P-1795584464-CLA-CO5.5.md` unformatted and causing immediate `Test - Hygiene` failure on `4cdc1913`),
    `0450` (`#308` Iter 3 & Iter 4 `review_local` failed `4/4` on `1` host test — Iter 3 named
    `test_repository_ledgers_survive_precheck_and_reconcile_byte_for_byte` — and Iter 4 failed `47 s` after GitHub CI
    passed `11/11` on `c960579d`), `0449` (`#308` Iter 3 resolver marked `R1-F1` `"applied"` on `executions/*.md` only,
    driving Iter 4 where R3 reversed approval), `0443` (`#308` hit 3rd 4-push `29 s` burst cancelling `8857f506`),
    `0407` (`#308` Round 2 `86+ min` on unchanged code; `#309` Iter 1 `3/3` approved blocked by Prettier failure),
    `0408` (`#309` `4cdc1913` failed `Test - Hygiene` on plan Prettier; `#296` `2` Hygiene failures), `0412` (wrapper
    pre-flight `lines 1–13` on `0371`/`0438` un-timestamped; Antigravity PRs `#295–#301` & `0407` unlogged; pushes,
    per-reviewer, and inner tool-vs-model timings unmeasured).

#### 1. Per-Step Timing Table (`2026-11-25T05:07:00Z` to `2026-11-25T05:40:24Z`)

Measured across `4` active/queued `hac` flows (`workspace-survival-job-parallel` `#308`,
`ledger-fragments-and-promotion` `0371`, `calibration-merge-adapted-file` `0438`/`#309`, `no-unneeded-full-review`
`0407`) plus GitHub PR/CI/commit records (`hac#295–#309`, `coh#56`, `dev-env#42`):

| Step                                                                                      | Count | Median (min) | Longest (min) | Longest in                                   |
| :---------------------------------------------------------------------------------------- | ----: | -----------: | ------------: | :------------------------------------------- |
| Pre-flight (credential probe, image check, worktree creation)                             |     - | not measured |  not measured | `0371`/`0438` lines 1–13 un-timed (`0412`)   |
| Stage 1: intent agent turn (`0371`, `0438`; full stage `0.33 m`)                          |     2 |         0.24 |          0.25 | `0371` (`ledger-fragments-and-promotion`)    |
| Stage 2: planner agent turn (incl. `60 s` Prettier timeouts)                              |     2 |         3.98 |          4.83 | `0371` (`0438`: `3.12 m`; stage `4.93/3.22`) |
| Stage 3: admission check (`0371` refused vs `#305`, `0438` admitted)                      |     2 |         0.27 |          0.27 | `0371` / `0438` (`0.27 m` each)              |
| Stage 3: overlap wait / halted block (`0407` `33.40 m` in-win / `178.73 m` tot.; `0371`)  |     2 |        20.50 |         33.40 | `0407` (`178.73 m` total since `02:41:40Z`)  |
| Stage 3: executor agent turn (`#309`/`0438`; stage `5.33 m`; tool vs model unlogged)      |     1 |         4.98 |          4.98 | `0438` (`calibration-merge-adapted-file`)    |
| Each git push & conflict probe/merge of target                                            |     - | not measured |  not measured | folded into stage turns (`0412`)             |
| Stage 4: empty-diff guard + PR create (`#309`/`0438`)                                     |     1 |         0.20 |          0.20 | `0438` (`calibration-merge-adapted-file`)    |
| Stage 4: reviewer ensemble turn (`3` reviewers; per-reviewer unlogged; `#308` i4, `#309`) |     2 |         4.15 |          4.47 | `hac#308` Round 2 iter 4 (`#309` i1 `3.83`)  |
| Stage 4: `review_local` host test run (`#308` i3 `05:06:12Z–05:09:01Z`, `#308` i4)        |     2 |         3.36 |          3.90 | `hac#308` Round 2 iter 4 (`#308` i3 `2.82`)  |
| Stage 4: resolver turn (`#308` i3; live `#308` i4 `15.20+ m`, `#309` i1 `0.12+ m`)        |     1 |         7.45 |          7.45 | `hac#308` Round 2 iter 3 (live i4 `15.20+`)  |
| Stage 4: target sync + ledger commit after resolver (`#308` i3)                           |     1 |         0.22 |          0.22 | `hac#308` Round 2 iter 3 (`29 s` burst)      |
| Stage 4: individual review iteration (review+local, excl. resolver; `#308` i3/i4, `#309`) |     3 |         7.63 |          8.43 | `hac#308` Round 2 iter 4 (`#309` i1 `3.93`)  |
| Stage 5: calibration work, CI registration wait, `final_head_ci`                          |     0 |            - |             - | no flow reached Stage 5 in window            |
| Pre-merge `Merge origin/main` CI wait (`#297`–`#300`; `#297`/`#298`/`#300` merged early)  |     4 |         8.36 |          9.12 | `hac#300` (`a4e23b9e`; `#297` `8.62 m`)      |
| Wait: PR ready (last cal) $\rightarrow$ maintainer merge (`#295–#299` cadence)            |     5 |       273.07 |        323.95 | `hac#295` (`#297` `295.98`, `#299` `273.07`) |
| GitHub: PR open $\rightarrow$ merged (`#295–#299` cadence)                                |     5 |       313.23 |        336.37 | `hac#295` (`#297` `317.95`, `#296` `313.23`) |

Stage totals clipped strictly inside `2026-11-25T05:07:00Z–05:40:24Z` (human wait sums `1.29 h` across merged
`hac#297–#301` plus `4.45 h` across open ready queue `hac#302–#307`, `coh#56`, `dev-env#42` = `5.75 h`):

| Stage     | Total (h) | Working (h) | Waiting on CI (h) | Waiting on another flow (h) | Waiting on human (h) | Idle (h) |
| :-------- | --------: | ----------: | ----------------: | --------------------------: | -------------------: | -------: |
| intent    |      0.01 |        0.01 |              0.00 |                        0.00 |                 0.00 |     0.00 |
| plan      |      0.14 |        0.14 |              0.00 |                        0.00 |                 0.00 |     0.00 |
| execute   |      0.78 |        0.09 |              0.00 |                        0.68 |                 0.00 |     0.00 |
| review    |      0.63 |        0.63 |              0.00 |                        0.00 |                 0.00 |     0.00 |
| calibrate |      0.00 |        0.00 |              0.00 |                        0.00 |                 5.75 |     0.00 |

- **Missing timing (`0412`):** `0371` and `0438` logs miss UTC timestamps on wrapper pre-flight (`lines 1–13`),
  Antigravity PRs (`#295–#301`) and `0407` left no `todo/flow-*.log`, and individual git pushes, conflict merges,
  per-reviewer latencies inside `4.47 / 3.83 min` ensembles, and tool-vs-model splits inside `4.98 min` Stage 3 and
  `7.45 / 15.20+ min` Stage 4 resolvers remain unmeasured.

#### 2. Churn Counts (`2026-11-25T05:07:00Z` to `2026-11-25T05:40:24Z`, plus `#295–#299` lifetimes)

- **CI pipeline runs:**
  - Across the **5 cadence merges (`hac#295–#299`, full PR lifetime):** `30` tested CI heads (`198` workflow runs:
    `#295` `4/28`, `#296` `10/64`, `#297` `6/42`, `#298` `6/36`, `#299` `4/28`), of which **`27` (`90.0%`) were churn**
    (`21` bookkeeping/conflict + `6` `main_merge` vs `3` resolver code-fix heads). Review iterations across `#295–#299`:
    **`8` total** (`1+3+2+1+1`): `5` minimum initial + **`3` repeat churn iterations** (`#296` x2 for `Hygiene`
    `FIND-CI-002` + `Merge main`, `#297` x1).
  - Across **in-window `hac` CI (`05:07:00Z–05:40:24Z`):** `86` workflow runs across `17` push/PR head events (`70`
    success, `1` failure on `#309` `4cdc1913` `Test - Hygiene` Prettier, `6` cancelled: `5` on `#308` `8857f506` +
    `05:09:38Z` `push` `0bd580ea` `Test - Unit`, `9` still in progress). Of `9` PR heads in window (`79e0ab33`,
    `821656a1`, `ebb688d6`, `69c4188f`, `8857f506`, `c960579d`, `a4e23b9e`, `cf7c77f6`, `4cdc1913`), **`8/9` (`88.9%`)
    were churn** (`5` `main_merge` + `3` bookkeeping/doc-only incl. `ebb688d6` `executions/*.md`-only fix; only `#309`
    `4cdc1913` carried new feature/test code).
- **Stage 2/3/4/5 & Harness churn:**
  - **Stage 2 `formatting.py` Prettier timeouts $\rightarrow$ `#309` immediate CI fail (`0442`, `0408`, `0407`):**
    `formatting.py:11` (`prettier@3.8.4`) timed out `2x 30 s` in both `0371` and `0438`, leaving
    `P-1795584464-CLA-CO5.5.md` unformatted; `#309` (`4cdc1913`) immediately failed `Test - Hygiene` (`make lint-md`),
    blocking `3/3` `APPROVED (0/0/0)` reviewers at `05:40:16Z` into a full resolver/re-review cycle.
  - **Stage 5 KB chatter bloat (`0452`):** `3,205` `KB-failure-*.json` files on `main` (`2,896` = `90.4%` with `ACT-*`
    refs `< 1 h` apart); `#296` added `21`, `#297` `4`, `#300` `3`, `#308` `6`.
  - **Duplicate `self_doc` test scanners (`0453`):** `#295`, `#297`, `#298`, `#300` added separate copy-pasted scanners;
    `19` files (`2,199` lines) on `main` + `7` open (`932` lines) duplicate identical AST/allowlist guards.
  - **Pre-merge `Merge origin/main` CI & queue cascade (`0454`, `0371`):** `#295–#301` (`7/7` PRs) triggered full
    `7–9 min` CI on `Merge origin/main` despite `pr_own_identical=True`; `#302–#308` remain queued (`#305`–`#308`
    `DIRTY`/`UNKNOWN`), while `0371` itself blocked at `05:32:48Z` on `#305` (`warning: folder touch set ledger/`).
  - **`#308` Round 2 `86+ min` loop (`0407`, `0449`, `0450`, `0443`):** Iter 3 doc-only fix (`ebb688d6`) + `29 s` 4-push
    burst cancelled `8857f506` and triggered Iter 4 (`R3` reversed approval); host `review_local` failed `4/4` on `1`
    test (`1/7755`, `1/7788`), failing Iter 4 `47 s` after GitHub CI passed `11/11` on `c960579d`.
  - **Harness burst-merge rebuilds & stale triage (`0455`):** `7` `hac` merges in `39 min` omitted `--holon-only` and
    left `.beans/bean-triage-prioritisation.md` stale since `02:29:34Z`.

#### 3. Ranked Suggestions

1. **Bean `0452` (high, Stage 5 / Knowledge — new):** Exclude intra-flow Stage 4 `ACT-REV`/`ACT-FIND` rows (or require
   `>= 2` distinct intents) from `KB-failure-*.json` promotion (`2,896/3,205` single-flow artifacts bloating
   git/`lint-json` and conflicts; `#296` added `21`).
2. **Bean `0454` (high, Pipeline / CI Gate — new):** Avoid redundant `7–9 min` full CI in `ci_bookkeeping_gate.py` on
   mechanical `Merge origin/main` pushes with `pr_own_identical=True` and disjoint `main` changes (after/alongside
   `0371`; `#295–#301` `7/7` hit full CI).
3. **Bean `0455` (high, Harness / `post-pr-merge` — new):** Pass `--holon-only` on `hac` merges, coalesce concurrent
   burst rebuilds, and run/commit `prioritise_beans.py` cleanly (`bean-triage-prioritisation.md` stale `3.1+ h` across
   `7` merges).
4. **Bean `0453` (normal, Code Quality / Tests — new):** Consolidate `19` (`2,199` lines) + `7` open (`932` lines)
   duplicated `test_*_self_doc.py` AST/tokenize scanners into one shared parameterized guard after `#301–#307` drain.
5. **Extended `0442`, `0450`, `0449`, `0443`, `0407`, `0408`, `0412`:** Fix `formatting.py:11` (`prettier@3.8.4`
   timeouts causing `#309` `4cdc1913` CI failure despite `3/3` approval), probe finished GitHub CI in `review_local`
   (`#308` Iter 4 failed `47 s` after green CI) and isolate
   `test_repository_ledgers_survive_precheck_and_reconcile_byte_for_byte`, count `"applied"` on `executions/*.md`-only
   diffs as no code change for `unchanged_streak`, batch Stage 4 pushes (`29 s` 4-push burst on `#308`), skip unchanged
   `end_of_flow_sync` / Markdown-only re-reviews, gate local Markdown before push, and timestamp wrapper pre-flight
   lines (`lines 1–13`). _(Existing critical/high `0371`, `0446`, `0448`, `0403`/`0405` remain top priorities.)_

#### 4. Examined and Found in Order

- **Cadence `#295–#299` CI & review churn:** `27/30` (`90.0%`) tested PR heads were bookkeeping/conflict (`21`) or
  `main_merge` (`6`); `#295, #298, #299` passed reviewers in `1` iteration (`#297` `2`, `#296` `3` due to `Hygiene`
  Prettier + `Merge main`), while every PR waited `255–324 min` (`median 273.07 min`) for maintainer merge and hit queue
  conflicts.
- **Live Stage 2 $\rightarrow$ Stage 4 `#309` (`0438`) causality:** Double `30 s` `npx --yes prettier@3.8.4` timeouts in
  `formatting.py` directly caused unformatted `P-1795584464-CLA-CO5.5.md` $\rightarrow$ `Test - Hygiene` failure
  $\rightarrow$ blocked `3/3` approved reviewers at `05:40:16Z`.
- **Stage 5 KB audit on `main`:** Confirmed `2,896/3,205` (`90.4%`) `KB-failure-*.json` files record single-flow `< 1 h`
  `ACT-*` references generated by `wisdom.py:278-296` + flow-scoped branch targets.
- **`#308` Iter 3–4 + `0371` admission block:** Confirmed
  `test_repository_ledgers_survive_precheck_and_reconcile_byte_for_byte` (`test_ledger_append_only.py:469-488`) failed
  host `review_local` `4/4` while passing CI/container/isolated runs; `0371` (`ledger-fragments-and-promotion`) blocked
  immediately at `05:32:48Z` overlapping `PR #305`.

### 2026-11-25T05:07:00Z — Fifth-Merge Audit

- **Trigger:** fifth target-repo merge since `2026-11-25T04:02:00Z` (`holon-agentic-coder` PRs `#290`, `#291`, `#292`,
  `#293`, `#294`; `holon-coherence` unchanged at `#55` merged `2026-11-24T12:44:47Z` with `#56` open;
  `thomashan/dev-env` merged `#41` at `04:03:06Z` and completed flow `#42`). Note: `hac#295` (`04:59:58Z`) and `hac#296`
  (`05:01:49Z`) also merged while this audit was running (`04:56:57Z–05:07:00Z`).
- **Last merged pull requests at audit time:**
  - `holon-agentic-coder`: `#294` at trigger (`core-helpers-test-helpers`, merged `2026-11-25T04:55:29Z`; `#296`
    `split-cli-init-modules` merged during audit at `2026-11-25T05:01:49Z`)
  - `holon-coherence`: `#55` (`coherence-module-line-budget-all`, merged `2026-11-24T12:44:47Z`)
  - `thomashan/dev-env`: `#41` (`tmux-shift-enter-extkeys`, merged `2026-11-25T04:03:06Z`)
- **Beans created or extended:**
  - Created: `0448` (`end_of_flow_sync._reenter_review_and_calibrate` leaves stale `calibrate=SUCCESS` + stale `review`,
    causing nested `Stage 5 rerun` inside Stage 4, bogus `ACT-WITHDRAW`, 4-push CI cancellations, and double Stage 5 on
    `hac#308`), `0449` (Stage 4 `unchanged_streak` keys on raw `head_sha` and ignores unresolvable `open` findings,
    letting `hac#308` Round 2 loop `49.6+ min` over `3` iterations on doc-only/sync commits), `0450` (Stage 4
    `review_local` drops `TestMeasurement.output_excerpt` and preempts pending GitHub CI with `2.8–2.9 min` macOS host
    runs failing `1/7690`), `0451` (`dev-env` CI lacks `ci_bookkeeping_gate` and runs `test-unit (macos-latest)`
    serially in `14.4 min`, causing `18.63 min` Stage 5 overruns on `dev-env#41`/`#42`).
  - Extended: `0407` (`hac#308` Round 2 ledger-only `end_of_flow_sync` `1a6c1ab1` re-entered `49.6+ min` Stage 4 and
    allowed reviewer reversal; `0407` idled `69.25 min` more = `142.33 min` total), `0443` (`hac#308` hit two `30–39 s`
    quadruple-push bursts cancelling CI; `15/17` PR heads churn; `dev-env#42` `ef1fbd76` cancelled `b1dc27bb` runs),
    `0445` (`hac#308` checkpoint stayed frozen at `current_stage: "completed"` across all `49.6+ min` of Round 2),
    `0442` (`hac#308` Round 1 re-calibration `2.50 min`; `dev-env#42` Stage 5 calibration `2.60 min`), `0412`
    (`dev-env#42` and `0407` unlogged in `todo/flow-*.log`; pre-flight, pushes, conflict merges, per-reviewer/tool
    latencies unmeasured). _(Concurrent Claude Code session dirty beans such as `0371`, `0383`, `0405` left untouched.)_

#### 1. Per-Step Timing Table (`2026-11-25T03:54:45Z` to `2026-11-25T05:04:00Z`)

Measured across `2` active `hac` flows (`workspace-survival-job-parallel` `#308` in
`todo/flow-workspace-survival-job-parallel.log` + git/GitHub; `no-unneeded-full-review` `0407` checkpoint, halted in
Stage 3), `1` completed `dev-env` flow (`tmux-focus-events-on` `#42` checkpoint), and GitHub PR/CI/commit records
(`hac#290`–`#308`, `coh#56`, `dev-env#41`–`#42`):

| Step                                                                                        | Count | Median (min) | Longest (min) | Longest in                                   |
| :------------------------------------------------------------------------------------------ | ----: | -----------: | ------------: | :------------------------------------------- |
| Pre-flight (credential probe, image check, worktree creation)                               |     - | not measured |  not measured | `dev-env#42` & `0407` unlogged (`0412`)      |
| Stage 1: intent agent turn (`dev-env#42` total stage `0.28 m`)                              |     1 |         0.18 |          0.18 | `dev-env#42` (`tmux-focus-events-on`)        |
| Stage 2: planner agent turn (`dev-env#42` total stage `2.53 m`)                             |     1 |         2.45 |          2.45 | `dev-env#42` (`tmux-focus-events-on`)        |
| Stage 3: admission check (`dev-env#42`)                                                     |     1 |         0.05 |          0.05 | `dev-env#42` (`tmux-focus-events-on`)        |
| Stage 3: overlap wait / admission refusal (`0407` blocked `03:54:45Z–05:04:00Z+`)           |     1 |        69.25 |         69.25 | `no-unneeded-full-review` (`142.33 m` tot.)  |
| Stage 3: executor agent turn (tool vs model split unlogged)                                 |     1 |         4.80 |          4.80 | `dev-env#42` (`tmux-focus-events-on`)        |
| Each push & conflict probe/merge of target                                                  |     - | not measured |  not measured | folded into surrounding stage (`0412`)       |
| Stage 4: empty-diff guard + PR create/edit (`dev-env#42`, `hac#308` r2)                     |     2 |         0.19 |          0.20 | `dev-env#42` (`tmux-focus-events-on`)        |
| Stage 4: reviewer ensemble turn (`3` reviewers; per-reviewer unlogged; r2i3 `2.55+ m`)      |     4 |         6.84 |         14.85 | `dev-env#42` iter 1 (`hac#308`: `4.13–9.28`) |
| Stage 4: local test run after reviewers (`review_local` on `1a6c1ab1`, `31fdc482`)          |     2 |         2.85 |          2.87 | `hac#308` Round 2 iter 2                     |
| Stage 4: resolver turn (incl. push; tool vs model split unlogged)                           |     2 |        15.75 |         27.02 | `hac#308` Round 2 iter 1 (`FIND-CI` blind)   |
| Stage 4: conflict gate + nested `Stage 5 rerun` + ledger (`hac#308` `0.80 m` / `#42`)       |     2 |         0.46 |          0.80 | `hac#308` r1i2 (incl. `0.25 m` Stg5 rerun)   |
| Stage 4: individual review iteration (review pass only; full r2i1+res `34.48 m`)            |     4 |         8.34 |         14.98 | `dev-env#42` iter 1 (`hac#308`: `7.05–9.40`) |
| CI wait (Stage 5 `merged_head_ci` on `3357edd2`)                                            |     1 |         7.97 |          7.97 | `hac#308` Round 1 post-sync                  |
| Stage 5: calibration work + reconciliation + promotion (excl. CI waits)                     |     2 |         2.55 |          2.60 | `dev-env#42` (`hac#308`: `2.50 m`)           |
| CI registration wait (Stage 5 `final_head_ci`: `1 s` `#308`, `18 s` `#42`)                  |     2 |         0.16 |          0.30 | `dev-env#42` (`tmux-focus-events-on`)        |
| CI wait (Stage 5 `final_head_ci`: `65 s` `#308`, `926.88 s` `ef1fbd76` `#42`)               |     2 |         8.27 |         15.45 | `dev-env#42` (serial macOS `862.45 s`)       |
| Stage 5: final-head check & exit                                                            |     2 |         0.10 |          0.12 | `hac#308` (`f727226d`)                       |
| End-of-flow sync check + `origin/main` merge (`04:14:18Z–04:14:26Z`)                        |     1 |         0.13 |          0.13 | `hac#308` Round 2 entry (`1a6c1ab1`)         |
| Pre-merge `Merge origin/main` CI wait (`#290`–`#293` completed; `#294`–`#295` merged early) |     4 |         8.08 |          8.67 | `holon-agentic-coder#292`                    |
| Wait: PR ready (last calibration) $\rightarrow$ maintainer merge (`#290`–`#294`)            |     5 |       338.43 |        482.95 | `holon-agentic-coder#291` (`#41`: `235.0`)   |
| GitHub: PR open $\rightarrow$ merged (`#290`–`#294`)                                        |     5 |       494.13 |        516.15 | `holon-agentic-coder#290` (`#292`: `504.6`)  |

Stage totals across in-window events (`03:54:45Z`–`05:04:00Z`; human/merge wait sums in-window `03:54:45Z`/ready
$\rightarrow$ `mergedAt`/`05:04Z` across `hac#290`–`#296` + `dev-env#41`–`#42` = `5.86 h`, `#290`–`#294` alone =
`3.25 h`):

| Stage     | Total (h) | Working (h) | Waiting on CI (h) | Waiting on another flow (h) | Waiting on human (h) | Idle (h) |
| :-------- | --------: | ----------: | ----------------: | --------------------------: | -------------------: | -------: |
| intent    |      0.00 |        0.00 |              0.00 |                        0.00 |                 0.00 |     0.00 |
| plan      |      0.04 |        0.04 |              0.00 |                        0.00 |                 0.00 |     0.00 |
| execute   |      1.24 |        0.08 |              0.00 |                        1.15 |                 0.00 |     0.00 |
| review    |      1.21 |        1.21 |              0.00 |                        0.00 |                 0.00 |     0.00 |
| calibrate |      0.51 |        0.10 |              0.41 |                        0.00 |                 5.86 |     0.00 |

- **Missing timing (`0412`):** `dev-env#42` and `0407` left no `todo/flow-*.log`; pre-flight (credential probe, image
  check, worktree creation), individual git pushes, conflict merges, per-reviewer latencies inside `4.13 / 4.40 / 14.85`
  min ensembles, and Stage 3 / resolver tool-vs-model splits remain unmeasured.

#### 2. Churn Counts (`2026-11-25T03:54:45Z` to `2026-11-25T05:05:00Z`)

- **CI pipeline runs:**
  - Across the **5 cadence merges** (`hac#290`–`#294`, full PR lifetime): `47` tested CI heads (`459` check-runs), of
    which **`43` (`91.5%`) were churn** (`29` bookkeeping, `14` `main`-merge, vs `4` code heads; `#290` `11`, `#291`
    `4`, `#292` `19`, `#293` `8`, `#294` `5` heads).
  - Across **in-window `hac` CI activity** (`03:54:45Z`–`05:05:00Z`): `144` workflow runs across `24` head SHAs (`112`
    success, `23` cancelled, `9` in progress): `7` `main` push heads (`ae2c5b41`..`4c6232cb`, with `daf3fa74` &
    `099025f8` cancelled mid-run on `Test - Unit`/`Test - Stress` by subsequent merges) and `17` PR heads (`#291`–`#295`
    - `12` heads on `#308`). Of the `17` PR heads, **`15` (`88.2%`) were churn** (`7` `main`-merge, `8` bookkeeping, vs
      `2` code-push heads `3595c1f1` & `54321e50` which themselves only edited `executions/E-*.md` after
      `review_local`).
  - Across **`dev-env#42`** (`04:14:12Z`–`04:48:00Z`): `15` workflow runs across `3` heads (`2/3 = 66.7%` bookkeeping
    churn; `2` cancelled on `b1dc27bb` when `ef1fbd76` pushed). **Zero** CI check failures occurred in `hac` or
    `dev-env` during the window; all cancellations were self-inflicted head replacements/merges.
- **Review, Stage 3/5, and Queue churn:**
  - **Queue conflict cascade (`0371`):** after `#290`–`#296` merged (`4c6232cb`), **`12/12` open `hac` PRs**
    (`#297`–`#308`) sit `CONFLICTING`/`DIRTY`; `git merge-tree` confirms all `17` non-merged `flow-*` worktrees conflict
    **solely** on `holon-knowledge/ledger/*.jsonl`.
  - **Nested `Stage 5 rerun` + false consensus withdrawal (`0448`):** `end_of_flow_sync._reenter_review_and_calibrate`
    left stale `calibrate=SUCCESS` + stale `review` in `context`, triggering a `0.25 min` `Stage 5 rerun` inside Stage 4
    (`04:01:58Z`), false `ACT-WITHDRAW` (`04:02:08Z`), a `4`-push CI-cancelling burst (`39 s`), and `12.08 min` of
    double Stage 5 work/CI wait on `hac#308`.
  - **Ledger-only `End-of-flow sync` re-review + frozen checkpoint (`0407`, `0445`):** `hac#308` merged ledger-only
    `origin/main` (`1a6c1ab1`, `04:14:22Z`) and re-entered full Stage 4 (`49.6+ min` still live in Iter 3) while
    `checkpoint.current_stage` stayed stuck at `"completed"`, allowing reviewers to reverse Round 1 approval on
    unchanged code.
  - **Infinite `unchanged_streak` loop + blind `review_local` (`0449`, `0450`):** `hac#308` Round 2 ran `2` macOS host
    `review_local` passes (`2.82 + 2.87 min`, failing `1/7690` unseen in Linux CI) with `output_excerpt` dropped from
    `FIND-CI`, driving `27.02 min` + `4.47 min` doc-only resolver churn (`3595c1f1`, `54321e50`) and target merge
    `bd581a65` that reset raw-`head_sha` `unchanged_streak`, dispatching Iter 3 (`05:01:27Z+`).
  - **Stage 4 quadruple-push bursts (`0443`):** `hac#308` hit `2` quadruple-push bursts (`39 s` at `04:01:29Z`, `30 s`
    at `05:00:49Z`), cancelling `03b6dbe7`, `b95c09b7`, `3595c1f1`, and `bd581a65`.
  - **`dev-env` bookkeeping & serial macOS CI (`0451`):** `dev-env#42` waited `15.45 min` (`926.88 s`) on bookkeeping
    head `ef1fbd76` (`18.68 min` Stage 5 vs `10 min` budget) because `dev-env` lacks `ci_bookkeeping_gate` and runs
    `203` macOS unit tests serially (`862.45 s` vs `2.3 min` Ubuntu).
  - **Stage 3 `SPLIT` admission block (`0446`, `0407`):** `0407` stayed idle an additional `69.25 min` (`142.33 min`
    total). **Container rebuild churn (`0402`):** `5` post-merge 8-image Docker Bake rebuilds ran during live Stage 4.

#### 3. Ranked Suggestions

1. **Extended `0407` & `0445` (critical/high, Flow / End-of-Flow Sync):** Skip full Stage 4 re-entry when
   `end_of_flow_sync` merges zero code diff (`hac#308` Round 2 `49.6+ min` still live; reviewer reversal on unchanged
   code) and clear `checkpoint.current_stage == "completed"` before re-entry.
2. **Bean `0448` (high, Flow / Stage 4 / Stage 5 — new):** Clear stale `context.stage_results["calibrate"]` (and
   supersede prior `review`) in `end_of_flow_sync._reenter_review_and_calibrate` so `review_calibration_freshness`
   cannot run nested Stage 5 inside Stage 4 (`hac#308` false `ACT-WITHDRAW`, 4-push cancellation burst, `12.08 min`
   double Stage 5).
3. **Bean `0449` (high, Flow / Stage 4 / Convergence — new):** Key `unchanged_streak` in `flow/review/loop.py:568-578`
   on `(reviewer_finding_sigs, PR-own code diff fingerprint)` instead of raw `head_sha`, and halt when actionable
   findings stay `open` with zero code diff (`hac#308` Round 2 `49.6+ min` loop across `3` iterations).
4. **Bean `0450` (high, Flow / Stage 4 / `review_local` — new):** Preserve `TestMeasurement.output_excerpt` and failing
   test names in `local_tests.py` / `review_report.py`, and wait briefly for `pending > 0` GitHub CI instead of eager
   host `7,690`-test runs on objected iterations (`hac#308` `2` host runs failing `1/7690`, driving `27.02 min` +
   `4.47 min` blind resolver churn).
5. **Bean `0451` (high, Pipeline / `dev-env` — new):** Port `ci_bookkeeping_gate` and `pytest -n auto --dist worksteal`
   to `thomashan/dev-env` workflows (`dev-env#42` `15.45 min` `final_head_ci` wait on `ef1fbd76`, `18.68 min` Stage 5;
   `dev-env#41` `d6fb465c` `15.1 min`).
6. **Extended `0443`, `0442`, `0412` (high/normal):** Batch Stage 4 pushes (`hac#308` `2` quadruple-push bursts,
   `dev-env#42` `b1dc27bb` cancelled), avoid double `npx prettier` (`2.50–2.60 min` calibration in `#308`/`#42`), and
   close remaining logging/timing gaps (`dev-env#42`/`0407` unlogged, per-reviewer/tool splits unmeasured). _(Existing
   `0371` critical and `0446` high remain urgent for the `12/12` `CONFLICTING` PR cascade and `142.33 min` `0407`
   block.)_

#### 4. Examined and Found in Order

- **Zero CI failures in window (`hac` & `dev-env`):** All `112` completed `hac` workflow runs and `13` completed
  `dev-env` runs passed; all `25` cancellations (`23` `hac`, `2` `dev-env`) were self-inflicted head
  replacements/merges.
- **Mechanical ledger-only queue cascade confirmed:** `git merge-tree` across all `17` non-merged `hac` `flow-*`
  worktrees against `origin/main` (`4c6232cb`) showed zero non-ledger code conflicts; all conflicts lie in
  `holon-knowledge/ledger/*.jsonl`.
- **`dev-env` end-to-end flow healthy except Stage 5 CI wait:** `dev-env#42` completed Stage 1–3 cleanly in `7.75 min`
  (`04:06:16Z..04:14:01Z`) and passed reviewers in 1 iteration (`14.98 min`), with `15.45 min` of its `41.73 min`
  runtime spent waiting on serial macOS unit CI over a bookkeeping-only commit (`ef1fbd76`).

### 2026-11-25T04:02:00Z — Fifth-Merge Audit

- **Trigger:** fifth merge since `2026-11-25T02:54:00Z` (`holon-agentic-coder` PRs `#285`, `#286`, `#287`, `#288`,
  `#289`; `holon-coherence` last merged `#55` at `2026-11-24T12:44:47Z`, with `#56` open).
- **Last merged pull requests at audit time:**
  - `holon-agentic-coder`: `#289` (`core-helpers-self-doc`, merged `2026-11-25T03:42:30Z`)
  - `holon-coherence`: `#55` (`coherence-module-line-budget-all`, merged `2026-11-24T12:44:47Z`)
- **Beans created or extended:**
  - Created: `0445` (end-of-flow sync leaves `checkpoint.current_stage` stuck at `"completed"` with frozen
    `context.logs` during `15.3+ min` Stage 4/5 re-entry on `PR #308`), `0446` (Stage 3 admission checks `SPLIT` parent
    plans against their union touch set before decomposition, blocking `0407` `60.75 min` on
    `apps/sandbox-executor/tests/` and `budgets.py`), `0447` (`Workspace survival` concurrent child runs saturate 4-vCPU
    runners at `364 s` vs `365.5 s` baseline on `PR #308`, needing one shared child run or separate CI jobs).
  - Extended: `0439` (`PR #287` `ba6b525a` edited `7` and `PR #290` `a06586a6`/`0b7f019c` edited `12` out-of-scope files
    on macOS `CI Timing Gate` `FIND-CI` failures, colliding on `9` code/test files in `#290` `a344ce2f` after `#287`
    merged and putting `#287`/`#290` into `0407`'s `blocked_by`), `0443` (`PR #308` hit `3` Stage 4 `9–16 s`
    double/triple-push CI cancellations across `16` cancelled runs and `317 s` wasted `Docker Build`), `0407` (`PR #308`
    ran full re-reviews on `0b986f9b`, `11721091`, and ledger-only `End-of-flow sync` `adaf72a8`; `0407` itself blocked
    `60.75 min` in Stage 3), `0442` (`PR #308` spent `2.60 min` in Stage 5 calibration and hit `2×30 s` `npx prettier`
    timeouts in Stage 2), `0412` (`no-unneeded-full-review` unlogged in `todo/flow-*.log`; wrapper pre-flight
    untimestamped; `End-of-flow sync` unlogged in checkpoint; per-reviewer/tool-vs-model split unmeasured). _(Note:
    `0371`, `0400`, `0405` had concurrent session edits and were left untouched.)_

#### 1. Per-Step Timing Table (`2026-11-25T02:54:00Z` to `2026-11-25T03:54:45Z`)

Measured across `2` active flows (`workspace-survival-job-parallel` `#308` in
`todo/flow-workspace-survival-job-parallel.log` and checkpoint; `no-unneeded-full-review` `0407` checkpoint, halted in
Stage 3) and GitHub PR/CI/commit records (`hac#285`–`#308`, `coh#56`):

| Step                                                                                                   | Count | Median (min) | Longest (min) | Longest in                                  |
| :----------------------------------------------------------------------------------------------------- | ----: | -----------: | ------------: | :------------------------------------------ |
| Pre-flight (credential probe, image check, worktree creation)                                          |     - | not measured |  not measured | wrapper lines untimestamped (`0412`)        |
| Stage 1: intent agent turn                                                                             |     0 |            - |             - | none in window (`0407` at `02:35Z`)         |
| Stage 2: planner agent turn                                                                            |     0 |            - |             - | none in window (`0407` at `02:35Z–02:41Z`)  |
| Stage 3: admission wait / refusal (`0407` blocked `02:54:00Z–03:54:45Z`)                               |     1 |        60.75 |         60.75 | `no-unneeded-full-review` (`73.08 m` total) |
| Stage 3: executor work in window (`#308` `02:54:00Z–03:10:31Z`; `42.09 m` total)                       |     1 |        16.52 |         16.52 | `workspace-survival-job-parallel` (`#308`)  |
| Each push & conflict probe/merge of target                                                             |     - | not measured |  not measured | folded into surrounding stage (`0412`)      |
| Stage 4: empty-diff guard + PR create/edit (`#308` initial + re-entry)                                 |     2 |         0.19 |          0.20 | `workspace-survival-job-parallel` (`#308`)  |
| Stage 4: reviewer ensemble turn (`3` reviewers; per-reviewer unlogged)                                 |     3 |         4.20 |          9.42 | `workspace-survival-job-parallel` iter 2    |
| Stage 4: local test run after reviewers (`review_local` on `adaf72a8`)                                 |     1 |         2.87 |          2.87 | `workspace-survival-job-parallel` re-entry  |
| Stage 4: resolver turn (incl. push)                                                                    |     2 |         3.60 |          5.17 | `workspace-survival-job-parallel` re-entry  |
| Stage 4: conflict gate + ledger commits (`5cb52b05` $\rightarrow$ `b14bd3dd` $\rightarrow$ `24d23329`) |     1 |         0.47 |          0.47 | `workspace-survival-job-parallel` (`#308`)  |
| Stage 4: individual review iteration (completed in window; iter 4 `2.73 m` live)                       |     3 |         7.13 |          9.55 | `workspace-survival-job-parallel` iter 2    |
| Stage 4: full review stage (`16.00 m` initial + `15.28 m` re-entry in progress)                        |     2 |        15.64 |         16.00 | `workspace-survival-job-parallel` (`#308`)  |
| CI wait (Stage 5 `merged_head_ci` on `24d23329`)                                                       |     1 |         8.75 |          8.75 | `workspace-survival-job-parallel` (`#308`)  |
| Stage 5: calibration work + reconciliation + promotion (excl. CI waits)                                |     1 |         2.60 |          2.60 | `workspace-survival-job-parallel` (`#308`)  |
| CI registration + CI wait (Stage 5 `final_head_ci` on `de6441ff`: `18 s` + `49 s`)                     |     1 |         1.13 |          1.13 | `workspace-survival-job-parallel` (`#308`)  |
| Stage 5: final-head check & exit (`03:39:13Z–03:39:19Z`)                                               |     1 |         0.10 |          0.10 | `workspace-survival-job-parallel` (`#308`)  |
| End-of-flow sync check + `origin/main` merge (`03:39:20Z–03:39:28Z`)                                   |     1 |         0.13 |          0.13 | `workspace-survival-job-parallel` (`#308`)  |
| Pre-merge `Merge origin/main` CI wait (`#285`–`#289` merge commit $\rightarrow$ CI)                    |     5 |         6.95 |         10.12 | `holon-agentic-coder#287` (`3b9ad780`)      |
| Wait: PR ready (last calibration) $\rightarrow$ maintainer merge (`#285`–`#289`)                       |     5 |       523.05 |        564.13 | `holon-agentic-coder#285`                   |
| GitHub: PR open $\rightarrow$ merged (`#285`–`#289`)                                                   |     5 |       552.62 |        587.47 | `holon-agentic-coder#285`                   |

Stage totals across in-window events (`02:54:00Z`–`03:54:45Z`; `PR #285`–`#289` pre-merge waits accrued largely before
`02:54Z`; in-window `02:54Z`–`mergedAt` human/merge-queue wait across `#285`–`#289` was `2.70 h`):

| Stage     | Total (h) | Working (h) | Waiting on CI (h) | Waiting on another flow (h) | Waiting on human (h) | Idle (h) |
| :-------- | --------: | ----------: | ----------------: | --------------------------: | -------------------: | -------: |
| intent    |      0.00 |        0.00 |              0.00 |                        0.00 |                 0.00 |     0.00 |
| plan      |      0.00 |        0.00 |              0.00 |                        0.00 |                 0.00 |     0.00 |
| execute   |      1.29 |        0.28 |              0.00 |                        1.01 |                 0.00 |     0.00 |
| review    |      0.52 |        0.52 |              0.00 |                        0.00 |                 0.00 |     0.00 |
| calibrate |      0.21 |        0.05 |              0.16 |                        0.00 |                 2.70 |     0.00 |

- **Missing timing (`0412`):** `no-unneeded-full-review` (`0407`) left no `todo/flow-*.log`;
  `flow-workspace-survival-job-parallel.log` wrapper pre-flight lines have no timestamps; `End-of-flow sync` re-entry
  (`03:39:20Z–03:54:45Z+`) is absent from `checkpoint.context.logs` and `checkpoint.stage_results` while running
  (`0445`); per-reviewer latencies and executor tool-vs-model split remain unmeasured.

#### 2. Churn Counts (`2026-11-25T02:54:00Z` to `2026-11-25T03:54:45Z`)

- **CI pipeline runs:**
  - Across the **5 cadence merges** (`hac#285`–`#289`, full PR lifetime): `25` tested CI heads (`275` check-runs), of
    which **`18` (`72.0%`) were churn** (`13` bookkeeping, `5` `main`-merge, `7` code).
  - Across **all CI activity in the window** (`02:54:00Z`–`03:54:45Z`): `20` distinct head SHAs (`128` GitHub Actions
    workflow runs: `108` success, `16` cancelled, `4` in progress at cutoff), comprising `5` `main` push heads (`35`
    runs) and `15` PR heads (`93` runs). Of the `15` PR heads, **`12` (`80.0%`) were churn** (`7` `main`-merge: `#286`
    `59abd6bc`, `#287` `3b9ad780`, `#288` `d3d6f5a8`, `#289` `f2c8b08f`, `#290` `a344ce2f`, `#308` `b14bd3dd` &
    `adaf72a8`; `5` bookkeeping: `#308` `8f533e24`, `5cb52b05`, `24d23329`, `de6441ff`, `a27a4ce4`; vs `3` code heads:
    `#308` `2b840055`, `0b986f9b`, `11721091`).
  - **Zero** CI failures occurred in the window; all `16` cancelled workflow runs were self-inflicted head replacements
    on `PR #308` (`3` double/triple-push ledger cancellations + `2b840055` `Test - Unit` cancelled at `371 s` when
    `0b986f9b` arrived).
- **Review, Stage 3/5, and Queue churn:**
  - **Queue conflict cascade (`0371`):** after `#285`–`#289` merged, **`16` of `19` open `hac` PRs** (`#291`–`#295`,
    `#297`–`#307`) sit `CONFLICTING`/`DIRTY` solely on `holon-knowledge/` files (`non_kb_overlaps_285_289={}` for all
    `17` PRs `#291`–`#307`), while `5` `Merge origin/main` CI runs executed in-window (`6.95 min` median CI).
  - **Out-of-scope `FIND-CI` resolver edits (`0439`):** discovered in `#287` (`ba6b525a`, `7` out-of-scope files) and
    `#290` (`a06586a6`/`0b7f019c`, `12` out-of-scope files) after macOS `CI Timing Gate` failures; when `#287` merged
    (`03:21:48Z`), `#290`'s `a344ce2f` merge (`03:50:30Z`) hit **9 code/test conflicts** (plus 3 ledgers) and both PRs
    blocked `0407`.
  - **Stage 4 double/triple-push cancellations (`0443`):** on `PR #308`, `0b986f9b` $\rightarrow$ `8f533e24` (`+13 s`),
    `5cb52b05` $\rightarrow$ `b14bd3dd` $\rightarrow$ `24d23329` (3 pushes in `20 s`), and `11721091` $\rightarrow$
    `a27a4ce4` (`+16 s`) cancelled `15` workflow runs (`317 s` wasted `Docker Build`) and forced full CI on all `3`
    `chore(review)` heads.
  - **End-of-flow sync & checkpoint bug (`0445`, `0407`):** `PR #308` merged ledger-only `origin/main` (`adaf72a8`,
    `03:39:23Z`), unconditionally re-entered full Stage 4 (`15.3+ min` in window) instead of carrying approval by
    fingerprint, and left `checkpoint.current_stage == "completed"` for `15.3+ min` while live.
  - **Stage 3 admission block on `SPLIT` parent (`0446`):** `0407` (`no-unneeded-full-review`) sat blocked
    **`60.75 min`** (`73.08 min` total) on `apps/sandbox-executor/tests/` and `budgets.py` across `7` in-flight items
    before child 1 could even plan.
  - **`Test - Stress` 4-vCPU saturation (`0447`):** `PR #308`'s concurrent child runs (`~334 s` each vs `~180 s` serial)
    yielded `364 s` (`399 s` workflow) vs `365.5 s` baseline (`R3-F1` left `open`).

#### 3. Ranked Suggestions

1. **Extended `0439` (high, Flow / Stage 4 / Resolver):** Enforce Stage 4 resolver touch-set guards and ignore
   timing-gate `FIND-CI` failures (evidence: `#287` `7` and `#290` `12` out-of-scope files $\rightarrow$ `9` code/test
   conflicts in `#290` `a344ce2f`).
2. **Extended `0443` (high, Flow / Stage 4 / CI Churn):** Batch Stage 4 resolver/conflict-gate and `chore(review)`
   pushes into one push (evidence: `#308` `3` double/triple-push cancellations wasting `317 s` `Docker Build` and
   defeating `ci_bookkeeping_gate` `3` times).
3. **Bean `0445` (high, Flow / End-of-Flow Sync / Checkpoint — new):** Transition `checkpoint.current_stage` out of
   `"completed"` and flush logs before `finish_flow` re-enters Stage 4/5 (`PR #308` stuck at `"completed"` for
   `15.3+ min` while re-entry ran).
4. **Bean `0446` (high, Flow / Stage 3 / Admission — new):** Skip Stage 3 union touch-set admission on
   `DECISION_DECOMPOSED` (`SPLIT`) parent plans so children admit on their own narrow touch sets, and ban bare directory
   prefixes (`apps/sandbox-executor/tests/`) in intent scopes (`0407` blocked `60.75 min` in window).
5. **Extended `0407` & `0442` (critical/high, Stage 4/5):** Documented `#308`'s `0b986f9b`/`11721091` full re-reviews +
   `15.3+ min` ledger-only `End-of-flow sync` re-review (`0407`), plus Stage 5 `2.60 min` calibration and `2×30 s` Stage
   2 `npx prettier` timeouts (`0442`).
6. **Bean `0447` (normal, Pipeline / CI / Stress — new) & Extended `0412` (normal, Timing/Logging):** Share one child
   unit run or split `Workspace survival` into two CI jobs (`#308` `364 s` vs `365.5 s` on 4-vCPU runner), and close
   remaining unlogged/unmeasured gaps (`0412`). _(Plus existing `0371` critical for the `16/19` `CONFLICTING/DIRTY`
   ledger-only queue cascade.)_

#### 4. Examined and Found in Order

- **Timing Gate (`PR #278`):** Zero timing-gate CI failures occurred across all `128` workflow runs (`20` heads) in
  `02:54Z–03:54:45Z`.
- **Bookkeeping Gate (`PR #272`):** On `PR #308`, `5cb52b05` (`03:26:07Z`) and `de6441ff` (`03:38:05Z`, `48.6 s`
  `final_head_ci`) ran only `CodeQL`/`Analyze`, skipping all `Unit`/`Stress`/`Integration`/`Hygiene`/`Docker` runs when
  their parent heads had passing CI.
- **Self-doc merge queue (`PR #285`–`#289`):** All `5` pre-merge `Merge origin/main` CI runs passed `11/11` checks
  cleanly on first run (`6.95 min` median CI).

### 2026-11-25T02:54:00Z — Fifth-Merge Audit

- **Trigger:** fifth merge since `2026-11-25T00:28:00Z` (`holon-agentic-coder` PRs `#278`, `#280`, `#281`, `#283`,
  `#284`; `holon-coherence` last merged `#55` at `2026-11-24T12:44:47Z`, with `#56` open; `dev-env` `#41` open).
- **Last merged pull requests at audit time:**
  - `holon-agentic-coder`: `#284` (`e2e-self-doc`, merged `2026-11-25T02:47:53Z`)
  - `holon-coherence`: `#55` (`coherence-module-line-budget-all`, merged `2026-11-24T12:44:47Z`)
- **Beans created or extended:**
  - Created: `0442` (Stage 5 calibration invokes `npx --yes prettier` twice per run, consuming `~140 s` of `155 s` Stage
    5 work vs `64 ms` with direct local `prettier`), `0443` (Stage 4 pushes `chore(review): record review ledger rows`
    `9–12 s` after resolver/conflict-gate pushes, causing `5/5` cancelled CI heads and defeating `ci_bookkeeping_gate`),
    `0444` (Stage 5 `calibrate_sync._fetch_execution_branch` lacks transient retry on `Permission denied (publickey)`
    errors, halting `touch-set-self-doc`).
  - Extended: `0408` (`PR #306` `2c31f500` failed `Test - Hygiene` solely on engine-generated
    `executions/E-1795571328-ANA-G4N.md`, the window's only CI failure), `0433` (`9/9` new flows launched
    `00:28Z–02:25Z` halted on `gh pr diff 283` HTTP 406; `workspace-survival` idled `181.5 min`), `0422` (`11/13` active
    checkpoints ran with `allow_overlap=True`), `0407` (`PR #300` full `6.0 min` re-review after `main` merge +
    `PR #306` full `7.6 min` re-review after `E-*.md` Prettier fix), `0403` (verified `22` bookkeeping heads dropped
    `Unit`/`Stress` to `9–23 s` and `final_head_ci` to `0.82 min` median, while `9–12 s` double pushes negated skipping
    on `5` heads), `0412` (`12/14` flows unlogged in `todo/flow-*.log`, wrapper pre-flight untimestamped,
    `calibrate.end_time` vs `elapsed_seconds` divergence).

#### 1. Per-Step Timing Table (`2026-11-25T00:28:00Z` to `2026-11-25T02:54:07Z`)

Measured across `13` active checkpoints (`split-cli-init-modules`, `touch-set-self-doc`, `in-flight-pr-files-fallback`,
`decomposition-rule-self-doc`, `preflight-self-doc`, `review-report-self-doc`, `agent-defaults-self-doc`,
`github-ci-self-doc`, `git-refs-self-doc`, `github-pr-merge-self-doc`, `github-misc-self-doc`,
`workspace-survival-job-parallel`, `no-unneeded-full-review`), `2` `todo/flow-*.log` files with post-`00:28Z` entries
(`flow-timing-gate-judges-test-time.log`, `flow-workspace-survival-job-parallel.log`), and GitHub PR/CI/commit records
(`hac#278`, `#280`, `#281`, `#283`, `#284`, `#285`–`#307`, `coh#56`, `dev-env#41`):

| Step                                                                     | Count | Median (min) | Longest (min) | Longest in                                  |
| :----------------------------------------------------------------------- | ----: | -----------: | ------------: | :------------------------------------------ |
| Pre-flight (credential probe, image check, worktree creation)            |     - | not measured |  not measured | wrapper lines untimestamped (`0412`)        |
| Stage 1: intent agent turn (`context.logs`)                              |     9 |         0.25 |          0.32 | `no-unneeded-full-review`                   |
| Stage 2: planner agent turn (`context.logs`)                             |    10 |         3.53 |          5.62 | `no-unneeded-full-review`                   |
| Stage 3: admission check (`context.logs`)                                |    19 |         0.60 |          1.13 | `review-report-self-doc`                    |
| Stage 3: refusal $\rightarrow$ resume wait (`9` 406 + `1` `#283` wait)   |    10 |         0.86 |        181.48 | `workspace-survival-job-parallel`           |
| Stage 3: executor agent turn (tool vs model split unlogged)              |     9 |         5.85 |          6.68 | `review-report-self-doc`                    |
| Stage 3: re-plan after touch-set breach                                  |     0 |            - |             - | none in window (`split-cli-init` pre-00:28) |
| Each push & conflict probe/merge of target                               |     - | not measured |  not measured | folded into surrounding stage (`0412`)      |
| Stage 4: empty-diff guard + PR create (`context.logs`)                   |     9 |         0.17 |          0.20 | `agent-defaults-self-doc`                   |
| Stage 4: reviewer ensemble turn (`3` reviewers; per-reviewer unlogged)   |    14 |         7.03 |          7.92 | `review-report-self-doc`                    |
| Stage 4: resolver turn (incl. push)                                      |     2 |         3.19 |          4.23 | `github-pr-merge-self-doc` (`#306`)         |
| Stage 4: ledger commit (`Consensus approval` $\rightarrow$ `Committed`)  |    11 |         0.12 |          0.13 | `agent-defaults-self-doc`                   |
| Stage 4: individual review iteration                                     |    14 |         7.14 |          8.03 | `review-report-self-doc`                    |
| Stage 4: full review stage (`10` in-win + `#296` spanning `00:28Z`)      |    11 |         7.65 |         47.58 | `split-cli-init-modules` (`#296`)           |
| CI registration wait (Stage 5 `final_head_ci`)                           |    16 |         0.28 |          0.30 | `decomposition-rule-self-doc` (`#300`)      |
| CI wait (Stage 5 `merged_head_ci`)                                       |     3 |         7.92 |          7.97 | `touch-set-self-doc` (`#298`)               |
| CI wait (Stage 5 `final_head_ci` after calibration push)                 |    13 |         0.82 |          1.81 | `split-cli-init-modules` (`#296`)           |
| Stage 5: calibration work + reconciliation + promotion (excl. CI waits)  |    13 |         2.58 |          2.65 | `timing-gate-judges-test-time` (`#278`)     |
| Stage 5: final-head check after CI settled                               |    13 |         0.10 |          0.17 | `timing-gate-judges-test-time` (`#278`)     |
| Idle: interrupted / failed Stage 4/5 $\rightarrow$ resume                |     2 |         1.37 |          1.37 | `decomposition-rule-self-doc` (`#300`)      |
| Wait: PR ready (last calibration) $\rightarrow$ maintainer merge (5 PRs) |     5 |       588.38 |        632.45 | `holon-agentic-coder#281`                   |
| GitHub: PR open $\rightarrow$ merged (`#278,#280,#281,#283,#284`)        |     5 |       638.73 |        648.33 | `holon-agentic-coder#281`                   |

Stage totals across in-window events (`00:28:00Z`–`02:54:07Z`; `no-unneeded-full-review` also stayed halted `12.45 min`
on real overlap at cutoff; `split-cli-init-modules` carried `0.66 h` pre-`00:28Z` Stage 4 work):

| Stage     | Total (h) | Working (h) | Waiting on CI (h) | Waiting on another flow (h) | Waiting on human (h) | Idle (h) |
| :-------- | --------: | ----------: | ----------------: | --------------------------: | -------------------: | -------: |
| intent    |      0.04 |        0.04 |              0.00 |                        0.00 |                 0.00 |     0.00 |
| plan      |      0.63 |        0.63 |              0.00 |                        0.00 |                 0.00 |     0.00 |
| execute   |      4.24 |        1.09 |              0.00 |                        3.02 |                 0.00 |     0.13 |
| review    |      1.73 |        1.71 |              0.00 |                        0.00 |                 0.00 |     0.02 |
| calibrate |      1.25 |        0.58 |              0.64 |                        0.00 |                38.88 |     0.02 |

- **Missing timing (`12/14` active flows unlogged in `todo/flow-*.log`):** only `flow-timing-gate-judges-test-time.log`
  and `flow-workspace-survival-job-parallel.log` contain post-`00:28Z` entries; wrapper pre-flight lines in the latter
  have no timestamps; `calibrate.end_time` precedes `publish_calibration` and `final_head_ci` wait (`0412`).
- **Stage 5 Prettier overhead (`~140 s` per flow):** profiling `flow-agent-defaults-self-doc` showed Python/git
  calibration + self-check + promotion takes `9.36 s`, while `_converge_report`'s two `npx --yes prettier` calls take
  `~140 s` (direct cached `prettier --check`: `0.064 s`; `0442`).

#### 2. Churn Counts (`2026-11-25T00:28:00Z` to `2026-11-25T02:54:07Z`)

- **CI pipeline runs:**
  - Across the **5 cadence merges** (`hac#278, #280, #281, #283, #284`, full PR lifetime): `35` CI heads (`210` workflow
    runs), of which **`23` (`65.7%`) were churn** (`15` bookkeeping, `8` `main`-merge, `12` code), with `5` failed heads
    and `8` cancelled heads (`#278`: 1, `#280`: 1, `#281`: 1, `#283`: 5).
  - Across **all CI heads in the window** (`17` `hac` PRs, `00:28Z–02:54Z`): `46` CI heads (`276` workflow runs), of
    which **`36` (`78.3%`) were churn** (`28` bookkeeping, `8` `main`-merge, `10` code), with `1` failed head (`PR #306`
    `2c31f500` `Test - Hygiene`) and **`5` cancelled heads** (`#296` twice, `#305` once, `#306` twice).
- **Review & Stage 3/5 churn:**
  - **HTTP 406 storm on `PR #283` (`0433`, `0422`):** `9/9` new flows launched `00:28Z–02:25Z` failed Stage 3 admission
    on `gh pr diff 283` (`>300 files`), forcing `9` manual `--allow-overlap` resumes (`11/13` active checkpoints carried
    `allow_overlap=True`), while `workspace-survival-job-parallel` idled `181.5 min` waiting for `#283` to merge.
  - **Stage 4 `9–12 s` double-push cancellations (`0443`):** every Stage 4 resolver or conflict-gate push (`b646d346`,
    `59d41deb`, `4ea64923`, `1a49bac5`, `4ba9ecf7`) was cancelled `8–51 s` later by
    `chore(review): record review ledger rows`, wasting `Docker Build` runs (`96–126 s`) and forcing full `6–9 min` CI
    on the ledger commit.
  - **Unnecessary full re-reviews (`0407`, `0408`):** `PR #300` re-reviewed `6.0 min` after a `DIRTY` ledger conflict
    with `#280`; `PR #306` failed `Test - Hygiene` on engine-generated `executions/E-1795571328-ANA-G4N.md` after 3/3
    `APPROVED` (`0/0/0`), costing a `4.2 min` resolver pass + `7.6 min` re-review.
  - **Transient Stage 5 SSH fetch halt (`0444`):** `touch-set-self-doc` failed Stage 5 at `00:30:27Z` on
    `Permission denied (publickey)` without retry (`1.37 min` stop/resume), then collided with `#278`'s merge
    (`7.97 min` `merged_head_ci` wait).
  - **Cross-PR `KB-failure-*.json` promotion sprawl (`0371`):** `6` feature PRs independently promoted `40` shared
    `holon-knowledge/kb/failure_modes/KB-failure-*.json` files into their PR diffs (`#296`: 21, `#305`: 7, `#297`: 4,
    `#300`: 3, `#292`: 3, `#306`: 2).
  - **Open PR backlog & merge-wait amplification:** `25` PRs (`hac#285`–`#307`, `coh#56`, `dev-env#41`) await human
    merge (`588.4 min` median wait on the 5 merged PRs; `8` `main`-merge CI heads triggered in window).

#### 3. Ranked Suggestions

1. **Bean `0442` (high, Flow / Stage 5 / Calibration — new):** Resolve local/cached `prettier` directly in
   `calibration.py:_converge_report` before falling back to `npx --yes prettier` (cuts Stage 5 calibration work from
   `~2.58 min` / `155 s` to `~0.2 min` / `10–12 s`, saving `~2.3 min` per flow / `~30 min` across `13` runs in this
   window).
2. **Bean `0443` (high, Flow / Stage 4 / CI Churn — new):** Eliminate the `9–12 s` double push between Stage 4
   resolver/conflict-gate pushes and `chore(review): record review ledger rows` (`loop.py:329,857`,
   `ledger_commit.py:135-155`), stopping self-inflicted CI cancellations (`5/5` cancelled heads in window) and restoring
   `ci_bookkeeping_gate` savings on post-resolver/post-merge ledger rows.
3. **Extended `0408` & `0407` (high/critical, Pipeline / Stage 4):** Recorded `PR #306`'s `Test - Hygiene` failure on
   engine-generated `executions/E-1795571328-ANA-G4N.md` (`0408`) and avoidable full re-reviews on `#300` (`6.0 min`)
   and `#306` (`7.6 min`) (`0407`).
4. **Extended `0433` & `0422` (high, Flow / Stage 3):** Recorded `9/9` new flows hitting `gh pr diff 283` HTTP 406,
   `181.5 min` wait on `workspace-survival`, and `11/13` flows running with `allow_overlap=True` (noting `PR #299`
   awaits merge).
5. **Bean `0444` (normal, Flow / Stage 5 — new):** Add bounded transient retry to
   `calibrate_sync._fetch_execution_branch` (`touch-set-self-doc` `00:30:27Z` `Permission denied (publickey)` halt).
6. **Extended `0403` & `0412` (high/normal, CI / Timing):** Recorded `ci_bookkeeping_gate` `9–23 s` skips across `22`
   clean bookkeeping heads (`0.82 min` median `final_head_ci`), `12/14` unlogged flows in `todo/flow-*.log`, and
   `calibrate.end_time` divergence (`0412`). Also documented `KB-failure-*.json` promotion sprawl (`40` files across `6`
   PRs) against `0371` (left untouched due to concurrent session edits).

#### 4. Examined and Found in Order

- **Timing Gate (`PR #278`, Bean `0404`/`0419`):** Merged `00:33:04Z`; **zero** timing-gate failures occurred across all
  `46` CI heads (`276` workflow runs) in `00:28Z–02:54Z`.
- **Bookkeeping Gate (`PR #272`, Bean `0403`):** `22` uncancelled post-Stage-3 bookkeeping heads skipped
  `Unit`/`Stress`/`Integration`/`Docker`/`Make` in `9–23 s`, holding Stage 5 `final_head_ci` waits to `48–65 s`
  (`0.82 min` median vs `7.92 min` on `merged_head_ci`).
- **Self-doc slice quality (`Bean 0153`):** `9` of `11` Stage 4 runs in the window (`#298`–`#304`, `#307`) passed
  3-reviewer consensus on **iteration 1 with `0/0/0` findings** (`7.0–8.4 min` Stage 4), and `#305` resolved its sole
  nit in `2.2 min`.

### 2026-11-25T00:28:00Z — Fifth-Merge Audit

- **Trigger:** fifth merge since `2026-11-24T12:59:00Z` (`holon-agentic-coder` PRs `#282`, `#272`, `#275`, `#276`,
  `#277`; plus decomposed child PR `#279` merged into `#283`'s plan branch; `holon-coherence` last merged `#55` at
  `12:44:47Z`, with `#56` open).
- **Last merged pull requests at audit time:**
  - `holon-agentic-coder`: `#277` (`ci-wait-fast-poll-and-early-fail`, merged `2026-11-25T00:18:17Z`)
  - `holon-coherence`: `#55` (`coherence-module-line-budget-all`, merged `2026-11-24T12:44:47Z`)
- **Beans created or extended:**
  - Created: `0438` (Stage 5 `counted_target_only_file` false positive on PR `#283` after merge commit `221f9d73`
    adapted `test_replan_request.py`), `0439` (Stage 4 resolver has no scope guard and edits unrelated files on
    timing-gate `FIND-CI` failures), `0440` (harness `.git/hooks/pre-commit` runs Prettier across unstaged working-tree
    `.md` files), `0441` (Stage 5 `final_head_ci` reports `unknown` on bookkeeping-gated / transient-probe heads).
  - Extended: `0433` (HTTP 406 recurred on `infra-helpers-self-doc` and `workspace-survival-job-parallel`;
    cross-referenced companion `0437`), `0412` (`19/24` flows unlogged, `split-cli-init-modules` missing `review`
    start/end, `+11:00` mixed into `Z` log timestamps, `calibrate.elapsed_seconds` vs `start_time..end_time`), `0407`
    (timing-gate `FIND-CI` re-reviews on `#276`/`#290`/`#292`, 3 approvals on `#292`, merge withdrawal on `#283`),
    `0408` (`PR #296` failed `Test - Hygiene` on engine-generated `executions/E-1795563737-ANA-G4N.md` and
    `Lint with Ruff`; `PR #289` failed hygiene), `0422` (`14/23` `hac` flows ran with `allow_overlap=True`).

#### 1. Per-Step Timing Table (`2026-11-24T12:59:00Z` to `2026-11-25T00:19:32Z`)

Measured across `24` active checkpoints (`23` `holon-agentic-coder` + `1` `holon-coherence`), `5` `todo/flow-*.log`
files with post-`12:59Z` entries (`ci-skip-bookkeeping-only-pushes`, `launcher-proxy-self-doc`,
`timing-gate-judges-test-time`, `unit-suite-slowest-tests-speedup`, `workspace-survival-job-parallel`), and GitHub
PR/CI/commit records (`hac#272`, `#275`–`#297`, `coh#55`–`#56`):

| Step                                                                   | Count | Median (min) | Longest (min) | Longest in                                   |
| :--------------------------------------------------------------------- | ----: | -----------: | ------------: | :------------------------------------------- |
| Pre-flight (credential probe, image check, worktree creation)          |     - | not measured |  not measured | missing wrapper timestamps (`0412`)          |
| Stage 1: intent agent turn (checkpoint)                                |    20 |          0.3 |           1.7 | `entrypoint-exec-self-doc`                   |
| Stage 2: planner agent turn (checkpoint)                               |    22 |          3.8 |          22.9 | `timing-gate-judges-test-time`               |
| Stage 3: admission check (`todo/flow-*.log` only; 22 unlogged)         |     1 |          0.1 |           0.1 | `timing-gate-judges-test-time`               |
| Stage 3: overlap wait / admission refusal (14/23 used `allow_overlap`) |     - | not measured |  not measured | 2 immediate HTTP 406 halts (`0433`, `0437`)  |
| Stage 3: executor agent turn (checkpoint, incl. local tests)           |    23 |          7.9 |          34.6 | `timing-gate-judges-test-time`               |
| Stage 3: re-plan after touch-set / entropy breach (2 flows)            |     - | not measured |  not measured | `split-cli-init-modules`, `end-of-flow-sync` |
| Each push & conflict probe/merge of target                             |     - | not measured |  not measured | folded into surrounding stage (`0412`)       |
| Stage 4: empty-diff guard + PR create/edit                             |     - | not measured |  not measured | not split in checkpoints (`0412`)            |
| Stage 4: reviewer ensemble turn (3 reviewers; per-reviewer unlogged)   |    10 |         24.5 |          56.9 | `unit-suite-slowest-tests-speedup` (`#275`)  |
| Stage 4: resolver turn (incl. push; 1 aborted `-6` pass ran 227.1m)    |     3 |          9.4 |          33.4 | `timing-gate-judges-test-time` (`#278`)      |
| Stage 4: ledger commit                                                 |     - | not measured |  not measured | not logged individually (`0412`)             |
| Stage 4: individual review iteration (log)                             |    12 |         26.6 |          56.9 | `unit-suite-slowest-tests-speedup` (`#275`)  |
| Stage 4: full review stage (checkpoint, all iters + CI/local tests)    |    19 |         17.0 |         122.9 | `timing-gate-judges-test-time` (`#278`)      |
| CI registration wait (`todo/flow-*.log`)                               |     8 |          0.3 |           3.0 | `unit-suite-slowest-tests-speedup` (budget)  |
| CI wait (Stage 5 `final_head_ci.ci_wait` in checkpoints)               |    16 |         11.9 |          30.0 | `timing-gate-judges-test-time` (budget)      |
| CI wait (`todo/flow-*.log`)                                            |     5 |          7.9 |          18.0 | `ci-skip-bookkeeping-only-pushes` (`#272`)   |
| Stage 5: calibration work + promotion + reconciliation (excl. CI)      |    19 |          0.3 |           2.6 | `config-env-self-doc` (+4 self-doc flows)    |
| Stage 5: final-head check after CI settled                             |     - | not measured |  not measured | folded into Stage 5 (`0412`)                 |
| Wait: PR ready (`last_calib`) $\rightarrow$ maintainer merge           |     6 |        132.5 |         615.0 | `holon-agentic-coder#277`                    |
| Idle: interrupted / stopped run $\rightarrow$ resume (`flow-*.log`)    |     7 |         21.7 |         393.4 | `ci-skip-bookkeeping-only-pushes` (`#272`)   |
| GitHub: PR open $\rightarrow$ merged (`#272,#275,#276,#277,#282,#279`) |     6 |        621.3 |         658.4 | `holon-agentic-coder#277`                    |

Stage totals across the `24` active checkpoints in the window (Stage 5 split into working vs `final_head_ci` wait;
inter-stage gaps/idle across unlogged flows `not measured`):

| Stage     | Total (h) | Working (h) | Waiting on CI (h) | Waiting on another flow (h) | Waiting on human (h) | Idle in logs (h) |
| :-------- | --------: | ----------: | ----------------: | --------------------------: | -------------------: | ---------------: |
| intent    |      0.13 |        0.13 |              0.00 |                        0.00 |                 0.00 |                - |
| plan      |      1.71 |        1.71 |              0.00 |                        0.00 |                 0.00 |                - |
| execute   |      3.34 |        3.34 |              0.00 |                not measured |                 0.00 |                - |
| review    |     10.44 |       10.44 |  incl. in working |                        0.00 |                 0.00 |             3.07 |
| calibrate |      3.37 |        0.28 |              3.09 |                        0.00 |                22.61 |             6.92 |

- **Missing timing (`19/24` active flows unlogged in `todo/flow-*.log`):** only `5` flows wrote post-`12:59Z` entries to
  `todo/flow-*.log`; `split-cli-init-modules` recorded `review: status=failed start=None end=None elapsed=1.161`;
  `todo/flow-unit-suite-slowest-tests-speedup.log` mixed `+11:00` container timestamps inside `[...Z]` lines (`0412`).
- **Bookkeeping-gate before/after (`PR #272` merged `21:10:12Z`):** Stage 5 `ci_wait` dropped from `11.9–30.0 min`
  before `21:10Z` to `0.3–1.9 min` (`16–112 s`) after `21:10Z`, and bookkeeping-only `Test - Unit` workflow runs dropped
  to `18–25 s`.

#### 2. Churn Counts (`2026-11-24T12:59:00Z` to `2026-11-25T00:19:32Z`)

- **CI pipeline runs:**
  - Across the **5 cadence merges** (`hac#282`, `#272`, `#275`, `#276`, `#277`): `47` CI heads in the window, of which
    **37 (79%) were churn** (`30` bookkeeping-only, `7` `main`-merge), with `6` failed heads (`3` `Workspace survival`,
    `2` `unit (macos-latest)` timing gate on `#276` bookkeeping commits, `1` `build` on `#282`).
  - Across **all 24 `hac` PRs + `coh#56` in the window**: `136` `hac` CI heads (`26` code, `20` `main`-merge, `90`
    bookkeeping) + `16` reruns = `152` `hac` runs, of which **126 (83%) were churn**, with `26` failed heads (`20` on
    bookkeeping/merge heads, `6` on code heads) and `1` failure on `coh#56` (`4` heads: `1` code, `3` bookkeeping).
- **Review & Stage 3/5 churn:**
  - `PR #276` (`launcher-proxy-self-doc`): 6 review iterations; `unit (macos-latest)` timing-gate failures on
    bookkeeping heads (`c1f20b9e`, `f5baea47`) triggered `FIND-CI-002` / `FIND-CI-004` and pushed resolver edits into 8
    out-of-scope files (`cli/__init__.py`, `config_env_report.py`, `scripts/pre_commit_check.py`, and 5 test files),
    causing `PR #296` (`split-cli-init-modules`) to collide in `cli/__init__.py` (`23:47:23Z`).
  - `PR #292` (`config-env-self-doc`): 7 review iterations (3 separate 3/3 approvals) across 30 commits (20 bookkeeping,
    4 `main`-merges) and out-of-scope resolver edits in `redaction.py`/`test_redaction.py`.
  - `PR #290` (`knowledge-self-doc`): 4 review iterations driven by `unit (macos-latest)` timing-gate `FIND-CI-002` /
    `FIND-CI-003` on bookkeeping heads (`9b4d2bd4`, `b15549be`), then `final_head_ci: unknown`.
  - `PR #283` (`resolve-conflicts-in-flow`): `221f9d73` merge adaptation caused consensus withdrawal (`e1e7150`) and a
    false-positive Stage 5 `counted_target_only_file` halt (`23:36:28Z`); PR #283's >300-file / >20k-line diff also
    blocked Stage 3 admission on `infra-helpers-self-doc` (`19:32:54Z`) and `workspace-survival-job-parallel`
    (`23:26:48Z`).
  - `PR #275` (`unit-suite-slowest-tests-speedup`): 9 review iterations total; hit `227.1 min` `-6` resolver abort +
    `94.0 min` idle on `monthly spend limit` (`0434`).
  - `PR #272` (`ci-skip-bookkeeping-only-pushes`): `393.4 min` idle before `calibrate` failed at `21:10:18Z` (`6 s`
    after PR #272 merged and deleted the remote branch, `0420`).

#### 3. Ranked Suggestions

1. **Bean `0439` (high, Flow / Architecture / Stage 4 — new):** Enforce a touch-set / scope boundary on Stage 4 resolver
   commits and filter out `CI Timing Gate` failures from `FIND-CI` resolver dispatch (prevents cross-PR collisions like
   `PR #276` $\rightarrow$ `PR #296`, silent test-budget weakening, and `9.4–33.4 min` wasted resolver turns +
   `26.6 min` re-reviews).
2. **Bean `0438` (high, Flow / Stage 5 — new):** Fix `target_only_paths` in `calibration_self_check.py` to stop using
   `git log --no-merges` so conflict-merge adaptations of `main`-added files (e.g. `PR #283` `221f9d73` on
   `test_replan_request.py`) do not trigger false-positive `counted_target_only_file` Stage 5 failures.
3. **Bean `0440` (high, Harness — new):** Scope `.git/hooks/pre-commit` Prettier checks to staged Markdown files only so
   concurrent sessions with unstaged `.md` edits do not block `git commit --only` in other sessions.
4. **Extended `0433` (high, Flow / Stage 3):** Added `infra-helpers-self-doc` (`19:32:54Z`) and
   `workspace-survival-job-parallel` (`23:26:48Z`) HTTP 406 Stage 3 admission halts on PR `#283` and cross-referenced
   companion `0437`.
5. **Extended `0407` & `0408` (critical/high, Flow / Pipeline):** Recorded timing-gate `FIND-CI` re-review churn on
   `#276`/`#290`/`#292` and merge withdrawal on `#283` in `0407`, plus engine-generated
   `executions/E-1795563737-ANA-G4N.md` Prettier hygiene failures on `PR #296` and `#289` in `0408`.
6. **Bean `0441` (normal, Flow / Stage 5 — new):** Fix `ci_final_head.py` so transient non-`github_cli` poll hiccups
   retry within budget and bookkeeping-gated final heads classify cleanly instead of reporting `unknown` (`PR #290`,
   `PR #293`).
7. **Extended `0412` & `0422` (high/normal, Flow / Harness):** Recorded `19/24` unlogged flows, missing `review` failure
   timestamps (`PR #296`), mixed `+11:00`/`Z` log timestamps, `calibrate` elapsed mismatch in `0412`, and `14/23`
   `allow_overlap=True` flows in `0422`.

#### 4. Examined and Found in Order

- **PR #272 (`ci_bookkeeping_gate`, Bean `0403`):** Once merged at `21:10:12Z`, bookkeeping-only `Test - Unit` runs
  dropped to `18–25 s` and Stage 5 `final_head_ci` waits dropped from `11.9–30.0 min` to `0.3–1.9 min` on clean flows
  (`git-flow-self-doc`, `local-llm-self-doc`, `claude-auth-self-doc`, `config-env-self-doc`).
- **PR #277 (`ci_wait` fast-poll & early-fail, Bean `0399`):** Merged cleanly at `00:18:17Z`, capping CI wait polling at
  `15 s` instead of `120 s` backoff.
- **Self-doc slice flows (`PR #280`, `#281`, `#282`, `#284`–`#288`, `#291`, `#294`, `#295`):** `11` slice PRs passed
  Stage 4 consensus in `1–2` iterations with `7.6–17.0 min` review stages when not hit by timing-gate `FIND-CI` or
  `main`-merge churn.

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
