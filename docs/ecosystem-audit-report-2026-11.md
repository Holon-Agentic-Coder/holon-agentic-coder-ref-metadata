# Holon Ecosystem Architecture & Source-Code Audit (2026-11)

**Original Audit:** 2026-11-26 (`holon-agentic-coder@f1e18bcd`, `holon-coherence@18084f3`)  
**Refreshed:** 2026-11-27 (`holon-agentic-coder@f006e79b`, +20 merged PRs; `holon-coherence@18084f3`, unchanged)  
**Remediation Beans:** `0524`–`0539`, `0584`–`0588` (plus cross-referenced existing beans)

---

## 1. Executive Comparison & Scorecard

| Metric                              |                  `holon-agentic-coder` |                  `holon-coherence` |
| ----------------------------------- | -------------------------------------: | ---------------------------------: |
| Source files / LOC                  |                 362 `.py` / 54,525 LOC |              63 `.py` / 10,994 LOC |
| Test files / scale                  | 393 `.py` / 102,753 LOC (~4,739 `def`) | 60 `.py` / 16,038 LOC (~920 `def`) |
| Functions / return-typed            |                          2,896 / 99.5% |                        527 / 98.3% |
| Files > 200L / > 400L               |          64 / 20 (default budget 400L) |       19 / 8 (default budget 200L) |
| Max cyclomatic complexity           |                205 (`run_review_loop`) | 24 (`normalize_anthropic_request`) |
| Bare `except:` / `except Exception` |                                0 / 128 |                             0 / 35 |

> **Progress since `f1e18bcd` (20 HAC PRs):** Merged `calibration.py` package split (`#347`), `0o600` secret bundle
> unpacking & redacted failure logs (`#356`), single-instance `run_lock` + `process_reaper` (`#351`), single-flow KB
> failure pruning (`#344`), plus CI invariants for self-explaining code (`#357`), 3-ledger enforcement (`#362`), and
> `module-budget-change` actor checks (`#366`). `holon-coherence` remains at `18084f3`.

|  #  | Aspect                                     | `holon-agentic-coder` | `holon-coherence` | Summary Takeaway                                                                                                                                                       |
| :-: | ------------------------------------------ | :-------------------: | :---------------: | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|  1  | Clean Architecture & Layer Boundaries      |    6.6 / 10 (+0.1)    |     7.8 / 10      | Coherence uses a crisp declarative proxy pipeline; HAC split `calibration/` cleanly (`#347`), though 12 flat `calibration_*.py` siblings created a new local cycle.    |
|  2  | Modularity, Cohesion & File Sizing         |    6.9 / 10 (+0.4)    |     7.5 / 10      | Removing `calibration.py` (`1,471L`) lifted HAC noticeably, though `991L`/`940L`/`912L` files, 834L shims, and 12 flat calibration siblings remain.                    |
|  3  | Complexity & Control Flow                  |    5.9 / 10 (+0.4)    |     8.0 / 10      | `calibration.py` decomposition retired 4 CC 26–38 hotspots in HAC; `run_review_loop` (CC=205) and CC≈50 functions (`planner.py`, `review.py`, `turns.py`) still lead.  |
|  4  | Clean Code & Idiomatic Python              |       7.2 / 10        |     7.0 / 10      | Modern Python 3.13 idioms throughout both, but neither runs `mypy`/`pyright` in CI and both have costly DRY drift.                                                     |
|  5  | Intention-Revealing & Self-Doc Code        |    7.1 / 10 (+0.1)    |     8.2 / 10      | Coherence hits 100% repo-wide self-doc naming; HAC added `check_self_explaining.py` (`#357`), though legacy docstrings (`1,207`) and zero `# WHY` nuance persist.      |
|  6  | Extensibility & Plug-in Seams              |       6.8 / 10        |     7.3 / 10      | Coherence has `StepSpec` + `ProviderFormat`, yet needs a pluggable `ReductionPass` seam and open registry; HAC runner additions still touch ~8 files.                  |
|  7  | Testability & Verification Quality         |    7.6 / 10 (+0.1)    |     7.0 / 10      | HAC added fixture-discovery & contract canary tests while test volume grew to 102.8k LOC; Coherence still lacks real `mitmproxy.test.tflow` / `HTTPServer` wire tests. |
|  8  | Error Handling, Resilience & Failure Modes |    8.0 / 10 (+0.4)    |     7.0 / 10      | HAC added `run_lock`, `process_reaper` (`#351`), and unrecorded branch adoption (`#345`); Coherence retains unbounded async queues & SSE chunk bugs.                   |
|  9  | Security, Isolation & Secret Hygiene       |    8.2 / 10 (+0.2)    |     5.5 / 10      | HAC fixed secret-bundle `0o600` perms & log redaction (`#356`); Coherence still `chmod 0o666`s its Root CA private key and leaves `/holon/api/mode` unauthenticated.   |
| 10  | Observability, Provenance & Config         |    8.1 / 10 (+0.3)    |     7.4 / 10      | HAC pruned 3,500+ noisy single-flow KB entries (`#344`) and enforced 3-ledger CI (`#362`); Coherence has `X-Holon-*` telemetry but scattered `os.getenv`.              |
|     | **Overall Score**                          |  **7.2 / 10 (+0.2)**  |   **7.3 / 10**    | **HAC:** rapidly hardening systems & CI governance (`#344`–`#366`), slowed by structural cycles/hotspots. **Coherence:** clean pipeline awaiting security/SSE fixes.   |

