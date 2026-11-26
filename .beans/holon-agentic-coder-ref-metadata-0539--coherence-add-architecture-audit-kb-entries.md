---
# holon-agentic-coder-ref-metadata-0539
title: "Add 2026-11 architecture audit patterns and failure modes to holon-coherence KB"
status: todo
type: task
priority: normal
tags:
  - holon-coherence
  - knowledge-base
  - architecture
  - audit
created_at: 2026-11-26T13:35:00Z
updated_at: 2026-11-26T13:35:00Z
---

## Problem

Key architectural patterns and critical failure modes identified during the 2026-11 review of `holon-coherence`
(`HEAD 18084f3`) should be codified inside `holon-coherence/holon-knowledge/kb/` so future flows reuse clean pipeline
patterns and avoid security/SSE regressions. Under the Sole Change Path rule, these KB files must land via `holon flow`.

## Proposed Change

Run `holon flow` targeting `holon-coherence` to add the 7 curated, target-native KB JSON files below to
`holon-knowledge/kb/patterns/` and `holon-knowledge/kb/failure_modes/`. All payloads conform to
`knowledgebase_schema.md` and contain zero harness references.

### 1. `holon-knowledge/kb/patterns/KB-pattern-declarative-proxy-step-pipeline.json`

```json
{
  "kb_id": "KB-pattern-declarative-proxy-step-pipeline",
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
  "tags": ["proxy", "architecture", "pipeline", "modularity"],
  "human_approved": true,
  "payload": {
    "name": "Declarative Fail-Open StepSpec Proxy Pipeline",
    "description": "Keep MitmproxyAddon.request/response under 30 lines by composing small (33-146L), single-purpose StepSpec modules operating over typed RequestContext/ResponseContext objects with explicit Outcome.CONTINUE/HALT control flow and run_guarded fail-open isolation.",
    "modules": [
      "src/holon_coherence/proxy/steps/base.py",
      "src/holon_coherence/proxy/steps/__init__.py",
      "src/holon_coherence/proxy/addon.py"
    ],
    "known_pitfalls": [
      "Retire legacy sys.modules compat probes (_compat.py) promptly so step execution stays side-effect free",
      "Copy payload once at the entry boundary rather than calling deepcopy inside multiple sequential steps"
    ]
  }
}
```

### 2. `holon-knowledge/kb/patterns/KB-pattern-locked-complexity-and-self-doc-hygiene.json`

```json
{
  "kb_id": "KB-pattern-locked-complexity-and-self-doc-hygiene",
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
  "tags": ["complexity", "hygiene", "self-documenting", "testing"],
  "human_approved": true,
  "payload": {
    "name": "Locked Complexity Baseline Ratchet & Dynamic Self-Doc Verification",
    "description": "Enforce a 200-line default module budget, lock inline complexity # noqa counts with an automated ratchet test (test_complexity_baseline.py), and dynamically enforce self-documenting symbol naming across every source module (test_repo_self_doc.py).",
    "modules": [
      "holon-config/hygiene/module_budgets.json",
      "tests/test_complexity_baseline.py",
      "tests/test_module_budgets.py",
      "tests/test_repo_self_doc.py"
    ],
    "known_pitfalls": [
      "Remove per-module *_self_doc.py duplicates once covered globally by test_repo_self_doc.py",
      "Pair complexity gates with static type checking (mypy/pyright) in CI"
    ]
  }
}
```

### 3. `holon-knowledge/kb/patterns/KB-pattern-honest-unmeasured-wire-telemetry.json`

