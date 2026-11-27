# Self-Improvement Audit Log

This log is written by the self-improvement audit described in `.agents/self-improvement-audit.md`; the newest entry is
first.

## Entries

### 2026-11-27T11:54:15Z — Fifth-Merge Audit

- **Trigger:** fifth merge (`7` merges in `holon-agentic-coder` since `2026-11-27T10:56:02Z` at
  `holon-agentic-coder#411` and `holon-coherence#73`):
  - `holon-agentic-coder` (`7`): `#412` (`11:40:08Z`), `#414` (`11:40:26Z`), `#416` (`11:41:06Z`), `#417` (`11:41:23Z`),
    `#418` (`11:41:40Z`), `#419` (`11:41:58Z`), `#422` (`11:42:42Z`). Open: `#413` (`0611`, halted `CF-0055`), `#415`
    (`0615`, `3/3 APPROVED` + `calibrate: ok`, `CLEAN`), `#420` (`0601`, halted `CF-0058`), `#421` (`0617`, halted
    `CF-0059`), `#423` (`0607`, in Stage 4 review).
  - `holon-coherence` (`0` at trigger baseline `52019174`; note `#76`–`#81` merged concurrently at `11:45:04Z–11:46:18Z`
    while this audit ran and remain queued for the next fifth-merge audit).
- **Last merged pull requests at audit baseline:** `Holon-Agentic-Coder/holon-agentic-coder#422` (`2a83e4cc7`);
  `Holon-Agentic-Coder/holon-coherence#73` (`52019174f`).
- **Coordinator failure ledger repeats (`CF-0056`–`CF-0059`, `4` new rows since `CF-0055`):**
  - `overlap-scheduling` (`2` new rows, `15` total — **repeat flagged high priority**): `CF-0056` (`0535` Stage 2
    widened into `flow/review/loop.py`, overlapping `#412`) and `CF-0057` (`0610` launched without reading `0216`'s
    `plans/*/P-*.md ## Touch Set`, hitting `flow/stages/plan.py`). `slot_keeper.py` only checks `queue.json`
    `kind=resume` entries rather than scanning all on-disk parked flow worktrees -> **new Bean `0628`** (extended
    `0610`).
  - `intent-scope` (`2` new rows, `16` total — **repeat flagged high priority**): `CF-0058` (`#420` `0601` omitted
    `tests/test_ci_bookkeeping_wiring.py` when adding `.github/workflows/test-self-doc-behavior.yml` -> extended `0546`,
    `0624`) and `CF-0059` (`#421` `0617` edited `flow/lazy_exports.py` and `flow/stages/calibrate.py` -> extended
    `0546`, `0624`). Inspecting `flow/review/resolver.py:112-135` and `entrypoint/review_loop.py:323-375` confirmed
    Stage 4's resolver prompt never receives the plan's Touch Set -> **new Bean `0627`**.
- **Premature merge & clean findings:**
  - **Premature mid-Stage-5 merge (`HAC #419`, `b366a559e`):** Merged at `11:41:58Z` (`33 s` after Stage 5 pushed
    `2bf82d86`) with `2` macOS unit checks still pending, **0 `_calibration.md` / Stage 5 reconciliation commits**, and
    checkpoint stranded at `stage: calibrate` -> extended **`0602`** so the readiness script gates on both completed CI
    and `P-*_calibration.md` on the PR head.
  - **Clean findings (examined and in order):** `6` of the `7` merged HAC PRs (`#412`, `#414`, `#416`–`#418`, `#422`)
    completed `3/3 APPROVED` + Stage 5 calibration with `0` docstrings added, `0` comments added, and `100%` Touch Set
    recall (`87.5%`–`100%` precision); `#418` (`0600`) cleanly recovered from its earlier `04:47Z` Stage 3 failure and
    shipped host-push retry + `execution_branch` preservation.
- **Per-flow churn summary (CI heads / total checks / review iterations / churn vs defect):**
  - Merged HAC PRs: `#412` `6 / 90 (12 canc) / 1 full + 1 scoped (0 churn, iter 1 quota resume)`; `#414`
    `4 / 60 (12 canc) / 2 full (0 churn, iter 1 quota resume)`; `#416` `3 / 45 (3 canc) / 1 full (0 churn)`; `#417`
    `5 / 75 (12 canc) / 1 full + 1 scoped (0 churn)`; `#418`
    `5 / 75 (12 canc, 1 fail) / 1 full + 1 scoped (0 churn, pre-reset fail)`; `#419`
    `6 / 78 (22 canc, 1 pend) / 1 full + 1 scoped (0 churn, merged mid-Stage-5)`; `#422`
    `3 / 45 (1 canc) / 1 full (0 churn)`.
  - Halted/open HAC PRs: `#413` `1 / 15 / 1 full (halted CF-0055)`; `#415`
    `4 / 60 (11 canc) / 2 full (CLEAN, awaiting merge)`; `#420` `1 / 16 (1 fail) / 1 full (halted CF-0058)`; `#421`
    `1 / 15 / 1 full (halted CF-0059, after 2 Stage 3 re-plans)`; `#423` in Stage 4 review (`9.8 min` Stage 3).
- **Per-step timing table (`>= 2026-11-27T10:35:00Z` across `15` checkpointed flows + `7` merged HAC PR timelines):**

| Step                                   | Count |    Median (s / min) |    Longest (s / min) | Category / Notes                                                           |
| :------------------------------------- | ----: | ------------------: | -------------------: | :------------------------------------------------------------------------- |
| Pre-flight (wrapper start -> Stage 1)  |     - |        not measured |         not measured | `0/14` active/completed flows wrote `todo/flow-*.log` (`0412`)             |
| Stage 1 (`INTENT`)                     |    10 |     17.0 s (0.28 m) |      28.0 s (0.47 m) | Working (`review-posting-transient-retry` max)                             |
| Stage 2 (`PLAN`)                       |    11 |    219.0 s (3.65 m) |     277.0 s (4.62 m) | Working (`stage5-fail-closed-calibrate` max)                               |
| Stage 3 admission — admitted           |    12 |     12.5 s (0.21 m) |      24.0 s (0.40 m) | Working (`stage5-fail-closed-calibrate` max)                               |
| Stage 3 (`EXECUTE` — succeeded)        |    10 |    294.5 s (4.91 m) |    938.0 s (15.63 m) | Working (`stage5-fail-closed-calibrate` max)                               |
| Stage 3 (`EXECUTE` — failed/re-plan)   |     4 |    143.5 s (2.39 m) |   1216.0 s (20.27 m) | Failure/re-plan (`stage5-fail-closed-calibrate` touch-set widen max)       |
| Execute end -> PR create               |     9 |     11.0 s (0.18 m) |      13.0 s (0.22 m) | Working (`self-doc-ast-behavior-gate` max)                                 |
| Stage 4 reviewer ensemble turn         |    13 |    295.0 s (4.92 m) |    628.0 s (10.47 m) | Working + CI (`stage5-fail-closed-calibrate` max; per-reviewer unmeasured) |
| Stage 4 resolver turn                  |     4 |    277.5 s (4.62 m) |     303.0 s (5.05 m) | Working (`stage5-fail-closed-calibrate` max; inner splits unmeasured)      |
| Stage 4 CI registration wait           |     9 |     17.0 s (0.28 m) |      18.0 s (0.30 m) | Waiting on CI (`hac-import-cycle-ratchet` max)                             |
| Stage 4 (`REVIEW` total)               |    10 |    499.0 s (8.32 m) |   1055.0 s (17.58 m) | Working + CI (`measure-ci-head-durations` max)                             |
| Stage 5 calibration work (excl. CI)    |     7 |     43.7 s (0.73 m) |      47.4 s (0.79 m) | Working (`hac-import-cycle-ratchet` max; `publish` split unmeasured)       |
| Stage 5 final-head CI wait             |     7 |    261.2 s (4.35 m) |     377.0 s (6.28 m) | Waiting on CI (`coherence-single-request` max)                             |
| Stage 5 (`CALIBRATE` total)            |     7 |    308.0 s (5.13 m) |     427.0 s (7.12 m) | Work + CI (`coherence-single-request` max)                                 |
| Idle between stop & resume             |     5 | 7831.0 s (130.52 m) | 17043.0 s (284.05 m) | Idle (`coherence-commit-trailer-check` max)                                |
| Human wait (calibration -> merge, HAC) |     7 |   1074.0 s (17.9 m) |    3564.0 s (59.4 m) | Waiting on human (`#414` max `59.4 m`; `#419` `0.9 m` mid-Stage-5)         |

- **Not measured:** `0/14` flows wrote `todo/flow-*.log` (`0412`), `6` merged HAC PRs lost local checkpoint logs upon
  post-merge pruning, per-reviewer / resolver-inner / Stage 5 `ci_reg_wait` & `publish_calibration` splits remain
  unlogged (`0412`), and per-stage/turn LLM token usage is unrecorded (**new Bean `0629`**).
- **Beans created:** **`0627`** (high: pass plan Touch Set to Stage 4 resolver prompt & reject out-of-set edits
  pre-commit), **`0628`** (high: pre-launch parked-worktree Touch Set guard across all on-disk flows), **`0629`**
  (normal: record per-stage & per-turn token usage and wall timings in checkpoints).
- **Beans extended:** **`0412`**, **`0531`**, **`0546`**, **`0602`**, **`0610`**, **`0611`**, **`0616`**, **`0624`**.
- **Architecture & source-code quality refresh
  ([docs/ecosystem-audit-report-2026-11.md](../docs/ecosystem-audit-report-2026-11.md), `hac@2a83e4cc7` vs `0d8d1249f`;
  `coherence@52019174f` baseline):**
  - **Overall scores:** **`holon-coherence` `7.9 / 10 (0.0)`** retains its lead over **`holon-agentic-coder`
    `7.5 / 10 (0.0)`** (`hac@2a83e4cc7` closed `0538`, `0594`, `0600`, `0618` and landed `0533`/`0608`/`0616` slices).
  - **HAC deltas (`0d8d1249f → 2a83e4cc7`):** Complexity `5.9→5.8 (-0.1)` (`run_review_loop` `CC=207→219`, `947/950L`),
    Clean Code `7.3→7.4 (+0.1)` (`#422` DRY unification), Testability `7.8→7.9 (+0.1)` (`#414` broad-except ratchet,
    `+7` test files / `+1,985` test LOC / `5,177` `test_*`), Error Handling `8.1→8.2 (+0.1)` (`#412`, `#414`
    `broad_except` `138→137`, `#418`), Observability `8.2→8.1 (-0.1)` (`#416` `553` KB entries vs `#419` missing
    `_calibration.md`, pending fragments `270→291`, `0` wrapper logs).

### 2026-11-27T10:56:02Z — Fifth-Merge Audit

- **Trigger:** fifth merge (`7` merges in `holon-coherence` since `2026-11-27T07:49:25Z` at `holon-agentic-coder#411`
  and `holon-coherence#65`; `0` new merges in `holon-agentic-coder`):
  - `holon-coherence` (`7`): `#69` (`08:02:58Z`), `#71` (`08:06:25Z`), `#68` (`08:08:11Z`), `#75` (`08:27:33Z`), `#74`
    (`08:36:52Z`), `#72` (`09:29:55Z`), `#73` (`09:29:55Z`). Open: `#66` (`CF-0044`), `#67` (`0623`), `#70` (`CF-0054`).
  - `holon-agentic-coder` (`0`): latest merged remains `#411` (`07:40:19Z`). Open: `#408` (`CF-0043`), `#412` (`0618`,
    `3/3 APPROVED` + `calibrate: ok` `10:48:47Z`), `#413` (`0611`, halted `CF-0055`), `#414` (`0616`, `3/3 APPROVED` +
    `calibrate: ok` `10:47:40Z`), `#415` (`0615`, `3/3 APPROVED` + `calibrate: ok` `10:46:16Z`).
- **Last merged pull requests at audit time:** `Holon-Agentic-Coder/holon-agentic-coder#411`;
  `Holon-Agentic-Coder/holon-coherence#73` (`5201917`).
- **Coordinator failure ledger repeats (`CF-0047`–`CF-0055`, `9` new rows since `CF-0046`):**
  - `intent-scope` (`2` new rows, `14` total): `CF-0053` (`0527` slice 1 & `#67` halted on `test_module_budgets` /
    `test_complexity_baseline` ratchet deadlock -> `0623`) and `CF-0055` (`HAC #413` Stage 4 resolver halted with
    `touch_set_violation` on `.github/workflows/README.md` -> extended `0546`, new **`0624`**).
  - `overlap-scheduling` (`2` new rows, `13` total): `CF-0050` (`0599` parked on older `0216` checkpoint) and `CF-0052`
    (`0619` Stage 2 widened into `flow/review/loop.py` overlapping live `0618` -> extended `0610`).
  - `resume-checkpoint` (`2` new rows, `3` total): `CF-0051` (`0216` resume adopted stale `E-1795726868` ->
    `lint_failed`) and `CF-0054` (`Coherence #70` Stage 4 resolver halted with `touch_set_violation` on `sse_tap.py:79`
    after `#64` merged -> new **`0624`**).
  - `conflict-handling` (`1`), `post-merge` (`1`), `brief` (`1`): `CF-0048` (`#70` post-`#64` mismatch), `CF-0047`
    (`flash_lite` post-merge omissions), `CF-0049` (`0617` missing `## Acceptance Criteria` from `new_bean.py` -> new
    **`0626`**).
