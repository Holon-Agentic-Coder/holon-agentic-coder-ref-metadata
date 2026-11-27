# Holon Ecosystem Architecture & Source-Code Audit (2026-11)

**Original Audit:** 2026-11-26 (`holon-agentic-coder@f1e18bcd`, `holon-coherence@18084f3`)  
**Previous Refresh:** 2026-11-27 (`holon-agentic-coder@2a83e4cc7`, `holon-coherence@52019174f`)  
**Refreshed:** 2026-11-27 (`holon-agentic-coder@2a83e4cc7`; `holon-coherence@4a02926b`, +7 PRs `#76`–`#82` since
`52019174f`)  
**Remediation Beans:** `0524`–`0539`, `0584`–`0588`, `0614`–`0634` (plus cross-referenced `0383`, `0405`, `0412`,
`0491`, `0546`, `0558`, `0563`, `0564`, `0596`, `0601`, `0602`, `0610`, `0611`, and existing beans)

---

## 1. Executive Comparison & Scorecard

| Metric (`src/` baseline)            |                                                                   `holon-agentic-coder` |                                                                               `holon-coherence` |
| ----------------------------------- | --------------------------------------------------------------------------------------: | ----------------------------------------------------------------------------------------------: |
| Source files / LOC (`src/` only)    |                              382 `.py` / 52,432 LOC (`425` / `60,008` incl. `scripts/`) |                                        66 `.py` / 11,553 LOC (`76` / `13,278` incl. `scripts/`) |
| Test files / scale                  |                        449 `.py` / 108,979 LOC (`5,177` `test_*` / `8,075` total `def`) |                                  76 `.py` / 20,439 LOC (`1,067` `test_*` / `1,469` total `def`) |
| Functions / return-typed (`src/`)   |                                                                           3,052 / 99.5% |                                                                                     578 / 98.6% |
| Files > 200L / > 400L (`src/`)      |                                     61 / 17 (default budget 350L; `>350L`: 20, 2 stale) |                                              19 / 8 (default budget 200L; `>350L`: 11, 0 stale) |
| Max cyclomatic complexity           |                                                                 219 (`run_review_loop`) |                                                              24 (`normalize_anthropic_request`) |
| Bare `except:` / `except Exception` |                                                   0 / 137 (`3` silent `pass` in `src/`) |                                                            0 / 30 (`0` silent `pass` in `src/`) |
| Docstrings / comments (`src/`)      | 73 func docstrings (+17 mod, +6 cls), 582/668 `# why:` (87.1%); tests: 1,057 docstrings | 0 docstrings / 0 prose comments (`11` `# noqa` in `src/`, `0/0` across `src`/`tests`/`scripts`) |

> **Progress since `52019174f` (`7` Coherence PRs `#76`–`#82`; HAC remains at `2a83e4cc7`):** `holon-coherence` closed
> **`0621`** (`#76` added `tests/test_import_cycle_ratchet.py`), **`0623`** (`#77` unblocked strict module-budget
> shrinking and `# noqa` ceiling reductions), **`0567`** (`#78` added `check_commit_trailers.py`,
> `.githooks/commit-msg`, and `test-commit-trailers.yml`), **`0622`** (`#79` eliminated all `3` remaining silent
> `except Exception: pass` blocks and locked per-module `broad_except` caps across 19 modules, `33→30`), **`0529`**
> (`#81` added frozen `CoherenceSettings.from_env()` in `settings.py` + `#82` pinned multi-arch Docker digests, frozen
> `uv.lock` install, TCP `HEALTHCHECK`, and `.dockerignore`), and landed the single-copy
> `clean_payload -> payload_cleaner` slice of **`0528`** (`#80`). Overall, **`holon-coherence` rose to
> `8.0 / 10 (+0.1)`**, widening its lead over **`holon-agentic-coder` (`7.5 / 10`)**, while exposing root-module cycle
> blind spots in `test_import_cycle_ratchet.py` (**`0632`**), `36` remaining `os.getenv` call sites outside
> `settings.py` (**`0634`**), GitHub squash-merge `Co-authored-by:` trailers (**`0633`**), and pending ledger fragments
> growing `48→69` (`0620`).

