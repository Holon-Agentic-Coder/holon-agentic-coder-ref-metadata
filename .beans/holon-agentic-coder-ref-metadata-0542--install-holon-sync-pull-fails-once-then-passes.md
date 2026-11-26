---
# holon-agentic-coder-ref-metadata-0542
title: "install_holon sync step failed once with 'no candidates for merging', then passed unchanged"
status: todo
type: bug
priority: normal
tags:
  - harness
  - install
created_at: 2026-11-26T20:59:53Z
updated_at: 2026-11-26T20:59:53Z
---

## Problem

After PR #342 merged (`57a8aa38`, post-merge of 2026-11-26), the first `install_holon.py` run failed in
`sync_git_worktree` at `git pull --ff-only origin main` with "There are no candidates for merging among the refs that
you just fetched", although the `main` worktree was already at `origin/main` and clean. A manual pull then printed
"Already up to date", and a second run of the same script, with no other install running, completed all builds and CLI
installs.

## Next step

Find why the pull can report no merge candidates right after a fetch (concurrent install, fetch race, or the
`FETCH_HEAD` handling). Make the sync step retry or fail with the fetched state printed. Cause not confirmed.