- **Clean findings (examined and in order):**
  - **`exit code 3` quota isolation:** `6` concurrent flows (`#414`, `#415`, `0538`, `0617`, `0621`, `0623`) hit
    `gemini-4-neon` `quota (resets 2026-11-27T10:30Z)` at `08:42–08:46Z` and exited cleanly with zero branch corruption;
    `#412`, `#414`, and `#415` resumed cleanly post-reset to `3/3 APPROVED` + `calibrate: ok` (idle-stall improvement
    logged as **`0625`**).
  - **Coherence CI stability:** `0` cancelled CI runs across all `10` Coherence PRs (`#66`–`#75`), `100.0%` touch-set
    precision/recall and `0` docstrings/comments across all `7` Coherence calibration reports (`#68,#69,#71–#75`).
  - **Stage 4 scope gate (`0596`):** `#410` gate immediately caught out-of-scope resolver edits on `#70` and `#413`.
- **Per-flow churn summary (CI heads / total runs / review iterations / churn vs defect):**
  - Coherence (`#67`–`#75`): `#68` `3 / 15 / 1 full (0 churn)`; `#69` `3 / 15 / 1 full (0 churn)`; `#71`
    `3 / 15 / 1 full (0 churn)`; `#75` `3 / 18 / 1 full (0 churn)`; `#74`
    `8 / 56 / 2 full + 1 scoped (2 target-merge churn, 2 carry-overs)`; `#72`
    `5 / 29 (1 fail) / 1 full (2 target-merge churn, 2 carry-overs; Stage 5 27.0 m)`; `#73`
    `4 / 23 / 1 full (2 target-merge churn, 2 carry-overs; Stage 5 17.6 m)`; open `#67`
    `3 / 16 (3 fail) / 2 full (halted 0623)`; open `#70`
    `5 / 29 (3 fail) / 1 full + 1 carried resolver (2 target-merge churn, halted CF-0054)`.
  - HAC (`#412`–`#415` open): `#412`
    `6 / 54 (9 canc) / 1 full + 1 scoped (0 churn, iter 1 resolver idle exit 3 -> approved on resume)`; `#413`
    `1 / 9 / 1 full (halted CF-0055 touch_set_violation)`; `#414`
    `4 / 36 (8 canc) / 2 full (0 churn, iter 1 quota exit 3 -> approved on resume)`; `#415`
    `4 / 36 (8 canc) / 2 full (0 churn, iter 1 quota exit 3 -> approved on resume)`.
- **Per-step timing table (`>= 2026-11-27T07:15:00Z` checkpoint events across `24` active/completed/parked flows):**

| Step                                        | Count |    Median (s / min) |   Longest (s / min) | Category / Notes                                                                 |
| :------------------------------------------ | ----: | ------------------: | ------------------: | :------------------------------------------------------------------------------- |
| Pre-flight (wrapper start -> Stage 1)       |     - |        not measured |        not measured | `0` `todo/flow-*.log` files written in `07:29Z–10:49Z` (`0412`)                  |
| Stage 1 (`INTENT`)                          |    13 |     17.0 s (0.28 m) |     21.0 s (0.35 m) | Working (`stage4-carried-finding-clean-tree` max)                                |
| Stage 2 (`PLAN`)                            |    15 |    202.0 s (3.37 m) |    341.0 s (5.68 m) | Working (`stage5-fail-closed-calibrate` max)                                     |
| Stage 3 admission — admitted                |    14 |     12.0 s (0.20 m) |     21.0 s (0.35 m) | Working (`hac-architecture-audit-kb-entries` max)                                |
| Stage 3 admission — refused (per poll)      |     3 |      8.0 s (0.13 m) |      9.0 s (0.15 m) | Overlap wait (`stage4-main-baseline-guard` max)                                  |
| Stage 3 (`EXECUTE` — succeeded)             |     6 |    339.0 s (5.65 m) |   832.0 s (13.87 m) | Working (`stage4-carried-finding-clean-tree` max)                                |
| Stage 3 (`EXECUTE` — failed/refused)        |    11 |     49.0 s (0.82 m) |  1273.0 s (21.22 m) | Failure/refusal (`stage5-fail-closed-calibrate` re-plan breach max)              |
| Execute end -> PR create                    |     6 |     13.0 s (0.22 m) |     14.0 s (0.23 m) | Working (`hac-import-cycle-ratchet` max)                                         |
| Stage 4 reviewer ensemble turn              |     8 |    336.0 s (5.60 m) |   678.0 s (11.30 m) | Working + CI (`coherence-translation-sse-finish` max; per-reviewer unmeasured)   |
| Stage 4 resolver turn                       |     5 |    128.0 s (2.13 m) |    313.0 s (5.22 m) | Working (`promote-ledger-debounce-alert` max; inner splits unmeasured)           |
| Stage 4 carried-finding resolver            |     2 |    187.0 s (3.12 m) |    213.0 s (3.55 m) | Working (`coherence-translation-sse-finish` max)                                 |
| Stage 4 CI registration wait                |     3 |      2.0 s (0.03 m) |      2.0 s (0.03 m) | Waiting on CI                                                                    |
| Stage 4 (`REVIEW` total)                    |    11 |    263.0 s (4.38 m) |   931.0 s (15.52 m) | Working + CI (`coherence-dashboard-html-asset` max)                              |
| Stage 5 calibration work (before CI wait)   |     4 |     17.0 s (0.28 m) |     18.0 s (0.30 m) | Working (`stage4-carried-finding-clean-tree` max)                                |
| Stage 5 merged-head CI wait                 |     1 |    357.0 s (5.95 m) |    357.0 s (5.95 m) | Waiting on CI (`coherence-translation-sse-finish` failed head `1d7726f9`)        |
| Stage 5 final-head CI reg wait              |     3 |     18.0 s (0.30 m) |     18.0 s (0.30 m) | Waiting on CI (`hac-broad-except-ratchet` max)                                   |
| Stage 5 final-head CI wait                  |     4 |    221.3 s (3.69 m) |    360.7 s (6.01 m) | Waiting on CI (`hac-broad-except-ratchet` max)                                   |
| Stage 5 (`CALIBRATE` total, incl. `#72–74`) |     6 |    451.2 s (7.52 m) |  1619.1 s (26.99 m) | Work + CI (`coherence-abtest-leaks-deps` `#72` max; `#73` `1056.1 s` / `17.6 m`) |
| Idle between stop & resume                  |     8 | 6648.5 s (110.81 m) | 7571.0 s (126.18 m) | Idle (`gemini-4-neon` `10:30Z` quota reset wait across `6` flows)                |
| Human wait (approval -> merge, Coherence)   |     7 |   1398.0 s (23.3 m) |  6204.0 s (103.4 m) | Waiting on human (`#75` `6.0 m`, `#74` `9.4 m`, `#72` `103.4 m`)                 |

- **Not measured:** `100%` of flows (`07:29Z–10:49Z`) wrote `0` `todo/flow-*.log` files, leaving wrapper pre-flight,
  per-reviewer latencies inside Stage 4 ensembles (`8` runs), resolver inner splits (`5` runs), and Stage 5
  `publish_calibration` split unmeasured (extended **`0412`**).
- **Beans created:** **`0624`** (high: Stage 4 `touch_set_violation` rollback & bounded re-plan recovery), **`0625`**
  (high: Stage 3/4 quota `exit code 3` automatic ladder step-down), **`0626`** (normal: `new_bean.py` scaffold
  `## Acceptance Criteria`).
- **Beans extended:** **`0383`** (`#72`/`#73`/`#74` Stage 5 CI-wait overruns), **`0412`** (`0` wrapper logs in
  `07:29Z–10:49Z`), **`0528`** (`#75` closed `3x normalize_payload` & unused SQLite index), **`0546`** (`CF-0055`
  `.github/workflows/README.md` companion gap), **`0610`** (`CF-0052` `0619` Stage 2 `loop.py` expansion), **`0620`**
  (Coherence pending fragments `27→48`), **`0622`** (`#69` fixed `wire_log.py:69`, `4→3` silent `pass`, `34→33` broad
  catches).
- **Architecture & source-code quality refresh
  ([docs/ecosystem-audit-report-2026-11.md](../docs/ecosystem-audit-report-2026-11.md), `hac@0d8d1249f` unchanged,
  `coherence@52019174f` vs `ce39bf34d`):**
  - **Overall scores:** **`holon-coherence` `7.9 / 10 (+0.2)`** widened its lead over **`holon-agentic-coder`
    `7.5 / 10 (0.0)`** after closing `0524` (`#75`) and `0563` (`#74`) plus 5 resilience/hygiene PRs
    (`#68,#69,#71–#73`).
  - **Coherence deltas (`ce39bf34d → 52019174f`):** Clean Code `7.1→7.3 (+0.2)`, Self-Doc `8.2→8.3 (+0.1)`, Testability
    `7.8→8.0 (+0.2)` (`+3` test files / `+792` LOC / `1,019` `test_*`), Error Handling `7.6→7.9 (+0.3)` (`broad_except`
    `34→33`, silent `pass` `4→3`), Security `7.4→8.4 (+1.0)` (`0524` closed), Observability `7.6→7.7 (+0.1)` (`0563`
    closed, `0` `index.json`, `48` pending fragments remain under `0620`).

### 2026-11-27T07:49:25Z — Fifth-Merge Audit

- **Trigger:** fifth merge (`14` merges across both target repos since `2026-11-27T05:19:35Z` at
  `holon-agentic-coder#405` and `holon-coherence#57`):
  - `holon-agentic-coder` (`6`): `#403` (`07:24:46Z`), `#406` (`07:36:44Z`), `#407` (`07:37:02Z`), `#409` (`07:38:45Z`),
    `#410` (`07:39:41Z`), `#411` (`07:40:19Z`). Open: `#408` (`self-doc-tests-49`).
  - `holon-coherence` (`8`): `#58` (`07:45:52Z`), `#59` (`07:46:29Z`), `#60` (`07:46:29Z`), `#61` (`07:46:47Z`), `#62`
    (`07:47:33Z`), `#63` (`07:47:51Z`), `#64` (`07:48:09Z`), `#65` (`07:48:26Z`). Open: `#66` (`CF-0044`, unreviewed).
    (`#57` merged `05:17:48Z`, prior audit; included in flow metrics: `14.8 min` span, `1` iter, `15` runs all green.)
- **Last merged pull requests at audit time:** `Holon-Agentic-Coder/holon-agentic-coder#411`;
  `Holon-Agentic-Coder/holon-coherence#65`.
- **Coordinator failure ledger repeats (`CF-0039`–`CF-0046`, 8 new rows since `CF-0038`):**
  - `overlap-scheduling` (`5` new rows, `11` total): `4` were Stage 2 plan expansion outside `intent.scope` (`CF-0039`
    `0590`, `CF-0041` `0567`, `CF-0042` `0563`, `CF-0045` `0524` slice 2 — extended bean `0610`); `1` was a parked flow
    blocking resume (`CF-0046`, `flow-references-github-issues` idle since `2026-11-26` blocking `0590` — extended bean
    `0544`).
  - `verification` (`2` new rows, `6` total): `CF-0043` (`#408` carried-finding loop + false readiness claim) and
    `CF-0044` (Coherence `#66` bypassed failed Stage 3/4 via `--from-stage calibrate` — bean `0617`).
  - `readiness-check` (`1` new row, `6` total): `CF-0040` (`#410` halted on broken `origin/main` `wisdom.py` budget).
- **Root-cause findings & new beans:**
  - **Bean `0617` (new, high):** `--from-stage calibrate` skips Stage 4 approval gate
    (`"Merged-head CI gate skipped: no Stage 4 approval recorded"`) and exited `calibrate: ok` on unreviewed
    `holon-coherence#66` (`reviews: []`, `comments: []`, `execute` failed on `module_budgets.json`, `CF-0044`).
    `hac#410` also merged with `reviews: []` and no calibration commit.
  - **Bean `0618` (new, high):** `#408` (`self-doc-tests-49`, `CF-0043`) pre-iteration carried-finding resolver crashed
    `6` consecutive resumes (`06:05Z`–`06:32Z`, `~24 min`) on `nothing to commit, working tree clean` and
    committed/pushed `6` empty `chore(review): record review ledger rows` heads (`c778c1633`..`be2a5e799`, `54` wasted
    CI runs) without starting a review.
  - **Bean `0619` (new, high):** `#404`/`#405` merged at `05:13Z` with `Test - Hygiene` failing on `wisdom.py`
    (`386 > 350`), poisoning `origin/main` for `2 h 11 min` until `#403` merged (`07:24:46Z`). Stage 4/5 synced broken
    `main`, withdrew `#408`'s `3/3` `abcd50c7` approval (`9773e1d15`), inflicted `8` extra `FIND-CI` churn iterations
    (`~90+ min`) across `#403`/`#406`/`#407`/`#409` despite `3/3 APPROVED`, halted `#410` (`CF-0040`), and forced `#411`
    to split `wisdom.py` out-of-scope.
