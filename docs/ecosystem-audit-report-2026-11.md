# Holon Ecosystem Architecture & Source-Code Audit (2026-11)

**Original Audit:** 2026-11-26 (`holon-agentic-coder@f1e18bcd`, `holon-coherence@18084f3`)  
**Previous Refresh:** 2026-11-27 (`holon-agentic-coder@2a83e4cc7`, `holon-coherence@4a02926b`)  
**Refreshed:** 2026-11-27 (`holon-agentic-coder@1f3331637`, +4 PRs `#415`, `#424`–`#426`; `holon-coherence@4d2cfcf8`, +4
PRs `#83`, `#67`, `#84`, `#85`)  
**Remediation Beans:** `0524`–`0539`, `0584`–`0588`, `0614`–`0638` (plus cross-referenced `0383`, `0405`, `0412`,
`0491`, `0543`, `0546`, `0558`, `0563`, `0564`, `0596`, `0601`, `0602`, `0610`, `0611`, and existing beans)

---

## 1. Executive Comparison & Scorecard

| Metric (`src/` baseline)            |                                                                   `holon-agentic-coder` |                                                                               `holon-coherence` |
| ----------------------------------- | --------------------------------------------------------------------------------------: | ----------------------------------------------------------------------------------------------: |
| Source files / LOC (`src/` only)    |                              382 `.py` / 52,432 LOC (`426` / `60,314` incl. `scripts/`) |                                        67 `.py` / 11,092 LOC (`77` / `12,817` incl. `scripts/`) |
| Test files / scale                  |                        452 `.py` / 109,532 LOC (`5,207` `test_*` / `8,128` total `def`) |                                  77 `.py` / 21,145 LOC (`1,082` `test_*` / `1,495` total `def`) |
| Functions / return-typed (`src/`)   |                                                                           3,052 / 99.5% |                                                                                     594 / 98.7% |
| Files > 200L / > 400L (`src/`)      |                                     61 / 17 (default budget 350L; `>350L`: 20, 1 stale) |                                              17 / 7 (default budget 200L; `>350L`: 10, 2 stale) |
| Max cyclomatic complexity           |                                                                 219 (`run_review_loop`) |                                                              24 (`normalize_anthropic_request`) |
| Bare `except:` / `except Exception` |                                                   0 / 137 (`3` silent `pass` in `src/`) |                                                            0 / 26 (`0` silent `pass` in `src/`) |
| Docstrings / comments (`src/`)      | 73 func docstrings (+17 mod, +6 cls), 584/707 `# why:` (82.6%); tests: 1,022 docstrings | 0 docstrings / 0 prose comments (`10` `# noqa` in `src/`, `0/0` across `src`/`tests`/`scripts`) |

> **Progress since `2a83e4cc7` / `4a02926b` (`4` HAC PRs `#415`, `#424`–`#426`; `4` Coherence PRs `#83`, `#67`, `#84`,
> `#85`):** `holon-coherence` broke the `parsers ↔ providers` (`3↔4`) import cycle and added structural
> `ProviderFormat.matches()` seams (`#84`, `0527`), unified `CumulativeMetrics` + `OfflineMetricsAccumulator` into
> `metrics_math.py` (`#85`, `0528`, dropping `broad_except` `30→26`), fixed SSE carry-buffer / EOF alignment (`#83`,
> `0528`), and extracted `dashboard.html` (`#67`, `0530`, shrinking `dashboard.py` `383→9L`), lifting
> **`holon-coherence` to `8.1 / 10 (+0.1)`**. `holon-agentic-coder` closed **`0615`** (`#415` subpackage import-cycle
> ratchet) and **`0611`** (`#424` debounced `promote-ledger.yml` + missing-token warning), landed the AST
> behaviour-preservation CI gate (`#425`, `0601` slice 1), and cleaned `12` more test files (`#426`, `0153`), holding
> **`holon-agentic-coder` at `7.5 / 10`** while surfacing root-module ratchet gaps in HAC (**`0635`**), `303` pending
> HAC fragments (**`0636`**), `2` stale Coherence budget overrides (**`0637`**), and Stage 4→5 triple-push CI churn
> (**`0638`**).

