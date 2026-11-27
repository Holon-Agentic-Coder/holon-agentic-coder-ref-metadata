# Holon Ecosystem Architecture & Source-Code Audit (2026-11)

**Original Audit:** 2026-11-26 (`holon-agentic-coder@f1e18bcd`, `holon-coherence@18084f3`)  
**Previous Refresh:** 2026-11-27 (`holon-agentic-coder@0d8d1249f`, `holon-coherence@ce39bf34d`)  
**Refreshed:** 2026-11-27 (`holon-agentic-coder@0d8d1249f`, unchanged since `#411`; `holon-coherence@52019174f`, +7 PRs
`#68`, `#69`, `#71`–`#75` since `ce39bf34d`)  
**Remediation Beans:** `0524`–`0539`, `0584`–`0588`, `0614`–`0626` (plus cross-referenced `0383`, `0405`, `0412`,
`0491`, `0546`, `0558`, `0563`, `0564`, `0596`, `0601`, `0610`, `0611`, and existing beans)

---

## 1. Executive Comparison & Scorecard

| Metric (`src/` baseline)            |                                                                   `holon-agentic-coder` |                                              `holon-coherence` |
| ----------------------------------- | --------------------------------------------------------------------------------------: | -------------------------------------------------------------: |
| Source files / LOC (`src/` only)    |                              382 `.py` / 52,140 LOC (`423` / `59,039` incl. `scripts/`) |       65 `.py` / 11,399 LOC (`74` / `13,029` incl. `scripts/`) |
| Test files / scale                  |                        442 `.py` / 106,994 LOC (`5,119` `test_*` / `7,967` total `def`) | 70 `.py` / 19,061 LOC (`1,019` `test_*` / `1,384` total `def`) |
| Functions / return-typed (`src/`)   |                                                                           3,030 / 99.5% |                                                    568 / 98.6% |
| Files > 200L / > 400L (`src/`)      |                                     60 / 16 (default budget 350L; `>350L`: 20, 2 stale) |             19 / 8 (default budget 200L; `>350L`: 11, 0 stale) |
| Max cyclomatic complexity           |                                                                 207 (`run_review_loop`) |                             24 (`normalize_anthropic_request`) |
| Bare `except:` / `except Exception` |                                                   0 / 138 (`3` silent `pass` in `src/`) |                           0 / 33 (`3` silent `pass` in `src/`) |
| Docstrings / comments (`src/`)      | 73 func docstrings (+17 mod, +6 cls), 581/663 `# why:` (87.6%); tests: 1,057 docstrings |       0 docstrings / 0 comments (`src/`, `tests/`, `scripts/`) |

> **Progress since `ce39bf34d` (`7` Coherence PRs `#68`, `#69`, `#71`–`#75`; HAC `0d8d1249f` unchanged):**
> `holon-coherence` closed **`0524`** (`#75` eliminated raw `?token=` URLs in `commands/endpoints.py`, added
> `scrub_sensitive_data()` + `0o600` DB/WAL/SHM permissions in `HybridCacheStore`, dropped unused SQLite index
> `idx_prompt_cache_provider_system_created`, and removed `3x normalize_payload`), closed **`0563`** (`#74` added
> `check_ledger_stores.py`, `check_ledger_rows_append_only.py`, and `.github/workflows/test-ledger-invariants.yml`), and
> landed partial slices for **`0588`** (`#68` removed `holon-knowledge/kb/*/index.json`), **`0529`** (`#69` bounded
> `_pending_wire_log_futures` & fixed silent `pass` in `wire_log.py`; `#73` added `logger.warning` in `ca_generator.py`
> and `importlib.resources` `resolve_build_context()` in `container/image.py`), **`0530`** (`#71` renamed
> `_check_structural_parity` & updated hygiene), and **`0528`** (`#72` replaced `ab_test.py` `mkdtemp` leak with
> `TemporaryDirectory` & removed unused `cryptography`). Overall, **`holon-coherence` (`7.9`, `+0.2`) extended its lead
> over `holon-agentic-coder` (`7.5`, `0.0`)**.

