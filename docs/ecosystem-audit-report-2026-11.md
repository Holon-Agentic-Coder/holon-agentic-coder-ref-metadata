# Holon Ecosystem Architecture & Source-Code Audit (2026-11)

**Original Audit:** 2026-11-26 (`holon-agentic-coder@f1e18bcd`, `holon-coherence@18084f3`)  
**Previous Refresh:** 2026-11-27 (`holon-agentic-coder@1f3331637`, `holon-coherence@4d2cfcf8`)  
**Refreshed:** 2026-11-28 (`holon-agentic-coder@27b4197e77`, +23 PRs
`#428, #430–#434, #437–#440, #442–#444, #446–#449, #451–#456`; `holon-coherence@bcad21c86e`, +8 PRs
`#86–#88, #90–#94`)  
**Remediation Beans:** `0524`–`0539`, `0584`–`0588`, `0614`–`0639` (plus cross-referenced `0383`, `0405`, `0412`,
`0458`, `0491`, `0543`, `0546`, `0558`, `0563`, `0564`, `0596`, `0601`, `0608`, `0610`, `0611`, `0612`, and existing
beans)

---

## 1. Executive Comparison & Scorecard

| Metric (`src/` baseline)            |                                                                 `holon-agentic-coder` |                                                                               `holon-coherence` |
| ----------------------------------- | ------------------------------------------------------------------------------------: | ----------------------------------------------------------------------------------------------: |
| Source files / LOC (`src/` only)    |                            388 `.py` / 54,039 LOC (`432` / `62,058` incl. `scripts/`) |                                        68 `.py` / 11,183 LOC (`78` / `12,931` incl. `scripts/`) |
| Test files / scale                  |                      432 `.py` / 112,592 LOC (`5,226` `test_*` / `8,240` total `def`) |                                  69 `.py` / 21,195 LOC (`1,097` `test_*` / `1,490` total `def`) |
| Functions / return-typed (`src/`)   |                                                                         3,163 / 99.5% |                                                                                     603 / 98.7% |
| Files > 200L / > 400L (`src/`)      |                                   61 / 17 (default budget 350L; `>350L`: 20, 1 stale) |                                              16 / 7 (default budget 200L; `>350L`: 10, 3 stale) |
| Max cyclomatic complexity           |                                                               219 (`run_review_loop`) |                                                              24 (`normalize_anthropic_request`) |
| Bare `except:` / `except Exception` |                                                 0 / 131 (`2` silent `pass` in `src/`) |                                                            0 / 26 (`0` silent `pass` in `src/`) |
| Docstrings / comments (`src/`)      | 73 func docstrings (+17 mod, +6 cls), 608/690 `# why:` (88.1%); tests: 638 docstrings | 0 docstrings / 0 prose comments (`10` `# noqa` in `src/`, `0/0` across `src`/`tests`/`scripts`) |

> **Progress since `1f3331637` / `4d2cfcf8` (`23` HAC PRs `#428..#456`; `8` Coherence PRs `#86..#94`):**
> `holon-coherence` broke `commands ↔ container` (`#87` + `#92`, leaving `3` cycles), cut provider `deepcopy`s `17→2`
> (`#88`), pruned `10→1` `*_self_doc.py` files (`#86`), cut env reads `40→19` across `11` modules (`#91` + `#94`), added
> `--fail-on-stale-overrides` (`#90`), and wired `make install-hooks` (`#93`), lifting **`holon-coherence` to
> `8.2 / 10 (+0.1)`**. `holon-agentic-coder` closed **`0601`** (`#428` deleting `30` `test_self_doc*.py` copies),
> **`0635`** (`#432` root import-cycle ratchet), **`0638`** (`#440`), **`0612`** (`#456`), **`0368`** (`#451`), broke
> `ledger ↔ knowledge` (`#439`), decomposed `turns.py:run_turn` (`CC=49→4`, `#442`), landed `GitForge`/stage registry
> (`#431`), sped up git-heavy unit tests (`#443`, `#448`, `#449`), and restored `# why:` comments (`#454`, `#455`),
> lifting **`holon-agentic-coder` to `7.6 / 10 (+0.1)`** — **however**, burst-merging `23` PRs (`23:38Z–23:45Z`) broke
> **`Test - Unit` and `Test - Stress` on `hac/main` (`27b4197e7`)** with `4` cross-PR failures
> (`preflight ↔ preflight_cooldown` cycle `#432+#456` and `test_plan_scope_guard.py` missing `assumptions` `#430+#438`,
> **new Bean `0639`**).

