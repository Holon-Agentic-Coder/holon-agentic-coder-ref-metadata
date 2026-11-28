---
# holon-agentic-coder-ref-metadata-0595
title: "install_holon sync races on FETCH_HEAD and fails with 'Cannot fast-forward to multiple branches'"
status: todo
type: bug
priority: medium
tags:
  - harness
  - install
  - post-merge
created_at: 2026-11-27T00:57:36Z
updated_at: 2026-11-27T04:31:36Z
---

## Observed

2026-11-27, post-merge of PR #363: `install_holon.py` failed at its sync step (`git pull --ff-only origin main`, exit
128, "Cannot fast-forward to multiple branches") while another post-merge was fetching `main` into the same repository.
A rerun a minute later succeeded. FETCH_HEAD lives in the shared git directory, so concurrent fetches overwrite each
other.

### Second symptom (noted 2026-11-27T04:31:36Z; observed 2026-11-27 ~04:29Z)

install_holon.py built all holon-agentic-coder images, then failed in the holon-coherence step because the temporary
worktree `build-images-18084f3` already existed (a concurrent install, or a leftover from an aborted one). A rerun
succeeded. The temporary worktree name is not unique per run, so concurrent installs collide on it.

## Fix

- Sync with `git fetch origin main` followed by `git merge --ff-only origin/main`, so no FETCH_HEAD is read.
- Retry the fetch and fast-forward once before failing.
- Use a unique temporary worktree per run (or a lock), and remove it on every exit path.
- Concurrent post-merge installs serialise.

## Acceptance

- install_holon's sync step never reads FETCH_HEAD.
- A test simulates two concurrent fetches and passes; the failure is reproduced first.
- A test simulates a pre-existing temporary worktree name and a concurrent install; both complete, and no temporary
  worktree remains after success or failure.
- Concurrent post-merge installs serialise: a second install waits on the lock rather than colliding.
