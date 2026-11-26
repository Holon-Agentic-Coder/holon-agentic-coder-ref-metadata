---
# holon-agentic-coder-ref-metadata-0403
title: "No full CI run for commits that only touch bookkeeping files"
status: in-progress
type: feature
priority: high
tags:
  - ci
  - flow
  - performance
  - holon-agentic-coder
created_at: 2026-11-24T08:30:00Z
updated_at: 2026-11-25T03:08:00Z
---

## Problem

Stage 4's ledger rows and Stage 5's calibration commits touch only `plans/`, `executions/` and `holon-knowledge/`. They
cannot change a test result, yet each push of them starts the whole pipeline (median 7.9 minutes) and the flow waits for
it. No workflow has a path filter today. This is the second CI wait of every Stage 5.

## Goal

- A push whose changes since the last fully tested commit lie only in those paths finishes its required checks in
  seconds: path filters with a matching always-green job for each required check, or one gate job that decides and skips
  the rest.
- The engine may equally treat such a head as covered by the last full run and not wait at all; pick one mechanism and
  make the other consistent with it.
- A change outside those paths, however small, always gets the full pipeline. The rule is tested with a mixed commit.
- Formatting checks that do apply to these files (Prettier on the calibration report) still run.

## Notes

- Logged from Bean 0394 (no unnecessary waiting in the holon flow), on the maintainer's word of 2026-11-24. Split out of
  Bean 0383 (Goal 2) so it can run by itself: it changes the workflow files, not the flow engine.
- Saves about 8 minutes in every flow.

## Progress

- 2026-11-24: flow `ci-skip-bookkeeping-only-pushes` launched (`claude-agent` / `claude-fable-5-2`). Design chosen: an
  in-job gate, not workflow path filters, because on pull request events GitHub evaluates path filters against the whole
  pull request diff. The main ruleset has no required status checks, so job names are kept only for continuity.

- 2026-11-24 21:10Z: PR #272 merged (`4c82c0f`) through the merge queue. The gate (`scripts/ci_bookkeeping_gate.py`, the
  composite action, six workflow wirings, 225 tests) is on `main`. Not closed: the live effect is not yet shown. On PR
  #272 the calibration and reconciliation pushes had no workflow runs at all, and the promotion push fell back to a full
  run (unit macOS 259 s). The engine-side wait is not changed by this PR. Next step: confirm on a real bookkeeping-only
  push that every job finishes in seconds. Flow worktree and branches pruned after post-merge; backup in
  `todo/post-merge-backups/ci-skip-bookkeeping-only-pushes-2026-11-25.bundle`.

## Measured (self-improvement audit 2026-11-24)

From GitHub check runs of the 47 pull requests merged 2026-11-21 to 2026-11-24 (both target repositories; scripts in the
git-ignored `todo/self-improvement-audit-2026-11-24/`, `pipelines.py`): 422 pipeline runs, 230 of them (55 percent) on
heads whose diff against the previous tested head lies only in `holon-knowledge/`, `plans/` and `executions/`. Every
pull request had at least two such runs; PR #263 had 11, PR #267 and #268 had 9 each. 14 of these bookkeeping-only heads
failed a check anyway: 7 involving `hygiene` (Prettier on engine-written `executions/E-*.md` and calibration reports,
Bean 0408) and 8 involving `unit` (mostly the macOS timing ceiling, Bean 0404), each of which withdrew or delayed an
approval of unchanged code. The Stage 4 ledger commit (148 in the logged flows) is the main source.

## Audit evidence, 2026-11-25T02:54Z (self-improvement audit, fifth merge)

- Verified live effect across `22` post-Stage-3 bookkeeping heads in `2026-11-25T00:28Z–02:54Z` (`#278`, `#298`–`#307`,
  `#296`): `Test - Unit` skipped in `13–23 s`, `Test - Stress` in `9–19 s`, `Test - Integration` in `11–16 s`,
  `Docker Build` in `9–18 s`, `Run Make` in `11–23 s`, and `Test - Hygiene` finished in `38–62 s`, dropping Stage 5
  `final_head_ci` wait across `13` runs to a median of `0.82 min` (`max 1.81 min` on `#296`) vs `7.92 min` on
  `merged_head_ci`.
- Remaining gap: when Stage 4 pushes `chore(review): record review ledger rows` `9–12 s` after a resolver or
  conflict-gate push (`#296`, `#305`, `#306`), the earlier head's CI is cancelled before finishing, so the ledger-row
  push cannot skip CI and runs the full `6–9 min` suite anyway; tracked in Bean `0443`.

## Evidence (audit 2026-11-26T10:50Z)

Heads that ran full CI per PR (unit workflow runs, all green): #325 8 (19 commits), #326 14 (22), #327 7 (17), #329 3
(9), #330 5 (13), #331 7 (15): 44 heads, 0 failed unit runs, so every extra head was bookkeeping or review-resolver
churn. Each head also runs six other workflows.
