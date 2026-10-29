---
# holon-agentic-coder-ref-metadata-0163
title: "CI timing regression gate: fail any build whose duration regresses beyond a tolerance"
status: completed
type: feature
priority: high
tags:
  - ci
  - performance
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-10-26T10:04:41Z
updated_at: 2026-10-29T12:00:00Z
---

## Problem

Nothing stops a change that makes tests or builds slower from reaching `main`. On 2026-10-26 the maintainer saw the
holon-agentic-coder `unit (macos-latest)` job pass the 10-minute mark while PR #97 was under review. Slow pipelines cost
every later PR, every review-loop iteration (each push waits for CI) and every flow run.

### Evidence (2026-10-26, holon-agentic-coder `unit (macos-latest)`, pytest time only)

| Head                                         | Tests | pytest time |
| -------------------------------------------- | ----- | ----------- |
| `e3bbd67` (`main`, before #97)               | 2167  | 662 s       |
| `ca22157`                                    | 2218  | 643 s       |
| `a66ad46` (only a doc change from `ca22157`) | 2218  | 544 s       |
| `78423a2`                                    | 2220  | 776 s       |
| `10cd32e`                                    | 2230  | 523 s       |
| `c9bc826`                                    | 2241  | 697 s       |
| `a755bf5`                                    | 2265  | 526 s       |
| `c479dd4`                                    | 2271  | 681 s       |

`main` was already over 10 minutes before #97. The same code varies by about ±20% between runs on hosted macOS runners,
so wall-clock time alone is a noisy signal.

## Scope

Add a timing gate to every CI build in both target repositories (`holon-agentic-coder` and `holon-coherence`): unit,
integration, stress, hygiene, image builds (Buildx Bake) and any other job.

1. **Record:** each job on `main` records its duration, plus pytest's per-test durations (`--durations=0` or a JUnit XML
   report) for test jobs. Store them as a CI artefact or cache keyed by job and runner OS, never in the repository and
   never as a fourth ledger.
2. **Compare:** each PR job compares against a baseline from recent `main` runs of the same job and OS. Use a rolling
   median of the last N runs (N configurable, for example 5), not only the previous run, because a single previous run
   would fail healthy builds given the measured variance.
3. **Fail:** fail the job when its duration exceeds the baseline by more than a configurable tolerance. The maintainer
   suggested 10% of the previous run as the example. Calibrate the default against real data (AGENTS.md item 10) so it
   catches real regressions without flaking on runner noise. Options: a per-OS tolerance, a minimum absolute delta, or
   comparing the sum of per-test times (which is much less noisy than wall clock).
4. **Explain:** test jobs also flag individual tests whose duration grew past a per-test tolerance and name the top
   offenders in the failure, so the author can see what got slower.
5. **Absolute ceiling:** also fail any job over a hard ceiling (for example 10 minutes for unit), whatever the baseline.
6. **Override:** an explicit, auditable opt-out for deliberate slow-downs (a PR label or a committed baseline bump with
   a reason), so the gate can't be bypassed silently.
7. Document the gate, the tolerance, how to read the report and how to bump the baseline.

## Notes

- Run through the Holon flow, one flow per target repository. It changes CI workflows only, so it can run in parallel
  with flows that don't touch `.github/workflows/`.
- Bring the macOS unit job back under 10 minutes first, or set the initial ceiling from today's `main`. Otherwise the
  gate fails every build on arrival.
- Related: Bean 0154 (the flaky fuzz test turns CI red), Bean 0160 (the review loop waits on CI), Bean 0152 (smaller
  modules and faster tests).

## Progress (2026-10-29)

- **`holon-agentic-coder` half — COMPLETED & MERGED (PR #109):**
  - Flow: `I-1793246551-ci-timing-regression-gate` → `P-1793246567-claude-agent-claude-opus-5-5` →
    `E-1793246853-claude-agent-claude-opus-5-5`.
  - PR #109 (https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/109): converged in 5 review-loop iterations
    (3/3 ensemble approval at `74113db`, review `5693019917`, 10/10 CI green), Stage 5 calibrated (`147ea4f`, EV 41.40
    predicted / 67.00 actual, Prettier-formatted in `cd2ab9b`), ledger conflicts resolved in `0b9e858`, and merged by
    the maintainer as `993b686` (2026-10-29T05:57:21Z).
- **`holon-coherence` half — MERGED (PR #30):**
  - Flow: `I-1793246826-coherence-ci-timing-regression-gate` → `P-1793246842-claude-agent-claude-opus-5-5` →
    `E-1793247065-claude-agent-claude-opus-5-5`.
  - PR #30 (https://github.com/Holon-Agentic-Coder/holon-coherence/pull/30): calibration report included (`6dea412`),
    merged by the maintainer as `6d9dae7` (2026-10-29T11:40:26Z) while the harness review loop was paused at
    iteration 5. The only posted review is holon's native Stage 4 report (5694137530, `FAILED`). The open Important
    finding (label query needs `issues: read`) and two Nits are carried by Bean 0184.
