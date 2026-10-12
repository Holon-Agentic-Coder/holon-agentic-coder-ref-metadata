---
# holon-agentic-coder-ref-metadata-0096
title: "Coherence port conflict resolution, down indicator, and comprehensive web telemetry metrics"
status: completed
type: feature
priority: high
created_at: 2026-10-15T07:55:00Z
updated_at: 2026-10-15T20:58:00Z
---

## Summary

Resolve host port conflict hazards and upgrade observability in `holon-coherence`:

1. **Proactive Port Conflict Detection & Dynamic Mapping (Ports 8080 and 8081)**:
   - Proactively check if default proxy port 8080 or web dashboard port 8081 are already in use on the host before
     running Docker.
   - If occupied, automatically probe and find an available open port on the host, map the Docker host port to it
     (`-p 127.0.0.1:{actual_port}:{internal_port}`), and alert the user with a clear warning.
   - Detect and raise a clean descriptive error if Docker fails to publish or expose any requested ports.

2. **Explicit Service Down Status Indicator**:
   - In `holon-coherence status`, when the container is not running, explicitly output
     `🔴 holon-coherence is down (not running)` instead of only dumping an empty `docker ps` table with column headers.

3. **Dynamic Port Discovery & Web UI Context**:
   - In `holon-coherence status` and `web-token`, dynamically query `docker port` to read the exact host mappings for
     8080/tcp and 8081/tcp.
   - Only display the Web Dashboard Token and Access URL if port 8081 was actually published on the container
     (preventing phantom web dashboard messages in headless proxy mode).
   - Display the live optimization dashboard URL pointing to the actual mapped proxy port
     (`http://127.0.0.1:{proxy_port}/holon/`).

4. **Default Offline Log Fallback in `metrics.py`**:
   - Update `WIRE_LOG_DIR` resolution in `src/holon_coherence/commands/metrics.py` to automatically check
     `~/.holon/logs` (where the container actually mounts host logs) if `$WIRE_LOG_DIR` is unset, ensuring offline
     metrics work out of the box.

5. **Comprehensive Throughput & Latency Metrics**:
   - In `CumulativeMetrics` (`mitm_addon.py`):
     - Track `sum_prefill_throughput_tps`, `count_prefill`, and `latest_prefill_tps`.
     - Track `sum_tail_prefill_throughput_tps`, `count_tail_prefill`, and `latest_tail_prefill_tps` (speed on uncached
       tokens).
     - Track `latest_decode_throughput_tps`, `latest_ttft_ms`, and `latest_total_time_ms`.
     - Pass calculated `prefill_tps` and `tail_prefill_tps` from `response()` into `self.metrics.record_response()`.
     - Expose all throughput metrics in `to_dict()` and the `/holon/api/metrics` JSON endpoint.

6. **Provider KV Cache & Reasoning Tokens Observability**:
   - Track cumulative `total_cache_creation_tokens`, `total_cache_read_tokens`, and provider KV Cache Hit Ratio
     (`cache_read_tokens / total_input_tokens`).
   - Track and expose `total_reasoning_tokens` (thinking tokens) from model output details.

7. **Unified Web Dashboard (`/holon/`) & Terminal Metrics Display**:
   - In `render_dashboard_html()` (`/holon/`), add dedicated prominent statistical cards for:
     - **Prefill Speed** (`tok/s` - Average & Latest)
     - **Generation Speed** (`tok/s` - Average & Latest)
     - **Provider KV Cache Hit Ratio** (`%` and cached prompt tokens read)
     - **Reasoning Tokens** (thinking tokens count)
   - Add a **Live Per-Request Transaction Table** at the bottom of the `/holon/` dashboard showing each recent turn's
     TTFT, Prefill TPS, Output TPS, Input/Output Tokens, and Context Reduction.
   - Update `holon-coherence metrics` terminal display to show Prefill Throughput, Provider KV Cache stats, and
     Reasoning Tokens.

## Target Repository

- Repository: `holon-coherence` (`apps/holon-coherence/`)

## Key Tasks

- **Port Checking & Dynamic Fallback (`src/holon_coherence/commands/start.py`)**:
  - Implement proactive port checking for both proxy port (8080) and web dashboard port (8081).
  - When a requested port is taken on the host, automatically select an open free port, map it to the container port,
    and notify the user with a warning.
  - Fail fast with a clear descriptive error if Docker fails to expose ports.
- **Service Down Status & Dynamic Ports (`src/holon_coherence/commands/docker_ops.py`)**:
  - When `is_container_running()` is False, print `🔴 holon-coherence is down (not running).`
  - Query `docker port` to read the exact host mappings for 8080/tcp and 8081/tcp.
  - Only show Web Dashboard credentials if 8081/tcp is actually exposed.
- **Offline Log Path Fallback (`src/holon_coherence/commands/metrics.py`)**:
  - Check `~/.holon/logs` automatically when `WIRE_LOG_DIR` is not explicitly set.
  - Update terminal scorecard formatting to include Prefill TPS, KV Cache Hit Ratio, and Reasoning Tokens.
