---
# holon-agentic-coder-ref-metadata-0214
title: "Pilot beads (bd) issue tracking inside holon-agentic-coder"
status: completed
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
updated_at: 2026-11-17T09:50:00Z
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

## Resolution

Delivered via [PR #204](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/204) and merged into `main`
(`d09df711`):

- **Key Architectural Deliverables**: `bd` (beads) pinned in the `holon/agent-*` images and verified offline at build
  time; `.beads/config.yaml` committed with prefix `hac-`, with `.beads/embeddeddolt/` gitignored; `AGENTS.md` and
  `.agents/` guidance for `bd ready`, `--claim` and `bd close`, plus the narrow issue-data change-path exception.
- **Folded-in Bean 0147 cleanup**: already done on `main` before this PR (via PR #199). `todo/` and `.subagent/` are no
  longer tracked, and no `Bean NNNN` ids remain in source, docs or CLI help outside append-only ledgers. The hygiene
  check now covers harness paths and `Bean [0-9]{4}`.
- **Verification & Tests**: hermetic tests for the committed config shape, the gitignore entry and the pinned Dockerfile
  version; the repository hygiene check (`test_repository_hygiene.py`) covers `.beads/`. Not verified in this PR: a live
  create/claim/close cycle by a flow, and sync across two concurrent flow branches (Acceptance items left open).
- **Holon Flow Traversal**: all 5 stages completed (flow `I-1794891082-beadspil`, plan
  `P-1794892061-52a8e074-claude-agent-claude-fable-5`, execution `E-1794892278-9d45d78f-claude-agent-claude-fable-5`).
  Calibration (`plans/P-1794892061-52a8e074-claude-agent-claude-fable-5_calibration.md`): expected value predicted
  39.65, actual 62.59 (clean; 22.94 conservative underestimate). With bugs included the observed value was -17.41.
- **Follow-up**: the `bd` tarball sha256 digest pin in `apps/sandbox-executor/Dockerfile` (in-repo checksums instead of
  the release's `checksums.txt`) was an uncommitted edit in the flow worktree and is not in PR #204. Saved as
  `todo/beadspil-dockerfile-digest-pin.patch` in the harness; to be applied through a new Holon flow.
