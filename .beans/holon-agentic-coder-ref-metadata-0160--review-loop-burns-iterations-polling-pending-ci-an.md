---
# holon-agentic-coder-ref-metadata-0160
title: "Review loop burns its iteration budget polling pending CI and then reports a test failure"
status: todo
type: bug
priority: critical
tags:
  - review-loop
  - ci
  - holon-flow
  - holon-agentic-coder
created_at: 2026-10-26T06:01:45Z
updated_at: 2026-10-26T06:01:45Z
---

## Problem

Found on 2026-10-26 in the Bean 0159 flow (PR #97, log `todo/logs/0159-flow-r2-review.log`). Stage 4 used all 25 review
iterations in 8.3 minutes (about 18 s each), and no reviewer agent ever ran. It then failed with "Autonomous review
consensus failed: test suite reported failures". In fact every completed check had passed, including
`unit (ubuntu-latest)` (6m41s), and only `unit (macos-latest)` was still queued.

- `sandbox_executor/flow.py` around lines 3469-3476: when `github_cli` CI reports pending checks, the iteration sleeps
  once for 15 s and re-probes. Still-pending checks then count as `all_passed=False`, the iteration records
  `FIND-CI-NNN` and ends. Each CI poll consumes one review iteration, so a normal 7-10 minute CI run (macOS runners
  queue longer) exhausts the default budget of 25 before review starts.
- `flow.py` around line 3988: the catch-all error reports "test suite reported failures" even when nothing failed and
  checks were only pending.

## Scope

- Waiting for pending CI must not consume review iterations. Wait under a separate CI wall-clock budget (a configurable
  `HOLON_REVIEW_CI_WAIT_SECONDS` with a documented default, alongside the Bean 0139 budgets) with back-off, then run the
  reviewer ensemble on settled results.
- Distinguish outcomes in the stage error: CI still pending after the wait budget, CI failed (name the failed checks),
  and tests not measured.
- Tests (fixtures only, never real `gh`): pending checks that settle as passes reach consensus without spending
  iterations; a CI wait-budget timeout reports "pending", not "failures"; a real failed check names the check.

## Notes

- Run through the Holon flow on holon-agentic-coder. It overlaps 0151/0159 on `flow.py`; run it sequentially.
- Workaround: wait for `gh pr checks <N> --watch` to settle, then resume with `--from-stage review`.
