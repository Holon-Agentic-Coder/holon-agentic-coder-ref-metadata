---
# holon-agentic-coder-ref-metadata-0503
title: "Review loop approves a flow PR whose measured acceptance criteria are not met"
status: todo
type: bug
priority: high
tags:
  - tests
  - flow
  - holon-agentic-coder
created_at: 2026-11-26T09:45:00Z
updated_at: 2026-11-26T09:45:00Z
---

## Problem

Flow `tests-cpu-bound-redaction-ledger` (PR #327 on holon-agentic-coder, merged by the maintainer 2026-11-26 09:38:33Z)
reached 3/3 consensus approval, calibration and a clean merge while its own execution notes state two acceptance misses
in the intent:

- The summed time of the files in scope fell 27.8 percent (median 68.16 s to 49.24 s), not the required 35 percent.
- The whole unit selection still shows `9 failed` (all in `test_stress_support.py`, called out of scope in the notes) in
  every run of both arms, while the intent requires the selection to pass.

Neither criterion gates Stage 4 or Stage 5; the wrapper reported "completed successfully" and the review loop recorded
"Consensus approval reached".

## Why it matters

The intent's measurable criteria are the reason the flow was launched. A PR that misses them can merge under a green
"approved" banner, and the calibration then records a result the intent said was a failure.

## Next step

Make the review ensemble (or the wrapper's terminal gate) check each intent `acceptance_criteria` item that the
execution notes report as not met, and withhold consensus or report it as a blocker. Keep `apps/sandbox-executor`
test-only flows as the regression case.
