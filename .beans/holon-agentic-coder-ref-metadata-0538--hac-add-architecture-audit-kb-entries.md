---
# holon-agentic-coder-ref-metadata-0538
title: "Add 2026-11 architecture audit patterns and failure modes to holon-agentic-coder KB"
status: todo
type: task
priority: normal
tags:
  - holon-agentic-coder
  - knowledge-base
  - architecture
  - audit
created_at: 2026-11-26T13:35:00Z
updated_at: 2026-11-26T13:35:00Z
---

## Problem

Key architectural patterns and systemic failure modes uncovered during the 2026-11 review of `holon-agentic-coder`
(`HEAD f1e18bcd`) are not yet persisted inside `holon-knowledge/kb/` where Stage 2 planners and Stage 4 reviewers can
consult them. Under the Sole Change Path rule, target repository KB entries must land via `holon flow`.

## Proposed Change

Run `holon flow` targeting `holon-agentic-coder` to add the 7 curated, target-native KB JSON files below to
`holon-knowledge/kb/patterns/` and `holon-knowledge/kb/failure_modes/`. All payloads conform to
`docs/knowledgebase_schema.md` and contain zero harness references.

### 1. `holon-knowledge/kb/patterns/KB-pattern-worktree-git-hardening.json`

```json
{
  "kb_id": "KB-pattern-worktree-git-hardening",
  "kb_type": "pattern",
  "version": "1.0",
  "created_ts": "2026-11-26T13:35:00Z",
  "updated_ts": "2026-11-26T13:35:00Z",
  "created_by": "architecture-audit-2026-11",
  "status": "active",
  "evidence": {
    "ledger_refs": ["architecture-audit-2026-11-26"],
    "success_count": 1,
    "failure_count": 0
  },
  "tags": ["security", "git", "worktree", "docker", "secrets"],
  "human_approved": true,
  "payload": {
    "name": "Host .git Worktree Metadata Hardening & 0o600 Temp Env-Files",
    "description": "Isolate containerised role execution from host git hook/config tampering by rejecting extensions.worktreeConfig=true, mounting .git/{hooks,config,modules} read-only with inert sentinels, checking POSIX ACLs, and passing secrets exclusively via 0o600 temp env-files in 0o700 dirs.",
    "modules": [
      "apps/sandbox-executor/src/sandbox_executor/git_flow.py",
      "apps/sandbox-executor/src/sandbox_executor/launcher/env_files.py",
      "apps/sandbox-executor/src/sandbox_executor/redaction.py"
    ],
    "known_pitfalls": [
      "Always pair --add-host metadata overrides with network-level blocks if direct IP egress is undesirable",
      "Avoid overwriting secret mounts with writable tmpfs or process-umask file copies"
    ]
  }
}
```

### 2. `holon-knowledge/kb/patterns/KB-pattern-hermetic-pytest-conftest.json`

```json
{
  "kb_id": "KB-pattern-hermetic-pytest-conftest",
  "kb_type": "pattern",
  "version": "1.0",
  "created_ts": "2026-11-26T13:35:00Z",
  "updated_ts": "2026-11-26T13:35:00Z",
  "created_by": "architecture-audit-2026-11",
  "status": "active",
  "evidence": {
    "ledger_refs": ["architecture-audit-2026-11-26"],
    "success_count": 1,
    "failure_count": 0
  },
  "tags": ["testing", "pytest", "hermeticity", "isolation"],
  "human_approved": true,
  "payload": {
    "name": "Suite-Wide Hermetic pytest Guards in conftest.py",
    "description": "Enforce global git identity isolation, credential/keychain scrubbing, active-checkout ledger mutation detection, GitHub CLI write guards, and socket/network guards inside tests/conftest.py alongside automated environment-reference and repository-hygiene drift suites.",
    "modules": [
      "apps/sandbox-executor/tests/conftest.py",
      "apps/sandbox-executor/tests/test_environment_reference.py",
      "apps/sandbox-executor/tests/test_repository_hygiene.py"
    ],
    "known_pitfalls": [
      "Avoid hardcoded test-function name allowlists; use explicit pytest markers",
      "Prefer adapter/contract test seams over monkeypatching private _-prefixed symbols"
    ]
  }
}
```

### 3. `holon-knowledge/kb/patterns/KB-pattern-three-ledger-fragment-routing.json`

