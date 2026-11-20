---
# holon-agentic-coder-ref-metadata-0295
title: "A rejected resolver diff is saved as a patch the host can read (patch_path is null today)"
status: completed
type: bug
priority: normal
tags:
  - review-loop
  - resolver
  - observability
  - holon-agentic-coder
created_at: 2026-11-13T11:00:00Z
updated_at: 2026-11-13T11:00:00Z
---

## Problem

The rejected-diff record added for a failed resolver pre-push run (`.holon/review/rejected/iter-<n>.json`) keeps the
failing tests, the summary and the counts, but `patch_path` is `null` on PR #187's iteration 3: the patch itself was not
written. The resolver's uncommitted edits survived only because the flow worktree is a bind mount. In a run where they
die with the container, the diff would be lost again, which is what the feature was built to prevent.

## Goal

1. Write the resolver's uncommitted diff (`git diff HEAD` plus staged changes) to
   `.holon/review/rejected/iter-<n>.patch` before the container exits, and record its path in the JSON and the ledger
   action entry.
2. Redact the patch like the rest of the record.
3. A hermetic test with a fixture repository: a failed pre-push run leaves a patch whose content matches the resolver's
   change, and `patch_path` points to it.

## Notes

- Target repository change in `holon-agentic-coder`: through the 5-stage Holon flow. The intent JSON must not mention
  bean ids or harness paths.
- Touches the resolver's failure handling in `entrypoint/review_loop.py` and `review_failure_detail.py`. Follow-up to
  the rejected-diff work.

## Resolution (completed, 2026-11-13)

Delivered by flow `savepat` as holon-agentic-coder PR #189, merged 2026-11-13T12:47:06Z (merge commit `bde4934`, review
`PRR_kwDORMmd1c8AAAABXyLiTw`, all 11 checks green on the final head). Calibration report
`plans/P-1794567538-ea208f06-claude-agent-claude-sonnet-5-5_calibration.md` is in the PR. EV predicted vs actual: delta
-33.17 (actual -8.72); the test-pass term was 0 because the flow ran on the install that predates measured test results.
The review took 14 iterations: four were stalled on a macOS unit timing gate (5.2 minutes against 5.0) with no code
finding, and the PR needed a conflict merge with `origin/main` after PRs #188 and #190 landed.
