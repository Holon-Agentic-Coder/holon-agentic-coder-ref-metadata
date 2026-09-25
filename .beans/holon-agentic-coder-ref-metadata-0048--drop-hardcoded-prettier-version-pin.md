---
# holon-agentic-coder-ref-metadata-0048
title: "Drop hardcoded Prettier version pin across Makefile and workflows"
status: todo
type: task
priority: normal
created_at: 2026-09-26T00:21:00Z
updated_at: 2026-09-26T15:20:00Z
---

Evaluate and remove the hardcoded Prettier version pin (`@3.8.4` in `npx --yes prettier@3.8.4`) across `Makefile`, CI
workflows, and documentation.

## Context & Problem Statement

Currently, multiple places in `holon-agentic-coder` (e.g. `Makefile#L87`, `.github/workflows/hygiene.yml`) invoke:

```bash
npx --yes prettier@3.8.4 --check "**/*.md"
```

Or instructions recommend:

```bash
npx --yes prettier@3.8.4 --write "**/*.md"
```

1. **Why was `@3.8.4` pinned?**: In automated CI pipelines, pinning a specific minor/patch version prevents subtle
   formatting drift across different Prettier releases.
2. **Problems with hardcoded version pin**:
   - For daily developer and agent workflows, forcing `@3.8.4` bypasses locally installed or globally cached Prettier
     binaries and forces `npx` to query or resolve the specific remote package, adding network and execution overhead.
   - AGENTS.md rule 6 states: `npx prettier --write "**/*.md"` (without a version pin), leading to inconsistent commands
     between agent guidelines, `Makefile`, and CI.
   - If version pinning is desired, standard practice is to specify devDependencies in `package.json` with a lockfile or
     let `npx prettier` resolve cleanly.

## Acceptance Criteria

1. **Audit Prettier Version Pinning**: Identify all occurrences of `prettier@` or `3.8.4` across:
   - `Makefile` (e.g. `lint-docs`, `format-docs`)
   - `.github/workflows/` (e.g. `hygiene.yml`)
   - Documentation (`AGENTS.md`, `.agents/rules.md`, `README.md`)
2. **Standardize Prettier Invocation**:
   - Evaluate whether dropping the `@3.8.4` pin in favor of standard `npx prettier` (or configuring `package.json` /
     `.prettierrc`) satisfies repo formatting stability.
   - Update `Makefile` and workflow scripts to use unpinned `npx prettier` (or project-configured Prettier) if strict
     pinning is not required.
3. **Verify Documentation & CI**:
   - Ensure `make lint-docs` and `npx prettier --check "**/*.md"` succeed consistently.
   - Verify CI hygiene workflows pass with the standardized command.

## Status Verification (2026-09-26)

Still open. Verified against the current tip of the target repository: `Makefile:87` and `Makefile:96` still invoke
`npx --yes prettier@3.8.4`.
