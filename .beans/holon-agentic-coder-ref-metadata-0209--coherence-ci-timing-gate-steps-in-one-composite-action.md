---
# holon-agentic-coder-ref-metadata-0209
title: "holon-coherence: move the pasted CI timing-gate steps into one composite action"
status: todo
type: task
priority: low
tags:
  - ci
  - duplication
  - holon-coherence
blocked_by:
  - holon-agentic-coder-ref-metadata-0184
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-30T00:48:53Z
---

## Problem

Spawned by Bean 0177. On `68fdf67` each of the 5 workflows under `.github/workflows/` carries its own copy of the CI
timing-gate steps (two `ci_timing_gate` references per file). PRs #24, #25 and #30 each touched all 5 workflow files
plus the README, so any two CI changes conflict.

## Scope

1. `.github/actions/ci-timing-gate/action.yml` with inputs; each workflow calls it in one step.
2. Gate behaviour unchanged; `tests/test_ci_timing_gate.py` and `tests/test_makefile.py` green.

## Touch set

`.github/workflows/*.yml`, `.github/actions/`, `.github/workflows/README.md`.

## Dependencies

Blocked by 0184 (residual gate findings edit the same steps). Same shape as 0202 on holon-agentic-coder.

- 2026-10-30: satisfied. Bean 0184 is completed (holon-coherence PR #32, merged as `cefebe3`), so the gate steps are
  stable.

## Notes

- Run through the Holon flow on holon-coherence. Needs a token with the `workflow` scope (Bean 0175).
