---
id: holon-agentic-coder-ref-metadata-0019
title: Fix executor.py git re-initialization fallback wiping parent commit history
status: todo
type: task
created_at: 2026-08-31T20:56:00+10:00
updated_at: 2026-08-31T20:56:00+10:00
---

# Fix executor.py git re-initialization fallback wiping parent commit history

## Context

During containerized agent execution (`./holon execute`), `executor.py` encountered an invalid or missing `.git` state
after running the agent
(`Warning: git repository invalid or missing after agent execution. Re-initializing git repo...`).

The current fallback implementation in `executor.py` performs a naive `git init` and sets `symbolic-ref HEAD` without
fetching or checking out the parent `plan_branch` commit. Consequently, the resulting execution commit is created as an
orphan root commit containing only the execution ledger files (`executions/*.md` and
`holon-knowledge/ledger/executions.jsonl`), stripping all parent commit history and codebase files.

## Goals & Action Plan

1. **Investigate Agent Execution Behavior**:
   - Determine why the agent runner inside the container sandbox causes `git rev-parse --is-inside-work-tree` to fail
     after `agy` completes.

2. **Fix `executor.py` Git Fallback**:
   - Update `executor.py` fallback logic when `.git` is missing or invalid to fetch and re-attach the base `plan_branch`
     commit before staging changes.
   - Ensure `git add -A` and `git commit` preserve parent commit history so the execution branch builds directly upon
     `plan_branch`.

3. **Add Unit Tests**:
   - Add unit test in `apps/sandbox-executor/tests/test_executor.py` simulating git re-initialization to ensure parent
     commit history and codebase files are preserved.
