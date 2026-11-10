---
# holon-agentic-coder-ref-metadata-0273
title: "Stage 4 declares consensus and posts an approving review while a reviewer's critical finding is open"
status: in-progress
type: bug
priority: critical
tags:
  - review-loop
  - stage-4
  - consensus
  - honesty
  - holon-agentic-coder
created_at: 2026-11-10T07:00:00Z
updated_at: 2026-11-10T07:00:00Z
---

## Problem

On PR #159 (Bean 0262), iteration 16, the container's own summary read `Ensemble: CHANGES_REQUESTED`, reviewer 3
`CHANGES_REQUESTED (critical 1)` and `Consensus: CHANGES_REQUESTED`. The host loop then logged "Consensus approval
reached at iteration 16" (`if ensemble_verdict is ConsensusVerdict.APPROVED` in `flow/review/loop.py`), posted a review
headed `APPROVED (3/3)` listing reviewer 3 as `APPROVED (critical 0, important 0, nit 0)`, halted for the human and ran
calibration. The same posted review's role table showed **Security: CHANGES**. 8 iterations of the cap were unused.

The same pattern appeared earlier: PR #147's first loop, and Bean 0254's iteration 4, reached "consensus" with a
reviewer still requesting changes on a nit.

**Likely cause (not confirmed):** the loop filters findings the resolver already adjudicated
(`_filter_adjudicated_findings`) before computing the ensemble verdict. The ledger shows the resolver rejected many
findings as "out of scope" (91 rejection rows, including `important` ones at iteration 5, one about the sibling-worktree
`commondir`), so a critical raised again was probably filtered out as already adjudicated and reviewer 3's verdict
flipped to APPROVED.

## Goal

1. **A critical, or any security-role, finding can never be filtered out as already adjudicated.** Adjudication
   suppression applies to nits only, and a finding whose severity is higher than when it was rejected is a new finding.
2. **The verdict is computed from what the reviewers returned**, and the posted review reports each reviewer's verdict
   and counts exactly as returned. If the filtered and raw verdicts differ, the loop does not declare consensus, logs
   both and continues to the resolver.
3. **No approval with any reviewer in CHANGES_REQUESTED at the head.** Add a test for the PR #159 shape: reviewers
   APPROVED, APPROVED, CHANGES_REQUESTED (critical 1) with a matching earlier `rejected: out of scope` row, expecting no
   consensus and no approving post.
4. **A resolver rejection of an `important` or higher finding requires an evidenced reason** (not "out of scope"), and a
   rejected important-or-higher finding is re-raised to the next ensemble as open, not as adjudicated.
5. **The flow-end notification** must not say a flow "ended cleanly, merge if ready": it names the verdicts of the last
   ensemble and warns when any reviewer's final verdict was not APPROVED.
6. `uv run pytest`, `uv run task lint` and `uv run task lint-docs` pass; no new dependencies.

## Notes

- Target repository changes in `holon-agentic-coder` must be delivered through the 5-stage Holon flow, and must not
  mention bean IDs or harness paths in the intent.
- Touches `flow/review/loop.py`, `flow/review/resolver.py` and `flow/review/records.py`; run it alone on the review
  loop.

## Progress (2026-11-10)

[PR #161](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/161) ran through the flow on
`claude-agent`/`claude-opus-5-5` (25 files, +2,253/−267). The loop hit the usage limit at iteration 3 (all three
reviewers died); a watcher resumed it from the checkpoint at 19:11 Melbourne. **Verified from the worktree ledger, not
the posted review**: iteration 6 is a genuine 3/3 APPROVED at head `eea0332` (iter 4: r3 CHANGES; iter 5: r1+r3 CHANGES;
fixes `c361127`, `eea0332`). Calibration (predicted EV 43.19, actual 72.12, ΔEV +28.93; Clean = Observed) merged into
the PR as `5f6a76f` with ledger-union conflict resolution; all three ledgers parse. Awaiting CI at the new head and the
maintainer's merge. After it merges: images rebuild, then restore PR #159's contents (revert of PR #160) and run the
review loop on them on the fixed engine (the agreed re-land path for Bean 0262).
