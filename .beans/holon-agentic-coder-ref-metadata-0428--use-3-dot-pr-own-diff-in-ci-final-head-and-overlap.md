---
# holon-agentic-coder-ref-metadata-0428
title: "Use PR-own 3-dot diff instead of 2-dot diff in ci_final_head and touch-set inspection"
status: todo
type: bug
priority: medium
tags:
  - flow
  - stage-3
  - stage-5
  - diff
  - holon-agentic-coder
created_at: 2026-11-24T13:00:00Z
updated_at: 2026-11-24T13:00:00Z
---

## Why

Two-dot `git diff A..B` sweeps in every commit that `main` landed between `A` and `B` across a target-branch merge,
misclassifying a clean merged head as having code edits when only `main` moved.

## Evidence (`2026-11-24T11:05Z–12:47Z` audit)

1. **`apps/sandbox-executor/src/sandbox_executor/flow/github/ci_final_head.py:213`**: `_git_changed_paths` runs
   `git diff --name-only {approved}..{head} --`. When `origin/main` is merged into the PR branch between `approved` and
   `final` (as in `holon-agentic-coder#270` at `11:29:55Z`, commit `c341f784`, where `unit (ubuntu-latest)` then failed
   the timing gate at `360 s > 344 s`), `{approved}..{head}` includes all non-bookkeeping files from `main`, causing
   `_bookkeeping_only(paths)` (`line 230`) to return `False` and blocking `_retry_timing_noise` even though the PR's
   `approval_fingerprint` is unchanged.
2. **2-dot vs 3-dot touch-set inspection on active PRs**:
   - On `PR #273` (`resolve-conflicts-in-flow`), `git diff --name-only origin/main..head` (2-dot) reports **407** files
     (**190** extra `main` files such as `README.md` and `models.py`), vs **217** files with 3-dot `origin/main...head`
     (which `gh pr diff` in `in_flight.py` correctly uses).
   - On `PR #275` (`unit-suite-slowest-tests-speedup`), 2-dot reports **33** files (**14** extra `main` files including
     `preflight.py`, `test_preflight.py`, `test_preflight_retries.py`), vs **19** files with 3-dot.
3. **Shared test-file overlap waits in this window**:
   - Bean `0399` (`ci-wait-fast-poll-and-early-fail`) has been blocked for **65.3 min** (`11:42:16Z`–`12:47:33Z`) on
     `PR #273` (`test_calibrate_final_head_ci.py`, `test_review_ci_wait.py`).
   - Bean `0265` (`split-cli-init-modules`) was blocked for **17.7 min** (`12:29:50Z`–`12:47:33Z`) first on `PR #274`
     (`test_preflight.py`) and local flow `0405`, then on `PR #275` (`test_url_credential_redaction.py`) because its
     plan listed 10+ unrelated test files for `mock.patch` target rewrites.

## Proposed change

1. In `ci_final_head.py`, replace the raw 2-dot `{approved}..{head}` check in `_eligible_run_ids` with a PR-own diff
   comparison (e.g. `approval_fingerprint` match or `changed_paths` ignoring content that arrived only from
   `origin/main` merges), so mechanical `main` merges remain eligible for `_retry_timing_noise` when only timing-gate
   variance fails.
2. Document and enforce 3-dot (`origin/main...head`) semantics in any touch-set inspection or harness overlap helper so
   `main` commits are never misattributed to an open branch.
3. Add a regression test in `tests/test_calibrate_final_head_ci.py` where `origin/main` merges code commits into a
   bookkeeping-unchanged PR and a timing-gate failure still triggers `_retry_timing_noise`.

## Expected gain

Prevents false consensus withdrawals on merged-head timing-gate variance (like `PR #270` at `11:37:55Z`) and eliminates
2-dot diff noise during overlap and touch-set inspection.

## Cost

Small target-repo change in `ci_final_head.py` + tests via the Holon flow.
