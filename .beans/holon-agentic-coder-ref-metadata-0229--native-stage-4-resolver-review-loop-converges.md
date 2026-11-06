---
# holon-agentic-coder-ref-metadata-0229
title: "Native Stage 4 resolver: the review loop resolves findings and converges, it does not just review once"
status: completed
type: feature
priority: high
tags:
  - flow
  - review-loop
  - stage-4
  - resolver
  - holon-agentic-coder
created_at: 2026-11-05T00:50:00Z
updated_at: 2026-11-05T15:40:00Z
---

## Problem

The flow engine's Stage 4 halts at the first CHANGES_REQUESTED verdict: "no automatic resolver; findings stop the
stage". The 25-iteration loop machinery is therefore dead code — nothing inside the flow ever changes the head between
passes, so iteration 2 can only happen via a manual resume after external resolution. Maintainer ruling (2026-11-05,
during the manual end-to-end flow run): "we have to put the resolve into the review loop as well or else the review loop
is useless. It's a loop not a reviewer."

## Decision

Stage 4 is review AND resolve, iterating to convergence inside the flow. Per engine iteration: ensemble pass; on
findings, dispatch a resolver pass that adjudicates EVERY finding (nits included) to exactly one disposition — `applied`
(fixed, committed to the execution branch, pushed) or `rejected` (with a one-line reason: not diff-grounded, inaccurate,
out of scope, or conflicting with a higher-severity finding) — then the next engine iteration reviews the new head.
Exits: consensus approval (posted, stage succeeds), or the engine's iteration/time budgets (stage fails with everything
recorded). No human pause mid-loop.

## Scope

1. A resolver role container (same dispatch machinery as the reviewer), fresh clone of the execution branch, given the
   iteration's findings (ids, severities, file:line, recommendations) from the engine's result file; it applies or
   rejects each one, runs the repo's lint and test tasks, commits with the finding ids in the message, and pushes.
2. Ledger: populate the existing `review_disposition`, `rejection_reason`, `review_finding_ids` and
   `introduced_by_action_id` fields on the resolver's action entries in `executions.jsonl`; rejected findings carry
   their reason and are handed to the next iteration's reviewers as already adjudicated so they are not re-raised.
3. Convergence guards: a finding set that survives unchanged across 3 consecutive iterations with no diff change is
   adjudicated `rejected: no-convergence` and reported rather than spun on; any push invalidates earlier votes — a new
   head is always re-reviewed in full.
4. Posting: the consensus is posted only at an exit (approval, or budget exhaustion with the final state), never per
   intermediate iteration.
5. Tests (pytest only; no real Docker, gh, git remotes or LLM calls): review-with-findings dispatches the resolver;
   every finding ends with a disposition; rejected findings are not re-raised; the 3-iteration no-convergence guard;
   approval exits post exactly once; budget exhaustion records open findings.

## Notes

- Run through the Holon flow on holon-agentic-coder.
- Depends on 0228 (engine-owned single loop; the resolver is a step inside the engine's iteration, the container stays
  single-shot). Mirrors the harness pr-review-loop doctrine: Nits are actioned, not waved through; the loop never pauses
  for guidance mid-flight; merging stays human-only.

## Completed (2026-11-06)

Delivered via the Holon flow on `antigravity-agent` / `gemini-4-argon`: intent
`I-1793869839-stage-4-resolver-review-loop-converges`, plan `P-1793869856-antigravity-agent-gemini-4-argon`, PR #125,
merged as `baf3f8c`. Native Stage 3 implemented the in-container resolver loop (`bd320bb`). Stage 4 review iteration 1
halted at findings (expected during bootstrap — native resolver feature in-flight on the PR itself); the harness
`pr-review-loop` converged in 3 iterations (resolver commits `8b3cf3a`, `6f0a7c0`, and `342dfc1`), adding hermetic unit
test coverage for the resolver dispatch, disposition logging, 3-iteration `no-convergence` guard, and single exit
posting, with 2971 unit tests passing. Unanimous 3/3 consensus `APPROVED` achieved at `342dfc1` and posted to PR #125.
Stage 5 calibrated (`eb3302f`, EV predicted 64.91 vs actual -8.92, ΔEV -73.83), `/calibrated` branch pushed to origin,
and calibration report (`plans/P-1793869856-antigravity-agent-gemini-4-argon_calibration.md`) merged into the PR head.
