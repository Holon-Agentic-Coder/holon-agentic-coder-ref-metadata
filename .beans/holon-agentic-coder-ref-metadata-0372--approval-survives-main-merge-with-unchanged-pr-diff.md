---
# holon-agentic-coder-ref-metadata-0372
title: "An approval survives a merge of main that leaves the PR's own diff unchanged; only CI re-runs"
status: todo
type: feature
priority: critical
tags:
  - flow
  - stage-4
  - review-loop
  - merge-conflicts
  - cost
  - holon-agentic-coder
created_at: 2026-11-23T06:45:00Z
updated_at: 2026-11-23T06:45:00Z
---

## Problem

Stage 4 (the 3-reviewer ensemble) is the most expensive part of a flow, and it is re-run over and over for code that has
not changed. Every time any PR merges into `main`, every other open PR conflicts on the shared ledgers (see Bean 0371).
Merging `origin/main` in moves the head, and three rules then throw the approval away:

- `flow/review/conflict_gate.py` (engine): "Ledger-only conflicts are resolved without a test run ... and pushed; the
  approval must then be re-earned."
- `pr_review_loop` skill (principle 2) and `FLOW_PR_DRIVER.md`: "Votes count only at the current head. Any push ...
  invalidates earlier votes."
- Operator practice (#244 and #248 on 2026-11-23): a fresh 3/3 review after any merge of `main`.

PR #250 (merged 2026-11-23) already gates Stage 5 on CI of the merged head and withdraws the consensus only when that CI
fails. The review itself is still repeated, though, for merges that added nothing to the PR's own change.

## Goal

An approval is bound to the PR's own change, not to a commit SHA. When the head moves only by merges of the target
branch and bookkeeping commits, and the PR's own diff is identical, the approval and its votes carry over to the new
head; only CI must pass on the new head (the existing merged-head gate). A full re-review happens only when the PR's own
diff changed: a hand-resolved code conflict, a resolver or agent code push, or a failed CI on the merged head.

## Design

- **PR-own diff fingerprint.** `git diff <merge-base(head, origin/<target>)> <head>` excluding `holon-knowledge/**`
  (ledgers, KB) and Stage 5 calibration paths, reduced to a stable fingerprint (`git patch-id --stable` or a sorted
  per-file blob-hash list). Store it in the approval record and the approval stamp next to the head SHA.
- **Carry-over check.** Wherever an approval or vote is checked against the current head (conflict gate, review loop
  vote counting, Stage 5 merged-head gate, `approved_head_of` / `_same_commit`), "same head" becomes "same head, or same
  PR-own fingerprint". The carry-over is logged with both SHAs and the fingerprint, and recorded as one append-only
  ledger row; no earlier row is edited.
- **Conflict gate.** A target-branch merge whose conflicts were only ledger/KB (resolved mechanically) keeps the
  approval when the fingerprint matches; a code conflict still aborts and blocks as today.
- **CI is never skipped.** Carry-over never bypasses CI: the merged-head gate still waits for every check on the new
  head and still withdraws the consensus and restarts Stage 4 on a failure.
- **Calibration** evaluates the last code commit (consistent with Bean 0369) and needs no re-run when only a bookkeeping
  commit or a fingerprint-preserving merge followed it.

## Acceptance criteria

- A PR approved at head A, then merged with `origin/main` (clean or ledger-only conflicts) to head B with the same
  PR-own fingerprint: no reviewer is dispatched again; Stage 5 waits for CI on B and proceeds when it passes.
- Same setup but CI fails on B: the consensus is withdrawn and Stage 4 restarts (unchanged behaviour).
- A merge with a hand-resolved code conflict, or any push changing a non-`holon-knowledge` file of the PR's own diff,
  changes the fingerprint and requires a fresh review.
- Property test (Hypothesis): random PR changes plus 0-3 merges of a moving `main` with disjoint files; the fingerprint
  is invariant across those merges and changes whenever a PR-own file changes.
- The approval stamp names the head, the fingerprint and the CI result at that head.
- All tests pass via `uv run pytest`; `uv run task lint` and `uv run task lint-docs` pass.

## Harness changes (done with this bean, 2026-11-23)

`pr_review_loop` SKILL principle 2, `FLOW_PR_DRIVER.md` and the `resolve-conflict` skill now say that a push which is
only a merge of the target branch with mechanically resolved ledger/KB conflicts keeps the votes when the PR's own diff
is unchanged; only CI on the new head must pass.

## Delivery

Holon flow on `holon-agentic-coder`, intent `todo/intent-0372-approval-survives-main-merge.json`. Runs before Bean 0371,
since it removes most of the re-review cost immediately.
