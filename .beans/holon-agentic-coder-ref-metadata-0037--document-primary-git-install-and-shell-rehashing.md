---
# holon-agentic-coder-ref-metadata-0037
title: "Document primary Git installation entrypoint and shell rehashing for holon-coherence"
status: todo
type: task
priority: normal
tags:
  - documentation
  - holon-coherence
  - installation
created_at: 2026-09-26T09:06:00Z
updated_at: 2026-09-26T15:20:00Z
---

Update `holon-coherence` documentation (including `README.md` and onboarding guidelines) to establish
`uv tool install git+https://github.com/Holon-Agentic-Coder/holon-coherence.git` as the primary standard entrypoint for
consumers and operators, and document shell command rehashing.

## Context

When developers install or update tools globally via `uv tool install`, existing open terminal sessions may cache
previous binary paths in their shell command lookup tables, or users may encounter conflicts with pre-existing
environment binaries. Documenting the primary installation command alongside shell cache refresh instructions (`rehash`
in zsh, `hash -r` in bash) ensures a seamless onboarding experience.

## Acceptance Criteria

1. Update `apps/holon-coherence/README.md`:
   - Elevate `uv tool install git+https://github.com/Holon-Agentic-Coder/holon-coherence.git` as the primary standard
     entrypoint for operators and consumers.
   - Demarcate `cd apps/holon-coherence && uv tool install --editable .` specifically for local contributor and agent
     development.
   - Add a note detailing shell rehashing (`rehash` for zsh, `hash -r` for bash) to refresh the command cache if
     updating from a previous installation in an active terminal session.
2. Ensure consistent guidance across related documentation and agent instructions where global CLI setup is referenced.
3. Format updated markdown files with Prettier.

## Notes

- Target repository: `apps/holon-coherence/`
- Target files:
  - `apps/holon-coherence/README.md`

## Status Verification (2026-09-26)

Still open. Verified against the current tip of the target repository: `apps/holon-coherence/README.md:98-103` still
presents the local `uv tool install --editable .` as the primary command with the `git+https://...` form as an "Or"
alternative, and no `rehash` / `hash -r` guidance exists anywhere in the README.
