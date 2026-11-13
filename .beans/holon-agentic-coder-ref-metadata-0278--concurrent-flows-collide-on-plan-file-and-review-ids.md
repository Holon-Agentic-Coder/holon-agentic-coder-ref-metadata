---
# holon-agentic-coder-ref-metadata-0278
title: "Concurrent flows collide on plan file names and review execution ids"
status: completed
type: bug
priority: high
tags:
  - flow
  - ledger
  - concurrency
  - holon-agentic-coder
created_at: 2026-11-12T09:00:00Z
updated_at: 2026-11-12T22:30:00Z
---

## Problem

Two flows that start within the same second produce the same names where the id has no 8-character hex part:

- plan files `plans/P-<ts>-<agent>-<model>.md` (the ledger row's `plan_file` has no hex), so two plans collide on one
  path;
- review ids `REV-<ts>-<agent>` in `executions.jsonl`, so the duplicate-id validation and tests fail after the second
  merge.

Seen 2026-11-11 with the flows for Beans 0160 and 0263 (plan timestamp 1794388224, review timestamp 1794390267): the
later PR hit an add/add conflict on the plan file and duplicate review ids, resolved by hand by giving its file and rows
the hex-qualified name.

## Action

Run through the Holon flow. Include the plan's 8-character hex in the plan file name and the review id, keep existing
names valid, make the ledger duplicate check name both owners, and add hermetic tests with two plans and two reviews
created in the same second. Keep exactly the three ledgers.

## Resolution (completed, 2026-11-12)

Delivered by flow `ids` as holon-agentic-coder PR #169, merged 2026-11-12T22:06:24Z (merge commit `94b2e19`, review
`PRR_kwDORMmd1c8AAAABXqJDxw`). Calibration report
`plans/P-1794446836-06880b0b-claude-agent-claude-sonnet-5-5_calibration.md` is in the PR. EV predicted vs actual: delta
-52.41 (actual -14.31); entropy predicted 5.00 vs observed 3.04. The calibration's test-pass term was 0, so the flow
still records no measured `test_pass_rate` (Bean 0267). The flow needed a conflict merge with `origin/main` and three
review-loop launches; see Beans 0290 and 0291.
