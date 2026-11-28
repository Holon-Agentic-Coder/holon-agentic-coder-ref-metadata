---
# holon-agentic-coder-ref-metadata-0639
title: "HAC main broken at 27b4197e7 after burst merge: preflight cycle and test_plan_scope_guard assumptions"
status: todo
type: bug
priority: high
tags:
  - holon-agentic-coder
  - ci
  - architecture
created_at: 2026-11-28T00:01:43Z
updated_at: 2026-11-28T00:01:43Z
---

## Notes

### Evidence (2026-11-28T00:01Z fifth-merge audit, `holon-agentic-coder@27b4197e7`)

- Burst-merging `23` `holon-agentic-coder` PRs (`#428..#456`) between `2026-11-27T23:38:00Z` and `23:45:15Z` left
  `origin/main` (`27b4197e7`) **RED** on both **`Test - Unit`** (run `46084228956`: `4 failed, 10772 passed` on
  `ubuntu-latest` and `macos-latest`) and **`Test - Stress`** (run `46084229004`: `stress-child survival` failed the
  same `4` unit tests).
- Two cross-PR semantic interactions caused the `4` failures (each PR was individually `MERGEABLE`/`CLEAN` against its
  pre-burst base):
  1. **Root import cycle (`#432` + `#456`):** `PR #432` (`65c7741f7`, merged `23:38:54Z`) extended
     `apps/sandbox-executor/tests/test_import_cycle_ratchet.py` to cover root-level modules, while `PR #456`
     (`27b4197e7`, merged `23:44:57Z`) added a bidirectional cycle `preflight -> preflight_cooldown` (`1` site in
     `apps/sandbox-executor/src/sandbox_executor/preflight.py`) `<->` `preflight_cooldown -> preflight` (`4` sites in
     `apps/sandbox-executor/src/sandbox_executor/preflight_cooldown.py:19, 218, 252, 291`), failing
     `test_sandbox_executor_package_import_cycle_ratchet`.
  2. **Stage 1 `assumptions` contract (`#430` + `#438`):** `PR #430` (`c7700077c`, merged `23:38:18Z`) added
     `apps/sandbox-executor/tests/flow/stages/test_plan_scope_guard.py` with `intent_data` fixtures lacking
     `assumptions`, while `PR #438` (`e2e4e6c0f`, merged `23:41:22Z`) enforced non-empty `assumptions` in Stage 1,
     failing:
     - `test_pipeline_fails_at_stage2_before_stage3_admission_on_unrecorded_out_of_scope_touch_set` (`KeyError: 'plan'`)
     - `test_run_plan_stage_passes_with_in_scope_provenance_and_recorded_expansion`
     - `test_run_plan_stage_fails_when_plan_row_touch_set_exceeds_intent_scope`

### Proposed Change

1. Break the `preflight <-> preflight_cooldown` bidirectional import cycle (e.g., extract shared cooldown
   result/status/redaction types or pass callbacks/types from `preflight_cooldown.py` without importing
   `sandbox_executor.preflight`).
2. Add valid non-empty `"assumptions"` entries to the `intent_data` test fixtures in
   `apps/sandbox-executor/tests/flow/stages/test_plan_scope_guard.py` so Stage 1 passes and tests the Stage 2 plan scope
   guard.
3. Re-establish green `Test - Unit` and `Test - Stress` on `holon-agentic-coder/main` (note: downstream flows cut from
   `27b4197e7` will fail `Test - Unit` until this lands).

### Expected Gain & Cost

- Unblocks `holon-agentic-coder/main` CI (`Test - Unit` and `Test - Stress`) for all subsequent flows.
- Cost: small (`~20` lines across `preflight_cooldown.py` / `preflight.py` and `test_plan_scope_guard.py`).

## Acceptance Criteria

- [ ] `apps/sandbox-executor/src/sandbox_executor/preflight_cooldown.py` and `preflight.py` have zero bidirectional
      import cycle; `test_sandbox_executor_package_import_cycle_ratchet` passes with no ratchet baseline bump.
- [ ] `apps/sandbox-executor/tests/flow/stages/test_plan_scope_guard.py` supplies valid non-empty `assumptions` and all
      tests pass under `uv run pytest`.
- [ ] `Test - Unit` and `Test - Stress` pass on `holon-agentic-coder/main` (`uv run pytest`).

## Resolution
