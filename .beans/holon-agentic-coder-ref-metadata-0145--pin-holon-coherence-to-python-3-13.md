---
# holon-agentic-coder-ref-metadata-0145
title: "Pin holon-coherence to Python 3.13 to match holon-agentic-coder"
status: todo
type: task
priority: normal
tags:
  - holon-coherence
  - python
  - tooling
created_at: 2026-10-23T15:30:00Z
updated_at: 2026-10-23T15:30:00Z
---

## Problem

`holon-agentic-coder` pins `requires-python = "==3.13.*"` (workspace root `pyproject.toml`) with ruff
`target-version = "py313"`, but `holon-coherence` (`origin/main` `29b7e50`) declares only `requires-python = ">=3.12"`
and ruff `target-version = "py311"`. With no upper bound and no `.python-version`, `uv sync` resolves to the newest
interpreter on the host: on 2026-10-24 both a fresh verification worktree and the `main` worktree's `.venv` came up on
Python 3.14.8, so coherence is developed and tested on a different interpreter than the rest of the ecosystem.

## Scope

- `pyproject.toml`: `requires-python = "==3.13.*"`; ruff `target-version = "py313"`; regenerate and commit `uv.lock`.
- Align any classifiers, Dockerfile base image / `uv` python selection, and CI workflow `python-version` matrices with
  3.13 so local, container and CI interpreters agree.
- Fix anything the newer ruff target flags (`ruff check` / `ruff format --check` clean).
- Docs: state the supported interpreter wherever install/dev setup is described.
- Verify: `uv sync --group dev` creates a 3.13 venv; `uv run task test` and `uv run task lint` pass.

## Notes

- Run through the Holon flow on `holon-coherence`.
- Until this lands, harness verification builds coherence venvs explicitly with `uv sync --python 3.13`.
