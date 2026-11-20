---
# holon-agentic-coder-ref-metadata-0343
title: "A test writes checkpoint-parent.json into the real flow worktree instead of a temporary directory"
status: completed
type: bug
priority: normal
tags:
  - tests
  - isolation
  - checkpoint
  - holon-agentic-coder
created_at: 2026-11-20T20:40:00+11:00
updated_at: 2026-11-20T22:40:00+11:00
---

## Problem

On 2026-11-20 a `uv run pytest` run inside the `flow-freeze-module-budgets-split` worktree left a stray
`.holon/flow/checkpoint-parent.json` (`intent_slug: "parent"`) in the worktree. Some test saves a checkpoint relative to
the current directory or the real repository instead of `tmp_path`, so running the suite can leave or overwrite state
that a live flow reads.

## Action

Through the Holon flow on `holon-agentic-coder`: find the test(s) writing `checkpoint-parent.json` (likely the
decomposition or children tests), make them write under `tmp_path`, and add a guard (an autouse fixture or a session
check) that fails the run if any test creates files under the repository's `.holon/`.

## Progress

- 2026-11-20: Holon flow `tests-never-write-real-worktree` started (claude-agent, claude-opus-5-5) in worktree
  `flow-tests-never-write-real-worktree`.
- 2026-11-20: Flow completed all 5 stages. PR #215 (https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/215)
  approved 3/3 at review iteration 2; calibration report in PR diff; EV predicted 46.57, actual 62.39; MERGEABLE/CLEAN,
  all checks green. Awaiting human merge.

## Resolution

Delivered via [PR #215](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/215) and merged into `main`
(`c3c0471`):

- **Key Architectural Deliverables**: decomposition tests now write under `tmp_path` through
  `tests/flow/decomposition_fakes.py`, so no test saves a checkpoint relative to the real worktree.
  `tests/holon_dir_guard.py` is hooked in `conftest.py` and fails the session on any write under `.holon/`.
- **Verification & Tests**: guard covered by `tests/test_holon_dir_guard.py`; isolation rules documented in
  `docs/hermetic_testing.md`.
- **Holon Flow Traversal**: all 5 stages completed (Intent -> Plan -> Execute -> Review Loop -> Calibration); approved
  3/3 at review iteration 2. Calibration: expected value 46.57, actual 62.39.
