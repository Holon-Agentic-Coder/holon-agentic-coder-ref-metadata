---
# holon-agentic-coder-ref-metadata-0323
title: "A resolver turn that crashes records its findings as rejected, and a resume never adjudicates them"
status: todo
type: bug
priority: high
tags:
  - review-loop
  - resolver
  - ledger
  - holon-agentic-coder
created_at: 2026-11-17T15:00:00Z
updated_at: 2026-11-17T15:00:00Z
---

## Problem

Seen on holon-agentic-coder PR #203 (Bean 0297), 2026-11-17. Review iteration 3 ended with Reviewer 1 requesting changes
on two nits (`FIND-R1-003-01` and `FIND-R1-003-02`, both in `flow/calibrate_rerun.py`). The resolver was dispatched at
13:08:21 UTC and exited with code 1 eight seconds later on `You've hit your session limit`. Two things then went wrong:

1. **False ledger rows.** At 13:08:29 UTC the loop appended `ACT-RES-1794920909-f4cc16ac` and
   `ACT-RES-1794920909-d214a869` to `executions.jsonl`: both findings "adjudicated: rejected", `outcome: success`,
   `rejection_reason: unspecified`. No resolver looked at either finding. A crash is recorded as a decision.
2. **The resume skips them.** The flow was resumed with `--from-stage review` after the limit reset. It ran no resolver
   for the open findings; it started iteration 4 on the unchanged head, a fresh ensemble returned 3/3 APPROVED with no
   findings, and the flow went on to Stage 5. The two nits were neither applied nor rejected with a reason, and the code
   they point at is unchanged.

So a usage limit at the wrong moment waves findings through, against the rule that every finding, nits included, is
applied or rejected with a stated reason.

## Action

Run through the Holon flow on `holon-agentic-coder`:

- A resolver turn that fails (non-zero exit, usage limit, timeout) writes no adjudication rows. A rejection row requires
  a reason supplied by the resolver; `unspecified` is not accepted.
- The checkpoint keeps the findings of a halted iteration as open, and a resume of the review stage sends them to the
  resolver before any new review iteration. Approval is not reachable while a finding from an earlier iteration has no
  disposition.
- Hermetic tests: a resolver that exits 1 leaves the findings open and writes no `ACT-RES` row; a resume adjudicates
  them first; a rejection without a reason fails.
- Append correction rows for the two false rows on PR #203 (see Bean 0146 for the correction-row mechanism).
- PR #203 (Bean 0297) merged on 2026-11-18 with its two iteration-3 nits still open, so this flow must also apply or
  reject-with-reason both carried nits: (1) `flow/calibrate_rerun.py` `_post_marked_comment` resolves
  `approval_pr_number(context)` before its try block, although it is documented as never raising; (2)
  `review_calibration_freshness` must store the refreshed StageResult back into `context.stage_results['calibrate']`, so
  a gate-driven rerun's report-back and checkpoint name the final head, not the superseded one.

## Notes

- Related: Bean 0297 (the affected PR), Bean 0146 (correction rows).
- Touches the review loop (`entrypoint/review_loop.py`, `flow/review/`); sequence it in the review-loop lane.
