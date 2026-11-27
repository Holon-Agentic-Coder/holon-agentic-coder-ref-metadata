# Holon Ecosystem Architecture & Source-Code Audit (2026-11)

**Original Audit:** 2026-11-26 (`holon-agentic-coder@f1e18bcd`, `holon-coherence@18084f3`)  
**Previous Refresh:** 2026-11-27 (`holon-agentic-coder@5c0a557cc`, `holon-coherence@c26a0c1`)  
**Refreshed:** 2026-11-27 (`holon-agentic-coder@0d8d1249f`, +6 PRs `#403`, `#406`–`#411` since `5c0a557cc`;
`holon-coherence@ce39bf34d`, +8 PRs `#58`–`#65` since `c26a0c1`)  
**Remediation Beans:** `0524`–`0539`, `0584`–`0588`, `0614`–`0622` (plus cross-referenced `0405`, `0412`, `0491`,
`0558`, `0564`, `0596`, `0601`, `0611`, and existing beans)

---

## 1. Executive Comparison & Scorecard

| Metric (`src/` baseline)            |                                                                   `holon-agentic-coder` |                                            `holon-coherence` |
| ----------------------------------- | --------------------------------------------------------------------------------------: | -----------------------------------------------------------: |
| Source files / LOC (`src/` only)    |                              382 `.py` / 52,140 LOC (`423` / `59,039` incl. `scripts/`) |     65 `.py` / 11,364 LOC (`72` / `12,705` incl. `scripts/`) |
| Test files / scale                  |                        442 `.py` / 106,994 LOC (`5,119` `test_*` / `7,967` total `def`) | 67 `.py` / 18,269 LOC (`985` `test_*` / `1,341` total `def`) |
| Functions / return-typed (`src/`)   |                                                                           3,030 / 99.5% |                                                  561 / 98.6% |
| Files > 200L / > 400L (`src/`)      |                                     60 / 16 (default budget 350L; `>350L`: 20, 2 stale) |           19 / 8 (default budget 200L; `>350L`: 11, 0 stale) |
| Max cyclomatic complexity           |                                                                 207 (`run_review_loop`) |                           24 (`normalize_anthropic_request`) |
| Bare `except:` / `except Exception` |                                                   0 / 138 (`3` silent `pass` in `src/`) |                         0 / 34 (`4` silent `pass` in `src/`) |
| Docstrings / comments (`src/`)      | 73 func docstrings (+17 mod, +6 cls), 581/663 `# why:` (87.6%); tests: 1,057 docstrings |                0 docstrings / 0 comments (`src/` & `tests/`) |

> **Progress since `5c0a557cc` / `c26a0c1` (6 HAC PRs `#403`, `#406`–`#411` + 8 Coherence PRs `#58`–`#65`):**
> `holon-coherence` closed **`0525`** (`#59` dashboard `Host`/auth/CORS/path hardening), **`0526`** (`#64` SSE
> carry-buffer, incremental UTF-8 decode, `tflow`/`HTTPServer` wire tests, `0` `unittest.TestCase`), **`0539`** (`#62` 7
> KB entries), **`0586`** (`#60` `providers/registry.py`), **`0587`** (`#61` `ReductionPass` `Protocol`), **`0614`**
> (`#65` `promote-ledger.yml`), **`0564`** (`#58` fail-closed `no-harness-references`), and slice 1 of **`0524`** (`#63`
> `0o700`/`0o600` CA permissions and `0o600` `web_password` env-file/config). `holon-agentic-coder` closed **`0596`**
> (`#410` Stage 4/5 `intent.scope` guard), **`0558`** (`#411` Markdown/JSON/JSONL self-explaining exemptions), split
> `wisdom.py` (`386→320L`, `#403`), and trimmed test docstrings (`1,089→1,057`) across `#403,#406,#407,#409`. Overall,
> **Coherence (`7.7`, `+0.4`) reclaimed the lead over HAC (`7.5`, `+0.1`)**.