```json
{
  "kb_id": "KB-pattern-honest-unmeasured-wire-telemetry",
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
  "tags": ["telemetry", "metrics", "security", "redaction"],
  "human_approved": true,
  "payload": {
    "name": "Provider-Agnostic X-Holon-* Telemetry with Honest Unmeasured Labels & Recursive Scrubbing",
    "description": "Emit uniform X-Holon-* wire telemetry headers across providers, explicitly report 'unmeasured' for non-streaming or sub-50ms decode timings rather than synthetic estimates, and scrub 16+ sensitive headers, query parameters, token regexes, and recursive JSON bodies before persisting wire logs.",
    "modules": [
      "src/holon_coherence/proxy/steps/record_metrics.py",
      "src/holon_coherence/metrics_math.py",
      "src/holon_coherence/proxy/timing.py",
      "src/holon_coherence/proxy/scrubbing.py"
    ],
    "known_pitfalls": [
      "Bound async wire-log pending queues and rotate transactions/turn logs to cap disk growth",
      "Ensure HybridCacheStore entries undergo the same scrubbing/permission hygiene as wire logs"
    ]
  }
}
```

### 4. `holon-knowledge/kb/failure_modes/KB-failure-world-writable-ca-mount-permissions.json`

```json
{
  "kb_id": "KB-failure-world-writable-ca-mount-permissions",
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
  "tags": ["security", "ca", "permissions", "secrets", "docker"],
  "human_approved": true,
  "payload": {
    "name": "Container Startup Overwrites CA Private Key Permissions to 0o666 / 0o777",
    "description": "Passing world_accessible_mounts=True from commands/start.py into container/lifecycle.py chmods ~/.holon/{proxy-ca,cache,logs} to 0o777 and holon-root-ca.key / mitmproxy-ca.pem to 0o666, completely nullifying ca_generator.py's 0o700/0o600 hardening. Paired with passing HOLON_COHERENCE_WEB_PASSWORD on docker/mitmproxy argv and ?token= URLs plus unscrubbed payloads in 0o777 cache.",
    "symptoms": [
      "MITM Root CA private key is world-readable and world-writable on host",
      "Web UI password visible in process table (ps) and terminal URL logs"
    ],
    "root_causes": [
      "Broad chmod 0o777/0o666 workaround for container UID mismatch instead of UID/GID mapping or read-only cert mounts",
      "Passing secret values via CLI flags and URL query parameters"
    ],
    "mitigations": [
      {
        "strategy": "Enforce strict 0o700/0o600 permissions and file-based secret passing",
        "description": "Remove world_accessible_mounts=True, align container UID/GID or use separate cert-only mounts keeping private keys 0o600, pass web_password via 0o600 env/config files, and scrub cached payloads.",
        "cost": "Low",
        "effectiveness": 0.99
      }
    ]
  }
}
```

### 5. `holon-knowledge/kb/failure_modes/KB-failure-unauthenticated-hostless-proxy-control.json`

```json
{
  "kb_id": "KB-failure-unauthenticated-hostless-proxy-control",
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
  "tags": ["security", "proxy", "dashboard", "csrf"],
  "human_approved": true,
  "payload": {
    "name": "Host-Less /holon/* Dashboard Hijack & Unauthenticated /holon/api/mode",
    "description": "proxy/steps/serve_dashboard.py intercepts any request matching path_clean under /holon/* without validating Host, sets Access-Control-Allow-Origin: *, and accepts unauthenticated POST /holon/api/mode payloads with an unvalidated wire_log_dir path (while GET /holon/api/mode ignores runtime overrides when HOLON_PASSIVE_MONITORING=1).",
    "symptoms": [
      "External websites or proxied traffic under /holon/* collide with the local control plane",
      "Any local process or cross-origin page can switch proxy mode or redirect wire logs to arbitrary host paths"
    ],
    "root_causes": [
      "Route matcher checks path without explicit loopback/holon Host allowlist",
      "State-mutating control endpoint lacks token auth, CORS restriction, and path containment validation"
    ],
    "mitigations": [
      {
        "strategy": "Validate Host header, authenticate POST /holon/api/mode, and confine wire_log_dir",
        "description": "Only intercept explicit localhost/holon Host headers, require web-token authentication on mode mutations, drop wildcard CORS, and confine wire_log_dir via Path.resolve() containment.",
        "cost": "Low",
        "effectiveness": 0.98
      }
    ]
  }
}
```

