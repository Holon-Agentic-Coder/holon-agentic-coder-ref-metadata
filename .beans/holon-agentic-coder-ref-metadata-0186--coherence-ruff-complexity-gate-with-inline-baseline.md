---
# holon-agentic-coder-ref-metadata-0186
title: "holon-coherence: adopt ruff complexity rules (C901, PLR0911-PLR0915) with an inline noqa baseline"
status: completed
type: task
priority: high
tags:
  - code-quality
  - lint
  - complexity
  - holon-coherence
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-30T03:10:00Z
---

## Problem

Spawned by Bean 0177. On holon-coherence `origin/main` `68fdf67` (`src/`, 9,211 lines, 209 functions) ruff selects no
complexity rule. Measured: C901 **38** functions; PLR0912 32, PLR0915 20, PLR0913 4, PLR0911 4; radon average CC B
(8.7), 7 functions graded F (`parsers/sse.extract_sse_token_counts` 85, `commands/ab_test.evaluate_runs` 69,
`MitmproxyAddon.request` 65, `translate_gemini_to_openai_request` 45).

## Scope

Same rules and mechanism as Bean 0185: C901 at 10 and PLR0911/0912/0913/0915 at ruff defaults, an inline `noqa` baseline
via `ruff check --add-noqa` (never `per-file-ignores`), a ratchet pytest that fails if the baseline count rises, and one
short thresholds section in the docs.

## Touch set

`pyproject.toml`, `def` lines of the 38+ offenders in `src/holon_coherence/`, one new test, one docs section.

## Dependencies

None. Must land before 0203, 0204, 0207 and 0208.

## Notes

- Run through the Holon flow on holon-coherence.
- pytest only; no harness paths or bean ids in the target.

## Completion Summary

- Traversing the complete 5-stage Holon flow:
  1. Intent: `I-1793325100-coherence-ruff-complexity-gate-with-inline-baseline/_`
  2. Plan: `P-1793325355-antigravity-agent-gemini-3.8-flash-medium`
  3. Execution: `E-1793325932-antigravity-agent-gemini-3.8-flash-medium`
  4. Review Loop: PR #35 raised; iterative reviews converged to 3/3 unanimous approval across 7/7 CI checks.
  5. Calibration: Calibrated branch `.../calibrated` and fast-forwarded into PR head with ΔEV +0.45.
- Merged to `main` via PR #35 (`f7e4aa6`).
