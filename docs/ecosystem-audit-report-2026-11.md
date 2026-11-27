# Holon Ecosystem Architecture & Source-Code Audit (2026-11)

**Original Audit:** 2026-11-26 (`holon-agentic-coder@f1e18bcd`, `holon-coherence@18084f3`)  
**Previous Refresh:** 2026-11-27 (`holon-agentic-coder@f006e79b`, `holon-coherence@18084f3`)  
**Refreshed:** 2026-11-27 (`holon-agentic-coder@5c0a557cc`, +42 PRs since `f006e79b`; `holon-coherence@c26a0c1`, +1 PR
`#57`)  
**Remediation Beans:** `0524`–`0539`, `0584`–`0588`, `0614`–`0616` (plus cross-referenced `0601`, `0611`, and existing
beans)

---

## 1. Executive Comparison & Scorecard

| Metric                              |                                                 `holon-agentic-coder` |                       `holon-coherence` |
| ----------------------------------- | --------------------------------------------------------------------: | --------------------------------------: |
| Source files / LOC                  |                                                381 `.py` / 51,867 LOC |                   63 `.py` / 10,994 LOC |
| Test files / scale                  |                                436 `.py` / 106,359 LOC (~5,086 `def`) |      61 `.py` / 16,178 LOC (~928 `def`) |
| Functions / return-typed            |                                                         3,015 / 99.5% |                             527 / 98.3% |
| Files > 200L / > 400L               |                     58 / 16 (default budget 350L; >350L: 21, 2 stale) | 19 / 8 (default budget 200L; >350L: 11) |
| Max cyclomatic complexity           |                                               207 (`run_review_loop`) |      24 (`normalize_anthropic_request`) |
| Bare `except:` / `except Exception` |                                                               0 / 137 |                                  0 / 35 |
| Docstrings / comments (`src/`)      | 73 func docstrings (down from 1,207; -94%), 577/659 `# why:` comments |               0 docstrings / 0 comments |

> **Progress since `f006e79b` / `18084f3` (42 HAC PRs + Coherence `#57`):** HAC lowered its default module budget from
> `400` → `350` LOC and decomposed 7 files (`#365`), mounted `/tmp/intent.json:ro` (`#372`), gated all review findings
> (`#374`), enforced self-explaining code at pre-push + CI with `src_func_docstrings` dropping **1,207 → 73** (-94%)
> across ~22 `0153` slices (`#364`, `#375`, `#378`, `#379`–`#405`), added macOS unit sharding (`#376`), real Agent/Model
> PR metadata (`#377`), commit-trailer checks (`#371`), intent scope & no-harness-ref guards (`#363`), checkpoint resume
> intent refresh (`#370`), and Stage 5 test-failure promotion (`#380`). `holon-coherence` merged `#57` (planner
> `## Touch Set`). Overall, **HAC (`7.4`) has now overtaken Coherence (`7.3`)**.

