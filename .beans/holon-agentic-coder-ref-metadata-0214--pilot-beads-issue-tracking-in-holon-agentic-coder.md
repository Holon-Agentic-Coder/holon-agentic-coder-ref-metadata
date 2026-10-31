---
# holon-agentic-coder-ref-metadata-0214
title: "Pilot beads (bd) issue tracking inside holon-agentic-coder"
status: todo
type: feature
priority: high
tags:
  - issue-tracking
  - beads
  - harness-deprecation
  - holon-agentic-coder
blocked_by:
  - "0156"
created_at: 2026-10-30T00:00:00Z
updated_at: 2026-10-30T00:00:00Z
---

## Problem

Bean 0156's investigation recommends adopting [beads](https://github.com/steveyegge/beads) (`bd`, v1.3.2, MIT,
Dolt-backed, data synced on `refs/dolt/data`) inside each target repository ahead of deprecating this harness.
`holon-agentic-coder` is the pilot target. Nothing in the target carries a tracker today; work items live only in the
harness's `.beans/`.

## Scope

- `bd init` with prefix `hac-` in `holon-agentic-coder`: commit `.beads/config.yaml` (without `node_id`), gitignore
  `.beads/embeddeddolt/`, set `dolt.local-only` as appropriate for sandboxed role agents.
- Pin the `bd` version in the `holon/agent-*` images and verify it runs offline inside them.
- Target `AGENTS.md`/`.agents/` guidance: how agents use `bd ready`, `--claim`, `bd close`, and the narrow change-path
  exception for issue-data writes (`refs/dolt/data` + `.beads/` data only, never source) — pending maintainer decision
  points 1, 2 and 4 in Bean 0156.
- **Folds in the holon-agentic-coder half of Bean 0147** (as the triage matrix predicts): remove `todo/` artifacts,
  `.subagent/.gitkeep`, and `Bean 0NNN` ids from source/docs/CLI help; add the hygiene check failing on harness paths
  and `Bean [0-9]{4}` (beads ids `hac-xxxx` cannot collide with it).
- Acceptance: `bd` works offline in the images; a flow can create, claim and close an issue; sync survives two
  concurrent flow branches; hygiene check passes.

## Notes

- Runs through the **Holon flow** (target source, docs and CI change). Touch set: `.beads/`, `.gitignore`, image
  Dockerfiles, `AGENTS.md`/`.agents/`, hygiene test, plus the 0147 cleanup paths — do not run concurrently with other
  flows touching the Dockerfiles or CI.
- Blocked by maintainer sign-off on Bean 0156 decision points 1, 2, 4, 5 and 7.
- Related: Bean 0147 (its hac half folds in here), Bean 0156 (investigation), Bean 0183 (sandboxed clones — bd must work
  in role containers).
