---
# holon-agentic-coder-ref-metadata-0233
title: "Validate that repo_dir is an attached git worktree"
status: todo
type: bug
priority: high
tags:
  - cli
  - flow
  - git
  - worktree
  - validation
  - holon-agentic-coder
created_at: 2026-11-05T14:20:00Z
updated_at: 2026-11-05T14:20:00Z
---

## Problem

`holon flow` and `holon` role subcommands accept `--repo-dir` (defaulting to the current working directory).

Currently, repo directory validation only checks `git -C <target_dir> config --get remote.origin.url` in
`_resolve_target_repo()`. In bare clone repository layouts (such as `apps/holon-agentic-coder/`), an arbitrary directory
or the bare repository itself satisfies `git config --get remote.origin.url` because Git walks up to the parent bare
`.git` config.

As a result:

1. Stages 1–3 (Intent, Plan, Execute) run inside Docker containers that perform their own remote clones, masking that
   the host `--repo-dir` is not a working tree.
2. When the flow reaches Stage 4 (Review) or Stage 5 (Calibration), host-side Git operations
   (`_checkout_execution_branch` and ledger reconciliation) fail with:
   ```text
   fatal: this operation must be run in a work tree
   ```
   halting the entire pipeline after hours of execution.

## Decision

Validate `--repo-dir` fail-fast before any pipeline stage runs:

1. The target path must exist and be a directory.
2. The target path must be an active Git worktree (`git -C <target_dir> rev-parse --is-inside-work-tree` == `true`).
3. The target path must NOT be a bare repository (`git -C <target_dir> rev-parse --is-bare-repository` == `false`).
4. On failure, fail immediately with an actionable error message explaining that `--repo-dir` must be an attached
   worktree (and recommending `git worktree add` for bare clones).
5. Apply the same check in `FlowContext` / `PipelineEngine` when resuming from a checkpoint, in case the checkpoint's
   recorded `repo_dir` was removed, detached, or was never a worktree.

## Scope

1. **CLI & Flow Validation**:
   - Add a worktree verification helper in `sandbox_executor.git` or `sandbox_executor.cli`.
   - Invoke verification early in `cli/commands/flow.py` and `PipelineEngine.validate()`.
2. **Error Messaging**:
   - Produce a clear error when `--repo-dir` is a bare repo or plain non-worktree folder.
3. **Tests**:
   - Add hermetic pytest test cases in `apps/sandbox-executor/tests/test_cli.py` and
     `apps/sandbox-executor/tests/test_flow.py` asserting that bare repositories and non-worktree directories are
     rejected before Stage 1 or on resume.

## Notes

- Target repository: `holon-agentic-coder`.
- Must be delivered through the Holon flow (`holon flow`).
