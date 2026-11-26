---
# holon-agentic-coder-ref-metadata-0541
title: "Planner touch set exceeds the intent scope (no check between intent scope and plan touch set)"
status: todo
type: bug
priority: high
tags:
  - flow
  - planner
  - admission
  - holon-agentic-coder
created_at: 2026-11-26T14:28:39.444Z
updated_at: 2026-11-26T14:28:39.444Z
---

## Problem

Flow `admission-remote-in-flight` (bean 0519, 2026-11-26) declared six files in its intent scope. The Stage 2 planner
wrote a plan whose `## Touch Set` lists fourteen files: the intent's six plus `flow/in_flight_liveness.py` (new),
`flow/worktree_checkpoints.py`, `flow/lazy_exports.py`, `tests/flow/remote_flow_fixtures.py` (new),
`tests/flow/test_in_flight.py`, `tests/flow/test_admission_order.py`, `tests/flow/stages/test_execute_touch_set.py`,
`tests/flow/stages/test_execute_budget_guard.py` and `docs/touch_set.md`. Nothing checked the plan against the scope.

Stage 3 admission then compared the wider plan touch set and refused on open PR #342 (branch
`I-1795694671-ledgers-sorted-chronologically`) on `flow/lazy_exports.py`, a file the intent did not name. The refusal
parked the flow.

## Expected

A plan whose touch set adds files outside the intent scope is refused at Stage 2 (or the extra files are rejected before
admission), so a scope-limited flow is not parked by an overlap its intent never asked for.

## Acceptance

- A test: a planner touch set with a file absent from the intent scope fails the plan check with the extra files named.
- A test: a plan whose touch set is a subset of the intent scope passes unchanged.

## Evidence

Flow log: todo/flow-admission-remote-in-flight.log (Stage 3 refusal at 2026-11-26T14:28:21Z).