```json
{
  "kb_id": "KB-pattern-three-ledger-fragment-routing",
  "kb_type": "pattern",
  "version": "1.0",
  "created_ts": "2026-11-26T13:35:00Z",
  "updated_ts": "2026-11-26T13:35:00Z",
  "created_by": "architecture-audit-2026-11",
  "status": "active",
  "evidence": {
    "ledger_refs": ["architecture-audit-2026-11-26"],
    "success_count": 1,
    "failure_count": 0
  },
  "tags": ["ledger", "provenance", "concurrency", "resilience"],
  "human_approved": true,
  "payload": {
    "name": "Append-Only 3-Ledger Fragment Routing & Prefix Verification",
    "description": "Preserve provenance without cross-flow merge conflicts by routing concurrent flow writes to per-intent pending fragments under holon-knowledge/ledger/pending/, enforcing LedgerLock advisory locking with fsync and prefix-rewrite verification, and promoting fragments idempotently on main.",
    "modules": [
      "apps/sandbox-executor/src/sandbox_executor/ledger/route.py",
      "apps/sandbox-executor/src/sandbox_executor/ledger/fragments.py",
      "apps/sandbox-executor/src/sandbox_executor/ledger/promote.py",
      "apps/sandbox-executor/src/sandbox_executor/ledger/lock.py"
    ],
    "known_pitfalls": ["Keep runtime metadata paths relative to target-native holon-knowledge/ only"]
  }
}
```

### 4. `holon-knowledge/kb/failure_modes/KB-failure-bidirectional-flow-entrypoint-cycle.json`

```json
{
  "kb_id": "KB-failure-bidirectional-flow-entrypoint-cycle",
  "kb_type": "failure_mode",
  "version": "1.0",
  "created_ts": "2026-11-26T13:35:00Z",
  "updated_ts": "2026-11-26T13:35:00Z",
  "created_by": "architecture-audit-2026-11",
  "status": "active",
  "evidence": {
    "ledger_refs": ["architecture-audit-2026-11-26"],
    "success_count": 0,
    "failure_count": 1
  },
  "tags": ["architecture", "import-cycle", "layer-boundary"],
  "human_approved": true,
  "payload": {
    "name": "Bidirectional flow <-> entrypoint and ledger <-> knowledge Import Cycles",
    "description": "Mutually importing flow and entrypoint (11 edges each way) or ledger and knowledge (via redaction imports), paired with deferred private imports from flow in review_target.py and side-effecting resolve_flow_proxy_choice() in FlowContext.__post_init__, tangles host orchestration and in-container execution layers.",
    "symptoms": [
      "Deferred function-local imports required to avoid ImportError at startup",
      "Dataclass construction triggers external proxy/network lookup",
      "Unit tests require heavy monkeypatching across internal private module boundaries"
    ],
    "root_causes": [
      "Shared domain contracts, target models, and redactors live inside higher orchestration packages instead of leaf modules",
      "Configuration side effects executed inside __post_init__"
    ],
    "mitigations": [
      {
        "strategy": "Invert dependencies via leaf contract modules and explicit factories",
        "description": "Extract shared contracts/redaction interfaces into leaf packages, construct FlowContext via an explicit factory, and enforce acyclic layer direction with an import test.",
        "cost": "Medium refactor",
        "effectiveness": 0.95
      }
    ]
  }
}
```

### 5. `holon-knowledge/kb/failure_modes/KB-failure-monolithic-review-loop-complexity.json`

```json
{
  "kb_id": "KB-failure-monolithic-review-loop-complexity",
  "kb_type": "failure_mode",
  "version": "1.0",
  "created_ts": "2026-11-26T13:35:00Z",
  "updated_ts": "2026-11-26T13:35:00Z",
  "created_by": "architecture-audit-2026-11",
  "status": "active",
  "evidence": {
    "ledger_refs": ["architecture-audit-2026-11-26"],
    "success_count": 0,
    "failure_count": 1
  },
  "tags": ["complexity", "maintainability", "review-loop"],
  "human_approved": true,
  "payload": {
    "name": "Extreme Cyclomatic Complexity & God Object Growth in Orchestration Loops",
    "description": "Unbounded stateful loops accumulate 17-18 parameters, ~25 locals, and cyclomatic complexity up to 205-210 (flow/review/loop.py:run_review_loop), alongside CC~50 functions (entrypoint/planner.py:main, turns.py:run_turn, flow/stages/review.py) and 5-mixin bags like ExecutionRun.",
    "symptoms": [
      "Single functions exceed 300-750 lines and Ruff C901 limits via inline suppressions",
      "Merge conflicts converge repeatedly on oversized loop/calibration modules",
      "High cognitive load and fragile white-box mocking in unit tests"
    ],
    "root_causes": [
      "Inline state mutation across multi-stage retries, CI waits, consensus evaluation, and resolution without a dedicated step object",
      "Adding new flags/options directly to function signatures instead of typed request/context objects"
    ],
    "mitigations": [
      {
        "strategy": "Decompose into stateful coordinator + pure decision functions",
        "description": "Replace monolithic loops and multi-mixin inheritance with a focused coordinator holding named step methods and pure functional verdict transitions.",
        "cost": "High initially, lowers long-term churn",
        "effectiveness": 0.9
      }
    ]
  }
}
```

