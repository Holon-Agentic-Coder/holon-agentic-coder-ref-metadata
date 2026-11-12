---
# holon-agentic-coder-ref-metadata-0285
title:
  "A resolver pre-push test failure keeps only the start of the pytest output, so the failing tests are never named"
status: todo
type: bug
priority: high
tags:
  - flow
  - review-loop
  - resolver
  - holon-agentic-coder
created_at: 2026-11-12T04:45:00Z
updated_at: 2026-11-12T04:45:00Z
---

## Problem

When the Stage 4 resolver's pre-push `uv run task test` fails, the engine records
`Resolver pre-push test failed (exit code 1)` followed by only the first ~2,000 characters of the output: the session
header and the first lines of progress dots. With 18 xdist workers and about 3,600 tests, those characters end near 35%
progress, so the `FAILED` summary at the end of the run is never captured. On the `calci` flow (Bean 0280, 2026-11-12)
this halted Stage 4 twice with 4 failing tests (visible only as `F` marks) that could not be named from the log, the
checkpoint or the ledger. The failure did not reproduce on the host (3,651 passed on the flow tree, 3,637 on a clean
`main`), so the container run itself had to be repeated by hand to find out what failed.

## Action

Run through the Holon flow. Keep the tail of the failing test output as well as the head (or run the failing gate with
`-rf` and keep the short test summary), name the failed tests in the halt message and the stage result, and keep the
full output in a file the log points at. Hermetic test with a fake failing test run longer than the cap, asserting the
failed test names survive. Keep exactly the three ledgers; no new dependencies.
