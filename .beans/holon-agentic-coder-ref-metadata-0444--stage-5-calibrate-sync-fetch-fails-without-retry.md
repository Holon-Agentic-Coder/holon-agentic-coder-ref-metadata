---
# holon-agentic-coder-ref-metadata-0444
title: "Stage 5 calibrate_sync._fetch_execution_branch fails on transient SSH error without retry"
status: completed
type: bug
priority: normal
tags:
  - flow
  - stage-5
  - reliability
  - git
  - holon-agentic-coder
created_at: 2026-11-25T03:08:00Z
updated_at: 2026-11-26T13:13:04Z
---

## Problem

In Stage 5 (`sandbox_executor/flow/stages/calibrate.py:266`), `_prepare_execution_branch` calls
`calibrate_sync.sync_execution_ref` $\rightarrow$ `_fetch_execution_branch` (`calibrate_sync.py:43-50`) outside
`call_with_retries` (`calibrate.py:279`). Whenever `git fetch origin` hits a transient SSH/keychain/network failure
while `refs/remotes/origin/<branch>` already exists locally, Stage 5 immediately aborts with `CalibrationSyncError`
instead of retrying with short backoff.

## Evidence (2026-11-25T00:28Z–02:54Z fifth-merge audit)

- On `touch-set-self-doc` (`PR #298`, checkpoint
  `apps/holon-agentic-coder/flow-touch-set-self-doc/.holon/flow/checkpoint-touch-set-self-doc.json`), Stage 5 failed
  after `6 s` at `2026-11-25T00:30:27Z`:
  ```text
  Calibrate stage failed: could not fetch origin/I-1795565481-touch-set-self-doc/P-1795565501-ANA-G4N/E-1795565805-ANA-G4N/_ (host fetch of '...' through remote 'origin' failed: git@github.com: Permission denied (publickey).
  fatal: Could not read from remote repository.
  ```
- Resumed `1.37 min` later (`00:31:52Z`) with no host or key changes and fetched/calibrated cleanly (`00:36:11Z`),
  proving the failure was transient.

## Proposed change

1. Wrap `fetch_base` in `_fetch_execution_branch` (`calibrate_sync.py:43-50`, or `host_remote.fetch_base` for transient
   SSH/network errors) with bounded retry + short backoff (e.g., 3 attempts over `~10–15 s`) before raising
   `CalibrationSyncError`.
2. Add a hermetic unit test in `tests/flow/test_calibrate_sync.py` verifying that a transient `HostRemoteError` on the
   first fetch attempt succeeds on retry without failing Stage 5.

## Expected gain

Prevents transient SSH/network fetch hiccups from halting Stage 5 and forcing a stop/resume cycle (`~1.5 min` wasted per
incident).

## Cost

Small: tiny retry wrapper in `calibrate_sync.py` + unit test, delivered via the Holon flow.

## Notes

- Target repo change through the Holon flow (`holon-agentic-coder`).
- Related: Bean `0424` (Stage 4 transient DNS/Docker retries), Bean `0393` (preflight retry).

## Flow

In progress 2026-11-26: flow `fetch-execution-branch-retry` (intent
`todo/intent-0444-fetch-execution-branch-retry.json`, log `todo/flow-fetch-execution-branch-retry.log`). Scope:
`flow/calibrate_sync.py` (the bean's `stages/calibrate.py` path is stale), new `flow/calibrate_fetch_retry.py`, new test
file.

## Resolution

Delivered via [PR #340](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/340) and merged into `main`
(`72de702c`):

- **Key Architectural Deliverables**: the execution-branch fetch in Stage 5 (`_fetch_execution_branch`, via the new
  `flow/calibrate_fetch_retry.py`) makes three attempts with short backoff before raising `CalibrationSyncError`, so a
  transient SSH or network failure no longer aborts calibration.
- **Verification & Tests**: hermetic retry test in `apps/sandbox-executor/tests/test_calibrate_fetch_retry.py`; a
  transient fetch failure succeeds on a later attempt.
- **Holon Flow Traversal**: all 5 stages completed for slug `fetch-execution-branch-retry`; the flow worktree and its
  `I-1795693496-fetch-execution-branch-retry/*` branches were removed after merge (post-PR-merge step 4). Four
  uncommitted review-loop ledger rows in that worktree were saved to
  `/private/tmp/claude-501/-Users-thomashan-git-holon-agentic-coder-ref-metadata/f956a41e-6830-4ee3-9257-8c114a4af5b9/scratchpad/fetch-execution-branch-retry-worktree-ledger.patch`
  before removal.
