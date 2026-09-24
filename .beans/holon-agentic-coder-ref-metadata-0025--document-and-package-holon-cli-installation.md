---
# holon-agentic-coder-ref-metadata-0025
title: Package, document, and support global installation and ephemeral execution of holon CLI
status: completed
type: task
created_at: 2026-09-17T00:00:00Z
updated_at: 2026-09-22T00:00:00Z
---

Configure entrypoints and package naming in `apps/sandbox-executor/pyproject.toml` and document standard execution
pathways for the `holon` CLI so external projects and developers can run Holon either ephemerally (using `uvx`) or
persistently (using `uv tool install`). Covers running the latest tip (`--refresh` against `@main`), pinned versions
(`@<tag-or-sha>`), local editable installs, and tool upgrades.

## Notes

- Target repository: holon-agentic-coder (apps/sandbox-executor/pyproject.toml and documentation)
- Implementation: configure `name = 'holon'` in `apps/sandbox-executor/pyproject.toml` (aligning package name so
  `uv tool` names the installed environment `holon`) and `[project.scripts] holon = 'sandbox_executor.cli:main'`
  (coordinated with Bean 0024). Uncomment and activate `[build-system]` (`hatchling.build`) and
  `[tool.hatch.build.targets.wheel]` in `apps/sandbox-executor/pyproject.toml` so wheel builds succeed during `uvx` and
  `uv tool install`.
- Ephemeral execution (latest): uvx --refresh --from
  'git+https://github.com/Holon-Agentic-Coder/holon-agentic-coder.git@main#subdirectory=apps/sandbox-executor' holon
  <subcommand>
- Ephemeral execution (pinned): uvx --from
  'git+https://github.com/Holon-Agentic-Coder/holon-agentic-coder.git@<tag-or-sha>#subdirectory=apps/sandbox-executor'
  holon <subcommand>
- Ephemeral execution caveat: Ephemeral execution must explicitly use the
  `--from 'git+https://github.com/Holon-Agentic-Coder/holon-agentic-coder.git#subdirectory=apps/sandbox-executor'`
  parameter (or local path `--from apps/sandbox-executor`) rather than bare `uvx holon` to prevent package namespace
  collisions with PyPI before official namespace reservation.
- Global installation: uv tool install
  'git+https://github.com/Holon-Agentic-Coder/holon-agentic-coder.git@<tag-or-main>#subdirectory=apps/sandbox-executor'
- Global tool upgrade: uv tool upgrade holon (or `uv tool upgrade sandbox-executor` if package name remains
  sandbox-executor)
- Local editable installation: uv tool install --editable apps/sandbox-executor
- Workspace Synchronization: Update root `holon-agentic-coder/pyproject.toml` dependency to `holon` and update
  `[tool.uv.sources] holon = { path = 'apps/sandbox-executor', editable = true }`, then run `uv lock` to maintain
  lockfile integrity.
- Documentation: Update README.md and docs in holon-agentic-coder to guide multi-repo / external project usage,
  highlighting the `--from` requirement for ephemeral uvx execution to avoid PyPI namespace collisions.
- Merged: holon-agentic-coder PR #52 (2026-09-20), merge commit a4d6930 on origin/main (current main tip).
- Post-merge audit 2026-09-22: local pr-52 worktree/branch deleted (PR head 528c336 confirmed an ancestor of the merged
  head 8735755, so no unique work) and the local intent branch I-1789686556-.../E-1789687466-.../_ deleted after
  verifying 12/14 touched paths are byte-identical blobs already on origin/main.
- Open follow-up: three origin/I-1789686556-* intent branches remain on the remote with 1-2 unmerged commits and no
  associated PR; deletion withheld pending explicit maintainer authorisation (AGENTS.md rule 7).

## Assignment

Assignee: `Antigravity`

## Resolution

Successfully implemented Bean 25 strictly using the containerized Holon Flow lifecycle (Intent -> Plan -> Execute):

1. Intent: Logged intent `intents/package-and-document-holon-cli.json` and executed `./holon intent` to produce intent
   branch `I-1789686556-package-and-document-holon-cli/_`.
2. Plan: Generated 4-step execution plan using `antigravity-agent` (`gemini-3.8-flash-medium`) on branch
   `I-1789686556-package-and-document-holon-cli/P-1789686633-antigravity-agent-gemini-3.8-flash-medium/_`.
3. Execute: Executed plan via containerized agent runner on branch
   `I-1789686556-package-and-document-holon-cli/P-1789686633-antigravity-agent-gemini-3.8-flash-medium/E-1789687466-antigravity-agent-gemini-3.8-flash-medium/_`.
4. Packaging & Sync: Configured `apps/sandbox-executor/pyproject.toml` with `name = "holon"`,
   `[project.scripts] holon = "sandbox_executor.cli:main"`, and hatchling wheel build target
   `packages = ["src/sandbox_executor"]`. Synchronized root `pyproject.toml` dependency to `holon` with editable source
   mapping and updated `uv.lock`.
5. Documentation & Verification: Documented execution pathways in `README.md`, `docs/sandbox/create_intent.md`,
   `docs/sandbox/create_plan.md`, and `docs/sandbox/execute_plan.md`, detailing ephemeral execution (`uvx`), global
   installation (`uv tool install`), upgrades, and local editable workflows, highlighting the `--from` requirement to
   avoid PyPI namespace collisions. Validated wheel creation with `uv build --wheel` and verified test suite passing
   (221 passed unit tests, ruff lint and formatting passed, prettier formatting applied). Landed on origin/main as merge
   commit a4d6930 via holon-agentic-coder PR #52 (merged 2026-09-20).