|  #  | Aspect                                     | `holon-agentic-coder` |  `holon-coherence`  | Summary Takeaway                                                                                                                                                                                                                                                                                                                                                                                                                |
| :-: | ------------------------------------------ | :-------------------: | :-----------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|  1  | Clean Architecture & Layer Boundaries      |       6.6 / 10        |      7.6 / 10       | Coherence `#74` (`0563`) enforced the 3-ledger store boundary via CI (`check_ledger_stores.py`, `check_ledger_rows_append_only.py`); `commands ↔ container` (`4↔3`), `parsers ↔ providers` (`3↔4`), and `TYPE_CHECKING` `reduction_passes → payload_cleaner` remain (`0527`, `0621`). HAC `entrypoint ↔ flow` (`12↔15`) and `knowledge ↔ ledger` (`4↔1`) remain (`0531`, `0615`).                                               |
|  2  | Modularity, Cohesion & File Sizing         |       7.4 / 10        |      7.6 / 10       | Coherence `#73` extracted `resolve_build_context()` cleanly in `container/image.py`; `19` `>200L` / `8` `>400L`, `0` stale/missing overrides under `200L` budget. HAC holds `20` `>350L` `src/` modules (`1` stale `flow/__init__.py: 522/27L`, `1` missing `calibration.py: 1608`, `0585`).                                                                                                                                    |
|  3  | Complexity & Control Flow                  |       5.9 / 10        |      8.0 / 10       | Unchanged — HAC `run_review_loop` (`CC=207` on radon / `212` AST-walk, `764L` excl. blanks/`941L` raw, `17` args) alongside `stages/review.py` (`51`), `turns.py` (`49`), `planner.py` (`49`); Coherence max CC stays `24` (`normalize_anthropic_request`).                                                                                                                                                                     |
|  4  | Clean Code & Idiomatic Python              |       7.3 / 10        |   7.3 / 10 (+0.2)   | Coherence `#72` fixed `ab_test.py` `mkdtemp` leak & dropped unused `cryptography`, `#75` cut `3x normalize_payload` & unused SQLite index, `#71` fixed `_check_structural_parity` naming, and `98.6%` (`560/568`) stay return-typed; `10` redundant `*_self_doc.py` files (`1,206L`, `0530`) and `mypy`/`pyright` CI gaps remain.                                                                                               |
|  5  | Intention-Revealing & Self-Doc Code        |       8.1 / 10        |   8.3 / 10 (+0.1)   | Coherence kept `0` docstrings and `0` noise comments across all `65` `src/`, `70` `tests/`, and `9` `scripts/` files while adding `+792` test LOC and `2` CI scripts, and renamed misleading `semantic_parity` (`#71`). HAC holds `73` `src/` func docstrings, `581/663` `# why:`, and `1,057` test docstrings.                                                                                                                 |
|  6  | Extensibility & Plug-in Seams              |       6.8 / 10        |      7.7 / 10       | Coherence `ProviderFormat.matches()` & `KNOWN_PROVIDERS` (`0527`, slice 1 blocked on `0623` ratchet deadlock) remain open; HAC `RunnerSpec`/`GitForge` (`0535`) unchanged (`#414`/`#415` in review).                                                                                                                                                                                                                            |
|  7  | Testability & Verification Quality         |       7.8 / 10        |   8.0 / 10 (+0.2)   | Coherence added `+3` test files (`+792` test LOC, `1,019` `test_*` cases, `0` `TestCase`) covering bounded `wire_log`, `resolve_build_context`, no-`index.json`, 3-ledger invariants, and `HybridCacheStore` scrubbing (`#68,#69,#73,#74,#75`). HAC `todo/test-suite-audit-2026-11-26.md` batches (`0405`, `0491`) and `10` `test_self_doc_tests_*.py` copies (`0601`) remain open.                                             |
|  8  | Error Handling, Resilience & Failure Modes |       8.1 / 10        |   7.9 / 10 (+0.3)   | Coherence `#69` bounded `_pending_wire_log_futures` & removed `wire_log.py:69` silent `pass` (`broad_except` `34→33`, silent `pass` `4→3`), `#73` logged CA sync `OSError` warnings & replaced brittle 4-level `__file__` lookup, and `#72` used `TemporaryDirectory`; `3` silent `pass` blocks remain (`0622`). HAC `broad_except` stays `138` (`#414` in progress) alongside Stage 4/5 gaps (`0617`–`0619`, `0624`–`0625`).   |
|  9  | Security, Isolation & Secret Hygiene       |       8.4 / 10        |   8.4 / 10 (+1.0)   | Coherence closed **`0524`** (`#75` removed `?token=` query URLs in `endpoints.py`, added `scrub_sensitive_data()` for headers/payloads before `HybridCacheStore` writes, and enforced `0o600` perms on `llm_cache.db`/`-wal`/`-shm`), joining closed `0525` & `0564`. HAC awaits Docker quotas, `local_llm` modes, `git.py` `--`, `Dockerfile` pin (`0532`).                                                                    |
| 10  | Observability, Provenance & Config         |       8.2 / 10        |   7.7 / 10 (+0.1)   | Coherence closed `0563` (`#74` CI ledger invariants) and removed stale `kb/*/index.json` (`#68`), yet **48** pending ledger fragments (`+21` since `ce39bf3`) sit unpromoted without `HOLON_LEDGER_BOT_TOKEN` (`0620`) and `CoherenceSettings` centralization (`0529`) remains open. HAC pending backlog stays **270** (`0611`, PR `#413` halted on `CF-0055`), with `0` wrapper flow logs written in `07:29Z–10:49Z` (`0412`). |
|     | **Overall Score**                          |  **7.5 / 10 (0.0)**   | **7.9 / 10 (+0.2)** | **Coherence (`7.85`) widened its lead over HAC (`7.5`)** by closing `0524` (`#75`) and `0563` (`#74`) plus 5 hygiene/resilience PRs (`#68,#69,#71–#73`); remaining Coherence gaps centre on `0527`–`0530`, `0588`, and `0620`–`0623`.                                                                                                                                                                                           |

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

