---
# holon-agentic-coder-ref-metadata-0488
title: "bean-progress lists a non-flow worktree as a bean row"
status: todo
type: bug
priority: low
tags:
  - harness
  - bean-progress
created_at: 2026-11-26T06:20:00Z
updated_at: 2026-11-26T06:20:00Z
---

## Problem

On 2026-11-26 `bean_progress.py` showed a row `— | HAC | audit test suite | Not started` for the temporary read-only
worktree `apps/holon-agentic-coder/audit-test-suite` (a detached checkout made by an audit subagent, not a flow). The
row has no bean id and its "last activity" is the newest commit on `main`.

## Fix

Only treat `flow-*` worktrees (or worktrees with a flow checkpoint) as in-flight flows; ignore other worktrees.
