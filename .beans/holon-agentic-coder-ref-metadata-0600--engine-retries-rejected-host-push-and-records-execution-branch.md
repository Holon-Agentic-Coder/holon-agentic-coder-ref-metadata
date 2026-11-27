---
# holon-agentic-coder-ref-metadata-0600
title: "Engine retries a rejected host push and records execution_branch before pushing"
status: completed
type: bug
priority: high
tags:
  - holon-flow
  - git
  - resume
created_at: 2026-11-27T03:52:30Z
updated_at: 2026-11-27T11:48:04Z
---

## Evidence

- Flows self-doc-src-j, self-doc-src-g, 0574 and 0400 hit a remote push rejection at Stage 3 that names no reason:
  `! [remote rejected] <E-branch> -> <E-branch> (failed)`, preceded only by GitHub's "Create a pull request" hint.
- The engine keeps the commits on `refs/holon/recovery/E-...` and halts. A resume re-ran execute, which created a second
  E-branch under the same plan.
  - self-doc-src-j: two E-branches (E-1795749046, E-1795750182); the engine refused to continue with "ambiguous
    E-branches ... refusing to guess", and the checkpoint held `execution_branch: null`.
  - self-doc-src-g: the checkpoint had no `execution_branch` after the halt.

## Cause (investigated 2026-11-27)

- Not a ref-name or size limit: the branch name is 75 characters (limit 255), the pack is about 52 MiB, and the only
  repository ruleset targets the default branch.
- The same ref pushed under a throwaway name in the same prefix succeeded at once (`GIT_TRACE=1`), and the recovery ref
  and the re-run branch both pushed later, so the rejection was transient. The remote accepted the pack (it printed the
  pull-request hint) and then failed the ref update server-side, which is what a bare `(failed)` means; it coincided
  with many flows pushing at once.
- The engine's real fault is its handling of that one failure: it does not retry and does not record the branch it just
  created, so a resume cannot reuse it.

## Acceptance

- The engine records `execution_branch` in the checkpoint before the host push.
- A rejected push is retried with backoff (bounded attempts), and each failure's full remote output and attempt number
  are logged.
- A resume after a failed push reuses the recorded branch (re-pushes it, from the recovery ref if needed) instead of
  re-running execute, and never leaves a second E-branch.
- Tests with a fake remote that rejects once and then accepts: the push succeeds on the retry; a push that always
  rejects halts with the branch recorded; a resume after that halt re-pushes without re-running execute.

## Assumptions

- The rejection is transient and server-side. Validation: the throwaway push succeeded and both branches later pushed;
  confirm by logging the retry count on the next occurrence.
- A bounded retry (for example 5 attempts, 5 s doubling) is enough. Validation: the later pushes succeeded on a single
  retry minutes later; check the logged attempt numbers across the next ten flows.
- The recorded branch name is unique per execute run. Validation: names embed the run timestamp, so a rerun never
  collides; the test asserts a resume does not mint a new name.
- A fake remote (a local bare repository with a pre-receive hook that fails once) reproduces the `(failed)` shape
  closely enough. Validation: the test asserts on the exit code and the "remote rejected" line, not on GitHub's text.

## Resolution

Delivered via [PR #418](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/418) and merged into `main`
(`8351cde7`):

- **Key Deliverables**: Updated `flow/stages/execute.py`, `flow/host_remote.py`, and `flow/execution_recovery.py` to
  record `execution_branch` in the checkpoint before the host push, retry rejected pushes with bounded exponential
  backoff while logging remote output and attempt numbers, and reuse the recorded branch on resume (from the recovery
  ref when needed) without creating a duplicate execution branch.
- **Verification & Tests**: Added hermetic tests in
  `apps/sandbox-executor/tests/flow/test_host_push_retry_record_branch.py`.
- **Holon Flow Traversal**: Completed Stage 4 consensus approval and merged to `main`.
