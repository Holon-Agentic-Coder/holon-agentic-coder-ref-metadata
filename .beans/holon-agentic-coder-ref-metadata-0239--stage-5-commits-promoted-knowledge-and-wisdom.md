---
# holon-agentic-coder-ref-metadata-0239
title:
  "Stage 5 calibration commits and pushes promoted knowledge and wisdom artifacts to the `/calibrated` branch and PR"
status: completed
type: bug
priority: high
tags:
  - flow
  - stage-5
  - calibration
  - knowledge
  - wisdom
  - holon-agentic-coder
created_at: 2026-11-06T04:22:00Z
updated_at: 2026-11-06T08:16:00Z
---

## Problem

In `sandbox_executor.flow.run_calibration_stage()`, Stage 5 runs continuous learning pattern promotion via
`promote_pending_candidates()`:

```python
if os.path.exists(db_path):
    index_db = ActionIndexDatabase(db_path=db_path)
    promoted_candidates = promote_pending_candidates(
        index_db=index_db,
        kb_dir=os.path.join(repo_dir, "holon-knowledge/kb"),
        wb_dir=os.path.join(repo_dir, "holon-knowledge/wisdom"),
        min_trials=2,
        dry_run=context.dry_run,
    )
    if promoted_candidates:
        context.log(f"Stage 5 promoted {len(promoted_candidates)} knowledge/wisdom candidate(s).")
```

When candidates qualify for promotion, `promote_pending_candidates()` calls `persist_kb_fact()` and `persist_wb_rule()`,
writing JSON artifacts to `holon-knowledge/kb/` (e.g. `failure_modes/`, `patterns/`) and `holon-knowledge/wisdom/` (e.g.
`heuristics/`) in the local repository working tree.

However, the flow engine never stages or commits these files:

1. `_commit_stage5_reconciliation()` runs **before** `promote_pending_candidates()` and stages strictly
   `holon-knowledge/ledger/executions.jsonl`.
2. Following promotion, lines 5351–5359 execute `git push` on `context.calibrated_branch` and fast-forward the execution
   branch without running `git add` or `git commit` for `holon-knowledge/kb/` or `holon-knowledge/wisdom/`.
3. Consequently, all promoted knowledge and wisdom files remain as untracked files in the local working tree, are
   omitted from the `/calibrated` branch, and are never pushed to the PR head branch or merged into `main`.

## Decision

Commit and push promoted knowledge base and wisdom artifacts to the `/calibrated` branch and include them in the PR:

1. **Commit Promoted Knowledge in Stage 5**:
   - In `sandbox_executor.flow.run_calibration_stage()`, after `promote_pending_candidates()` completes:
     - If `promoted_candidates` is non-empty, stage the promoted directories:
       `run_git(["add", "holon-knowledge/kb", "holon-knowledge/wisdom"], cwd=repo_dir)`
     - Commit the changes onto the `/calibrated` branch:
       `run_git(["commit", "-m", "chore(calibration): promote knowledge base and wisdom heuristics", "--", "holon-knowledge/kb", "holon-knowledge/wisdom"], ...)`
     - Alternatively, sequence `promote_pending_candidates()` before or within the reconciliation commit so that all
       Stage 5 artifacts (ledger reconciliation row, knowledge facts, wisdom heuristics) are staged and committed
       together under `calibration_commit_env()`.
2. **Include in PR Head**:
   - Because `context.calibrated_branch` is pushed to origin and subsequently fast-forwarded into
     `context.execution_branch` (`run_git(["merge", "--ff-only", context.calibrated_branch])`), committing the
     knowledge/wisdom files to `/calibrated` automatically carries them into the PR head branch and PR diff when pushed.
3. **Empty / No-Op Protection**:
   - If `promoted_candidates` is empty or no files were modified, skip committing without raising an error.
4. **Hermetic Unit Tests**:
   - Add unit tests in `apps/sandbox-executor/tests/test_flow.py` (or `test_calibration.py`) asserting that when
     `promote_pending_candidates()` returns promoted items:
     - `git add` is called for `holon-knowledge/kb` and `holon-knowledge/wisdom`.
     - The commit is created on the calibrated branch and merged into the execution branch.

## Scope

1. `apps/sandbox-executor/src/sandbox_executor/flow.py`: Stage and commit `holon-knowledge/kb/` and
   `holon-knowledge/wisdom/` in `run_calibration_stage()`.
2. `apps/sandbox-executor/tests/test_flow.py`: Hermetic tests for Stage 5 knowledge/wisdom artifact committing.

## Resolution

Delivered via [PR #130](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/130) and merged into `main`
(`1619cec`):

- Added `_commit_stage5_promoted_artifacts()` helper in `flow.py` called immediately following
  `promote_pending_candidates()`.
- Automatically stages and commits any generated or updated files in `holon-knowledge/kb/` and `holon-knowledge/wisdom/`
  to the `/calibrated` branch.
- Fast-forwards the `/calibrated` commit into the PR head execution branch and pushes to `origin`, preserving all
  promoted heuristics and failure patterns in the PR diff and `main` branch history.
- Added comprehensive unit tests in `test_flow.py` asserting clean staging and committing when candidates qualify.
- Traversed all 5 stages of the Holon flow, passed 3/3 ensemble consensus review, and calibrated before merging.
