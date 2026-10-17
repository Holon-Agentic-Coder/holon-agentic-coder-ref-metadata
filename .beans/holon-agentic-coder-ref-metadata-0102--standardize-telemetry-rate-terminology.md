---
# holon-agentic-coder-ref-metadata-0102
title: "Standardize telemetry rate terminology consistently on throughput across CLI and dashboard"
status: completed
type: task
priority: normal
tags:
  - coherence
  - telemetry
  - metrics
  - cli
  - dashboard
created_at: 2026-10-17T00:37:00Z
updated_at: 2026-10-17T01:30:00Z
---

## Summary

Consolidate rate terminology in `holon-coherence` uniformly on **Throughput** across the terminal scorecard, web
dashboard, JSON API contracts, wire logs, and documentation:

1. **Current Inconsistency**:
   - Terminal scorecard and dashboard mix terms: `Prompt (Prefill) Speed`, `Tail Prefill Speed`, and
     `Decode Throughput`.
   - In modern LLM inference systems (vLLM, SGLang, MLPerf), token generation and processing rates are uniformly termed
     **Throughput** (tokens/sec), while latency is measured in seconds/milliseconds (TTFT, ITL).

2. **Standardized Vocabulary**:
   - `Prefill Throughput` (tokens/sec) — formerly `Prompt (Prefill) Speed`
   - `Tail Prefill Throughput` (tokens/sec) — formerly `Tail Prefill Speed`
   - `Decode Throughput` (tokens/sec) — unchanged

3. **Scope of Updates**:
   - Update `src/holon_coherence/commands/metrics.py` terminal display labels.
   - Update web dashboard labels in `src/holon_coherence/mitm_addon.py` HTML template.
   - Update `src/holon_coherence/metrics_math.py` docstrings and function aliases (preserving backward-compatible helper
     names).
   - Update A/B test scorecard output in `src/holon_coherence/commands/ab_test.py`.
   - Update test assertions in `tests/test_cli.py`, `tests/test_ab_testing.py`.
   - Update operator guides in `docs/ab_testing_guide.md` and `README.md`.

## Target Repository & Files

- Repository: `holon-coherence` (`apps/holon-coherence/`)
- Target Files:
  - `src/holon_coherence/commands/metrics.py`
  - `src/holon_coherence/commands/ab_test.py`
  - `src/holon_coherence/mitm_addon.py`
  - `src/holon_coherence/metrics_math.py`
  - `tests/test_cli.py`
  - `tests/test_ab_testing.py`
  - `docs/ab_testing_guide.md`

## Acceptance Criteria

- [x] All three token processing rate metrics use consistent `Throughput` terminology (`Prefill Throughput`,
      `Tail Prefill Throughput`, `Decode Throughput`).
- [x] Terminal scorecard (`holon-coherence metrics`), web dashboard (`/holon/`), and JSON exports display the unified
      terminology.
- [x] Existing JSON metrics keys remain backward-compatible or include clear alias mapping.
- [x] 100% of unit and integration tests pass with 0 errors.

## Notes

- Directly addresses user feedback requesting unified terminology instead of mixing speed and throughput across metrics.

## Resolution

Implemented via the 5-stage Holon flow:

1. **Flow Branches**:
   - Intent branch: `I-1792158378-active-opt-dedup-and-throughput-terminology/_`
   - Plan branch:
     `I-1792158378-active-opt-dedup-and-throughput-terminology/P-1792158378-antigravity-agent-gemini-3.8-flash-medium/_`
   - Execution branch:
     `I-1792158378-active-opt-dedup-and-throughput-terminology/P-1792158378-antigravity-agent-gemini-3.8-flash-medium/E-1792158381-antigravity-agent-gemini-3.8-flash-medium/_`
   - Calibrated branch:
     `I-1792158378-active-opt-dedup-and-throughput-terminology/P-1792158378-antigravity-agent-gemini-3.8-flash-medium/E-1792158381-antigravity-agent-gemini-3.8-flash-medium/calibrated`
2. **Pull Request**:
   - [Holon-Agentic-Coder/holon-coherence#22](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/22)
3. **Review & Calibration**:
   - Unanimously approved by 3-agent ensemble review (`pr-reviewer` skill).
   - Calibrated via `holon calibrate` with calibration report merged into PR head branch ($\Delta EV$ -72.24).
   - All 630 tests passed; GitHub Actions CI 7/7 passed cleanly.
   - Merged into `origin/main` (commit `ded9f80`) on 2026-10-17.
