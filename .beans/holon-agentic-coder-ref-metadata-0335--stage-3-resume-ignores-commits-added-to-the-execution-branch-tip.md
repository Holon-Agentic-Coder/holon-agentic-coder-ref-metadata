---
# holon-agentic-coder-ref-metadata-0335
title: "A Stage 3 resume restarts from the ledger partial_head and ignores commits added to the execution branch tip"
status: in-progress
type: bug
priority: normal
tags:
  - flow
  - stage-3
  - resume
  - holon-agentic-coder
created_at: 2026-11-20T11:30:00+11:00
updated_at: 2026-11-20T12:05:00+11:00
---

## Problem

Seen on the `shortref` flow (Bean 0321), 2026-11-20. After a pre-push sync conflict, `origin/main` was merged by hand
into the execution branch (`E-1795088115-4e818090`, merge `58949669`) and pushed. The resume still failed on the same
conflict: the executor resumes from the `partial_head` in the latest ledger summary row for that execution, which still
named the step-3 commit before the merge, not the branch tip. It worked only after a new summary row
(`ledger_revision` 3) pointing `partial_head` at the merge commit was appended by hand. The failed attempt also left a
pushed execution branch, `E-1795130302-4856d0ac`, with no ledger row.

## Action

Through the Holon flow on `holon-agentic-coder`: when the execution branch tip descends from the recorded `partial_head`
(and from the plan tip), resume from the tip. Do not push an execution branch before its ledger row exists. Add a
hermetic test: record a partial head, add a merge commit on the branch, resume, and assert the executor starts from the
merge commit.

## Progress

- **2026-11-20:** Flow `resumetip` (holon-agentic-coder, claude-agent/claude-opus-5-5, combined with Bean 0331/0335)
  passed Stage 1 (`I-1795136616-resumetip/_`) and Stage 2 (`P-1795136633-CLA-CO5.5`, EV 39.61). Stage 3 admission
  refused: touch set overlaps PR #207 (`rescrash` flow) on `apps/sandbox-executor/flow_module_budgets.json`,
  `apps/sandbox-executor/src/sandbox_executor/flow/__init__.py`, `apps/sandbox-executor/tests/flow/test_admission.py`
  and `apps/sandbox-executor/tests/flow/stages/test_execute.py`. Not overridden; resume with `--from-stage execute` in
  `flow-resumetip` after PR #207 merges.

## Notes

- Related: Bean 0171 (partial-work salvage), Bean 0331 (plan tip moved by override records).
