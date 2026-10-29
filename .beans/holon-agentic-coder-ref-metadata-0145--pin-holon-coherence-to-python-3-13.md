---
# holon-agentic-coder-ref-metadata-0145
title: "Pin holon-coherence to Python 3.13 to match holon-agentic-coder"
status: in-progress
type: task
priority: normal
tags:
  - holon-coherence
  - python
  - tooling
created_at: 2026-10-23T15:30:00Z
updated_at: 2026-10-29T06:40:00Z
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

## Progress (2026-10-29)

- Completed all 5 stages of the Holon flow on `holon-coherence` (worktree
  `apps/holon-coherence/flow-0145-python-version-alignment`): `I-1793246643-coherence-pin-python-3-13` →
  `P-1793246658-claude-agent-claude-opus-5-5` → `E-1793246775-claude-agent-claude-opus-5-5`.
- **PR #28** (https://github.com/Holon-Agentic-Coder/holon-coherence/pull/28): converged in 4 review-loop iterations
  (3/3 ensemble approval at `5dd6181`, review `5692867047`, 7/7 CI green), Stage 5 calibrated (`dadf1dd`, EV 0.19
  predicted / 0.07 actual, `/calibrated` pushed and fast-forwarded into PR head `dadf1dd`). Awaiting the maintainer's
  merge.
