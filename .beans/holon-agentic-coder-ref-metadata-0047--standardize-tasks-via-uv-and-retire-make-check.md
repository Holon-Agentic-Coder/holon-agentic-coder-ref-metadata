---
# holon-agentic-coder-ref-metadata-0047
title: "Standardize project tasks through uv and evaluate retiring make check"
status: todo
type: task
priority: normal
created_at: 2026-09-26T00:19:00Z
updated_at: 2026-09-26T15:20:00Z
---

Standardize all developer and CI project verification tasks through native `uv` commands and evaluate retiring or
replacing `make check`.

## Context & Problem Statement

Currently, `make check` is defined in `Makefile` as:

```makefile
check: lint lint-docs

lint:
	uv lock --check
	git diff --exit-code uv.lock
	uv run ruff check .
	uv run ruff format --check .

lint-docs:
	npx --yes prettier@3.8.4 --check "**/*.md"
```

In Python/uv ecosystems:

1. Developers and agents should be able to execute all testing, linting, formatting, and verification tasks directly
   through the `uv` toolchain (e.g. `uv run ruff check .`, `uv run pytest`, `uv run task ...`) without depending on GNU
   Make or external make wrappers.
2. `pyproject.toml` already includes `taskipy` under dev dependencies (`[tool.taskipy.tasks]`), supporting native
   `uv run task <target>` definitions (e.g. `uv run task check`, `uv run task lint`, `uv run task format`).
3. Markdown formatting (`prettier`) can either be invoked as a dedicated script/hook or wrapped within task runner
   tooling.
4. Requiring GNU Make introduces unnecessary platform friction (e.g. differences between GNU Make, BSD Make, and Windows
   environments) for what should be native Python toolchain operations.

## Acceptance Criteria

1. **Audit `make check` usage**: Identify all references to `make check` across GitHub Actions workflows, documentation
   (`README.md`, `AGENTS.md`, `.agents/`), and scripts.
2. **Define Native `uv` Verification Workflows**:
   - Standardize equivalent native `uv` commands in `pyproject.toml` under `[tool.taskipy.tasks]` or direct `uv run`
     commands:
     - Linting: `uv lock --check`, `uv run ruff check .`, `uv run ruff format --check .`
     - Testing: `uv run pytest -m "not integration_test"`
     - Markdown docs hygiene: document/script native execution (e.g. via `npx prettier --check "**/*.md"` or task
       definition).
     - Unified check: `uv run task check` that runs all static validations.
3. **Evaluate Makefile Retirement or Simplification**:
   - If `Makefile` is retained for Docker orchestration (`make build-images`, `make test-integration`), ensure all
     Python verification targets delegate to `uv run` commands or are superseded by direct `uv` invocations.
   - If `make check` is deemed redundant, remove or alias it to `uv run task check`.
4. **Update CI/CD and Agent Documentation**:
   - Update `.github/workflows/` (e.g. `hygiene.yml`, `ci.yml`) to invoke native `uv` / `npx` steps directly.
   - Update `.agents/rules.md` and contributor guides to specify `uv run` commands as the primary task execution
     interface.

## Status Verification (2026-09-26)

Still open. Verified against the current tip of the target repository: `Makefile:78` still defines
`check: lint lint-docs`, and the CI workflows still shell out through `make`.
