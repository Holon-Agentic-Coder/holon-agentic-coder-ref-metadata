---
# holon-agentic-coder-ref-metadata-0019
title: Fix executor.py git re-initialization fallback wiping parent commit history
status: todo
type: task
created_at: 2026-08-31T10:56:00Z
updated_at: 2026-09-22T13:10:00Z
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

## Status Verification (2026-09-22)

Status remains `todo`. Re-audited against the current `holon-agentic-coder` tip (`origin/main` = `a4d6930`) and the
defect is still present and unfixed:

- `apps/sandbox-executor/src/sandbox_executor/entrypoint/executor.py:516-531` still implements the fallback as
  `rmtree(.git)` -> `git init` -> `git symbolic-ref HEAD refs/heads/<exec_branch>` -> `git remote add origin`, with no
  `git fetch`, `git reset`, or `git update-ref` step to re-attach the parent `plan_branch` commit. The subsequent
  `git add` / `git commit` therefore produces an orphan root commit.
- The fallback is now worse than originally described: it deletes the existing `.git` directory outright, so any local
  object database and refs present in the sandbox at that moment are destroyed before re-initialisation.
- `apps/sandbox-executor/tests/test_executor.py:342` still asserts only that a `git symbolic-ref HEAD` command was
  issued, which actively locks in the defective behaviour; the goal 3 regression test must replace that assertion.

No code change is warranted in the metadata repository; this bean stays open against `holon-agentic-coder`.