|  #  | Aspect                                     | `holon-agentic-coder` | `holon-coherence` | Summary Takeaway                                                                                                                                                                                    |
| :-: | ------------------------------------------ | :-------------------: | :---------------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|  1  | Clean Architecture & Layer Boundaries      |       6.6 / 10        |  7.7 / 10 (-0.1)  | Coherence retains a crisp declarative proxy pipeline, though AST graph checks surfaced `payload_cleaner ↔ providers`; HAC `entrypoint ↔ flow` edges grew `12↔11` → `12↔15`.                         |
|  2  | Modularity, Cohesion & File Sizing         |    7.3 / 10 (+0.4)    |     7.5 / 10      | HAC lowered default budget `400→350L` (`#365`), dropped `>400L` files `20→16` (`review_ensemble.py` `991→828L`), and shaved 2,658 source LOC despite +19 modules.                                   |
|  3  | Complexity & Control Flow                  |       5.9 / 10        |     8.0 / 10      | HAC `run_review_loop` crept `205→207` (764L, 17 args) and `stages/review.py` `50→51`; Coherence still caps max CC at 24 (`normalize_anthropic_request`).                                            |
|  4  | Clean Code & Idiomatic Python              |    7.3 / 10 (+0.1)    |     7.0 / 10      | HAC removed 2.6k LOC of boilerplate/docstrings; neither repo runs `mypy`/`pyright` in CI yet and DRY drift remains (`apply_patch`, agent normalizers, provider branches).                           |
|  5  | Intention-Revealing & Self-Doc Code        |    8.0 / 10 (+0.9)    |     8.2 / 10      | Massive HAC leap: `src_func_docstrings` fell **1,207 → 73** (-94%), `577/659` comments are `# why:`, enforced at pre-push + CI (`#364`/`#375`/`#378`); 1,089 test docstrings remain.                |
|  6  | Extensibility & Plug-in Seams              |       6.8 / 10        |     7.3 / 10      | Unchanged — HAC needs unified `RunnerSpec`/`GitForge`; Coherence needs `ProviderFormat.matches()`, `ReductionPass` `Protocol`, and registry-derived provider lists.                                 |
|  7  | Testability & Verification Quality         |    7.7 / 10 (+0.1)    |     7.0 / 10      | HAC added macOS unit sharding (`#376`), Stage 5 failure promotion (`#380`), and intent/trailer/ledger CI suites; test LOC hit 106.4k (`436` files) partly from per-slice `0153` tests.              |
|  8  | Error Handling, Resilience & Failure Modes |    8.1 / 10 (+0.1)    |     7.0 / 10      | HAC added checkpoint resume goal refresh (`#370`) and all-findings-actioned gate (`#374`), though `broad_except` climbed `128→137`; Coherence still has SSE/chunk & unbounded queue bugs.           |
|  9  | Security, Isolation & Secret Hygiene       |    8.4 / 10 (+0.2)    |     5.5 / 10      | HAC landed `/tmp/intent.json:ro` (`#372`, partial `0532`), no-harness-ref (`#363`), and trailer checks (`#371`); Coherence still has P0 Root CA `0o666` (`0524`) & unauthed control API (`0525`).   |
| 10  | Observability, Provenance & Config         |    8.2 / 10 (+0.1)    |     7.4 / 10      | HAC emits real Agent/Model in PR bodies (`#377`) and Stage 5 failures (`#380`), though `252` pending fragments piled up (`0611`). Coherence `#57` added `## Touch Set`; 3 pending fragments remain. |
|     | **Overall Score**                          |  **7.4 / 10 (+0.2)**  |   **7.3 / 10**    | **HAC (`7.43`) overtook Coherence (`7.26`)** on sustained CI/security/self-doc sweeps; Coherence awaits security/SSE fixes (`0524`–`0526`).                                                         |

---

## 2. Remediation Matrix

### `holon-coherence` Findings