### 6. `holon-knowledge/kb/failure_modes/KB-failure-unbuffered-sse-chunks-without-wire-tests.json`

```json
{
  "kb_id": "KB-failure-unbuffered-sse-chunks-without-wire-tests",
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
  "tags": ["sse", "streaming", "testing", "mitmproxy"],
  "human_approved": true,
  "payload": {
    "name": "Unbuffered SSE Chunk Splitting Masked by Duck-Typed Fake Proxy Tests",
    "description": "providers/translation.py splits streaming TCP chunks on newline without a carry buffer for partial lines, and proxy/steps/sse_tap.py decodes raw byte chunks without an incremental UTF-8 decoder. Unit tests relied solely on duck-typed fake flow objects with zero mitmproxy.test.tflow or HTTPServer wire tests, letting chunk-boundary corruption go untested.",
    "symptoms": [
      "JSON SSE events split across TCP packets are silently dropped during translation",
      "Multi-byte UTF-8 characters split across chunks raise or corrupt tap output"
    ],
    "root_causes": [
      "Per-chunk stateless .split('\\n') and .decode('utf-8') instead of persistent line buffer and incremental UTF-8 decoder",
      "Absence of real mitmproxy tflow and chunked HTTPServer wire tests"
    ],
    "mitigations": [
      {
        "strategy": "Add incremental line + UTF-8 buffering and wire-level chunk-split tests",
        "description": "Carry partial SSE lines between chunks, use codecs.getincrementaldecoder('utf-8'), and add real mitmproxy.test.tflow + local HTTPServer tests splitting mid-JSON and mid-rune.",
        "cost": "Low",
        "effectiveness": 0.95
      }
    ]
  }
}
```

### 7. `holon-knowledge/kb/failure_modes/KB-failure-hot-path-deepcopy-and-provider-drift.json`

```json
{
  "kb_id": "KB-failure-hot-path-deepcopy-and-provider-drift",
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
  "tags": ["performance", "dry", "providers", "extensibility"],
  "human_approved": true,
  "payload": {
    "name": "Hot-Path Deepcopy Multiplication & Divergent Provider Detection Logic",
    "description": "Each proxied LLM request undergoes up to 4x copy.deepcopy calls, 2x response token parses, and 3x cache payload normalizations while proxy/addon.py:detect_provider and providers/__init__.py disagree on claude/system-vs-messages precedence and closed ProviderName Literals block extensible provider registration.",
    "symptoms": [
      "Added proxy latency on large multi-turn context payloads",
      "Routing vs token-cleaning steps can classify edge payloads to different providers"
    ],
    "root_causes": [
      "Independent helper functions performing defensive deep copies and re-parsing instead of sharing normalized context per flow",
      "Duplicate detect_provider implementations instead of ProviderFormat.matches(url, payload)"
    ],
    "mitigations": [
      {
        "strategy": "Single boundary copy + registry-driven ProviderFormat.matches()",
        "description": "Copy mutated payloads at most once per request, parse response tokens once, and consolidate provider classification into a registry-backed ProviderFormat.matches() seam.",
        "cost": "Medium",
        "effectiveness": 0.9
      }
    ]
  }
}
```

## Acceptance Criteria

- All 7 `KB-*.json` files above are committed under `holon-knowledge/kb/{patterns,failure_modes}/` via `holon flow`
  targeting `holon-coherence`.
- All JSON files pass schema validation and contain zero harness path references.

## Notes

- Target repository: `holon-coherence` (must execute via `holon flow`; never hand-edit `apps/holon-coherence/main`).
- Source: 2026-11 ecosystem architecture & source-code review (`docs/ecosystem-audit-report-2026-11.md`).