|  #  | Aspect                                     | `holon-agentic-coder` |  `holon-coherence`  | Summary Takeaway                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| :-: | ------------------------------------------ | :-------------------: | :-----------------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|  1  | Clean Architecture & Layer Boundaries      |    6.7 / 10 (+0.1)    |   7.9 / 10 (+0.2)   | HAC `#415` (`0615`) ratcheted `entrypoint↔flow` (`12↔15`) and `knowledge↔ledger` (`4↔1`), **but** skips root modules (`calibration↔calibration_self_check`, `entrypoint↔review_target`, `flow↔review_target`, `flow↔flow_guard` -> **`0635`**). Coherence `#84` (`0527` slice 1) broke `parsers↔providers` (`3↔4 → 0`); 4 cycles remain (`commands↔container`, `payload_cleaner↔providers`, `payload_cleaner↔reduction_passes`, `hybrid_cache↔proxy` + `0632`). |
|  2  | Modularity, Cohesion & File Sizing         |       7.4 / 10        |   7.9 / 10 (+0.2)   | HAC holds `20` `>350L` `src/` modules (`1` stale `flow/__init__.py: 27/522L`, `1` missing `calibration.py: 1608`, `0585`; `loop.py` `947/950L`). Coherence `#67` (`dashboard.py` `383→9L`) and `#85` (`metrics/aggregation.py` `222→150L`) dropped `>200L` (`19→17`) and `>400L` (`8→7`), leaving `2` stale overrides in `module_budgets.json` (**`0637`**).                                                                                                    |
|  3  | Complexity & Control Flow                  |       5.8 / 10        |      8.0 / 10       | HAC `run_review_loop` sits at `CC=219` (`947L`) alongside `planner.py:main` (`49`), `turns.py:run_turn` (`49`), and `stages/review.py` (`47`) (`0192`, `0531`). Coherence max CC stays `24` (`normalize_anthropic_request`) with `10` inline `# noqa` lines in `src/`.                                                                                                                                                                                          |
|  4  | Clean Code & Idiomatic Python              |       7.4 / 10        |   7.6 / 10 (+0.2)   | HAC stays `99.5%` return-typed (`3,037/3,052`). Coherence `#85` unified live/offline metrics (`metrics_math.py`), `#84` extracted `providers/_common.py`, `#83` aligned streaming/non-streaming `finish_reason`, and `#67` decoupled `dashboard.html` (`-461` net `src/` LOC, `586/594 = 98.7%` return-typed; `14` `deepcopy` sites in `providers/` `0528` & `39` non-settings env sites **`0634`** remain).                                                    |
|  5  | Intention-Revealing & Self-Doc Code        |    8.2 / 10 (+0.1)    |      8.3 / 10       | HAC `#425` (`0601`) added `scripts/check_self_doc_behavior.py` + `test-self-doc-behavior.yml` and `#426` cut test docstrings (`1,057→1,022`), though `31` `test_self_doc*.py` copies remain (`0601`). Coherence maintains `0` docstrings and `0` prose comments across all `67` `src/`, `77` `tests/`, and `10` `scripts/` files (`10` `# noqa` in `src/`).                                                                                                     |
|  6  | Extensibility & Plug-in Seams              |       6.8 / 10        |   8.0 / 10 (+0.3)   | HAC `RunnerSpec`/`GitForge` (`0535`) parked. Coherence `#84` (`0527`) added structural `ProviderFormat.matches()` / `is_cloud_host()` seams and unified `detect_provider_name()` + dynamic `KNOWN_PROVIDERS` in `providers/registry.py`, `proxy/addon.py`, `proxy/routing.py`, and `parsers/sse.py`.                                                                                                                                                            |
|  7  | Testability & Verification Quality         |    8.0 / 10 (+0.1)    |   8.3 / 10 (+0.1)   | HAC added `+3` test files (`5,177→5,207` `test_*` cases; `65` cancelled check-runs across `#415,#424–#426`, **`0638`**). Coherence added `+1` test file / `+706` test LOC (`1,067→1,082` `test_*` cases) covering format seams, metrics parity, dashboard asset loading, and SSE wire finish, with `0` cancelled CI runs across `222` check-runs.                                                                                                               |
|  8  | Error Handling, Resilience & Failure Modes |       8.2 / 10        |   8.3 / 10 (+0.1)   | HAC `broad_except` steady (`137` `except Exception`, `3` silent `pass`); `0424` hit `CF-0064` & `0607` hit `CF-0065`. Coherence `#83` fixed split-chunk/EOF SSE buffering (`translation.py`, `sse_tap.py`), and `broad_except` dropped `30→26` (`0` silent `pass`).                                                                                                                                                                                             |
|  9  | Security, Isolation & Secret Hygiene       |       8.4 / 10        |      8.6 / 10       | HAC awaits Docker quotas, `local_llm` modes, `git.py` `--`, `Dockerfile` pin (`0532`). Coherence maintains pinned multi-arch digests, frozen `uv.lock`, `HEALTHCHECK`, and `check_commit_trailers.py` (`8/8` new HAC & Coherence squash merges still carry 5 `Co-authored-by:` agent trailers -> **`0633`**).                                                                                                                                                   |
| 10  | Observability, Provenance & Config         |       8.1 / 10        |   7.6 / 10 (-0.1)   | HAC `#424` (`0611`) debounced `promote-ledger.yml` + added missing-token `::warning::`, offset by `291→303` pending fragments (**`0636`**), `210/287` bookkeeping check-runs (**`0638`**), and `5/8` unlogged flows (`0412`). Coherence pending fragments grew `69→81` (`737` rows, `0620`), `155/222` (`69.8%`) check-runs ran on bookkeeping commits (`0588`), and `39` non-settings env sites remain (`0634`).                                               |
|     | **Overall Score**                          |     **7.5 / 10**      | **8.1 / 10 (+0.1)** | **At `4d2cfcf8` vs `1f3331637`, Coherence rises to `8.1 / 10` (+0.1) over HAC (`7.5`)**, closing `parsers↔providers` (`#84`), metrics unification (`#85`), dashboard asset decoupling (`#67`), and SSE finish (`#83`); top remaining priorities are `0638`/`0383` (Stage 4→5 triple push & double CI wait), `0546`/`0628`/`0543` (`CF-0062/64/65`), `0625` (181m quota stalls), `0635`/`0632`, `0636`/`0620`, and `0637`.                                       |

