---
# holon-agentic-coder-ref-metadata-0217
title: "Adopt beads (bd) issue tracking inside holon-coherence"
status: todo
type: feature
priority: normal
tags:
  - issue-tracking
  - beads
  - holon-coherence
blocked_by:
  - "0214"
  - "0215"
created_at: 2026-10-30T00:00:00Z
updated_at: 2026-10-30T00:00:00Z
---

## Problem

After the holon-agentic-coder pilot (Bean 0214) meets its acceptance criteria, `holon-coherence` gets its own tracker so
both targets are self-sufficient before the harness retires. Per Bean 0156 decision point 1 the recommended topology is
one tracker per target (prefix `hcoh-`), keeping the submodule standalone (rule 12); cross-target dependencies use beads
`external:` references if ever needed.

## Scope

- `bd init` with prefix `hcoh-`, same commit/ignore/config conventions as the pilot; pin `bd` in the coherence image.
- Import the open coherence-routed beans from the Bean 0215 converter output.
- Coherence `AGENTS.md`/`.agents/` guidance mirroring the pilot's, adjusted for the coherence toolchain.

## Notes

- Runs through the **Holon flow** against `holon-coherence`. Touch set: `.beads/`, `.gitignore`, image Dockerfile,
  `AGENTS.md`/`.agents/` — avoid concurrency with other coherence flows touching the Dockerfile.
- Blocked by Bean 0214 (pilot acceptance) and Bean 0215 (converter output). Related: Bean 0156, Bean 0147 (coherence
  half already merged via PR #29).
