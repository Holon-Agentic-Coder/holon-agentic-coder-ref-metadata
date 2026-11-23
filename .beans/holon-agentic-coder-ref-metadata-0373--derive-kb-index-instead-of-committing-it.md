---
# holon-agentic-coder-ref-metadata-0373
title: "Stop committing the KB/WB index.json files; derive the index from the entry files"
status: todo
type: feature
priority: critical
tags:
  - knowledge-base
  - merge-conflicts
  - cost
  - holon-agentic-coder
created_at: 2026-11-23T06:45:00Z
updated_at: 2026-11-23T06:45:00Z
---

## Problem

`knowledge/wisdom.py::_update_directory_index` rewrites `holon-knowledge/kb/failure_modes/index.json` (also
`kb/patterns/index.json` and `wisdom/heuristics/index.json`) whenever an entry is added or changes, stamping a new
top-level `updated_ts`. Any two flows that add KB entries both change that line and the closing brackets, so the file
conflicts on nearly every PR, which forces a merge of `main`, a CI cycle and (today) a re-review.

Nothing in production reads these files: the only references are the writer, tests asserting the file exists, and
`docs/knowledgebase_schema.md` / `docs/wisdombase_schema.md`. Every field an index entry holds (`kb_id`, `file`,
`kb_type`, `status`, `created_ts`, `tags`) is already in the matching `KB-*.json` / `WB-*.json` entry file.

## Goal

No flow writes a shared index file. The index is derived from the entry files when needed.

## Acceptance criteria

- `_update_directory_index` is removed; writing a KB or WB entry writes only that entry's own file.
- The three tracked `index.json` files are removed from git and ignored.
- A `load_index(subfolder)` helper globs the entry files and returns the same entries the index held, sorted by
  `created_ts` then id; tests compare it with the last committed index content.
- Tests that asserted `index.json` exists now assert the derived index; `docs/knowledgebase_schema.md` and
  `docs/wisdombase_schema.md` describe the index as derived.
- Two flows that each add KB entries produce PRs that merge in either order with no conflict under
  `holon-knowledge/kb/`.
- All tests pass via `uv run pytest`; `uv run task lint` and `uv run task lint-docs` pass.

## Delivery

Holon flow on `holon-agentic-coder`, intent `todo/intent-0373-derive-kb-index.json`. Small; split out of Bean 0371.
