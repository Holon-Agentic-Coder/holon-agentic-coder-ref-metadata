---
# holon-agentic-coder-ref-metadata-0317
title: "GitHub Projects kanban board for holon-agentic-coder, fed by beads issues"
status: todo
type: feature
priority: normal
tags:
  - issue-tracking
  - beads
  - github-projects
  - holon-agentic-coder
blocked_by:
  - "0214"
created_at: 2026-11-17T10:15:00Z
updated_at: 2026-11-17T10:15:00Z
---

## Problem

Beads (`bd`, piloted in `holon-agentic-coder` by Bean 0214, prefix `hac-`) keeps issue data on `refs/dolt/data`, which
has no web view: the maintainer cannot see at a glance what is ready, claimed, in review or done. There is no board
under <https://github.com/Holon-Agentic-Coder/holon-agentic-coder/projects> today.

## Goal

1. A GitHub Projects (v2) kanban board exists for `holon-agentic-coder`, linked to the repository so it shows under its
   Projects tab, with columns that map one-to-one onto beads statuses (for example Ready, In progress, In review, Done,
   plus Blocked).
2. Every open beads issue appears on the board as one card carrying its `hac-` id, title, priority and status; the card
   moves when the beads status changes (`bd` claim, close) and links to the flow's pull request when one exists.
3. Beads stays the source of truth. The sync is one-way (beads to board) unless the design below decides otherwise, is
   idempotent (re-running it creates no duplicate cards) and needs no human step.
4. The board survives two concurrent flow branches updating issues, the same acceptance the beads pilot uses.

## Design questions to settle first

- **Card type**: draft items on the project (no GitHub Issues created) vs one GitHub Issue per beads issue. Draft items
  keep beads as the only tracker; real Issues give links and notifications but create a second tracker to reconcile.
- **Where the sync runs**: a GitHub Actions workflow triggered when `refs/dolt/data` moves, a step in the Holon flow
  (claim at intent, move at PR open, close at merge; ties in with Bean 0216), or both.
- **Direction**: whether dragging a card on the board may write back to beads, or the board is read-only.
- **Scope of the board**: repository-level project for `holon-agentic-coder` only, or one organisation-level board that
  later also takes `holon-coherence` (`hcoh-`, Bean 0217).

## Notes

- Prerequisite outside the flow: the `gh` token needs the `project` scope (today it lacks `read:project`; run
  `gh auth refresh -s project`), and any workflow token needs project write access. Creating the board itself
  (`gh project create`, fields, columns, repository link) is GitHub configuration, not a source change.
- The sync code, workflow and docs are a target repository change in `holon-agentic-coder`: through the 5-stage Holon
  flow. The intent JSON must not mention bean ids or harness paths.
- Blocked by Bean 0214 (beads must be in the repository first; PR #204). Related: Bean 0216 (flow claims and closes
  beads issues), Bean 0217 (coherence tracker), Bean 0218 (harness retirement), Bean 0156 (investigation).
