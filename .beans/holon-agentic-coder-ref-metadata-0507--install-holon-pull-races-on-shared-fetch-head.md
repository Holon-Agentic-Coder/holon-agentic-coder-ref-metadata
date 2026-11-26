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
updated_at: 2026-11-26T21:05:39Z
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

## Evidence (folded from bean 0542, 2026-11-26)

- PR #342 merged (`57a8aa38`); the first `install_holon.py` run failed in `sync_git_worktree` at
  `git pull --ff-only origin main` with "There are no candidates for merging among the refs that you just fetched",
  although the main worktree was already at `origin/main` and clean. A manual pull printed "Already up to date"; a
  second run completed all builds and CLI installs.
- Cause still unconfirmed; both symptoms look like the shared `FETCH_HEAD` race above. Fix candidates are the same:
  retry once, or `git fetch origin main` then `git merge --ff-only origin/main`.
- Post-merge install for PR #348 (2026-11-26) ran clean on the first attempt, after the other install (#346) had
  finished.
