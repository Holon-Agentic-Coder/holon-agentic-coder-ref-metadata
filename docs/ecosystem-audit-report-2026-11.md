# Holon Ecosystem Architecture & Source-Code Audit (2026-11)

**Original Audit:** 2026-11-26 (`holon-agentic-coder@f1e18bcd`, `holon-coherence@18084f3`)  
**Previous Refresh:** 2026-11-27 (`holon-agentic-coder@0d8d1249f`, `holon-coherence@52019174f`)  
**Refreshed:** 2026-11-27 (`holon-agentic-coder@2a83e4cc7`, +7 PRs `#412`, `#414`, `#416`–`#419`, `#422` since
`0d8d1249f`; `holon-coherence@52019174f` baseline, with `#76`–`#81` merged concurrently at `11:45–11:46Z` queued for the
next refresh)  
**Remediation Beans:** `0524`–`0539`, `0584`–`0588`, `0614`–`0629` (plus cross-referenced `0383`, `0405`, `0412`,
`0491`, `0546`, `0558`, `0563`, `0564`, `0596`, `0601`, `0602`, `0610`, `0611`, and existing beans)

---

## 1. Executive Comparison & Scorecard

| Metric (`src/` baseline)            |                                                                   `holon-agentic-coder` |                                              `holon-coherence` |
| ----------------------------------- | --------------------------------------------------------------------------------------: | -------------------------------------------------------------: |
| Source files / LOC (`src/` only)    |                              382 `.py` / 52,432 LOC (`425` / `60,008` incl. `scripts/`) |       65 `.py` / 11,399 LOC (`74` / `13,029` incl. `scripts/`) |
| Test files / scale                  |                        449 `.py` / 108,979 LOC (`5,177` `test_*` / `8,075` total `def`) | 70 `.py` / 19,061 LOC (`1,019` `test_*` / `1,384` total `def`) |
| Functions / return-typed (`src/`)   |                                                                           3,052 / 99.5% |                                                    568 / 98.6% |
| Files > 200L / > 400L (`src/`)      |                                     61 / 17 (default budget 350L; `>350L`: 20, 2 stale) |             19 / 8 (default budget 200L; `>350L`: 11, 0 stale) |
| Max cyclomatic complexity           |                                                                 219 (`run_review_loop`) |                             24 (`normalize_anthropic_request`) |
| Bare `except:` / `except Exception` |                                                   0 / 137 (`3` silent `pass` in `src/`) |                           0 / 33 (`3` silent `pass` in `src/`) |
| Docstrings / comments (`src/`)      | 73 func docstrings (+17 mod, +6 cls), 582/668 `# why:` (87.1%); tests: 1,057 docstrings |       0 docstrings / 0 comments (`src/`, `tests/`, `scripts/`) |

> **Progress since `0d8d1249f` (`7` HAC PRs `#412`, `#414`, `#416`–`#419`, `#422`; Coherence `52019174f` baseline):**
> `holon-agentic-coder` closed **`0538`** (`#416` added the 7 curated 2026-11 architecture patterns and failure modes to
> `holon-knowledge/kb/`, `546→553` entries), **`0618`** (`#412` fixed Stage 4 clean-tree carried-finding crashes and
> empty review ledger commits), **`0600`** (`#418` added bounded backoff host-push retry and preserved
> `execution_branch`), and **`0594`** (`#419` added `scripts/measure_ci_head_durations.py`), plus landed the
> broad-except AST ratchet in **`0616`** (`#414`, live `broad_except` `138→137`), the deleted-reason scanner in
> **`0608`** (`#417` `scripts/measure_deleted_why_comments.py`), and DRY helper consolidation in **`0533`** (`#422`
> `agent_defaults.normalise_agent_id` & `git.parse_numstat`). Overall, **`holon-agentic-coder` stayed `7.5 / 10 (0.0)`**
> (`+0.1` in Clean Code, Testability, Error Handling offset by `-0.1` in Complexity from `run_review_loop` `CC 207→219`
> and Observability from `#419` merging mid-Stage-5 without `_calibration.md` and pending fragments `270→291`).