|  #  | Aspect                                     | `holon-agentic-coder` |  `holon-coherence`  | Summary Takeaway                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| :-: | ------------------------------------------ | :-------------------: | :-----------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
|  1  | Clean Architecture & Layer Boundaries      |    6.8 / 10 (+0.1)    |   8.1 / 10 (+0.2)   | HAC `#439` broke `knowledge↔ledger` (`4↔1 → 0`), `#432` (`0635`) locked root cycles, **but** `#456` introduced `preflight↔preflight_cooldown` (`1↔4`) breaking `main` (`0639`); `entrypoint↔flow` (`12↔15`), `flow↔review_target` (`8↔4`), `flow↔flow_guard` (`4↔1`), `calibration↔calibration_self_check` (`2↔1`), `entrypoint↔review_target` (`1↔1`) remain. Coherence `#87`+`#92` broke `commands↔container` (`4↔3 → 0`); `3` cycles remain (`0632` in-flight). |
|  2  | Modularity, Cohesion & File Sizing         |       7.4 / 10        |   8.0 / 10 (+0.1)   | HAC holds `20` `>350L` `src/` modules (`1` stale `flow/__init__.py: 27/522L`, `1` missing `calibration.py: 1608`, `0585`; `loop.py` `948/950L`, `turns.py` `892→766L`). Coherence dropped `>200L` (`17→16`, `#92` shrank `docker_ops.py` `221→174L`) and `#90` added `--fail-on-stale-overrides`, leaving `3` stale overrides (`docker_ops.py`, `aggregation.py`, `dashboard.py`) for `0637` Slice 2.                                                              |
|  3  | Complexity & Control Flow                  |    6.0 / 10 (+0.2)    |      8.0 / 10       | HAC `#442` decomposed `turns.py:run_turn` (`CC=49 → 4`); `run_review_loop` stays `CC=219` (`948L`) alongside `planner.py:main` (`49`) and `stages/review.py` (`47`) (`0192`, `0531`). Coherence max CC stays `24` (`normalize_anthropic_request`) with `10` inline `# noqa` lines in `src/`.                                                                                                                                                                       |
|  4  | Clean Code & Idiomatic Python              |    7.5 / 10 (+0.1)    |   7.9 / 10 (+0.3)   | HAC holds `99.5%` return-typed (`3,148/3,163`) and dropped `broad_except` (`137→131`, `#444`+`#453`, `agent_runner.py` `782→651L`). Coherence `#88` cut `deepcopy` sites (`17→2` across `2` files) and `#91`+`#94` cut env reads (`40→19` across `11` modules, `595/603 = 98.7%` return-typed).                                                                                                                                                                    |
|  5  | Intention-Revealing & Self-Doc Code        |    8.5 / 10 (+0.3)    |   8.5 / 10 (+0.2)   | HAC `#428` (`0601`) deleted `30` redundant `test_self_doc*.py` copies (`31→2`) and `#454`+`#455` restored `# why:` comments (`584→608` in `src/`, `603` in `tests/`, test docstrings `1,022→638`); `82` non-why `src/` comments remain (`0608`). Coherence `#86` consolidated `10→1` `test_repo_self_doc.py` while keeping `0` docstrings and `0` prose comments across all `147` `.py` files (`10` `# noqa` in `src/`, `10` in `scripts/`).                       |
|  6  | Extensibility & Plug-in Seams              |    7.1 / 10 (+0.3)    |      8.0 / 10       | HAC `#431` (`0535`) landed `GitForge` Protocol + stage dispatch registry in `flow/pipeline.py` (`RunnerSpec` single-source `#441` parked behind `#428`). Coherence holds `ProviderFormat.matches()` seams (`0527` continues).                                                                                                                                                                                                                                      |
|  7  | Testability & Verification Quality         |    7.9 / 10 (-0.1)    |   8.4 / 10 (+0.1)   | HAC `#443, #448, #449` cut git spawns (`5,207→5,226` `test_*`, `unit (ubuntu)` `~250→163–240s`), **but** `Test - Unit` and `Test - Stress` are **RED on `main` (`27b4197e7`)** (`4` cross-PR failures, **`0639`**) with `210` cancelled CI check-runs. Coherence grew `1,082→1,097` `test_*` cases (`69` files), `0` cancelled CI runs across `240` check-runs, `main` green.                                                                                      |
|  8  | Error Handling, Resilience & Failure Modes |    8.4 / 10 (+0.2)    |      8.3 / 10       | HAC `#444`+`#453` reduced `broad_except` (`137→131`) & silent `pass` (`3→2`); `#433` added exhausted-ladder `blocked_on`; `#446`/`#447` fixed Stage 3 plan refresh & parked-flow admission; `#451` fixed submodule gitfile; `#456` added cooldown marker; `#430`+`#437` tightened Stage 2/4 scope guards (`CF-0066..0082` still hit `17` scope/overlap halts). Coherence holds `0` silent `pass` (`26` `broad_except`).                                            |
|  9  | Security, Isolation & Secret Hygiene       |       8.4 / 10        |   8.7 / 10 (+0.1)   | HAC awaits `0532` (Docker quotas, `local_llm` modes, `git.py` `--`, `Dockerfile` pin). Coherence `#93` (`0633` s1) wired `make install-hooks` for `.githooks/commit-msg`; `31/31` new squash merges across both repos still carry 5 `Co-authored-by:` agent trailers (`0633`).                                                                                                                                                                                     |
| 10  | Observability, Provenance & Config         |       8.1 / 10        |   7.7 / 10 (+0.1)   | HAC `#434` (replan feedback file), `#440` (`ci_merge_push_gate`), `#452` (unique CAL IDs), `#438` (`assumptions` required), offset by `303→372` pending fragments (`4,985` rows **`0636`**), `19/23` unlogged flows (`0412`), `992/1,552` bookkeeping check-runs. Coherence `#91`+`#94` cut env reads (`40→19`, `0634`), offset by `81→105` pending fragments (`881` rows `0620`) and `160/240` bookkeeping check-runs (`0588`).                                   |
|     | **Overall Score**                          |  **7.6 / 10 (+0.1)**  | **8.2 / 10 (+0.1)** | **At `bcad21c86e` vs `27b4197e77`, Coherence rises to `8.2 / 10` (+0.1) and HAC rises to `7.6 / 10` (+0.1)**; **top urgent priority is `0639` (fix red `Test - Unit` / `Test - Stress` on `hac/main` `27b4197e7`)**, followed by `0546`/`0624`/`0628` (`CF-0066..0082`), `0458` (burst-merge recheck), `0588`, `0636`/`0620`, `0637`, and `0412`/`0383`.                                                                                                           |

