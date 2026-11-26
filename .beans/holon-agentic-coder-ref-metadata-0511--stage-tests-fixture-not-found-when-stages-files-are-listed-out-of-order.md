---
# holon-agentic-coder-ref-metadata-0511
title: "Stage test files error with fixture 'no_origin_reconcile' not found when pytest arguments are out of order"
status: scrapped
type: bug
priority: normal
tags:
  - tests
  - flow
  - holon-agentic-coder
created_at: 2026-11-26T10:55:00Z
updated_at: 2026-11-26T10:57:00Z
---

## Problem

Found by the batch 2 flow for `tests-fewer-git-stage-pipeline` (flow PR #332, execution notes). When
`apps/sandbox-executor/tests/flow/stages/test_replan_request.py` is listed on the pytest command line after a
parent-directory file that itself follows other `stages/` files (for example
`stages/test_children.py flow/test_git_refs.py stages/test_replan_request.py`), its eight cases error with "fixture
'no_origin_reconcile' not found", serially and under xdist. Listing the `stages/` files contiguously, or a
full-directory run, passes.

## Goal

Make the fixture visible to every `stages/` test regardless of argument order (for example by moving it to
`stages/conftest.py` or `flow/conftest.py` at the right scope), or add a test that fails on the out-of-order invocation
so it cannot regress silently.

## Resolution

Scrapped 2026-11-26: duplicate of bean 0491 (same family: a subset or ordered pytest run loses a fixture). The evidence
was added to bean 0491.
