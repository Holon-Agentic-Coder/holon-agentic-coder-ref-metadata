---
# holon-agentic-coder-ref-metadata-0183
title: "Every flow stage works in its own sandboxed clone; holon flow needs no host checkout"
status: scrapped
type: feature
priority: high
tags:
  - holon-flow
  - sandbox
  - concurrency
  - holon-agentic-coder
created_at: 2026-10-29T04:20:00Z
updated_at: 2026-11-11T09:30:00Z
---

## Problem

Stages 1-3 already comply: the intent, plan and execute role agents each work in their own clone inside their role
container (`holon flow` dispatches them through `cli.dispatch_role_agent` since PR #95, 2026-10-25; before that the flow
dispatched no agents at all and wrote a template plan). What still needs a host checkout was built host-side and never
containerised:

| Part                                                                              | Where it works on `main` (`cc4bf1b`)                                                           | Since                                        |
| --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | -------------------------------------------- |
| Flow checkpoint                                                                   | `<repo-dir>/.holon/flow/checkpoint-<slug>.json` (`flow.py:463-482`)                            | PR #58 (2026-09-26)                          |
| Engine checks (empty-diff guard, mergeability, `git status`, `merge-tree`, `add`) | host checkout (`flow.py:829-915`)                                                              | PR #84 (2026-10-18), PR #95                  |
| Stage 4 review                                                                    | host side; PR #102 refuses host reviewer turns                                                 | routing into the role container is Bean 0179 |
| Stage 5 calibration                                                               | host checkout: checks out `/calibrated` and pushes from it, no container (`flow.py:4728-4733`) | PR #86 (2026-10-19)                          |

Two concurrent flows therefore cannot share a checkout (they race on `HEAD`, the index and `.holon/flow/`), and the
user's `main` checkout cannot be used either, so each parallel flow currently needs a throwaway host worktree.

## Requirement (maintainer, 2026-10-29)

All agents — intent, plan, execute, PR review and calibration — check out their **own copy** of the repository inside
their sandbox. **The engine's bookkeeping is sandboxed too** (maintainer, 2026-10-29): the checkpoint, the git checks
and the calibration all run inside the sandboxed environment. The host never needs a working checkout of the target
repository and keeps no flow state of its own; it only starts the containers and streams their output.

## Scope

- Stage 5 calibration runs in a role container with its own clone and creates and pushes `/calibrated` from there. Stage
  4 reviewers do the same through Bean 0179. Stages 1-3 already work this way.
- The engine's bookkeeping runs inside the sandbox, not on the host: the empty-diff guard and mergeability checks run in
  a sandboxed clone, and the checkpoint lives in sandbox-owned storage (for example a per-run volume or a remote
  checkpoint ref keyed by the intent id) rather than in a target checkout or a host state directory. Resume reattaches
  to that storage. The target repository is identified by its remote URL rather than a local path.
- The host CLI becomes a thin launcher: it resolves the target remote, starts the flow's containers (for example the
  existing `holon/orchestrator` image driving the stage role containers), passes credentials through the existing
  redacted routes, and reports status. It performs no git operation on any target checkout.
- `--repo-dir` becomes optional (still accepted for compatibility or local inspection); the default no longer touches
  the current directory's checkout, index or branches.
- Concurrent `holon flow` runs need nothing more than separate invocations. Shared ledger appends
  (`holon-knowledge/ledger/*.jsonl`) stay append-only and are reconciled at merge time (related to Bean 0158).
- Tests (pytest only, never naming another runner): two flows run concurrently without touching a shared host checkout;
  no stage or bookkeeping step mutates the host directory or runs git on the host; checkpoints resume from sandbox-owned
  storage; calibration pushes from the sandbox; no real Docker, `gh`, git remotes or LLM calls in tests.

## Notes

- Enables safe parallel flows together with Bean 0151 (touch-set admission) and Bean 0149 (ID collisions across
  concurrently planned intents); related to Bean 0152 (bringing parallelism back).
- Until it lands, each parallel flow runs with its own throwaway host worktree, created and removed automatically.

## Resolution (scrapped, 2026-11-11)

Superseded by the opposite design, at the maintainer's agreement. Bean 0183 required every stage to clone its own copy
inside its container and the host to keep no checkout. Bean 0259 gave each flow its own host worktree (`flow-<slug>`),
and Bean 0262 ([PR #162](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/162), merged `dd00fb9`)
bind-mounts that worktree into the role containers, with the shared git directory's `worktrees/` area read-only so a
sandbox cannot reach a sibling worktree. Concurrent flows are safe because each has its own worktree, which was this
bean's goal. Stage 4 already runs in the review-loop container (PR #116); the checkpoint lives in the flow's own
worktree, and calibration and the engine's git checks run in that worktree by design. No residual work.
