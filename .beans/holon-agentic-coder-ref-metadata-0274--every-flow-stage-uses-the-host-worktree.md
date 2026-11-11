---
# holon-agentic-coder-ref-metadata-0274
title: "Every flow stage works in the host-provisioned worktree; remove `HOLON_REPO_URL` altogether"
status: todo
type: feature
priority: high
tags:
  - flow
  - sandbox
  - worktree
  - holon-agentic-coder
created_at: 2026-11-11T10:00:00Z
updated_at: 2026-11-11T10:00:00Z
---

## Problem

Bean 0262 (PR #162) mounted the flow's worktree into the Stage 3 and Stage 4 role containers, but not the other two
stages, and left the clone URL in place:

- `entrypoint/intent_creator.py:94` (Stage 1) and `entrypoint/planner.py:283` (Stage 2) still run
  `git clone ... $HOLON_REPO_URL` into an empty in-container workspace.
- `entrypoint/executor.py:1246` still calls `get_repo_url()`, which raises when the variable is unset, although the
  mounted path never clones.
- The review loop pushes to the credential-free URL (`entrypoint/review_loop.py:493`, "the host worktree's origin may be
  an SSH remote") but the execution-diff check fetches the plan and execution branches from the worktree's own `origin`.

A container cannot use an SSH `origin`: Docker Desktop's forwarded agent socket is `root:root` mode 0660 and the roles
run as uid 1000, so `ssh-add -l` as that user reports "Permission denied". Stage 4 of the flows for Beans 0160 and 0263
therefore halted with `git@github.com: Permission denied (publickey)` on 2026-11-11 (loading the key into the host agent
made no difference). Stages 1 to 3 passed only because they clone over HTTPS or never fetch.

## Requirement (maintainer, 2026-11-11)

All stages should use the local worktree, and `HOLON_REPO_URL` should be removed altogether (maintainer, 2026-11-11).
Containers never touch the remote: roles commit inside the mounted worktree and the host does every fetch and push with
its own credentials. `gh` reads the repository from the worktree's own remote, so no replacement variable is added.

## Action

Run through the Holon flow: `todo/intent-0274-every-flow-stage-uses-the-host-worktree-and-no-clone-url.json`. It mounts
the worktree for the intent and plan roles with the same protections as the existing mount, moves the resolver push and
the review loop fetches to the host, deletes `HOLON_REPO_URL` and `get_repo_url()` with every reference, and names the
operation, branch and remote in failures.

## Blocker for running it

The installed flow engine still fetches from the worktree's SSH `origin` in Stage 4, so any flow, this one included,
stops there until the shared repository's fetch URL is HTTPS (or this bean lands). The workaround is
`git config remote.origin.url https://github.com/Holon-Agentic-Coder/holon-agentic-coder.git` plus
`remote.origin.pushurl git@github.com:Holon-Agentic-Coder/holon-agentic-coder.git` in `apps/holon-agentic-coder`. The
auto-mode classifier denied the agent making that change, so it needs the maintainer's go-ahead. Flows for Beans 0160
and 0263 are halted at Stage 4 (checkpoints in their `flow-<slug>` worktrees) and resume from there.
