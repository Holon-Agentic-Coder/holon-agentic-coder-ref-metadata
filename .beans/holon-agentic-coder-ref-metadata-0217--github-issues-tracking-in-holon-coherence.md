---
# holon-agentic-coder-ref-metadata-0217
title: "GitHub Issues tracking for holon-coherence: labels, guidance and import"
status: todo
type: task
priority: normal
tags:
  - issue-tracking
  - github-issues
  - holon-coherence
blocked_by:
  - "0215"
created_at: 2026-10-30T00:00:00Z
updated_at: 2026-11-19T11:30:00Z
---

## Problem

`holon-coherence` needs its own tracker so both targets are self-sufficient before the harness retires. With GitHub
Issues as the tracker (Bean 0333; this bean was "adopt beads in holon-coherence") there is nothing to install: Issues
are already enabled on the repository. What remains is the label set, the agent guidance and the import.

## Scope

- Create the same label set as `holon-agentic-coder` (`type:`, `priority:`), using the Bean 0215 importer's label step.
- Import the open coherence-routed beans from the Bean 0215 importer.
- Coherence `AGENTS.md`/`.agents/` guidance on how a work item is referenced and who writes to it, mirroring the
  `holon-agentic-coder` guidance written under Bean 0333.

## Notes

- Labels and the import are GitHub configuration and data, not source: no flow needed, and they run on the maintainer's
  word like the main import. The guidance change is a target change and goes through the **Holon flow** against
  `holon-coherence`.
- Much smaller than the beads version: no image change, no `.beads/`, no sync.
- Blocked by Bean 0215 (importer). Related: Bean 0333, Bean 0317 (the organisation board takes this repository too).
