---
# holon-agentic-coder-ref-metadata-0247
title: "holon flow automatically creates dedicated git worktree if target worktree does not exist"
status: completed
type: feature
priority: high
tags:
  - flow
  - cli
  - git
  - worktree
  - holon-agentic-coder
  - automation
created_at: 2026-11-06T22:25:00Z
updated_at: 2026-11-07T03:02:00Z
---

## Problem

Currently, `holon flow` requires operators and agents to manually manage Git worktrees before running the pipeline:

```bash
cd apps/holon-agentic-coder/.git
git worktree add --no-track -b flow-0244-immutable-facts ../flow-0244-immutable-facts origin/main
cd ../flow-0244-immutable-facts
holon flow /path/to/intent.json ...
```

This manual prerequisite introduces significant friction, failure modes, and fragile state:

1. **Branch Collision on Retries**: If a previous attempt failed or was restarted, `git worktree add -b <branch>` fails
   with:
   ```text
   fatal: a branch named 'flow-XXXX' already exists
   ```
2. **Missing Worktree Directory**: If an operator or cleanup script deletes the folder (`rm -rf flow-XXXX`) without
   running `git worktree prune`, Git's internal index retains the worktree registration, blocking re-creation.
   Subsequent `cd ../flow-XXXX` fails, causing `holon flow` to inadvertently execute inside the bare `.git` directory
   and crash hours later during Stage 4/5 with:
   ```text
   fatal: this operation must be run in a work tree
   ```
3. **Manual Overhead**: Developers and autonomous agents should be able to execute `holon flow <intent.json>` directly.
   The tool should handle its own execution environment setup.

## Goal

`holon flow` must automatically detect, create, and configure its target working tree if it does not already exist.

1. **Automatic Worktree Resolution & Provisioning**:
   - When `holon flow <intent.json>` is invoked:
     - Inspect the resolved `--repo-dir` and target repository.
     - If `--repo-dir` does not exist or points to a bare repository / parent bare checkout:
       - Derive the worktree path (e.g. `apps/<repo>/flow-<slug>`) and branch name (`flow-<slug>`).
       - Ensure stale worktree metadata is cleaned up by running `git worktree prune`.
       - Check if the branch `<branch>` already exists locally or on `origin`:
         - If the branch **does not exist**: run `git worktree add --no-track -b <branch> <path> origin/main`.
         - If the branch **already exists**: attach the worktree to the existing branch via
           `git worktree add <path> <branch>`.
     - Automatically switch execution context (`repo_dir`) to the provisioned worktree.

2. **Self-Healing Stale Worktree Records**:
   - Before attempting `git worktree add`, automatically execute `git worktree prune` to clean any orphaned worktree
     records whose folders were deleted from disk.
   - If a worktree directory exists on disk but is detached or dirty, validate its state cleanly before proceeding.

3. **Seamless CLI Execution from Anywhere**:
   - Operators and agents can invoke:
     ```bash
     holon flow /path/to/intent.json --agent antigravity-agent --model gemini-3.8-flash-medium
     ```
     from the repository root or bare repository without manual worktree creation or manual directory navigation.

4. **Hermetic Unit Tests with Real Git Repositories (Minimise Mocking)**:
   - In `apps/sandbox-executor/tests/test_flow.py` (or a dedicated `test_worktree.py`):
     - Create a real local bare git repository in `tmp_path` (with an initial commit on `main`).
     - Test that invoking flow worktree resolution automatically creates the worktree directory on disk.
     - Test that when the directory is removed with `shutil.rmtree()`, the flow prunes and re-attaches to the existing
       branch without error.
     - Test that subsequent runs against an existing worktree reuse it idempotently.
     - Strictly avoid mocking Git commands; test against actual real Git operations on disk.

## Resolution

Delivered and verified through the 5-stage Holon flow via
[PR #135](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/135) and merged into `main` at commit
`fe17e191de55f09239939aad2182317c4b83d2f2`.

Key technical deliveries:

1. **Automatic Worktree Resolution & Provisioning (`sandbox_executor.git_flow`)**:
   - Added `ensure_active_worktree()` and supporting helpers (`is_bare_repository()`, `is_worktree()`,
     `prune_worktrees()`, `resolve_target_worktree_path()`).
   - Automatically derives dedicated worktree directory paths (e.g. `apps/<repo>/flow-<slug>`) and branches
     (`flow-<slug>`).
   - Pre-emptively runs `git worktree prune` to purge orphaned worktree metadata from manual disk deletions.
   - Dispatches branch detection: if the branch exists locally or on remote, it attaches cleanly via
     `git worktree add <path> <branch>`; if new, it cuts from `origin/main` without tracking.
2. **`holon flow` Integration (`sandbox_executor.cli.commands.flow`)**:
   - Integrated `ensure_active_worktree()` into `_resolve_checkpoint_and_intent()` and `_build_flow_context()`.
   - Allows operators and agents to invoke `holon flow <intent.json>` from root, bare directories, or arbitrary
     locations, seamlessly re-anchoring `context.repo_dir` to the active worktree.
3. **Hermetic Integration Tests Minimising Mocks (`test_flow.py`)**:
   - Added real Git repository test cases in `apps/sandbox-executor/tests/test_flow.py` using `tmp_path`.
   - Verified real bare repository worktree creation, `git worktree prune` recovery from `shutil.rmtree()` deletions,
     and idempotent re-use of pre-existing branches without mocking.
