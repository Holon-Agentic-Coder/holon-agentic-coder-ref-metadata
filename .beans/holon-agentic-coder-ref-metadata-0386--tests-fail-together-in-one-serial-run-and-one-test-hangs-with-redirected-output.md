---
# holon-agentic-coder-ref-metadata-0386
title:
  "Some review tests fail when run together in one serial invocation, and test_backgrounded_sleep hangs with redirected
  output"
status: todo
type: bug
priority: normal
tags:
  - tests
  - hygiene
  - holon-agentic-coder
created_at: 2026-11-23T12:40:00Z
updated_at: 2026-11-24T13:00:00Z
---

## Problem

Two test-hygiene defects reported by agents on 2026-11-23, both present on `main` (not caused by the PRs that hit them):

1. **Order dependence.** Some review test files fail when run together in one serial pytest invocation and pass on their
   own or under xdist; identical at the PR #255 base (`11b66276`). Reviewers treated it as out of scope.
2. **A hanging test.** The host-only `test_backgrounded_sleep` appears to hang when pytest's output is redirected to a
   file; a full serial run also takes about 25 minutes when the hermetic canary test (`test_sandbox_hermetic_guard`,
   which runs the suite in a nested sandbox) is included.

## Goal

- Find the shared state (module globals, environment, git config, monkeypatched module attributes) behind the order
  dependence and isolate it; add a CI job or a periodic check that runs the suite serially in random order.
- `test_backgrounded_sleep` does not depend on a TTY or an unredirected stdout, and has a timeout.
- State the expected wall time of a full local run in the developer docs, with the flag that skips the nested canary.
