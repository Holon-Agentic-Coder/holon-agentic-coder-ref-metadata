---
# holon-agentic-coder-ref-metadata-0287
title:
  "An interrupted Stage 3 leaves uncommitted edits in the mounted worktree, so the resume refuses to start and the work
  is lost"
status: completed
type: bug
priority: high
tags:
  - flow
  - execute
  - resume
  - holon-agentic-coder
created_at: 2026-11-12T05:30:00Z
updated_at: 2026-11-12T05:30:00Z
---

## Problem

The executor writes straight into the mounted host worktree. When a session or stage dies mid-run (limit hit, killed
container), its edits stay uncommitted. The next `holon flow --checkpoint ... --from-stage execute` then fails within
seconds: `validate_mounted_workspace` raises
`mounted workspace ... has uncommitted changes, which are kept on the host; commit, stash or discard them in the host worktree before executing`.
Resume already looks for partial work
(`Stage 3 resume: no failed execution branch carries partial work; starting from the plan tip`) but only finds committed
work, so interrupted edits are never picked up. Seen 2026-11-12 on the `stubfetch` flow (Bean 0286): three resumes
failed on leftovers (a half-written network guard in `conftest.py` and `network_guard.py`, then a
`test_decomposition.py` stub), and each time the work was backed up and discarded by hand.

## Action

Run through the Holon flow. Do not expect a clean worktree on resume: when a stage is interrupted, or resume finds a
dirty worktree, commit the leftovers onto the failed execution branch as a partial-work commit (excluding the ledger
rows and execution report the engine owns), so the existing partial-work lookup finds them and the executor continues
from them instead of the plan tip. The executor still re-runs its checks and the review loop sees the final diff, so the
partial work is vetted before merge; the commit keeps the audit trail that discarding loses. Cover: dirty tracked and
untracked files, no leftovers (unchanged behaviour), a failed branch that already has partial commits, and the
ledger-only dirty case.

## Notes

Touches `flow` and the executor entrypoint (`execution_workspace.py`), so it must not run concurrently with another flow
on those files.

## Resolution

Delivered via [PR #178](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/178) and merged into `main`
(`ebfa3bb`):

- **Fix**: a Stage 3 resume over a worktree with uncommitted leftovers commits them as a labelled partial-work commit on
  the failed execution branch (engine-owned ledger and report files excluded) and continues from them, instead of
  refusing to start. The commit is recorded in the existing ledgers; a clean resume is unchanged.
- **Review**: 3/3 ensemble approval in 4 iterations; one `COMMENTED` review; CI green on the final head.
- **Calibration**: `plans/P-1794478317-4eb07fff-claude-agent-claude-sonnet-5-5_calibration.md` in the PR; EV predicted
  37.48 vs actual 52.17.
- **Flow**: all five stages traversed through `holon flow`, uninterrupted.
