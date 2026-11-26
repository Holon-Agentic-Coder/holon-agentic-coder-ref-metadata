---
# holon-agentic-coder-ref-metadata-0518
title:
  "Review loop writes its git identity into the shared repository config, so host-side commits are authored by the agent"
status: todo
type: bug
priority: high
tags:
  - flow
  - git
  - review-loop
  - holon-agentic-coder
created_at: 2026-11-26T13:06:00Z
updated_at: 2026-11-26T13:06:00Z
---

## Problem

On 2026-11-26 the bare repository config shared by every worktree of holon-agentic-coder
(`apps/holon-agentic-coder/.git/config`) holds `user.name = Holon Review Loop Agent` and
`user.email = review-loop-agent@holon-agentic-coder.com`. The Stage 4 review loop runs `git config` on the mounted
worktree, and because worktrees share one config file, the identity leaks to every worktree on the host. A conflict
resolution merge made on the host for PR #340 (`da5880ad`) was authored as "Holon Review Loop Agent" instead of the
maintainer. Any harness subagent or the maintainer committing in a holon-agentic-coder worktree now does the same. The
global identity (`~/.gitconfig`) is unaffected.

## Proposed fix

- The review loop (and any container role) sets identity per command (`git -c user.name=... -c user.email=...` or
  `GIT_AUTHOR_*`/`GIT_COMMITTER_*` env), or with `git config --worktree` after enabling `extensions.worktreeConfig`,
  never in the shared repository config.
- One-off: remove the two keys from the shared config once no flow depends on them (check first that flows still set
  their own identity).
- Related: earlier hits on git identity: , 0019, 0118, 0131, 0213.