|  #  | Aspect                                     | `holon-agentic-coder` | `holon-coherence`  | Summary Takeaway                                                                                                                                                                                                                                                                                                                                                                                                                        |
| :-: | ------------------------------------------ | :-------------------: | :----------------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|  1  | Clean Architecture & Layer Boundaries      |       6.6 / 10        |      7.6 / 10      | HAC `entrypoint ↔ flow` (`12↔15`) and `knowledge ↔ ledger` (`4↔1`) remain (`0531`; `#415`/`0615` import-cycle ratchet `3/3 APPROVED` + `CLEAN`, awaiting merge). Coherence `commands ↔ container` (`4↔3`), `parsers ↔ providers` (`3↔4`), and `TYPE_CHECKING` `reduction_passes → payload_cleaner` at `52019174f` (`0527`).                                                                                                             |
|  2  | Modularity, Cohesion & File Sizing         |       7.4 / 10        |      7.6 / 10      | HAC holds `20` `>350L` `src/` modules (`1` stale `flow/__init__.py: 522/27L`, `1` missing `calibration.py: 1608`, `0585`), while `flow/review/loop.py` grew `941→947/950L` after `#412`. Coherence at `52019174f` holds `19` `>200L` / `8` `>400L`, `0` stale/missing overrides.                                                                                                                                                        |
|  3  | Complexity & Control Flow                  |    5.8 / 10 (-0.1)    |      8.0 / 10      | HAC `run_review_loop` rose `CC=207→219` (`947L`) after `#412`, alongside `planner.py:main` (`49`), `turns.py:run_turn` (`49`), and `stages/review.py` (`47`) (`0192`, `0531`); Coherence max CC stays `24` (`normalize_anthropic_request`).                                                                                                                                                                                             |
|  4  | Clean Code & Idiomatic Python              |    7.4 / 10 (+0.1)    |      7.3 / 10      | HAC `#422` (`0533` slice) unified `local_llm.normalize_agent_id → agent_defaults.normalise_agent_id` and extracted `git.parse_numstat` across 4 callers, with `99.5%` (`3,037/3,052`) return-typed; `mypy`/`pyright` CI & `env_registry` runtime alignment remain (`0533`). Coherence `98.6%` (`560/568`) return-typed (`52019174f`).                                                                                                   |
|  5  | Intention-Revealing & Self-Doc Code        |       8.1 / 10        |      8.3 / 10      | HAC `#417` (`0608` slice) added `scripts/measure_deleted_why_comments.py` (`329L`), and all 7 merged PRs added `0` new docstrings; `73` existing `src/` func docstrings, `582/668` `# why:` (`87.1%`), and `1,057` test docstrings remain under `0153`. Coherence keeps `0`/`0` across all `65` `src/`, `70` `tests/`, `9` `scripts/` files.                                                                                            |
|  6  | Extensibility & Plug-in Seams              |       6.8 / 10        |      7.7 / 10      | HAC `RunnerSpec`/`GitForge` (`0535`) parked on `#412` (`CF-0056`, Stage 2 widened into `loop.py`). Coherence `ProviderFormat.matches()` & `KNOWN_PROVIDERS` (`0527`) at `52019174f`.                                                                                                                                                                                                                                                    |
|  7  | Testability & Verification Quality         |    7.9 / 10 (+0.1)    |      8.0 / 10      | HAC `#414` added `test_broad_except_ratchet.py` CI gate, `+7` test files / `+1,985` test LOC (`5,177` `test_*`, `10,706 passed` recorded on `#419`), and offline hermetic measurement tests (`#417`, `#419`); `0405`, `0491`, `0601` (`#420` halted `CF-0058`) remain open. Coherence holds `1,019` `test_*` cases / `0` `TestCase` at `52019174f`.                                                                                     |
|  8  | Error Handling, Resilience & Failure Modes |    8.2 / 10 (+0.1)    |      7.9 / 10      | HAC `#412` (`0618`) fixed clean-tree carried-finding crashes, `#414` (`0616`) ratcheted `broad_except` (`82` modules / `13` packages, live `138→137`), and `#418` (`0600`) added bounded host-push retry + branch retention; `3` silent `pass` blocks remain (`0534`), and Stage 4 `touch_set_violation` halted `#413`, `#420`, `#421` (`0624`, **`0627`**).                                                                            |
|  9  | Security, Isolation & Secret Hygiene       |       8.4 / 10        |      8.4 / 10      | Unchanged — HAC awaits Docker quotas, `local_llm` modes, `git.py` `--`, `Dockerfile` pin (`0532`). Coherence closed `0524`, `0525`, `0564` by `52019174f`.                                                                                                                                                                                                                                                                              |
| 10  | Observability, Provenance & Config         |    8.1 / 10 (-0.1)    |      7.7 / 10      | HAC `#416` (`0538`) added 7 curated audit KB entries (`553` total) and `#417`/`#419` added deleted-`# why:` & per-head CI duration scanners — **but** `#419` merged mid-Stage-5 without `_calibration.md` (`0602`), pending fragments grew **`270→291`** (`0611`, `#413` halted), `0/14` flows wrote `todo/flow-*.log` (`0412`), and tokens/turn timings stay unrecorded (**`0629`**). Coherence holds `48` pending fragments (`0620`). |
|     | **Overall Score**                          |  **7.5 / 10 (0.0)**   | **7.9 / 10 (0.0)** | **At `2a83e4cc7` vs `52019174f`, Coherence (`7.9`) holds its lead over HAC (`7.5`)**; HAC gains in resilience (`#412`,`#414`,`#418`) and DRY (`#422`) were offset by `loop.py` complexity (`207→219`), `#419` missing calibration, pending fragment growth (`270→291`), and 3 Stage 4 `touch_set_violation` halts (`#413`,`#420`,`#421`).                                                                                               |

