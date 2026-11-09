---
# holon-agentic-coder-ref-metadata-0254
title: "Split flow.py into a flow/ package of focused modules (move only) so concurrent flows stop colliding"
status: completed
type: task
priority: critical
tags:
  - flow
  - refactor
  - architecture
  - concurrency
  - holon-agentic-coder
created_at: 2026-11-09T01:00:00Z
updated_at: 2026-11-09T04:00:00Z
---

## Problem

`apps/sandbox-executor/src/sandbox_executor/flow.py` (`main` at `8b1e668`) is **6,160 lines** with **124 top-level
functions and classes**. Its test file, `tests/test_flow.py`, is **6,483 lines**. Since 2026-10-01, 44 commits have
touched `flow.py`. Almost every flow PR in the current batch changed it: #135, #137, #139, #140, #141, #143 and #145.

Because the whole flow engine lives in one file:

- **Concurrent flows cannot run in parallel.** Any two holon-agentic-coder beans almost always overlap on `flow.py`, so
  the triage runs them strictly one at a time. Beans 0252 and 0253 both wait behind Bean 0149 (PR #146) for this reason
  alone.
- **Every merge to `main` invalidates the open PRs.** PR #143 needed two `merge origin/main` rounds and a stale
  `/calibrated` rebuild while #142 and #144 landed.
- **Reviews are slow and noisy.** Reviewers and resolvers load a 6,000-line file to change a 30-line function.

It supersedes Bean 0187, which planned the same split from a 5,157-line snapshot (`993b686`) that is now out of date.

## Current inventory (`8b1e668`)

The 124 definitions already fall into clear clusters by line range. The largest single definitions are
`_run_review_loop_iterations` (776 lines), `PipelineEngine` (335), `run_execute_stage` (306), `run_review_stage` (259),
`post_pr_review_consensus` (200) and `check_pr_mergeability` (193).

## Scope

### 1. Turn `flow.py` into a `flow/` package, moving code only

No function or class body changes. Target layout, by cluster:

| Module                         | Definitions moved (current line range)                                                                                                                                                                             |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `flow/context.py`              | `FlowStage`, `StageStatus`, `StageResult`, `FlowContext` (152–471)                                                                                                                                                 |
| `flow/checkpoint.py`           | `_migrate_v0_to_v1`, `migrate_checkpoint_data`, `_support_legacy_repo_dir`, `FlowCheckpoint`, `get_default_checkpoint_path`, `save_checkpoint`, `load_checkpoint` (262–577)                                        |
| `flow/ledger_reconcile.py`     | `ConflictResolutionError` through `_resolve_conflicting_ledger` (585–783)                                                                                                                                          |
| `flow/stage_conflicts.py`      | `check_and_resolve_stage_conflicts` (786–907)                                                                                                                                                                      |
| `flow/github/pr.py`            | `_resolve_commit_ref`, `check_pr_mergeability`, `format_review_git_trailers`, `generate_semantic_pr_metadata`, `create_or_update_pr` (910–1503)                                                                    |
| `flow/github/ci.py`            | `probe_ci_checks`, `resolve_ci_registration_timeout`, `_wait_for_ci_registration`, `_wait_for_pending_ci`, `_ci_green`, `_extract_failed_ci_check_names`                                                           |
| `flow/github/review_post.py`   | `post_pr_review_consensus` (1506–1705)                                                                                                                                                                             |
| `flow/intent_questions.py`     | `validate_intent_questions` (1708–1812)                                                                                                                                                                            |
| `flow/dispatch.py`             | `recorded_test_pass_rate`, `_test_evidence`, `_get_dispatcher`, `_dispatch_role`, `_stage_failure` (1829–1911)                                                                                                     |
| `flow/git_refs.py`             | fetch, branch, child-branch, ledger-reader and execution-ref helpers, `_fetch_branch_prefix_error` through `_execution_effective_diff` (1914–2249)                                                                 |
| `flow/stages/intent.py`        | `_reused_intent_conflict`, `run_intent_stage` (2257–2430)                                                                                                                                                          |
| `flow/stages/plan.py`          | `run_plan_stage`, `_plan_budget_decision`, `_format_entropy`, `_over_budget_failure` (2438–2654)                                                                                                                   |
| `flow/stages/decomposition.py` | `_sub_intent_depth` through `_run_decomposed_plan` (2657–2879)                                                                                                                                                     |
| `flow/stages/execute.py`       | `failed_partial_head`, `_resumable_partial_branch`, `run_execute_stage`, `_warn_ledger_failure` (2882–3243)                                                                                                        |
| `flow/review/workspace.py`     | `reviewers_sandboxed`, `review_persist_enabled`, `review_session_volume_name`, `ReviewWorkspaceSession` (3451–3592)                                                                                                |
| `flow/review/records.py`       | `_refused_review_result`, `_bounded_error_context`, `_posting_failure_context`, `record_review_action`, `_worst_severity` through `_record_infrastructure_findings`, `render_reviewer_summary_line`                |
| `flow/review/ensemble.py`      | `_resolve_reviewed_target`, `_semantic_pr_text`, `_review_base_ref`, `_ensemble_iteration`, `_dispatch_review_ensemble` (3764–3880)                                                                                |
| `flow/review/resolver.py`      | `ResolverOutcome`, `ResolverInput`, `_dispatch_review_resolver`, `_augment_pr_text_with_rejected`, `_filter_adjudicated_findings`, `_lookup_introducing_action_id`, `DispositionRecorder`, `_invoke_resolver_pass` |
| `flow/review/loop.py`          | `_loop_status`, `run_review_loop`, `_run_review_loop_iterations`, `_reviewers_objected`, `_review_window`, `_run_engine_review_loop`, `review_loop_approved`, `review_summary_lines`, `run_review_loop_cli`        |
| `flow/stages/review.py`        | `_checkout_execution_branch`, `run_review_stage` (5100–5418)                                                                                                                                                       |
| `flow/stages/calibrate.py`     | `_commit_stage5_reconciliation`, `_commit_stage5_promoted_artifacts`, `run_calibrate_stage` (5520–5797)                                                                                                            |
| `flow/pipeline.py`             | `PipelineEngine`, `run_flow_pipeline` (5805–6160)                                                                                                                                                                  |

Module-level imports, constants and loggers go to the module that uses them. Shared constants go in `flow/constants.py`.
The planner should confirm the exact boundaries against the inventory at plan time, keeping each cluster together and
avoiding import cycles between submodules.

### 2. Keep every caller working

- `flow/__init__.py` re-exports every public name and every private name that other modules or tests import today, so
  the 25 modules that import from `sandbox_executor.flow` need no changes in this PR.
- The 269 `mock.patch("sandbox_executor.flow.<name>")` targets in the tests move to the module that now defines (or
  looks up) each name. Patching the re-export is not enough, because code in a submodule looks names up in its own
  namespace.

### 3. Prove it is only a move

Add a test (or a review-evidence script under `scripts/`) that parses `flow.py` at the merge base and every module in
the new package, and compares `ast.dump` of each function and class body, keyed by qualified name. It must report zero
differences and zero missing or extra definitions. Reviewers verify this check, the re-exports and the patch targets,
rather than re-reading 6,000 moved lines.

### 4. Split the tests to match

Split `tests/test_flow.py` into `tests/flow/test_<module>.py` mirroring the new layout. The test count stays the same or
grows, and the full suite passes via `uv run pytest`.

### 5. Stop it growing back

Add a hygiene check that fails when a `flow/` module grows past its recorded line count (a ratchet that only lets sizes
shrink), with a per-module budget file. Several modules start above the 200-line guideline. The ratchet stops them
growing while follow-up beans decompose them.

### 6. Document the map

Update `docs/architecture.md` with the module map and a one-line responsibility per module.

## Touch set

`apps/sandbox-executor/src/sandbox_executor/flow.py` (deleted), the new `flow/` package,
`apps/sandbox-executor/tests/test_flow.py` (split into `tests/flow/`), the hygiene check and its budget file,
`docs/architecture.md`.

## Dependencies and sequencing

- **Run alone.** No other flow PR touching `flow.py` or `test_flow.py` may be open while this runs. Start it right after
  Bean 0149 (PR #146) merges, and hold Beans 0252 and 0253 until it lands.
- **Unblocks parallel work.** Once it lands, 0253 touches only `flow/stages/calibrate.py` and `flow/git_refs.py`, and
  0252 only `flow/review/resolver.py` and `flow/review/loop.py`, so they can run concurrently. It also unblocks the
  decomposition lanes from Bean 0177: 0189 (launcher module), 0190 (checkpoint and ledger reconciliation), 0191 then
  0192 (GitHub adapter, `ReviewLoop` class), 0193, 0194 and 0197. Bean 0192 is the natural home for breaking up
  `_run_review_loop_iterations` (776 lines).
- Supersedes Bean 0187.

## Acceptance criteria

1. `flow.py` no longer exists. `sandbox_executor.flow` is a package, and every existing import of it still resolves.
2. The AST comparison reports zero body differences and zero missing or extra definitions.
3. `tests/test_flow.py` is split into `tests/flow/`, with an equal or higher test count, and `uv run pytest` passes.
4. `uv run task lint` and `uv run task lint-docs` pass, and the new size ratchet passes at the recorded baseline.
5. No behaviour change: all CI checks pass, and the next flow run uses the new package unchanged.

## Notes

- Target repository changes in `holon-agentic-coder` must be delivered through the 5-stage Holon flow.
- Stage 3 output is large. Set `HOLON_STAGE_BUDGET_EXECUTE_MINUTES` generously for this run.
- The intent JSON must not mention bean IDs or harness paths, because it is copied into `intents.jsonl`.

## Resolution

Delivered via [PR #147](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/147) and merged into `main`
(`7258f61`, 2026-11-09T03:51:32Z):

- **Package split**: `flow.py` (6,159 lines) replaced by a `sandbox_executor.flow` package of cluster modules
  (`context`, `checkpoint`, `ledger_reconcile`, `stage_conflicts`, `github/`, `dispatch`, `git_refs`, `stages/`,
  `review/` including a new `review/cli.py`, `pipeline`, `constants`). `flow/__init__.py` re-exports every name, so
  callers are unchanged. 78 files, +15,884 / −12,772.
- **Proof of move**: `tests/flow/test_move_proof.py` and `tests/flow/move_proof.py` compare `ast.dump` of every
  definition against the original `flow.py` blob, with zero differences. `tests/flow/test_patch_targets.py` blocks
  package-level `mock.patch` targets, and `tests/flow/test_package_exports.py` checks the re-exports.
- **Tests**: `tests/test_flow.py` split into `tests/flow/`, 293 test functions against 280 before. CI 11/11 green.
- **Size ratchet**: `scripts/check_flow_module_budgets.py` with `apps/sandbox-executor/flow_module_budgets.json`, run by
  lint. `docs/architecture.md` has the module map.
- **Holon flow traversal**: all 5 stages on `claude-agent` / `claude-opus-5-5`. Execute took 21.2 min. Consensus came at
  iteration 4 and again 3/3 at iteration 5, after a resume. Calibration: predicted EV 27.39, actual −32.01 (ΔEV −59.40).
  The actual figure is distorted by Bean 0257 (`halted_for_human` counted as `p_success=0`) and Bean 0253 (`/calibrated`
  was cut from the pre-resolver head `377e17e`, so it was merged into the PR with an ordinary merge commit).
- **Known residuals**: the resolver crashed in iterations 2 and 3 because `uv` is missing from the agent image, which
  lost those fixes and made the posted summary claim 3/3 at iteration 4 (Bean 0258). The open docs nit (the
  `flow/stage_conflicts.py` docstring and the architecture map say "pre-push" when the check runs before each stage) is
  left for a follow-up flow.
