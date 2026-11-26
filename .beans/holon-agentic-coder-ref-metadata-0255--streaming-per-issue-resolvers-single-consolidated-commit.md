---
# holon-agentic-coder-ref-metadata-0255
title: "Streaming per-issue resolvers during Stage 4 CI & review with single consolidated commit"
status: todo
type: feature
priority: critical
tags:
  - flow
  - review-loop
  - stage-4
  - ci
  - resolver
  - concurrency
  - holon-agentic-coder
created_at: 2026-11-09T12:17:00Z
updated_at: 2026-11-24T11:12:00Z
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

## Audit (2026-11-21)

Still valid. Locations moved: the loop is `run_review_loop` in `flow/review/loop.py` and CI waiting is
`wait_for_pending_ci` in `flow/github/ci_wait.py` (the `sandbox_executor.flow` module reference above means the `flow/`
package). Overlaps Beans 0192 and 0345 on `flow/review/loop.py`.

## Maintainer direction (2026-11-24)

Maintainer's words: "in the review process, we shouldn't wait for the whole pipeline to finish. we should start on a new
iteration to fix the issue. that way we don't have to idle. while we're on the next iteration to fix the pipeline it
should also refer back to the complete pipeline failures so that we fix ALL the failing tests from the previous
iteration."

This confirms the decision above and makes two points binding:

1. **Never idle on a pipeline that has already failed.** The first failed check starts the fixing work at once; the flow
   does not wait for the remaining checks before the resolver begins (the fail-early rule of Beans 0383 and 0394).
2. **The fix covers the whole run, not only the first failure.** While the resolver works, the flow keeps collecting the
   results of that same pipeline run, and the resolver is given every failure of the run (each failed check, its failing
   tests and their output) before its fix is pushed. One push answers all the failures of the previous iteration, so the
   next pipeline run is not spent rediscovering the second and third failure.

Consequences to design for (agent's notes):

- **Do not cut the evidence short.** A push to the branch cancels the pipeline run in progress (`cancel-in-progress` is
  on for pull requests), which would throw away the failures not yet reported. The resolver's push therefore waits until
  the run it is fixing has finished or every one of its jobs has reported, whichever is first. The work starts early;
  only the push waits.
- **`fail-fast` stays off** on the test matrices for the same reason: a failed leg must not cancel its siblings, or the
  complete list of failures is never produced (this settles the `fail-fast` question left open in Bean 0400).
- **The failure list is carried in the checkpoint**, per head: check name, job, failing test ids and the tail of the
  log. A resumed flow, and the next iteration, read it from there and do not depend on the run still being retrievable.
- **Reproduce locally where possible.** The resolver runs the failing tests it was given in its own worktree, so it can
  confirm each fix before the push and does not need the pipeline to find out.
- **Noise is told apart from failures first**: a timing-gate or runner failure is not handed to the resolver as a defect
  (Beans 0404 and 0407); it is rerun.
- **Reviewer findings join the same push**: findings that arrive while the resolver is working are added to its list, as
  the decision above already says, so one consolidated commit answers reviewers and pipeline together.

Measured motivation (self-improvement audit, 2026-11-24): the review stage carried 9.2 hours of idle time in three days;
33 pipeline heads failed and each cost at least one more full run of about 8 minutes; the median pull request took 6
pipeline runs.
