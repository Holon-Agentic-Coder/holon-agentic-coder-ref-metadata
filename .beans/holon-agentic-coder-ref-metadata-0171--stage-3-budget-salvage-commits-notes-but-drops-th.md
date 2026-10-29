---
# holon-agentic-coder-ref-metadata-0171
title: "Stage 3 budget breach commits the notes and ledger but discards the executor's code changes"
status: completed
type: bug
priority: critical
tags:
  - executor
  - budgets
  - holon-flow
  - holon-agentic-coder
created_at: 2026-10-27T13:20:33Z
updated_at: 2026-10-29T06:40:00Z
---

## Problem

Found on 2026-10-27 running Bean 0168 through `holon flow` on claude-agent (log `todo/logs/0168-flow.log`). Stage 3 used
44.1 of its 43.9 minutes and failed. The executor had edited 14 files: `tests/conftest.py`, `hermetic_fixtures.py`, six
test files, `.github/workflows/test-unit.yml`, `pyproject.toml`, `uv.lock` and two docs. Its execution notes record
steps 2-4 as complete and measured.

The failure commit `f93c4f2` ("execute: ... failed for plan ...") staged only
`executions/E-1793104532-claude-agent-claude-opus-5-5.md` and `holon-knowledge/ledger/executions.jsonl`. Every code
change was left unstaged (`git status` showed `M` without staging) and was lost when the `--rm` container exited. The
pushed execution branch has notes describing work that does not exist in it.

Bean 0139's design says a budget breach salvages the partial artefact. In this case the artefact was only the notes; the
work itself was discarded.

## Scope

- On any Stage 3 failure, including a budget breach or an agent exit other than 0, commit the agent's working-tree
  changes to the execution branch, with a commit message that marks them as partial and failed, so that a resume or a
  human can continue from them. They must never be silently dropped.
- Resume must be able to continue from the partial execution, starting from its head instead of the plan branch.
  Alternatively, document clearly that a resume restarts from the plan.
- The executor prompt should ask the agent to commit its work step by step. With a long plan, budget exhaustion is then
  cheap.
- Tests: a budget breach with dirty tracked and untracked files leaves them committed on the execution branch, and the
  ledger row records `outcome: failure` with the partial head.

## Notes

- Run through the Holon flow on holon-agentic-coder. It touches the executor entrypoint and `flow.py`, so run it
  sequentially.
- Workaround used for Bean 0168: re-run Stage 3 with `HOLON_STAGE_BUDGET_EXECUTE_MINUTES=120`.

## Resolution

Completed through the Holon flow on `holon-agentic-coder`:

- **Flow**: `I-1793246184-execute-failure-keeps-partial-code-and-resumes-from-it` →
  `P-1793246201-claude-agent-claude-opus-5-5` → `E-1793246527-claude-agent-claude-opus-5-5`.
- **PR #108** (https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/108): Stage 3 failure and budget-breach
  salvage now stages and commits working-tree changes as a partial head, emits a redacted format-patch on a refused push
  (with size caps and private-key / credential / env-file exclusions), and resumes Stage 3 from `failed_partial_head`
  (`failure` or `failed` ledger rows). Five resolver iterations (`406ef34`..`b1fa45f`), iteration 6 dry-run `APPROVED`
  with 10/10 CI green (including CodeQL), ledger conflicts resolved in `55a11e0`, and merged by the maintainer as
  `c7dfd5e` (2026-10-29T05:52:18Z, before Stage 5 calibration ran). Step-by-step executor commit guidance also landed in
  PR #105 (Bean 0178).