| Area                          |  Priority  | Summary                                                                                                                                                                       | Existing / New Bean     |
| ----------------------------- | :--------: | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------- |
| Security / CA & Secrets       | `critical` | `world_accessible_mounts=True` (`0o777` dirs, `0o666` Root CA private key), `web_password` in argv/`?token=`, unscrubbed `0o777` cache                                        | Bean `0524`             |
| Security / Control Plane      | `critical` | Host-less `/holon/*` interception, wildcard CORS, unauthenticated `POST /holon/api/mode` with arbitrary `wire_log_dir`, `GET /mode` override bug                              | Bean `0525`             |
| SSE Streaming & Wire Tests    |   `high`   | Unbuffered chunk `\n` split & non-incremental UTF-8 decode, zero real `mitmproxy.test.tflow` / `HTTPServer` tests, `example.com` call, `unittest`, `".beans"` ref             | Bean `0526`             |
| Extensibility & Import Cycles |   `high`   | Divergent `detect_provider`, closed `ProviderName` Literal, hardcoded `KNOWN_PROVIDERS`, `parsers ↔ providers`, `docker_ops ↔ endpoints`, & **`payload_cleaner ↔ providers`** | Bean `0527` _(updated)_ |
| Package `__init__.py` Logic   |  `normal`  | 7 functions inside `providers/__init__.py` (`register_provider`, `get_provider`, `resolve_provider`, detection helpers) with no AST guard                                     | Bean `0586`             |
| Token Reduction Seam          |  `normal`  | Imperative token reduction logic in `clean_payload.py` / `payload_cleaner.py` / `anthropic.py` with no composable `ReductionPass` `Protocol`                                  | Bean `0587`             |
| CI Parity & KB Index          |  `normal`  | Missing `ci_bookkeeping_gate.py`, `check_self_explaining.py`, and budget-label actor checks; legacy tracked `holon-knowledge/kb/*/index.json` conflict magnets                | Bean `0588`             |
| Ledger Promotion Workflow     |  `normal`  | `3` unpromoted pending fragments in `holon-knowledge/ledger/pending/` with no `.github/workflows/promote-ledger.yml` workflow yet                                             | **Bean `0614` (new)**   |
| Performance & DRY Drift       |  `normal`  | Up to 4× `copy.deepcopy` per request, 2× token parse, 3× `normalize_payload`, unused SQLite index, duplicate SSE/metrics helpers, `ab_test` leaks, unused `cryptography`      | Bean `0528`             |
| Config, Resilience & Docker   |  `normal`  | Scattered/frozen `os.getenv`, unbounded wire-log futures & disk duplication, silent CA `suppress`, 4-level `__file__` Dockerfile lookup, `pip` vs `uv.lock`                   | Bean `0529`             |
| Typing & Hygiene              |  `normal`  | No `mypy`/`pyright` in CI, 9 redundant `*_self_doc.py` files (922 LOC), `_compat.py` probe & barrels, root experimental clutter, inline dashboard HTML, parity naming         | Bean `0530`             |

### `holon-agentic-coder` Findings

| Area                                | Priority | Summary                                                                                                                                                                                                            | Existing / New Bean                                                                 |
| ----------------------------------- | :------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| Layer Cycles & Hotspots             |  `high`  | `entrypoint↔flow` grew (`12↔11`→`12↔15`), `knowledge↔ledger` (`3↔1`→`4↔1`), `flow↔review_target` (`8↔4`); `run_review_loop` (`CC=207`), `stages/review.py` (`CC=51`), `planner.py` (`CC=49`), `turns.py` (`CC=49`) | Bean `0531` _(plus `0192`, `0152`)_                                                 |
| Import-Cycle CI Ratchet             | `normal` | Automated AST package-import graph check to prevent `entrypoint↔flow` / `knowledge↔ledger` cycle edges from regressing silently                                                                                    | **Bean `0615` (new)**                                                               |
| Calibration Package Finish          | `normal` | Flat `calibration_*.py` siblings, `calibration` ↔ `calibration_self_check` & `flow` ↔ `flow_guard` cycles                                                                                                          | Bean `0584`                                                                         |
| Orphaned Budget Overrides           | `normal` | `check_module_budgets.py` still accepts deleted `calibration.py: 1608` and stale `flow/__init__.py: 522` (27L actual) without failing                                                                              | Bean `0585` _(coord. `0489`, `0570`)_                                               |
| Security & Containers               |  `high`  | Missing `--memory`/`--cpus`/`--pids-limit`/`--read-only`, direct metadata IP egress, `0o777`/`0o644` `local_llm`, `git.py` `--`, `Dockerfile` pin (`#356` & `#372` landed secret/intent-ro)                        | Bean `0532` _(`in-progress`)_                                                       |
| Typing, DRY & Env Drift             |  `high`  | No `mypy`/`pyright` in CI, duplicate agent-ID normalizers & `git diff --numstat`, runtime/doc drift on `HOLON_AGENT_EFFORT`, `os.environ` mutations, dead shims                                                    | Bean `0533` _(coord. `0223`)_                                                       |
| Resilience & Adapters               | `normal` | 3 silent `except Exception: pass` blocks (incl. temp-cred cleanup), `sys.exit(1)` in library code, `GitHubAdapter` raw `json.loads` / dropped `proxy_env`, generic `RuntimeError` in `git.py`                      | Bean `0534`                                                                         |
| Broad `except Exception` Ratchet    | `normal` | `except Exception` count in `src/` climbed `128→137` (+9 in 42 PRs); add AST ratchet & narrow non-boundary catches                                                                                                 | **Bean `0616` (new)**                                                               |
| Extensibility & Protocols           | `normal` | Runner registration spans ~8 files despite `RunnerSpec`, missing `GitForge` Protocol, `if/elif` stage dispatch in `pipeline.py`                                                                                    | Bean `0535` _(rel. `0270`)_                                                         |
| Observability, Checkpoints & Ledger | `normal` | Mixed `print`/`logging`, unbounded `context.logs` in checkpoints, dual-writes; `252` pending ledger fragments + cancelled `Promote Ledger` churn without `HOLON_LEDGER_BOT_TOKEN`                                  | Bean `0536`, **Bean `0611`**                                                        |
| Hygiene, Tests & `# why:`           | `normal` | 834L shims exposing `_` symbols, 106.4k test LOC & per-slice `0153` test duplication, remaining `1,089` test docstrings / `73` src func docstrings                                                                 | Bean `0537` _(plus `0153`, `0601`, `0379`, `0404`, `0405`, `0540`, `0543`, `0558`)_ |

