---
# holon-agentic-coder-ref-metadata-0286
title:
  "A children test makes a real git fetch against origin, so the resolver pre-push gate fails in the review container"
status: completed
type: bug
priority: critical
tags:
  - flow
  - tests
  - review-loop
  - holon-agentic-coder
created_at: 2026-11-12T05:00:00Z
updated_at: 2026-11-12T05:00:00Z
---

## Problem

`tests/flow/stages/test_children.py::TestChildLoopWithStubbedPipelines::test_child_payload_fallbacks_and_copies` does
not stub the `git fetch` that `flow/stages/children._run_one_child` runs through `_fetch_refspecs_error` before it logs
`Stage 3: running sub-intent ...`. On the host the fetch works; in the review-loop container (no ssh, ssh origin) it
fails, `_run_one_child` returns early and the expected log line is never written, so the test fails. The resolver's
pre-push gate (`uv run task test`) runs in that container, so it fails on a clean `main` and halts Stage 4 whenever a
review asks for changes. Found 2026-11-12 on the `calci` flow (Bean 0280, PR #173, now on hold): the full suite in the
container fails exactly this one test on both the flow tree and a clean `main` (3,633 and 3,617 passed), and passes on
the host. Bean 0285 (truncated pytest output) hid it.

## Action

Run through the Holon flow; where a stage fails on the gate itself, hand-author the fix on a branch in a dedicated
worktree at the maintainer's instruction (2026-11-12), name the exception in the commit message and keep the 3-ledger
rule. Make the test hermetic by stubbing the fetch, and add a guard that fails any test that runs a real `git fetch`
against a remote (or reaches the network), then run the whole suite in the review-loop image to prove it passes there.

## Follow-up

After it merges: rebuild images, then resume the `calci` flow (Bean 0280) from review.

## Resolution

Delivered via [PR #174](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/174) and merged into `main`
(`a5550b5`):

- **Fix**: the children test no longer makes a real `git fetch`; the pipeline stubs it, and a network guard fixture in
  the suite (`tests/network_guard.py`) fails any test that opens a non-local git remote or socket, so the pre-push gate
  no longer depends on the network.
- **Review**: 3/3 ensemble approval after 8 iterations, in which the resolver gate ran in the container. Reviewer 2's
  open Nit was actioned. A spurious `uv.lock` rewrite from a newer host `uv` was reverted, not shipped.
- **Calibration**: `plans/P-1794458347-aa9e9dfa-claude-agent-claude-sonnet-5-5_calibration.md` in the PR; EV predicted
  35.20 vs actual -13.31.
- **Flow**: all five stages traversed through `holon flow`, resumed three times from partial work (Bean 0287).
