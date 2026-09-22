---
# holon-agentic-coder-ref-metadata-0024
title: Implement holon init CLI command to scaffold new and existing projects
status: completed
type: task
created_at: 2026-09-17T00:00:00Z
updated_at: 2026-09-22T00:00:00Z
---

Implement a `holon init` CLI subcommand in `apps/sandbox-executor/src/sandbox_executor/cli.py` in the
`holon-agentic-coder` repository to automate onboarding and scaffolding of new or existing projects (such as
`holon-coherence`) into the Holon ecosystem. Also register a `[project.scripts]` console script entrypoint in
`apps/sandbox-executor/pyproject.toml` so `holon` can be installed globally via `uv tool install` and executed from any
repository.

## Notes

- Target repository: holon-agentic-coder (implementation in apps/sandbox-executor)
- CLI implementation: apps/sandbox-executor/src/sandbox_executor/cli.py
- Packaging: add `[project.scripts] holon = 'sandbox_executor.cli:main'` to apps/sandbox-executor/pyproject.toml
  (coordinated with Bean 0025)
- Scaffolds `holon-config/` (world/ruleset.md, world/constraints.md, metrics configs, prompt templates)
- Scaffolds `holon-knowledge/` (empty ledger JSONLs, plans/, kb/)
- Scaffolds or updates `.gitignore` in target directory with standard ignores (e.g. `.venv/`, `.holon-cache/`,
  `__pycache__/`)
- Supports `holon init [TARGET_DIR] [--template <python|generic>] [--force]`
- Idempotency invariant: never truncate or overwrite existing ledger files
- Verification target: bootstrap holon-coherence using `holon init`
- Test Coverage: Add automated unit tests in `apps/sandbox-executor/tests/test_init.py` covering directory scaffolding,
  `--template` variations, `--force` flag, and verifying the idempotency invariant on pre-existing files.
- Merged: holon-agentic-coder PR #51 (2026-09-18), merge commit 93a830a; PR head be282c8 matched the local tip exactly.
- Post-merge audit 2026-09-22: worktree holon-agentic-coder/feat-0024-implement-holon-init and local branch removed
  (remote ref already gone). Verified scaffold.py, the init subcommand in cli.py and tests/test_init.py present on
  origin/main.

## Assignment

Assignee: `antigravity-agent`

## Resolution

Successfully implemented the `holon init` CLI command in `holon-agentic-coder` on dedicated worktree
`feat-0024-implement-holon-init` (branch `feat/0024-implement-holon-init`):

- Created `apps/sandbox-executor/src/sandbox_executor/scaffold.py` containing complete project scaffolding logic,
  ruleset templates (`python` and `generic`), world constraints, metrics physics JSON configs, agent prompt templates,
  and `.gitignore` rules.
- Implemented `holon init [TARGET_DIR] [--template <python|generic>] [--force]` subcommand in
  `apps/sandbox-executor/src/sandbox_executor/cli.py`.
- Registered `[project.scripts] holon = 'sandbox_executor.cli:main'` in `apps/sandbox-executor/pyproject.toml`, enabling
  global installation via `uv tool install`.
- Enforced the idempotency invariant: ledger files (`intents.jsonl`, `plans.jsonl`, `executions.jsonl`) are append-only
  and never truncated or overwritten, even when `--force` is passed.
- Added comprehensive automated unit test suite in `apps/sandbox-executor/tests/test_init.py` covering full directory
  scaffolding, template variations, force flag behavior, ledger idempotency, `.gitignore` deduplication, and CLI
  dispatch (all 6 tests passing).
- Validated full test suite (227 passed) and linters (`ruff check`, `ruff format --check`, and `uv lock --check`).
- Verified bootstrapping target on `holon-coherence` using `holon init`.
- Formatted markdown using Prettier and squashed changes into a single semantic commit on
  `feat/0024-implement-holon-init`. Landed on origin/main as merge commit 93a830a via holon-agentic-coder PR #51 (merged
  2026-09-18).