---

## 2. Key Takeaways from `todo/` Operational Audits (`2026-11-26`)

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
    (tracked in **`0491`**).
- **End-to-End Flow Timing (`todo/flow-time-audit-2026-11-26.md`, PRs `#296`–`#316`, plus `2026-11-27` audits):**
  - Active flow time in the `2026-11-26` baseline was **median `46 min` (`p90 102 min`)** for Claude flows vs
    **`23.7 min`** for Gemini self-doc flows (`#296`–`#307`), dominated by outage idle (`66.8%` of wall), Stage 3
    admission waits (`10.5%`), review-loop churn (`52%` of active time), and discarded executor turns (`11%`).
  - In `2026-11-27T07:49Z–10:49Z`, **`100%` of launched flows wrote zero `todo/flow-*.log` files** (`0412`), `6`
    concurrent flows idled **`110.8 min` median (`126.2 min` max)** on `gemini-4-neon` `quota` `exit code 3` halts
    without automatic ladder step-down (`0625`), and Stage 5 CI waits caused `17.6–27.0 min` budget overruns (`#72`,
    `#73`; `0383`).

---

## 3. Remediation Matrix

### `holon-coherence` Findings

| Area                            |  Priority  | Status at `52019174f`                                                                                                                                                                                                                                      | Bean                                |
| ------------------------------- | :--------: | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| Security / CA, Secrets & Cache  | `critical` | **Closed (`#63` + `#75`)**: `0o700`/`0o600` CA & `web_password`, raw `?token=` URLs removed (`endpoints.py`), `scrub_sensitive_data()` + `0o600` SQLite/WAL/SHM in `HybridCacheStore`.                                                                     | ~~Bean `0524`~~ _(completed)_       |
| Security / Control Plane        | `critical` | **Closed (`#59`)**: local `Host` restriction, bearer auth on `POST /holon/api/mode`, dropped wildcard CORS, `wire_log_dir` containment, `GET /mode` fix.                                                                                                   | ~~Bean `0525`~~ _(completed)_       |
| SSE Streaming & Wire Tests      |   `high`   | **Closed (`#64`)**: SSE carry-buffer, incremental UTF-8 decode, dead self-assign removed, `tflow` / `HTTPServer` wire tests, offline Docker tests, `0` `TestCase`.                                                                                         | ~~Bean `0526`~~ _(completed)_       |
| No-Harness-Refs Gate            | `critical` | **Closed (`#58`)**: fail-closed `check_no_harness_references.py` & CI workflow.                                                                                                                                                                            | ~~Bean `0564`~~ _(completed)_       |
| Three Append-Only Ledgers Check |   `high`   | **Closed (`#74`)**: `scripts/check_ledger_stores.py`, `scripts/check_ledger_rows_append_only.py`, and `.github/workflows/test-ledger-invariants.yml`.                                                                                                      | ~~Bean `0563`~~ _(completed)_       |
| Extensibility & Import Cycles   |   `high`   | Open: `detect_provider` divergence, closed `ProviderName` Literal, hardcoded `KNOWN_PROVIDERS`, `parsers↔providers` (`3↔4`), `commands↔container` (`4↔3`), `TYPE_CHECKING` `reduction_passes→payload_cleaner` (`0527` slice 1 blocked on `0623`).          | Bean `0527` _(`in-progress`)_       |
| Import-Cycle CI Ratchet         |  `normal`  | `in-progress`: AST package-import graph CI ratchet (`0621` Stage 3 halted at `08:42Z` on quota `exit code 3`, queued for resume).                                                                                                                          | Bean `0621` _(`in-progress`)_       |
| Ratchet Test Deadlock           |   `high`   | `in-progress`: allow `Ratchet notice:` stdout and `<= BASELINE_CEILING` in `test_module_budgets.py` & `test_complexity_baseline.py` (`0623` halted at `08:42Z` on quota `exit code 3`).                                                                    | Bean `0623` _(`in-progress`)_       |
| CI Parity & KB Index            |  `normal`  | Partial (`#58` `no-harness-references`, **`#68` removed `kb/*/index.json`**): remaining `ci_bookkeeping_gate.py`, `check_self_explaining.py`, `module-budget-change` actor check.                                                                          | Bean `0588` _(`in-progress`)_       |
| Ledger Promotion & Backlog      |   `high`   | `#65` added `promote-ledger.yml`, **but** `HOLON_LEDGER_BOT_TOKEN` stays unconfigured and pending fragments grew `27→48` (`+21` across `#68,#69,#71–#75`).                                                                                                 | Bean `0620` _(`todo`, extended)_    |
| Performance & DRY Drift         |  `normal`  | **Partial (`#72` fixed `ab_test.py` `mkdtemp` & `cryptography`; `#75` fixed `3x normalize_payload` & unused SQLite index)**: remaining `4x deepcopy`, `2x` token parse, `translation.py` EOF/finish (`#70` halted `CF-0054`), `metrics` (`#66` `CF-0044`). | Bean `0528` _(`in-progress`, ext.)_ |
| Config, Resilience & Docker     |  `normal`  | **Partial (`#69` bounded wire-log futures; `#73` CA `logger.warning` & `resolve_build_context`)**: remaining scattered/frozen `os.getenv` (`CoherenceSettings.from_env()`), `pip` vs `uv.lock`.                                                            | Bean `0529` _(`in-progress`)_       |
| Silent `except: pass` & Ratchet |  `normal`  | **Partial (`#69` fixed `wire_log.py:69`, `4→3` silent `pass`, `34→33` `broad_except`)**: replace remaining **3** silent `pass` blocks (`commands/ca.py:40`, `commands/docker_ops.py:81,169`) and add AST broad-catch CI ratchet.                           | Bean `0622` _(`in-progress`, ext.)_ |
| Typing & Hygiene                |  `normal`  | **Partial (`#71` fixed `_check_structural_parity` & experimental cleanups)**: no `mypy`/`pyright` in CI, `10` redundant `*_self_doc.py` files (`1,206L`), `_compat.py` probe & barrels, inline HTML (`#67` halted on `0623`).                              | Bean `0530` _(`in-progress`)_       |

