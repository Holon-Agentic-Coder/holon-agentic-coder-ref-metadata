---
# holon-agentic-coder-ref-metadata-0103
title: "Implement clean-workspace skill for branches, worktrees, directories, subagent, and todo"
status: completed
type: task
priority: normal
tags:
  - hygiene
  - skills
  - worktrees
  - branches
  - subagent
  - todo
created_at: 2026-10-17T01:07:00Z
updated_at: 2026-10-17T01:10:00Z
---

Implement a comprehensive, unified `clean-workspace` skill (`.agents/skills/clean_workspace/SKILL.md`) to audit, prune,
and safely delete merged worktrees, local and remote branches, orphaned on-disk directories, local `.subagent` review
artifacts, and temporary files in the `todo` directory across the entire Holon ecosystem.

## Context

While `.agents/skills/clean_branches/SKILL.md` defines branch and worktree cleanup across git repositories, multi-agent
development and Holon flow cycles leave behind additional transient artifacts across the workspace:

1. Intermediate PR review and consensus artifacts in local `.subagent/` directories.
2. Temporary intent payloads, debug logs, and scratch scripts in `todo/` (while persistent files like `todo/.gitkeep`
   and living triage documents like `todo/bean-triage-*.md` must be strictly preserved).
3. Residual build, IDE, and cache directories left behind when unmounting git worktrees.

## Tasks

- [x] Create `.agents/skills/clean_workspace/SKILL.md` covering all 9 operational phases:
  - Phase 1: Multi-repo discovery and remote tracking synchronization (`git fetch origin --prune`).
  - Phase 2: Detecting and deleting merged remote branches (direct ancestry, squash merges, closed PRs, and Holon flow
    `I-.../**` provenance trees).
  - Phase 3: Auditing and safely removing merged git worktrees.
  - Phase 4: Filesystem-vs-registry diffing and safe deletion of orphaned directories.
  - Phase 5: Pruning stale and gone local branches.
  - Phase 6: Base branch (`main`) fast-forward synchronization.
  - Phase 7: Purging intermediate PR review artifacts from `.subagent/`.
  - Phase 8: Cleaning transient files from `todo/` while enforcing strict preservation of `todo/.gitkeep` and
    `todo/bean-triage-*.md`.
  - Phase 9: End-to-end verification and structured reporting.
- [x] Provide an automated cleanup script `.agents/skills/clean_workspace/scripts/clean_workspace.py` supporting dry-run
      audits and safe automated execution.
- [x] Update `.agents/skills/clean_branches/SKILL.md` to reference `clean-workspace`.
- [x] Format all markdown files with Prettier.
- [x] Update bean status to `completed` upon verification.

## Resolution

- Created `.agents/skills/clean_workspace/SKILL.md` defining the 9-phase comprehensive cleanup lifecycle.
- Implemented and verified `.agents/skills/clean_workspace/scripts/clean_workspace.py` supporting `--dry-run`,
  `--git-only`, `--subagent-only`, and `--todo-only`.
- Cross-referenced `clean-workspace` in `.agents/skills/clean_branches/SKILL.md` and added to
  `.agents/scripts/validate-links.js`.
- Verified link integrity via `node .agents/scripts/validate-links.js` (100% green).