### 6. `holon-knowledge/kb/failure_modes/KB-failure-env-registry-runtime-drift.json`

```json
{
  "kb_id": "KB-failure-env-registry-runtime-drift",
  "kb_type": "failure_mode",
  "version": "1.0",
  "created_ts": "2026-11-26T13:35:00Z",
  "updated_ts": "2026-11-26T13:35:00Z",
  "created_by": "architecture-audit-2026-11",
  "status": "active",
  "evidence": {
    "ledger_refs": ["architecture-audit-2026-11-26"],
    "success_count": 0,
    "failure_count": 1
  },
  "tags": ["config", "dry", "documentation", "resilience"],
  "human_approved": true,
  "payload": {
    "name": "Declarative Env Registry Drift & Duplicated Normalization Helpers",
    "description": "When env_registry.py documents keys separately from runtime parsing, consumer behavior diverges silently (e.g. HOLON_AGENT_EFFORT documented for Claude while only read by AntigravityAgentRunner). Parallel agent-ID normalizers (4 copies), git diff --numstat parsers (5 copies), and silent except Exception: pass blocks compound maintenance drift.",
    "symptoms": [
      "Environment reference tables disagree with actual runner consumption",
      "Subtle behavioral divergence across duplicated ID normalizers or diff parsers",
      "Cleanup errors or credential unlink failures vanish under except Exception: pass"
    ],
    "root_causes": [
      "Registry acts as documentation metadata rather than the single runtime source of truth",
      "Utility parsing written inline across stages instead of centralized in git.py / agent_defaults.py"
    ],
    "mitigations": [
      {
        "strategy": "Single-source env definitions and shared helpers",
        "description": "Have runtime config resolution read directly from env_registry.py definitions, consolidate ID/numstat helpers, and forbid silent except Exception: pass blocks.",
        "cost": "Low",
        "effectiveness": 0.95
      }
    ]
  }
}
```

### 7. `holon-knowledge/kb/failure_modes/KB-failure-container-resource-and-secret-perm-gaps.json`

```json
{
  "kb_id": "KB-failure-container-resource-and-secret-perm-gaps",
  "kb_type": "failure_mode",
  "version": "1.0",
  "created_ts": "2026-11-26T13:35:00Z",
  "updated_ts": "2026-11-26T13:35:00Z",
  "created_by": "architecture-audit-2026-11",
  "status": "active",
  "evidence": {
    "ledger_refs": ["architecture-audit-2026-11-26"],
    "success_count": 0,
    "failure_count": 1
  },
  "tags": ["security", "docker", "secrets", "supply-chain"],
  "human_approved": true,
  "payload": {
    "name": "Missing Container Resource Limits, Permissive Secret Unpacking, & Unpinned Installers",
    "description": "Strong .git mount hardening is weakened when role containers launch without --memory/--cpus/--pids-limit/--read-only, mount /tmp/intent.json writable, rely only on --add-host against direct metadata IPs, unpack secret bundles without explicit 0o600 permissions (or log unredacted errors), or curl | bash unpinned installers in Dockerfile.",
    "symptoms": [
      "Runaway agent subprocesses can exhaust host memory or PIDs",
      "Secret bundle files inherit permissive umask or broad local_llm directory modes (0o777/0o644)"
    ],
    "root_causes": [
      "Container flags omitted resource quotas and read-only intent mount qualifier",
      "File creation helpers omitted explicit os.chmod(0o600/0o700) and redaction wrapping"
    ],
    "mitigations": [
      {
        "strategy": "Enforce Docker quotas, 0o600 permissions, and checksum-pinned builds",
        "description": "Pass --memory/--cpus/--pids-limit and :ro mounts, explicitly set 0o600/0o700 on secrets and local_llm configs, add -- terminators in git commands, and verify SHA256 checksums for Dockerfile downloads.",
        "cost": "Low",
        "effectiveness": 0.95
      }
    ]
  }
}
```

## Acceptance Criteria

- All 7 `KB-*.json` files above are committed under `holon-knowledge/kb/{patterns,failure_modes}/` via `holon flow`
  targeting `holon-agentic-coder`.
- `sandbox_executor.knowledge.wisdom.load_index()` loads every entry cleanly with zero schema/JSON errors and zero
  harness path leaks.

## Notes

- Target repository: `holon-agentic-coder` (must execute via `holon flow`; never hand-edit
  `apps/holon-agentic-coder/main`).
- Source: 2026-11 ecosystem architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