| Area                                | Priority | Status at `0d8d1249f`                                                                                                                                                                                                                                     | Existing / Reference Bean                                    |
| ----------------------------------- | :------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Layer Cycles & Hotspots             |  `high`  | `entrypoint↔flow` (`12↔15`), `knowledge↔ledger` (`4↔1`); `run_review_loop` (`CC=207`, 764L, 17 args), `stages/review.py` (`51`), `turns.py` (`49`), `planner.py` (`49`)                                                                                   | Bean `0531` _(plus `0192`, `0152`, `0584`)_                  |
| Import-Cycle & Broad-Catch Ratchets | `normal` | PR `#415` (`0615`, import-cycle ratchet) and PR `#414` (`0616`, broad-except ratchet; `138` in `src/`) both reached `3/3 APPROVED` + `calibrate: ok` after `10:30Z` quota reset                                                                           | Beans `0615`, `0616` _(`in-progress`, PRs `#415`, `#414`)_   |
| Orphaned Budget Overrides           | `normal` | `check_module_budgets.py` warns on deleted `calibration.py: 1608` and stale `flow/__init__.py: 522` (`27L` actual), plus 14 lowerable overrides (`>350L`: `20`)                                                                                           | Bean `0585` _(coord. `0489`, `0570`)_                        |
| Security & Containers               |  `high`  | Docker `--memory`/`--cpus`/`--pids-limit`/`--read-only`, metadata CIDR block, `local_llm` modes, `git.py` `--`, `Dockerfile` pin remain                                                                                                                   | Bean `0532` _(`in-progress`)_                                |
| Typing, DRY & Env Drift             |  `high`  | No `mypy`/`pyright` in CI, duplicate agent-ID normalizers & `git diff --numstat`, `HOLON_AGENT_EFFORT` drift, `os.environ` mutations, dead shims                                                                                                          | Bean `0533` _(coord. `0223`)_                                |
| Resilience & Adapters               | `normal` | `3` silent `except Exception: pass` blocks in `src/` (+`1` in `scripts/`), `sys.exit(1)` in library code, `GitHubAdapter` raw `json.loads` / dropped `proxy_env`, untyped `RuntimeError` in `git.py`                                                      | Bean `0534`                                                  |
| Extensibility & Protocols           | `normal` | Runner registration spans ~8 files despite `RunnerSpec`, missing `GitForge` `Protocol`, `if/elif` stage dispatch in `pipeline.py`                                                                                                                         | Bean `0535` _(rel. `0270`)_                                  |
| Stage 4/5 Gates & Quota Resilience  |  `high`  | `0618` (`#412`) `3/3 APPROVED` + `calibrate: ok`; `0617` & `0619` in progress; **new:** Stage 4 `touch_set_violation` rollback/re-plan (`0624`, `#70`/`#413`) and Stage 3/4 quota `exit code 3` ladder step-down (`0625`, `6` flows idled ~2 h)           | `0617`–`0619`, **`0624` (new)**, **`0625` (new)**            |
| Observability, Checkpoints & Ledger |  `high`  | Mixed `print`/`logging`, unbounded `context.logs`, dual-writes (`0536`); **270** pending fragments (`0611`, PR `#413` halted `CF-0055`); `0` wrapper logs written in `07:29Z–10:49Z` (`0412`); Stage 5 CI budget overrun (`0383`); `new_bean.py` (`0626`) | `0536`, `0611`, `0412` _(ext.)_, `0383` _(ext.)_, **`0626`** |
| Hygiene, Test Speed & `# why:`      |  `high`  | `834L` shims (`0537`), `107k` test LOC (`8,311` cases / `45,157` git spawns / quadratic `mktemp` in `0405`, `0491`), `10` `test_self_doc_tests_*.py` copies (`0601`), `1,057` test / `73` src func docstrings (`0153`)                                    | Bean `0537` _(plus `0153`, `0405`, `0491`, `0601`, `0608`)_  |

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