|  #  | Aspect                                     | `holon-agentic-coder` |  `holon-coherence`  | Summary Takeaway                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| :-: | ------------------------------------------ | :-------------------: | :-----------------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|  1  | Clean Architecture & Layer Boundaries      |       6.6 / 10        |   7.7 / 10 (+0.1)   | HAC `entrypoint ↔ flow` (`12↔15`) and `knowledge ↔ ledger` (`4↔1`) remain (`0531`; `#415`/`0615` awaiting merge). Coherence `#76` locked `commands↔container` (`4↔3`) and `parsers↔providers` (`3↔4`), **but** skipped root-level modules (`payload_cleaner↔providers` `2↔4`, `payload_cleaner↔reduction_passes` `1↔1`, and newly surfaced `hybrid_cache↔proxy` `1↔1` -> **`0632`**); `0527` hit `CF-0061` (**`0631`**) and re-cut onto `4a02926b`. |
|  2  | Modularity, Cohesion & File Sizing         |       7.4 / 10        |   7.7 / 10 (+0.1)   | HAC holds `20` `>350L` `src/` modules (`1` stale `flow/__init__.py: 522/27L`, `1` missing `calibration.py: 1608`, `0585`; `loop.py` `947/950L`). Coherence `#77` (`0623`) unblocked strict module-budget shrinking under frozen `module_budgets.json`; `19` `>200L` / `8` `>400L` (`0` stale/missing overrides) remain.                                                                                                                             |
|  3  | Complexity & Control Flow                  |       5.8 / 10        |      8.0 / 10       | HAC `run_review_loop` sits at `CC=219` (`947L`) alongside `planner.py:main` (`49`), `turns.py:run_turn` (`49`), and `stages/review.py` (`47`) (`0192`, `0531`). Coherence `#77` unblocked `# noqa` reductions (`<= BASELINE_CEILING`); max CC stays `24` (`normalize_anthropic_request`) with `11` inline `# noqa` lines in `src/`.                                                                                                                 |
|  4  | Clean Code & Idiomatic Python              |       7.4 / 10        |   7.4 / 10 (+0.1)   | HAC `#422` unified `normalise_agent_id` & `git.parse_numstat` (`99.5%` return-typed). Coherence `#80` cut `clean_payload→payload_cleaner` to single-copy (`14` `deepcopy` sites remain in `providers/`, `0528`) and `#81` added `settings.py` (`98.6%`, `570/578` return-typed; `36` `os.getenv` sites remain -> **`0634`**; `mypy`/`pyright` CI & `10` `*_self_doc.py` remain, `0530`).                                                            |
|  5  | Intention-Revealing & Self-Doc Code        |       8.1 / 10        |      8.3 / 10       | HAC `#417` added `measure_deleted_why_comments.py` (`73` existing `src/` func docstrings, `582/668` `# why:`, `1,057` test docstrings under `0153`). Coherence maintains `0` docstrings and `0` explanatory comments across all `66` `src/`, `76` `tests/`, and `10` `scripts/` files (`11` `# noqa`, `16` `# type: ignore`/`# noqa`, `10` shebangs + `1` `# noqa`).                                                                                |
|  6  | Extensibility & Plug-in Seams              |       6.8 / 10        |      7.7 / 10       | HAC `RunnerSpec`/`GitForge` (`0535`) parked on `#412` (`CF-0056`). Coherence `ProviderFormat.matches()` & `KNOWN_PROVIDERS` (`0527`) re-cut onto `4a02926b` after `CF-0061` (**`0631`**).                                                                                                                                                                                                                                                           |
|  7  | Testability & Verification Quality         |       7.9 / 10        |   8.2 / 10 (+0.2)   | HAC holds `5,177` `test_*` cases (`0405`, `0491`, `0601`). Coherence `#76`–`#82` added `+6` test files / `+1,378` test LOC (`1,019→1,067` `test_*` cases / `0` `TestCase`), covering cycle ratchets, shrink/reduction ratchets, commit trailers, `broad_except` caps, single-copy cleaning, typed settings, and Dockerfile/packaging, with `0` cancelled CI runs across `222` check-runs.                                                           |
|  8  | Error Handling, Resilience & Failure Modes |       8.2 / 10        |   8.2 / 10 (+0.3)   | HAC `broad_except` ratcheted (`137`, `3` silent `pass`, `0534`, `0624`, `0627`, **`0631`**). Coherence `#79` (`0622`) eliminated all `3` remaining silent `except Exception: pass` blocks (`3→0`), dropped `broad_except` `33→30`, and locked per-module AST caps across `19` modules (`tests/test_broad_except_ratchet.py`).                                                                                                                       |
|  9  | Security, Isolation & Secret Hygiene       |       8.4 / 10        |   8.6 / 10 (+0.2)   | HAC awaits Docker quotas, `local_llm` modes, `git.py` `--`, `Dockerfile` pin (`0532`). Coherence `#82` pinned multi-arch `mitmproxy:12.2.3` + `uv:0.9.5` `@sha256:` digests, installed frozen `uv.lock` deps without `pip`, added a TCP `HEALTHCHECK`, and tightened `.dockerignore`; `#78` added `check_commit_trailers.py` + `test-commit-trailers.yml` (squash-merge `Co-authored-by:` trailers & hook setup remain -> **`0633`**).              |
| 10  | Observability, Provenance & Config         |       8.1 / 10        |      7.7 / 10       | HAC holds `553` KB entries (`291` pending fragments `0611`, `0/14` wrapper logs `0412`, `0602`, `0629`). Coherence `#81` centralized `CoherenceSettings.from_env()` for 3 callers (`36` env sites & wire-log disk rotation remain -> **`0634`**), **offset** by pending fragments growing `48→69` (`0620`) and `132/222` (`59.5%`) check-runs spent on bookkeeping commits (`0588`).                                                                |
|     | **Overall Score**                          |     **7.5 / 10**      | **8.0 / 10 (+0.1)** | **At `4a02926b` vs `2a83e4cc7`, Coherence (`8.0`) widens its lead over HAC (`7.5`)**, closing `0621`, `0622`, `0623`, `0567`, and `0529` across `#76`–`#82` (`0` cancelled CI runs); remaining Coherence priorities are `0527` + **`0632`** (5 cycles), `0620` (`69` pending fragments), **`0634`** (`36` env sites + wire-log disk), `0588` (`ci_bookkeeping_gate`), and `0528` (`14` provider `deepcopy`s, `translation.py`, `metrics`).          |

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

