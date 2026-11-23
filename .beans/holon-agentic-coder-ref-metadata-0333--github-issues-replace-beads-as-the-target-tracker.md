---
# holon-agentic-coder-ref-metadata-0333
title: "GitHub Issues replace beads as the target tracker; remove the beads pilot from holon-agentic-coder"
status: in-progress
type: task
priority: high
tags:
  - issue-tracking
  - github-issues
  - beads
  - holon-agentic-coder
created_at: 2026-11-19T11:30:00Z
updated_at: 2026-11-23T08:33:00Z
---

## Decision (maintainer, 2026-11-19)

The move away from harness beans goes to **GitHub Issues**, not to beads (`bd`). This supersedes the recommendation of
Bean 0156 and the direction of the pilot in Bean 0214 (PR #204). Beans 0215, 0216, 0217, 0218 and 0317 are repurposed
accordingly.

Why:

- Issues have a web view, and a GitHub Project gives the board with no sync to build (the whole of the old Bean 0317).
- `Closes #N` in a pull request closes the issue on merge, which covers most of what the flow had to do for beads.
- Issue data lives outside the git tree: no `refs/dolt/data`, no question of how tracker data merges across concurrent
  flow branches, and no exception to the sole-change-path rule for issue writes.
- Nothing extra in the images: no pinned `bd` binary, no Dolt, no digest-pin follow-up.
- `#N` references in commits and pull requests are native, so there is no id-hygiene rule to police.

What is given up: offline access to the tracker from inside a sandboxed role container, and `bd ready`'s built-in
dependency resolution. The host-side flow engine reads and writes issues and hands the issue text to the role agents
through the intent, so role containers need neither `gh` nor a token for this.

## Design defaults (change here if the maintainer decides otherwise)

- **One tracker per repository**: issues live in the repository they change (`holon-agentic-coder`, `holon-coherence`).
  Harness-only work stays in harness beans until the harness retires (Bean 0218 decides whether the remainder becomes
  issues in the harness repository).
- **One organisation-level Project** spans both targets (Bean 0317).
- **Fields**: type and priority as labels (`type:bug|feature|task`, `priority:P0`-`P3`); status is open/closed plus the
  Project's status field; dependencies use GitHub's issue dependencies ("blocked by") and sub-issues.
- **No harness ids in the targets**: issues carry no bean id. The bean-to-issue mapping is kept in the harness only.
- All three repositories are public, so issue text is public, as the bean text already is.

## Action: remove the beads pilot (target change, through the Holon flow)

PR #204 left the pilot's scaffolding in `holon-agentic-coder`. Remove it:

- The pinned `bd` install and its offline check from the `holon/agent-*` image builds.
- `.beads/config.yaml` and the `.beads/embeddeddolt/` gitignore entry.
- The `bd ready` / `--claim` / `bd close` guidance and the issue-data change-path exception in `AGENTS.md` and
  `.agents/`; replace with the GitHub Issues guidance (how a work item is referenced, who writes to it).
- The pilot's hermetic tests (config shape, gitignore entry, pinned Dockerfile version) and the `.beads/` coverage in
  the repository hygiene check.

The follow-up in `todo/beadspil-dockerfile-digest-pin.patch` was dropped on 2026-11-19; it had nothing left to pin.

## Notes

- Touches the Dockerfile and bake file, `.gitignore`, `AGENTS.md`/`.agents/` and tests: run it after Bean 0321 merges,
  and not beside Bean 0322, which also edits the Dockerfile.
- The intent JSON must not mention bean ids or harness paths.
- Related: Bean 0156 (investigation, superseded on the tracker choice), Bean 0214 (pilot), Beans 0215-0218 and 0317.

## Audit (2026-11-21)

Still valid on `origin/main`: `.beads/config.yaml` and `tests/test_beads_integration.py` (the pilot from
[PR #204](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/204)) are still present, and Beans 0215-0218
and 0317 remain blocked on this decision bean.

## Audit (2026-11-23)

`0321` (PR #206) and `0322` (PR #222) have both merged. Beads pilot files still on `main` (`b22258d`):
`.beads/config.yaml`, `.gitignore`, `apps/sandbox-executor/Dockerfile`, `apps/sandbox-executor/docker-bake.hcl`,
`apps/sandbox-executor/tests/test_beads_integration.py`, `docs/agents.md`, `docs/issue_tracking.md`. Unblocked and
completely disjoint from PR #230.
