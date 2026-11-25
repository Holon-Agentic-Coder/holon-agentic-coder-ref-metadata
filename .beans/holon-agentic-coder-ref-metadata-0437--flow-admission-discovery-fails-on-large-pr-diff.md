---
# holon-agentic-coder-ref-metadata-0437
title: "Stage 3 admission discovery stops the flow when gh pr diff exceeds 300 files"
status: completed
type: bug
priority: high
tags:
  - holon-flow
  - admission
  - overlap
created_at: 2026-11-24T23:27:00Z
updated_at: 2026-11-25T05:23:00Z
---

## Problem

During Stage 3 admission for the 0405 flow (`workspace-survival-job-parallel`), the in-flight flow discovery ran
`gh pr diff 283` for the overlapping pull request (`I-1795425253-resolve-conflicts-in-flow`). GitHub answered HTTP 406
`diff exceeded the maximum number of files (300)`, so discovery failed and the wrapper stopped with "Stage 3 refused:
the flows in flight could not be discovered". The overlap was real (PR 283 touches `.github/workflows/test-unit.yml`),
but because discovery failed the wrapper did not poll the pull request (the overlap wait only runs on a touch-set
refusal), so the flow stopped instead of waiting for PR 283 to merge or close.

## Expected

Discovery should read the changed files through the paginated files API (`gh api repos/<repo>/pulls/<n>/files`) when
`gh pr diff` returns too-large, and a touch-set overlap should then take the overlap wait path.

## Notes

- Found 2026-11-24 while driving 0405 by hand; the flow was not hand-patched, the run stopped at execute with checkpoint
  at
  `apps/holon-agentic-coder/flow-workspace-survival-job-parallel/.holon/flow/checkpoint-workspace-survival-job-parallel.json`.
- Stage 3 refusal text: "the flows in flight could not be discovered: 'gh pr diff 283' failed".

## Resolution

Delivered via [PR #299](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/299) and merged into `main`
(`599630f8`, `2026-11-25T05:20:56Z`):

- **Deliverables**: Added the HTTP 406 (`too_large`) paginated REST `/pulls/{number}/files` fallback in
  `apps/sandbox-executor/src/sandbox_executor/flow/pr_changed_files.py` and wired it into
  `apps/sandbox-executor/src/sandbox_executor/flow/in_flight.py`, resolving the companion report in Bean `0433`.
- **Holon Flow Traversal**: All 5 stages (Intent -> Plan -> Execute -> Review Loop -> Calibration) completed on
  `I-1795566347-in-flight-pr-files-fallback`.
