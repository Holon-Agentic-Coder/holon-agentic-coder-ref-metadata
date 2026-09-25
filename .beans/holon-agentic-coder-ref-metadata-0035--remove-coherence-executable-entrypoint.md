---
# holon-agentic-coder-ref-metadata-0035
title: "Remove coherence executable entrypoint and retain only holon-coherence"
status: todo
type: task
priority: normal
tags:
  - packaging
  - holon-coherence
  - cli
created_at: 2026-09-26T08:58:00Z
updated_at: 2026-09-26T15:20:00Z
---

When installing `holon-coherence` via `uv tool install git+https://github.com/Holon-Agentic-Coder/holon-coherence.git`,
`uv` installs two executables: `coherence` and `holon-coherence`.

The `coherence` entrypoint was defined in `pyproject.toml` under `[project.scripts]` as an alias pointing to
`holon_coherence.cli:main`. To maintain a single unambiguous binary name and prevent naming collisions with other tools
or packages named `coherence`, remove the `coherence = "holon_coherence.cli:main"` entrypoint so only `holon-coherence`
is installed.

## Acceptance Criteria

- Remove `coherence = "holon_coherence.cli:main"` from `[project.scripts]` in `apps/holon-coherence/pyproject.toml`.
- Retain only `holon-coherence = "holon_coherence.cli:main"`.
- Verify packaging and test suites pass cleanly with `uv run pytest` and linting checks.
- Verify `uv tool install` installs only `holon-coherence`.

## Notes

- Target repository: `apps/holon-coherence/`
- Worktree & branch to be created off `origin/main` (e.g. `feat/0035-remove-coherence-entrypoint`).
- No internal CLI logic depends on `coherence`; all existing CLI commands, tests, and documentation use
  `holon-coherence`.

## Status Verification (2026-09-26)

Still open. Verified against the current tip of the target repository: `apps/holon-coherence/pyproject.toml:39` still
declares `coherence = "holon_coherence.cli:main"` alongside `holon-coherence`.
