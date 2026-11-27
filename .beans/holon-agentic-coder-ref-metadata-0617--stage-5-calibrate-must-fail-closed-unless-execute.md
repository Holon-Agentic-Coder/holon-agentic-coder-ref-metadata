---
# holon-agentic-coder-ref-metadata-0617
title: "Stage 5 calibrate must fail closed unless execute succeeded and review consensus is posted"
status: in-progress
type: bug
priority: high
tags:
  - flow
  - stage-5
  - holon-agentic-coder
created_at: 2026-11-27T07:49:17Z
updated_at: 2026-11-27T08:09:39Z
---

## Notes

### Evidence (2026-11-27T07:49Z fifth-merge audit)

- On `holon-coherence#66` (`coherence-metrics-unification`, `CF-0044`), Stage 3 execute `E-1795762157` failed on frozen
  `holon-config/hygiene/module_budgets.json` (`d46244705`) and `E-1795762823` recorded a failed execution row
  (`94ecffdc5`), and Stage 4 failed at `07:16:26Z` when `gh pr comment` / `gh pr review` hit a proxy connection reset
  (`reviews: []`, `comments: []`).
- At `07:16:58Z`, `holon flow --from-stage calibrate` was invoked by the `flash_lite` driver (`84d630b7`). Stage 5
  logged `"Merged-head CI gate skipped: no Stage 4 approval recorded"`, generated and pushed calibration commits
  (`e3d8256da`, `31201f262`, `46cf64b0b`), waited `114.54 s` for CI, and exited `calibrate: ok (2.6 min)`
  (`status=success`) on an unreviewed PR carrying an unauthorized `module_budgets.json` change.
- In the same window, `holon-agentic-coder#410` (`diff-stays-in-intent-scope`) halted in Stage 4 (`ac158b80`) and was
  manually salvaged (`4e6bb14f`) and merged at `07:39:41Z` with `reviews: []` and no calibration commit.

### Proposed Change

- Enforce fail-closed prerequisites on Stage 5 (`run_calibrate` / stage entry): refuse `CALIBRATE` with non-zero exit
  unless `stage_results["execute"].status == "success"` and `stage_results["review"].status == "approved"`, and verify a
  posted GitHub consensus review (or valid carried fingerprint on a reviewed PR) exists before calibrating or exiting 0.
- Remove `"Merged-head CI gate skipped: no Stage 4 approval recorded"` silent pass-through.
- Update `.agents/skills/holon_flow/SKILL.md` (or wrapper guard) to reject `--from-stage calibrate` when checkpoint
  `stage_results` shows `execute` or `review` did not succeed/approve.

### Expected Gain & Cost

- Eliminates unreviewed/unapproved PRs passing Stage 5 calibration and falsely appearing complete (`CF-0044`;
  `verification` repeated twice in `CF-0043`–`CF-0044`, 6x total).
- Cost: small prerequisite check in Stage 5 + wrapper guard + unit tests.

## Acceptance Criteria

- Stage 5 (`run_calibrate` / `stage5.py`) refuses calibration with non-zero exit unless `execute` succeeded and `review`
  reached consensus approval with a posted GitHub consensus review (or valid carried fingerprint on a reviewed PR).
- Stage 5 removes the silent `"Merged-head CI gate skipped: no Stage 4 approval recorded"` pass-through so unreviewed or
  unexecuted runs cannot exit `0`.
- Unit tests in `apps/sandbox-executor/tests/flow/test_stage5_fail_closed.py` fail without the guard and pass with
  `uv run pytest`, and `uv run task lint` passes cleanly; self-explaining code invariant holds.

## Resolution
