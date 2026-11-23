---
# holon-agentic-coder-ref-metadata-0383
title: "Stage 5 waits for CI twice and always overruns its 10-minute budget; no per-step timing breakdown"
status: todo
type: feature
priority: high
tags:
  - flow
  - stage-5
  - ci
  - performance
  - holon-agentic-coder
created_at: 2026-11-23T12:40:00Z
updated_at: 2026-11-23T12:40:00Z
---

## Problem

On PR #260 (2026-11-23) Stage 5 took 22.5 minutes against its 10-minute budget, and the calibration work itself took 14
seconds. From the flow log (UTC):

- 12:01:29 to 12:13:26 (11 min 57 s): the merged-head CI gate waits for CI on the head that the conflict gate's merge of
  `main` and the ledger commit produced.
- 12:13:26 to 12:13:40 (14 s): calibration report, reconciliation, knowledge promotion (three commits).
- 12:14:06 to 12:24:00 (9 min 54 s): the final-head check waits for CI again, because the calibration commits moved the
  head.

So Stage 5 is two full CI runs back to back. The same overrun was logged on PR #250, #251, #253, #256 and #258 ("ran
10.6 to 10.9 min against its 10 min budget") and the flow keeps the success, so the budget has no meaning. The
maintainer noticed the gap from the PR timeline and had no way to see where the time went.

## Goal

1. **One CI wait instead of two (maintainer decision needed).** After a merge of the target, calibrate at once, push the
   merge and the calibration commits together, and wait for CI once on the final head; a failed check withdraws the
   consensus as today. This relaxes PR #250's rule that no calibration commit is pushed before CI passed on the merged
   head.
2. **No full CI for calibration-only commits.** Commits touching only `plans/`, `executions/` and `holon-knowledge/`
   cannot change a test result: path filters let the workflows finish in seconds for them (or the engine treats such
   commits as bookkeeping and reuses the previous head's result).
3. **A budget that means something.** Stage 5's budget covers its own work; time spent waiting for external CI is
   accounted separately (it already has a 1800 s CI wait budget) and does not produce an overrun warning.
4. **Timing breakdown.** Every flow summary and the PR's final comment show time per stage split into agent turns, CI
   waits, git/merge work and idle time between resumes; `holon flow --timeline <checkpoint>` prints the same from the
   checkpoint log. (A harness-side script over the checkpoint logs can provide this before the engine does.)
