---
# holon-agentic-coder-ref-metadata-0429
title: "Validate .beans/ header ID, title uniqueness, and filename consistency in pre_commit_check.py"
status: todo
type: bug
priority: normal
tags:
  - harness
  - beans
  - hygiene
created_at: 2026-11-24T13:00:00Z
updated_at: 2026-11-24T13:00:00Z
---

## Why

During commit `907c0255`,
`.beans/holon-agentic-coder-ref-metadata-0417--gate-flow-wrapper-completion-against-premature-end.md` was committed with
`# holon-agentic-coder-ref-metadata-0416` and the exact frontmatter and body of Bean `0416`, silently erasing Bean
`0417`'s content until the next audit reconstructed it.

## Evidence

- `.agents/scripts/pre_commit_check.py` (lines 19–135) checks only disallowed scratch file globs and credential
  patterns; it performs no integrity check on `.beans/*.md` files.
- `git show 907c0255:.beans/holon-agentic-coder-ref-metadata-0417--gate-flow-wrapper-completion-against-premature-end.md`
  had `# holon-agentic-coder-ref-metadata-0416` and duplicate `title` matching Bean `0416`.

## Proposed change

1. Extend `.agents/scripts/pre_commit_check.py` (or a dedicated helper called by it) so when staged/checked paths
   include `.beans/holon-agentic-coder-ref-metadata-<NNNN>--*.md`:
   - Verify the `# holon-agentic-coder-ref-metadata-<id>` comment line (if present) matches `<NNNN>` from the filename.
   - Verify `title` is non-empty and not identical to another active `.beans/` file's `title`.
   - Verify `status` is one of the valid `beans` CLI values (`draft`, `todo`, `in-progress`, `completed`, `scrapped`)
     and `created_at`/`updated_at` are unquoted RFC3339 UTC timestamps.
2. Add unit tests in `tests/test_pre_commit_check.py`.

## Expected gain

Catches copy-paste or parallel-session bean overwrites before commit.

## Cost

Small harness-only change in `.agents/scripts/pre_commit_check.py` and `tests/`.
