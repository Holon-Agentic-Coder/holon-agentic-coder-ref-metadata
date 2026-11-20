---
# holon-agentic-coder-ref-metadata-0323
title: "A resolver turn that crashes records its findings as rejected, and a resume never adjudicates them"
status: completed
type: bug
priority: high
tags:
  - review-loop
  - resolver
  - ledger
  - holon-agentic-coder
created_at: 2026-11-17T15:00:00Z
updated_at: 2026-11-20T01:40:47Z
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

## Progress (2026-11-20)

- Flow `rescrash` started on `holon-agentic-coder` (claude-agent, claude-opus-5-5) in worktree
  `apps/holon-agentic-coder/flow-rescrash`; log `todo/flow-rescrash.log`.
- Stage 1 done: `I-1795130255-rescrash/_` (pushed). Stage 2 done:
  `I-1795130255-rescrash/P-1795130272-f4c1d312-claude-agent-claude-opus-5-5/_` (pushed), predicted EV 26.19.
- **Blocked at Stage 3 admission** (23:23 UTC): touch set overlaps the in-flight `shortref` flow
  (`I-1794976491-shortref/P-1795087811-3604f487-claude-agent-claude-fable-5/_`, worktree `flow-shortref`). The overlap
  comes from shortref's broad declared entries (`sandbox_executor/*.py`, `sandbox_executor/flow/`,
  `sandbox_executor/entrypoint/`, `tests/`, `docs/**/*.md`) covering this plan's `resolver_evidence.py`,
  `review_report.py`, `flow/review/{records,resolver,loop,adjudication,carried_findings}.py`, `flow/context.py`,
  `flow/calibrate_rerun.py`, `entrypoint/review_loop.py`, `flow_module_budgets.json`, four test files, and
  `docs/review_consensus.md`, `docs/ledger_schema.md`. Not overridden (no `--allow-overlap`).
- Resume after shortref merges:
  `python3 .agents/skills/holon_flow/scripts/run_holon_flow.py todo/intent-0323-rescrash.json --target-worktree apps/holon-agentic-coder/flow-rescrash --agent claude-agent --model claude-opus-5-5 --checkpoint apps/holon-agentic-coder/flow-rescrash/.holon/flow/checkpoint-rescrash.json`
  (the plan branch predates shortref's merge; check whether Stage 3 needs a re-plan on the new main).
- 2026-11-20: Re-planned on the new main (merged `origin/main` cac463b9 into `I-1795130255-rescrash/_`, resumed
  `--from-stage plan`). Plan `P-1795134970-CLA-CO5.5` (EV 21.70) widened its touch set after Stage 3 changed
  `flow/__init__.py`; final plan `P-1795136076-CLA-CO5.5` (EV 61.85), execution `E-1795136243-CLA-CO5.5`. Review 3/3
  APPROVED at iteration 3. Stage 5 first blocked on a macOS CI Timing Gate miss (345 s vs 181 s median) on the data-only
  calibration commit; runner variance, the job rerun passed in 4m49s and Stage 5 resumed green. PR #207
  (https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/207): calibration included, EV predicted 61.85 /
  actual 77.72 (+15.87), MERGEABLE/CLEAN, awaiting human merge. Logs `todo/flow-rescrash-replan-20261120.log`,
  `todo/flow-rescrash-calibrate-20261120.log`.

## Resolution

Delivered via [PR #207](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/207) and merged into `main`
(`d0b3e234`):

- **Key Architectural Deliverables**: a resolver turn that fails writes no `ACT-RES` rows and leaves its findings open;
  a rejection requires a resolver-supplied reason (`unspecified` or empty is refused); the checkpoint keeps a halted
  iteration's findings open and a review-stage resume sends them to the resolver before any new iteration; consensus
  approval is unreachable while an earlier finding has no disposition. Correction rows void the two false rows on PR
  #203, and the two carried nits (`_post_marked_comment` ordering, `review_calibration_freshness` store-back) are
  disposed of.
- **Verification & Tests**: the hermetic cases the Action asks for (resolver failure, resume adjudication, rejection
  without reason) are in PR #207's execution; see the PR for the test list.
- **Holon Flow Traversal**: all 5 stages completed. Review consensus 3/3 APPROVED at iteration 3. Calibration: EV
  predicted 61.85, actual 77.72 (+15.87). Stage 5 was first blocked by a macOS CI Timing Gate miss (runner variance); a
  rerun of that job passed and Stage 5 completed.