### `holon-agentic-coder` Findings

| Area                                 | Priority | Status at `2a83e4cc7`                                                                                                                                                                                                                                                      | Existing / Reference Bean                                          |
| ------------------------------------ | :------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| Layer Cycles & Hotspots              |  `high`  | `entrypoint↔flow` (`12↔15`), `knowledge↔ledger` (`4↔1`); `run_review_loop` grew (`CC=207→219`, `947/950L`) after `#412`, alongside `stages/review.py` (`47`), `turns.py` (`49`), `planner.py` (`49`)                                                                       | Bean `0531` _(plus `0192`, `0152`, `0584`)_                        |
| Import-Cycle & Broad-Catch Ratchets  | `normal` | **Partial (`#414` merged)**: `0616` landed `test_broad_except_ratchet.py` (`82` modules / `13` packages, live `138→137`; narrowing non-boundary catches remains); `0615` (PR `#415`) `3/3 APPROVED` + `CLEAN`, awaiting merge                                              | Beans `0615`, `0616` _(`in-progress`, PR `#415`)_                  |
| Orphaned Budget Overrides            | `normal` | `check_module_budgets.py` warns on deleted `calibration.py: 1608` and stale `flow/__init__.py: 522` (`27L` actual), plus lowerable overrides (`>350L`: `20`; `loop.py` `947/950L`)                                                                                         | Bean `0585` _(coord. `0489`, `0570`)_                              |
| Security & Containers                |  `high`  | Docker `--memory`/`--cpus`/`--pids-limit`/`--read-only`, metadata CIDR block, `local_llm` modes, `git.py` `--`, `Dockerfile` pin remain                                                                                                                                    | Bean `0532` _(`in-progress`)_                                      |
| Typing, DRY & Env Drift              |  `high`  | **Partial (`#422` merged)**: delegated `local_llm.normalize_agent_id` & extracted `git.parse_numstat` across 4 callers; `mypy`/`pyright` CI, `agent_runner.py`/`role_dispatcher.sh` normalizers, `HOLON_AGENT_EFFORT` drift, `os.environ` mutations remain                 | Bean `0533` _(`in-progress`, coord. `0223`)_                       |
| Resilience & Adapters                | `normal` | **Closed `0600` (`#418`)** host-push retry + branch retention; `3` silent `except Exception: pass` blocks in `src/` (`agent_runner.py:415`, `flow/pipeline.py:393`, `launcher/containers.py:209`), `sys.exit(1)` in library code, `GitHubAdapter` gaps remain              | Bean `0534` _(closed `0600`)_                                      |
| Extensibility & Protocols            | `normal` | Runner registration spans ~8 files despite `RunnerSpec`, missing `GitForge` `Protocol`, `if/elif` stage dispatch in `pipeline.py` (`0535` parked on `#412` in `CF-0056`)                                                                                                   | Bean `0535` _(`in-progress`, rel. `0270`)_                         |
| Stage 4/5 Gates & Touch-Set Guards   |  `high`  | **Closed `0618` (`#412`)**; `0617` (`#421`), `0619`, `0624` (`#413`,`#420`,`#421` halts), `0625` remain; **new (`0627`)**: Stage 4 resolver prompt omits Touch Set (`CF-0054`,`0055`,`0058`,`0059`); **new (`0628`)**: pre-launch parked Touch Set guard (`CF-0057`)       | `0617`, `0619`, `0624`, `0625`, **`0627` (new)**, **`0628` (new)** |
| Observability, Telemetry & Readiness |  `high`  | **Closed `0594` (`#419`)** & **`0538` (`#416`)**; **291** pending fragments (`0611`, `#413` halted); `0/14` wrapper logs (`0412`); `#419` merged mid-Stage-5 without `_calibration.md` (`0602`); **new (`0629`)**: per-stage/turn tokens & timings; `new_bean.py` (`0626`) | `0536`, `0611`, `0412`, `0383`, `0602`, `0626`, **`0629` (new)**   |
| Hygiene, Test Speed & `# why:`       |  `high`  | **`0608` partial (`#417`)** added `measure_deleted_why_comments.py`; `834L` shims (`0537`), `109k` test LOC (`5,177` `test_*`, `0405`, `0491`), `10` `test_self_doc_tests_*.py` copies (`0601`, `#420` halted `CF-0058`), `1,057` test / `73` src func docstrings (`0153`) | `0537`, `0608`, `0153`, `0405`, `0491`, `0601`                     |

