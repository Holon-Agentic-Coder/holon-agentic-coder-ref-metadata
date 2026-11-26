---
# holon-agentic-coder-ref-metadata-0507
title: "install-holon fails its main-worktree pull when a concurrent fetch rewrites the shared FETCH_HEAD"
status: todo
type: bug
priority: medium
tags:
  - harness
  - install
  - post-merge
  - holon-agentic-coder
created_at: 2026-11-26T10:40:20Z
updated_at: 2026-11-26T10:40:20Z
---

## Problem

Running `install_holon.py` after PR #331 merged (2026-11-26) failed at its sync step with exit 128:
`git pull --ff-only origin main` printed `Cannot fast-forward to multiple branches`. The main worktree was already
fast-forwarded to `origin/main` by the same run. A retry of the same pull succeeded, and the second install run
completed all images and both CLIs.

`FETCH_HEAD` is shared by every worktree of the repository and had accumulated about 180 lines from live flows' fetches,
which points to a concurrent fetch from a running flow rewriting it mid-pull.

## Proposed fix

- In `install_holon` / `install_coherence` sync, retry the fetch-and-pull once on this exit, or use
  `git merge --ff-only origin/main` after `git fetch origin main` (no `FETCH_HEAD` dependency on the pull's merge
  candidates).
- Consider trimming `FETCH_HEAD` or running the pull with `--no-write-fetch-head` where supported.