- **Web UI & Telemetry Throughput (`src/holon_coherence/mitm_addon.py`)**:
  - Add prefill throughput, tail prefill throughput, KV cache stats, and reasoning tokens to `CumulativeMetrics`.
  - Pass calculated `prefill_tps` and `tail_prefill_tps` into `self.metrics.record_response()`.
  - In `render_dashboard_html()`, add dedicated metric cards for Prefill Speed, Generation Speed, KV Cache, and
    Reasoning Tokens.
  - Add a live recent transaction table to the `/holon/` dashboard.
- **Verification & Tests**:
  - Unit tests for port conflict detection, fallback allocation, and exposure error handling in `tests/test_cli.py`.
  - Unit tests for `status` down indicator and dynamic port discovery in `tests/test_cli.py`.
  - Unit tests for `CumulativeMetrics` throughput and cache extensions in `tests/test_mitm_addon.py`.
  - End-to-end verification and markdown formatting.

## Resolution Summary

All 5 stages of the Holon flow have executed and passed:

1. **Stage 1 (Intent)**:
   - Branch: `I-1792052725-coherence-port-conflicts-down-status-and-throughput-metrics/_`
   - Logged in `holon-knowledge/ledger/intents.jsonl`.
2. **Stage 2 (Plan)**:
   - Branch: `.../P-1792052725-antigravity-agent-gemini-3.8-flash-medium/_`
   - Plan document: `plans/P-1792052725-antigravity-agent-gemini-3.8-flash-medium.md`
   - Logged in `holon-knowledge/ledger/plans.jsonl`.
3. **Stage 3 (Execute)**:
   - Branch: `.../E-1792052726-antigravity-agent-gemini-3.8-flash-medium/_`
   - Logged in `holon-knowledge/ledger/executions.jsonl`.
   - Core implementation:
     - `src/holon_coherence/commands/start.py`: Added `is_port_in_use`, `find_available_port`, and collision avoidance
       loop between proxy port and web dashboard port during host port conflict fallbacks.
     - `src/holon_coherence/commands/docker_ops.py`: Added `get_container_mapped_port`, explicit service down indicator
       (`🔴 holon-coherence is down (not running)`), and exception-guarded `docker ps` execution.
     - `src/holon_coherence/commands/metrics.py`: Dynamic port discovery for live metrics, deduplicated candidate log
       paths with automatic `~/.holon/logs` fallback, prompt prefill throughput, provider KV cache stats, and reasoning
       tokens formatting with defensive null handling.
     - `src/holon_coherence/mitm_addon.py`: Extended `CumulativeMetrics` with prefill throughput, tail prefill
       throughput, KV cache stats, reasoning tokens, and upgraded `/holon/` web dashboard with prominent statistical
       cards and a live recent transaction table.
     - Test coverage: Added comprehensive unit tests in `tests/test_cli.py` and `tests/test_mitm_addon.py`, resulting in
       579 passing unit tests.
4. **Stage 4 (PR Creation & Review Loop)**:
   - GitHub Pull Request: **[PR #18](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/18)**.
   - Executed iterative review loop (Iterations 1–4).
   - Iteration 1 & 2: Addressed hygiene formatting, macOS CI Docker mocking, port collisions, and defensive null token
     parsing in commit `9eda1b7`.
   - Iteration 3: 3-Agent Ensemble Review unanimously **`APPROVED`** (3/3 votes, 0 Critical, 0 Important, 0 Nit; Review
     [#5531291819](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/18#pullrequestreview-5531291819)).
   - Iteration 4: Integrated Stage 5 calibration report into the PR branch, expanded
     `plans/P-1792052725-antigravity-agent-gemini-3.8-flash-medium.md` to full specification (commit `58c2bbb`), and
     3-Agent Ensemble Review unanimously **`APPROVED`** (3/3 votes, 0 Critical, 0 Important, 0 Nit).
   - Consensus review posted to GitHub PR #18:
     [Review #5532182747](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/18#pullrequestreview-5532182747).
   - All 7 GitHub Actions CI workflow checks passed cleanly (`SUCCESS`).
   - Merged to `main` at commit `6599f4b96a6c51e8c9df4fb6bdf23b35137d0eca`.
5. **Stage 5 (Calibration)**:
   - Branch:
     `I-1792052725-coherence-port-conflicts-down-status-and-throughput-metrics/P-1792052725-antigravity-agent-gemini-3.8-flash-medium/E-1792052726-antigravity-agent-gemini-3.8-flash-medium/calibrated`
   - Calibration Report: `plans/P-1792052725-antigravity-agent-gemini-3.8-flash-medium_calibration.md`
   - Result: $P(\text{success})_{\text{actual}} = 1.00$, $EV_{\text{actual}} = 76.90$ ($\Delta EV = +8.00$).
   - Pushed `/calibrated` branch to `origin`.
