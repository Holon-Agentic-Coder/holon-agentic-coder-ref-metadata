---
# holon-agentic-coder-ref-metadata-0023
title: Create clean-branches skill to remove stale and merged branches and PRs
status: completed
type: task
created_at: 2026-09-17T00:00:00Z
updated_at: 2026-09-22T00:00:00Z
---

Create a specialized skill (.agents/skills/clean_branches/SKILL.md) to audit, prune, and delete stale and merged pull
requests, local branches, and remote branches across all managed repositories in the Holon ecosystem
(holon-agentic-coder, holon-coherence, and holon-agentic-coder-ref-metadata).

## Notes

- Target path: .agents/skills/clean_branches/SKILL.md
- Includes multi-repo discovery, PR merge detection via gh CLI, safe protection of base branches (main), and git
  worktree cleanup.
- Merged: ref-metadata PR #42 (2026-09-17), squash commit 6d33e6d on origin/main.
- Field validation 2026-09-22: skill executed across all three managed repositories; removed 3 worktrees
  (holon-coherence/feat-0026-coding-agent-runners, holon-agentic-coder/feat-0024-implement-holon-init,
  holon-agentic-coder/pr-52) and 4 local branches with zero unremovable directories. The mandatory remote-push step was
  held pending explicit maintainer authorisation per AGENTS.md rule 7.

## Assignment

Assignee: `antigravity`

## Resolution

Created .agents/skills/clean_branches/SKILL.md defining multi-repository discovery, strict base branch protection
(main), safe worktree removal and pruning, remote branch pruning and deletion via gh CLI and git push --delete, and
local tracking branch cleanup.
