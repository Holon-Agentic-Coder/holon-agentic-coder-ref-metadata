---
# holon-agentic-coder-ref-metadata-0438
title: "Stage 5 counted_target_only_file fails calibration after a conflict-merge adapts a main file"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-5
  - calibration
  - conflict-resolution
  - holon-agentic-coder
created_at: 2026-11-25T00:28:00Z
updated_at: 2026-11-25T00:28:00Z
---

## Problem

Stage 5 calibration fails with `CalibrationSelfCheckError: counted_target_only_file` whenever a flow merges
`origin/main` and its merge commit adapts a file that `main` added since the plan branch.

## Evidence (2026-11-24, PR #283)

- On `holon-agentic-coder#283` (`resolve-conflicts-in-flow`, checkpoint
  `apps/holon-agentic-coder/flow-resolve-conflicts-in-flow/.holon/flow/checkpoint-resolve-conflicts-in-flow.json`),
  Stage 5 failed at `2026-11-24T23:36:28Z` (`0.3 min`):
  `Calibrate stage failed: the calibration report self-check found counted_target_only_file, so nothing was committed or pushed.`
- Reproduced on head `08f788a7` (`merge_base_sha=acbf790ea691cf89a53dd8f986eeb01a1855386b`):
  - `origin/main` (`acbf790e`, PR #275) added `apps/sandbox-executor/tests/flow/stages/test_replan_request.py`.
  - Merge commit `221f9d73` merged `origin/main` into PR #283 and adapted 1 line of `test_replan_request.py`
    (`check_and_resolve_stage_conflicts` $\rightarrow$ `at_stage_boundary`) to match PR #283's refactor.
  - `execution_patch_numstat` (`git diff --numstat acbf790e...08f788a7`) therefore legitimately includes
    `test_replan_request.py` (1 insertion, 1 deletion), and `git diff --name-only <plan>...acbf790e` (`on_target`) also
    includes it.
  - However, `target_only_paths` in
    `apps/holon-agentic-coder/main/apps/sandbox-executor/src/sandbox_executor/calibration_self_check.py:112-120`
    computes `own` via `git log --no-merges --name-only --format= {merge_base_sha}..{head_sha} --`, which skips merge
    commits (`221f9d73`). Because `--no-merges` omits the conflict-resolution edit, `test_replan_request.py` falls into
    `on_target - own` (`337` paths) and intersects `counted_paths` (`301` paths), falsely failing Stage 5.

## Proposed change

1. Fix `target_only_paths` in `calibration_self_check.py` so `own` includes paths actually modified relative to
   `merge_base_sha` across merge commits (e.g. `git diff --name-only {merge_base_sha}...{head_sha} --` or inspecting
   merge-commit diffs against their target parent), instead of relying solely on `git log --no-merges`.
2. Add a hermetic regression test in `tests/test_calibration_self_check.py` where the target branch adds a file after
   the plan branch, a merge commit adapts that file on the execution branch, and `self_check_report` returns `[]`.

## Expected gain

Unblocks Stage 5 calibration on PR #283 and prevents false-positive `counted_target_only_file` failures (saving ~15–30
min of halted-PR triage and manual recovery per affected conflict-merging flow).

## Cost

Small: single-function fix and unit test in `sandbox_executor`, delivered via the Holon flow (touches
`calibration_self_check.py` and `test_calibration_self_check.py`).

## Notes

- Target repo change through the Holon flow (`holon-agentic-coder`).
- Related: Bean `0428` (3-dot PR-own diff semantics), Bean `0376` (`PR #283` in-flow conflict resolution).
