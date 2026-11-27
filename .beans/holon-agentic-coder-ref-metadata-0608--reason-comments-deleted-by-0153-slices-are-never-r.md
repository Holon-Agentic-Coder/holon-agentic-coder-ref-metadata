---
# holon-agentic-coder-ref-metadata-0608
title: "Reason comments deleted by 0153 slices are never restored as why comments"
status: in-progress
type: bug
priority: high
tags:
  - self-explaining-code
  - holon-flow
created_at: 2026-11-27T04:43:38Z
updated_at: 2026-11-27T23:07:00Z
---

## Evidence (audit 2026-11-27T04:43Z, PRs #396, #393, #392, #390, #389, #385, #384, #382, #383, #380)

- Removed comment lines that read as reasons (keywords because, so that, otherwise, must, avoid, never, race, ensure) in
  the nine slice diffs: 10, 2, 4, 88, 16, 2, 19, 1, 6, about 148 lines. A heuristic; none of the PR bodies reports how
  many reasons were deleted, so the true count is **not measured**.
- `# why:` lines added: 37, 23, 37, 242, 62, 8, 98, 8, 40; no `# why:` line removed. Added counts include docstring
  reasons, so they do not show which deleted reasons survived.
- Bean 0153 already records deletions per slice (9 in one slice, "Lazy:" import reasons dropped in #401) but no restore
  slice or bean exists: grep of beans for restore finds nothing.

## Goal

1. Measure: a script compares removed comment text against added `# why:` text per merged slice and lists removed
   reasons with no counterpart (file, line, text).
2. Restore: one flow intent per package re-adds the lost reasons as `# why:` where the code cannot show them.
3. Prevent: the 0153 intent template tells the planner to keep each reason as `# why:` and the PR body to report reasons
   kept and deleted.

## Acceptance

- [ ] The list of unmatched removed reasons exists for every merged 0153 slice.
- [ ] Each entry is restored or marked as shown by the code, with the reason.
- [ ] New slice PR bodies report reasons kept and deleted.

## Notes

- **Progress (2026-11-27)**: [PR #417](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/417) (`ea7a43fa`,
  `measure-deleted-why-comments`) merged into `main`: added `scripts/measure_deleted_why_comments.py` and unit tests in
  `apps/sandbox-executor/tests/test_measure_deleted_why_comments.py` scanning merged self-doc diffs for removed reason
  comments without matching `# why:` restorations. Keeping `status: in-progress` for the remaining restore and
  template-prevention slices.
- **Slice 2 (`hac-restore-why-tests`):** Completed 5-stage Holon flow (`antigravity-agent` / `gemini-4-neon`), awaiting
  human maintainer merge:
  - **PR**: [PR #454](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/454)
  - **Branch**: `I-1795817852-hac-restore-why-tests/P-1795817878-ANA-G4N/E-1795818137-ANA-G4N/_`
  - **Worktree**: `apps/holon-agentic-coder/flow-hac-restore-why-tests`
  - **Checkpoint**:
    `apps/holon-agentic-coder/flow-hac-restore-why-tests/.holon/flow/checkpoint-hac-restore-why-tests.json`
  - **Consensus**: `APPROVED` (Reviewer 1 APPROVED 0/0/0, Reviewer 2 APPROVED 0/0/0, Reviewer 3 APPROVED 0/0/0)
  - **CI Status**: `success` (16 passed, 0 failed, 0 other; `MERGEABLE`, `CLEAN`)
  - **Calibration**: Included in PR diff
    (`plans/I-1795817852-hac-restore-why-tests/P-1795817878-ANA-G4N_calibration.md`), Predicted EV: `35.32`, Actual EV:
    `40.82`, `ΔEV`: `+5.50`
- **Slice 3 (`hac-restore-why-src-batch1`):** Completed 5-stage Holon flow (`antigravity-agent` / `gemini-4-neon`),
  awaiting human maintainer merge (also updates `tests/test_self_doc_modules.py` to `allow_why=True`, unblocking Slice 4
  on merge):
  - **PR**: [PR #455](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/455) (`79ed5987`)
  - **Branch**: `I-1795819107-hac-restore-why-src-batch1/P-1795819130-ANA-G4N/E-1795819432-ANA-G4N/_`
  - **Worktree**: `apps/holon-agentic-coder/flow-hac-restore-why-src-batch1`
  - **Checkpoint**:
    `apps/holon-agentic-coder/flow-hac-restore-why-src-batch1/.holon/flow/checkpoint-hac-restore-why-src-batch1.json`
  - **Consensus**: `APPROVED` (3/3 unanimous iter 1: Reviewer 1/2/3 APPROVED 0/0/0)
  - **CI Status**: `success` (16/16 passed; `MERGEABLE`, `CLEAN`)
  - **Calibration**: Included in PR diff
    (`plans/I-1795819107-hac-restore-why-src-batch1/P-1795819130-ANA-G4N_calibration.md`), Predicted EV: `44.30`, Actual
    EV: `51.83`, `ΔEV`: `+7.52`
- **Slice 4 (`hac-restore-why-launcher-batch`):** Parked after Stage 3 halt (`CF-0081`, `a7a913e1`) because
  `apps/sandbox-executor/tests/test_self_doc_modules.py:221` on `main` calls `find_disallowed_comments()` with
  `allow_why=False`, failing tests on restored `# why:` comments in all 7 governed launcher modules (`empty_diff` after
  executor discarded edits). Worktree `apps/holon-agentic-coder/flow-hac-restore-why-launcher-batch` and checkpoint
  preserved for resume/re-sync once `allow_why=True` lands on `main` (`PR #455` / follow-up).
- **Slice 5 (`hac-restore-why-cli-entrypoint`):** Launched `todo/intent-0608-restore-why-cli-entrypoint.json`
  (`todo/intent-coverage-0608.json`) restoring or documenting all 10 unmatched removed reason entries across
  `claude_keychain.py`, `cli/commands/execute.py`, `cli/commands/review_fetch.py`, `config_env_secrets.py`,
  `entrypoint/executor/outcome.py`, `entrypoint/executor/sub_intents.py`, `entrypoint/git_locks.py`,
  `entrypoint/rejected_attempt.py`, and `entrypoint/taken_ids.py` (all within 350 lines).

## Resolution
