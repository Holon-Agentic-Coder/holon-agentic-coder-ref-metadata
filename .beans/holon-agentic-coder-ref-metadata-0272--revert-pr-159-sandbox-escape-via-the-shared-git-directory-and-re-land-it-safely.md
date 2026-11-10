---
# holon-agentic-coder-ref-metadata-0272
title: "Revert PR #159 (sandbox escape through the shared git directory) and re-land the host-worktree mount safely"
status: in-progress
type: bug
priority: critical
tags:
  - security
  - sandbox
  - docker
  - git
  - holon-agentic-coder
created_at: 2026-11-10T07:00:00Z
updated_at: 2026-11-10T07:00:00Z
---

## Problem

PR #159 (Bean 0262, merged as `80b844d`, 2026-11-10T05:50:44Z) bind-mounts the host worktree into role containers.
`sandbox_worktree_mounts` in `git_flow.py` mounts the repository's whole **common git directory read-write at its host
path** and overlays read-only only `config`, `config.worktree`, `hooks`, `modules` and the mounted worktree's own
`.git`, `gitdir` and `commondir` pointers. Every **sibling worktree's** administrative folder under `worktrees/<name>/`
stays writable, including the user's `main` worktree. A compromised container (for example a prompt-injected agent) can
rewrite a sibling's `commondir` or `gitdir` so that the next git command run in that worktree on the host executes code
from a directory the container controls: host code execution. The previous design (named volumes and in-container
cloning) never exposed a host git directory.

The final review round raised exactly this as a **critical** finding (reviewer 3, Security role). The flow still
declared consensus and posted a review claiming `APPROVED (3/3)` with reviewer 3 approving, although its own role table
showed Security as CHANGES. See Bean 0273 for the engine defect. The maintainer merged the PR on the strength of that
review.

## Action (maintainer decision, 2026-11-10: revert now)

1. **Revert the source, test and docs changes of PR #159** with a hand-authored revert PR into `main`, outside the Holon
   flow, at the maintainer's explicit instruction (the exception is named in the commit and PR description). **Keep the
   provenance records** of that flow (`holon-knowledge/ledger/*.jsonl`, `plans/`, `executions/`): ledgers are
   append-only and the revert does not erase the history of what was merged and why it was reverted.
2. The maintainer merges the revert PR (it targets `main`). Until it merges, no flow is started: `main` is live in the
   editable `holon` install, so any new run would use the bind-mount path.
3. After the revert merges: rebuild the images from `main` and close this bean's revert step.
4. **Re-land Bean 0262 through the flow** with the security requirement stated in the intent as a hard constraint: the
   container must not be able to write any git administrative path that host git later reads or executes. That includes
   every sibling worktree's folder under `worktrees/`, `commondir`, `gitdir`, `config*`, `hooks/` and `modules/`; prefer
   mounting only the paths the container needs (the worktree, its own admin folder, `objects/` and `refs/` as required)
   instead of the whole common directory, and add tests with a sibling worktree present that fail if the container can
   modify its pointers. The review loop must treat any critical or security finding as blocking regardless of an earlier
   rejection.

## Notes

- Related: Bean 0273 (consensus declared with an open critical finding), Bean 0262 (the original feature).
- PRs #152 and #155 and their branch tree are left alone as the reference for the earlier decomposed attempt.
