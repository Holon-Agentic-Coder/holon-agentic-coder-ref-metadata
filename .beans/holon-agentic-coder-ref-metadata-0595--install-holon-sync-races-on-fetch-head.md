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
updated_at: 2026-11-27T01:07:06Z
---

## Observed

2026-11-27, post-merge of PR #363: `install_holon.py` failed at its sync step (`git pull --ff-only origin main`, exit
128, "Cannot fast-forward to multiple branches") while another post-merge was fetching `main` into the same repository.
A rerun a minute later succeeded. FETCH_HEAD lives in the shared git directory, so concurrent fetches overwrite each
other.

## Fix

- Sync with `git fetch origin main` followed by `git merge --ff-only origin/main`, so no FETCH_HEAD is read.
- Retry the fetch and fast-forward once before failing.

## Acceptance

- install_holon's sync step never reads FETCH_HEAD.
- A test simulates two concurrent fetches and passes; the failure is reproduced first.
