---
# holon-agentic-coder-ref-metadata-0107
title: "Add Python unit test and lint workflow to CI for metadata repository"
status: todo
type: task
priority: normal
tags:
  - ci
  - testing
  - python
  - ruff
  - pytest
created_at: 2026-10-17T04:14:00Z
updated_at: 2026-10-17T04:14:00Z
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

- [ ] Update `.github/workflows/test-hygiene.yml` (or create a dedicated `.github/workflows/test-python.yml`) to set up
      Python 3.12+ and `uv`.
- [ ] Run `uv run pytest tests/` as an automated status check on PRs and commits targeting `main`.
- [ ] Add `uv run ruff check` and `uv run ruff format --check` to enforce linting and style standards on repository
      Python scripts.
- [ ] Ensure tests run hermetically without requiring external repository checkouts or live GitHub network dependencies.
- [ ] Verify workflow passes cleanly in CI.
