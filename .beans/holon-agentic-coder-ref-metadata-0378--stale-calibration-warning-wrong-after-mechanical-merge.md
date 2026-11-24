---
# holon-agentic-coder-ref-metadata-0378
title: "Stale-calibration warning fires on a mechanical merge of main and is not cleared when the fresh report lands"
status: completed
type: bug
priority: high
tags:
  - flow
  - stage-5
  - calibration
  - pr-comments
  - holon-agentic-coder
created_at: 2026-11-23T09:25:00Z
updated_at: 2026-11-23T14:57:40Z
---

## Problem

PR #258 (2026-11-23) carried this comment up to and after its merge:

> ⚠️ Calibration report is stale. The calibration report covers `aad504e` but the pull request head is `a4afb30` (2
> non-calibration commit(s) landed after the evaluated commit). Stage 5 must rerun; do not merge on this report.

Nothing but a ledger-only merge of `main`, review ledger rows and a regenerated calibration report had been added (the
PR's own diff patch-id was identical before and after the merge: `25983f3d…`). Timeline (UTC):

- 09:10:12 `a4afb308` merge of `origin/main` (ledger-only conflict, resolved mechanically);
- 09:18:09 the warning is posted by the rerun's Stage 5, naming the old report (`aad504e`) and head `a4afb30`;
- 09:18:13 `3d95f13b` review ledger rows (before Stage 5); 09:18:34 `2f0c0321` fresh calibration report (evaluated
  `3d95f13b`);
- the PR merged (maintainer's auto-merge) with the comment still saying "stale … do not merge".

Confirmed causes:

1. **A merge of the target counts as a head move.** `flow/calibrate_rerun.py::head_move_since_calibration` treats "any
   merge commit or non-calibration commit" after the evaluated SHA as a move. The two "non-calibration commits" were the
   merge commit and `main`'s own squash commit reachable through it. It does not use the PR-own diff fingerprint that PR
   #254 introduced for approvals, so a merge that changes nothing of the PR still marks the report stale. Review
   ledger-row commits (`chore(review): record review ledger rows`) are not discounted either (`is_calibration_commit`
   only knows Stage 5's own commits).
2. **The warning is posted by the same run that is about to regenerate the report**, 25 seconds before the fresh report
   is committed, so it is noise at best.
3. **The comment is not edited to "superseded" when the fresh report is pushed.** `flow/calibrate_stale_warning.py`
   promises one comment that is edited to superseded once a report covers the head; on PR #258 that edit had not
   happened when the PR merged (the flow was still in its final CI wait), so the last word on the PR was "do not merge".
4. **Nothing ties the warning to mergeability.** The text says "do not merge", but the PR was `MERGEABLE` and auto-merge
   merged it.

## Goal

- Staleness is judged on the PR's own change: a head that differs from the evaluated SHA only by merges of the target
  that leave the PR-own fingerprint unchanged, review/ledger-only commits and calibration commits is **not** stale.
- A run that is about to redo Stage 5 does not post the stale warning for the report it is replacing.
- When a fresh report covering the head is pushed, the existing warning is edited to superseded immediately (before the
  final CI wait), naming the new evaluated SHA; a flow resuming on an already-covered head clears a leftover warning.
- The comment's text matches what the flow will do: if the report is genuinely stale, the flow reruns Stage 5 itself
  (end-of-flow rule, Bean 0376) rather than telling a human not to merge.
- Tests: mechanical merge after calibration (no warning); code push after calibration (warning); warning then fresh
  report (edited to superseded before CI wait); Stage 5 rerun (no warning posted for the replaced report).

## Touch set

`apps/sandbox-executor/src/sandbox_executor/flow/calibrate_rerun.py`,
`apps/sandbox-executor/src/sandbox_executor/flow/calibrate_stale_warning.py`,
`apps/sandbox-executor/src/sandbox_executor/calibration_evaluated_sha.py`,
`apps/sandbox-executor/src/sandbox_executor/flow/review/approval_fingerprint.py` (reuse), their tests
(`tests/test_calibrate_rerun.py` and the stale-warning tests).

## Related

Bean 0362 / PR #247 (the warning never cleared: first fix), Bean 0372 / PR #254 (PR-own fingerprint), Bean 0369 / PR
#253 (evaluated SHA), Bean 0376 (end-of-flow rerun; also where "the flow stops when its PR is merged" is recorded).

## Progress

- 2026-11-23: PR #263 (`I-1795432203-stale-calibration-warning-fix/P-1795432220-CLA-CF5.2/E-1795433754-CLA-CF5.2/_`,
  head `f61ce141`) completed all 5 stages via `cf3b215e-a4cb-41c3-968e-578b183a495f` (`3/3` consensus approved, Stage 5
  calibration included, `11/11` CI checks passed, `MERGEABLE` + `CLEAN`), awaiting human merge.

## Resolution

- Delivered via [PR #263](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/263) and merged into `main` (`e563254e`).
- Key deliverables: PR-own diff fingerprint for staleness checks (`calibrate_rerun.py`), suppressing stale warnings when Stage 5 is regenerating, editing any existing warning comment to superseded before the final CI wait (`calibrate_stale_warning.py`), and hermetic tests.
- Verification & Holon Flow traversal: 3/3 consensus approval, 11/11 CI checks green on calibrated head `84c7bb58`, Stage 5 calibration included.