---

## 2. Key Takeaways from `todo/` Operational Audits (`2026-11-26`–`2026-11-27`)

- **Test Suite Performance (`todo/test-suite-audit-2026-11-26.md`, HAC `412bed21` baseline):**
  - `8,311` unit cases (`+25%` in 2 days) run across `unit (ubuntu-latest)` (`250 s` 3-run mean), `unit (macos-latest)`
    (`512 s` mean), and `Workspace survival` (`247 s` mean). No single slow test dominates; wall time tracks
    `summed test time / workers`.
  - Two structural bottlenecks dominate runtime: **(1) `45,157` git subprocess spawns** across `1,731` tests
    (`1,195 / 1,424 s` summed on macOS at `~25 ms/spawn` vs `~5 ms` on Linux), and **(2) quadratic
    `tmp_path_factory.mktemp` directory scanning** in 4 autouse fixtures (`56.4 s` for `4,200` empty tests vs `5.7 s`
    with constant-time numbered dirs).
  - Eight disjoint test-only batches (`0405`) project `ubuntu 250→170 s`, `macOS 512→339 s` (`~100–150 s` if git-heavy
    suite runs Linux-only), and `WS 247→172 s`; running a 20-file subset exposed missing `flow_repos` fixture wiring
    (closed in **`0491`**).
- **End-to-End Flow Timing (`todo/flow-time-audit-2026-11-26.md`, PRs `#296`–`#316`, plus `2026-11-27` audits):**
  - Active flow time in the `2026-11-26` baseline was **median `46 min` (`p90 102 min`)** for Claude flows vs
    **`23.7 min`** for Gemini self-doc flows (`#296`–`#307`), dominated by outage idle (`66.8%` of wall), Stage 3
    admission waits (`10.5%`), review-loop churn (`52%` of active time), and discarded executor turns (`11%`).
  - In `2026-11-27T12:14Z–15:46Z`, **`5/8` merged PRs wrote zero `todo/flow-*.log` files** (`0412`), `3` concurrent
    Stage 3 flows (`0599`, `0590`, `0619`) idled **`~181 min`** after `12:45Z` `exit code 3` halts (`0625`), **`365/509`
    (`71.7%`) check-runs** ran on bookkeeping/sync commits (`0638`, `0588`), and Stage 5 double CI waits pushed total
    Stage 5 to `14.77 min` (`#425`), `13.70 min` (`#85`), and `11.53 min` (`#426`, `0383`).

---

## 3. Remediation Matrix

### `holon-coherence` Findings

