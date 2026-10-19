---
# holon-agentic-coder-ref-metadata-0108
title: "Implement automated subagent artifact archiving and retention policy"
status: completed
type: task
priority: normal
tags:
  - subagent
  - hygiene
  - review-loop
  - archiving
created_at: 2026-10-17T04:14:30Z
updated_at: 2026-10-18T09:40:00Z
---

Implement an automated archiving and retention policy for multi-agent PR review artifacts in `.subagent/`.

## Context

- In PR #52 review (Finding PE-01), indiscriminate deletion of `.subagent/` files in workspace cleanups was flagged as a
  critical hazard that destroys active PR review state.
- While `clean_workspace.py` now protects open PR files and core state files (`_state.json`, `_coordination.json`,
  `_loop_history.md`, `_posted_review.md`, consensus reports), completed intermediate review files
  (`_ensemble_review_iter_*`, `_resolver_iter_*`, `_dry_run_review_iter_*`) accumulate indefinitely.
- The `pr-review-loop` specification states that completed intermediates should be cleanly moved into
  `.subagent/<repo>_pr<N>_archive/` once a PR reaches terminal status (merged or closed), rather than left loose or
  purged blindly.

## Tasks

- [x] Add an `--archive` mode to `clean_workspace.py` that relocates completed intermediate artifacts for closed/merged
      PRs into `.subagent/<repo>_pr<N>_archive/`.
- [x] Strictly ensure permanent receipts (`_state.json`, `_posted_review.md`, final consensus report) remain intact.
- [x] Implement a 30-day retention pruning rule for archived intermediate bundles while preserving the permanent audit
      trail.
- [x] Add unit tests in `tests/test_clean_workspace.py` verifying archival relocation and retention bounds.
- [x] Update `.agents/skills/clean_workspace/SKILL.md` with the formal archiving workflow.

## Resolution Summary

Implemented `--archive` mode and 30-day retention pruning in `clean_workspace.py`
(`.agents/skills/clean_workspace/scripts/clean_workspace.py`). Added unit tests in `tests/test_clean_workspace.py`
testing artifact relocation, permanent receipt immunity, and retention expiration. Documented workflow in
`.agents/skills/clean_workspace/SKILL.md`.
