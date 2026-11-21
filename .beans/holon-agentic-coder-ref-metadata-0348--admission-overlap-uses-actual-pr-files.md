---
# holon-agentic-coder-ref-metadata-0348
title: "Stage 3 admission blocks on folder or wildcard touch-set entries and on planned rather than actual PR files"
status: in-progress
type: bug
priority: high
tags:
  - flow
  - stage-3
  - admission
  - touch-set
  - concurrency
  - holon-agentic-coder
created_at: 2026-11-20T20:40:00+11:00
updated_at: 2026-11-21T01:20:00+11:00
---

## Problem

Stage 3 admission compares touch sets path by path, and a folder or wildcard entry matches every file under it. On
2026-11-20 this blocked flows that shared no code:

- The `tests-never-write-real-worktree` flow (PR #215) planned entries like `apps/sandbox-executor/tests/test_*.py` and
  `apps/sandbox-executor/tests/flow/**/test_*.py`. Three unrelated flows were refused for almost two hours because they
  each **added new** test files (`test_resume_checkpoint.py`, `test_promotion_idempotence.py`, …) that matched those
  wildcards. #215 itself changed about 8 files.
- The combined `review-report-ci-log-redaction` flow carried the folder entry `apps/sandbox-executor/tests/` and was
  refused on the other session's PR #218 (remove the gemini runner), which edits many existing test files. The source
  modules of the two changes were disjoint; the maintainer authorised a one-time `--allow-overlap`.

Broad intent scopes cause the wide entries (the harness now writes intents with explicit files), but admission should
not turn them into false conflicts.

## Action

Through the Holon flow on `holon-agentic-coder`:

- **Open pull requests are compared by their actual changed files** (`gh pr diff --name-only` or the GitHub files API),
  not by their planned touch set. A local flow that has not opened a PR keeps using its touch set.
- **New files never overlap.** A path that does not exist on the base branch only overlaps an exact same path in the
  other set, never a folder or wildcard entry.
- **Folder and wildcard entries match only existing files**, and the refusal message lists the concrete files that
  overlap, not just the pattern.
- Optionally warn at Stage 2 when a planned touch set contains a bare folder or a wildcard, so plans name files.
- Hermetic tests: a new test file does not overlap a wildcard entry; an open PR is compared by its diff; an existing
  file under a folder entry still overlaps; the refusal lists concrete files.

## Notes

- Related: Bean 0151 (touch-set admission), Bean 0337 (blocked state), Bean 0338 (plan refresh after a wait).

## Audit (2026-11-21)

Still valid, with exact locations: `flow/admission_decision.py` still compares an open pull request by its declared
touch set (`overlapping_entries(own, flow.declared)`, around line 63) in addition to its real changed files from
`flow/in_flight.py` (`gh pr diff --name-only` is already fetched), and `touch_set.py` `entries_overlap` treats
directories and globs conservatively with no new-file rule. Remaining work: use the real files only for an open PR, and
never overlap a path that does not exist on the base branch with a wildcard or folder entry.

## Progress

- 2026-11-21: Holon flow `admission-uses-actual-pr-files` started (claude-agent, claude-opus-5-5).
