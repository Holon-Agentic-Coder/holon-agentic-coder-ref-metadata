---
# holon-agentic-coder-ref-metadata-0255
title: "Streaming per-issue resolvers during Stage 4 CI & review with single consolidated commit"
status: todo
type: feature
priority: high
tags:
  - flow
  - review-loop
  - stage-4
  - ci
  - resolver
  - concurrency
  - holon-agentic-coder
created_at: 2026-11-09T12:17:00Z
updated_at: 2026-11-09T12:20:00Z
---

## Problem

During a Stage 4 review iteration in `sandbox_executor.flow`, CI pipelines finish at vastly different times (e.g.
`Test - Hygiene` fails in ~10s, `Test - Unit` fails at ~2m20s, `Test - Stress` fails at ~4m30s), and the 3-reviewer
ensemble also produces findings asynchronously.

Currently, `run_review_loop()` and `_wait_for_pending_ci()` wait for all reviewers and all pending CI pipelines to
finish before launching a single monolithic resolver pass at the very end of the iteration:

1. **Idle Time on Early Failures**: When `Test - Hygiene` fails after 10 seconds, no resolver starts working on it for
   another 4+ minutes while `Test - Unit` and `Test - Stress` are still running.
2. **Why Failing Fast & Aborting Early Is Also Suboptimal**: If the loop immediately aborted CI polling on the first
   failure (`Test - Hygiene` at 10s) and pushed right away, it would miss the `Test - Unit` failure at 2m20s and the
   `Test - Stress` failure at 4m30s—forcing multiple sequential review/CI rounds instead of fixing every issue in one
   iteration.

## Decision

Implement **streaming, parallel per-issue resolvers** that launch immediately as each pipeline failure or review finding
is detected, while continuing to wait for all CI pipelines and reviewers to complete, and then **consolidate all
resolver fixes into a single commit**:

1. **Immediate Resolver Dispatch per Detected Issue (Streaming Fan-Out)**:
   - While CI checks and the reviewer ensemble are running, poll CI check transitions continuously (building on Bean
     0234).
   - The moment any individual CI pipeline transitions to `fail` (e.g. `Test - Hygiene` at 10s), immediately emit its
     specific finding (`FIND-CI-{iteration:03d}-{check_slug}`) with the failure output and **spin up a dedicated
     resolver** (in an isolated git worktree / patch context) to resolve that specific issue immediately—**without**
     stopping the poll loop for the remaining pending CI pipelines.
   - As subsequent CI checks fail (e.g. `Test - Unit` at 2m20s, `Test - Stress` at 4m30s) or reviewer findings arrive,
     spin up additional resolvers in parallel for each newly discovered issue/finding group.
2. **Wait for All Pipelines and All Spawned Resolvers (Fan-In Barrier)**:
   - Continue tracking all pending CI pipelines until every check has completed (or the iteration budget expires) so no
     secondary failure is missed.
   - Wait for all dispatched per-issue resolvers to finish producing their fixes and dispositions.
3. **Single Consolidated Commit & Push**:
   - Merge/apply the patches from all completed resolvers into the canonical execution branch workspace.
   - Run a single verification pass (`uv run task lint` and `uv run task test`) across the combined working tree (and a
     lightweight conflict reconciliation if two resolvers touched overlapping lines).
   - Record all `ACT-RES` dispositions in `holon-knowledge/ledger/executions.jsonl` and **commit & push everything as a
     single atomic commit** for the iteration (with all resolved `FIND-*` git trailers attached).

## Scope

1. **Streaming CI Watcher & Per-Issue Finding Emission (`sandbox_executor/flow.py` / `flow/github/ci.py`)**:
   - Track individual check state transitions during `_wait_for_pending_ci()` / iteration monitoring.
   - Emit per-check `FIND-CI-{iteration:03d}-{slug}` findings as soon as any check transitions to `fail`, invoking a
     callback/dispatcher immediately while continuing to poll remaining `pending` checks until `pending == 0`.
2. **Parallel Per-Issue Resolver Coordinator (`sandbox_executor/entrypoint/review_loop.py` / `flow.py`)**:
   - Support spawning concurrent resolver runs (each scoped to its issue/finding in an isolated worktree or diff patch
     under the persistent review workspace volume).
   - Collect all resolver patches and `dispositions.json` outputs once all CI pipelines, reviewers, and active resolvers
     have finished.
   - Apply/merge all fixes into the execution branch, verify cleanly, and create **one single commit** and push per
     iteration.
3. **Hermetic Unit Tests (`apps/sandbox-executor/tests/`)**:
   - Verify that when `Test - Hygiene` fails on poll 1 (`pending=2, failed=1`) and `Test - Unit` fails on poll 3
     (`pending=0, failed=2`), resolver #1 is launched immediately at poll 1 without waiting for poll 3, resolver #2 is
     launched at poll 3, all pipelines are awaited, and both fixes are committed together in a single commit.

## Notes

- Target repository: `holon-agentic-coder`.
- Must be executed through the 5-stage Holon flow (`holon flow`).
- Supersedes the naive single-failure abort approach and pairs directly with Bean 0234 (event-driven CI check progress
  reporting) and Bean 0241 (persistent review loop workspace volume).
