---
# holon-agentic-coder-ref-metadata-0152
title: "Audit long files and decompose oversized functions (flow.py and cli.py first)"
status: todo
type: task
priority: high
tags:
  - code-smell
  - refactor
  - concurrency
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-10-25T07:35:41Z
updated_at: 2026-10-25T07:35:41Z
---

## Problem

Long files are a code smell. Here the length comes mostly from functions that were never decomposed, not from files
holding too many separate concerns. That is especially true of `flow.py` and `cli.py`. Almost every recent flow PR (#90,
#93, #94, #95, #96) changed both, so concurrent flows kept conflicting and each merge forced another review round.
Splitting the files without decomposing their functions would only move the problem.

### Audit (2026-10-25, AST pass over `origin/main`: holon-agentic-coder `b3e2727`, holon-coherence `acbe924`)

**holon-agentic-coder:** 33 source files (20,763 lines), 458 functions. 74 are over 50 lines, 36 over 100 and 9
over 200.

| File                                             | Lines | Functions | Longest function                 | Functions >80 lines | Lines inside them |
| ------------------------------------------------ | ----- | --------- | -------------------------------- | ------------------- | ----------------- |
| `sandbox_executor/flow.py`                       | 4434  | 81        | `run_review_loop` (475)          | 15                  | 2789 (63%)        |
| `sandbox_executor/cli.py`                        | 2757  | 47        | `main` (**1062**)                | 4                   | 1554 (56%)        |
| `sandbox_executor/entrypoint/executor.py`        | 1627  | 23        | `main` (729)                     | 4                   | 1079 (66%)        |
| `sandbox_executor/calibration.py`                | 1520  | 23        | `parse_actual_metrics` (226)     | 5                   | 853               |
| `sandbox_executor/token_reduction/mitm_addon.py` | 1359  | 36        | `extract_sse_token_counts` (193) | 6                   | 704               |
| `sandbox_executor/ledger.py`                     | 793   | 22        | 122                              | 2                   | 203               |

Longest functions:

- `cli.py`: `main` (1062), `run_docker_container` (221), `setup_token_reduction_proxy` (186).
- `entrypoint/executor.py`: `main` (729).
- `flow.py`:
  - `run_review_loop` (475)
  - `build_pr_review_consensus_report` (303)
  - `run_execute_stage` (265)
  - `run_review_stage` (235)
  - `check_pr_mergeability` (192)
  - `post_pr_review_consensus` (178)
  - `run_calibrate_stage` (159)
  - `generate_semantic_pr_metadata` (151)
  - `run_plan_stage` (150)
  - `check_and_resolve_stage_conflicts` (149)
- `entrypoint/planner.py`: `main` (252).
- `calibration.py`: `parse_actual_metrics` (226), `generate_calibration` (164), `run_calibrate` (159).
- `knowledge/`: `index.sync_ledger_incremental` (196), `promotion.evaluate_action_promotion` (178).

Tests mirror this: `test_flow.py` 3952 lines, `test_token_reduction.py` 3725, `test_executor.py` 3351,
`test_cli.py` 1836.

**holon-coherence:** 26 source files (9,452 lines), 225 functions. 38 are over 50 lines, 15 over 100 and 4 over 200.

- `mitm_addon.py` has 2348 lines, including `render_dashboard_html` (379), `request` (209) and `response` (187).
- `cli.main` is 349 lines.
- `commands/start.handle_start` is 203 lines.
- `commands/ab_test.py` has 900 lines.
- `tests/test_cli.py` has 3679 lines.

**Duplication across the repositories:** holon-agentic-coder still ships `token_reduction/mitm_addon.py` and
`payload_cleaner.py` while holon-coherence has its own copies, and both contain the same 193-line
`extract_sse_token_counts`. This looks like an unfinished extraction of token reduction into holon-coherence.

## Scope

1. **Decompose before splitting.** Break every function over 100 lines into named, single-purpose, separately tested
   helpers. Go in this order: `cli.main` (argument parsing, then one handler per command), `executor.main`,
   `run_review_loop`, `build_pr_review_consensus_report`, the `run_*_stage` functions, then the rest of the list.
   Behaviour stays unchanged, and the existing suite, the URL fuzz tests and the `gh` write guard stay green.
2. **Then split the modules along the new seams.**
   - `flow.py`: one module per stage (intent, plan, execute, review, calibrate), plus shared context, ledger and guard
     helpers.
   - `cli.py`: one module per command group (`intent`, `plan`, `execute`, `flow`, `review-loop`, `calibrate`, `doctor`),
     plus the shared parser, runner resolution and credential plumbing.
   - Keep thin re-exports so imports don't break. Split the big test files to match.
3. **Add a lint gate:** a function-length or complexity limit (for example ruff `PLR0915`/`C901`, or a max-statements
   rule), applied to new and changed code with a baseline for the remainder. This stops the smell coming back.
4. **Resolve the token-reduction duplication:** pick one owner (holon-coherence) and remove or import the other copy.
   This needs a decision; record it in the bean before doing the work.
5. **Run each step as its own Holon flow PR** on the affected repository, landing each one while no other flow PR is
   open on the same files. Bean 0151 (touch-set admission) enforces that once it exists.

## Notes

- Re-run the audit after each step and add the numbers here, so progress is measured.
- The audit script (an `ast` pass for file length, function count, longest function and lines inside functions over 80
  lines) should be committed with the lint gate in step 3, inside the target repository.
- Related: Bean 0151 (planner touch sets with a hard block on overlapping concurrent flows). Decomposition makes touch
  sets finer-grained, so more flows can run in parallel.
