# Holon Ecosystem Architecture & Source-Code Audit (2026-11)

**Audit Date:** 2026-11-26  
**Scope:** `holon-agentic-coder` (`HEAD f1e18bcd`), `holon-coherence` (`HEAD 18084f3`)  
**Remediation Beans:** `0524`–`0539` (plus cross-referenced existing beans)

---

## 1. Executive Comparison & Scorecard

| Metric                              |                  `holon-agentic-coder` |                     `holon-coherence` |
| ----------------------------------- | -------------------------------------: | ------------------------------------: |
| Source files / LOC                  |                 341 `.py` / 52,457 LOC |                 63 `.py` / 10,994 LOC |
| Test files / scale                  | 372 `.py` / ~97,463 LOC (~6,965 cases) | 60 `.py` (1,511 unit + 8 integration) |
| Functions / return-typed            |                          2,730 / 99.5% |                           527 / 98.3% |
| Files > 200L / > 400L               |          57 / 21 (default budget 400L) |          19 / 8 (default budget 200L) |
| Max cyclomatic complexity           |            205–210 (`run_review_loop`) |    24 (`normalize_anthropic_request`) |
| Bare `except:` / `except Exception` |                                0 / 133 |                                0 / 35 |

|  #  | Aspect                                     | `holon-agentic-coder` | `holon-coherence` | Summary Takeaway                                                                                                                                               |
| :-: | ------------------------------------------ | :-------------------: | :---------------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
|  1  | Clean Architecture & Layer Boundaries      |       6.5 / 10        |     7.8 / 10      | Coherence uses a crisp declarative proxy step pipeline; HAC carries an 11-edge `flow` ↔ `entrypoint` cycle.                                                    |
|  2  | Modularity, Cohesion & File Sizing         |       6.5 / 10        |     7.5 / 10      | Both enforce module budgets, yet HAC has 1,471L/991L/940L god modules and 834L of compat shims.                                                                |
|  3  | Complexity & Control Flow                  |       5.5 / 10        |     8.0 / 10      | Coherence caps CC at 24 with a locked `# noqa` ratchet; HAC retains CC=205 and CC≈50 functions.                                                                |
|  4  | Clean Code & Idiomatic Python              |       7.2 / 10        |     7.0 / 10      | Modern Python 3.13 idioms throughout both, but neither runs `mypy`/`pyright` in CI and both have DRY drift.                                                    |
|  5  | Intention-Revealing & Self-Doc Code        |       7.0 / 10        |     8.2 / 10      | Coherence hits 100% repo-wide self-doc naming; HAC's strict zero-comment ban hides critical "why" invariants.                                                  |
|  6  | Extensibility & Plug-in Seams              |       6.8 / 10        |     7.4 / 10      | Coherence has `StepSpec` + `ProviderFormat`, though providers still edit core files; adding a HAC runner touches ~8 files.                                     |
|  7  | Testability & Verification Quality         |       7.5 / 10        |     7.0 / 10      | HAC has standout suite hermeticity (with heavy white-box patching); Coherence lacks real `mitmproxy` wire tests.                                               |
|  8  | Error Handling, Resilience & Failure Modes |       7.6 / 10        |     7.0 / 10      | HAC locks, checkpoints, and supervises turns well; Coherence has fail-open steps but unbounded queues & SSE chunk bugs.                                        |
|  9  | Security, Isolation & Secret Hygiene       |       8.0 / 10        |     5.5 / 10      | HAC's `.git` worktree & credential hardening excels; Coherence `chmod 0o666`s its Root CA private key and leaves `/holon/api/mode` unauthenticated.            |
| 10  | Observability, Provenance & Config         |       7.8 / 10        |     7.4 / 10      | HAC's 3-ledger fragment architecture & env registry shines; Coherence has honest `X-Holon-*` telemetry but scattered `os.getenv`.                              |
|     | **Overall Score**                          |     **7.0 / 10**      |   **7.3 / 10**    | **HAC:** battle-hardened systems engineering slowed by structural debt. **Coherence:** disciplined pipeline codebase held back by fixable security & SSE bugs. |

---

## 2. Remediation Matrix

### `holon-coherence` Findings

| Area                          |  Priority  | Summary                                                                                                                                                                  | Remediation Bean |
| ----------------------------- | :--------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------- |
| Security / CA & Secrets       | `critical` | `world_accessible_mounts=True` (`0o777` dirs, `0o666` Root CA private key), `web_password` in argv/`?token=`, unscrubbed `0o777` cache                                   | Bean `0524`      |
| Security / Control Plane      | `critical` | Host-less `/holon/*` interception, wildcard CORS, unauthenticated `POST /holon/api/mode` with arbitrary `wire_log_dir`, `GET /mode` override bug                         | Bean `0525`      |
| SSE Streaming & Wire Tests    |   `high`   | Unbuffered chunk `\n` split & non-incremental UTF-8 decode, zero real `mitmproxy.test.tflow` / `HTTPServer` tests, `example.com` call, `unittest`, `".beans"` ref        | Bean `0526`      |
| Extensibility & Import Cycles |   `high`   | Divergent `detect_provider`, closed `ProviderName` Literal, hardcoded `KNOWN_PROVIDERS`, `parsers` ↔ `providers` & `docker_ops` ↔ `endpoints` cycles                     | Bean `0527`      |
| Performance & DRY Drift       |  `normal`  | Up to 4× `copy.deepcopy` per request, 2× token parse, 3× `normalize_payload`, unused SQLite index, duplicate SSE/metrics helpers, `ab_test` leaks, unused `cryptography` | Bean `0528`      |
| Config, Resilience & Docker   |  `normal`  | Scattered/frozen `os.getenv`, unbounded wire-log futures & disk duplication, silent CA `suppress`, 4-level `__file__` Dockerfile lookup, `pip` vs `uv.lock`              | Bean `0529`      |
| Typing & Hygiene              |  `normal`  | No `mypy`/`pyright` in CI, 9 redundant `*_self_doc.py` files (922 LOC), `_compat.py` probe & barrels, root experimental clutter, inline dashboard HTML, parity naming    | Bean `0530`      |

