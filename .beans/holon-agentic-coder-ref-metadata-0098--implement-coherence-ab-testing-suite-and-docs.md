---
# holon-agentic-coder-ref-metadata-0098
title: "Implement comprehensive A/B testing suite and documentation for holon-coherence"
status: completed
type: feature
priority: high
tags:
  - testing
  - ab-testing
  - benchmarking
  - documentation
  - token-reduction
  - holon-coherence
created_at: 2026-10-15T22:35:00Z
updated_at: 2026-10-16T19:20:00Z
---

## Summary

Build an extensive A/B testing suite and comprehensive operator documentation for evaluating `holon-coherence` context
optimization and performance benefits:

1. **A/B Testing Harness / Runner**:
   - Provide an automated testing vehicle (`holon-coherence ab-test` or benchmark runner) that executes reproducible
     agent trace payloads against two parallel or sequential targets:
     - **Variant A (Baseline / Control)**: Proxy in passive monitoring mode (`HOLON_PASSIVE_MONITORING=1`) or
       unoptimized pass-through.
     - **Variant B (Optimized / Treatment)**: Proxy with active context cleaning, tool call output deduplication, prompt
       cache breakpoint injection, and semantic disk caching.
   - Collect and calculate differential scorecards across:
     - **Total Tokens Transmitted**: Prompt tokens, completion tokens, cache read tokens.
     - **Context Reduction**: Percentage reduction in transmitted prompt tokens and omitted characters.
     - **Tool Calls Pruned**: Count of redundant historical tool execution results omitted.
     - **Latency & Throughput**: Time To First Token (TTFT) and decode speed comparisons.
     - **Semantic Integrity**: Verify assistant completion validity and functional parity between baseline and optimized
       runs (asserting that optimization does not break tool calling or code generation).

2. **Extensive Integration & Regression Test Suite**:
   - Add comprehensive tests in `tests/test_ab_testing.py` covering:
     - Multi-turn conversation traces with repeating tool outputs (e.g. repetitive `git status` or build outputs).
     - Cache breakpoint injection efficacy across Anthropic and OpenAI protocols.
     - Streaming SSE chunk delivery and timing accuracy between Variant A and Variant B.
     - Assertion of statistically significant token reduction (>20% reduction on repetitive turn workloads) without
       payload loss or tool call corruption.

3. **Operator Documentation & Guides**:
   - Create `docs/ab_testing_guide.md` in `holon-coherence` providing:
     - Step-by-step instructions for running A/B comparisons locally, in Docker, and in CI.
     - Configuration flags: `HOLON_PASSIVE_MONITORING`, `COHERENCE_TOKEN_REDUCTION`, `HOLON_PROXY_PORT`.
     - Sample terminal outputs and interpretation of the comparative scorecard.
     - Methodological guidelines on authentic data sampling (strictly observing repository Rule 10 — zero synthetic mock
       data for official benchmarks).
   - Update `README.md` to reference the A/B testing suite and optimization benchmarks.

## Target Repository

- Repository: `holon-coherence` (`apps/holon-coherence/`)
- Target Files:
  - `src/holon_coherence/commands/ab_test.py`
  - `src/holon_coherence/cli.py`
  - `src/holon_coherence/mitm_addon.py`
  - `src/holon_coherence/commands/docker_ops.py`
  - `src/holon_coherence/commands/metrics.py`
  - `tests/test_ab_testing.py`
  - `docs/ab_testing_guide.md`

## Acceptance Criteria

- [x] Automated A/B test command/script compares Variant A (baseline / passive) vs Variant B (optimized) across real
      traffic workloads (`--command`), two authentic wire log sessions (`--baseline` & `--optimized`), live proxy replay
      (`--trace-file` & `--live`), and offline differential evaluation.
- [x] Outputs a comparative scorecard displaying prompt tokens reduced, tool calls pruned, cache hit ratios, authentic
      TTFT delta, and decode throughput.
- [x] Integration test suite in `tests/test_ab_testing.py` verifies reduction assertions, streaming behavior, and
      payload equivalence across 30 dedicated test cases.
- [x] Comprehensive documentation added in `docs/ab_testing_guide.md`.
- [x] 100% clean test pass (all 624 unit and integration tests pass cleanly) and ruff lint clean.

## Resolution

Implemented the complete A/B testing suite and operator guide for `holon-coherence` across Pull Request #20:

1. **Core Command & Evaluation Engine (`src/holon_coherence/commands/ab_test.py`, `src/holon_coherence/cli.py`)**:
   - Implemented `evaluate_runs` to perform turn-by-turn statistical comparison of authentic baseline vs optimized runs
     with authentic provider token usage, authentic TTFT delta, decode throughput, and semantic parity checking.
   - Implemented `run_workload_ab_test` to execute real agent command workloads twice through the proxy (Variant A
     passive baseline vs Variant B active optimization) with real traffic interception.
   - Implemented `run_live_replay_ab_test` to replay authentic request traces as live HTTP traffic through the running
     proxy with per-request header control (`X-Holon-Mode: baseline` vs `X-Holon-Mode: optimized`).
   - Implemented `evaluate_offline_ab_run` for offline differential evaluation through `JSONContextCleaner` strictly
     adhering to Rule 10 (Zero synthetic data for benchmarks).
   - Added `--fail-under-reduction` CI gating, `--rounds` statistical multiplier, and `--json` raw scorecard output.
2. **Dynamic Runtime Mode Control (`src/holon_coherence/mitm_addon.py`)**:
   - Added `/holon/api/mode` (GET/POST) endpoint allowing dynamic runtime switching of monitoring modes and log
     directories without requiring proxy container restarts.
   - Enhanced `is_flow_passive(flow)` to inspect `X-Holon-Mode` and `X-Holon-Passive` per-request headers.
3. **Container Sandbox Isolation & Health Reporting**:
   - Plumbed `--name` across all docker operations and isolated integration tests using `test-holon-coherence-sandbox`
     with exact regex filtering (`name=^{sandbox_container}$`) to protect running host proxies.
   - Updated `holon-coherence metrics` to display explicit down status (`🔴 PROXY STATUS: DOWN / UNREACHABLE`) and exit
     1 when the container is stopped.
4. **Testing, Linting & Verification**:
   - Added 30 unit and integration tests in `tests/test_ab_testing.py` covering directory ingestion, multi-round runs,
     semantic parity failures, and CLI options.
   - Full test suite passed (624 tests passed in 21.36s), `ruff check .` clean (0 errors), and all 7 GitHub CI checks
     green on PR #20.
   - 3-agent ensemble review passed unanimously with 3/3 `APPROVED` on PR #20.
   - Executed Stage 5 calibration (`holon calibrate`), pushed the `/calibrated` provenance branch, merged the
     calibration commit into the PR head execution branch, and pushed to origin.
   - PR #20 merged into `origin/main` (commit `61e6962`).
