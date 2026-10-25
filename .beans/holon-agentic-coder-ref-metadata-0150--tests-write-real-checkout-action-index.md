---
# holon-agentic-coder-ref-metadata-0150
title: "Flow tests write the real checkout's holon-knowledge/.index/action_index.db"
status: todo
type: bug
priority: low
tags:
  - tests
  - hermeticity
  - holon-agentic-coder
created_at: 2026-10-24T09:00:00Z
updated_at: 2026-10-24T09:00:00Z
---

## Problem

The PR #95 iteration-9 dry run (2026-10-24) found two unchanged tests in holon-agentic-coder that write the git-ignored
`holon-knowledge/.index/action_index.db` in the real checkout instead of a temporary directory:

- `TestFlowStages::test_stage1_intent_validation_failure`
- `test_intent_stage_fails_fast_on_unresolved_open_questions`

The file is git-ignored, so `git status` stays clean, but the tests are not hermetic: they mutate the developer's local
index and can interfere with concurrent runs in the same worktree. PR #95 already fixed a similar test
(`test_flow_stage_environment_propagation`) that rewrote the real `intents.jsonl`.

## Scope

- Point both tests (and any others found by a sweep) at `tmp_path` for `repo_dir` / the index location.
- Extend the hermetic-guard test so it also fails when a test touches `holon-knowledge/.index/` in the checkout.

## Notes

- PR #95 has merged, so this can now run through the Holon flow on holon-agentic-coder.

## Resolution
