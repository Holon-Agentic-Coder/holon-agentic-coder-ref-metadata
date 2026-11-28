---
# holon-agentic-coder-ref-metadata-0552
title: "Flow calibration-in-diff gate fails when the PR diff exceeds GitHub's 300-file limit"
status: todo
type: bug
priority: high
tags:
  - flow
  - review-loop
  - calibration
  - harness
created_at: 2026-11-26T22:59:29Z
updated_at: 2026-11-26T22:59:29Z
---

## Problem

PR #344 (prune-single-flow-kb-failures) reached 3/3 approval, calibration on the PR branch and MERGEABLE/CLEAN, but
`run_holon_flow.py` exited 1 with "Could not read the diff of PR #344; the calibration report is unverified."

Cause: `gh pr diff 344 --name-only` fails with HTTP 406 `too_large` because the diff has more than 300 files (the PR
touches about 3,019 files, mostly KB-failure deletions). The calibration-in-diff check reads the diff through that same
endpoint, so the gate reports an incomplete deliverable for a PR whose calibration report is in fact on the branch.

Verified by hand: the calibration file is in the PR head
(`plans/I-1795696249-.../P-1795696276-CLA-CO5.5_calibration.md`), branch head equals the remote head, and
`gh api repos/.../pulls/344/files --paginate` lists it.

## Fix direction

- Check calibration inclusion with `gh api repos/{repo}/pulls/{n}/files --paginate` (or
  `git diff --name-only origin/<base>...HEAD` on the flow worktree) instead of `gh pr diff`.
- Or treat HTTP 406 `too_large` as "check via files API", never as a failed deliverable.
- Add a regression test with a mocked 406 response for a PR over 300 files.

## Context

Found while resuming bean 0506 (PR #344) after PR #352 merged. Review of the 3,019-file diff itself fit the prompt (no
"Prompt is too long" on iterations 2 and 3).
