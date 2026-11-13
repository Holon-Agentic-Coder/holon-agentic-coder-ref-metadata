---
# holon-agentic-coder-ref-metadata-0292
title: "A red CI check, including a timing gate, blocks the approval and the merge-ready report on the final head"
status: completed
type: bug
priority: high
tags:
  - review-loop
  - stage-5
  - ci
  - holon-agentic-coder
created_at: 2026-11-13T04:30:00Z
updated_at: 2026-11-13T04:30:00Z
---

## Problem

A pull request can carry a posted `Ensemble Consensus Review — APPROVED (3/3)` while a required CI check is red on its
head. Seen on holon-agentic-coder PR #184 (the Stage 5 sync flow), 2026-11-13:

1. At iteration 11 the ensemble approved commit `2e0dcd1` with CI `11 total, 11 passed, 0 failed, 0 pending`, and the
   approval was posted, saying all CI checks are green.
2. Stage 5 then added the calibration report commit, so the head became `310dd9a`. CI reran on that head and
   `unit (macos-latest)` failed its `CI Timing Gate (Check <= 5 min)` step (the job took 6 minutes; every test passed).
3. No comment said the approval no longer held. The flow logged `final head CI: timing gate only: unit (macos-latest)`,
   treated it as non-blocking, finished Stage 5 successfully and reported the PR ready for the maintainer to merge.

Two defects:

- **A timing gate is a failure.** A unit job that exceeds its time limit is a failed check. The "timing gate only"
  classification in the final-head CI check lets a red required check through; the maintainer ruled (2026-11-13) that a
  timeout on a unit job is still a failure.
- **The approval is bound to a head that no longer exists.** The approval text is true for the reviewed commit only.
  When Stage 5 (or anything else) moves the head, the CI claim in the approval is no longer verified, yet the PR still
  reads as approved and ready.

## Goal

1. **No timing-gate exemption**: remove the "timing gate only" tolerance from the final-head CI check. Any failed check,
   including `CI Timing Gate`, fails the final-head check.
2. **Re-verify after the head moves**: after Stage 5 pushes the calibration commit (or any later push), wait for CI on
   the new head, as Stage 4 does. If it is not fully green, do not report the PR as ready to merge: report the failing
   check by name, with the job duration for a timing gate, and either resume the review loop (so the resolver can fix
   it) or stop as blocked. Never end Stage 5 as a success with a red check.
3. **Invalidate the approval on the PR**: when CI on the final head is not fully green after an approval was posted (for
   example the calibration commit triggers a failing check), the flow posts one follow-up comment on the PR saying the
   consensus approval no longer stands, naming the head commit it covered, the head commit now failing, and each failing
   check (with the job duration for a timing gate). The comment is posted once per head, never repeated. When CI on a
   later head is fully green again and the ensemble re-approves, the new approval states its own head. The approval text
   always names the head it covers and the CI result at that commit.
4. **A timing-gate failure is actionable**: when the only failing check is a timing gate, the resolver finding names the
   slowest tests of the failing job (a `--durations` summary from CI or a local run) so the fix targets them. A bare
   rerun is not offered as the fix.
5. **Tests**: hermetic tests with fake CI payloads: a timing-gate-only failure fails the final-head check; a green head
   after the calibration push passes; a head that differs from the approved one is reported; the report is not
   merge-ready while any check is red.
6. **Constraints**: `uv run pytest`, `uv run task lint` and `uv run task lint-docs` pass; no new dependencies; keep the
   three ledgers.

## Notes

- Target repository change in `holon-agentic-coder`: deliver through the 5-stage Holon flow. The intent JSON must not
  mention bean ids or harness paths.
- Touches the final-head CI check and Stage 5 (`flow/github/ci_final_head.py`, `flow/stages/calibrate.py`) and the
  posted-review text; run it when no other flow is editing those files.
- Related: Bean 0253 (Stage 5 sync, where this was found); the post-review CI gating work that added the final-head
  check.

## Resolution (completed, 2026-11-13)

Delivered by flow `chkgate` as holon-agentic-coder PR #186, merged 2026-11-13T07:10:34Z (merge commit `9f2187e`, review
`PRR_kwDORMmd1c8AAAABXt7cBA`). Calibration report
`plans/P-1794546213-1bdbac00-claude-agent-claude-sonnet-5-5_calibration.md` is in the PR. EV predicted vs actual: delta
+24.69 (actual 57.14). The PR needed a conflict merge with `origin/main` after PR #185 landed, resolved by the
`resolve-conflict` skill (two wisdom files it escalated were settled by hand and the skill's script now handles that
case). A red CI check, including a timing gate, now fails the final head, and the approval is invalidated on the PR; the
first real proof is the next flow's Stage 5.
