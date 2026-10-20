---
# holon-agentic-coder-ref-metadata-0128
title: "Audit ecosystem documentation and remediate coverage gaps across Holon flow lifecycle"
status: in-progress
type: task
priority: normal
tags:
  - documentation
  - audit
  - holon-flow
  - ledger
  - standards
  - en-au
created_at: 2026-10-19T12:41:00Z
updated_at: 2026-10-19T12:41:00Z
---

Conduct a comprehensive audit of holon-agentic-coder documentation and specifications to identify and remediate gaps,
reconciling docs with recently landed features, architectural invariants, and flow commands.

## Context

Recent milestones across the Holon ecosystem introduced key architectural, operational, and tooling enhancements:

- The 5-stage automated Holon flow lifecycle (`holon flow` CLI runner with checkpointing and flags).
- Autonomous native Stage 4 review loop (`holon review-loop` / `pr-review-loop`) and Stage 5 calibration
  (`holon calibrate`).
- Canonical 3-ledger architecture (`intents.jsonl`, `plans.jsonl`, `executions.jsonl`) with interleaved micro-actions
  (`entry_type: "action"`) under `LedgerLock` (retirement of auxiliary `actions.jsonl`).
- Hardened sandbox container security (`--cap-drop=ALL`, `--security-opt=no-new-privileges`, non-root execution).
- Unified Git repository abstraction (`sandbox_executor.git`).
- Strict test execution standards (`uv run pytest`, zero `PYTHONPATH` overrides).
- Australian English spelling standardization across user-facing documentation, manuals, and code comments.

Existing documentation across `docs/` and `README.md` must be systematically audited against these capabilities to
identify missing sections, outdated legacy descriptions (e.g. outdated ledger schemas, missing flow runner parameters),
and formatting inconsistencies.

## Tasks

- [ ] Audit `docs/ledger_schema.md` and `docs/architecture.md` to ensure full alignment with the canonical 3-ledger
      layout, `LedgerLock` concurrency, and unified micro-action logging in `executions.jsonl`.
- [ ] Document the complete `holon flow` CLI options, stage state machine, and autonomous review-loop invocation in
      `apps/sandbox-executor/README.md` and `docs/stage-machine.md` or equivalent guides.
- [ ] Document sandbox container security parameters (`--cap-drop=ALL`, non-root container isolation) and unified
      `sandbox_executor.git` abstraction in developer guides.
- [ ] Validate and enforce Australian English spelling across all modified documentation.
- [ ] Format modified documentation with Prettier and verify quality gates.