---

## 2. Key Takeaways from `todo/` Operational Audits (`2026-11-26`–`2026-11-28`)

- **Test Suite Performance (`todo/test-suite-audit-2026-11-26.md`, HAC `412bed21` baseline vs `27b4197e7`):**
  - `8,311` unit cases (`+25%` in 2 days) ran across `unit (ubuntu-latest)` (`250 s` 3-run mean), `unit (macos-latest)`
    (`512 s` mean), and `Workspace survival` (`247 s` mean), dominated by `45,157` git subprocess spawns and quadratic
    `tmp_path_factory.mktemp` scanning.
  - `#443`, `#448`, and `#449` landed three remaining git-heavy unit-test speedups (`unit (ubuntu-latest)` `163–240 s`,
    `unit (macos-latest)` shards `214–397 s` across `#451, #454–#456`, `0405`).
- **End-to-End Flow Timing (`todo/flow-time-audit-2026-11-26.md` + `2026-11-28T00:01Z` fifth-merge audit):**
  - Across the `31` newly merged PRs (`#428..#456`, `#86..#94`), **`27/31` PRs (`19/23` HAC + `8/8` Coherence) wrote
    zero `todo/flow-*.log` files** (`0412`), `5` HAC PRs (`#442–#444, #448, #449`) lost **`~838.5 min`** to an
    `18:06Z–20:51Z` idle gap, and **`1,152/1,792` (`64.3%`) check-runs** (`78/121` CI-tested heads) ran on bookkeeping
    commits with `210` cancelled HAC check-runs (`0` in Coherence).
  - Stage 5 calibration work took `19–36 s` (`median 27.0 s`), yet final-head CI wait on `chore(calibration)` took
    `median 303.0 s` (`5.05 min`, `max 933.0 s` / `15.55 min` on `COH #88`; `Stage 5` total `median 5.87 min`,
    `max 16.73 min`, `0383`, `0588`).

---

## 3. Remediation Matrix

### `holon-coherence` Findings

