---
# holon-agentic-coder-ref-metadata-0171
title: "Stage 3 budget breach commits the notes and ledger but discards the executor's code changes"
status: todo
type: bug
priority: critical
tags:
  - executor
  - budgets
  - holon-flow
  - holon-agentic-coder
created_at: 2026-10-27T13:20:33Z
updated_at: 2026-10-27T13:20:33Z
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