---

## 4. What's Been Done Well vs. What Could Be Better

### `holon-coherence`

- **Done Well:** Landed 7 more PRs (`#68`, `#69`, `#71`–`#75`), closing **`0524`** (`#75` removed `?token=` URLs and
  added `HybridCacheStore` scrubbing + `0o600` DB/WAL/SHM permissions) and **`0563`** (`#74` CI-enforced 3-ledger and
  append-only invariants), plus bounding `wire_log` futures (`#69`), logging CA sync errors & `importlib.resources`
  build-context resolution (`#73`), fixing `ab_test.py` `mkdtemp` leaks & pruning unused `cryptography` (`#72`),
  retiring `kb/*/index.json` (`#68`), and keeping `0` docstrings / `0` noise comments across all `144` Python files
  (`src/` + `tests/` + `scripts/`) with `0` cancelled CI runs across all `10` recent PRs (`#66`–`#75`).
- **Could Be Better:** Unblock **`0623`** (`test_module_budgets.py` / `test_complexity_baseline.py` ratchet deadlock) so
  `0527` (`commands↔container` `4↔3`, `parsers↔providers` `3↔4`) and `#67` (`dashboard.py`) can land; configure
  `HOLON_LEDGER_BOT_TOKEN` and drain the **48** pending ledger fragments (`0620`); replace the **3** remaining silent
  `except Exception: pass` blocks (`0622`); land `0621` import-cycle ratchet; resolve `#70` (`CF-0054`) and finish
  `0528`–`0530` / `0588`.

