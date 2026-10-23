# Holon Ecosystem Comprehensive Quality, Architecture, and Security Audit

**Audit Date:** 2026-10-19  
**Audit Reference:** Bean `0122` (`holon-agentic-coder-ref-metadata-0122`)  
**Scope:** `holon-agentic-coder`, `holon-coherence`, `holon-agentic-coder-ref-metadata`  
**Lead Evaluator:** Antigravity Autonomous Agent

---

## 1. Executive Summary

A comprehensive, multi-pillar audit was conducted across all three repositories comprising the Holon ecosystem.
Following the delivery of unified 5-stage Holon flow orchestration (`holon flow`), native PR review loops, and
autonomous calibration, this audit evaluated systemic health across six core pillars:

1. **Intent-Revealing Code & Clean Coding**: Expressiveness, naming clarity, dead code pruning, and orthographic
   consistency (`en-AU`).
2. **Clean Architecture & Decoupling**: Separation of concerns between domain planning, container execution runtimes,
   wire proxies, and git ledgers.
3. **Security & Hermetic Sandbox Boundaries**: Container privilege dropping, filesystem mounts, credential redacting,
   and egress restrictions.
4. **Provenance & Ledger Integrity**: Atomic safety of append-only JSONL ledgers, schema validation, and complete flow
   auditability.
5. **Concurrency, Error Handling & DevEx**: Parallel execution guards, signal handling, process lifecycle isolation, and
   diagnostic feedback.
6. **Calibration Rigour & Metric Isolation**: Verification that quantitative metrics (State Surface Area, diff sizes,
   entropy) reflect true source changes rather than metadata/ledger overhead.

---

## 2. Audit Findings & Remediation Matrix

| Finding ID      | Domain / Pillar    |   Severity    | Summary & Root Cause                                                                                                                                                    | Remediation Bean |   Status    |
| :-------------- | :----------------- | :-----------: | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------- | :---------: |
| **AUD-2026-01** | Metric Isolation   |   **High**    | Metadata & ledger files (`holon-knowledge/**`, `plans/**`, `.holon/**`) were counted in `git diff` metrics, distorting State Surface Area (SSA) and file counts.        | **Bean 0123**    | `completed` |
| **AUD-2026-02** | Clean Architecture | **Important** | Scattered, ad-hoc `subprocess.run(["git", ...])` calls across `flow.py`, `calibration.py`, and `pr_review_loop.py` lack unified error handling and typing.              | **Bean 0124**    | `completed` |
| **AUD-2026-03** | Intent & Style     | **Important** | Residual American English orthography (`initialize`, `behavior`, `optimize`) in code comments and logging messages breaks `en-AU` ecosystem standard.                   | **Bean 0125**    | `completed` |
| **AUD-2026-04** | Security Boundary  | **Important** | Container dispatchers should enforce explicit capability dropping (`--cap-drop=ALL` / `--security-opt=no-new-privileges`) to prevent container escape risks.            | **Bean 0126**    | `completed` |
| **AUD-2026-05** | Provenance Safety  | **Important** | High-concurrency agent execution risks interleaved or partially written lines in `holon-knowledge/ledger/*.jsonl` without explicit advisory file locks (`fcntl.flock`). | **Bean 0127**    | `completed` |

> [!NOTE] **Status refresh (2026-10-22)** The four `todo` rows above were re-verified against `holon-agentic-coder`
> `origin/main` and flipped to `completed`: `sandbox_executor/git.py` exists (0124), zero American-orthography hits
> remain under `apps/sandbox-executor/src` (0125), `--cap-drop` is applied in the dispatchers (0126), and `LedgerLock`
> uses `fcntl.flock(LOCK_EX | LOCK_NB)` with bounded retries (0127). Beans 0124-0127 landed together through PR #86; the
> table originally recorded the state at audit time.

---

## 3. Detailed Pillar Analysis

### Pillar 1: Metric Isolation & Calibration Accuracy (AUD-2026-01)

- **Observation**: During Stage 5 calibration of Bean 0122, `parse_actual_metrics` and `run_review_stage` utilized
  `git diff --shortstat` against the plan branch. Because Stage 2 (Plan), Stage 3 (Execute), and Stage 4 (Review) append
  actions and write plan markdown files, these metadata files were measured as source code changes, inflating files
  changed, insertions, deletions, and State Surface Area (SSA).
- **Remediation**: Implemented `is_metadata_path` and `git diff --numstat` filtering in `calibration.py` and `flow.py`.
  Filtered out all `holon-knowledge/`, `plans/`, `.holon/`, `.beans/`, and `todo/` entries. Ensured zero-file changes
  evaluate to strictly `0.0` SSA.

### Pillar 2: Clean Architecture & Subprocess Isolation (AUD-2026-02)

- **Observation**: Raw `subprocess.run(["git", ...])` invocations are duplicated across multiple modules with divergent
  error checking, timeout parameters, and output decoding.
- **Remediation**: Planned Bean 0124 to centralize git operations into a typed `sandbox_executor.git` abstraction layer.

### Pillar 3: Intent-Revealing Code & Australian English Spelling (AUD-2026-03)

- **Observation**: While top-level guidelines mandate Australian English (`en-AU`), internal module docstrings, logging
  statements, and inline comments contain mixed US spellings (`synchronize`, `serialize`, `initialize`).
- **Remediation**: Planned Bean 0125 to automate linting and systematic substitution to enforce `en-AU` standards across
  all docstrings and logging.
- **Invariant**: Upstream license files (`LICENSE`, Apache 2.0 text) and legal notices must remain word-for-word exact
  as the original upstream text and must not use Australian English. Legal integrity strictly supersedes dialectal
  standardisation.

### Pillar 4: Container Hermeticity & Least Privilege (AUD-2026-04)

- **Observation**: Role execution containers run under Docker with specific network restrictions, but can be further
  hardened by explicitly dropping all default Linux capabilities (`--cap-drop=ALL`) and enabling `no-new-privileges`.
- **Remediation**: Planned Bean 0126 to audit and harden role container launch flags across all dispatchers.

### Pillar 5: Ledger Concurrency & Append-Only Atomicity (AUD-2026-05)

- **Observation**: Action ledgers (`actions.jsonl` and `executions.jsonl`) rely on POSIX filesystem append semantics.
  Under high-frequency concurrent writes from parallel review agents, lines can occasionally race or interleave without
  advisory file locking.
- **Remediation**: Planned Bean 0127 to introduce an advisory file-locking context manager (`fcntl.flock`) for all
  ledger mutations.

---

## 4. Conclusion & Next Steps

All five identified audit items have been formalised into sequential beans (`0123` through `0127`), with Bean 0123
resolved immediately as part of the Bean 0122 execution lifecycle. The remaining four remediation tasks have been
entered into the active triage matrix for systematic scheduling.

As of the 2026-10-22 status refresh, all four remaining tasks are closed: Beans 0124-0127 traversed the 5-stage Holon
flow through `holon-agentic-coder` PR #86 (Stage 4 consensus approval, Stage 5 calibration report in the PR diff) and
are merged into `main`. See the status refresh note in section 2.
