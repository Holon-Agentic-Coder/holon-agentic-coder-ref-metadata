---
# holon-agentic-coder-ref-metadata-0518
title:
  "Review loop writes its git identity into the shared repository config, so host-side commits are authored by the agent"
status: completed
type: bug
priority: high
tags:
  - flow
  - git
  - review-loop
  - holon-agentic-coder
created_at: 2026-11-26T13:06:00Z
updated_at: 2026-11-26T22:58:29Z
---

## Problem

On 2026-11-26 the bare repository config shared by every worktree of holon-agentic-coder
(`apps/holon-agentic-coder/.git/config`) holds `user.name = Holon Review Loop Agent` and
`user.email = review-loop-agent@holon-agentic-coder.com`. The Stage 4 review loop runs `git config` on the mounted
worktree, and because worktrees share one config file, the identity leaks to every worktree on the host. A conflict
resolution merge made on the host for PR #340 (`da5880ad`) was authored as "Holon Review Loop Agent" instead of the
maintainer. Any harness subagent or the maintainer committing in a holon-agentic-coder worktree now does the same. The
global identity (`~/.gitconfig`) is unaffected.

## Status

Delivered via [PR #350](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/350) and merged into `main`
(`cc1f256`, 2026-11-26T21:04:13Z): the review loop sets its identity per command and never writes the shared repository
config. Flow `review-loop-git-identity-env` (intent todo/intent-0518-review-loop-git-identity-env.json, log
todo/flow-review-loop-git-identity-env.log) cleaned up after the merge.

Remaining step (bean stays in-progress, awaiting maintainer go-ahead): remove `user.name` and `user.email` (Holon Review
Loop Agent) from the shared `apps/holon-agentic-coder/.git/config`. Not done by the agent; check first that no flow
depends on them. install-holon was rerun after the merge.

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

## Shared config cleared (2026-11-26 21:08Z)

The maintainer removed `user.name`/`user.email` (Holon Review Loop Agent) from `apps/holon-agentic-coder/.git/config`;
`git config --get user.name` now resolves to the global identity. Flows 0216 and 0390 were started before PR #350's
reinstall and may still write the keys back during their review stage: re-check the shared config after both finish,
then close this bean.

## Resolution

Shared repository config cleared (maintainer, 2026-11-26 21:08Z) and re-checked at 2026-11-26T22:58:29Z:
`git -C apps/holon-agentic-coder/main config --local --get user.name` returns nothing, so the shared `.git/config` no
longer carries `Holon Review Loop Agent` and identities resolve to the global config. The per-command identity fix is in
[PR #350](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/350) (`cc1f256`). The last flow started before
that reinstall (0390) has finished; PR #351 merged at `2f29d8c`. Flow 0216 was resumed separately: if the shared config
gets the keys back, that is a regression of PR #350 and needs a new bean.