- **Done Well:** `0596` (`#410`) immediately caught unauthorized Stage 4 out-of-scope edits (`CF-0054` `#70`, `CF-0055`
  `#413`); `exit code 3` quota handling cleanly halted `6` concurrent flows during the `08:42–08:46Z` `gemini-4-neon`
  outage with zero corrupted state; and after the `10:30Z` reset, `#412` (`0618`), `#414` (`0616`), and `#415` (`0615`)
  all resumed cleanly, reached `3/3 APPROVED`, and completed Stage 5 calibration.
- **Could Be Better:** Add clean rollback/patch-save and bounded re-plan recovery on Stage 4 `touch_set_violation`
  (`0624`) plus `.github/workflows/*.yml -> README.md` companion prediction (`0546`); step down the `AGENTS.md` model
  ladder automatically on Stage 3/4 quota `exit code 3` instead of idling ~2 h (`0625`); enforce `todo/flow-*.log`
  persistence and step timings (`0412`) plus CI-excluded Stage 5 budgets (`0383`); scaffold `## Acceptance Criteria` in
  `new_bean.py` (`0626`); and drive `0538` / `0617` / `0619` / `0405` / `0491` to completion.

---

## 5. Curated Knowledge Base Additions

- **Bean `0538` (`holon-agentic-coder`):** `in-progress` — halted in Stage 3 (`exit code 3` at `08:43:20Z`), resumed at
  `10:49:31Z` to land 3 proven patterns and 4 failure modes.
- **Bean `0539` (`holon-coherence`):** **Completed (`#62`, `85af07d`)** — 7 curated pattern and failure-mode KB entries
  live (`80` total KB entries in `holon-knowledge/kb/`, `0` `index.json` manifests after `#68`).