| Area                            |  Priority  | Status at `4d2cfcf8`                                                                                                                                                                                                                                                          | Bean                                |
| ------------------------------- | :--------: | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| Security / CA, Secrets & Cache  | `critical` | **Closed (`#63` + `#75`)**: `0o700`/`0o600` CA & `web_password`, raw `?token=` URLs removed (`endpoints.py`), `scrub_sensitive_data()` + `0o600` SQLite/WAL/SHM in `HybridCacheStore`.                                                                                        | ~~Bean `0524`~~ _(completed)_       |
| Security / Control Plane        | `critical` | **Closed (`#59`)**: local `Host` restriction, bearer auth on `POST /holon/api/mode`, dropped wildcard CORS, `wire_log_dir` containment, `GET /mode` fix.                                                                                                                      | ~~Bean `0525`~~ _(completed)_       |
| No-Harness-Refs Gate            | `critical` | **Closed (`#58`)**: fail-closed `check_no_harness_references.py` & CI workflow.                                                                                                                                                                                               | ~~Bean `0564`~~ _(completed)_       |
| SSE Streaming & Wire Tests      |   `high`   | **Closed (`#64`)**: SSE carry-buffer, incremental UTF-8 decode, dead self-assign removed, `tflow` / `HTTPServer` wire tests, offline Docker tests, `0` `TestCase`.                                                                                                            | ~~Bean `0526`~~ _(completed)_       |
| Three Append-Only Ledgers Check |   `high`   | **Closed (`#74`)**: `scripts/check_ledger_stores.py`, `scripts/check_ledger_rows_append_only.py`, and `.github/workflows/test-ledger-invariants.yml`.                                                                                                                         | ~~Bean `0563`~~ _(completed)_       |
| Ratchet Test Deadlock           |   `high`   | **Closed (`#77`)**: `test_module_budgets.py` allows `Ratchet notice:` stdout and `test_complexity_baseline.py` enforces `<= BASELINE_CEILING`.                                                                                                                                | ~~Bean `0623`~~ _(completed)_       |
| Import-Cycle CI Ratchet         |  `normal`  | **Closed (`#76`) / Follow-up (`0632`)**: `tests/test_import_cycle_ratchet.py` locks subpackages, **but** skips root modules (`payload_cleaner↔providers`, `payload_cleaner↔reduction_passes`, `hybrid_cache↔proxy`) -> **`0632`**.                                            | ~~Bean `0621`~~ / **`0632`**        |
| Silent `except: pass` & Ratchet |  `normal`  | **Closed (`#79`)**: all `3` remaining silent `except Exception: pass` blocks eliminated (`3→0`), live `broad_except` `30→26` after `#85`, and `tests/test_broad_except_ratchet.py` caps `19` modules.                                                                         | ~~Bean `0622`~~ _(completed)_       |
| Commit Trailers & Hook Setup    |  `normal`  | **Closed `0567` (`#78`) / Follow-up (`0633`)**: `check_commit_trailers.py` + `test-commit-trailers.yml` landed, **but** `#83,#67,#84,#85` squash merges still add 5 `Co-authored-by: Holon <Role> Agent` trailers on `main` -> **`0633`**.                                    | ~~Bean `0567`~~ / **`0633`**        |
| Extensibility & Import Cycles   |   `high`   | **Partial (`#84` broke `parsers↔providers` `3↔4→0`, added `ProviderFormat.matches()` & unified `detect_provider_name`)**: `commands↔container` (`4↔3`), `payload_cleaner↔providers` (`2↔4`), `payload_cleaner↔reduction_passes` (`1↔1`), `hybrid_cache↔proxy` (`1↔1`) remain. | Bean `0527` _(`in-progress`)_       |
| CI Parity & Bookkeeping Gate    |  `normal`  | Partial (`#58`, `#68`): `155/222` (`69.8%`) check-runs on `#83,#67,#84,#85` (`17/23` heads) ran full CI on bookkeeping/sync commits; `ci_bookkeeping_gate.py`, `check_self_explaining.py`, `module-budget-change` actor check remain.                                         | Bean `0588` _(`in-progress`, ext.)_ |
| Ledger Promotion & Backlog      |   `high`   | `#65` added `promote-ledger.yml`, **but** `HOLON_LEDGER_BOT_TOKEN` stays unconfigured and pending fragments grew `69→81` (`737` rows across `#83,#67,#84,#85`).                                                                                                               | Bean `0620` _(`todo`, extended)_    |
| Performance & DRY Drift         |  `normal`  | **Partial (`#72`, `#75`, `#80`, `#83` SSE finish, `#85` unified `metrics_math.py`)**: `17` `deepcopy` sites across 7 modules (`14` in `providers/`), `2x` token parse remain.                                                                                                 | Bean `0528` _(`in-progress`)_       |
| Config, Wire-Log Disk & Docker  |  `normal`  | **Closed `0529` / Follow-up (`0634`)**: `39` `os.getenv`/`os.environ` sites across 15 non-settings modules (`40` total across 16) + wire-log disk rotation remain -> **`0634`**.                                                                                              | ~~Bean `0529`~~ / **`0634`**        |
| Typing, Hygiene & Budgets       |  `normal`  | **Partial (`#67` extracted `dashboard.html`, `dashboard.py` `383→9L`)**: `2` stale overrides (`dashboard.py` `9/383L`, `metrics/aggregation.py` `150/222L`) -> **`0637` (new)**; `mypy`/`pyright` CI, `10` `*_self_doc.py` files remain.                                      | Bean `0530` + **`0637` (new)**      |

