---
# holon-agentic-coder-ref-metadata-0363
title: "After merging main, wait for CI before calibrating; restart PR review from the start if CI breaks"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-4
  - stage-5
  - ci
  - calibration
  - holon-agentic-coder
created_at: 2026-11-23T03:30:00Z
updated_at: 2026-11-23T03:30:00Z
---

## Problem

After Stage 4 reaches consensus, the flow merges `origin/main` into the PR branch and goes straight to Stage 5, pushing
calibration commits without waiting for CI on the merged head. An approval can therefore be calibrated on code CI never
passed.

Seen on PR #244 (2026-11-23): stress CI passed on `360f8471` (iteration 9) and consensus was reached at iteration 10
(`aad7dae9`, ledger rows only). At 03:17:47 the flow merged main (`3dc0830c`, which brought in PR #243's env-file
change), then pushed calibration commits up to `575655bb` at 03:18:09. Workspace survival then failed on `575655bb`
(`test_url_message_fuzz.py::test_invalid_envelope_value_never_echoed_by_doctor_or_run_path`, 2/2480 cases with an
invalid `HOLON_TURN_TIMEOUT_SECONDS` value echoed). The flow's guard posted "Ensemble Consensus Approval no longer
stands" at 03:26, but the calibration report was already on the PR.

## Goal

1. **Wait for CI on the merged head.** Whenever the flow merges `main` into the PR branch (after consensus or at any
   later point before Stage 5), Stage 5 starts only once every CI check on the merged head commit has completed and
   passed. Cancelled or superseded runs do not count as passing; the flow waits for (or re-triggers) a run on that exact
   head SHA.
2. **CI breaks → review restarts from the beginning.** If any check on the merged head fails, the earlier consensus is
   void: the flow returns to the start of Stage 4 (a fresh review loop, iteration counter and reviewer ensemble reset
   for the new head) so the failure is reviewed and resolved like any other finding, and must reach a new 3/3 consensus
   before Stage 5. The voided approval is recorded in the ledger (append-only; old rows untouched) and the PR comment
   says the approval was withdrawn and review restarted.
3. **No merge needed → unchanged.** If the head was already current with `main` and CI on it is green, Stage 5 proceeds
   as today.
4. Log which CI run (head SHA, run ids, conclusions) Stage 5 relied on.

## Tests

- merge main after consensus → Stage 5 blocked until CI on the merged head is green, then runs;
- merge main → CI fails → review restarts at iteration 1 for the new head, no calibration commit pushed;
- cancelled run on the merged head → treated as not passed (wait or re-run), never as green;
- no merge needed and CI green → Stage 5 runs immediately.

## Notes

- Related: bean 0362 (stale-calibration warning lifecycle) and bean 0354 (test gate judges the current head).
