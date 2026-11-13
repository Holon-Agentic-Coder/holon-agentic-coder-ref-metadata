---
# holon-agentic-coder-ref-metadata-0241
title: "Persist review loop sandbox across iterations to eliminate repeated clone and teardown overhead"
status: completed
type: feature
priority: high
tags:
  - flow
  - review-loop
  - stage-4
  - performance
  - sandbox
  - holon-agentic-coder
created_at: 2026-11-06T06:01:17Z
updated_at: 2026-11-08T23:49:31Z
---

## Problem

Following Bean 0228 (PR #124), the flow engine owns the Stage 4 review loop, dispatching containers with
`--max-iterations=1`.

Consequently, in multi-iteration review and resolution loops:

1. **Container Churn**: Every reviewer pass and every resolver pass launches a completely separate Docker container
   (`docker run ...`).
2. **Network Git Clone Overhead**: Inside each container, the review loop performs a full network `git clone` from
   GitHub:
   ```
   Cloning I-... into /home/holon/.holon-sandbox/workspace from https://github.com/Holon-Agentic-Coder/holon-agentic-coder.git...
   ```
3. **Repeated Teardown**: Upon completing iteration $N$, the container terminates and discards all cloned repository
   state, caches, and environment setup. The subsequent resolver pass or iteration $N+1$ reviewer pass must repeat the
   entire container startup, network clone, and environment initialization cycle.

This container churn introduces substantial latency (often several minutes per iteration spent solely on container
startup, network git clone, and git checkout) and burns excess compute resources.

## Goal

1. **Persistent Sandbox Session**: Enable the review loop sandbox to persist across iterations within Stage 4, or allow
   a single container run to execute the iterative convergence cycle without full teardown between iterations.
2. **Incremental Git Sync**: For subsequent iterations or resolution passes within the sandbox, fetch only new
   incremental commits (`git fetch origin <head_branch> && git checkout <head_branch>`) rather than re-cloning the
   entire repository from scratch over the network.
3. **Hermetic State Boundaries**: Ensure that while the sandbox repository checkout is reused and incrementally updated,
   ledger invariants and provenance records remain hermetic and accurate across iterations.
4. **Hermetic Unit & Integration Tests**: Verify that multi-iteration reviews operate cleanly within a single sandbox
   lifecycle without leaking uncommitted state between iterations.

## Resolution

Holon flow completed all 5 stages. Stages 1-3 and review iterations 1-3 ran on claude-agent / claude-fable-5; iterations
4-6 stepped down to claude-opus-5-5 after the Fable limit, where the resolver's pre-push tests failed deterministically
on iterations 5-6; a cross-runner switch to antigravity-agent / gemini-3.8-flash-medium converged on 3/3 consensus at
iteration 10 (posted once via the HTTP 422 fallback). Two ledger-only merges of `origin/main` (PRs #142, #144) were
interleaved by `created_at`. Stage 5 calibration (`plans/P-1794136106-claude-agent-claude-fable-5_calibration.md`, EV
47.66 predicted vs 66.63 actual, ΔEV +18.97) was merged into the PR head because `/calibrated` was cut from a stale
local head. All 11 CI checks passed and [PR #143](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/143)
merged into `main` (`a17a854`, 2026-11-08T23:49:31Z): the Stage 4 review loop sandbox now persists across reviewer and
resolver passes with incremental `git fetch` sync instead of a full clone and teardown per pass, covered by hermetic
no-leak integration tests.
