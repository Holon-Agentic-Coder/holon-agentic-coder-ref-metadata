---
# holon-agentic-coder-ref-metadata-0159
title: "Executor ignores the intent's entropy budget and fabricates placeholder sub-intents"
status: in-progress
type: bug
priority: critical
tags:
  - executor
  - planner
  - decomposition
  - holon-flow
  - holon-agentic-coder
blocking:
  - holon-agentic-coder-ref-metadata-0151
created_at: 2026-10-26T04:31:31Z
updated_at: 2026-10-26T05:26:38Z
---

## Problem

Found on 2026-10-26 running Bean 0151 through `holon flow --agent claude-agent` (log `todo/logs/0151-flow-r3.log`). The
intent had `entropy_budget: 16.0`. The claude planner produced a sound plan with `entropy_pred 12.6`
(`P-1792988757-claude-agent-claude-opus-5-5`, EV 19.82). Stage 3 then printed "Plan entropy/structure requires
decomposition into 2 sub-intents", pushed an execution branch containing only two ledger rows, and halted for a human.

- `entrypoint/planner.py:322` shows the agent `intent_data["entropy_budget"]` (default `15.0`) as its budget.
- `entrypoint/executor.py:710` (`should_decompose()`) reads `plan_data["entropy_budget"]` with a default of `5.0`. The
  `plans.jsonl` row never carries `entropy_budget`, so every plan above 5.0 decomposes, whatever the intent allowed.
  Earlier plans passed only because they scored entropy 0.2–2.
- When the plan has no `Sub-Intents` section, `should_decompose()` invents two generic sub-intents (`sub-intent-part-1`
  "Implement component core logic", `sub-intent-part-2` "Implement integration tests and validation"). They are
  unrelated to the plan and are appended to `intents.jsonl`, which breaks the flow's own "refusing to fabricate" rule.
  The code dates from #26 (`eaf4757`).

Artifacts left on `origin` (audited provenance, do not rewrite):
`I-1792988604-touch-set-estimate-and-overlap-admission/P-1792988757-claude-agent-claude-opus-5-5/E-1792989014-claude-agent-claude-opus-5-5/_`
(`4ce9182`).

## Scope

- Carry the intent's `entropy_budget` into the plan row (`plans.jsonl`, documented in `docs/ledger_schema.md`) and have
  the executor compare against that same value. Use one default shared by planner and executor.
- **No human halt in Stage 3 (maintainer decision, 2026-10-26).** Execution must never stop to wait for a human review.
  Remove the Stage 3 `StageStatus.HALTED_FOR_HUMAN` path (`sandbox_executor/flow.py` around line 2983, "executor
  decomposed ... halting for human review"). The flow's only human boundary is the merge, after the review loop reaches
  consensus and Stage 5 calibration has run (`flow.py` around lines 4011 and 4531, which stay as they are).
- When a plan lists concrete sub-intents, the flow handles them autonomously: each sub-intent goes through the full
  pipeline (intent -> plan -> execute -> review -> calibrate) in order, never concurrently, without stopping for a
  human. Otherwise the executor executes the plan as written.
- Never synthesise sub-intents. Decomposition happens only when the plan itself lists concrete sub-intents. An
  over-budget plan without them goes back to Stage 2 automatically (bounded re-plan attempts, asking for a smaller plan
  or an explicit sub-intent list). If that is exhausted, the stage fails with a clear message, never a human halt, and
  appends no fake intent rows.
- Tests: Stage 3 never returns `HALTED_FOR_HUMAN`; an intent budget of 16 with plan entropy 12.6 executes; an
  over-budget plan with no sub-intent section re-plans and then fails without writing intents; an explicit sub-intent
  list is honoured.

## Notes

- **Second trigger (2026-10-26, 0159 run 1):** the first 0159 plan (`P-1792992418-claude-agent-claude-opus-5-5`, entropy
  4.5, EV 53.25) still halted with "decomposition into 1 sub-intents". `should_decompose()` checks
  `"## Sub-Intents" in plan_content` as a substring, and a prose mention (plan line 280) matched. It then starts
  collecting at the first line containing "Sub-Intents" (line 52) and turned an unrelated step bullet into a sub-intent.
  The parser must match only a real heading line. Run 2's intent forbids the literal token in the plan as a bootstrap
  workaround.

- Run through the Holon flow on holon-agentic-coder. It overlaps Bean 0151 on `entrypoint/planner.py`, so run it first
  and re-plan 0151 on the new `main`.
