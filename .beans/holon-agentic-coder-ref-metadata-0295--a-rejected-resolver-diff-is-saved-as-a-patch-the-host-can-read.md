---
# holon-agentic-coder-ref-metadata-0295
title: "A rejected resolver diff is saved as a patch the host can read (patch_path is null today)"
status: todo
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
