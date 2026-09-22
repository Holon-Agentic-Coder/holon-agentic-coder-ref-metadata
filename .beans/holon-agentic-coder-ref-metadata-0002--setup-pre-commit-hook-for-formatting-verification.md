---
# holon-agentic-coder-ref-metadata-0002
title: Setup pre-commit hook for formatting verification
status: completed
type: task
created_at: 2026-07-18T00:00:00Z
updated_at: 2026-07-18T00:00:00Z
---

Configure a local git pre-commit hook (e.g. using Husky or standard git hooks) to run 'npx prettier --check "**/*.md"'
before commits are made. This ensures local developer/agent environment formatting safety.

## Assignment

Assignee: `antigravity`

## Resolution

Created .git/hooks/pre-commit executable script to run 'npx prettier --check "**/*.md"' before committing changes
locally.
