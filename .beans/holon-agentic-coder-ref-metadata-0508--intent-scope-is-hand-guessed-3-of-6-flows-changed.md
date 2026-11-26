---
# holon-agentic-coder-ref-metadata-0508
title: "Intent scope is hand-guessed: 3 of 6 flows changed files they did not list"
status: todo
type: task
priority: high
tags:
  - flow
  - intent
  - scope
  - holon-agentic-coder
created_at: 2026-11-26T10:50:00Z
updated_at: 2026-11-26T10:50:00Z
---

## Problem

Self-improvement audit 2026-11-26T10:50Z. Comparing each intent's `scope` with the merged PR's files:

| PR  | Listed but unchanged                                       | Changed but unlisted (non-bookkeeping)                                                                     |
| :-- | :--------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------- |
| 326 | `scripts/check_module_budgets.py`                          | `holon-config/prompts/planner.template.md`                                                                 |
| 327 | `test_executor_agent_output_redaction.py`, `test_merge.py` | 10 files: `doctor_replay.py`, `fast_home.py`, `ledger_parity_rows.py`, `make_dry_run.py`, 3 new tests, ... |
| 330 | none                                                       | `flow/review/loop.py`                                                                                      |
| 331 | `tests/test_wisdom.py`                                     | none                                                                                                       |

#325 and #329 matched exactly. On #327 the executor's edit outside the touch set returned the plan to Stage 2 at
`08:28:01Z`; the re-plan plus a second admission cost about 33 min (Stage 2 at `07:56`, Stage 3 end at `09:03`, against
18 to 24 min for a clean Stage 3 elsewhere). The flows with unlisted files passed review (beans 0492, 0502 cover the
engine side).

## Proposed fix

- A pre-launch intent check (`holon intent check <intent.json>`, read-only) that proposes companion files for the listed
  scope from the import graph (modules imported by listed tests, tests importing listed modules) and from co-change in
  `git log`, and warns about listed files that do not exist or that no acceptance criterion needs.
- Intent authors run it before launch; the intent instructions say so.

## Expected gain

Avoids a Stage 3 to Stage 2 round trip (about 33 min on #327) and the unlisted-file findings; 3 of 6 flows today. Cost:
a small read-only command.

## Update 2026-11-26T12:20Z (audit)

Seven more flows (#332, #333, #335 to #339), scope against the PR files (non-bookkeeping): #333, #336, #339 match
exactly; #332 changed 4 unlisted files (`hermetic_repos.py`, `stage_templates.py`, `sync_boundary_repos.py`,
`test_stage_templates.py`) and left 2 listed unchanged; #335 added `test_calibrate_final_head_ci.py`; #337 added
`test_ci_bookkeeping_chain.py`; #338 added `preflight.py`, `preflight_secret_args.py`, `test_preflight.py`. All passed
review. Combined with the table above: 7 of 13 flows escaped scope (54 %). The decomposed 0407 flow lost about 67 min of
discarded Stage 3 turns plus about 12 min of re-plan in 4 of its 5 children (child 1 15.6 min, child 2 11.8, child 3
26.0, child 5 13.3; escapes were `flow/__init__.py` re-exports, an app README and a fixture), the same pattern bean 0414
measured. Priority stays high; this is the cheapest fix at the source and should be picked before 0414 (engine side).
The most common escapes are companion files (package re-export, README, fixture, a test that exercises the changed
module), which the proposed `holon intent check` can list deterministically.

## Notes

Related: 0492, 0502, 0414, 0481 (engine-side touch-set handling).