| Area                            |  Priority  | Status at `4a02926b`                                                                                                                                                                                                                                                                 | Bean                                |
| ------------------------------- | :--------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------- |
| Security / CA, Secrets & Cache  | `critical` | **Closed (`#63` + `#75`)**: `0o700`/`0o600` CA & `web_password`, raw `?token=` URLs removed (`endpoints.py`), `scrub_sensitive_data()` + `0o600` SQLite/WAL/SHM in `HybridCacheStore`.                                                                                               | ~~Bean `0524`~~ _(completed)_       |
| Security / Control Plane        | `critical` | **Closed (`#59`)**: local `Host` restriction, bearer auth on `POST /holon/api/mode`, dropped wildcard CORS, `wire_log_dir` containment, `GET /mode` fix.                                                                                                                             | ~~Bean `0525`~~ _(completed)_       |
| No-Harness-Refs Gate            | `critical` | **Closed (`#58`)**: fail-closed `check_no_harness_references.py` & CI workflow.                                                                                                                                                                                                      | ~~Bean `0564`~~ _(completed)_       |
| SSE Streaming & Wire Tests      |   `high`   | **Closed (`#64`)**: SSE carry-buffer, incremental UTF-8 decode, dead self-assign removed, `tflow` / `HTTPServer` wire tests, offline Docker tests, `0` `TestCase`.                                                                                                                   | ~~Bean `0526`~~ _(completed)_       |
| Three Append-Only Ledgers Check |   `high`   | **Closed (`#74`)**: `scripts/check_ledger_stores.py`, `scripts/check_ledger_rows_append_only.py`, and `.github/workflows/test-ledger-invariants.yml`.                                                                                                                                | ~~Bean `0563`~~ _(completed)_       |
| Ratchet Test Deadlock           |   `high`   | **Closed (`#77`)**: `test_module_budgets.py` allows `Ratchet notice:` stdout and `test_complexity_baseline.py` enforces `<= BASELINE_CEILING`.                                                                                                                                       | ~~Bean `0623`~~ _(completed)_       |
| Import-Cycle CI Ratchet         |  `normal`  | **Closed (`#76`) / Follow-up (`0632`)**: `tests/test_import_cycle_ratchet.py` locks subpackage cycles (`commands↔container`, `parsers↔providers`), **but** skips root modules (`payload_cleaner↔providers`, `payload_cleaner↔reduction_passes`, `hybrid_cache↔proxy`) -> **`0632`**. | ~~Bean `0621`~~ / **`0632`**        |
| Silent `except: pass` & Ratchet |  `normal`  | **Closed (`#79`)**: all `3` remaining silent `except Exception: pass` blocks eliminated (`3→0`), live `broad_except` `33→30`, and `tests/test_broad_except_ratchet.py` caps `19` modules.                                                                                            | ~~Bean `0622`~~ _(completed)_       |
| Commit Trailers & Hook Setup    |  `normal`  | **Closed `0567` (`#78`) / Follow-up (`0633`)**: `check_commit_trailers.py` + `test-commit-trailers.yml` landed, **but** GitHub squash-merge adds `Co-authored-by: Holon <Role> Agent` trailers on `main` and local `.githooks/` lack setup -> **`0633`**.                            | ~~Bean `0567`~~ / **`0633`**        |
| Extensibility & Import Cycles   |   `high`   | Open: `detect_provider` divergence, closed `ProviderName` Literal, hardcoded `KNOWN_PROVIDERS`, `parsers↔providers` (`3↔4`), `commands↔container` (`4↔3`), `payload_cleaner↔providers` (`2↔4`), `payload_cleaner↔reduction_passes` (`1↔1`), `hybrid_cache↔proxy` (`1↔1`).            | Bean `0527` _(`in-progress`, ext.)_ |
| CI Parity & Bookkeeping Gate    |  `normal`  | Partial (`#58` `no-harness-references`, `#68` removed `kb/*/index.json`): `132/222` (`59.5%`) check-runs on `#76`–`#82` ran full CI on bookkeeping commits; `ci_bookkeeping_gate.py`, `check_self_explaining.py`, `module-budget-change` actor check remain.                         | Bean `0588` _(`in-progress`, ext.)_ |
| Ledger Promotion & Backlog      |   `high`   | `#65` added `promote-ledger.yml`, **but** `HOLON_LEDGER_BOT_TOKEN` stays unconfigured and pending fragments grew `48→69` (`+21` across `#76`–`#82`).                                                                                                                                 | Bean `0620` _(`todo`, extended)_    |
| Performance & DRY Drift         |  `normal`  | **Partial (`#72`, `#75`, `#80` single-copy `clean_payload→payload_cleaner`)**: `14` `deepcopy` sites remain in `providers/`, `2x` token parse, `translation.py` EOF/finish (`#70`), `metrics` (`#66`).                                                                               | Bean `0528` _(`in-progress`, ext.)_ |
| Config, Wire-Log Disk & Docker  |  `normal`  | **Closed `0529` (`#69`, `#73`, `#81` `settings.py`, `#82` pinned multi-arch `Dockerfile`/`.dockerignore`/`HEALTHCHECK`) / Follow-up (`0634`)**: `36` `os.getenv` sites across 11 modules + wire-log disk rotation remain -> **`0634`**.                                              | ~~Bean `0529`~~ / **`0634`**        |
| Typing & Hygiene                |  `normal`  | **Partial (`#71` fixed `_check_structural_parity` & experimental cleanups)**: no `mypy`/`pyright` in CI, `10` redundant `*_self_doc.py` files, `_compat.py` probe & barrels, inline HTML (`#67`).                                                                                    | Bean `0530` _(`in-progress`)_       |