|  #  | Aspect                                     | `holon-agentic-coder` |  `holon-coherence`  | Summary Takeaway                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| :-: | ------------------------------------------ | :-------------------: | :-----------------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|  1  | Clean Architecture & Layer Boundaries      |       6.6 / 10        |   7.6 / 10 (-0.1)   | Coherence extracted `providers/registry.py` (`#60`), **but** `#63` introduced `commands ↔ container` (`4↔3`) via `lifecycle.py → commands.web_token` and `#61` added `TYPE_CHECKING` `reduction_passes → payload_cleaner`. HAC `entrypoint ↔ flow` (`12↔15`) and `knowledge ↔ ledger` (`4↔1`) remain (`0531`, `0615`).                                                                                                                                                                       |
|  2  | Modularity, Cohesion & File Sizing         |    7.4 / 10 (+0.1)    |   7.6 / 10 (+0.1)   | HAC `#403` split `wisdom.py` (`386→320L`) + `wisdom_store.py` (`83L`), dropping `>350L` `src/` modules `21→20` (`2` stale overrides remain, `0585`). Coherence moved 7 functions out of `providers/__init__.py` (`#60`) and extracted `reduction_passes.py` (`128L`, `#61`) under its `200L` budget (`0` stale).                                                                                                                                                                             |
|  3  | Complexity & Control Flow                  |       5.9 / 10        |      8.0 / 10       | Unchanged — HAC `run_review_loop` (`CC=207`, `764L`, `17` args) was untouched since `#374`, alongside `stages/review.py` (`51`), `turns.py` (`46`), `planner.py` (`41`); Coherence max CC stays `24` (`normalize_anthropic_request`).                                                                                                                                                                                                                                                        |
|  4  | Clean Code & Idiomatic Python              |       7.3 / 10        |   7.1 / 10 (+0.1)   | Coherence removed dead self-assignment in `sse_tap.py` (`#64`), retired `unittest.TestCase`, cleaned `providers/__init__.py` (`#60`), and reached `98.6%` return-typed; `10` redundant `*_self_doc.py` files (`1,202L`, `0530`) and `mypy`/`pyright` CI gaps remain in both repos.                                                                                                                                                                                                           |
|  5  | Intention-Revealing & Self-Doc Code        |    8.1 / 10 (+0.1)    |      8.2 / 10       | HAC cut test docstrings `1,089→1,057` (`#403,#406,#407,#409`), closed `0558` (`#411` Markdown/JSON/JSONL gate coverage), and grew `src/` `# why:` comments `577→581/663` (`73` `src/` func docstrings left). Coherence holds `0` docstrings and `0` noise comments across `src/` and `tests/`.                                                                                                                                                                                               |
|  6  | Extensibility & Plug-in Seams              |       6.8 / 10        |   7.7 / 10 (+0.4)   | Coherence `#61` (`0587`) introduced the `ReductionPass` `Protocol` and `ReductionContext`, and `#60` (`0586`) isolated `providers/registry.py`; `ProviderFormat.matches()` & `KNOWN_PROVIDERS` (`0527`) remain. HAC still needs `RunnerSpec`/`GitForge` (`0535`).                                                                                                                                                                                                                            |
|  7  | Testability & Verification Quality         |    7.8 / 10 (+0.1)    |   7.8 / 10 (+0.8)   | Coherence `#64` (`0526`) added `mitmproxy.test.tflow` & `HTTPServer` wire tests, retired `example.com` & `unittest.TestCase`, and `#58`/`#65` added gate/workflow tests (`+2,091` test LOC). HAC added `test_diff_stays_in_intent_scope.py` & `test_self_explaining_markdown_coverage.py`, while `todo/test-suite-audit-2026-11-26.md` diagnosed `8,311` cases / `45,157` git spawns / quadratic `mktemp` (`0405`, `0491`); `10` per-slice `test_self_doc_tests_*.py` files remain (`0601`). |
|  8  | Error Handling, Resilience & Failure Modes |       8.1 / 10        |   7.6 / 10 (+0.6)   | Coherence `#64` fixed SSE line carry-buffering and incremental UTF-8 decode (`broad_except` `35→34`), though `4` silent `except Exception: pass` blocks (`0622`) and unbounded wire-log futures (`0529`) remain. HAC landed `0596` (`#410`); `broad_except` edged `137→138` (`0616`), `3` silent `pass` (`0534`) and Stage 4/5 gaps (`0617`–`0619`) remain.                                                                                                                                  |
|  9  | Security, Isolation & Secret Hygiene       |       8.4 / 10        |   7.4 / 10 (+1.9)   | Coherence closed `0525` (`#59` local `Host`/auth/CORS/path guard), `0564` (`#58` `no-harness-references`), and `0524` slice 1 (`#63` `0o700`/`0o600` CA perms & `0o600` `web_password` env/config); `0524` slice 2 (`?token=` URLs, unscrubbed cache) remains. HAC awaits Docker quotas, `local_llm` modes, `git.py` `--`, `Dockerfile` pin (`0532`).                                                                                                                                        |
| 10  | Observability, Provenance & Config         |       8.2 / 10        |   7.6 / 10 (+0.2)   | Coherence closed `0539` (`#62` KB) and `0614` (`#65` `promote-ledger.yml`), yet **27** pending fragments (`+24`) remain unpromoted without `HOLON_LEDGER_BOT_TOKEN` (`0620`) alongside `kb/*/index.json` (`0588`). HAC pending backlog hit **270** (`+18`, `0611`); `todo/flow-time-audit-2026-11-26.md` flagged unmeasured sub-steps (`0412`).                                                                                                                                              |
|     | **Overall Score**                          |  **7.5 / 10 (+0.1)**  | **7.7 / 10 (+0.4)** | **Coherence (`7.66`) overtook HAC (`7.46`)** by closing 7 security/SSE/extensibility/hygiene beans in `#58`–`#65`; remaining gaps centre on `0524` slice 2, `0527`–`0530`, `0588`, and new `0620`–`0622`.                                                                                                                                                                                                                                                                                    |

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
- **End-to-End Flow Timing (`todo/flow-time-audit-2026-11-26.md`, PRs `#296`–`#316`):**
  - Active flow time (excluding admission waits & outages): **median `46 min` (`p90 102 min`)** for Claude flows vs
    **`23.7 min`** median for Gemini self-doc flows (`#296`–`#307`). Wall time reached median `84 min` (`p90 1,080 min`)
    due to:
    1. **Un-resumed outage idle:** `2,178 min` (`66.8%` of total wall) from transient DNS/`gh`/Docker failures ending
       the wrapper (`0480`, `0396`).
    2. **Stage 3 admission/overlap waits:** `343 min` (`10.5%`, up to `300 min` holding a slot, `0481`).
    3. **Review-loop churn:** `386 min` (`52%` of active time; median `3` iters, max `9`), driven by Nit-only full
       re-reviews (`8/22` blocked iters, `0407`), false host `review_local` test runs (`0450`, `0469`), and full-PR
       re-review of decomposed parents (`0479`).
    4. **Discarded executor turns (`11%` active) & CI critical-path waits (`12%` active):** `6/9` Claude flows discarded
       median `11.4 min` on post-turn touch-set breaches (`0414`, `0463`); reviewers waited inside their turns for
       macOS/WS CI (`0478`).
    5. **Timing instrumentation gaps (`0412`):** unlogged wrapper pre-flight/Docker probes, missing per-reviewer
       latencies inside ensembles, unlogged inner executor/resolver test vs model splits, and missing
       `stage5_ci_reg_wait`.

