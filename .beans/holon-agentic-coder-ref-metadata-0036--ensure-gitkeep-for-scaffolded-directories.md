---
# holon-agentic-coder-ref-metadata-0036
title: "Ensure .gitkeep and directory persistence for scaffolded Holon project structures"
status: todo
type: task
priority: normal
tags:
  - scaffolding
  - holon-cli
  - git
created_at: 2026-09-26T09:05:00Z
updated_at: 2026-09-26T15:20:00Z
---

When initializing a new repository or onboarding a project using `holon init`, Git requires tracking at least one file
inside a directory to preserve that directory structure across clones and clean checkouts.

Currently, `holon init` scaffolds:

- `holon-config/` subdirectories (`world/`, `metrics/`, `prompts/`) which contain non-empty Markdown and JSON
  configuration files (tracked automatically by Git).
- `holon-knowledge/plans/` and `holon-knowledge/kb/` which already create `.gitkeep`.
- `holon-knowledge/ledger/` which creates three 0-byte `.jsonl` files (`intents.jsonl`, `plans.jsonl`,
  `executions.jsonl`).
- However, `holon-knowledge/ledger/` does not include a `.gitkeep`. If the 0-byte ledger files are cleaned, ignored, or
  reset, the `ledger/` directory is lost.
- Furthermore, `intents/` (the standard directory where operator intent definitions are staged for
  `./holon intent <file>`) is not currently scaffolded by `holon init`.

## Acceptance Criteria

1. Update `sandbox_executor.scaffold` in `apps/holon-agentic-coder/`:
   - Ensure `holon-knowledge/ledger/.gitkeep` is created to guarantee the `ledger/` directory is preserved even if
     `.jsonl` files are cleared, untracked, or empty.
   - Scaffold the `intents/` directory with an `intents/.gitkeep` (or `intents/README.md`) so new projects immediately
     have the canonical directory for storing intent JSON payloads.
2. Update unit tests in `apps/sandbox-executor/tests/test_init.py` to assert the presence of
   `holon-knowledge/ledger/.gitkeep` and `intents/.gitkeep`.
3. Verify idempotency: running `holon init` multiple times must preserve existing `.gitkeep` and configuration files
   without overwriting or erroring.
4. Verify all unit tests pass with `uv run pytest apps/sandbox-executor/tests/test_init.py`.

## Notes

- Target repository: `apps/holon-agentic-coder/`
- Target files:
  - `apps/sandbox-executor/src/sandbox_executor/scaffold.py`
  - `apps/sandbox-executor/tests/test_init.py`

## Status Verification (2026-09-26)

Still open. Verified against the current tip of the target repository: `scaffold.py` still creates `.gitkeep` for only
`plans/` and `kb/` (`for sub_dir in ["plans", "kb"]`); there is no `holon-knowledge/ledger/.gitkeep` and `intents/` is
still not scaffolded.