### `holon-agentic-coder` Findings

| Area                        | Priority | Summary                                                                                                                                                                                                  | Existing / New Bean                                 |
| --------------------------- | :------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| Layer Cycles & Hotspots     |  `high`  | `flow` ↔ `entrypoint` & `ledger` ↔ `knowledge` cycles, `FlowContext.__post_init__` side effects, 5-mixin `ExecutionRun`, `planner.py:main` (CC=50), `turns.py:run_turn` (CC=49)                          | Bean `0531` _(plus `0192`, `0197`, `0152`)_         |
| Security & Containers       |  `high`  | Missing `--memory`/`--cpus`/`--pids-limit`/`--read-only`, writable `/tmp/intent.json`, direct metadata IP egress, `0o777`/`0o644` `local_llm`, umask secret unpack, `git.py` `--`, unpinned `install.sh` | Bean `0532`                                         |
| Typing, DRY & Env Drift     |  `high`  | No `mypy`/`pyright` in CI, 4× agent-ID normalizers, 5× `git diff --numstat`, runtime/doc drift on `HOLON_AGENT_EFFORT`, `os.environ` mutations, dead shims                                               | Bean `0533` _(coord. `0223`)_                       |
| Resilience & Adapters       | `normal` | 3 silent `except Exception: pass` blocks (incl. temp-cred cleanup), `sys.exit(1)` in library code, `GitHubAdapter` raw `json.loads` / dropped `proxy_env`, generic `RuntimeError` in `git.py`            | Bean `0534`                                         |
| Extensibility & Protocols   | `normal` | Runner registration spans ~8 files despite `RunnerSpec`, missing `GitForge` Protocol, `if/elif` stage dispatch in `pipeline.py`, only 2 `Protocol`s in 341 modules                                       | Bean `0535` _(rel. `0270`)_                         |
| Observability & Checkpoints | `normal` | Mixed `print`/`logging` plain text, unbounded `context.logs` in checkpoint JSON, `FlowCheckpoint.to_dict` `admission`/`repo_dir` dual-write                                                              | Bean `0536` _(coord. `0412`)_                       |
| Hygiene, Tests & `# WHY:`   | `normal` | 834L legacy shims exposing `_` symbols, 9 stale budget overrides, empty `token_reduction/`, `conftest.py` name allowlist & 2,677 mocks, zero-comment ban hiding subtle invariants                        | Bean `0537` _(plus `0379`, `0405`, `0489`, `0176`)_ |

---

## 3. What's Been Done Well vs. What Could Be Better

### `holon-agentic-coder`

- **Done Well:** Worktree `.git` mount hardening & `0o600` temp env-files; suite-wide hermetic `tests/conftest.py`
  guards and drift suites; append-only 3-ledger fragment routing with prefix-integrity locking and crash-recoverable
  turn supervision; cleaner modular trajectory in newer packages (`flow/admission.py`, `approval_gates.py`,
  `ledger/route.py`, `cli/commands/`).
- **Could Be Better:** Break `flow` ↔ `entrypoint` and `ledger` ↔ `knowledge` cycles while finishing `run_review_loop` /
  `calibration` decomposition; enforce Docker resource quotas and `0o600` secret unpacking; wire static type checking
  into CI alongside single-source `env_registry.py` and `RunnerSpec`; retire 834L of compat shims and allow concise
  `# WHY:` invariant comments.

### `holon-coherence`

- **Done Well:** Declarative fail-open `StepSpec` proxy pipeline keeping `MitmproxyAddon` compact; 200L module budget +
  locked complexity baseline (`max CC = 24`) + 100% self-documenting symbol naming; honest `"unmeasured"` labels and
  recursive wire-log scrubbing; fast 2.3s pytest collection with golden pipeline parity tests.
- **Could Be Better:** Eliminate `0o777`/`0o666` Root CA key permissions and harden `/holon/*` Host checks &
  `/holon/api/mode` authentication immediately; fix SSE chunk-splitting and UTF-8 buffering backed by real
  `mitmproxy.test.tflow` / `HTTPServer` wire tests; unify `ProviderFormat.matches()` and trim multi-`deepcopy` hot-path
  overhead; centralize `CoherenceSettings` and wire `mypy`/`pyright` into CI.

---

## 4. Curated Knowledge Base Additions

Under the Sole Change Path rule, target-native KB JSON payloads matching `docs/knowledgebase_schema.md` are staged in
dedicated KB-curation beans for execution via `holon flow`:

- **Bean `0538` (`holon-agentic-coder`):** 3 proven patterns (`worktree-git-hardening`, `hermetic-pytest-conftest`,
  `three-ledger-fragment-routing`) and 4 failure modes (`bidirectional-flow-entrypoint-cycle`,
  `monolithic-review-loop-complexity`, `env-registry-runtime-drift`, `container-resource-and-secret-perm-gaps`).
- **Bean `0539` (`holon-coherence`):** 3 proven patterns (`declarative-proxy-step-pipeline`,
  `locked-complexity-and-self-doc-hygiene`, `honest-unmeasured-wire-telemetry`) and 4 failure modes
  (`world-writable-ca-mount-permissions`, `unauthenticated-hostless-proxy-control`,
  `unbuffered-sse-chunks-without-wire-tests`, `hot-path-deepcopy-and-provider-drift`).
