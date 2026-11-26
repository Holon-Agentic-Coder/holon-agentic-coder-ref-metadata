---
# holon-agentic-coder-ref-metadata-0420
title: "A flow whose pull request is merged while it is running fails instead of finishing cleanly"
status: todo
type: bug
priority: high
tags:
  - flow
  - review
  - holon-agentic-coder
created_at: 2026-11-24T11:45:00Z
updated_at: 2026-11-24T11:45:00Z
---

## Problem

The flow `ledger-temp-worktree-cleanup` (Bean 0387, holon-agentic-coder PR #270) exited with code 1 after the pull
request had merged. The maintainer merged PR #270 through the merge queue at 2026-11-24T11:31:45Z (merge commit
`bfbd9f4e`) and GitHub deleted the remote head branch. The flow was still in its merged-head CI wait. The log
`todo/flow-ledger-temp-worktree-cleanup.log` shows:

```text
[11:37:53Z] Merged-head CI on c341f7845d34: failed; ... unit (ubuntu-latest) ...: failure
[11:37:55Z] Consensus withdrawn: CI failed on merged head c341f7845d34; restarting Stage 4 at iteration 1 (restart 1 of 3).
[11:38:04Z] [Review Loop] Skipping PR creation: could not verify the execution diff (fetching 'I-.../_' and
  'I-.../E-1795505480-CLA-CF5.2/_' from origin failed: fatal: couldn't find remote ref refs/heads/I-.../E-.../_).
[11:38:07Z] Stage 4 failed: Autonomous review halted: Refusing to create or update a PR ...: could not verify the
  execution diff
[11:38:07Z] Pipeline halted due to failure in stage 'review'.
```

The message is raised in `sandbox_executor/flow/review/loop.py` (line 246, the empty-diff guard that fetches the plan
and execution branches) and, for Stage 3, in `sandbox_executor/flow/stages/execute.py` (line 376). Neither checks
whether the pull request is already merged. The flow therefore treated a finished delivery as a failed review, left
calibration skipped ("calibration report not refreshed for the current head") and told the maintainer to resume a flow
that has nothing left to do. Its CI failure trigger (Bean 0419) made it re-enter Stage 4 for a pull request that no
longer existed.

## Goal

- At each Stage 4 and Stage 5 entry, and before any consensus withdrawal or Stage 4 restart, the flow queries the pull
  request state. A merged (or closed with a merge commit) pull request ends the loop.
- On a merged pull request the flow stops its remaining stages, records the outcome as merged (a ledger row and the
  checkpoint status, with the merge commit), and exits 0. It does not post a withdrawal, restart Stage 4 or print the
  manual resume hint.
- A missing remote branch for a merged pull request is not an error; a missing remote branch for an open pull request
  stays one.
- A regression test simulates a merge and branch deletion while the CI wait is in progress and asserts exit 0 and the
  merged outcome.

## Notes

- Related: Bean 0419 (the timing-gate failure that triggered the withdrawal), Bean 0376, Bean 0403.
- Calibration after a merge is a separate question; this bean only requires a clean exit and a recorded outcome.