### `holon-agentic-coder`

- **Done Well:** Landed 7 PRs (`#412`, `#414`, `#416`–`#419`, `#422`) in ~1 hour post-reset, closing **`0538`** (`#416`,
  `553` KB entries), **`0618`** (`#412`, Stage 4 clean-tree crash fixed), **`0600`** (`#418`, bounded host-push retry +
  branch retention), and **`0594`** (`#419`, per-head CI duration script), while locking the broad-except AST ratchet
  across 82 modules (`#414`, `138→137`), adding the deleted-reason comment scanner (`#417`), and unifying `local_llm`
  agent-ID normalization and `git.parse_numstat` (`#422`).
- **Could Be Better:** Pass the plan Touch Set to the Stage 4 resolver prompt (**`0627`**) alongside post-violation
  rollback (`0624`) after 3 HAC PRs (`#413`, `#420`, `#421`) halted on Stage 4 `touch_set_violation`; add a shared
  on-disk parked Touch Set pre-flight check (**`0628`**) to stop `overlap-scheduling` repeats (`CF-0056`, `CF-0057`);
  require `P-*_calibration.md` in readiness gating (`0602`) after `#419` merged mid-Stage-5 with `2` pending macOS
  checks; keep `loop.py` (`947/950L`, `CC=219`) below its ceiling (`0531`/`0192`); drain `291` pending ledger fragments
  (`0611`); persist `todo/flow-*.log` (`0412`) and structured token/timing telemetry (**`0629`**).

---

## 5. Curated Knowledge Base Additions

- **Bean `0538` (`holon-agentic-coder`):** **Completed (`#416`, `a2e378b50`)** — 7 curated pattern and failure-mode KB
  entries live (`553` total KB entries in `holon-knowledge/kb/`).
- **Bean `0539` (`holon-coherence`):** **Completed (`#62`, `85af07d`)** — 7 curated pattern and failure-mode KB entries
  live (`80` total KB entries in `holon-knowledge/kb/`, `0` `index.json` manifests after `#68`).
