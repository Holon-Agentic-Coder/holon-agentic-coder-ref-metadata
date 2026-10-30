---
# holon-agentic-coder-ref-metadata-0179
title: "Route Stage 4 reviewer turns through the review-loop role container so holon flow can review on its own"
status: completed
type: feature
priority: high
tags:
  - review-loop
  - holon-flow
  - sandbox
  - holon-agentic-coder
blocked_by:
  - holon-agentic-coder-ref-metadata-0144
created_at: 2026-10-28T22:05:13Z
updated_at: 2026-10-30T21:05:00Z
---

## Problem

Bean 0144's third flow (PR #102) wired the real reviewer ensemble into `run_review_loop()` and removed the fabricated
consensus report. Its routing probe found that the `review-loop` role container clones rather than mounts the workspace,
and the ledger rows it records never reach the host. So it took the pre-registered fail-closed fallback: host-side
`holon flow` Stage 4 refuses to run reviewer agent turns outside a sandbox and fails with a clear error.

That is safe (no fabricated approval, no host agent), but `holon flow` still cannot complete Stage 4 by itself. Every
flow PR still needs the harness `pr-review-loop` skill for review, so the native five-stage flow is not yet
self-sufficient.

## Goal

Through the Holon flow on `holon-agentic-coder`, after PR #102 merges (it merged as `f09ca5e`, 2026-10-28T23:08:50Z):

1. Dispatch Stage 4 reviewer work through the existing `_dispatch_role()` into the `review-loop` role container, which
   runs `run_ensemble()` / `decide_consensus()` on the PR's real diff inside the sandbox.
2. Return the review outcome (per-reviewer results, findings, consensus) to the host without trusting anything the
   reviewers themselves wrote: for example a structured result file the entrypoint writes and the host reads back, or
   the pushed ledger rows on the PR branch. Decide the transport in the plan; keep all three ledgers append-only.
3. Host-side Stage 4 keeps mergeability, CI and posting; posting only from real completed reviewer results.
4. Remove the host-side refusal once routing works; keep it as the failure path if the container cannot run.
5. Tests with fakes at the dispatcher and container seams; an end-to-end dry run of `holon flow` reaching a real
   consensus decision.
6. Then retire the "Stage 4 runs through the harness `pr-review-loop` skill" workaround in the harness docs.

## Resolution

Completed through the Holon flow on `holon-agentic-coder`:

- Intent: `I-1793339088-route-stage-4-reviewer-turns-through-the-review-loop-role-container`
- Pull Request: [#116](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/116)
- Review: 3/3 unanimous approval with zero findings.
- Calibration: Stage 5 completed and merged into PR head (`4f119cd`, EV predicted 68.62, actual 78.04, $\Delta\text{EV}
  = +9.42$).
- Merged into `main` at commit `b746408565c1f71d29bc9411b03a0f17e8759d41`.

## Notes

- Related: Bean 0144 (flows 1-3, PRs #100, #101, #102), Bean 0170 (review-loop convergence: adopt its increment-only
  rules in the native loop), Bean 0161 (decomposed-child integration).