### `holon-agentic-coder` Findings

| Area                                 | Priority | Status at `1f3331637`                                                                                                                                                                                                                                                   | Existing / Reference Bean                                                |
| ------------------------------------ | :------: | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Layer Cycles & Hotspots              |  `high`  | `entrypoint↔flow` (`12↔15`), `knowledge↔ledger` (`4↔1`); `run_review_loop` sits at `CC=219` (`947/950L`) alongside `stages/review.py` (`47`), `turns.py` (`49`), `planner.py` (`49`)                                                                                    | Bean `0531` _(plus `0192`, `0152`, `0584`)_                              |
| Import-Cycle & Broad-Catch Ratchets  | `normal` | **Closed `0615` (`#415`)** + `0616` (`#414`); **new (`0635`)**: `test_import_cycle_ratchet.py` skips root modules (`calibration↔calibration_self_check`, `entrypoint↔review_target`, `flow↔review_target`, `flow↔flow_guard`)                                           | ~~`0615`~~, `0616`, **`0635` (new)**                                     |
| Orphaned Budget Overrides            | `normal` | `check_module_budgets.py` warns on deleted `calibration.py: 1608` and stale `flow/__init__.py: 522` (`27L` actual), plus lowerable overrides (`>350L`: `20`; `loop.py` `947/950L`)                                                                                      | Bean `0585` _(coord. `0489`, `0570`)_                                    |
| Security & Containers                |  `high`  | Docker `--memory`/`--cpus`/`--pids-limit`/`--read-only`, metadata CIDR block, `local_llm` modes, `git.py` `--`, `Dockerfile` pin remain                                                                                                                                 | Bean `0532` _(`in-progress`)_                                            |
| Typing, DRY & Env Drift              |  `high`  | `mypy`/`pyright` CI, `agent_runner.py`/`role_dispatcher.sh` normalizers, `HOLON_AGENT_EFFORT` drift, `os.environ` mutations, `lazy_exports_review.py` hub (`0543`) remain                                                                                               | Bean `0533` _(coord. `0223`, `0543`)_                                    |
| Resilience & Adapters                | `normal` | **Closed `0600` (`#418`)**; `0424` (`CF-0064`), `3` silent `except Exception: pass` blocks in `src/`, `sys.exit(1)` in library code remain                                                                                                                              | `0424`, `0534` _(closed `0600`)_                                         |
| Extensibility & Protocols            | `normal` | Runner registration spans ~8 files despite `RunnerSpec`, missing `GitForge` `Protocol`, `if/elif` stage dispatch in `pipeline.py` (`0535` parked)                                                                                                                       | Bean `0535` _(`in-progress`, rel. `0270`)_                               |
| Stage 4/5 Gates & Touch-Set Guards   |  `high`  | `0546`/`0628`/`0543` (`CF-0062/64/65` on `0424` & `#427`/`0607`), `0625` (181m `exit 3` idle across `0599/0590/0619`), **`0638` (new)**: Stage 4→5 triple push cancels CI & breaks `ci_merge_push_gate` on `stage 5 carry-over` (`#425` `12.3m`, `#426` `8.5m`), `0383` | `0546`, `0624`, `0625`, `0627`, `0628`, `0631`, `0383`, **`0638` (new)** |
| Observability, Telemetry & Readiness |  `high`  | **Closed `0611` (`#424`)**; **303** pending fragments (`4,357` rows) await `HOLON_LEDGER_BOT_TOKEN` -> **`0636` (new)**; `5/8` flows unlogged (`0412`); `0602`, `0626`, `0629` remain                                                                                   | ~~`0611`~~, **`0636` (new)**, `0412`, `0602`, `0626`, `0629`             |
| Hygiene, Test Speed & `# why:`       |  `high`  | **Partial (`#425` AST behavior gate, `#426` cleaned 12 test files)**: `31` `test_self_doc*.py` copies (`0601`), `1,022` test / `73` src func docstrings (`0153`), `834L` shims (`0537`), `109.5k` test LOC (`5,207` `test_*`, `0405`)                                   | `0601`, `0608`, `0153`, `0537`, `0405`                                   |

