---
# holon-agentic-coder-ref-metadata-0274
title: "Every flow stage works in the host-provisioned worktree; remove `HOLON_REPO_URL` altogether"
status: completed
type: feature
priority: high
tags:
  - flow
  - sandbox
  - worktree
  - holon-agentic-coder
created_at: 2026-11-11T10:00:00Z
updated_at: 2026-11-12T00:30:00Z
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

## Resolution

Delivered via [PR #165](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/165) and merged into `main`
(`660c50b`, 2026-11-11T13:24Z), through the 5-stage flow (`claude-agent` / `claude-sonnet-5-5`, intent slug `worktree`),
followed by a harness `pr-review-loop`.

- **Deliverable**: the intent and plan stages work in the host-provisioned worktree like execution and review, and no
  role container runs a remote git operation: the host fetches the base before each container and pushes after it (new
  `flow/host_remote.py`, fast-forward only, arguments validated and passed after `--`), and errors name the operation,
  branch and remote with credentials stripped. `HOLON_REPO_URL` and `get_repo_url()` are removed (a stale value is
  ignored). The existing mount protections are unchanged.
- **Why it was needed**: Stage 4 of Beans 0160 and 0263 failed with `Permission denied (publickey)` because a container
  cannot use an SSH `origin` (Docker Desktop's forwarded agent socket is `root:root` mode 0660 and the roles run as uid
  1000).
- **Review**: the flow's engine review took 2 iterations (calibration predicted EV 35.00, actual -4.91, delta -39.91).
  After the sync with `main` the harness loop ran 4 iterations from a full-scope first ensemble: iteration 1 found 1
  critical (the resolver's `head_sha` reached `git push` unchecked, a `--receive-pack` or `+` force-refspec injection),
  3 important and 7 nit findings, all applied or rejected with evidence; iterations 2 and 3 applied their important and
  nit findings; iteration 4 was 3 approvals (one nit rejected by the orchestrator itself, recorded in the coordination
  ledger). CI 11/11 at `f79eafb`.
- **Notes**: a first run with a 56-character slug failed at the push (`ref too long`, Bean 0275) and was rerun with the
  slug `worktree`. The executor lost its push when the sync with `main` hit the deleted snapshot fixture, so the
  execution branch was synced and pushed by hand and the flow resumed from review with a repaired checkpoint.
