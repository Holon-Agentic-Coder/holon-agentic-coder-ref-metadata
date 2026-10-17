---
# holon-agentic-coder-ref-metadata-0107
title: "Add Python unit test and lint workflow to CI for metadata repository"
status: completed
type: task
priority: normal
tags:
  - ci
  - testing
  - python
  - ruff
  - pytest
created_at: 2026-10-17T04:14:00Z
updated_at: 2026-10-18T09:40:00Z
---

Integrate Python unit testing (`pytest`) and code quality linting (`ruff`) into GitHub Actions CI workflows for the
`holon-agentic-coder-ref-metadata` repository.

## Context

- During PR #52 review (Finding QA-01), an automated unit test suite `tests/test_clean_workspace.py` was introduced to
  validate destructive filesystem operations, dry-run safety, and orphan detection in `clean_workspace.py`.
- However, `.github/workflows/test-hygiene.yml` currently only runs Node.js-based Markdown checks
  (`npx prettier --check` and `node .agents/scripts/validate-links.js`).
- Python test suites and utility scripts in this repository
  (`.agents/skills/clean_workspace/scripts/clean_workspace.py`, future harness automation) are not currently exercised
  in automated GitHub Actions CI checks on push or pull request.

## Tasks

- [x] Update `.github/workflows/test-hygiene.yml` (or create a dedicated `.github/workflows/test-python.yml`) to set up
      Python 3.12+ and `uv`.
- [x] Run `uv run pytest tests/` as an automated status check on PRs and commits targeting `main`.
- [x] Add `uv run ruff check` and `uv run ruff format --check` to enforce linting and style standards on repository
      Python scripts.
- [x] Ensure tests run hermetically without requiring external repository checkouts or live GitHub network dependencies.
- [x] Verify workflow passes cleanly in CI.

## Resolution Summary

Added Python 3.12 setup via `astral-sh/setup-uv@v5`, `uv run ruff check .agents/ tests/`,
`uv run ruff format --check .agents/ tests/`, and hermetic `uv run pytest tests/ -q` to
`.github/workflows/test-hygiene.yml`. Verified all 18 unit tests and ruff lint passes cleanly.
