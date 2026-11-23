---
# holon-agentic-coder-ref-metadata-0213
title: "Reflect review-loop skill rules into native Review Loop Holon Agent"
status: completed
type: task
priority: high
tags:
  - review-loop
  - prompts
  - conflict-resolution
  - holon-agentic-coder
created_at: 2026-10-30T03:02:00Z
updated_at: 2026-11-20T14:05:06Z
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

## Progress & Resolution

- **Explicit User Instruction (2026-10-30)**: "the review loop agent doesn't have the output the skill has ... copy the
  skill prompt template into the review loop agent".
- Updated `holon-config/prompts/review_loop.template.md` on branch `task/0213-reflect-review-loop-skill-template`
  (commit `c6ffe46`):
  - Standard Review Output Schema updated to match the verified skill consensus template:
    - Consensus Approval format (`## ✅ Ensemble Consensus Review — APPROVED ({ensemble_size}/{ensemble_size})` with
      bulleted verification points for architecture, backward compatibility, test suite, quality gates, complexity
      ratchet, and 3-ledger provenance).
    - Changes Requested format (`## ❌ Ensemble Consensus Review — CHANGES REQUESTED (Iteration {iteration})` with
      findings table).
    - Closing notice: "Stage 5 calibration will be added to this PR before merge. Merging remains with the human
      maintainer."
  - Added core loop principles: Mandatory Target-Branch Conflict Gate, Fast Ledger-Only Conflict Resolution,
    Increment-Scoped Reviews (Bean 0170), and Stage 5 Pre-Merge Calibration.
  - Formatted cleanly with Prettier; verified all 8 tests pass in
    `apps/sandbox-executor/tests/test_prompt_templates.py`, and `uv run task lint` / `uv run task lint-docs` pass
    cleanly.
- Pushed branch `origin/task/0213-reflect-review-loop-skill-template`. Remaining entrypoint / flow wiring will follow
  once PR #116 merges.

## Audit (2026-11-20)

Done on `main`: "Mergeability first" and "Increment review" in `holon-config/prompts/review_loop.template.md`;
ledger-only conflict interleaving in code (`flow/github/merge.py`, `flow/ledger_interleave.py`). The old branch
`task/0213-reflect-review-loop-skill-template` never merged. Remaining: the explicit CONFLICTING/DIRTY gate before
consensus posting and Stage 5, the ledger-only fast-path procedure, the model fallback ladder, the zero-synthetic rule
and the `uv run pytest`-only rule in the template.

## Progress

- 2026-11-20: Started holon flow `review-report-ci-log-redaction` (claude-agent, claude-opus-5-5), combined with beans
  0261, 0213, 0234 and 0148.
- 2026-11-20: Flow `review-report-ci-log-redaction` finished all 5 stages: 3/3 consensus approval at review iteration 3,
  calibration report in the diff (EV predicted 39.45, actual 59.09, delta +19.64), final-head CI green. PR
  [#220](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/220) was merged by the maintainer at 14:03Z.

## Resolution

Delivered via [PR #220](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/220) and merged into `main`
(`9a5454bf`), as part of the combined flow `review-report-ci-log-redaction`:

- **Key Deliverables**: `holon-config/prompts/review_loop.template.md` now carries the review-loop skill rules: the
  mandatory target-branch conflict gate (`CONFLICTING`/`DIRTY`) before consensus posting and Stage 5, the ledger-only
  fast conflict path, increment-scoped reviews, pre-merge Stage 5 calibration, and the `uv run pytest`-only and
  zero-synthetic-data rules. Conflict gate wiring lands in `flow/review/conflict_gate.py` and
  `flow/review/conflict_merge.py`.
- **Verification & Tests**: `tests/test_prompt_templates.py`, `tests/flow/review/test_conflict_gate.py`,
  `tests/test_ledger_fast_conflict.py`.
- **Holon Flow Traversal**: Intent -> Plan -> Execute -> Review Loop -> Calibration completed (predicted EV 39.45,
  actual 59.09).
