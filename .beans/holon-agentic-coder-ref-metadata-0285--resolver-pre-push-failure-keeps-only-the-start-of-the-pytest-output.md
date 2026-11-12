---
# holon-agentic-coder-ref-metadata-0285
title:
  "A resolver pre-push test failure keeps only the start of the pytest output, so the failing tests are never named"
status: completed
type: bug
priority: high
tags:
  - flow
  - review-loop
  - resolver
  - holon-agentic-coder
created_at: 2026-11-12T04:45:00Z
updated_at: 2026-11-12T06:20:00Z
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

## Resolution

Delivered via [PR #175](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/175) (flow `failnames`) and
merged into `main` (`f02a826`, 2026-11-12):

- **Key Architectural Deliverables**: a failed pre-push gate now names the failed (FAILED and ERROR) tests in the halt
  message and stage result, keeps the tail of the output, and writes the full redacted output to a git-ignored file
  under `.holon/` whose path the halt message names. Lint failures and tool-could-not-run failures keep their messages.
- **Verification & Tests**: full host suite 3,647 passed, 4 skipped, plus `uv run task lint` and `lint-docs`. The
  in-container gate was skipped at the maintainer's instruction (CI supplies test results); it had halted twice on the
  unrelated fetch test (Bean 0286).
- **Holon Flow Traversal**: intent, plan, execute and the review loop completed (two iterations: 1 Important and 5 Nits
  applied at `73ae604`, then three approvals); calibration `fed7aeb`, predicted EV 39.44, actual -9.22.
- **Notes**: the engine posted an intermediate changes-requested review before consensus (logged as Bean 0288). The
  resolver's leftover edits were hand-committed as a `wip:` commit to resume (Bean 0287).
