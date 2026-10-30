---
# holon-agentic-coder-ref-metadata-0201
title: "Planner, executor and reviewer prompts carry the module-layout, complexity and naming rules"
status: todo
type: task
priority: normal
tags:
  - prompts
  - code-quality
  - concurrency
  - holon-agentic-coder
blocked_by:
  - holon-agentic-coder-ref-metadata-0185
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-29T12:20:00Z
---

## Problem

Spawned by Bean 0177. The god modules grew because each flow added code to the file it was already editing: `flow.py`
went from 4,434 lines (`b3e2727`, 2026-10-25) to 5,157 (`993b686`, 2026-10-29) in four days, and `cli.main` from 1,062
to 1,097 lines. Nothing in the role prompts tells the agents where new behaviour belongs.

## Scope

1. Add a short "Code placement" section to `holon-config/prompts/planner.template.md`, the executor prompt and the
   reviewer prompt: new behaviour goes in the module that owns the data (or a new module); one module per stage,
   command, runner or provider; functions within the ruff limits from 0185; intention-revealing names in the domain
   language (intent, plan, execution, review, calibration, ledger); no new imports from entrypoints into the host
   engine.
2. The planner lists its touch set at module granularity (feeds Bean 0151) and prefers plans that add files over plans
   that grow files over about 400 lines.
3. Reviewers flag growth of any file over 1,000 lines as Important.
4. Prompt-template tests (`tests/test_prompt_templates.py`) cover the new placeholders, if any.

## Touch set

`holon-config/prompts/*.template.md`, `tests/test_prompt_templates.py`, `docs/architecture.md` (one cross-reference).

## Dependencies

Blocked by 0185 (the thresholds it cites). Parallel-safe with everything except other prompt changes.

## Notes

- Run through the Holon flow on holon-agentic-coder. Prompt text must not mention harness paths or bean ids.
