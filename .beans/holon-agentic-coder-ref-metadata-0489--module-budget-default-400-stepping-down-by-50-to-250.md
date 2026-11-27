---
# holon-agentic-coder-ref-metadata-0489
title: "Module line budget: default 400 for now, then step down by 50 per pull request to 250, decomposing at each step"
status: in-progress
type: task
priority: high
tags:
  - hygiene
  - module-budget
  - architecture
  - refactoring
  - holon-agentic-coder
created_at: 2026-11-26T06:30:00Z
updated_at: 2026-11-27T01:07:43Z
blocked_by:
  - "0380"
---

## Instruction (maintainer, 2026-11-26)

"Bump up the budget to 400 for now. There will be multiple PRs that will decrease the budget by 50. Each time the budget
is hit you will make a change to decompose the files, until the budget of 250 is achieved."

This is the maintainer's explicit authorisation to change `holon-config/hygiene/module_budgets.json` for this schedule
only; each flow's intent carries it in the `module_budget_change` field, and each pull request needs the
`module-budget-change` label (applied by the maintainer) for CI to accept the change (Bean 0486).

## Plan

One pull request per step, each a separate holon flow, in order:

| Step | Default budget | Work in the pull request                                                               |
| :--- | -------------: | :------------------------------------------------------------------------------------- |
| 1    |            400 | Raise the default from 200 to 400; drop every override at or below 400 (now redundant) |
| 2    |            350 | Lower the default to 350; decompose every module between 351 and 400 lines             |
| 3    |            300 | Lower the default to 300; decompose every module between 301 and 350 lines             |
| 4    |            250 | Lower the default to 250; decompose every module between 251 and 300 lines (target)    |

- A step that would touch too many modules for one flow is split into several flows (decomposition first, then the
  budget change), each with a file-level scope.
- Decomposition is move-only where possible (like the `flow/` and `cli/` splits), keeps public imports working, and puts
  no logic in `__init__.py` (Bean 0379).
- Every step re-measures: module count over the new default before and after, and the largest remaining modules.
- Overrides only ratchet down at every step; none is ever raised or added.

## Open question for the maintainer

Modules far over 400 (for example `calibration.py` about 1,600 lines, `review_ensemble.py` about 990, `env_registry.py`
about 930, `turns.py` about 890) keep frozen ratchet-down overrides from Bean 0380. Should each step also bring them
under the new default, or do they stay on their overrides and get their own decomposition beans (for example Bean 0197
for `calibration.py`)? Default assumed here: they stay on overrides and are handled by their own beans.

## Dependencies

