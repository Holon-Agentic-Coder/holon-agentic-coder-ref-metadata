---
# holon-agentic-coder-ref-metadata-0449
title:
  "Stage 4 unchanged_streak keys on raw head_sha and ignores open findings, letting target sync / doc-only commits loop
  indefinitely"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-4
  - review-loop
  - convergence
created_at: 2026-11-25T05:07:00Z
updated_at: 2026-11-25T05:07:00Z
---

# Stage 4 `unchanged_streak` keys on raw `head_sha` and ignores `open` findings, letting target sync / doc-only commits loop indefinitely

## Summary

Stage 4 convergence detection (`unchanged_streak` in `flow/review/loop.py:568-578`) requires
`current_sha == prev_head_sha` in addition to `current_sigs == prev_finding_sigs`. Whenever target-branch
synchronization merges `origin/main` or the resolver makes a bookkeeping/doc-only commit (such as writing a `FIND-CI`
section in `executions/E-*.md` with zero code diff), `head_sha` changes and resets `unchanged_streak` to zero — allowing
an unresolvable set of `open` reviewer findings to loop indefinitely through full reviewer ensembles, local test runs,
and resolver turns.

## Evidence

- `apps/sandbox-executor/src/sandbox_executor/flow/review/loop.py:568-578`:
  - `current_sigs = frozenset(...)` and `current_sha = (resolved_target.head_sha if resolved_target else "") or ""`.
  - `if current_sigs and current_sigs == prev_finding_sigs and current_sha == prev_head_sha: unchanged_streak += 1`
    resets `unchanged_streak` on **any** `head_sha` bump, including `origin/main` target merges (`bd581a65`) and
    resolver commits touching only `executions/E-*.md` (`3595c1f1`, `54321e50`) while leaving all reviewer findings
    `open`.
- **`holon-agentic-coder#308` (`workspace-survival-job-parallel`, Round 2, 2026-11-25T04:14:18Z–05:04:00Z+, `49.6+ min`
  and still live in Iter 3):**
  - Reviewer findings `R1-F1`/`R2-F1`/`R3-F1` required maintainer intent re-scope beyond Stage 4's authority, so the
    resolver left them `open` across both Round 2 Iter 1 (`04:21:54Z..04:48:55Z`, `27.02 min`) and Iter 2
    (`04:56:21Z..05:00:49Z`, `4.47 min`), changing only `executions/E-*.md` (`3595c1f1`, `54321e50`) and merging
    `origin/main` (`bd581a65`).
  - Because raw `head_sha` changed on those non-code commits, `unchanged_streak` failed to trip and dispatched Iter 3 at
    `05:01:27Z` (`49.6+ min` spent on `3` iterations with zero code change on the PR).

## Proposed Change

1. Compute `unchanged_streak` against `(reviewer_finding_sigs, pr_own_code_diff_fingerprint)` rather than raw `head_sha`
   (reusing the PR-own code diff fingerprint excl. `holon-knowledge/`, `.holon/`, and target-branch merges), so
   `origin/main` merges and ledger/execution-markdown commits do **not** reset `unchanged_streak`.
2. Halt Stage 4 cleanly for human/maintainer escalation when consecutive iterations produce identical open reviewer
   finding signatures with zero PR-own code diff change (or when the resolver returns with remaining actionable reviewer
   findings left `open` and zero non-ledger/non-doc diff added).
3. Add unit tests covering `run_review_loop` convergence when `origin/main` merges or `executions/E-*.md`-only commits
   advance `head_sha` while `R*-F*` findings stay `open`.

## Expected gain

Prevents `30–50+ min` stalled Stage 4 re-review loops (`49.6+ min` in `PR #308` Round 2 across 3 iterations) when
reviewer objections cannot be solved within Stage 4 scope or only ledger/`origin/main` commits occurred.

## Cost

Small: fingerprint-based streak comparison in `flow/review/loop.py` + unit test, delivered via the Holon flow
(`holon-agentic-coder`).

## Notes

- Target repo change through the Holon flow (`holon-agentic-coder`).
- Related: Bean `0407` (ledger-only sync shouldn't re-enter Stage 4), Bean `0439` (resolver scope guard), Bean `0450`
  (`review_local` `FIND-CI` churn feeding doc-only resolver commits).
- Audit source: `2026-11-25T05:07Z` fifth-merge self-improvement audit.
