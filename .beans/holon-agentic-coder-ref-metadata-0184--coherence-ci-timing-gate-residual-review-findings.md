---
# holon-agentic-coder-ref-metadata-0184
title: "holon-coherence CI timing gate: fix the residual review findings that merged with PR #30"
status: completed
type: bug
priority: high
tags:
  - holon-coherence
  - ci
  - review-loop
created_at: 2026-10-29T12:00:00Z
updated_at: 2026-10-29T12:31:00Z
---

## Problem

holon-coherence PR #30 (CI timing gate, Bean 0163) was merged as `6d9dae7` (2026-10-29T11:40:26Z) while findings were
still open. The harness review loop had been paused at iteration 5 (ensemble at `f6a2a7e`), and the only review posted
on the PR is holon's native Stage 4 report (review 5694137530, verdict `FAILED`: 2 of 3 reviewers completed, one timed
out at its 300 s budget). Open findings, all in `scripts/ci_timing_gate.py`:

| Source                                 | Severity  | Location | Finding                                                                                                                                                                                  |
| -------------------------------------- | --------- | -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Native Stage 4, reviewer 1             | Important | `:331`   | The live PR label query uses the Issues API (`/issues/{number}/labels`), which needs `issues: read`; under the workflow's permissions it returns 403, so the override label cannot work. |
| Native Stage 4, reviewer 1             | Nit       | `:376`   | `--pr-number` uses a raw `type=int`; an empty string (`--pr-number ""`, as an unset expression renders) crashes argparse.                                                                |
| Harness iteration 5, reviewer 1 (E1-1) | Nit       | `:372`   | `--baseline-count` accepts 0 or negative values and crashes.                                                                                                                             |

## Scope

- Through the Holon flow on holon-coherence: grant the minimal permission the label lookup needs (or read labels from
  the pull-request event payload / the Pulls API instead), make `--pr-number` tolerate an empty value, and reject
  non-positive `--baseline-count` with a clear error.
- Tests (pytest only): 403 from the label API is handled, empty `--pr-number`, non-positive `--baseline-count`.
- Check whether the holon-agentic-coder gate (PR #109, merged `993b686`) has the same label-permission defect, and fix
  it there through its own flow if so.

## Notes

- Also from the same merge window: holon-agentic-coder PR #108 (Bean 0171) merged as `c7dfd5e` before its consensus
  review was posted and before Stage 5 calibration ran; its execution branch is gone, so it has no calibration report.
- Lesson: a paused loop's PR shows no "do not merge yet" signal on GitHub. Bean 0182's event watcher (or a PR draft
  state while a loop runs) would make this visible.

## Progress (2026-10-29)

- Resolved by the resumed post-merge review loop at the maintainer's instruction (hand-authored, named in the commit):
  follow-up holon-coherence PR #32 (https://github.com/Holon-Agentic-Coder/holon-coherence/pull/32), head `e045a69`, 3/3
  blind ensemble approval with zero findings, 7/7 CI green, consensus review 5697506834; pointer comment on #30.
- (a) **Refuted**: the issue-labels endpoint accepts Pull requests read, the repo is public, and real PR runs
  40868392158 / 40868392169 never hit the fallback; a 403 falls back to the event-payload labels (now tested).
- (b) Applied defensively: a blank `--pr-number` means "no PR"; non-numeric still errors.
- (c) and D6-1 applied: `--baseline-count` and `--test-limit` reject 0, negatives and non-integers.
- D6-2 applied: tests for the 403 fallback, the redirect without `Authorization`, and a re-raised 404.
- holon-agentic-coder gate (#109): not affected (reads labels from the event payload).
- Close this bean when PR #32 merges.

## Summary of Changes (2026-10-29)

Resolved by holon-coherence PR #32, merged by the maintainer as `cefebe3`: blank `--pr-number` tolerated,
`--baseline-count` and `--test-limit` range-checked, and the 403 fallback and download redirect tested. The claimed
Important (label lookup needing `issues: read`) was refuted with evidence. Hand-authored at the maintainer's explicit
instruction as the post-merge follow-up to PR #30.
