---
# holon-agentic-coder-ref-metadata-0499
title: "Calibration report records, per flow, CI runs, review iterations and how many were churn"
status: todo
type: task
priority: normal
tags:
  - flow
  - stage-5
  - calibration
  - measurement
created_at: 2026-11-26T08:55:00Z
updated_at: 2026-11-26T08:55:00Z
---

## Evidence

Self-improvement audit 2026-11-26. The audit rules require, per flow, the number of pipeline runs and review iterations
needed to reach both passes, and how many were caused by churn rather than a defect. No flow records it. This audit had
to rebuild it from `gh run list` and the flow logs: PR #317 100 runs and 12 iterations, #320 66 runs and 2 approvals,
#321 66 and 2, #323 31 and 1, #319 42 and 1, #314 30 and 1. The distinction between churn and defect (ledger-only push,
main moved, unfixable-by-code finding, nit-only iteration) is visible to the engine at the time and lost afterwards.
Related: 0412 (step timing), 0443 (cancelled runs), 0495 (Stage 5 budget).

## Proposed change

At Stage 5 write to the calibration report (and the executions ledger row) a small table: workflow runs by conclusion
(success, failure, cancelled), review iterations, and for each blocked iteration a reason class from a fixed list
(defect, nit-only, ci-authorisation, ci-flake, main-moved, no-new-head, other). Counting uses data the loop already
holds; nothing new is fetched except one `gh run list` call.

## Expected gain and cost

Makes the next audit's churn count a read instead of a reconstruction, and lets a future gate warn when churn exceeds a
threshold. Cost: about 100 lines plus a test; no effect on the critical path.
