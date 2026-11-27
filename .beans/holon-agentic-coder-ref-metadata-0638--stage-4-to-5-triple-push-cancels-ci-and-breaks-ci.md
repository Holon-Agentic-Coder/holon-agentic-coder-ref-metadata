---
# holon-agentic-coder-ref-metadata-0638
title: "Stage 4-to-5 triple push cancels CI and breaks ci_merge_push_gate on carry-over"
status: in-progress
type: bug
priority: high
tags:
  - holon-agentic-coder
  - ci
  - stage-5
  - performance
created_at: 2026-11-27T15:53:29Z
updated_at: 2026-11-27T17:18:38Z
---

## Notes

### Evidence (2026-11-27 fifth-merge audit, `holon-agentic-coder@1f3331637`)

- Even after Bean `0454` (`PR #346`, `scripts/ci_merge_push_gate.py`) landed, Stage 4->5 pushes on target-syncing PRs
  still trigger triple rapid pushes within ~12 seconds that cancel intermediate CI and force `stage 5 carry-over` to run
  the full test suite:
  1. **`HAC #425` (`0601`, `self-doc-ast-behavior-gate`):**
     - `12:27:48Z` `e04ed6d3f` `chore(review): record review ledger rows (iteration 2)` -> `12/16` checks cancelled
     - `12:27:56Z` `fa817d52a` `sync: merge target origin/main at c03385aff0d7 (clean)` -> `12/16` checks cancelled
     - `12:28:00Z` `7f119d5fe` `chore(review): record review ledger rows (stage 5 carry-over)` -> **full CI (`740 s` /
       `12.33 min`, `unit (macos-latest, shard 1 of 2)` `350 s`)**!
  2. **`HAC #426` (`0153`, `self-doc-tests-49`):**
     - `12:35:13Z` `3021df5a1` `chore(review): record review ledger rows (iteration 1)` -> `11/15` checks cancelled
     - `12:35:21Z` `a42f26309` `sync: merge target origin/main at c03385aff0d7 (clean)` -> `6/10` checks cancelled
     - `12:35:25Z` `659c18787` `chore(review): record review ledger rows (stage 5 carry-over)` -> **full CI (`509 s` /
       `8.48 min`)**!
- Root cause: `ci_merge_push_gate.py` requires BOTH (a) `head_sha` itself to be a 2-parent merge commit and (b) its
  `before` SHA to have completed green CI. Because Stage 5 pushes `sync: merge target` (`fa817d52a`) and 4s later pushes
  a 1-parent `chore(review): stage 5 carry-over` (`7f119d5fe`), `fa817d52a` is cancelled (not green) and `7f119d5fe` is
  not a 2-parent merge commit, so BOTH `ci_bookkeeping_gate.py` and `ci_merge_push_gate.py` miss the fast-path and run
  full CI, followed by a second CI wait on `chore(calibration)` (`114–135 s`), pushing Stage 5 over its 10-minute budget
  (`14.9 min` on `#425`, `11.7 min` on `#426`).

### Proposed Change

1. Batch Stage 4 iteration ledger rows, Stage 5 `sync: merge target`, and `stage 5 carry-over` (or calibration commits,
   coordinating with Bean `0383`) into a single push instead of 3 pushes in 12s.
2. Extend `scripts/ci_merge_push_gate.py` / `scripts/ci_bookkeeping_gate.py` so a bookkeeping commit (`chore(review):`)
   stacked directly on a clean `sync: merge target` commit evaluates the combined `(last_green_head..head_sha)`
   equivalence (verifying only bookkeeping + green `origin/main` changed and the PR-own diff matches the last green
   head).

### Expected Gain & Cost

- Eliminates `~12–24` cancelled check-runs per PR and saves **`7–12 min`** of Stage 5 CI wait per target-syncing flow
  (`#425` `12.3 min`, `#426` `8.5 min`).
- Cost: small push consolidation in Stage 4/5 + merge-plus-bookkeeping check in `ci_merge_push_gate.py` + unit tests.

## Acceptance Criteria

- [ ] Stage 4->5 transition pushes at most once before Stage 5's CI gate (no back-to-back `iteration` -> `sync` ->
      `stage 5 carry-over` pushes cancelling each other's CI).
- [ ] `ci_merge_push_gate.py` skips heavy CI when a clean `sync: merge target` + bookkeeping commit chain preserves an
      unchanged PR-own diff against a green prior head and green `origin/main` commit.
- [ ] Hermetic tests cover the combined merge+bookkeeping push case; `uv run pytest` passes.

## Flow

- **Slice 1 (`2026-11-27`, `ci-merge-bookkeeping-chain`):** Covers AC #2 (`ci_merge_push_gate.py` /
  `ci_bookkeeping_gate.py` / `ci_bookkeeping_chain.py` / `ci_main_push_gate.py` handling a bookkeeping commit chain
  stacked on a clean `sync: merge target` merge commit) and AC #3 (hermetic tests). AC #1 (Stage 4->5 single push
  consolidation) is deferred to Slice 2 (`todo/intent-coverage-0638.json`).
  - Closed halted [PR #436](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/436) (`CF-0076`: Stage 4
    `touch_set_violation` on `scripts/ci_main_push_gate.py` and `apps/sandbox-executor/tests/test_ci_main_push_gate.py`
    while fixing `R2-F1`, plus Python 3.9 `R3-F1`), expanded scope to 9 files, and relaunched cleanly.

## Resolution
