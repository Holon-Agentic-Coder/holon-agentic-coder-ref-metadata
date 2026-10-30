---
# holon-agentic-coder-ref-metadata-0213
title: "Reflect review-loop skill rules into native Review Loop Holon Agent"
status: todo
type: task
priority: high
tags:
  - review-loop
  - prompts
  - conflict-resolution
  - holon-agentic-coder
created_at: 2026-10-30T03:02:00Z
updated_at: 2026-10-30T03:02:00Z
---

## Problem

The harness review loop skill (`.agents/skills/pr_review_loop/SKILL.md`) has evolved critical operational invariants
across recent review loop iterations:

1. **Mandatory Target-Branch Conflict Gate**: Prior to posting an approved consensus review to GitHub or executing Stage
   5 calibration, check `gh pr view <pr> --json mergeable,mergeStateStatus`. If `mergeable == "CONFLICTING"` or
   `mergeStateStatus == "DIRTY"`, immediately fetch `origin/main`, merge, and resolve conflicts.
2. **Fast Ledger-Only Conflict Resolution**: When conflicts are strictly confined to `holon-knowledge/ledger/*.jsonl`,
   interleave or append entries chronologically by `created_at`, verify valid JSON syntax, and skip test suite
   execution.
3. **Review the Increment (Bean 0170)**: Reviewers evaluate newly added/modified code relative to previous iterations
   rather than re-litigating unchanged code or re-raising deferred Nits.
4. **Automatic Model Fallback Ladder**: Step down model tiers (`pro` -> `flash-medium` -> `flash` / `opus` -> `sonnet`
   -> `haiku`) when encountering rate limits or quota exhaustion.
5. **Stage 5 Pre-Merge Calibration**: Stage 5 calibration is a pre-merge step executed by the loop, producing
   `/calibrated` and incorporated into the PR head diff before human merge.
6. **Zero Synthetic Data (Rule 10)**: Official reviews and scorecards derive exclusively from authentic data.
7. **Strict Test Execution Tooling (Rule 13)**: Tests execute strictly via `uv run pytest`; never `unittest` or
   `PYTHONPATH`.

However, the native containerised Review Loop Holon Agent in `holon-agentic-coder`
(`holon-config/prompts/review_loop.template.md` and
`apps/sandbox-executor/src/sandbox_executor/entrypoint/review_loop.py`) does not yet explicitly reflect these rules.

## Scope

1. **Update `holon-config/prompts/review_loop.template.md`**:
   - Add explicit sections detailing the target-branch conflict resolution gate, ledger-only fast resolution procedure,
     incremental review rules, and Stage 5 pre-merge calibration requirement.
   - Maintain documentation integrity and format with Prettier.
2. **Update `apps/sandbox-executor/src/sandbox_executor/entrypoint/review_loop.py` & `flow.py`**:
   - Ensure the conflict resolution gate is verified and executed before posting approved reviews and before invoking
     Stage 5 calibration.
3. **Tests**:
   - Verify prompt template unit tests in `apps/sandbox-executor/tests/test_prompt_templates.py` and review loop tests
     in `apps/sandbox-executor/tests/test_review_loop.py`.

## Notes

- Target repository: `holon-agentic-coder`.
- Must be executed via the 5-stage Holon flow (`holon intent` -> `plan` -> `execute` -> `review` -> `calibrate`).
- Target repository isolation (Rule 12): Prompt and code changes in `holon-agentic-coder` must not reference harness
  paths (`.beans/`, `todo/`, `.agents/`) or bean IDs.
