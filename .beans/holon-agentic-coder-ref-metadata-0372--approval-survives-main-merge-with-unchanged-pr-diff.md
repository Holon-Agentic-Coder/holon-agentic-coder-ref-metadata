---
# holon-agentic-coder-ref-metadata-0372
title: "An approval survives a merge of main that leaves the PR's own diff unchanged; only CI re-runs"
status: completed
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
updated_at: 2026-11-23T09:12:00Z
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

## Progress note (holon flow, 2026-11-23)

- PR #254 (`I-1795416692-approval-survives-main-merge`) is terminal: MERGEABLE/CLEAN on head a1d985dd, all checks green,
  calibration report `plans/I-1795416692-approval-survives-main-merge/P-1795418641-CLA-CO5.5_calibration.md` in the PR
  diff. Awaiting human merge into main.
- Stages: intent ok, plan ok, execute ok, review completed after 7 iterations (3/3 approval at iteration 4; later rounds
  re-earned after each target-branch merge), calibrate completed.
- Stopped and resumed several times: review halt on a nit with no resolver pass; conflict gate re-earned the approval
  after merging main (the bean's carry-over was not yet in effect for mechanical ledger merges); Stage 5 blocked once by
  the macOS CI Timing Gate (674 s job vs 600 s ceiling, slowdown spread across unrelated tests, not a test failure),
  cleared on rerun.
- Conflicts with main resolved mechanically via `resolve-conflict` subagents (ledger rows only) on each target-branch
  advance (#251-#256).
- Log: todo/flow-approval-survives-main-merge.log (the runner's own output was largely buffered there).

## Resolution

Delivered via [PR #254](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/254) and merged into `main`
(`84b70c1`), subject "feat(approval): Stage 4 review is the most expensive part of a flow and is repeated for code
that... (#254)":

- **Key Architectural Deliverables**: the PR-own diff fingerprint (merge-base to head, `holon-knowledge/**` and Stage 5
  calibration paths excluded) is stored in the approval record and approval stamp beside the head SHA; the conflict
  gate, review-loop vote counting and the Stage 5 merged-head gate accept an approval at a new head when the fingerprint
  is unchanged; carry-overs are logged with both SHAs as one append-only ledger row. CI on the new head is never
  skipped.
- **Verification & Tests**: PR #254 checks green at head a1d985dd before the merge (per the progress note above).
- **Holon Flow Traversal**: all 5 stages completed (intent, plan, execute, review loop, calibration) after several
  resumes; the review loop reached 3/3 approval at iteration 4, with later rounds re-earned after each target-branch
  merge.
- **Post-merge cleanup**: flow worktree `flow-approval-survives-main-merge` and all
  `I-1795416692-approval-survives-main-merge` branches deleted locally and on origin; no earlier attempts existed.
  Bundle backup: `todo/stale-worktree-backups/approval-survives-main-merge-2026-11-23.bundle` (verified).