---

## 3. Remediation Matrix

### `holon-coherence` Findings

| Area                            |  Priority  | Status at `ce39bf34d`                                                                                                                                                                                                                                                                                        | Bean                                |
| ------------------------------- | :--------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------- |
| Security / CA & Secrets         | `critical` | **Slice 1 landed (`#63`)**: `world_accessible_mounts=False`, `0o700`/`0o600` CA perms, `0o600` `web_password` env/config. **Slice 2 open**: `?token=` URLs (`endpoints.py:34`), unscrubbed `HybridCacheStore`.                                                                                               | Bean `0524` _(`in-progress`)_       |
| Security / Control Plane        | `critical` | **Closed (`#59`)**: local `Host` restriction, bearer auth on `POST /holon/api/mode`, dropped wildcard CORS, `wire_log_dir` containment, `GET /mode` fix.                                                                                                                                                     | ~~Bean `0525`~~ _(completed)_       |
| SSE Streaming & Wire Tests      |   `high`   | **Closed (`#64`)**: SSE carry-buffer, incremental UTF-8 decode, dead self-assign removed, `tflow` / `HTTPServer` wire tests, offline Docker tests, `0` `TestCase`.                                                                                                                                           | ~~Bean `0526`~~ _(completed)_       |
| No-Harness-Refs Gate            | `critical` | **Closed (`#58`)**: fail-closed `check_no_harness_references.py` & CI workflow.                                                                                                                                                                                                                              | ~~Bean `0564`~~ _(completed)_       |
| Extensibility & Import Cycles   |   `high`   | Open: `detect_provider` divergence, closed `ProviderName` Literal, hardcoded `KNOWN_PROVIDERS`, `parsers↔providers` (`3↔4`), `payload_cleaner↔providers` (`2↔4`), `docker_ops↔endpoints`, **plus new `commands↔container` (`4↔3` from `#63`) & `TYPE_CHECKING` `reduction_passes→payload_cleaner` (`#61`)**. | Bean `0527` _(extended)_            |
| Import-Cycle CI Ratchet         |  `normal`  | **New:** Add AST package-import graph CI ratchet so feature/security PRs cannot introduce new cycles like `commands↔container` (`#63`) silently.                                                                                                                                                             | **Bean `0621` (new)**               |
| Package `__init__.py` Logic     |  `normal`  | **Closed (`#60`)**: extracted 7 behavioural functions out of `providers/__init__.py` into `providers/registry.py` (`131L`) with `test_init_no_logic.py`.                                                                                                                                                     | ~~Bean `0586`~~ _(completed)_       |
| Token Reduction Seam            |  `normal`  | **Closed (`#61`)**: introduced composable `ReductionPass` `Protocol` and `ReductionContext` in `src/holon_coherence/reduction_passes.py`.                                                                                                                                                                    | ~~Bean `0587`~~ _(completed)_       |
| Curated KB Entries              |  `normal`  | **Closed (`#62`)**: landed 7 curated pattern and failure-mode KB entries.                                                                                                                                                                                                                                    | ~~Bean `0539`~~ _(completed)_       |
| CI Parity & KB Index            |  `normal`  | Partial (`#58` landed `no-harness-references`): remaining `ci_bookkeeping_gate.py`, `check_self_explaining.py`, `module-budget-change` actor check, and `kb/*/index.json`.                                                                                                                                   | Bean `0588` _(`in-progress`, ext.)_ |
| Ledger Promotion & Backlog      |   `high`   | `#65` added `promote-ledger.yml` (**closed `0614`**), **but** `HOLON_LEDGER_BOT_TOKEN` is unconfigured and **27** pending `.jsonl` fragments (`+24`) remain unpromoted.                                                                                                                                      | ~~`0614`~~ → **Bean `0620` (new)**  |
| Performance & DRY Drift         |  `normal`  | Up to 4× `copy.deepcopy` per request, 2× token parse, 3× `normalize_payload`, unused SQLite index, duplicate SSE/metrics helpers, `ab_test` leaks, unused `cryptography`.                                                                                                                                    | Bean `0528` _(`in-progress`)_       |
| Config, Resilience & Docker     |  `normal`  | Scattered/frozen `os.getenv`, unbounded wire-log futures & disk duplication, silent CA `suppress`, 4-level `__file__` Dockerfile lookup, `pip` vs `uv.lock`.                                                                                                                                                 | Bean `0529` _(`in-progress`)_       |
| Silent `except: pass` & Ratchet |  `normal`  | **New:** Replace **4 silent `except Exception: pass` blocks** (`commands/ca.py:40`, `commands/docker_ops.py:81,169`, `proxy/wire_log.py:69`) and add broad-catch CI ratchet.                                                                                                                                 | **Bean `0622` (new)**               |
| Typing & Hygiene                |  `normal`  | No `mypy`/`pyright` in CI, **`10` redundant `*_self_doc.py` files (`1,202` LOC, up from `9`/`922`)**, `_compat.py` probe & barrels, root experimental clutter, inline HTML.                                                                                                                                  | Bean `0530` _(`in-progress`, ext.)_ |