### `holon-agentic-coder` Findings

| Area                                 | Priority | Status at `2a83e4cc7`                                                                                                                                                                                                                                                      | Existing / Reference Bean                                                |
| ------------------------------------ | :------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Layer Cycles & Hotspots              |  `high`  | `entrypoint↔flow` (`12↔15`), `knowledge↔ledger` (`4↔1`); `run_review_loop` grew (`CC=207→219`, `947/950L`) after `#412`, alongside `stages/review.py` (`47`), `turns.py` (`49`), `planner.py` (`49`)                                                                       | Bean `0531` _(plus `0192`, `0152`, `0584`)_                              |
| Import-Cycle & Broad-Catch Ratchets  | `normal` | **Partial (`#414` merged)**: `0616` landed `test_broad_except_ratchet.py` (`82` modules / `13` packages, live `138→137`; narrowing non-boundary catches remains); `0615` (PR `#415`) `3/3 APPROVED` + `CLEAN`, awaiting merge                                              | Beans `0615`, `0616` _(`in-progress`, PR `#415`)_                        |
| Orphaned Budget Overrides            | `normal` | `check_module_budgets.py` warns on deleted `calibration.py: 1608` and stale `flow/__init__.py: 522` (`27L` actual), plus lowerable overrides (`>350L`: `20`; `loop.py` `947/950L`)                                                                                         | Bean `0585` _(coord. `0489`, `0570`)_                                    |
| Security & Containers                |  `high`  | Docker `--memory`/`--cpus`/`--pids-limit`/`--read-only`, metadata CIDR block, `local_llm` modes, `git.py` `--`, `Dockerfile` pin remain                                                                                                                                    | Bean `0532` _(`in-progress`)_                                            |
| Typing, DRY & Env Drift              |  `high`  | **Partial (`#422` merged)**: delegated `local_llm.normalize_agent_id` & extracted `git.parse_numstat` across 4 callers; `mypy`/`pyright` CI, `agent_runner.py`/`role_dispatcher.sh` normalizers, `HOLON_AGENT_EFFORT` drift, `os.environ` mutations remain                 | Bean `0533` _(`in-progress`, coord. `0223`)_                             |
| Resilience & Adapters                | `normal` | **Closed `0600` (`#418`)** host-push retry + branch retention; `3` silent `except Exception: pass` blocks in `src/` (`agent_runner.py:415`, `flow/pipeline.py:393`, `launcher/containers.py:209`), `sys.exit(1)` in library code, `GitHubAdapter` gaps remain              | Bean `0534` _(closed `0600`)_                                            |
| Extensibility & Protocols            | `normal` | Runner registration spans ~8 files despite `RunnerSpec`, missing `GitForge` `Protocol`, `if/elif` stage dispatch in `pipeline.py` (`0535` parked on `#412` in `CF-0056`)                                                                                                   | Bean `0535` _(`in-progress`, rel. `0270`)_                               |
| Stage 4/5 Gates & Touch-Set Guards   |  `high`  | **Closed `0618` (`#412`)**; `0617` (`#421`), `0619`, `0624` (`#413`,`#420`,`#421`,`#423` halts), `0625`, `0627`, `0628`, `0630` remain; **new (`0631`)**: Stage 3 `--from-stage execute` skips `plan_branch` target-sync (`CF-0061`)                                       | `0617`, `0619`, `0624`, `0625`, `0627`, `0628`, `0630`, **`0631` (new)** |
| Observability, Telemetry & Readiness |  `high`  | **Closed `0594` (`#419`)** & **`0538` (`#416`)**; **291** pending fragments (`0611`, `#413` halted); `0/14` wrapper logs (`0412`); `#419` merged mid-Stage-5 without `_calibration.md` (`0602`); **new (`0629`)**: per-stage/turn tokens & timings; `new_bean.py` (`0626`) | `0536`, `0611`, `0412`, `0383`, `0602`, `0626`, **`0629` (new)**         |
| Hygiene, Test Speed & `# why:`       |  `high`  | **`0608` partial (`#417`)** added `measure_deleted_why_comments.py`; `834L` shims (`0537`), `109k` test LOC (`5,177` `test_*`, `0405`, `0491`), `10` `test_self_doc_tests_*.py` copies (`0601`, `#420` halted `CF-0058`), `1,057` test / `73` src func docstrings (`0153`) | `0537`, `0608`, `0153`, `0405`, `0491`, `0601`                           |

