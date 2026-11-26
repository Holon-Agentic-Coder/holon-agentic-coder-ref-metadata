---
# holon-agentic-coder-ref-metadata-0557
title: "Flow-engine PRs must pass the suites run under the review loop's own environment (the #350 regression class)"
status: todo
type: task
priority: high
tags:
  - pipeline
  - review-loop
  - tests
  - readiness
  - holon-agentic-coder
created_at: 2026-11-27T00:30:00Z
updated_at: 2026-11-27T00:30:00Z
---

## Problem (repeat category `readiness-check`: CF-0003, CF-0006)

PR #350 (merged 2026-11-26T21:04Z, +744/-14, 10 files) changed `entrypoint/review_loop.py` so the review loop overlays a
git identity on `os.environ`. It passed CI and 3/3 review because both run the test suite in a plain environment, where
the overlay is absent. The overlay only matters when the resolver runs the pre-push suite as a child of the review loop.
There it halted three flows on two deterministic tests (beans 0547, 0548; follow-up PR #354). Neither reviewers nor the
coordinator asked what the change does to child processes; CF-0006 records the second readiness miss of the day after
CF-0003 (#321).

## What would have caught it earlier

- A contract test that starts the review-loop entrypoint's environment setup, runs a child `pytest` over
  `apps/sandbox-executor/tests` (or a marked subset that asserts executor identity and fixtures) and requires it to
  pass. The two failing tests are the canaries.
- A planner/reviewer rule: a diff that sets, overlays or removes environment variables, cwd or git config for a process
  that spawns children must list the child processes affected and carry a test that runs one under the new environment.
- A readiness step for changes to the flow engine: run the affected suite inside the review environment (CF-0006 rule)
  as a recorded command and its result in the readiness note.

## Expected gain

Prevents a flow-engine change from halting other flows (three halted, plus manual diagnosis). Cost: one contract test
and two prompt lines. Does not duplicate 0547/0548 (the fixes) or 0549 (halt handling).

## Resolution
