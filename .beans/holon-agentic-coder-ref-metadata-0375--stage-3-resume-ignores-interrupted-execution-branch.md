---
# holon-agentic-coder-ref-metadata-0375
title: "Stage 3 resume ignores an interrupted execution branch that has commits but no ledger row"
status: completed
type: bug
priority: high
tags:
  - flow
  - stage-3
  - resume
  - holon-agentic-coder
created_at: 2026-11-23T07:36:00Z
updated_at: 2026-11-26T13:34:00Z
---

## Problem

When the host process dies during Stage 3 (session restart, 2026-11-23), the execution branch keeps the executor's
commits but has no `executions.jsonl` summary row. On resume the flow cannot continue from that work. Seen three times
in one day:

- **Bean 0174** (`document-env-variables-v2`): branch `…/E-1795413310-CLA-CO5.5/_` holds steps 1 to 5 (tip `eaaa5b16`)
  and an uncommitted change to its tracked evidence file `executions/E-1795413310-CLA-CO5.5.md`. Resume logged "no
  failed execution branch carries partial work; starting from the plan tip", then ran
  `git checkout -b …/E-1795419188-CLA-CO5.5/_ d254bb21`, which failed: "Your local changes to the following files would
  be overwritten by checkout". Stage 3 failed; nothing was salvaged.
- **Bean 0191** child 3: the first resume re-cut a new execution branch from the plan tip and ignored `E-1795406584`
  (steps 1 to 4 committed, suite green). The second resume ran a full new execution (`E-1795415159`), but the checkpoint
  still named an older execution id, so the flow exited 1 with "no executions.jsonl row" although the executor had
  succeeded.

The partial-work salvage only looks for an execution branch with a _failed_ ledger row; a branch whose host died has no
row at all.

## Goal

- Resume detects an execution branch of the current plan that has commits past the plan tip and no summary row, and
  adopts it: the executor continues from its tip (with the "partial work" prompt), and uncommitted tracked changes on it
  are committed as partial work first, never left to break a checkout.
- The checkpoint's execution branch/id is updated whenever Stage 3 starts or adopts an execution branch, so the
  post-execution ledger lookup uses the id the executor actually wrote.
- A dirty worktree never turns into an opaque `git checkout` exit 1: the stage reports which files block it.
- Tests: kill-and-resume fixtures for (a) commits and no row, (b) commits, no row and a dirty tracked file, (c) a second
  resume after a new execution id.

## Related

Bean 0374 (scratch files committed by the same interrupted runs). Workaround used on 2026-11-23: bean 0191 recovered
manually on the maintainer's instruction; bean 0174 restarted as a fresh `-v3` intent from current `main`.

## Notes

- Overlap: Bean 0397 (resume adopts a completed, pushed execution branch) is the same resume lookup for the complete
  case. This bean owns the shared branch-adoption code.

## Flow

2026-11-26: flow `resume-adopts-unrecorded-branch` (claude-agent, claude-opus-5-5) started; log
`todo/flow-resume-adopts-unrecorded-branch.log`.

2026-11-26: PR #345 approved by the 3-reviewer ensemble (iteration 2), calibrated, `MERGEABLE`/`CLEAN`; awaiting the
maintainer merge.

## Resolution

Delivered via [PR #345](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/345) and merged into `main`
(`1567b6b`):

- **Key Architectural Deliverables**: new `flow/unrecorded_branch_adoption.py` detects an execution branch of the
  current plan with commits past the plan tip and no `executions.jsonl` row and adopts it on Stage 3 resume;
  `flow/partial_head.py` and `flow/partial_salvage.py` commit uncommitted tracked changes as labelled partial work
  first; `flow/stages/execute.py` calls the new detection and updates the checkpoint's execution branch and id to the
  adopted branch; a checkout blocked by a dirty worktree reports the blocking file names.
- **Verification & Tests**: `tests/flow/stages/test_execute_resume_unrecorded_branch.py` (commits without row; commits
  without row plus dirty tracked file; second resume after a new execution id) and `tests/test_partial_salvage.py`. Rows
  with a success or failure summary keep their existing behaviour.
- **Holon Flow Traversal**: flow `resume-adopts-unrecorded-branch` (claude-agent, claude-opus-5-5) ran through plan,
  execute, review (ensemble approval at iteration 2) and calibration before the maintainer merge.