---

## 2. Remediation Matrix

### `holon-coherence` Findings

| Area                          |  Priority  | Summary                                                                                                                                                                  | Existing / New Bean   |
| ----------------------------- | :--------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------- |
| Security / CA & Secrets       | `critical` | `world_accessible_mounts=True` (`0o777` dirs, `0o666` Root CA private key), `web_password` in argv/`?token=`, unscrubbed `0o777` cache                                   | Bean `0524`           |
| Security / Control Plane      | `critical` | Host-less `/holon/*` interception, wildcard CORS, unauthenticated `POST /holon/api/mode` with arbitrary `wire_log_dir`, `GET /mode` override bug                         | Bean `0525`           |
| SSE Streaming & Wire Tests    |   `high`   | Unbuffered chunk `\n` split & non-incremental UTF-8 decode, zero real `mitmproxy.test.tflow` / `HTTPServer` tests, `example.com` call, `unittest`, `".beans"` ref        | Bean `0526`           |
| Extensibility & Import Cycles |   `high`   | Divergent `detect_provider`, closed `ProviderName` Literal, hardcoded `KNOWN_PROVIDERS`, `parsers` ↔ `providers` & `docker_ops` ↔ `endpoints` cycles                     | Bean `0527`           |
| Package `__init__.py` Logic   |  `normal`  | 7 functions inside `providers/__init__.py` (`register_provider`, `get_provider`, `resolve_provider`, detection helpers) with no AST guard                                | **Bean `0586` (new)** |
| Token Reduction Seam          |  `normal`  | Imperative token reduction logic in `clean_payload.py` / `payload_cleaner.py` / `anthropic.py` with no composable `ReductionPass` `Protocol`                             | **Bean `0587` (new)** |
| CI Parity & KB Index          |  `normal`  | Missing `ci_bookkeeping_gate.py`, `check_self_explaining.py`, and budget-label actor checks; legacy tracked `holon-knowledge/kb/*/index.json` conflict magnets           | **Bean `0588` (new)** |
| Performance & DRY Drift       |  `normal`  | Up to 4× `copy.deepcopy` per request, 2× token parse, 3× `normalize_payload`, unused SQLite index, duplicate SSE/metrics helpers, `ab_test` leaks, unused `cryptography` | Bean `0528`           |
| Config, Resilience & Docker   |  `normal`  | Scattered/frozen `os.getenv`, unbounded wire-log futures & disk duplication, silent CA `suppress`, 4-level `__file__` Dockerfile lookup, `pip` vs `uv.lock`              | Bean `0529`           |
| Typing & Hygiene              |  `normal`  | No `mypy`/`pyright` in CI, 9 redundant `*_self_doc.py` files (922 LOC), `_compat.py` probe & barrels, root experimental clutter, inline dashboard HTML, parity naming    | Bean `0530`           |

### `holon-agentic-coder` Findings