| Area                            |  Priority  | Status at `bcad21c86e`                                                                                                                                                                                                                                                                 | Bean                                |
| ------------------------------- | :--------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| Security / CA, Secrets & Cache  | `critical` | **Closed (`#63` + `#75`)**: `0o700`/`0o600` CA & `web_password`, raw `?token=` URLs removed (`endpoints.py`), `scrub_sensitive_data()` + `0o600` SQLite/WAL/SHM in `HybridCacheStore`.                                                                                                 | ~~Bean `0524`~~ _(completed)_       |
| Security / Control Plane        | `critical` | **Closed (`#59`)**: local `Host` restriction, bearer auth on `POST /holon/api/mode`, dropped wildcard CORS, `wire_log_dir` containment, `GET /mode` fix.                                                                                                                               | ~~Bean `0525`~~ _(completed)_       |
| No-Harness-Refs Gate            | `critical` | **Closed (`#58`)**: fail-closed `check_no_harness_references.py` & CI workflow.                                                                                                                                                                                                        | ~~Bean `0564`~~ _(completed)_       |
| SSE Streaming & Wire Tests      |   `high`   | **Closed (`#64`)**: SSE carry-buffer, incremental UTF-8 decode, dead self-assign removed, `tflow` / `HTTPServer` wire tests, offline Docker tests, `0` `TestCase`.                                                                                                                     | ~~Bean `0526`~~ _(completed)_       |
| Three Append-Only Ledgers Check |   `high`   | **Closed (`#74`)**: `scripts/check_ledger_stores.py`, `scripts/check_ledger_rows_append_only.py`, and `.github/workflows/test-ledger-invariants.yml`.                                                                                                                                  | ~~Bean `0563`~~ _(completed)_       |
| Ratchet Test Deadlock           |   `high`   | **Closed (`#77`)**: `test_module_budgets.py` allows `Ratchet notice:` stdout and `test_complexity_baseline.py` enforces `<= BASELINE_CEILING`.                                                                                                                                         | ~~Bean `0623`~~ _(completed)_       |
| Import-Cycle CI Ratchet         |  `normal`  | **Closed `0621` (`#76`) / In-Flight (`0632`)**: `0632` launched on `bcad21c86e` to cover root modules (`payload_cleaner↔providers`, `payload_cleaner↔reduction_passes`, `hybrid_cache↔proxy`).                                                                                         | ~~Bean `0621`~~ / **`0632`**        |
| Silent `except: pass` & Ratchet |  `normal`  | **Closed (`#79`)**: `0` silent `except Exception: pass` blocks (`broad_except` `26`), `tests/test_broad_except_ratchet.py` caps `19` modules.                                                                                                                                          | ~~Bean `0622`~~ _(completed)_       |
| Commit Trailers & Hook Setup    |  `normal`  | **Partial (`#93` added `make install-hooks`)**: `8/8` new Coherence squash merges (`#86..#88, #90..#94`) still add 5 `Co-authored-by: Holon <Role> Agent` trailers on `main`; Slice 2 (`install_git_hooks.py` + uniform author) remains.                                               | Bean `0633` _(`in-progress`)_       |
| Extensibility & Import Cycles   |   `high`   | **Partial (`#87` + `#92` broke `commands↔container` `4↔3→0`, `#84` broke `parsers↔providers` `3↔4→0`)**: `payload_cleaner↔providers` (`2↔4`), `payload_cleaner↔reduction_passes` (`1↔1`), `hybrid_cache↔proxy` (`1↔1`) remain.                                                         | Bean `0527` _(`in-progress`)_       |
| CI Parity & Bookkeeping Gate    |  `normal`  | Partial (`#58`, `#68`): `160/240` (`66.7%`) check-runs on `#86..#94` (`16/24` heads) ran full CI on bookkeeping commits (`#88` `15.55m`); `coherence-bookkeeping-gate` now unblocked after `#86` merged (`CF-0066`).                                                                   | Bean `0588` _(`in-progress`, ext.)_ |
| Ledger Promotion & Backlog      |   `high`   | `#65` added `promote-ledger.yml`, **but** `HOLON_LEDGER_BOT_TOKEN` stays unconfigured and pending fragments grew `81→105` files (`881` rows across `#86..#94`).                                                                                                                        | Bean `0620` _(`todo`, extended)_    |
| Performance & DRY Drift         |  `normal`  | **Completed (`#72, #75, #80, #83, #85, #88`)**: `#88` cut `deepcopy` sites in `src/` from `17→2` across `2` files (`metrics_math.py`, `_common.py`, SSE EOF aligned).                                                                                                                  | ~~Bean `0528`~~ _(completed)_       |
| Config, Wire-Log Disk & Docker  |  `normal`  | **Partial (`#91` + `#94` cut env reads `40→19` across `11` modules)**: `18` non-settings env sites across `10` modules (`ca.py`, `docker_ops.py`, `endpoints.py`, `metrics.py`, `agents.py`, `start.py`, `lifecycle.py`, `host_local.py`) + wire-log disk rotation remain.             | Bean `0634` _(`in-progress`, ext.)_ |
| Typing, Hygiene & Budgets       |  `normal`  | **Partial (`#86` pruned `10→1` `*_self_doc.py`, `#90` added `--fail-on-stale-overrides`)**: `3` stale overrides (`docker_ops.py` `174/221L`, `aggregation.py` `150/222L`, `dashboard.py` `9/383L`) fail `--fail-on-stale-overrides` -> **`0637` Slice 2**; `mypy`/`pyright` CI remain. | Bean `0530` + **`0637` (ext.)**     |

