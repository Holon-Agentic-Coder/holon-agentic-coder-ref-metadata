---
# holon-agentic-coder-ref-metadata-0317
title: "GitHub Projects kanban board over the target repositories' issues"
status: todo
type: task
priority: normal
tags:
  - issue-tracking
  - github-issues
  - github-projects
  - holon-agentic-coder
  - holon-coherence
blocked_by:
  - "0215"
created_at: 2026-11-17T10:15:00Z
updated_at: 2026-11-19T11:30:00Z
---

## Problem

The maintainer cannot see at a glance what is ready, in progress, in review or done. This bean was a board synced from
beads data; with GitHub Issues as the tracker (Bean 0333) the board needs no sync code, only configuration.

## Goal

1. One organisation-level GitHub Project (v2) covering `holon-agentic-coder` and `holon-coherence`, linked to both so it
   shows under each repository's Projects tab, with a status field: Ready, In progress, In review, Done, plus Blocked.
2. The Project's built-in workflows do the moving: auto-add new issues from both repositories; set In review when a
   linked pull request opens; set Done when the issue closes.
3. Priority and type show on each card (from the labels), and a view groups by repository.
4. Issues are the source of truth. Nothing writes to the board except GitHub's own workflows and, for "In progress", the
   flow at intent time (Bean 0216).

## Notes

- GitHub configuration only: no target source change, so no Holon flow. Created with `gh project create` and the Project
  settings.
- Prerequisite: the `gh` token needs the `project` scope, which it lacks today (scopes: `repo`, `workflow`, `read:org`,
  `gist`, `admin:public_key`). The maintainer runs `gh auth refresh -s project`.
- Most useful after the import (Bean 0215), but the board can be created empty beforehand.
- Related: Bean 0333 (decision), Bean 0216 (flow sets In progress), Bean 0217 (coherence), Bean 0218 (retirement).