### `holon-agentic-coder` Findings

| Area                                | Priority | Status at `0d8d1249f`                                                                                                                                                                                                                                                                   | Existing / Reference Bean                                   |
| ----------------------------------- | :------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Layer Cycles & Hotspots             |  `high`  | `entrypoint↔flow` (`12↔15`), `knowledge↔ledger` (`4↔1`), `flow↔review_target` (`8↔4`), `calibration↔calibration_self_check` (`2↔1`), `flow↔flow_guard` (`4↔1`); `run_review_loop` (`CC=207`, 764L, 17 args), `stages/review.py` (`CC=51`), `turns.py` (`CC=46`), `planner.py` (`CC=41`) | Bean `0531` _(plus `0192`, `0152`)_                         |
| Import-Cycle CI Ratchet             | `normal` | Automated AST package-import graph check locking cycle edge baselines (`0531`/`0584` unwind them)                                                                                                                                                                                       | Bean `0615`                                                 |
| Calibration Package Finish          | `normal` | Flat `calibration_*.py` siblings, `calibration` ↔ `calibration_self_check` & `flow` ↔ `flow_guard` cycles                                                                                                                                                                               | Bean `0584`                                                 |
| Orphaned Budget Overrides           | `normal` | `check_module_budgets.py` warns but passes on deleted `calibration.py: 1608` and stale `flow/__init__.py: 522` (`27L` actual), plus 14 lowerable overrides (`wisdom.py` split in `#403` dropped `>350L` `21→20`)                                                                        | Bean `0585` _(coord. `0489`, `0570`)_                       |
| Security & Containers               |  `high`  | `#356` (`0o600` secret bundles) & `#372` (`/tmp/intent.json:ro`) landed; `--memory`/`--cpus`/`--pids-limit`/`--read-only`, metadata CIDR block, `local_llm` modes, `git.py` `--`, `Dockerfile` pin remain                                                                               | Bean `0532` _(`in-progress`)_                               |
| Typing, DRY & Env Drift             |  `high`  | No `mypy`/`pyright` in CI, duplicate agent-ID normalizers & `git diff --numstat`, `HOLON_AGENT_EFFORT` drift, `os.environ` mutations, dead shims                                                                                                                                        | Bean `0533` _(coord. `0223`)_                               |
| Resilience & Adapters               | `normal` | 3 silent `except Exception: pass` blocks in `src/` (+1 in `scripts/`), `sys.exit(1)` in library code, `GitHubAdapter` raw `json.loads` / dropped `proxy_env`, untyped `RuntimeError` in `git.py`                                                                                        | Bean `0534`                                                 |
| Broad `except Exception` Ratchet    | `normal` | `except Exception` in `src/` edged `137→138` (`148` incl. `scripts/`); add AST ratchet & narrow non-boundary catches                                                                                                                                                                    | Bean `0616`                                                 |
| Extensibility & Protocols           | `normal` | Runner registration spans ~8 files despite `RunnerSpec`, missing `GitForge` `Protocol`, `if/elif` stage dispatch in `pipeline.py`                                                                                                                                                       | Bean `0535` _(rel. `0270`)_                                 |
| Self-Explaining & Scope Gates       |  `high`  | **Closed:** `#411` (`0558`) fixed Markdown/JSON/JSONL gate exemptions & coverage; `#410` (`0596`) added Stage 4/5 `intent.scope` bounds                                                                                                                                                 | ~~Beans `0558`, `0596`~~ _(completed)_                      |
| Observability, Checkpoints & Ledger |  `high`  | Mixed `print`/`logging`, unbounded `context.logs`, dual-writes (`0536`); **270** pending ledger fragments (`+18`, `0611`); missing per-step timing (`0412`) & Stage 4/5 gate defects (`0617`–`0619`)                                                                                    | Bean `0536`, Bean `0611` _(ext.)_, `0412`, `0617`–`0619`    |
| Hygiene, Test Speed & `# why:`      |  `high`  | 834L shims exposing `_` symbols (`0537`), `107k` test LOC (`8,311` cases / `45,157` git spawns / quadratic `mktemp` in `0405`, `0491`), `10` `test_self_doc_tests_*.py` copies (`0601`), `1,057` test / `73` src func docstrings (`0153`)                                               | Bean `0537` _(plus `0153`, `0405`, `0491`, `0601`, `0608`)_ |

