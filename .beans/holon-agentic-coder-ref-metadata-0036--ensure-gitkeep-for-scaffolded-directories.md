---
# holon-agentic-coder-ref-metadata-0036
title: "Ensure .gitkeep and directory persistence for scaffolded Holon project structures"
status: completed
type: task
priority: normal
tags:
  - scaffolding
  - holon-cli
  - git
created_at: 2026-09-26T09:05:00Z
updated_at: 2026-10-06T15:00:00Z
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

## Resolution (2026-10-06)

Resolved via the 5-stage Holon flow in Batch A (PR
[#67](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/67)):

- Updated `apps/sandbox-executor/src/sandbox_executor/scaffold.py` so `holon init` scaffolds `.gitkeep` across `plans`,
  `kb`, and `ledger` subdirectories under `holon-knowledge/`.
- Added scaffolding for `intents/` directory with `intents/.gitkeep` and `intents/README.md`.
- Added assertions in `apps/sandbox-executor/tests/test_init.py` verifying presence of `holon-knowledge/ledger/.gitkeep`
  and `intents/.gitkeep`.
- Verified idempotency: re-running `holon init` does not clobber existing `.gitkeep` or ledger files.
- Unanimously approved by 3-agent ensemble review
  ([receipt](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/67#pullrequestreview-5430326410)), Stage 5
  calibrated ($\Delta\text{EV}: +4.30$). Ready for human merge.
