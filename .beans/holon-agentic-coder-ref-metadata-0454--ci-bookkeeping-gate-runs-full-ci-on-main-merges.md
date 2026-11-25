---
# holon-agentic-coder-ref-metadata-0454
title: "ci_bookkeeping_gate triggers full 7-workflow CI on mechanical Merge origin/main PR pushes"
status: todo
type: feature
priority: high
tags:
  - ci
  - pipeline
  - performance
  - merge-conflicts
  - holon-agentic-coder
created_at: 2026-11-25T05:41:00Z
updated_at: 2026-11-25T05:41:00Z
---

# `ci_bookkeeping_gate` triggers full 7-workflow CI on mechanical `Merge origin/main` PR pushes

## Summary

`scripts/ci_bookkeeping_gate.py:114-148` uses `compare(client, base, head_sha)` (`2-dot` `before..head_sha` GitHub
compare), which sweeps in every file `origin/main` changed since the PR branched whenever a conflict-resolution or
target-sync commit merges `origin/main`. Every mechanical pre-merge `Merge origin/main` push therefore runs the full
`7`-workflow CI suite (`~7.1–9.1 min`) even when the PR's own non-bookkeeping diff vs `origin/main` is unchanged
(`pr_own_identical=True`) and `origin/main` already ran CI.

## Evidence

- **Cadence PRs `#295–#299` and queue merges (`2026-11-25T04:57Z–05:38Z`):**
  - All `5` post-calibration `Merge remote-tracking branch 'origin/main'` pushes triggered full CI across `531–571`
    `2-dot`-changed files (`238–248` non-bookkeeping) while `pr_own_identical=True`:
    - `hac#295` (`f3caa65e`, `04:57:36Z..05:05:33Z`, `7.95 min`, merged early at `04:59:58Z` before `Unit`/`Stress`
      finished).
    - `hac#297` (`dfaf36cc`, `05:04:12Z..05:12:49Z`, **`8.62 min`**, merged at `05:09:36Z` while `Unit`/`Stress` ran).
    - `hac#298` (`79e0ab33`, `05:11:05Z..05:18:09Z`, **`7.07 min`**, merged at `05:12:10Z` with `4/7` checks running).
    - `hac#299` (`821656a1`, `05:13:57Z..05:22:03Z`, **`8.10 min`**).
    - `hac#300` (`a4e23b9e`, `05:23:06Z..05:32:13Z`, **`9.12 min`**).
  - Across `#295–#299` full lifetimes, `6/30` (`20%`) tested CI heads were `main_merge` heads (`27/30 = 90.0%` total
    churn incl. `21` bookkeeping/conflict heads), and `8` open PRs (`#302–#308`) remain queued behind additional
    `Merge origin/main` cycles (`cf7c77f6` on `#301` already ran at `05:32:56Z`).
- **Mechanism:** `apps/holon-agentic-coder/main/scripts/ci_bookkeeping_gate.py:114-148` inspects only `before..head_sha`
  (`compare`), never checking whether `head_sha` is a merge with `origin/<base>` whose resolved PR-own diff matches an
  earlier green head.

## Proposed Change

1. First let Bean `0371` eliminate ledger-only `Merge origin/main` pushes across disjoint PRs (highest-leverage root
   fix).
2. For remaining clean target merges (e.g., `end_of_flow_sync` or non-overlapping `origin/main` updates), evaluate a
   safe fast-path in `ci_bookkeeping_gate.py` (always keeping `Test - Hygiene` active for merge markers / Prettier /
   JSONL):
   - Note correctness constraint: merging new `origin/main` code with existing PR code _can_ interact semantically
     (callers/imports), so never skip blindly when both `origin/main..main` and PR code touch coupled symbols/tests;
     safely skip expensive jobs (`Docker Build`, redundant matrix legs, or full tests) only when `origin/main` changes
     since the prior base were limited to bookkeeping/docs/unrelated modules or after `origin/main` itself passed CI and
     both sides' touched packages are disjoint.
3. Add unit tests in `tests/` covering `ci_bookkeeping_gate` behavior on merge commits (skipping only under safe
   provenance conditions and running full CI whenever merge resolution edits code).

## Expected gain

Saves `~7–9 min` of runner compute and queue latency per mechanical `Merge origin/main` push across multi-PR queues (`8`
open PRs in current queue).

## Cost

Medium: merge-parent & disjoint-scope verification in `scripts/ci_bookkeeping_gate.py` / `ci_bookkeeping_api.py` + unit
tests via `holon flow` (`holon-agentic-coder`).

## Notes

- Target repo change through `holon flow` (`holon-agentic-coder`).
- Related: Bean `0371` (per-flow ledger fragments prevent most queue merges), Bean `0403` (`ci_bookkeeping_gate`), Bean
  `0407` (approval survives target merge), Bean `0428` (3-dot PR-own diff in `ci_final_head.py`).
- Audit source: `2026-11-25T05:41Z` fifth-merge self-improvement audit (`#295–#299`).
