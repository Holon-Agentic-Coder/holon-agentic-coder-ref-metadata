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

## Audit evidence (2026-11-26T13:40Z)

- Duration: not new. The host repository already holds commits whose author and committer are `Holon Review Loop Agent`
  made on the host (timezone +11:00): 210 of 738 such commits, the first `10da7fe5`
  (`Merge remote-tracking branch 'origin/main'`) on 2026-11-20, then every day since (229 commits on 11-20, 157 on
  11-21, 142 on 11-23, 71 on 11-26). 77 flow logs show `git config --global user.name Holon Review Loop Agent` run by
  the container. `.git/config` was last rewritten at 00:25 today, so it is live.
- What it affected: every host-side sync and merge commit of a flow (`sync: merge target origin/main at ...`,
  `Merge remote-tracking branch`, `chore(review): record review ledger rows`) is attributed to the agent, as are harness
  conflict merges made in a flow worktree (#340, `da5880ad`). The maintainer's global identity is still in
  `~/.gitconfig` but the repository setting wins. Audit trail by author is unusable for the whole period.
- The log line says `--global`, so the container's HOME (or a mounted config) resolves to the shared repository config.
  Fix the cause (do not mount or point HOME at a file inside the repository) and not only the symptom.
