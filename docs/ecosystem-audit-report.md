# Holon Ecosystem Quality, Architecture, Security, and DevEx Audit Report

**Audit Date:** 2026-10-18  
**Bean Reference:** Bean `0106`  
**Scope:** `holon-agentic-coder`, `holon-coherence`, and `holon-agentic-coder-ref-metadata`

---

## 1. Executive Summary

A comprehensive, multi-dimensional audit was conducted across all three repositories in the Holon ecosystem covering:

1. **Source Code Quality & Architecture**: Flow stage boundaries, conflict resolution under concurrent execution, action
   ledger schema consistency, and CLI modularity.
2. **Security & Hermeticity**: Container sandbox isolation, credential redaction, file permissions, and pre-commit
   secret/scratch interception.
3. **Developer Experience (DevEx) & Tooling**: Build/lint Makefile parity, automated image installation, subagent
   artifact archiving, CI test integration, and documentation readability.

All identified findings have been tracked via sequential beans (`0104`–`0121`) and resolved through verified commits and
the 5-stage Holon flow.

---

## 2. Audit Findings & Remediation Matrix

| ID         | Domain                 |  Severity  | Finding Summary                                                                                       | Remediation Bean & Status                                                                                          |
| :--------- | :--------------------- | :--------: | :---------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------- |
| **AUD-01** | Flow / Concurrency     |  **High**  | Concurrent flow runs and parallel PR merges to `main` can cause branch divergence and JSONL conflicts | **Bean 0121** (`completed`): Proactive conflict detection across all 5 stages + JSONL union-append reconciliation. |
| **AUD-02** | Security / Git Hygiene |  **High**  | Ephemeral scratch files (`tmp/*`, `.index/*`) and API keys risk accidental staging before PR review   | **Bean 0110** (`completed`): Implemented `pre_commit_check.py` scanning credentials and blocking scratch globs.    |
| **AUD-03** | Flow / Observability   |  **High**  | `executions.jsonl` only logged coarse stage completion without discrete review/resolver actions       | **Bean 0113** (`completed`): Added granular action event logging across review loop evaluations and resolutions.   |
| **AUD-04** | Flow / PR Review       |  **High**  | GitHub blocks PR authors from `gh pr review --approve` (HTTP 422), hiding consensus reports           | **Bean 0119** (`completed`): Dual-posts top-level `gh pr comment` + official review with HTTP 422 fallback.        |
| **AUD-05** | Build / DevEx          | **Medium** | Asymmetric `Makefile` targets (`build-image` vs `build-images`, missing `tools` and `lint-*`)         | **Bean 0116** (`completed`): Aligned `Makefile` targets across `holon-agentic-coder` and `holon-coherence`.        |
| **AUD-06** | CI / Testing           | **Medium** | Metadata repository lacked automated Python unit test (`pytest`) and lint (`ruff`) checks in CI       | **Bean 0107** (`completed`): Added `pyproject.toml`, `uv run ruff`, and `uv run pytest` to `test-hygiene.yml`.     |
| **AUD-07** | Flow / PR Metadata     | **Medium** | Autonomous PR creation used raw branch names instead of semantic titles and structured Markdown       | **Bean 0109** (`completed`): Implemented `generate_semantic_pr_metadata` and `create_or_update_pr`.                |
| **AUD-08** | Documentation / DevEx  | **Medium** | Root `README.md` mixed quick-start steps with deep worktree mechanics and lacked status badges        | **Bean 0111** (`completed`): Slimmed `README.md` with badges and extracted `docs/architecture-overview.md`.        |
| **AUD-09** | Hygiene / Tooling      |  **Low**   | Completed `.subagent/` intermediate review files accumulated without structured archival retention    | **Bean 0108** (`completed`): Added `--archive` relocation and 30-day retention pruning to `clean_workspace.py`.    |
| **AUD-10** | Legal / Standards      |  **Low**   | Licence files and Australian English (`en-AU`) orthography needed unification across all 3 repos      | **Beans 0104 & 0105** (`completed`): Standardised Apache 2.0 `LICENSE` and `en-AU` spelling across the ecosystem.  |

---

## 3. Architectural & Security Verification

### 3.1 Container Sandbox Hermeticity (`holon-agentic-coder`)

- **Privilege & Network Hardening**: Containers execute as non-root `holon` (`uid=1000`) with `--cap-drop=NET_RAW` and
  cloud metadata sinkholes (`169.254.169.254`, `metadata.google.internal`, `instance-data` routed to `127.0.0.1`).
- **Read-Only Credential Mounts**: Host session directories mount `:ro` with ephemeral `--tmpfs` overlays for writable
  caches and logs (Beans `0112`, `0114`).
- **Universal Credential Mapping**: Host CLI validates `HOLON_AGENT_KEY` without leaking vendor tokens into command-line
  arguments or PR metadata.

### 3.2 Proxy Telemetry & Cache Integrity (`holon-coherence`)

- **File Mode Hardening**: PKI certificates, SQLite cache databases, and wire logs enforce `0o700` directory and `0o600`
  file permissions.
- **Recursive Secret Scrubbing**: Payload and header scrubbers redact API keys, bearer tokens, and `auth`/`credential`
  dictionary fields prior to disk persistence.
- **Mathematical Telemetry Consistency**: Prefill throughput, tail prefill throughput, and streaming decode throughput
  share unified formulas and guards across live in-memory metrics, `/holon/api/metrics`, web dashboard, and CLI tables.