### `holon-agentic-coder` Findings

| Area                                 | Priority | Status at `27b4197e77`                                                                                                                                                                                                                                                          | Existing / Reference Bean                              |
| ------------------------------------ | :------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| Burst-Merge `main` Breakage          |  `high`  | **RED on `main` (`27b4197e77`)**: `Test - Unit` (`4` failures) & `Test - Stress` fail from `#432+#456` (`preflight↔preflight_cooldown` cycle `1↔4`) and `#430+#438` (`test_plan_scope_guard.py` missing `assumptions`).                                                         | **`0639` (new)** + `0458` _(ext.)_                     |
| Layer Cycles & Hotspots              |  `high`  | **Partial (`#439` broke `knowledge↔ledger`, `#442` cut `turns.py:run_turn` `CC=49→4`)**: `entrypoint↔flow` (`12↔15`), `flow↔review_target` (`8↔4`), `flow↔flow_guard` (`4↔1`), `calibration↔calibration_self_check` (`2↔1`), `run_review_loop` (`CC=219`, `948L`) remain.       | Bean `0531` _(plus `0192`, `0152`, `0584`)_            |
| Import-Cycle & Broad-Catch Ratchets  | `normal` | **Closed `0635` (`#432`)** + `0616` (`#414`); broken on `main` (`27b4197e77`) by `#456` (`preflight↔preflight_cooldown` -> **`0639`**).                                                                                                                                         | ~~`0635`~~, `0616`, **`0639` (new)**                   |
| Orphaned Budget Overrides            | `normal` | `check_module_budgets.py` warns on deleted `calibration.py: 1608` and stale `flow/__init__.py: 522` (`27L` actual), plus `20` `>350L` modules (`loop.py` `948/950L`, `turns.py` `766/892L`).                                                                                    | Bean `0585` _(coord. `0489`, `0570`)_                  |
| Security & Containers                |  `high`  | Docker `--memory`/`--cpus`/`--pids-limit`/`--read-only`, metadata CIDR block, `local_llm` modes, `git.py` `--`, `Dockerfile` pin remain; `23/23` squash merges carry 5 `Co-authored-by:` agent trailers (`0633`).                                                               | Bean `0532` _(`in-progress`)_, `0633`                  |
| Typing, DRY & Env Drift              |  `high`  | `mypy`/`pyright` CI, `agent_runner.py`/`role_dispatcher.sh` normalizers, `HOLON_AGENT_EFFORT` drift, `os.environ` mutations, `lazy_exports_review.py` hub (`0543`) remain.                                                                                                      | Bean `0533` _(coord. `0223`, `0543`)_                  |
| Resilience & Adapters                | `normal` | **Partial (`#444`+`#453` `broad_except` `137→131`, `#451` submodule gitfile, `#456` cooldown)**: `2` silent `except Exception: pass` (`flow/pipeline.py:392`, `launcher/containers.py:255`), `sys.exit(1)` in library code remain.                                              | `0424`, `0534` _(ext.)_                                |
| Extensibility & Protocols            | `normal` | **Partial (`#431` landed `GitForge` Protocol + stage dispatch registry)**: `RunnerSpec` single-source (`#441`) parked behind `#428` (now merged).                                                                                                                               | Bean `0535` _(`in-progress`, rel. `0270`)_             |
| Stage 4/5 Gates & Touch-Set Guards   |  `high`  | **Closed `0638` (`#440`), `0612` (`#456`)**; `0546`/`0624`/`0628` hit `17` new CF rows (`CF-0066..0082`: `8` Stage 4 `touch_set_violation` halts incl. `975L` `test_preflight.py`, `0590↔0617` deadlock); `#430`+`#437` landed at `23:38–23:41Z`; `0625`, `0383` remain.        | `0546`, `0624`, `0625`, `0627`, `0628`, `0631`, `0383` |
| Observability, Telemetry & Readiness |  `high`  | **372** pending fragments (`4,985` rows) await `HOLON_LEDGER_BOT_TOKEN` (**`0636`** ext.); `19/23` HAC flows unlogged (`0412` ext.); `#434`, `#438`, `#452` landed; `0602`, `0626`, `0629` remain.                                                                              | **`0636`**, `0412`, `0602`, `0626`, `0629`             |
| Hygiene, Test Speed & `# why:`       |  `high`  | **Closed `0601` (`#428` deleted `30` `test_self_doc*.py` copies `31→2`)**; `#443/#448/#449` cut git spawns (`0405`); `#454/#455` restored `# why:` (`src/` `584→608`, test docstrings `1,022→638`); `0608` s4/s5 (`#457`), `82` non-why `src/` comments, `0153`, `0537` remain. | ~~`0601`~~, `0608`, `0153`, `0537`, `0405`             |

