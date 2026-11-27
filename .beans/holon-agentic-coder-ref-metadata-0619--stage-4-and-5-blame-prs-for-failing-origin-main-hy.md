---
# holon-agentic-coder-ref-metadata-0619
title: "Stage 4 and 5 blame PRs for failing origin/main hygiene baseline and withdraw approvals"
status: in-progress
type: bug
priority: high
tags:
  - flow
  - ci
  - holon-agentic-coder
created_at: 2026-11-27T07:49:17Z
updated_at: 2026-11-27T16:18:16Z
---

## Notes

### Evidence (2026-11-27T07:49Z fifth-merge audit)

- `holon-agentic-coder#404` (`05:13:02Z`) and `#405` (`05:13:20Z`) merged to `origin/main` with `Test - Hygiene` failing
  (`45944464931` and `45944497911`: `apps/sandbox-executor/src/sandbox_executor/knowledge/wisdom.py` `386 > 350` lines).
  `origin/main` stayed red on `hygiene` for `2 h 11 min` until `#403` merged at `07:24:46Z`.
- During that window, syncing `origin/main` in Stage 4/5 poisoned 6 concurrent flows:
  - `#403` (`tests-46`), `#406` (`tests-48`), `#407` (`tests-51`), `#409` (`tests-45`) all received
    `3/3 APPROVED (0/0/0)` from reviewers yet hit `FIND-CI-003`/`FIND-CI-004` on Iter 3–4, adding **8 extra
    review/resolver churn iterations** (`~90+ min`) and forcing 4 unrelated test-cleanup PRs to split `wisdom.py`
    out-of-scope (causing cross-PR merge conflicts).
  - `#408` (`tests-49`) had already reached `3/3 APPROVED` on `abcd50c7` (`04:49:18Z`), synced broken `origin/main` at
    `05:31:57Z` (`9773e1d15`), failed `hygiene` (`45944550433` `Check module budgets`), had consensus withdrawn
    (`05:47:05Z`), and entered `CF-0043`.
  - `#410` (`0596`, `diff-stays-in-intent-scope`) halted in Stage 4 (`CF-0040`) on `wisdom.py`.
  - `#411` (`0558`) spent Step 4 of Stage 3 splitting `wisdom.py` out-of-scope (`e33a0cc0`).
- Distinct from `0493` (re-check open PRs after a budget-tightening merge), `0498` (live-tree budget unit test), and
  `0497` (ensemble re-runs on unfixable CI failures): Stage 4/5 lacks any `origin/main` baseline health check before
  syncing `main` or routing `FIND-CI` to a PR resolver.

### Proposed Change

- Before syncing `origin/main` into a PR branch in Stage 4/5 and when routing `FIND-CI` failures in `ci_routing`:
  1. Check `origin/main`'s latest `hygiene` (and `unit`) check status; if `origin/main` itself is red on a check whose
     failing path was not touched by the PR's own diff, do **not** sync broken `origin/main` into an already-approved PR
     and do **not** withdraw existing consensus (`#408`).
  2. Classify inherited `origin/main` failures as `blocked_on: "main-baseline-failing"` rather than PR defects, refusing
     to dispatch the PR's resolver to patch unrelated `main` modules out-of-scope.

### Expected Gain & Cost

- Eliminates cascading `8+` churn iterations, withdrawn approvals (`#408`), Stage 4 halts (`#410`), and redundant
  out-of-scope edits across unrelated PRs whenever a broken commit lands on `main`.
- Cost: small `origin/main` CI-status lookup in target sync / `ci_routing` + unit tests.
- parked 2026-11-27 (`stage4-main-baseline-guard`): halted in Stage 3 after 2 re-plans on omitted
  `flow/lazy_exports_review.py` (`CF-0067`); expanded intent scope upfront to all 11 modules and queued behind Bean
  `0607` (`lazy_exports_review.py`) and Bean `0535` (`flow/review/loop.py`).

## Acceptance Criteria

- Before syncing `origin/main` into an already-approved PR in Stage 4/5 or routing `FIND-CI` to a PR resolver, Stage 4/5
  inspects `origin/main`'s latest `hygiene` (and `unit`) check status; if `origin/main` itself is red on a check whose
  failing path was not touched by the PR diff, Stage 4/5 refuses to sync broken `origin/main` or withdraw existing
  consensus.
- Inherited `origin/main` baseline failures are classified as `blocked_on: "main-baseline-failing"` rather than PR
  defects, refusing to dispatch the PR resolver to edit unrelated `main` files out-of-scope.
- Unit tests in `apps/sandbox-executor/tests/flow/review/test_main_baseline_guard.py` prove the guard with
  `uv run pytest`, `uv run task lint` passes, and self-explaining code invariant holds.

## Resolution
