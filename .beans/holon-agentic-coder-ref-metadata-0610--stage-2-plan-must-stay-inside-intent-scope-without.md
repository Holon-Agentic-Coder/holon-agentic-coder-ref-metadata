---
# holon-agentic-coder-ref-metadata-0610
title: "Stage 2 plan must stay inside intent scope without recorded expansion"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-2
  - scope
  - holon-agentic-coder
created_at: 2026-11-27T05:18:43Z
updated_at: 2026-11-27T05:18:43Z
---

## Notes

### Evidence (2026-11-27T04:43Z–05:18Z fifth-merge audit)

- Four of the six non-`0153` PRs merged in the window touched code files outside `intent.scope`:
  - `PR #374` (`review-findings-all-actioned`): `intent.scope` listed `8` files; Stage 2 `plan` widened to `35` paths;
    PR changed `19` code files (`14` outside `intent.scope`, plus `flow/stages/review.py` outside even the plan touch
    set).
  - `PR #376` (`macos-unit-sharded`): `intent.scope` listed `3` files; Stage 2 `plan` widened to `16` paths (including
    shared hub docs `.github/workflows/README.md`, `docs/git_flow.md`, `.github/actions/bookkeeping-gate/action.yml`);
    PR changed `9` code files (`6` outside `intent.scope`).
  - `PR #378` (`self-explaining-counts-report`): `intent.scope` listed `5` files; Stage 2 `plan` widened to `8` paths;
    PR changed `8` code files (`3` outside `intent.scope`, plus `calibration/self_explaining_counts.py` outside the plan
    touch set).
  - `PR #375` (`self-explaining-gate-pre-push`): changed `test_executor_characterisation.py` outside both `intent.scope`
    and plan.
- Bean `0596` (`todo/intent-0596-diff-stays-in-intent-scope.json`) checks Stage 4 resolver commits and Stage 5 diffs
  against the **plan touch set** (plus recorded re-plans), NOT `intent.scope`. Bean `0546` only covers
  `holon intent-check` pre-launch companion discovery. Nothing stops Stage 2 (`plan`) from expanding a 3-file intent
  into a 16- or 35-file plan and pulling hub files into overlap queues.

### Proposed Change

- Enforce in Stage 2 (`plan` exit / Stage 3 admission) that every file in the plan's `## Touch Set` is present in
  `intent.scope` (excluding provenance paths `plans/`, `executions/`, `holon-knowledge/`, `intents/`), unless an
  explicit recorded scope-expansion entry is appended and checked against open PRs and active flows before Stage 3
  admission.
- Fail Stage 2 (or require explicit scope expansion) when the planner emits a `## Touch Set` file outside
  `intent.scope`.

### Expected Gain & Cost

- Eliminates silent post-intent scope creep (`23` out-of-scope files across `#374`, `#375`, `#376`, `#378`) and prevents
  Stage 2 from dragging hub docs (`README.md`, `git_flow.md`) into overlap refusals.
- Cost: small validation step at Stage 2 exit + tests; existing `intent-check` (bean `0546`) already supplies companion
  files before launch.

## Resolution