---

## 4. What's Been Done Well vs. What Could Be Better

### `holon-coherence`

- **Done Well:** Landed 4 high-impact PRs (`#83`, `#67`, `#84`, `#85`) with **`0` cancelled CI checks across `222`
  check-runs**, breaking `parsers↔providers` (`3↔4 → 0`) and adding structural `ProviderFormat.matches()` seams (`#84`,
  `0527`), unifying `CumulativeMetrics` and `OfflineMetricsAccumulator` into `metrics_math.py` (`#85`, `0528`, dropping
  `broad_except` `30→26`), fixing SSE line carry-buffering and EOF alignment (`#83`, `0528`), and extracting `376L`
  inline HTML into `proxy/dashboard.html` (`#67`, `0530`, `-461` net `src/` LOC), while maintaining `0` docstrings and
  `0` prose comments across all `154` Python files (`src/` + `tests/` + `scripts/`).
- **Could Be Better:** Prune the `2` stale `module_budgets.json` overrides (`dashboard.py` `9/383L`,
  `metrics/aggregation.py` `150/222L`) and fail on missing/stale overrides (**`0637`**); extend
  `test_import_cycle_ratchet.py` to cover root-level modules (`0632`) alongside `0527` breaking the remaining `4`
  cycles; migrate `39` non-settings `os.getenv`/`os.environ` sites and bound wire-log disk (`0634`); configure
  `HOLON_LEDGER_BOT_TOKEN` and drain **81** pending ledger fragments (`737` rows, `0620`); port `ci_bookkeeping_gate.py`
  (`155/222 = 69.8%` check-runs ran on bookkeeping/sync commits, `0588`); strip squash-merge `Co-authored-by:` agent
  trailers (`0633`); finish `0528` (`14` provider `deepcopy`s).

### `holon-agentic-coder`

- **Done Well:** Landed 4 PRs (`#415`, `#424`–`#426`), closing **`0615`** (`#415` subpackage import-cycle ratchet) and
  **`0611`** (`#424` debounced `promote-ledger.yml` + missing-token warning), shipping the AST behaviour-preservation CI
  gate (`#425`, `scripts/check_self_doc_behavior.py` + `test-self-doc-behavior.yml`), and stripping docstrings/comments
  across `12` more test files (`#426`, test docstrings `1,057→1,022`).
- **Could Be Better:** Eliminate Stage 4→5 triple pushes cancelling CI and breaking `ci_merge_push_gate` on
  `stage 5 carry-over` (`#425` `12.3m`, `#426` `8.5m`, **`0638`** + `0383`); fix `intent-check`
  (`lazy_exports_review.py`
  - fail-closed pre-flight, `0546`, `0543`) and parked/dynamic overlap guards (`0628`) after
    `CF-0062`/`CF-0064`/`CF-0065`; extend `test_import_cycle_ratchet.py` to cover the `4` missing root-module cycles
    (**`0635`**); configure `HOLON_LEDGER_BOT_TOKEN` and drain **303** pending fragments (`4,357` rows, **`0636`**);
    step down the model ladder on `exit code 3` quota stalls (`181m` idle across `0599`/`0590`/`0619`, `0625`); delete
    `31` redundant `test_self_doc*.py` copies (`0601`) and persist `todo/flow-*.log` (`5/8` missing, `0412`).

---

## 5. Curated Knowledge Base Additions

- **Bean `0538` (`holon-agentic-coder`):** **Completed (`#416`, `a2e378b50`)** — `554` total KB entries live in
  `holon-knowledge/kb/` (`+1` from `#415` `KB-failure-13b45264.json`).
- **Bean `0539` (`holon-coherence`):** **Completed (`#62`, `85af07d`)** — `82` total KB entries live in
  `holon-knowledge/kb/` (`+1` from `#67` `KB-failure-4e2fdf8109d94bc9.json`, `0` `index.json` manifests).