---

## 3. What's Been Done Well vs. What Could Be Better

### `holon-agentic-coder`

- **Done Well:** Dramatic execution of self-explaining code (`1,207 → 73` function docstrings in `src/`, `577` `# why:`
  rationale comments, pre-push & CI gates `#364`/`#375`/`#378`), tightening the default module budget `400 → 350L`
  (`#365`), `/tmp/intent.json:ro` container mounting (`#372`), `0o600` secret bundles + redacted failure logs (`#356`),
  macOS unit sharding (`#376`), real Agent/Model attribution in PR bodies (`#377`), Stage 5 failure promotion (`#380`),
  intent-scope/no-harness-ref/commit-trailer CI guards (`#363`/`#371`), and checkpoint resume goal refresh (`#370`).
- **Could Be Better:** Lock down `entrypoint ↔ flow` (`12↔15`) and `knowledge ↔ ledger` (`4↔1`) cycles with an AST
  ratchet (`0615`) while unwinding them (`0531`, `0584`); decompose `run_review_loop` (`CC=207`, 764L) and `CC=49–51`
  hotspots; ratchet `broad_except` (`128→137`, `0616`); reject orphaned budget paths (`0585`); finish Docker quotas &
  `Dockerfile` SHA256 pinning (`0532`); resolve the `252`-file pending ledger backlog (`0611`); and curb per-slice test
  bloat (`0601`, `1,089` test docstrings).

### `holon-coherence`

- **Done Well:** Crisp declarative `StepSpec` proxy pipeline keeping `MitmproxyAddon` compact; strict `200L` default
  module budget with `0` stale overrides; capped cyclomatic complexity (`max CC = 24`) and `100%` self-explaining code
  across `src/` and `tests/` (`0` docstrings, `0` noise comments); fast pytest collection; and landing planner
  `## Touch Set` (`#57`).
- **Could Be Better:** Eliminate P0 `0o777`/`0o666` Root CA key permissions (`0524`) and unauthenticated host-less
  `/holon/*` control endpoints (`0525`); fix SSE chunk-splitting and UTF-8 buffering backed by real
  `mitmproxy.test.tflow` / `HTTPServer` wire tests (`0526`); break `parsers ↔ providers`, `docker_ops ↔ endpoints`, and
  newly surfaced `payload_cleaner ↔ providers` cycles while unifying `ProviderFormat.matches()` (`0527`); extract logic
  from `providers/__init__.py` (`0586`), introduce a `ReductionPass` `Protocol` (`0587`), port HAC's CI hygiene gates
  (`0588`), and add a ledger-promotion workflow to drain `3` pending fragments (`0614`).

---

## 4. Curated Knowledge Base Additions

Under the Sole Change Path rule, target-native KB JSON payloads matching `docs/knowledgebase_schema.md` remain staged in
dedicated KB-curation beans for execution via `holon flow`:

- **Bean `0538` (`holon-agentic-coder`):** 3 proven patterns and 4 failure modes staged for flow execution.
- **Bean `0539` (`holon-coherence`):** 3 proven patterns and 4 failure modes staged for flow execution.