---

## 4. What's Been Done Well vs. What Could Be Better

### `holon-coherence`

- **Done Well:** Landed 7 PRs (`#76`–`#82`) cleanly with **`0` cancelled CI checks across `222` check-runs**, closing
  **`0621`** (`#76` subpackage import-cycle ratchet), **`0623`** (`#77` unblocking budget-shrinking & `# noqa`
  reductions), **`0567`** (`#78` commit-trailer check & workflow), **`0622`** (`#79` `3→0` silent `except: pass`,
  `33→30` `broad_except`, AST ratchet across `19` modules), and **`0529`** (`#81` `CoherenceSettings.from_env()` + `#82`
  multi-arch digests, frozen `uv.lock`, TCP `HEALTHCHECK`, `.dockerignore`), plus landing single-copy
  `clean_payload → payload_cleaner` (`#80`, `0528`) while keeping `0` docstrings and `0` prose comments across all `152`
  Python files (`src/` + `tests/` + `scripts/`).
- **Could Be Better:** Extend `test_import_cycle_ratchet.py` to cover root-level modules (`payload_cleaner↔providers`,
  `payload_cleaner↔reduction_passes`, `hybrid_cache↔proxy`, **`0632`**) alongside `0527` breaking all 5 cycles; migrate
  the **36** remaining `os.getenv` call sites across 11 modules to `CoherenceSettings.from_env()` and add wire-log disk
  rotation (**`0634`**); configure `HOLON_LEDGER_BOT_TOKEN` and drain **69** pending ledger fragments (`0620`); port
  `ci_bookkeeping_gate.py` (`132/222` check-runs on `#76`–`#82` ran full CI on bookkeeping commits, `0588`); strip
  squash-merge `Co-authored-by:` agent trailers & wire `.githooks/commit-msg` (**`0633`**); finish `0528` (`14` provider
  `deepcopy`s, `translation.py`, `metrics`) and `0530`.

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