---

## 4. What's Been Done Well vs. What Could Be Better

### `holon-coherence`

- **Done Well:** Landed `8` PRs (`#86–#88, #90–#94`) with **`0` cancelled CI checks across `240` check-runs** and green
  `main`, breaking `commands↔container` (`#87`+`#92`, leaving `3` cycles), cutting provider `deepcopy` sites `17→2`
  (`#88`), consolidating `10→1` `*_self_doc.py` files (`#86`), migrating `40→19` env reads to `CoherenceSettings`
  (`#91`+`#94`), adding `--fail-on-stale-overrides` (`#90`), and wiring `make install-hooks` (`#93`), while keeping `0`
  docstrings and `0` prose comments across all `147` Python files.
- **Could Be Better:** Prune the `3` stale `module_budgets.json` overrides (`docker_ops.py` `174/221L`, `aggregation.py`
  `150/222L`, `dashboard.py` `9/383L`, `0637` Slice 2); finish `0632` (root-module cycle ratchet) and `0527` (`3`
  cycles); migrate remaining `18` non-settings env sites + wire-log disk bounds (`0634`); configure
  `HOLON_LEDGER_BOT_TOKEN` and drain **105** pending fragments (`881` rows, `0620`); finish `0588` (`160/240 = 66.7%`
  check-runs ran on bookkeeping commits); strip squash-merge `Co-authored-by:` agent trailers (`0633`).

### `holon-agentic-coder`

- **Done Well:** Landed `23` PRs (`#428..#456`), closing **`0601`** (`#428` deleting `30` `test_self_doc*.py` copies),
  **`0635`** (`#432` root import-cycle ratchet), **`0638`** (`#440`), **`0612`** (`#456`), and **`0368`** (`#451`);
  breaking `ledger↔knowledge` (`#439`), decomposing `turns.py:run_turn` (`CC=49→4`, `#442`), landing `GitForge`/stage
  registry (`#431`), cutting git-heavy unit tests (`#443, #448, #449`), narrowing `broad_except` (`137→131`,
  `#444`+`#453`), and restoring `# why:` comments (`#454`, `#455`, test docstrings `1,022→638`).
- **Could Be Better:** Fix **RED `Test - Unit` and `Test - Stress` on `main` (`27b4197e7`)** immediately (**`0639`**:
  `preflight↔preflight_cooldown` cycle + `test_plan_scope_guard.py` `assumptions`) and add burst-merge speculative
  recheck (`0458`); fix `intent-check` (`>=900L` test-cap proximity warning + companion enforcement, `0546`, `0624`) and
  parked-deadlock pruning (`0628`) after `17` new `CF-0066..0082` halts; configure `HOLON_LEDGER_BOT_TOKEN` and drain
  **372** pending fragments (`4,985` rows, `0636`); preserve `todo/flow-*.log` (`19/23` missing, `0412`) and finish
  `0608` Slice 4/5 (`#457`).

---

## 5. Curated Knowledge Base Additions

- **Bean `0538` (`holon-agentic-coder`):** **Completed (`#416`, `a2e378b50`)** — `555` total KB entries live in
  `holon-knowledge/kb/` (`537` failure modes + `18` patterns).
- **Bean `0539` (`holon-coherence`):** **Completed (`#62`, `85af07d`)** — `82` total KB entries live in
  `holon-knowledge/kb/` (`75` failure modes + `7` patterns, `0` `index.json` manifests).
