---
# holon-agentic-coder-ref-metadata-0447
title: "Run Workspace survival via one shared child unit pass or separate CI jobs"
status: todo
type: task
priority: normal
tags:
  - ci
  - pipeline
  - stress
  - performance
  - holon-agentic-coder
created_at: 2026-11-25T04:02:00Z
updated_at: 2026-11-25T04:02:00Z
---

## Problem

Running both `Workspace survival` stress tests concurrently inside the same 4-vCPU `ubuntu-latest` GitHub Actions job
(`.github/workflows/test-stress.yml`) saturates CPU instead of speeding up the pipeline: each `-n auto` child unit run
slows from `~180 s` (serial) to `~334 s` (concurrent), leaving the job at `364 s` (`399 s` total workflow run) vs
`365.5 s` `main` baseline.

## Evidence (`2026-11-25T02:54Z–03:54:45Z` fifth-merge audit)

- On `holon-agentic-coder#308` (`workspace-survival-job-parallel`, run `45540005200` on `24d23329`), `Test - Stress`
  took `399 s` (`364 s` stress step) against a `365.5 s` `main` baseline.
- Reviewer 3 raised `R3-F1` (`important`) noting zero net CI wall-clock improvement; the Stage 4 resolver left `R3-F1`
  `open` because per-module `--durations` across 276 modules showed no single dominant module (max 7%) and concurrent
  child runs are 4-vCPU bound, requiring a design decision.
- Across the window, `Test - Stress` ran in `314–478 s` (`5.2–8.0 min`), setting or co-setting the critical path on
  every full CI wait alongside `unit (macos-latest)` (`368–588 s`).

## Proposed change

Choose one of two designs in a focused follow-up flow:

1. **One shared child unit pass:** execute the unit selection once under an isolated executor workspace + simulated
   container `HOME`, verify both the workspace/git/`HEAD` survival guarantee and the `HOME` hermeticity guard from that
   single run, and keep both negative controls (`head-moved` failure and deliberately non-hermetic canary trip).
2. **Two separate CI jobs:** split `test_workspace_survival_stress` and `test_sandbox_hermetic_guard` into two parallel
   jobs in `.github/workflows/test-stress.yml` so each gets its own 4-vCPU runner (`~180 s` each).

## Expected gain

Cuts `Workspace survival` CI duration from `365–478 s` (`6.1–8.0 min`) to `~180–210 s` (`3.0–3.5 min`), saving
`~3–4 min` per full CI wait (`~6–8 min` per flow).

## Cost

Small: follow-up adjustment to `.github/workflows/test-stress.yml` and `apps/sandbox-executor/tests/stress_support.py`,
delivered via the Holon flow (`holon-agentic-coder`).

## Notes

- Target repo change through the Holon flow (`holon-agentic-coder`) after `PR #308` merges.
- Related: Bean `0405` (`workspace-survival-job-parallel`, slice 2), Bean `0400` (shorten the CI pipeline).
