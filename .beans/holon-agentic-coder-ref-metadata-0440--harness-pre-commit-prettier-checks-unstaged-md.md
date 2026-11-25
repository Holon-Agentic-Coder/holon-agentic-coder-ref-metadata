---
# holon-agentic-coder-ref-metadata-0440
title: "Harness pre-commit Prettier check blocks commits on unstaged files from parallel sessions"
status: todo
type: bug
priority: high
tags:
  - harness
  - pre-commit
  - prettier
  - concurrency
created_at: 2026-11-25T00:28:00Z
updated_at: 2026-11-25T00:28:00Z
---

## Problem

The harness `.git/hooks/pre-commit` script runs `npx prettier --check "**/*.md"` across the entire working tree. When
multiple agent sessions run concurrently in the shared `holon-agentic-coder-ref-metadata` checkout, any unstaged or
untracked `.md` file left mid-edit by another session causes `git commit --only <own_files>` to fail for every other
session.

## Evidence (2026-11-25)

- `.git/hooks/pre-commit` executes:
  ```sh
  npx prettier --check "**/*.md"
  ```
- In the shared harness checkout (`git status --short` showing `50+` concurrent modified/untracked files across
  `.beans/`, `.agents/`, and root), sessions committing only their own formatted files via `git commit --only <files>`
  are blocked whenever any concurrent session holds an unformatted `.md` file in the working tree.

## Proposed change

1. Update `.git/hooks/pre-commit` (and any hook template/installer or harness documentation) to check **only staged
   Markdown files** (`git diff --cached --name-only --diff-filter=ACMR -- '*.md'`), matching the staged-files-only
   pattern already used by `.agents/scripts/pre_commit_check.py`.
2. Keep full-tree `npx prettier --check "**/*.md"` available for explicit CI/manual sweeps rather than blocking
   per-session commits on unrelated unstaged files.

## Expected gain

Eliminates cross-session commit blocks in the multi-agent harness without weakening Prettier enforcement on committed
files or tempting agents to edit another session's files.

## Cost

Tiny: small harness shell-hook change (and corresponding hook test/doc update if tracked).

## Notes

- Harness change (`holon-agentic-coder-ref-metadata`).
- Related: Bean `0423` (multi-session coordination), Bean `0429` (`pre_commit_check.py` `.beans/` validation), Bean
  `0002` (initial pre-commit hook setup).