- **Per-flow churn summary (CI heads / total runs / review iterations / churn vs defect):**
  - HAC (`#403,#406,#407,#408,#409,#410,#411`): `#403` `10 / 90 (29 canc, 5 fail) / 5 iters (1 defect, 4 churn)`; `#406`
    `12 / 100 (36 canc, 4 fail) / 5 iters (1 defect, 4 churn)`; `#407`
    `12 / 100 (43 canc, 3 fail) / 5 iters (1 defect, 4 churn)`; `#408` (open)
    `12 / 100 (15 canc, 12 fail, 2 queued) / 2 iters + 8 carried-resolver runs (1 defect, 7+ churn; `6179f55ef`dirtied 36`plans/*_calibration.md`, failing `lint-md`on`b734520fa`)`;
    `#409` `12 / 100 (36 canc, 5 fail) / 5 iters (1 defect, 4 churn)`; `#410`
    `6 / 54 (18 canc, 7 fail) / 1 iter (0 reviews at merge)`; `#411` `5 / 45 (3 canc, 0 fail) / 1 iter (0 churn)`.
  - Coherence (`#57`–`#66`, `0` cancelled runs across all 10 PRs): `#57` `3 / 15 / 1`; `#58` `5 / 30 / 2 (1 defect)`;
    `#59` `5 / 25 (1 fail) / 2 (1 defect)`; `#60` `3 / 15 / 1`; `#61` `3 / 15 / 1`; `#62` `5 / 25 / 2 (1 defect)`; `#63`
    `7 / 35 (4 fail) / 3 (2 defect/CI)`; `#64` `4 / 20 / 2 (1 defect)`; `#65` `5 / 25 / 2 (1 defect)`; `#66` (open,
    `CF-0044`) `2 / 10 / 1 (0 reviews posted, `127.0.0.1:8080` reset)`.
- **Per-step timing table (`30` active/completed/parked flows across HAC and Coherence):**

| Step                                     | Count |  Median (s / min) |  Longest (s / min) | Category / Notes                                                             |
| :--------------------------------------- | ----: | ----------------: | -----------------: | :--------------------------------------------------------------------------- |
| Pre-flight (wrapper start -> Stage 1)    |    35 |       not logged* |        not logged* | Engine `0.0 s / max 3.0 s`; wrapper pre-flight lines unmeasured (`0412`)     |
| Stage 1 (`INTENT`)                       |    35 |   16.0 s (0.27 m) |   303.0 s (5.05 m) | Working (`coherence-promote-ledger` max)                                     |
| Stage 2 (`PLAN`)                         |    37 |  174.0 s (2.90 m) |   420.0 s (7.00 m) | Working (`flow-references-github-issues` max)                                |
| Stage 3 admission — admitted             |    35 |   13.0 s (0.22 m) |   100.0 s (1.67 m) | Working (`self-doc-tests-51` max)                                            |
| Stage 3 admission — refused (per poll)   |    78 |    5.0 s (0.08 m) |    35.0 s (0.58 m) | Overlap wait (`flow-references-github-issues` max)                           |
| Stage 3 overlap wait (wall per parked)   |     5 |           290.7 m |           1125.1 m | Wait on other flow (`flow-references-github-issues` `68` refusals)           |
| Stage 3 (`EXECUTE` — succeeded)          |    23 |  296.0 s (4.93 m) | 1006.0 s (16.77 m) | Working (`self-doc-tests-49` max)                                            |
| Stage 3 (`EXECUTE` — failed/refused)     |    88 |    5.0 s (0.08 m) | 1149.0 s (19.15 m) | Refusal/failure (`flow-references-github-issues` max)                        |
| Execute end -> PR create                 |    19 |   11.0 s (0.18 m) |    13.0 s (0.22 m) | Working (`self-doc-tests-45` max)                                            |
| Stage 4 reviewer ensemble turn           |    44 |  437.5 s (7.29 m) | 2102.0 s (35.03 m) | Working + CI wait (`self-doc-tests-46` max; per-reviewer split unmeasured)   |
| Stage 4 resolver turn                    |    15 |  397.0 s (6.62 m) |   580.0 s (9.67 m) | Working (`self-doc-tests-51` max; inner pytest/push split unmeasured)        |
| Stage 4 carried-finding resolver         |     9 |  223.0 s (3.72 m) |   532.0 s (8.87 m) | Working (`self-doc-tests-49` max; 6x clean-tree crash on `#408`)             |
| Stage 4 (`REVIEW` total)                 |    33 | 786.0 s (13.10 m) | 3358.0 s (55.97 m) | Working + CI (`self-doc-tests-46` max)                                       |
| Stage 5 calibration work (excl. CI wait) |    15 |   50.0 s (0.83 m) |  864.0 s (14.40 m) | Working (`self-doc-tests-45` max)                                            |
| Stage 5 CI registration wait             |     - |      not measured |       not measured | Not logged separately (`0412`)                                               |
| Stage 5 final-head CI wait               |    15 |  147.7 s (2.46 m) |  928.2 s (15.47 m) | Waiting on CI (`self-explaining-markdown-coverage` max)                      |
| Stage 5 (`CALIBRATE` total)              |    17 |  293.0 s (4.88 m) | 2001.0 s (33.35 m) | Work + CI (`self-doc-tests-49` max failed on CI timeout)                     |
| Idle between stop & resume               |    99 |   64.0 s (1.07 m) |           645.62 m | Idle (`admission-remote-in-flight` max)                                      |
| Human wait (approval -> merge)           |    13 |      96.3 m (HAC) | 221.6 m (`coh#57`) | Waiting on human (Coherence `#58–#65` open `37–109 m` before `07:45Z` sweep) |

- **Not measured:** wrapper pre-flight, `stage5_ci_reg_wait`, per-reviewer latencies inside ensembles, resolver inner
  splits, hand pre-merge syncs, and `todo/flow-*.log` for `10/10` newer Coherence flows (extended `0412`).
- **Examined and extended (not duplicated):** `0408` (`#408` `6179f55ef` repo-wide Prettier breaking `lint-md` on 36
  historical plans), `0412` (missing Coherence logs & unmeasured steps), `0424` (Coherence `#66` `127.0.0.1:8080`
  consensus-posting reset without retry), `0544` (`CF-0046` parked `flow-references-github-issues` blocking `0590`),
  `0602` (`#404`/`#405` merged with failing `hygiene` + pending-CI merges + `#410` `reviews=0`), `0610` (`CF-0039`,
  `CF-0041`, `CF-0042`, `CF-0045` Stage 2 scope creep), `0613` (`3/3 APPROVED` printed with `CHANGES_REQUESTED` on
  `FIND-CI` + `target merge 0` in `tests-51`).
- **Examined and confirmed covered by existing beans:** `0612` (Claude org spend limit hit `self-doc-tests-45/46/48/51`
  at `04:48–04:50Z`), `0609` (all `6` merged HAC PRs had hand `Merge branch 'main'` commits seconds before merge),
  `0601`/`0603` (`#403,#406,#407,#409` per-slice scanner tests and identical titles), `0596` (`#410` merged).
- **Beans created:** `0617`, `0618`, `0619`, plus architecture/code-quality refresh beans `0620` (Coherence: drain 27
  pending ledger fragments / configure `HOLON_LEDGER_BOT_TOKEN`), `0621` (Coherence: CI package import-cycle ratchet),
  and `0622` (Coherence: replace 4 silent `except Exception: pass` catches and ratchet broad catches).
- **Beans extended:** `0408`, `0412`, `0424`, `0544`, `0602`, `0610`, `0613`, plus `0527` (`commands <-> container`
  `4 <-> 3` from `#63`, `TYPE_CHECKING` `reduction_passes -> payload_cleaner` from `#61`), `0530` (`*_self_doc.py` `10`
  files / `1,202` LOC; `0` `TestCase`), `0588` (`#58` landed), and `0611` (`270` pending HAC fragments).
- **Architecture & source-code quality refresh
  ([docs/ecosystem-audit-report-2026-11.md](../docs/ecosystem-audit-report-2026-11.md), `hac@0d8d1249f` vs `5c0a557cc`,
  `coherence@ce39bf34d` vs `c26a0c1`):**
  - **Overall scores:** `holon-coherence` **7.7 / 10 (+0.4)** reclaimed the lead over `holon-agentic-coder` **7.5 / 10
    (+0.1)**.
  - **10-aspect scorecard (HAC / Coherence, deltas vs `5c0a557cc` / `c26a0c1`):**
    1. Clean Architecture & Layer Boundaries: `6.6` / `7.6 (-0.1)` (`#63` added `commands <-> container` `4 <-> 3`)
    2. Modularity, Cohesion & File Sizing: `7.4 (+0.1)` / `7.6 (+0.1)` (HAC `wisdom.py` split `>350L` `21→20`; Coherence
       `providers/registry.py` & `reduction_passes.py`)
    3. Complexity & Control Flow: `5.9` / `8.0` (`run_review_loop` `CC=207`; Coherence max `CC=24`)
    4. Clean Code & Idiomatic Python: `7.3` / `7.1 (+0.1)` (Coherence `98.6%` return-typed, `0` `TestCase`)
    5. Intention-Revealing & Self-Doc Code: `8.1 (+0.1)` / `8.2` (HAC test docstrings `1,089→1,057`, `src/` `# why:`
       `581/663`; Coherence `0`/`0`)
    6. Extensibility & Plug-in Seams: `6.8` / `7.7 (+0.4)` (Coherence `#61` `ReductionPass` `Protocol`)
    7. Testability & Verification Quality: `7.8 (+0.1)` / `7.8 (+0.8)` (Coherence `#64` `tflow`/`HTTPServer` wire tests;
       `todo/test-suite-audit-2026-11-26.md` `8,311` cases / `45,157` git spawns / quadratic `mktemp` mapped to `0405`,
       `0491`)
    8. Error Handling, Resilience & Failure Modes: `8.1` / `7.6 (+0.6)` (Coherence `#64` SSE carry-buffer & incremental
       UTF-8, `broad_except` `35→34`; HAC `broad_except` `137→138`)
    9. Security, Isolation & Secret Hygiene: `8.4` / `7.4 (+1.9)` (Coherence `#59` `0525`, `#58` `0564`, `#63` `0524`
       slice 1)
    10. Observability, Provenance & Config: `8.2` / `7.6 (+0.2)` (Coherence `0539`/`0614` closed, `27` pending fragments
        remain (`0620`); HAC `270` pending fragments (`0611`); `todo/flow-time-audit-2026-11-26.md` timing gaps folded
        in)

### 2026-11-27T05:19:35Z — Fifth-Merge Audit

- **Trigger:** fifth merge (`15` merges across both target repos since `2026-11-27T04:43:40Z` at
  `holon-agentic-coder#383` and `holon-coherence#56`):
  - `holon-agentic-coder` (`14`): `#365` (`05:05:08Z`), `#374` (`05:06:17Z`), `#375` (`05:06:55Z`), `#376`
    (`05:07:30Z`), `#377` (`05:08:05Z`), `#378` (`05:08:41Z`), `#379` (`05:09:58Z`), `#381` (`05:10:32Z`), `#386`
    (`05:11:09Z`), `#387` (`05:11:27Z`), `#388` (`05:11:45Z`), `#391` (`05:12:24Z`), `#404` (`05:13:02Z`), `#405`
    (`05:13:20Z`).
  - `holon-coherence` (`1`): `#57` (`05:17:48Z`, `coherence-planner-touch-set`, bean `0598`, `14.8 min` flow time, `1`
    review iteration, `7/7` CI green, `217.7 min` human wait, no pre-merge main merge).
- **Last merged pull requests at audit time:** `Holon-Agentic-Coder/holon-agentic-coder#405`;
  `Holon-Agentic-Coder/holon-coherence#57`.
- **Coordinator failure ledger & operational repeats:** No new rows added to `.agents/ledger/coordinator-failures.jsonl`
  since `CF-0038` (`04:23:55Z`). Repeats observed in logs and flagged high priority:
  - `todo/slot-keeper.log` hit `live=10` again at `04:43:15Z` and `04:47:09Z` (repeat of `CF-0027`, exceeding cap `8`),
    went silent after `04:47:09Z` (`25+ min` gap vs `60 s` rule, repeat of `CF-0024`), and launched
    `self-doc-tests-45..51` on `claude-agent` instead of `AGENTS.md` default `antigravity-agent / gemini-4-neon`
    (extended bean `0592`).
  - Post-merge runner leak (`CF-0021` pattern): `self-doc-tests-47` (`#404`) kept running in Stage 5 past its
    `05:13:02Z` merge, re-triggering cancelled CI runs `7` times (`05:12:53Z`–`05:13:19Z`, `4` after merge) until killed
    manually (extended bean `0420`).
- **Scope creep past `intent.scope`:** `4` of `6` non-`0153` PRs (`#374`, `#375`, `#376`, `#378`) changed `24` code
  files outside `intent.scope` (`#374`: `8 -> 35` plan paths / `14` extra; `#376`: `3 -> 16` plan paths / `6` extra
  incl. hub docs; `#378`: `5 -> 8` plan paths / `3` extra; `#375`: `1` extra). Bean `0596` only checks against the plan
  touch set; Stage 2 widening needs its own guard: bean `0610`.
- **`Promote Ledger` silent no-op & backlog:** `origin/main` now holds `252` files in `holon-knowledge/ledger/pending/`;
  `.github/workflows/promote-ledger.yml` exits green in `2 s` (`HOLON_LEDGER_BOT_TOKEN` unset), while `15/20` recent
  burst runs were `cancelled`: bean `0611`.
- **Model spend-limit cascade:** `self-doc-tests-51` (`04:48:57Z`), `48` (`04:49:18Z`), `45` (`04:50:20Z`) all hit
  Claude's org monthly spend limit; `51` re-probed `claude-agent` at `05:11:15Z` before switching to `gemini-4-neon`:
  bean `0612`.
- **Review loop observability & churn accounting:** `[Review Loop]` terminal summaries printed
  `Non-defect churn: target merge 0` on all `14` merged PRs even where calibration reports recorded `2` (`#374`,
  `#375`), and `self-doc-tests-46` logs printed only `Reviewer 1: APPROVED` while container verdict returned
  `CHANGES_REQUESTED`: bean `0613`.
- **Timing highlights across 22 HAC flows in window (`14` merged + `8` active/halted):**
  - `pre_flight` (n=21): median `5.0 s`, max `8.0 s` (work).
  - `stage1_intent` (n=20): median `18.0 s`, max `50.0 s` (work).
  - `stage2_plan` (n=22): median `200.5 s`, max `474.0 s` (`#365`) (work).
  - `stage3_admission_refusal` (n=43): median `6.0 s`, max `1149.0 s` (`flow-references-github-issues`, `41` runs /
    `1460.4 min` wall) (overlap wait / sync).
  - `stage3_execute` (n=19): median `646.0 s`, max `1006.0 s` (`self-doc-tests-49`) (work).
  - `stage4_review_total` (n=20): median `1096.0 s` (`18.3 min`), max `6177.0 s` (`#365`) (work + CI wait);
    `review_reviewer_turn` (n=41): median `410.0 s`, max `2102.0 s` (`self-doc-tests-46`); `review_resolver_turn`
    (n=17): median `331.0 s`, max `900.0 s`.
  - `ci_reg_wait` (n=20): median `1.5 s`, max `18.0 s`; `ci_wait` (n=13): median `114.1 s`, max `670.8 s` (`#405`).
  - `stage5_calibrate_total` (n=12): median `185.0 s`, max `2311.0 s` (`#405`, `38.4 min` vs `10 min` budget, incl.
    `stage5_merged_head_ci_wait` `1595.0 s` + `final head CI` `670.8 s`; `#365` failed/skipped; `#404` merged mid-Stage
    5).
  - `human_wait_to_merge` (n=12): min `39.0 s` (`#405`), median `10427.5 s` (`173.8 min`), max `12323.0 s` (`205.4 min`,
    `#376`); `idle_between_runs` (n=54): median `64.0 s`, max `29962.0 s`.
  - **Not measured:** per-reviewer individual times inside ensembles, resolver inner split (edit vs local pytest/lint vs
    push), Stage 2/3/5 sub-step splits, `slot-keeper`/`harness-scribe` activity after `04:47Z`/`04:50Z`, and post-`#376`
    sharded `unit (macos-latest)` durations (all sharded runs queued or cancelled before finishing; pre-`#376` unsharded
    ran `422 s–485 s`). Covered by existing beans `0412` and `0594`.
- **Examined and confirmed against existing beans (not duplicated):** `0383` (`#405` Stage 5 `38.4 min` overrun), `0596`
  (`diff-stays-in-intent-scope` in Stage 2), `0600` (`host-push-retry-record-branch` failed Stage 3 execute at
  `04:47:27Z`), `0601`/`0603`/`0608` (all `8` `0153` PRs `#379..#405` keep per-slice scanner test copies, shared
  truncated titles/empty counts, and deleted `78` reason-keyword `#` lines), `0602`/`0609` (all `14` HAC PRs merged with
  fresh `Merge branch 'main'` commits and queued/cancelled head CI, incl. `#404` `10` cancelled + `4` queued).
- **Beans created:** `0610`, `0611`, `0612`, `0613`.
- **Beans extended:** `0420`, `0592`.

### 2026-11-27T04:43:40Z — Fifth-Merge Audit (light)

- **Trigger:** fifth merge (`holon-agentic-coder` #396 `04:33:40Z`, #393 `04:34:20Z`, #392 `04:34:56Z`, #390
  `04:35:35Z`, #389 `04:36:24Z`, #385 `04:37:02Z`, #384 `04:37:40Z`, #380 `04:38:35Z`, #382 `04:39:11Z`, #383
  `04:39:44Z`: ten merges in six minutes, confirmed from gh).
- **Last merged pull request at audit time:** `Holon-Agentic-Coder/holon-agentic-coder#383`; `holon-coherence#56`
  unchanged.
- **Deleted reason comments (focus 1):** about 148 removed comment lines read as reasons across nine slices (heuristic,
  bodies report none); no restore slice exists. Bean 0608.
- **#380 scope escape (focus 2):** calibration shows recall 0.625; `failure_classification.py`,
  `flow/github/stage5_test_failure.py` and `flow/lazy_exports.py` were outside the intent scope (the lazy_exports change
  is one added line). No park or conflict from it found in the window; covered by 0596 (gate) and 0543 (derive
  lazy_exports); no new bean.
- **Heads moving (focus 3):** not only #392: all ten had a merge-from-main commit 26 to 60 s before merge, after reviews
  0.7 to 2 h old. Bean 0609 (0372 and 0602 cover parts only).
- **Install races (focus 4):** no new occurrence in the evidence; 0595 unchanged.
- **New tools (focus 5):** stamp.py, harness_commit.py, new_bean.py, staged validation and slot_keeper.py landed in
  `b98d6da` (15:41 local) and are referenced from the rules; this audit used new_bean.py (ids 0608, 0609 after another
  agent took 0607). Beans 0600 to 0606 were written before it landed, by hand. Use of harness_commit and slot_keeper in
  a run is **not measured** (no log yet).
- **Beans created:** `0608`, `0609`.

### 2026-11-27T04:33:33Z — Fifth-Merge Audit

- **Trigger:** fifth merge (`holon-agentic-coder` #371 `00:57:33Z`, #372 `01:13:53Z`, #373 `01:16:57Z`, #402
  `04:26:41Z`, #401 `04:27:31Z`, #397 `04:28:20Z`, #395 `04:29:30Z`, #399 `04:30:21Z`, #400 `04:31:09Z`, #398
  `04:32:02Z`: ten merges).
- **Last merged pull requests at audit time:** `Holon-Agentic-Coder/holon-agentic-coder#398`; `holon-coherence#56`
  unchanged.
- **Coordinator ledger (CF-0031 to CF-0038):** repeats flagged high priority: `intent-scope` x3 more (CF-0031, 0033,
  0034; seven since CF-0028), `readiness-check` x2 (CF-0032, 0035), `overlap-scheduling` (CF-0037, fifth row), and the
  CF-0036 rule (short timeout, background) broken again as CF-0038 two hours later: bean 0605. Two rows share id
  CF-0028: bean 0606.
- **CI at merge (focus 1):** #395, #397, #399, #400, #401 show checks still pending at 04:32Z (merged 04:26Z to 04:31Z,
  about 10 min after head push); #373 shows all complete now, its merge-time state is **not measured**. No failed check
  on any of the ten; one review each. Bean 0602 (per-head CI block in the readiness report, merge-time snapshot).
- **0153 slices (focus 2):** #401 rewrote both `# Lazy:` import comments as `# why:` and added 16 `# why:` lines, so
  reasons are kept there; no deletion of reasons found. But each slice adds its own 93-line scanner test (token and
  string checks, copy of the gate): beans 0601 (duplicate mechanism, no behaviour check beyond the suite). PR titles are
  identical and truncated, bodies boilerplate with no counts; 85 percent of added lines are bookkeeping files:
  bean 0603.
- **Slot keeper (focus 3):** launches 13 (01:17Z) to 36 (03:32Z), mostly 0153; queue never held a harness bean. Slice
  PRs are disjoint packages, all open slice PRs MERGEABLE, so conflict risk is low. 0590 (critical), 0596, 0592, 0579,
  0581, 0600 all still todo: bean 0604. Log cadence 4 to 12 min against the 60 s rule (01:49 to 02:01, 03:00 to 03:11,
  03:22 to 03:32): evidence for existing bean 0592; live fell to 3 at 04:08Z with five queued.
- **Scribe and keeper as agents (focus 4):** one duplicate driver (CF-0037, `live=9` at 03:32Z) and a keeper restart at
  03:41Z; cadence gaps above; evidence added to 0592 in this entry, not duplicated. Commits are not measured for stalls
  (no per-commit scribe log).
- **Install races (focus 5):** bean 0595 updated 04:31Z with evidence; no new bean.
- **Timing:** slice PR lead time (create to merge) 21 to 54 min (#402 21 min, #395 54 min); per-step times other than
  these are **not measured** (bean 0412 and 0594 cover).
- **Examined, in order:** beans 0591 to 0600 not duplicated; 0597 covers N/A agent/model, not titles.
- **Beans created:** `0601`, `0602`, `0603`, `0604`, `0605`, `0606`.

### 2026-11-27T00:57:23Z — Fifth-Merge Audit

- **Trigger:** fifth merge (`holon-agentic-coder` #361 `00:05:38Z`, #362 `00:28:06Z`, #366 `00:29:24Z`, #364
  `00:31:39Z`, #360 `00:55:13Z`; #363 just after).
- **Last merged pull requests at audit time:** `Holon-Agentic-Coder/holon-agentic-coder#360`; `holon-coherence#56`
  unchanged.
- **Coordinator ledger (CF-0023 to CF-0030):** repeats flagged high priority: `intent-scope` x4 (CF-0025, 0028, 0029,
  0030), `overlap-scheduling` x4 (CF-0023, 0024, 0026, 0027). The CF-0024 rule (poll every 60 s) and CF-0026 rule
  (open-PR overlap check) were broken again within the hour.
- **Partial deliveries:** #361, #366, #364 (and #362, half of 0563) delivered part of their beans. The 0589 check is not
  enough: `--bean` optional, skipped on resume, a one-shared-token match passes, and exclusions are free text. The
  keeper excluded all three remaining items of 0532 ("queued as separate intents") although only one sibling intent
  exists: misuse, and split beans (0558 in four intents) can only pass per-intent checks through exclusions. Bean 0591.
- **Slot utilisation:** `todo/slot-keeper.log` shows 00:42:22Z live=8, then 00:53:37Z live=4: an 11-min gap against the
  60 s rule, six queued intents unlaunched with no recorded reason, and a stale `launched=` field. Bean 0592.
- **macOS unit cost:** 0400 and 0404 remain in-progress; final heads of #360 to #366 show the macOS jobs at 0.2 to 0.3
  min. Intermediate-head durations **not measured**. Bean 0594.
- **Assumptions design (0590):** nine gaps (completeness, outcome unknown, stale pins, exclusions, rollout, pr_question
  answers, scoring, size, leak scan). Bean 0593.
- **Coordinator errors in briefs today:** CF-0025 to CF-0030, all intent-scope or overlap; root cause is hand-written
  intents, covered by 0590.
- **Examined, in order:** merged PRs had one review each; the final-head CI is green on all five; beans 0578 to 0590 not
  duplicated.
- **Beans created:** `0591`, `0592`, `0593`, `0594`.

### 2026-11-26T23:51:36Z — Fifth-Merge Audit

- **Trigger:** fifth merge (`holon-agentic-coder` #353 `23:01:29Z`, #358 `23:23:01Z`, #357 `23:44:54Z`, #359
  `23:50:00Z`; #344 merged earlier in the window).
- **Last merged pull requests at audit time:** `Holon-Agentic-Coder/holon-agentic-coder#359`
  (`review-env-child-suite-contract`); `holon-coherence#56` unchanged.
- **Coordinator ledger (CF-0014 to CF-0022):** repeats flagged high priority: `brief` x6 over the ledger (CF-0012 to
  0015, 0018, 0019), `verification` x4, `readiness-check` x3, `bookkeeping` x3.
- **Hook gaps:** working tree vs staged and whole-tree blocking are covered by 0577. The PreToolUse matcher covering
  only `Bash` (not the REPL shell) was only a side note in 0566 and 0577: new bean 0578.
- **Self-explaining after #357:** #358 (merged before the gate) added three docstrings and a comment; #359 (after) added
  none, 3 `# why:` comments. #357's 22 triple-quoted lines are test fixtures. Blind window for in-flight PRs: bean 0582.
- **Invented timestamps:** cause is hand-typed time fields; check detects only at commit. Helper: bean 0579.
- **Slots:** created-to-merged times: #353 102 min, #357 50 min, #358 14 min, #359 36 min; #358, #357, #359 merged
  within 27 min, so three slots freed at once and post-merge/reinstall serialise behind them. Idle per slot is **not
  measured** (existing beans 0545, 0412, 0576).
- **Coordinator errors in briefs:** wrong slug (CF-0019), editing a staged shared file (CF-0022), shared-index sweeps:
  beans 0580, 0581.
- **Examined, in order:** #359 passed the gate cleanly; CF-0020 check now enforced and the current working-tree
  timestamps are valid.
- **Beans created:** `0578`, `0579`, `0580`, `0581`, `0582`.

### 2026-11-26T22:59:59Z — Fifth-Merge Audit

- **Trigger:** fifth merge (`holon-agentic-coder` #352 `22:31:45Z`, #354 `22:32:39Z`, #355 `22:33:28Z`, #356
  `22:56:12Z`, #351 `22:56:30Z`); #350 `21:04:13Z` examined as the regression source.
- **Last merged pull requests at audit time:** `Holon-Agentic-Coder/holon-agentic-coder#351`
  (`single-runner-per-checkpoint`); `holon-coherence#56` unchanged. #357 (self-explaining gate) open.
- **Coordinator ledger:** repeats flagged: `brief` x4 (CF-0012 to CF-0015), `readiness-check` x2 (CF-0003, CF-0006),
  `bookkeeping` x2, `verification` x2.
- **#350 regression:** CI and review ran the suite in a plain environment; the env overlay only bites under the review
  loop's child pytest run. Three flows halted (beans 0547, 0548, fixed by #354).
- **Self-explaining invariant:** all 6 PRs added docstrings (107 opener lines) and about 325 non-`# why:` `#` lines
  (upper bound; includes markdown headings). #357 covers code languages, diff-scoped, but fails open without a merge
  base and reports no counts.
- **Subagent breaches today:** `git stash`, `--no-verify`, `git add -A`, main-worktree measuring; `--no-verify` is in no
  harness rule file.
- **Not measured:** time lost per resolver halt; per-step timing of flows #351 to #356 (beans 0412, 0496).
- **Examined, in order:** #352, #355, #356 each merged in 1 flow with no resolver halt recorded.
- **Beans created:** `0556`, `0557`, `0558`, `0559`.

### 2026-11-26T21:10:00Z — Fifth-Merge Audit

- **Trigger:** fifth merge (`holon-agentic-coder` #347 `20:57:28Z`, #342 `20:58:25Z` commit, #346 `21:02:00Z`, #348
  `21:02:43Z`, #349 `21:03:27Z`).
- **Last merged pull requests at audit time:** `Holon-Agentic-Coder/holon-agentic-coder#349`
  (`kb-wisdom-deterministic-files`, merged `2026-11-26T21:03:27Z`); `holon-coherence#56` unchanged. #350 open and
  mergeable.
- **Hub file `flow/lazy_exports.py`:** named in 3 Stage 3 refusals on #342 and 1 on a parked flow; 4 flows parked about
  29 flow-hours in total; 4 execute discards today for editing it outside the touch set (bean 0543).
- **Parked flows blocking each other:** `admission-remote-in-flight` behind parked `module-budget-default-350`;
  `module-budget-default-350` behind the just-resumed `single-runner-per-checkpoint` (bean 0544).
- **Backfill picks:** 4 of 5 flows parked at first Stage 3; pick decisions are not logged, so idle slot cost is **not
  measured** (bean 0545).
- **Main-push CI:** #346 gate present on all 5 workflows from `aa085c38`. On the three pushes of the 21:02 to 21:03
  burst (`aa085c38`, `46a1185b`, `2c865160`) hygiene skipped its JSON and markdown checks, but unit, integration and
  stress ran in full (Bookkeeping gate succeeded, did not skip); the runs overlapped as designed by 0461 (per-SHA
  groups). No pure merge-origin/main push has occurred since #346, so its skip is not yet confirmed; #337 behaviour
  unchanged since the 13:40Z entry. Recheck on the next such push.
- **WB add/add after #349:** no PR has merged after #349 yet; #349 and #350 file lists contain no `WB-heuristic` file.
  Not yet confirmed; recheck after the next merge.
- **Not measured:** per-step timing of parks, admission waits and idle slots (beans 0412, 0496, 0545).
- **Beans created:** `0543`, `0544`, `0545`.

### 2026-11-26T13:40:00Z — Fifth-Merge Audit

- **Trigger:** fifth merge (`holon-agentic-coder` #341 `12:58:39Z`, #334 `13:01:37Z`, #340 `13:04:23Z`, #343
  `13:04:41Z`, #345 `13:32:07Z`).
- **Last merged pull requests at audit time:** `Holon-Agentic-Coder/holon-agentic-coder#345`
  (`resume-adopts-unrecorded-branch`, merged `2026-11-26T13:32:07Z`); `holon-coherence#56` unchanged.
- **Inputs:** flow logs of the five flows and of the parked `module-budget-default-350` and
  `single-runner-per-checkpoint`, `gh pr view` file lists, gate decisions in the main-push unit jobs (#334, #340, #343,
  #345), commit authors in the shared repository, `.git/config`, `git worktree list`.
- **Admission and parking:** 4 refusals on 11-26 are about hub paths and one wide open PR (#342, 34 files, 79 min open);
  `module-budget-default-350` parked on it, `single-runner-per-checkpoint` parked 3 times. Structural fix: trial merge
  instead of path overlap, plus auto-resume (beans 0520, 0523). 0519 got today's state.
- **Conflicts after merge-queue merges:** #340 and #343 were rerun with `--from-stage review` 21 and 33 s before they
  merged, restarting a full review with "last reviewed head unknown" and orphaning processes (bean 0522).
- **KB add/add:** 3 of 5 merges touch `WB-heuristic-84a6ddeb.json` (a counter-bearing wisdom entry); bean 0517 extended
  with the cause and the fix on main.
- **Git identity:** leaked since at least 2026-11-20; 210 host-side commits carry the agent identity (bean 0518
  extended).
- **Main-push gates:** #333 in order; #337 skips (#345, 19 s) but #334, #340 and #343 ran in full because the head job
  was still running (bean 0521).
- **Beans created:** `0520`, `0521`, `0522`, `0523`. **Extended:** `0517`, `0518`, `0519`.
- **Timing (PR open to merge; commits / posted reviews):** #341 58 min (19 / 1); #334 138 min (31 / 2); #340 71 min (17
  / 1); #343 40 min (18 / 1); #345 34 min (15 / 1); median 58 min, longest 138 min. Stage splits (working, CI,
  other-flow wait, human, idle) per step are **not measured**.
- **Not measured:** per-step times of reruns and parked waits (beans 0412, 0496 still open).

### 2026-11-26T12:20:00Z — Fifth-Merge Audit

- **Trigger:** fifth merge (`holon-agentic-coder` #332 `10:55:07Z`, #333 `10:51:16Z`, #336 `11:34:34Z`, #335
  `12:04:42Z`, #339 `12:05:00Z`, #337 and #338 `12:06:00Z`).
- **Last merged pull requests at audit time:** `Holon-Agentic-Coder/holon-agentic-coder#338` (`settings-token-off-argv`,
  merged `2026-11-26T12:06:00Z`); `holon-coherence#56` unchanged.
- **Inputs:** `gh run list` and job logs for the 9 main pushes since 10:51Z, intent files against PR file lists (#332,
  #333, #335 to #339), `todo/flow-no-unneeded-full-review.log`, admission lines of the flow logs of 11-26, bean 0436 and
  its flow log.
- **#333 per-SHA concurrency:** in order; no cancelled main run after 10:51Z, all 9 pushes completed green.
- **#337 tree gate:** one main push since (`5440e92`), `decision=RUN rule=main-push-tree-mismatch`, full runs. Three
  merges in 80 s each ran a full CI set (about 25 runner-minutes). Bean 0514.
- **Scope escapes:** #332, #335, #337, #338 changed unlisted files; #333, #336, #339 exact; with the earlier audit 7 of
  13 flows (bean 0508 extended, keep high). 0407 children lost about 67 min of discarded Stage 3 turns (bean 0414
  extended).
- **0407 decomposed flow (04:06Z to 11:43Z+):** per child 46, 84, 80, 91 and 87 min; 21 child review iterations (2, 4,
  4, 6, 5) plus 4 parent, about 284 min of review; approval withdrawn at 11:29:45Z by a ledger-only head and Stage 4
  restarted (bean 0513 extended with the table). Step-level times still not measured (0412, 0496).
- **Backfill pickers:** none of the 11-26 flows parked on an overlap since 04:06Z (every Stage 3 admission read
  "overlaps no flow in flight"); 5 flows plus `ledgers-sorted-chronologically` ran together. Risk of 0436 now running:
  bean 0515.
- **Beans created:** `0514` (coalesce a burst of main pushes), `0515` (ledger reorder lands against every merge,
  resolvers undo it). **Extended:** `0508`, `0513`, `0414`.
- **Examined and in order:** #333 concurrency; #337 gate fails safe (full run on mismatch, no error); #335 and #339
  matched or nearly matched scope and were approved in few iterations.

### 2026-11-26T10:50:00Z — Fifth-Merge Audit

- **Trigger:** fifth merge (`holon-agentic-coder` #325 `09:25:03Z`, #327 `09:38:33Z`, #326 `09:51:19Z`, #329
  `09:54:27Z`, #331 `10:37:55Z`, #330 `10:39:00Z`).
- **Last merged pull requests at audit time:** `Holon-Agentic-Coder/holon-agentic-coder#330` (`pr-url-without-gh-hints`,
  merged `2026-11-26T10:39:00Z`); `holon-coherence#56` unchanged.
- **Inputs:** flow logs `todo/flow-<slug>.log` of the six flows, GitHub job times for `main` pushes (unit, survival),
  intent files against PR file lists, `todo/flow-time-audit-2026-11-26.md`, `todo/test-suite-audit-2026-11-26.md`.
- **Per-flow measurements** (review iterations / pipeline heads / commits; 0 failed unit runs in all): #325 3 / 8 / 19;
  #326 9 / 14 / 22 (7 iterations at 3/3 APPROVED blocked by hygiene); #327 2 / 7 / 17 (plus a Stage 3 to Stage 2 round
  trip, about 33 min); #329 1 / 3 / 9; #330 2 / 5 / 13; #331 3 / 7 / 15. Step-level times for pre-flight, pushes, merges
  and CI waits remain **not measured** (beans 0412, 0496).
- **CI saving on main** (medians before/after #323): macOS unit 560 to 445 s, ubuntu unit 238 to 171 s, Workspace
  survival 268 to 269 s (no change).
- **Beans created:** `0508` (intent scope guessed by hand, 3 of 6 flows), `0509` (verify CI saving on main after a
  performance flow; survival unchanged), `0510` (main-push CI re-runs everything for already-tested trees).
  **Extended:** `0497`, `0502`, `0403`, `0447`.
- **Examined and in order:** #329 approved in one iteration with an exact scope match; no unit CI failure on any PR
  head; no reviewer finding left unresolved at merge.

### 2026-11-26T08:55:00Z — Fifth-Merge Audit

- **Trigger:** fifth merge (`holon-agentic-coder` #314 `04:02:07Z`, #319 `06:11:39Z`, #317 `07:50:13Z`, #320
  `08:46:12Z`, #321 `08:47:03Z`, #323 `08:47:39Z`; child PRs #310-#313 already counted in the `03:50Z` entry).
- **Last merged pull requests at audit time:** `Holon-Agentic-Coder/holon-agentic-coder#323`
  (`tests-fewer-git-worktree-exec`, merged `2026-11-26T08:47:39Z`); `holon-coherence#56` unchanged since the previous
  entry.
- **Inputs:** `todo/flow-time-audit-2026-11-26.md` and `todo/test-suite-audit-2026-11-26.md` (their beans 0478-0496 not
  duplicated); GitHub reviews and workflow runs for the six PRs; `todo/flow-module-line-budget-all-packages.log`.
- **Per-PR measurements (GitHub):** reviews approving 3/3 / workflow runs (success, failure, cancelled): #314 1 / 30
  (24, 0, 6); #319 1 / 42 (31, 0, 11); #317 1 (after 12 loop iterations) / 100 (70, 14, 16); #320 2 / 66 (43, 3, 20);
  #321 2 / 66 (45, 3, 18); #323 1 / 30 (21, 2, 7). Review-loop timing of #317: iterations 1-9 cover 05:16:53Z-06:22:10Z
  (65 min) and all 9 were blocked by one unfixable-by-code hygiene failure; ensemble about 3.7 min per iteration (log).
  Step-level timing for the other five flows is **not measured** at step level in this audit (logs for #314/#319 stage
  steps are covered by the flow time audit and bean 0412; `flow-tests-fewer-git-worktree-exec.log` stayed empty, bean
  0496).
- **Beans created:** `0497` (review loop re-runs the ensemble on a CI failure the resolver reports as not fixable in
  code; #317 about 85 min), `0498` (a unit test measures the live tree against the live budget file; failed
  #320/#321/#323 in 9 jobs after #317 merged), `0499` (calibration report records CI runs, review iterations and churn
  class per flow).
- **Examined and in order:** #323 reached 3/3 in one iteration with the template-repo test change (git processes -35.7
  percent, 40 percent target honestly recorded as missed); #314 (+10,112 lines, 210 files) and #319 approved in one
  iteration; #320/#321 second approvals trace to 0493/0494, not new beans; the `gh event listen` hint still appears in
  every review body (0427); stray `=2026-11-24T08:00:00Z` still untracked (0465).

### 2026-11-26T03:50:00Z — Fifth-Merge Audit

- **Trigger:** fifth merge (`7` target-repo merges since `2026-11-25T22:49:00Z`: `holon-agentic-coder` `#309`
  `22:51:23Z`, `#308` `00:03:10Z`, `#310` `00:38:28Z`, `#311` `02:02:27Z`, `#312` `02:48:42Z`, `#313` `03:30:27Z`;
  `holon-coherence` `#56` `22:57:30Z`; plus `thomashan/dev-env` `#43` `00:03:54Z` and `#42` `03:46:21Z`, and closed
  `#44` `23:28:48Z`).
- **Last merged pull requests at audit time:**
  - `Holon-Agentic-Coder/holon-agentic-coder#313` (`feat(add): Add .github/workflows/promote-ledger.yml`, merged
    `2026-11-26T03:30:27Z`; `#314` open in Stage 4)
  - `Holon-Agentic-Coder/holon-coherence#56` (`coherence-final-self-doc`, merged `2026-11-25T22:57:30Z`)
  - `thomashan/dev-env#42` (`tmux-focus-events-on`, merged `2026-11-26T03:46:21Z`, after `#43` `00:03:54Z`;
    `flow-warp-shift-enter-tmux-cj` live in Stage 4)
- **End state definition:** pipeline passes on the merged head + Stage 4 review consensus passes; everything else is
  churn.
- **Beans created or extended:**
  - Created: `0475` (`docker-build.yml` lacks `concurrency`, running to `success` on `26/26` cancelled PR SHAs =
    `39.93 runner-min` wasted), `0476` (local-flow overlap polling relaunches `holon flow` every `60 s` `200+` times,
    falsely logs `"Overlap cleared"`, and bloats `checkpoint.context.logs` to `275 KB`).
  - Extended: `0443` (`26/48` `hac` SHAs cancelled), `0450` (`9` blind `local_tests` findings across `#310`–`#312` and
    `#308`), `0414` & `0418` (`4/4` sub-intents of `0371` failed initial Stage 3; `3/4` on `touch_set_guard`), `0384`
    (`0371` sub-intent 2 `#311` Stage 3 `claude-opus-5-5` cut by `90 s` stall budget after `20.93 min`), `0451` & `0458`
    (`dev-env#43` `20.18 min` Stage 5 CI; `dev-env#42` merged `29 s` after `842a47cf` while `Unit Tests` takes
    `15–20 min`), `0472` (`dev-env#43` committed `4` plans across `2` intent IDs onto one PR), `0412` (unmeasured steps
    and missing `coherence`/`dev-env` flow logs), `0427` (`gh event listen` hint still in `#310`–`#313` and
    `dev-env#42`–`#43`), `0197` (`calibration.py` +1/+2 lines triggered Stage 4 `CHANGES_REQUESTED` on `#310` & `#311`),
    `0465` & `0467` (uncommitted harness work + stray `=2026-11-24T08:00:00Z` + `5/5` post-merge harness commits).

#### Step-Level Timing Table (`2026-11-25T22:49:00Z..2026-11-26T03:50:09Z`)

> Flows measured: `0371` (`ledger-fragments-and-promotion`: parent overlap wait + 4 sub-intents `#310`–`#313` + parent
> integration + live `#314`), `0405-s2` (`#308` resume Iter 4–5 + Stage 5 + merge), `0438` (`#309` merge), `0400`
> (`macos-unit-only-when-relevant` Stage 1–2 + live local-flow overlap wait), `holon-coherence#56` (merge + `main` CI),
> and `thomashan/dev-env#42`–`#44` (GitHub PR/CI history).

| Step                                                    | Count | Median (min) | Longest (min) | Notes / Where                                                                                  |
| :------------------------------------------------------ | ----: | -----------: | ------------: | :--------------------------------------------------------------------------------------------- |
| Pre-flight (wrapper start -> Stage 1)                   |     - | not measured |  not measured | Wrapper lines before `Pipeline run initiated` still lack UTC timestamps (`0412`)               |
| Stage 1 intent (checkpoints)                            |     5 |         0.28 |          0.33 | `0371` sub-intents `1..4` (`0.27–0.31m`), `0400` (`0.33m`); `dev-env` not measured (`0412`)    |
| Stage 2 plan — initial (checkpoints / logs)             |     5 |         4.00 |          5.49 | `0371` sub1–4 (`3.30–4.03m`), `0400` (`5.49m`)                                                 |
| Stage 2 plan — re-plan after `touch_set_guard`          |     4 |         2.56 |          3.15 | `0371` sub1–4 (`2.29m`, `2.52m`, `2.61m`, `3.15m`; total `10.57m` churn)                       |
| Stage 3 admission check — admitted                      |    10 |         0.07 |          0.12 | `0371` parent + sub1–4 initial & re-plan + `0371` post-merge (`sum 0.70m`)                     |
| Stage 3 admission check — refused (per poll round)      |   202 |         0.08 |          0.13 | `0371` (`2x 0.10m`) + `0400` (`200+` logged rounds `0.05–0.13m`, `sum 16.20m+` pure churn)     |
| Stage 3 overlap wait per flow (wall)                    |     2 |       138.71 |        274.70 | `0371` parent (`2.72m` on `0175`), `0400` (`274.70m+` live `23:02:33Z..03:37:15Z+`, `0476`)    |
| Stage 3 execute — failed / discarded                    |     5 |        12.53 |         20.93 | `0371` sub1–4 (`15.57m` TS, `20.93m` 90s stall, `2.63m` TS, `9.12m` TS, `12.53m` TS = `60.8m`) |
| Stage 3 execute — succeeded (sub-intents)               |     4 |         4.56 |          4.91 | `0371` sub1–4 (`4.25m`, `4.88m`, `4.04m`, `4.91m`; `sum 18.08m`)                               |
| Execute end -> PR create                                |     4 |         0.21 |          0.22 | `0371` sub1–4 (`0.18–0.22m`)                                                                   |
| Stage 4 review ensemble + inner CI wait                 |    18 |         4.12 |         10.28 | `17` iters on `#310`–`#313` + `#308` i5 (`10.27m`); inner `review_local` CI split unmeasured   |
| Per-reviewer latency inside ensemble                    |     - | not measured |  not measured | Engine logs only ensemble completion (`0412`)                                                  |
| Stage 4 resolver turn + verify + commit                 |    14 |         3.73 |         30.22 | `13` iters on `#310`–`#313` (`2.07–6.32m`, `med 3.60m`) + `#308` i4 (`30.22m`)                 |
| Stage 4 review iteration total                          |    19 |         9.38 |         30.22 | `17` iters `#310`–`#313` (`5.70–11.90m`) + `#308` i4 (`30.22m`) & i5 (`10.27m`)                |
| Stage 4 git pushes & conflict/sync merges               |     - | not measured |  not measured | Individual push and conflict-merge durations not logged separately (`0412`)                    |
| CI check registration wait (Stage 4 / Stage 5)          |     9 |         0.03 |          0.28 | `5` Stage 4 waits (`0.02–0.03m`) + `4` Stage 5 waits (`0.28m` each)                            |
| PR CI wall — `hac` full code / merge                    |    14 |         8.83 |         10.17 | `14` completed SHAs (`#308`–`#314`, driven by `Test - Unit` `med 8.8m` / `Test - Stress`)      |
| PR CI wall — `hac` bookkeeping-gated                    |     5 |         1.33 |          1.38 | `#308` (`1eac4196`), `#310`–`#313` calibration heads (`64–83 s` in `Test - Hygiene`)           |
| PR CI wall — `hac` cancelled SHAs (`Docker Build` leak) |    26 |         1.82 |          9.77 | `26/26` cancelled SHAs ran `Docker Build` to `success` (`med 1.78m`, `sum 39.93m`, `0475`)     |
| `main` push CI — `hac` / `coherence` / `dev-env`        |     4 |         9.76 |         20.03 | `hac` `#309` (`10.67m`) & `#308` (`8.85m`); `coherence#56` (`1.97m`); `dev-env#43` (`20.03m`)  |
| PR CI wall — `dev-env` (`#42`, `#43`, `#44`)            |     7 |        14.90 |         20.18 | `3` full passes (`14.90–20.18m`), `1` partial (`11.72m`), `2` cancelled (`0.40–0.67m`), `1` IP |
| Stage 5 calibration + reconcile + promote work          |     5 |         0.77 |          0.91 | `#310`–`#313` (`0.75–0.78m`) + `#308` (`0.91m`); Prettier passed locally without timeout       |
| Stage 5 final-head CI wait (bookkeeping)                |     5 |         1.09 |          1.35 | `#310`–`#313` (`0.82–1.35m`) + `#308` (`1.09m`)                                                |
| Stage 5 total (`#310`–`#313`, `#308`)                   |     5 |         2.00 |          2.20 | `#310`–`#313` (`1.57–2.10m`) + `#308` (`2.00m`)                                                |
| Ready-to-merge queue wait (target PRs -> `main`)        |     5 |        32.48 |       1617.70 | `hac#309` (`2.88m`), `#308` (`8.75m`), `dev-env#43` (`32.48m`), `#42` (`1394.4m`), `coh#56`    |
| Sub-intent merge into parent plan (`#310`–`#313`)       |     4 |         0.18 |          0.18 | Auto-merged `11 s` after Stage 5 completed                                                     |
| Hand pre-merge sync to merge (`dev-env#42`)             |     1 |         0.48 |          0.48 | `842a47cf` pushed `03:45:52Z`, merged `29 s` later (`03:46:21Z`) before `Unit Tests` (`0458`)  |
| Idle between stop & resume                              |     - | not measured |  not measured | `0400` log buffered after `03:01:05Z` (`0385`); `coherence#56` / `dev-env#42–44` have no logs  |

**Stage / Wall Time Split (`2026-11-25T22:49:00Z..2026-11-26T03:50:09Z`):**

- **Working (`~4.5 h` across concurrent flows):** `0371` parent & `#310`–`#313` Stages 1–5 + `#314` Stage 4 (`~4.0 h`
  active work minus CI/overlap waits, including `60.78 min` discarded Stage 3 + `10.57 min` Stage 2 re-plans), `#308`
  resume (`~42.9 min`), `0400` Stage 1–2 (`5.82 min`) + `200+` failed admission launches (`16.2 min+`), `dev-env#43` &
  `#44` active stages (no wrapper logs).
- **Waiting on CI (`346` runs across 3 repos):** `hac` `298` runs (`206` `success`, `89` `cancelled`, `1` `failure` in
  `#311` `Test - Integration` `d65b84d7`, `2` `in_progress`); `coherence` `5` runs (`5` `success`, `1.97 min` wall);
  `dev-env` `43` runs (`30` `success`, `10` `cancelled`, `3` `in_progress`; `Unit Tests` `macos-latest`
  `14.9–20.2 min`).
- **Waiting on another flow (`~4.6 h`):** `0371` parent waited `2.72 min` on `0175`; `0400` (`macos-unit`) blocked
  `274.7+` min (`23:02:33Z..03:37:15Z+`) polling local flow `0371` every `60 s`.
- **Waiting on human merge:** `hac#309` (`2.88 min`), `hac#308` (`8.75 min`), `dev-env#43` (`32.48 min`), `dev-env#42`
  (`23.2 h`), `holon-coherence#56` (`27.0 h`).

**Churn Counts (`hac` in Window):**

- `26/48` (`54.2%`) `hac` SHAs were cancelled mid-CI (`24` by `0443` `chore(review)` double-pushes or fast follow-ups),
  yet `Docker Build` ran to `success` on all `26/26` (`39.93 runner-min` pure churn).
- `0371` sub-intents `1..4` ran `17` review iterations (`#310`: `8`, `#311`: `4`, `#312`: `3`, `#313`: `2`); `9` of
  those (`#310` iters `2–7`, `#311` iters `2–3`, `#312` iter `2`, plus `#308` iter `4`) carried `FIND-CI` `local_tests`
  failures (`0450`) triggered while `0443` cancelled/delayed GitHub CI, and `4/4` sub-intents lost `60.78 min` Stage 3 +
  `10.57 min` Stage 2 re-plan work to initial `touch_set_guard` / `90 s` stall failures.

#### Ranked Suggestions

1. **`0475` (new, high — Pipeline / GitHub Actions):** Add `concurrency` (`cancel-in-progress` on `pull_request`,
   `github.sha`-scoped on `push`) to `.github/workflows/docker-build.yml`. Eliminates `~40 runner-min` per 5 h wasted on
   `26/26` cancelled SHAs.
2. **`0476` (new, high — Flow / Wrapper & Engine):** Fix local-flow Stage 3 overlap polling in `run_holon_flow.py` (no
   false `"Overlap cleared"`, back off / inspect local blocker before re-spawning `holon flow`) and bound `context.logs`
   in flow checkpoints. Eliminates `200+` redundant launches (`~16–20 min` CPU/IO churn) and stops `275 KB+` checkpoint
   bloat.
3. **High-impact extensions (`0443`, `0450`, `0414`, `0418`, `0384`, `0451`):**
   - `0443` + `0450`: combined, they cancelled `26/48` `hac` SHAs and caused `9` blind `local_tests` Stage 4 churn
     iterations across `#310`–`#312` and `#308`.
   - `0414` + `0418`: `4/4` sub-intents of `0371` failed initial Stage 3 (`3/4` on `touch_set_guard`), discarding
     `37.22 min` of execution + `10.57 min` of Stage 2 re-plans.
   - `0384`: `90 s` stall budget killed Stage 3 `claude-opus-5-5` on `#311` (`20.93 min` lost).
   - `0451`: `dev-env#43` Stage 5 calibration commit `13844ea7` ran another `20.18 min` full CI pass (`Unit Tests`).
4. **Other extensions (`0458`, `0472`, `0427`, `0197`, `0412`, `0465`, `0467`):** `dev-env#42` merged `29 s` after
   `842a47cf` before `Unit Tests` (`0458`), `dev-env#43` accumulated `4` plan commits from `2` intent IDs (`0472`),
   `gh event listen` hints still corrupt review URLs (`0427`), `calibration.py` growth still blocks Iter 1 (`0197`),
   unmeasured steps and buffered logs persist (`0412`), and uncommitted harness files + `5/5` post-merge commits persist
   (`0465`, `0467`).

#### Examined and Found in Order

- `ci_bookkeeping_gate` on uncancelled `holon-agentic-coder` Stage 5 calibration heads (`1eac4196`, `e34e0be7`,
  `d80fcea3`, `fb12d695`, `0acbcd18`): all `5` settled in `64–83 s` (`~1.1–1.4 min` total CI).
- `holon-coherence#56`: merged cleanly (`22:57:30Z`) and `main` push CI passed all `5` workflows in `1.97 min`.
- `post-pr-merge` sub-intent handling: correctly skipped per-sub-intent runs on `#310`–`#313` (which target the parent
  plan branch) and synced `hac#309`, `coh#56`, `hac#308`, `dev-env#43`, and `dev-env#42` cleanly.
- `hac#309` (`22:51:23Z`) and `hac#308` (`00:03:10Z`) `main` push CI: both passed all `6` workflows cleanly (`10.67 min`
  and `8.85 min`).

#### Unmeasured Steps

- Pre-flight wrapper setup duration (no UTC timestamps in `run_holon_flow.py` header lines).
- Per-reviewer latency inside the Stage 4 ensemble and `review_local` reviewer-turn vs CI-wait split inside Stage 4.
- Individual Stage 4 git push and conflict-merge durations.
- Flow logs for `holon-coherence#56` and `thomashan/dev-env#42`–`#44` (missing), and final `36+ min` of
  `todo/flow-macos-unit-only-when-relevant.log` (`03:01:05Z..03:37:15Z+`, buffered under `0385`).

### 2026-11-25T22:49:00Z — Session-Start Audit

- **Trigger:** session start (2026-11-26 local). Evidence window: since the `2026-11-25T06:05:00Z` entry.
- **Last merged pull requests at audit time:** `Holon-Agentic-Coder/holon-agentic-coder#307` (merged
  `2026-11-25T06:54:51Z`, after `#305` `06:12:01Z` and `#306` `06:51:27Z`); `holon-coherence#55`
  (`2026-11-24T12:44:47Z`, `#56` open); `thomashan/dev-env` unchanged. Open: `hac#308` (CONFLICTING, 39 commits) and
  `hac#309` (MERGEABLE).
- **Beans created:** `0465` (uncommitted harness beans and audit instruction), `0466` (flow aborts when Docker is
  briefly down), `0467` (per-merge record commits are 60 of 92 harness commits).
- **Extended or already covered:** `0458` (#305 to #307 sat 4.3 to 4.8 h between approval `01:49Z`, `02:15Z`, `02:02Z`
  and merge, each with a final `origin/main` sync commit at `05:48Z`, `06:13Z`, `06:53Z` right before merge); `0412`
  (the 37 `0153` self-doc flows wrote only one `todo/flow-*-self-doc.log`, so per-step timing is not measured); the
  DNS/resolver bean and `0432` (`hac#308` review halted at iteration 4 on ENOTFOUND, then target sync blocked by
  uncommitted tracked changes).
- **Examined and in order:** #305 to #307 had 0 failed checks and 1 consensus review each; all 15 pipeline runs on their
  branches succeeded.
- **Not measured:** per-step timing for #305 to #309 (no flow logs); no timing table was built.

### 2026-11-25T06:05:00Z — Fifth-Merge Audit

- **Trigger:** fifth target-repo merge since `2026-11-25T05:41:00Z` (`holon-agentic-coder` PRs `#300`, `#301`, `#302`,
  `#303`, `#304`; `holon-coherence` unchanged at `#55` merged `2026-11-24T12:44:47Z` with `#56` open;
  `thomashan/dev-env` unchanged at `#41` merged `2026-11-25T04:03:06Z` with `#42` open). Note a parallel peer audit
  (`2026-11-25T05:45:00Z` below, uncommitted on disk) covered up to `#300` and created Beans `0458`–`0459`; this audit
  covers the `#300–#304` merge sweep, `05:20:56Z–06:04:00Z` CI/flow delta, `0371`, `#308`, and `#309` (`0438`)
  completion without duplicating `0458`–`0459`.
- **Last merged PR at audit time:** `Holon-Agentic-Coder/holon-agentic-coder#304` (`github-ci-self-doc`, merged
  `2026-11-25T05:46:57Z`), `Holon-Agentic-Coder/holon-coherence#55` (`2026-11-24T12:44:47Z`), `thomashan/dev-env#41`
  (`2026-11-25T04:03:06Z`).
- **End state definition:** pipeline passes on the merged head + Stage 4 review consensus passes; everything else is
  churn.
- **Beans created or extended:**
  - Created: `0460` (Stage 4 resolver runs 7,800+ pytest twice and unconditionally on Markdown/bookkeeping-only fixes),
    `0461` (`main`-push CI `concurrency.group` silently cancels intermediate `main` commits during burst merges), `0462`
    (epoch-second `I-`, `P-`, `REV-ITR-`, and `CAL-` IDs collide across concurrent flows), `0463` (Stage 2 planner
    collapses file-scoped intents into directory touch-set entries that broaden Stage 3 overlap blocking).
  - Extended: `0407` (`#309` `21.63 min` Stage 4 after `3/3` APPROVED, `#300` `FIND-DIRTY-001` churn iter, `#308` Iter
    4), `0412` (unmeasured steps in `0371`, `#309`, `#308`, `#300–#304`), `0442` (`#309` Stage 2 timeouts ->
    `Test - Hygiene` failure + `2.60 min` Stage 5 overhead), `0443` (`#309` `29 s` 4-push Stage 4 burst), `0454` (`6`
    more `Merge origin/main` full-CI heads `7.35–9.17 min` on `#300–#305`), `0455` (`bean-triage-prioritisation.md`
    `3.5+ h` stale across `#293–#304`).

#### Step-Level Timing Table (Cadence `#300–#304`, Active `0371` & `#309`, Live Window `05:20:56Z–06:04:00Z`)

> Flows measured: cadence `#300–#304` (`antigravity-agent/gemini-4-neon`, execution summaries `283.2–384.3 s` and full
> PR/CI histories), plus post-`05:21Z` runs `0371` (`ledger-fragments-and-promotion`) and `#309` (`0438`,
> `calibration-merge-adapted-file`), alongside live `#308` (`workspace-survival-job-parallel`) and halted `0407`.

| Step                                                     | Count | Median (min) | Longest (min) | Notes / Where                                                                                   |
| :------------------------------------------------------- | ----: | -----------: | ------------: | :---------------------------------------------------------------------------------------------- |
| Pre-flight (wrapper start -> Stage 1)                    |     2 | not measured |  not measured | `flow-*.log:1-13` lack UTC timestamps (`0371`, `0438`); Antigravity `#300–#304` no wrapper log  |
| Stage 1 intent (checkpoints)                             |     2 |         0.34 |          0.34 | `0371` `0.34m`, `0438` `0.34m` (`#300–#304` pruned worktrees; live `#308` `0.53m`)              |
| Stage 2 plan (checkpoints)                               |     2 |         4.08 |          4.94 | `0438` `3.22m` (incl. `60s` Prettier timeouts), `0371` `4.94m` (incl. `60s` Prettier timeouts)  |
| Plan end -> Stage 3 start gap                            |     2 |         0.00 |          0.00 | `0371` / `0438` checkpoint `end == start`; `#300–#304` ledger plan->override `1.9–2.7m`         |
| Stage 3 admission block / overlap wait                   |     2 |       114.8+ |        200.3+ | `0371` refused at `05:32:48Z` on `#305` (`29.2m+` live); `0407` halted since `02:41:40Z`        |
| Stage 3 execute (checkpoint / ledger summary)            |     6 |         5.31 |          6.41 | `#300` `4.72m`, `#301` `5.29m`, `#302` `6.41m`, `#303` `5.10m`, `#304` `5.97m`, `0438` `5.33m`  |
| Execute end -> Stage 4 start / PR open                   |     6 |         0.20 |          0.45 | `0438` `0.20m` to `PR create`; `#300–#304` ledger-commit to `PR created` `0.37–0.48m`           |
| Stage 4 review iteration (wall / ensemble)               |     9 |         7.42 |         10.15 | `#309` i1 `3.9m`/i2 `10.15m`; `#300–#304` `6` iters (`4.78–8.42m`); `#308` i4 `8.4m` (`05:25Z`) |
| Per-reviewer latency inside ensemble                     |     - | not measured |  not measured | Ledger/checkpoint log ensemble wall only (`0412`)                                               |
| Stage 4 resolver (`#309` `.md` Prettier / `#308` i4)     |     2 |        22.0+ |         37.5+ | `#309` i1 `6.58m` (`.md` Prettier only, `0460`); `#308` i4 live since `05:25:12Z` (`37.5m+`)    |
| Stage 4 total (`0438` `#309`)                            |     1 |        21.63 |         21.63 | `05:36:09Z..05:57:47Z` (blocked `17.7m` on unformatted `.md` plan; `1` iter needed, `2` run)    |
| Conflict check / in-flow target sync                     |     1 |         0.23 |          0.23 | `0438` `#309` `05:47:06Z..05:47:20Z` (`14 s`, `05:47:20Z`)                                      |
| Stage 4 git pushes & `review_local` wall                 |     - | not measured |  not measured | Individual push and `review_local` durations not split (`0412`)                                 |
| CI check registration wait (`#309` Iter 2 / Stage 5)     |     2 |         0.16 |          0.30 | `#309` Iter 2 `1 s` (`05:57:32Z..33Z`); Stage 5 `18 s` (`06:00:37Z..55Z`)                       |
| PR CI wait — full code / `main_merge` (`05:23Z–06:02Z`)  |     8 |         8.63 |          9.95 | `6` `main_merge` (`7.35–9.17m`) + `#309` `4cdc1913` (`7.93m` fail) + `4ded0b14` (`9.95m`)       |
| PR CI wait — gated bookkeeping heads (`05:23Z–06:02Z`)   |     2 |         0.93 |          0.95 | `#309` `32b8b868` (`0.90m`) and `0c534bf2` (`0.95m`; inner wait `48.93s`)                       |
| PR CI wait — cancelled burst head (`#309` `26eca98f`)    |     1 |         2.47 |          2.47 | `5` checks cancelled in `7 s`; `Docker Build` ran `2.47m` (`05:47:25Z..05:49:53Z`)              |
| `main` push CI (`6` pushes `05:20:57Z–05:57:42Z`)        |     6 |         9.43 |         11.43 | `4` passed (`8.13–11.43m`, med `11.01m`); `67bfb621` (`#302`) & `d281e437` (`#303`) cancelled   |
| Stage 5 calibration work (`#309` `05:57:50Z..06:00:26Z`) |     1 |         2.60 |          2.60 | Inflated by `npx --yes prettier` (`0442`); `#300–#304` `2.60–2.83m` ledger delta                |
| Stage 5 promotion + reconciliation + ledger commit       |     5 |         ~0.0 |          0.02 | Within final `1–2 s` of Stage 5 work (`#300–#304`, `#309`)                                      |
| Stage 5 total (`#309`)                                   |     1 |         3.98 |          3.98 | `05:57:47Z..06:01:51Z` (incl. `48.93s` `final_head_ci` on `0c534bf2`)                           |
| Ready-to-merge queue wait (`#300–#304`)                  |     5 |       256.07 |        276.65 | `#300` `269.03m`, `#301` `275.35m`, `#302` `276.65m`, `#303` `254.60m`, `#304` `256.07m`        |
| Hand pre-merge sync to merge (`#300–#304`)               |     5 |         1.17 |          8.32 | All `5` merged early (`55 s` to `8.18m` before PR CI completed); `#300` `8.32m`, `#301` `5.75m` |
| Idle between stop & resume                               |     - | not measured |  not measured | `0407` halted since `02:41:40Z`; `#300–#304` no wrapper logs (`0412`)                           |

**Stage / Wall Time Split (Post-`05:21Z` Active Flows `#309`, `0371`, `#308` live + `#300–#304` sync sweep):**

- **Working (`~1.0 h` wall):** `#309` active stages (`34.5m` total minus CI waits), `0371` Stages 1–2 (`5.28m`), `#308`
  live Iter 4 resolver container (`37m+` since `05:25:12Z`).
- **Waiting on CI (`~1.3 h` PR-head wall in window, `121` `hac` runs):** `66` `pull_request` runs across `11` heads
  (`10/11 = 90.9%` churn; `7/7 = 100%` churn after `05:42Z`), `19` `dynamic` runs, `36` `push` runs on `main` (`2/6`
  burst pushes `#302`/`#303` `cancelled`).
- **Waiting on another flow (`~4.1 h` accumulated):** `0371` polling `#305` (`29.2m+`), `0407` blocked in Stage 3 since
  `02:41:40Z` (`202m+`).
- **Waiting on maintainer merge:** `#300–#304` cleared after `254.6–276.7m` ready waits; `#305` (`CLEAN`, synced
  `05:48:38Z`), `#306` (`DIRTY`), `#307` (`DIRTY`), `#308`, `#309` (`CLEAN` at `06:01:51Z`) await merge.

**Churn Counts (`#300–#304` Lifetime + In-Window):**

- **`#300–#304` full lifetimes:** `20` PR-tested CI heads (`4` each): `16/20` (`80.0%`) post-open churn (`10`
  bookkeeping + `6` `Merge origin/main`), with `4` PR-open heads (`934ae1c9`, `03510f82`, plus reconcile-on-open
  `b9bb5c99`, `2de5dd7e`). Review iterations: `6` total across `5` PRs (`5` needed + `1` churn on `#300`
  `FIND-DIRTY-001` `01:06Z`); in-window (`05:20:56Z..06:02Z`), `#309` required `1` iter + `1` churn iter (`6.58m`
  resolver + `10.15m` Iter 2) solely to Prettier-format `P-1795584464-CLA-CO5.5.md`.
- **Window CI (`05:20:56Z–06:02:00Z`):** `121` total `hac` runs; `10/11` (`90.9%`) `pull_request` heads were churn (`7`
  `main_merge` + `3` bookkeeping), only `1/11` (`4cdc1913` on `#309`) carried new code; `2/6` `main` push CI runs
  (`67bfb621`, `d281e437`) cancelled mid-queue.

#### Ranked Suggestions

1. **`0460` (new, high — Flow / Stage 4):** Skip `uv run task test` in `_verify_before_push`
   (`entrypoint/review_loop.py`) when resolver edits are Markdown/bookkeeping-only, and stop running the `7,800+`-test
   suite twice back-to-back on code fixes (agent + `_verify_before_push`). Saves `~3–6 min` per doc-only resolver pass
   (`#309` `6.58m`) and `~2–3 min` per code resolver pass.
2. **`0461` (new, high — Pipeline / GitHub Actions):** Fix `push` to `main` `concurrency.group` in
   `.github/workflows/{test-unit,test-stress,test-hygiene,test-integration,make}.yml` (scope `push` by `github.sha`, not
   bare `github.ref`) so burst merges (`#301–#304`) stop silently cancelling intermediate `main` `Test - Unit` and
   `Test - Stress` runs (`67bfb621`, `d281e437`).
3. **`0463` (new, high — Flow / Stage 2):** Prohibit Stage 2 planner from collapsing concrete file-scoped `intent.json`
   lists into directory touch-set entries (`planner.template.md`, `entrypoint/planner.py`). `0371` supplied `19`
   explicit files and `0` folders, yet Stage 2 emitted `.../ledger/` with only an advisory stderr warning.
4. **`0462` (new, normal — Architecture / Flow):** Add `build_stage_disambiguator` hex suffixes to
   `intent_creator.py:86`, `build_plan_id` (`ledger/rows.py:122`), `REV-ITR-...` (`flow/review/loop.py:463`), and
   `CAL-...` (`calibration.py:1316`). Live flows `0371` and `0438` (`#309`) minted identical `I-1795584436-*` and
   `P-1795584464-CLA-CO5.5`, adding to `5` duplicate `plan_id`s already on `main` (`#300` & `#302` shared
   `P-1795567904-ANA-G4N`).
5. **Extensions (`0407`, `0442`, `0443`, `0454`, `0455`, `0412`):** Prioritized evidence strengthens the active fixes
   for unneeded Iter 2 review (`0407` on `#309`), `npx prettier` Stage 2 failure + Stage 5 overhead (`0442` directly
   cost `#309` `~17 min`), Stage 4 4-push burst cancellation (`0443` cancelled `26eca98f`), mechanical
   `Merge origin/main` CI (`0454` ran `6` more `7.35–9.17 min` suites), `post-pr-merge` triage staleness (`0455`), and
   unmeasured steps (`0412`).

#### Examined and Found in Order

- `hac#300–#304` `main` merges: all `5` merged cleanly, and `post-pr-merge` recorded `0153` updates cleanly (`da742b5`,
  `51e3135`) without duplicate flow launches across sessions.
- `hac#309` (`0438`) Stage 5 calibration: `calibration_self_check` + `final_head_ci` settled cleanly (`3.98 min`,
  `MERGEABLE/CLEAN`, `ΔEV +10.42`, `4` promoted candidates, all `11` CI checks passed on `0c534bf2`).
- `ci_bookkeeping_gate` on un-cancelled pure bookkeeping heads (`#309` `32b8b868` `0.90 min`, `0c534bf2` `0.95 min`):
  gating worked accurately once parent heads were not cancelled.
- `holon-coherence` (`#55`, `#56` open) and `thomashan/dev-env` (`#41`, `#42` open): unchanged since `05:41Z`, no new
  merge regressions.

### 2026-11-25T05:45:00Z: Fifth-Merge Audit (Claude Code session, incremental from 00:28Z)

- **Trigger:** fifth merge. Since the 00:28Z entry of this session, `holon-agentic-coder` merged #278, #280, #281, #283
  to #300 (21 PRs). Entries at 02:54Z, 04:02Z and 05:07Z overlap this period; their beans (0442 to 0451) were not
  duplicated. The 05:41Z entry below was written by the other session while this audit ran; its beans are `0452` to
  `0455`, so this audit's beans are `0458` and `0459`.
- **Last merged pull requests at audit time:**
  - `holon-agentic-coder`: `#300` (`decomposition-rule-self-doc`, merged `2026-11-25T05:30:59Z`)
  - `holon-coherence`: `#55` (`coherence-module-line-budget-all`, merged `2026-11-24T12:44:47Z`; `#56` open)
- **Beans created or extended:**
  - Created: `0458` (ready PRs hand-synced before each merge, 8 of 12 merged before that pipeline ended; complements
    `0454`, written by the other session at 05:41Z), `0459` (maintainer rules kept only in Claude Code's private memory
    never reach the Antigravity session).
  - Extended: `0400` (macOS unit leg is now the critical path), `0411` (`AGENTS.md` says `gemini-4-argon`,
    `holon-flow.md` and every flow use `gemini-4-neon`), `0412` (unrecorded gaps between stages), `0423` (measured
    concurrency and cross-session blocking), `0398` (approved PR #305 blocks 0371), `0446` (0407 still refused, no
    wrapper alive). `0371` and `0383` have uncommitted edits from another session and were left alone.
- **Outputs:** `todo/self-improvement-audit-2026-11-25a/` (`timing-period.md`, `churn-period.md`, `pipeline-fixes.md`,
  `sweep.md`, `per-pr.md`, `churn-ledger.md`, scripts).

#### 1. Timing (00:28Z to 05:41Z; ANA = Antigravity `gemini-4-neon`, CLA = Claude Code `claude-opus-5-5`)

| Step                                                |       Count |    Median (min) | Longest (min) | Longest in             |
| :-------------------------------------------------- | ----------: | --------------: | ------------: | :--------------------- |
| Pre-flight                                          |           - |    not measured |  not measured | (0412)                 |
| Stage 1 intent                                      |          10 |             0.3 |           0.3 |                        |
| Stage 2 plan                                        |          10 |             3.5 |           5.6 | 0407                   |
| Plan end to Stage 3, ANA (unrecorded)               |           8 |             1.4 |           1.8 | review-report-self-doc |
| Stage 3 refusal (waiting on another flow)           |           3 |             178 |         181.5 | #308 on #283 HTTP 406  |
| Stage 3 executor ANA / CLA                          |       8 / 2 |      6.5 / 23.1 |    7.6 / 41.3 | #308                   |
| Stage 4 review iteration ANA / CLA                  |      13 / 8 |       7.5 / 7.4 |     8.4 / 9.6 | #308                   |
| Stage 4 resolver ANA / CLA                          |       2 / 5 |       3.2 / 5.2 |    4.2 / 27.2 | #308                   |
| Stage 4 total (checkpoints)                         |           8 |             8.0 |          22.8 | #308                   |
| Target sync (#283 path)                             |           7 |             0.1 |           0.2 | #308                   |
| CI wait, gated heads                                |           3 |             0.8 |           1.1 | #308                   |
| Stage 5 total (checkpoints)                         |           8 |             4.0 |          12.0 | #308                   |
| Pipeline wall: code / main-merge / bookkeeping head | 9 / 21 / 33 | 6.5 / 7.9 / 0.9 |             - |                        |
| Hand pre-merge sync to merge                        |          11 |             5.5 |          34.6 | #292                   |
| Intent to ready, ANA one-iteration slice            |           8 |            23.4 |          31.2 | #297                   |
| Ready to maintainer merge (sweep #288 to #299)      |          12 |           335.7 |         523.4 | #288                   |

Stage split: working about 5.4 h across all flows. Waiting on another flow 5.1 h (#308, 0407, 0371). Waiting on CI 0.15
h. Waiting on the maintainer's merge 94.6 PR-hours (27 ready PRs).

#### 2. Answers

1. **Pipeline fixes worked.** Full pipeline median 10.8 min (p90 24.2) before #272, 7.6 min (p90 8.7) after #278.
   Bookkeeping heads are gated to 0.9 min (32% of completed heads after #278). `unit (ubuntu)` went from 4.7 to 3.2 min
   and `unit (macos)` from 8.2 to 7.0 min (#275). Timing-gate failures: 10 macOS and 4 Workspace survival between 16:00Z
   and 21:10Z, none in the 94 PR and main heads since #278. The last one was at 20:56:19Z. No failure since #278 was
   noise; the one failure (hygiene, #306) was real.
2. **#283 worked inside a flow, not outside.** #308 took 7 target syncs and no hand resolution. Its re-reviews after a
   ledger-only sync are 0407/0449. PRs whose flow had already ended still needed 13 hand `resolve-conflict` merges
   (02:28Z to 05:23Z, Bean 0458). After #278, review iterations on conflicting heads: none seen.
3. **Antigravity sweep:** the 12 PRs took 18.9 to 31.2 min from intent to ready when one review iteration was enough (8
   of 12; #289 63.5, #290 114.4, #292 241.3, #296 731.8). They then waited 265.9 to 523.4 min for the merge. Pipeline
   heads per PR: median 4.5 (2 bookkeeping and 1 hand sync each). Review iterations: 1 to 5 (median 1). Claude Code
   flows in the period: #308 intent to first approval 245 min, of which 181.5 waited on #283; working time about 75 min.
   Per-iteration speed is the same (7.4 against 7.5 min). The difference is the size of the work and Stage 3.
4. **Churn left:** 65 of 78 PR heads in the period were churn. Main-merge heads use 409 runner-min against 167 for code
   heads. Review churn: 26% of iterations over #272 to #308, but 1 of 11 in flows started after #278.
5. **Coordination:** at most 4 flows at once across both sessions. 0407 (Antigravity) has been refused since 02:41:40Z
   on a directory in its scope. The rule against that exists only in Claude Code's memory. 0371 (Claude Code) was
   refused at 05:32:48Z on Antigravity's approved #305. No duplicate flow for one bean. Merges cannot be attributed
   (shared account).

#### 3. Ranked suggestions

1. **`0458` (new, high):** sync ready PRs once in a batch after a merge, not before each merge; skip `MERGEABLE` PRs;
   wait for green on any synced head. About 12 pipelines (95 min serial) saved per sweep of 12, and no unverified
   merges.
2. **`0459` (new, high):** move workspace rules from private memory into `.agents/`, and have the wrapper refuse
   directory scopes. Saves about 180 min on 0407 alone.
3. **`0400` (extended):** run the macOS unit leg only where it matters; about 3 min off every code and merge head.
4. **`0423`, `0398`, `0446` (extended):** a shared registry across sessions, starting stacked on an approved PR, and
   SPLIT parent admission.
5. **`0411`, `0412` (extended):** one canonical model ladder; record the unrecorded stage gaps.

#### 4. Examined and found in order

- `ci_bookkeeping_gate` (#272), unit speed-up (#275) and timing gate (#278): working as intended (above).
- HTTP 406 admission failure on oversized PRs: fixed by #299. No refusal of that kind after 05:20:56Z.
- Antigravity one-iteration flows: Stage 5 is a steady 3.9 to 4.1 min, already in 0442.

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
