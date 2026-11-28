---
# holon-agentic-coder-ref-metadata-0613
title: "Review loop prints zero non-defect churn and hides Reviewer 2 and 3 verdicts in flow logs"
status: todo
type: bug
priority: normal
tags:
  - review-loop
  - observability
  - holon-agentic-coder
created_at: 2026-11-27T05:18:43Z
updated_at: 2026-11-27T07:50:33Z
---

## Notes

### Evidence (2026-11-27T04:43Z–05:18Z fifth-merge audit)

- **Non-defect churn mismatch:** Calibration reports for `PR #374` (`review-findings-all-actioned`) and `PR #375`
  (`self-explaining-gate-pre-push`) both record `Non-defect churn (target merge): 2`, yet their Stage 4 `[Review Loop]`
  terminal summaries in `todo/flow-*.log` printed `Non-defect churn: target merge 0, bookkeeping 0, CI noise 0` (every
  one of the 14 merged flows in the window printed `0, 0, 0`).
- **Missing Reviewer 2/3 verdicts in flow log:** In `todo/flow-self-doc-tests-46.log` (`04:31:07Z` and `05:12:59Z`), the
  log prints only: `[Review Loop] Reviewer 1: claude-agent / claude-opus-5-5: APPROVED (critical 0, important 0, nit 0)`
  followed immediately by:
  `Stage 4 failed: Autonomous review blocked: consensus withheld by reviewer container reported ensemble verdict CHANGES_REQUESTED`
  Reviewer 2 and Reviewer 3 verdicts are omitted from the flow log whenever the container ensemble returns
  `CHANGES_REQUESTED`, making diagnosis from flow logs blind.

### Proposed Change

- Wire the actual `target_merge`, `bookkeeping`, and `ci_noise` counts into `review_accounting.py`'s `[Review Loop]`
  terminal summary so flow logs match calibration reports.
- Log all ensemble reviewer verdicts (`Reviewer 1..N` with critical/important/nit counts) on every iteration, including
  `CHANGES_REQUESTED` and container-verdict runs.

### Expected Gain & Cost

- Eliminates blind spots in Stage 4 flow logs and ensures review churn accounting matches calibration reports without
  querying GitHub or container artefacts.
- Cost: minor logging and accounting fix in `flow/review/` with unit tests.

### Audit evidence (2026-11-27T07:49Z fifth-merge audit)

- On `#408` (`self-doc-tests-49`, `06:00:28Z`), `#403` (`tests-46`), `#406` (`tests-48`), `#407` (`tests-51`), and
  `#409` (`tests-45`) Iter 3–4 (`05:25Z`–`05:40Z`), Stage 4 logs printed `APPROVED (0/0/0)` for all 3 reviewers followed
  immediately by `Consensus blocked ...: reviewer container reported ensemble verdict CHANGES_REQUESTED` when `FIND-CI`
  (`hygiene`) blocked consensus, without naming the CI blocker in the verdict line.
- `todo/flow-self-doc-tests-51.log` (`05:59:16Z`) still printed
  `Non-defect churn: target merge 0, bookkeeping 0, CI noise 0` despite target-sync merges (`a572af8d`, `3ee72bf9`).

## Resolution