| Area                        | Priority | Summary                                                                                                                                                                                       | Existing / New Bean                                                         |
| --------------------------- | :------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Layer Cycles & Hotspots     |  `high`  | `flow` ↔ `entrypoint`, `ledger` ↔ `knowledge`, `flow` ↔ `review_target` cycles; `FlowContext.__post_init__`; `ExecutionRun`; `planner.py:main` (CC=50), `turns.py:run_turn` (CC=49)           | Bean `0531` _(plus `0192`, `0152`)_                                         |
| Calibration Package Finish  | `normal` | 12 flat `calibration_*.py` siblings still at root (with `calibration_predicted.py` vs `calibration/predicted.py` collision), `calibration` ↔ `calibration_self_check` & `flow` ↔ `flow_guard` | **Bean `0584` (new)**                                                       |
| Orphaned Budget Overrides   | `normal` | `check_module_budgets.py` accepts deleted path `calibration.py: 1608` and stale `flow/__init__.py: 522` (38L actual) without failing                                                          | **Bean `0585` (new)** _(coord. `0489`, `0570`)_                             |
| Security & Containers       |  `high`  | Missing `--memory`/`--cpus`/`--pids-limit`/`--read-only`, writable `/tmp/intent.json`, direct metadata IP egress, `0o777`/`0o644` `local_llm`, `git.py` `--`, `install.sh`                    | Bean `0532` _(`in-progress`; PR `#356` fixed secret bundle)_                |
| Typing, DRY & Env Drift     |  `high`  | No `mypy`/`pyright` in CI, 4× agent-ID normalizers, 5× `git diff --numstat`, runtime/doc drift on `HOLON_AGENT_EFFORT`, `os.environ` mutations, dead shims                                    | Bean `0533` _(coord. `0223`)_                                               |
| Resilience & Adapters       | `normal` | 3 silent `except Exception: pass` blocks (incl. temp-cred cleanup), `sys.exit(1)` in library code, `GitHubAdapter` raw `json.loads` / dropped `proxy_env`, generic `RuntimeError` in `git.py` | Bean `0534`                                                                 |
| Extensibility & Protocols   | `normal` | Runner registration spans ~8 files despite `RunnerSpec`, missing `GitForge` Protocol, `if/elif` stage dispatch in `pipeline.py`, only 2 `Protocol`s in 362 modules                            | Bean `0535` _(rel. `0270`)_                                                 |
| Observability & Checkpoints | `normal` | Mixed `print`/`logging` plain text, unbounded `context.logs` in checkpoint JSON, `FlowCheckpoint.to_dict` `admission`/`repo_dir` dual-write                                                   | Bean `0536` _(coord. `0412`)_                                               |
| Hygiene, Tests & `# WHY:`   | `normal` | 834L shims exposing `_` symbols, empty `token_reduction/`, `conftest.py` allowlist & 2,677+ mocks, 102.8k test LOC bloat, `# why:` clarity                                                    | Bean `0537` _(plus `0379`, `0404`, `0405`, `0540`, `0543`, `0558`, `0176`)_ |

---

## 3. What's Been Done Well vs. What Could Be Better

### `holon-agentic-coder`

- **Done Well:** Worktree `.git` mount hardening, `0o600` temp env-files, and `0o600` secret-bundle unpacking with
  redacted failure logs (`#356`); suite-wide hermetic `tests/conftest.py` guards and CI contract tests; append-only
  3-ledger fragment routing with automated CI checks (`#362`), `run_lock` + `process_reaper` (`#351`), and cleaner
  modular splits (`calibration/`, `flow/admission.py`, `approval_gates.py`, `ledger/route.py`).
- **Could Be Better:** Consolidate the 12 flat `calibration_*.py` siblings and break remaining import cycles (`flow` ↔
  `entrypoint`, `ledger` ↔ `knowledge`, `calibration` ↔ `calibration_self_check`) while decomposing `run_review_loop`
  (`CC=205`); reject orphaned budget paths (`calibration.py: 1608`); enforce Docker resource quotas and pinned
  `Dockerfile` installers; wire static type checking into CI alongside single-source `env_registry.py` and `RunnerSpec`.

### `holon-coherence`

- **Done Well:** Declarative fail-open `StepSpec` proxy pipeline keeping `MitmproxyAddon` compact; 200L module budget +
  locked complexity baseline (`max CC = 24`) + 100% repo-wide self-doc compliance (`0` docstrings); honest
  `"unmeasured"` labels and recursive wire-log scrubbing; fast pytest collection with golden pipeline parity tests.
- **Could Be Better:** Eliminate `0o777`/`0o666` Root CA key permissions and harden `/holon/*` Host checks &
  `/holon/api/mode` authentication immediately; fix SSE chunk-splitting and UTF-8 buffering backed by real
  `mitmproxy.test.tflow` / `HTTPServer` wire tests; unify `ProviderFormat.matches()`, extract `providers/__init__.py`
  logic, add a pluggable `ReductionPass` `Protocol`, port HAC's CI hygiene gates (`ci_bookkeeping_gate`,
  `check_self_explaining`, budget actor verification), and remove legacy `kb/*/index.json` files.

---

## 4. Curated Knowledge Base Additions

Under the Sole Change Path rule, target-native KB JSON payloads matching `docs/knowledgebase_schema.md` remain staged in
dedicated KB-curation beans for execution via `holon flow`:

- **Bean `0538` (`holon-agentic-coder`):** 3 proven patterns (`worktree-git-hardening`, `hermetic-pytest-conftest`,
  `three-ledger-fragment-routing`) and 4 failure modes (`bidirectional-flow-entrypoint-cycle`,
  `monolithic-review-loop-complexity`, `env-registry-runtime-drift`, `container-resource-and-secret-perm-gaps`).
- **Bean `0539` (`holon-coherence`):** 3 proven patterns (`declarative-proxy-step-pipeline`,
  `locked-complexity-and-self-doc-hygiene`, `honest-unmeasured-wire-telemetry`) and 4 failure modes
  (`world-writable-ca-mount-permissions`, `unauthenticated-hostless-proxy-control`,
  `unbuffered-sse-chunks-without-wire-tests`, `hot-path-deepcopy-and-provider-drift`).