- Starts after Bean 0380 (PR #317: discovery-based coverage, overrides frozen at current size) merges, since step 1
  edits the configuration that pull request introduces, and after Bean 0486 (CI honours the label).
- Related: Bean 0340 (revisit the 200-line default), Bean 0197 (split `calibration.py`).

## Flow

in-progress 2026-11-26T08:31:01Z: holon flow `module-budget-default-400` (step 1, default 400), runner claude-agent /
claude-opus-5-5, log `todo/flow-module-budget-default-400.log`, intent `todo/intent-0489-module-budget-default-400.json`
(scope adds docs/architecture.md, which states the 200-line default).

PR #326 opened by flow `module-budget-default-400` (2026-11-26T08:42:18Z). Needs the maintainer's `module-budget-change`
label for CI hygiene to accept the budget change; not applied by the agent.

flow `module-budget-default-400` completed 2026-11-26T09:51:05Z: PR #326 (head 532f3834, base main), MERGEABLE/CLEAN,
label `module-budget-change` applied by the maintainer (not by the agent), review consensus APPROVED on iteration 8
(iterations 1-7 blocked on the label, same as bean 0497), calibration included (EV predicted 64.59 in state file).
Overrides 61 -> 24: 37 removed (all at or below 400), 24 kept (all above 400, unchanged). Next step's decomposition set:
5 modules at 351-400 (knowledge/wisdom.py 353, budgets.py 359, flow/git_refs.py 380, scripts/pre_commit_check.py 381,
cli/commands/flow.py 398). Scope note: the flow also edited holon-config/prompts/planner.template.md (stale "default
200" text), outside the intent scope. Status stays in-progress until the maintainer merges.

Step 1 merged: PR #326 merged into `main` (`67f6ea89`, 2026-11-26T09:51:19Z). Default raised 200 to 400; overrides 61 to
24 (37 removed, all at or below 400; the 24 kept are all above 400 and unchanged). The flow also edited
`holon-config/prompts/planner.template.md` (stale "default 200" wording), outside the intent scope. Post-merge:
`install-holon` rebuilt all images and reinstalled `holon` and `holon-coherence`; the flow worktree and the intent's
branches were removed.

Step 2 set (default 350, decompose the modules between 351 and 400): `knowledge/wisdom.py` 353,
`sandbox_executor/budgets.py` 359, `flow/git_refs.py` 380, `scripts/pre_commit_check.py` 381, `cli/commands/flow.py` 398
lines on `main` (measured 2026-11-26; the flow's own count matches).

2026-11-26T09:55:25Z: in-progress, holon flow `module-budget-default-350` (step 2, default 350), runner claude-agent /
claude-opus-5-5, log `todo/flow-module-budget-default-350.log`, intent `todo/intent-0489-module-budget-default-350.json`
(scope adds the new split modules).

2026-11-26T10:01:04Z: parked: Stage 3 admission refused (touch set overlaps local flow `no-unneeded-full-review`, branch
I-1795665991-no-unneeded-full-review, on apps/sandbox-executor/src/sandbox_executor/budgets.py); flow
`module-budget-default-350` kept its worktree `flow-module-budget-default-350` and checkpoint; resume from checkpoint
(--checkpoint, never relaunch without it) once that flow merges or releases budgets.py.

- 2026-11-26T12:10Z: PR #335 merged to `main` (`f0d6c56d`).
  `apps/sandbox-executor/src/sandbox_executor/flow/github/ci_final_head.py` is now 368 lines (wc -l on `main`), above
  the step-2 default of 350. Add it to the step-2 split set (`module-budget-default-350`, parked; resume from
  checkpoint). The step-2 set on `main` is then: `knowledge/wisdom.py` 353, `sandbox_executor/budgets.py` 359,
  `flow/git_refs.py` 380, `cli/commands/flow.py` 398, `flow/github/ci_final_head.py` 368.

## Flow log (2026-11-27, parked)

- Retired the stale attempt (worktree `flow-module-budget-default-350`, local and remote
  `I-1795686809-module-budget-default-350/*` branches; no PR, nothing unique beyond its plan).
- Launched a fresh step-2 flow from `todo/intent-0489-module-budget-default-350.json` (six modules, plus
  `ci_final_head_seams.py` and `ci_final_head_rerun.py` for `ci_final_head.py`; `module_budget_change` kept). Intent and
  plan stages passed (plan EV 36.6).
- Stage 3 refused on a touch-set overlap with flow `I-1795665991-no-unneeded-full-review` on `budgets.py`. Run stopped
  with `--no-wait-on-overlap`; `--allow-overlap` not used. Parked:
  `parked 2026-11-27: blocked by flow no-unneeded-full-review (PR #334, merged 2026-11-26) on budgets.py`.
- The blocker has since merged, but the flow worktree and its checkpoint no longer exist (I-/P- branches also gone; the
  intent and plan commits survive as unreferenced objects). Resuming needs a maintainer or coordinator decision on a
  fresh launch without a checkpoint.
- No PR yet, so the `module-budget-change` label has not been requested. Bug logged as bean 0519.

- 2026-11-26T20:59:26Z: resumed: holon flow `module-budget-default-350` (step 2, default 350) from checkpoint (execute
  stage), runner claude-agent / claude-opus-5-5. Blocker PR #342 merged (57a8aa38, 2026-11-26T20:58:42Z).
  Module-budget-change label: required for CI on the PR; noted here, not applied by the agent.
- 2026-11-26T21:00:28Z: parked: Stage 3 admission refused on overlap with PR #349 (branch
  I-1795704651-kb-wisdom-deterministic-files) on apps/sandbox-executor/src/sandbox_executor/knowledge/wisdom.py.
  Worktree flow-module-budget-default-350 and checkpoint kept; resume from checkpoint (--checkpoint, never relaunch
  without it) once PR #349 merges or releases wisdom.py.

## Note (coordinator, 2026-11-26 21:05Z)

After PR #347 split `calibration.py` into the `calibration/` package, `holon-config/hygiene/module_budgets.json` still
carries an override `calibration.py: 1608` for a file that no longer exists. Removing a dead override is a budget-file
change, so it belongs to this bean's authorised schedule: drop it in the next budget step (step 2 if its plan can take
it, otherwise step 3), and have the budget check flag overrides whose file is gone.

- 2026-11-26T21:04Z: resumed: holon flow `module-budget-default-350` (step 2, default 350) from checkpoint (execute
  stage), runner claude-agent / claude-opus-5-5, log `todo/flow-module-budget-default-350.log`. Blocker PR #349 merged
  (2c865160, 2026-11-26T21:03:27Z); PR #346 merged (aa085c38). Module-budget-change label: required for CI on the PR;
  noted here, not applied by the agent. Worktree was behind main (3e83fadc vs 2c865160); the flow engine owns any sync.
- 2026-11-26T21:05Z: parked again: Stage 3 admission refused on overlap with local flow `single-runner-per-checkpoint`
  (branch I-1795685390-single-runner-per-checkpoint/P-1795704471-CLA-CO5.5/_, worktree
  flow-single-runner-per-checkpoint, still running) on apps/sandbox-executor/src/sandbox_executor/flow/lazy_exports.py.
  Worktree flow-module-budget-default-350 and checkpoint kept; resume from checkpoint (--checkpoint, never relaunch
  without it) once that flow merges or releases lazy_exports.py. Also: wisdom.py overlap with #349 cleared (PR #349
  merged 2026-11-26T21:03:27Z).

