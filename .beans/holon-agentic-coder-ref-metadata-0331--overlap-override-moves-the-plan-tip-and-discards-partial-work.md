---
# holon-agentic-coder-ref-metadata-0331
title: "Each --allow-overlap resume moves the plan tip, so Stage 3 partial work is never continued"
status: completed
type: bug
priority: high
tags:
  - flow
  - stage-3
  - resume
  - overlap
  - holon-agentic-coder
created_at: 2026-11-18T12:45:00Z
updated_at: 2026-11-20T14:30:00+11:00
---

## Problem

Seen on the `shortref` flow (Bean 0321), 2026-11-18, run concurrently with `macgate` (Bean 0316, PR #205). Stage 3 was
executed three times from scratch, about 45 minutes each, and no attempt continued the previous one.

1. **The override record moves the plan tip.** When Stage 3 is admitted with `--allow-overlap`, the engine commits
   "execute: record the --allow-overlap admission override" on the plan branch (`ea75ca96`, then `f2be3a87`). A partial
   head left by an earlier attempt descends from the older plan tip, so `resolve_partial_head`
   (`entrypoint/execution_workspace.py`) rejects it with "not a descendant of the plan tip" and the executor starts
   again from the plan. Every resume under an overlap adds another record commit, so the salvage of Bean 0171 can never
   apply while the overlap lasts.
2. **The harness runner overrides the admission refusal by itself.**
   `.agents/skills/holon_flow/scripts/run_holon_flow.py` (around line 406) relaunches with `--allow-overlap` after Stage
   3 is refused for a touch-set overlap, with nobody asking for it. This also happened on the `macgate` flow.
3. **Directory entries in a touch set overlap everything beneath them.** The `shortref` intent listed `flow/` and
   `tests/` as scope, and the refusal counted every file PR #205 changed under those directories. The only file both
   flows really changed was `apps/sandbox-executor/flow_module_budgets.json`.
4. **The execute budget was not raised.** The triage note says to set `HOLON_STAGE_BUDGET_EXECUTE_MINUTES=10080` until
   Bean 0172 lands; the runner does not set it, and the third attempt was cut off by the 45-minute budget at step 11 of
   the plan (`execute stage budget of 2614 s exceeded`).

## Action

- Target (`holon-agentic-coder`, through the Holon flow): recording an overlap override must not invalidate partial
  work. Either record the override once per plan and not again on a resume, or accept a partial head that descends from
  any earlier tip of the same plan branch. Add a hermetic test: fail Stage 3 under an override, resume, and assert the
  executor continues from the partial head.
- Harness (directly editable): `run_holon_flow.py` must not add `--allow-overlap` on its own; it stops and reports the
  overlapping paths unless the flag was passed by the caller. It should also set the execute budget from the triage
  note, or the note should be retired by Bean 0172.
- Intent authoring: list files, not whole directories, in `scope` when another flow is in flight.

## Progress

- **Harness half done (2026-11-19).** `run_holon_flow.py` no longer retries with `--allow-overlap` after an admission
  refusal: it prints the refusal and exits, and passes the flag only when the caller gave it. `flow_env.py` sets
  `HOLON_STAGE_BUDGET_EXECUTE_MINUTES=10080` unless the caller set a value. Three tests added to
  `tests/test_flow_env.py`; `uv run pytest` passes (84).
- **Target half open.** It changes the Stage 3 resume code, which the Bean 0321 flow also changes, so its flow starts
  after Bean 0321 merges.
- **2026-11-20:** Bean 0321 merged (PR #206, `cac463b9`), so the target half is now unblocked and can start as its own
  flow. Harness half remains done; status stays in-progress.
- **2026-11-20:** Flow `resumetip` (holon-agentic-coder, claude-agent/claude-opus-5-5, combined with Bean 0331/0335)
  passed Stage 1 (`I-1795136616-resumetip/_`) and Stage 2 (`P-1795136633-CLA-CO5.5`, EV 39.61). Stage 3 admission
  refused: touch set overlaps PR #207 (`rescrash` flow) on `apps/sandbox-executor/flow_module_budgets.json`,
  `apps/sandbox-executor/src/sandbox_executor/flow/__init__.py`, `apps/sandbox-executor/tests/flow/test_admission.py`
  and `apps/sandbox-executor/tests/flow/stages/test_execute.py`. Not overridden; resume with `--from-stage execute` in
  `flow-resumetip` after PR #207 merges.

- **2026-11-20:** Flow `resumetip` resumed at Stage 3 with the maintainer-authorised one-time `--allow-overlap` (overlap
  with the waiting `blockedflow` flow, recorded on the plan branch). Executor (claude-opus-5-5) finished in 13.5 min
  (4441 tests passed) and pushed `E-1795139222-CLA-CO5.5/_`, but its pre-push sync hit non-ledger conflicts with
  `origin/main` (PR #207) in `apps/sandbox-executor/flow_module_budgets.json` and
  `apps/sandbox-executor/src/sandbox_executor/flow/__init__.py`, so Stage 4 stopped. A resolve-conflict subagent merged
  `origin/main` (additive `__all__` union; budget for `flow/__init__.py` set to its real 514 lines; lint and 898 flow
  tests pass), then the flow resumed from Stage 4 without the override. PR #208
  (https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/208) reached 3/3 approval at iteration 2 (iteration 1
  had one Important finding per reviewer, resolved). Calibration is in the PR: predicted EV 39.61, actual EV -19.01 (ΔEV
  -58.62). CI is green on head `18c4e10`, and the PR is MERGEABLE/CLEAN and waiting for a human merge.

## Resolution

Delivered via [PR #208](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/208) and merged into `main`
(`00fa535`), in the same `resumetip` flow as Bean 0335:

- **Override records no longer invalidate partial work**: the `--allow-overlap` admission override is recorded once per
  plan, not on every resume, and `resolve_partial_head` accepts a partial head that descends from any earlier tip of the
  same plan branch.
- **Harness half**: the runner no longer relaunches with `--allow-overlap` on its own (done before this flow).
- **Verification & Tests**: 4441 tests passed on the executor run; review approved 3/3 at iteration 2; CI green on head
  `18c4e10`. Calibration: predicted EV 39.61, actual EV -19.01 (delta -58.62).
- **Holon Flow Traversal**: Stage 4 stopped on a pre-push sync conflict with `origin/main` (PR #207); a resolve-conflict
  subagent merged `origin/main` and the flow resumed from Stage 4 without the override. All five stages then completed.

## Notes

- Related: Bean 0151 (touch-set admission), Bean 0171 (Stage 3 partial-work salvage), Bean 0172 (explicit unlimited
  budgets), Bean 0321 (the affected flow).
