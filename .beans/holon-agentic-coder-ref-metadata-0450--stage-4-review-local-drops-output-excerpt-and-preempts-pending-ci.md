---
# holon-agentic-coder-ref-metadata-0450
title:
  "Stage 4 review_local drops TestMeasurement.output_excerpt and preempts pending GitHub CI with slow host test runs"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-4
  - testing
  - ci
  - observability
created_at: 2026-11-25T05:07:00Z
updated_at: 2026-11-25T05:41:00Z
---

# Stage 4 `review_local` drops `TestMeasurement.output_excerpt` and preempts pending GitHub CI with slow host test runs

## Summary

When any reviewer objects in Stage 4 (`flow/review/loop.py:374-386`), the review loop probes GitHub CI once without
waiting for pending checks (`ci_status.get("pending", 0) > 0`). Because `_is_ci_head_passing` in
`head_test_evidence.choose_evidence` requires `pending == 0`, pending GitHub CI immediately forces
`TEST_SOURCE_REVIEW_LOCAL` (`uv run task test` on the host OS). When that host run fails, `local_tests.py:163-176` and
`review_report.py:126-137` discard `TestMeasurement.output_excerpt` and failing test node IDs — passing only
`"CI checks failed in iteration N"` + `"rate 0.99986996, failed=1"` to the resolver, forcing blind diagnosis across
`7,690` tests.

## Evidence

- `apps/sandbox-executor/src/sandbox_executor/flow/review/loop.py:374-386`: `if reviewer_objected:` performs a single
  non-waiting CI lookup (`ci_status.get("pending", 0) > 0`), causing `head_test_evidence.choose_evidence`
  (`pending == 0` required in `_is_ci_head_passing`) to fall back immediately to `TEST_SOURCE_REVIEW_LOCAL`, running
  `uv run task test` on the host.
- `apps/sandbox-executor/src/sandbox_executor/flow/review/local_tests.py:163-176`:
  `detail = outcome.measurement.run_error or f"rate {rate}, failed={failed}"` omits `outcome.measurement.output_excerpt`
  from logs and `executions.jsonl`.
- `apps/sandbox-executor/src/sandbox_executor/review_report.py:126-137`: `ci_failure_finding` emits
  `summary=f"CI checks failed in iteration {iteration}{names}."` without attaching `output_excerpt` or failing test
  names.
- **`holon-agentic-coder#308` (`workspace-survival-job-parallel`, 2026-11-25T03:43Z–05:01Z):**
  - Ran `3` host `review_local` suites (`~8.56 min` total: pre-window `03:43:39Z..03:46:26Z`; Round 2 Iter 1
    `04:19:05Z..04:21:54Z`, `2.82 min` on `1a6c1ab1`; Round 2 Iter 2 `04:53:29Z..04:56:21Z`, `2.87 min` on `31fdc482`).
  - Both Round 2 host runs failed `1` macOS host test out of `7,690` (`7689/7690`, `rate 0.99986996`), an
    environment-specific failure unseen in Linux Docker CI (`7692/7692` passing), while GitHub CI on the PR was still
    running/pending.
  - Because `FIND-CI` omitted which test failed and its traceback, the resolver spent **`27.02 min`** in Round 2 Iter 1
    (`04:21:54Z..04:48:55Z`) and **`4.47 min`** in Round 2 Iter 2 (`04:56:21Z..05:00:49Z`) probing and writing `FIND-CI`
    diagnostics to `executions/E-*.md` (`3595c1f1`, `54321e50`) without resolving the host test or reviewer objections.

## Proposed Change

1. Preserve `outcome.measurement.output_excerpt` and parsed failing test node IDs/names in `local_tests.py` (logs +
   `executions.jsonl`) and include a concise failure excerpt in `ci_failure_finding` (`review_report.py`) so the
   resolver never gets a blind `"failed=1"` finding.
2. In `flow/review/loop.py:374`, when `reviewer_objected` and GitHub CI already has matching checks running
   (`pending > 0`) on the reviewed head (and reviewers did not specifically pass on code), prefer waiting briefly for
   the pending GitHub CI check status (or defer test verification when an objecting review will already trigger resolver
   edits that supersede the head) instead of eagerly launching a `~2.9 min` host-OS `uv run task test` fallback.
3. Add unit tests verifying `local_tests.py` / `review_report.py` propagate `output_excerpt` into `FIND-CI` and
   `loop.py` avoids redundant host runs while GitHub CI is pending.

## Expected gain

Saves `~2.8–2.9 min` per objected iteration on host test fallbacks, removes false macOS-host `1/7690` test blockers that
pass in Linux Docker CI, and eliminates multi-minute blind resolver diagnosis (`27.02 min` in `PR #308` Round 2 Iter 1).

## Cost

Small-to-medium: excerpt propagation in `local_tests.py` / `review_report.py` + pending-CI handling in `loop.py` with
unit tests, delivered via the Holon flow (`holon-agentic-coder`).

## Notes

- Target repo change through the Holon flow (`holon-agentic-coder`).
- Related: Bean `0412` (step timing and structured diagnostics), Bean `0449` (`FIND-CI` doc-only commits resetting
  `unchanged_streak`).
- Audit source: `2026-11-25T05:07Z` fifth-merge self-improvement audit.

## Audit evidence, 2026-11-25T05:41Z (self-improvement audit, fifth merge #295–#299)

- **`holon-agentic-coder#308` Round 2 Iter 3 & Iter 4:** host `review_local` failed **`4/4` times** on `1` test
  (`FIND-CI-003` at `05:09:01Z`, `2.82 min`, `1/7755`, `rate 0.99987105`; `FIND-CI-004` at `05:25:12Z`, `3.90 min`,
  `1/7788`, `rate 0.99987160`) while Linux/macOS CI passed `7788/7788` and container `uv run task test` passed
  `7757/7757`.
- Iter 3 resolver log (`todo/flow-workspace-survival-job-parallel.log:878`) identified the host-only failure as
  `tests/test_ledger_append_only.py::test_repository_ledgers_survive_precheck_and_reconcile_byte_for_byte` (lines
  `469-488` checksum live `REPO_LEDGER_DIR` before/after running, passing in isolation and CI but failing under host
  `-n auto` `review_local`).
- In Iter 4, **GitHub CI on `c960579d` completed `11/11` green at `05:24:25Z`, `47 s` BEFORE host `review_local`
  reported `failed=True` at `05:25:12Z`**, proving `review_local` does not even re-check GitHub CI completion before
  emitting `FIND-CI` and dispatching a live resolver (`05:25:12Z..05:40:24Z+`).