## Note (post-merge of PR #346, 2026-11-26T21:05:09Z)

PR #346 (merged `aa085c3`) takes `scripts/ci_bookkeeping_api.py` to 383 lines (`wc -l` on `main`), above the step-2
default of 350. The parked step-2 plan was made before #346 and does not cover it. When step 2 resumes, its review loop
will hit a hygiene failure on that file. The fix is to split it (move-only), not an override. Add it to the step-2 split
set.

- 2026-11-26T22:58Z: resumed: holon flow `module-budget-default-350` (step 2, default 350) from checkpoint (execute
  stage), runner claude-agent / claude-opus-5-5, `--no-wait-on-overlap`, log `todo/flow-module-budget-default-350.log`.
  PR #351 (blocker) merged; main contains 2f29d8c. Post-merge reinstall of holon finished (no install process live for
  two checks). Module-budget-change label: required for CI on the PR, noted here, not applied by the agent.
- 2026-11-26T22:59Z: parked again: Stage 3 admission refused on overlap with PR #357 (flow `self-explaining-code-gate`,
  branch I-1795732927-self-explaining-code-gate/..., still open) on `scripts/pre_commit_check.py`. Worktree
  `flow-module-budget-default-350` and checkpoint kept; resume from checkpoint (`--checkpoint`, never relaunch without
  it) once PR #357 merges or releases `scripts/pre_commit_check.py`. PR #357 touches a file in this step's decomposition
  set.

## Progress

- resumed 2026-11-26: PR #357 merged (main contains 5a2868a); flow module-budget-default-350 resumed from its checkpoint
  (Stage 3 admitted with --no-wait-on-overlap). Invariant sentence added to the intent goal and checkpoint copies.
- 2026-11-27 Stage 4 blocked: flow module-budget-default-350 reached consensus CHANGES_REQUESTED in review iterations
  1-3 (engine still looping to iteration 4 of 25). Finding: default 350 unmet because scripts/ci_bookkeeping_api.py (383
  lines) is not in the intent scope; resolver rejects it as out of scope. Needs an intent scope change (add that file)
  before a rerun.