---

## 4. What's Been Done Well vs. What Could Be Better

### `holon-coherence`

- **Done Well:** Landed 8 PRs (`#58`–`#65`) closing 7 beans (`0525`, `0526`, `0539`, `0564`, `0586`, `0587`, `0614`) and
  `0524` slice 1: eliminated wildcard CORS and unauthenticated control endpoints (`#59`), hardened Root CA permissions
  to `0o700`/`0o600` and moved `web_password` off process argv (`#63`), fixed SSE line/UTF-8 fragmentation with real
  `tflow` and `HTTPServer` wire tests (`#64`), added `ReductionPass` `Protocol` (`#61`) and `providers/registry.py`
  (`#60`), enforced fail-closed `no-harness-references` (`#58`), and kept `100%` self-explaining code (`0` docstrings,
  `0` noise comments, `0` stale `200L` budget overrides, `max CC = 24`).
- **Could Be Better:** Finish `0524` slice 2 (`?token=` URLs in `endpoints.py:34`, `HybridCacheStore` scrubbing); break
  `commands ↔ container` (`4↔3` introduced in `#63`), `parsers ↔ providers` (`3↔4`), `payload_cleaner ↔ providers`
  (`2↔4`), and `docker_ops ↔ endpoints` (`0527`) while locking them with an AST cycle ratchet (`0621`); configure
  `HOLON_LEDGER_BOT_TOKEN` and drain the **27** pending ledger fragments (`0620`); replace the **4** silent
  `except Exception: pass` catches (`0622`); prune the **10** redundant `*_self_doc.py` files (`1,202L`, `0530`); and
  port HAC's remaining CI gates (`0588`).

