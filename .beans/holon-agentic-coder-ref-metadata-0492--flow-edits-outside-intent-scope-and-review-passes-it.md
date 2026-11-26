---
# holon-agentic-coder-ref-metadata-0492
title: "A flow edited a file outside its intent scope and the review passed it"
status: todo
type: bug
priority: normal
tags:
  - flow
  - scope
  - holon-agentic-coder
created_at: 2026-11-26T07:12:00Z
updated_at: 2026-11-26T07:12:00Z
---

## Problem

The flow for intent `timing-gate-runner-variance` (PR #321 on holon-agentic-coder) declared four files in its intent
scope. Its pull request also changed `apps/sandbox-executor/src/sandbox_executor/flow/github/ci_failure_detail.py`,
which is not in the scope. The change itself is reasonable (it recognises the bare `Timing gate` step name used by the
Workspace survival job), but the flow edited the file without it being declared, Stage 3 and Stage 4 did not stop it,
and the approval covered it. Found 2026-11-26 while verifying PR #321 after its flow completed.

## Why it matters

Intent scope is what admission uses to decide overlaps with other flows in flight. An undeclared file in a pull request
can overlap a flow that was admitted on the declared scope, so the admission decision no longer holds for the PR as
written.

## Next step

Find where the execute-stage touch set is checked against the intent scope (and why the review did not reject the extra
path), then make an edit outside the declared scope fail Stage 3 or Stage 4 unless the plan declares it. Check whether
PR #321 should be re-scoped or the file added to the intent scope before the maintainer merges.
