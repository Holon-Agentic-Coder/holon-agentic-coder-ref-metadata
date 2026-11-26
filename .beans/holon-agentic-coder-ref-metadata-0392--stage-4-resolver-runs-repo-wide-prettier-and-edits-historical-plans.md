---
# holon-agentic-coder-ref-metadata-0392
title: "Stage 4 resolver runs repo-wide Prettier and mutates untouched historical plans/ files"
status: todo
type: bug
priority: high
tags:
  - review-loop
  - resolver
  - hygiene
  - prettier
  - holon-agentic-coder
created_at: 2026-11-24T07:20:00Z
updated_at: 2026-11-24T07:20:00Z
---

## Problem

During Stage 4 of PR #268 (`claude-code-mode-default-on`, 2026-11-24), the resolver polluted the PR diff with 36
unrelated historical files under `plans/` (34 historical `plans/*/*_calibration.md` reports plus 2 old plan files):

1. In iteration 2 (`1676ccbf`, `FIND-CI-002`), to fix a `hygiene` formatting finding, the resolver ran Prettier across
   the whole repository instead of scoping formatting to PR-changed files. Because the container Prettier version
   wrapped LaTeX math lines (`$cost\_error = ...$`) differently from GitHub Actions' Prettier version, 36 untouched
   historical files were modified.
2. In iteration 3 (`23d6f9c7`, `FIND-CI-003`), when CI `hygiene` flagged those newly reformatted historical files, the
   resolver inserted `<!-- prettier-ignore -->` above the math paragraphs across all 34 historical calibration reports
   instead of reverting untouched files back to `origin/main`.

A maintainer-instructed host-side cleanup (`ce56b34d`) was required to restore those 36 historical files before
re-running Stage 4 review.

## Goal

- The Stage 4 resolver (prompts and pre-push/post-turn guard) formats only files changed by the PR itself, never the
  entire repository.
- Any Stage 4 resolver commit touching historical `plans/` files outside the current intent's own `plans/<intent>/`
  directory is refused fail-closed (or reverted before commit/push).
- Container Prettier version matches CI (`hygiene` workflow) so formatting checks are deterministic across host,
  container, and CI.
- Add hermetic tests verifying out-of-scope historical `plans/` edits by a resolver are rejected.