### `holon-agentic-coder`

- **Done Well:** Closed `0596` (`#410` Stage 4/5 `intent.scope` bounds) and `0558` (`#411` Markdown/JSON/JSONL
  self-explaining coverage), split `wisdom.py` (`386→320L` + `wisdom_store.py` `83L` in `#403`), reduced test docstrings
  (`1,089→1,057`) across `#403,#406,#407,#409`, lifted `src/` `# why:` rationale comments to `581/663`, and produced
  empirical bottlenecks in `todo/test-suite-audit-2026-11-26.md` and `todo/flow-time-audit-2026-11-26.md`.
- **Could Be Better:** Execute the 8 `todo/test-suite-audit-2026-11-26.md` batches (`0405`, `0491`) and consolidate the
  `10` per-slice `test_self_doc_tests_*.py` copies (`0601`); resolve Stage 4/5 flow churn & fail-closed defects
  (`0617`–`0619`, `0478`–`0481`); lock layer cycles (`entrypoint ↔ flow` `12↔15`, `knowledge ↔ ledger` `4↔1`) and
  `broad_except` (`138`, `3` silent `pass`) behind AST ratchets (`0615`, `0616`, `0531`, `0534`); reject orphaned budget
  paths (`0585`); finish Docker quotas & `Dockerfile` pinning (`0532`); and drain the **270** pending ledger fragments
  (`0611`).

---

## 5. Curated Knowledge Base Additions

Under the Sole Change Path rule, target-native KB JSON payloads matching `docs/knowledgebase_schema.md` were staged for
execution via `holon flow`:

- **Bean `0538` (`holon-agentic-coder`):** `todo` — 3 proven patterns and 4 failure modes staged for flow execution.
- **Bean `0539` (`holon-coherence`):** **Completed (`#62`, `85af07d`)** — 7 curated pattern and failure-mode KB entries
  merged into `holon-knowledge/kb/`.
