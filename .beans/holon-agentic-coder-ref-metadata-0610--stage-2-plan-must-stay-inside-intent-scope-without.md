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
updated_at: 2026-11-27T10:56:02Z
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

### Audit evidence (2026-11-27T07:49Z fifth-merge audit — 4 recurrences in 2.5 h)

- **`CF-0039` (`0590`, `stage1-requires-assumptions`, `05:22:32Z`):** passed `intent.scope` disjointness pre-launch,
  then Stage 2 expanded into `apps/sandbox-executor/tests/flow/test_pipeline_unlimited.py` and parked on PR `#407`.
- **`CF-0041` (`0567`, `coherence-commit-trailer-check`, `06:09:19Z`):** Stage 2 expanded into
  `tests/test_scripts_self_doc.py` (unlisted in `intent.scope`) and parked on Coherence PR `#58`.
- **`CF-0042` (`0563`, `coherence-ledger-invariants`, `06:15:08Z`):** Stage 2 expanded into
  `tests/test_scripts_self_doc.py` (unlisted in `intent.scope`) and parked on Coherence PR `#58`.
- **`CF-0045` (`0524` slice 2, `coherence-cache-scrub-endpoints`, `07:34:44Z`):** Stage 2 expanded into
  `tests/commands/test_start.py` and `tests/commands/test_web_token.py` and parked on Coherence PR `#63`.

### Audit evidence (2026-11-27T10:55Z fifth-merge audit)

- **`CF-0052` (`0619`, `stage4-main-baseline-guard`, `08:29:46Z`):** Stage 2 plan widened into
  `apps/sandbox-executor/src/sandbox_executor/flow/review/loop.py` outside `intent.scope` and parked cleanly at Stage 3
  admission on live bean `0618` (`flow-stage4-carried-finding-clean-tree`).

## Resolution
