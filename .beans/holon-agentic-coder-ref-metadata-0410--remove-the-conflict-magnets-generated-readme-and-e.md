---
# holon-agentic-coder-ref-metadata-0410
title:
  "Remove the conflict magnets: generated README and env docs, and a module budget file that does not serialise flows"
status: todo
type: feature
priority: high
tags:
  - architecture
  - flow
  - merge-conflicts
  - admission
  - holon-agentic-coder
created_at: 2026-11-24T11:00:00Z
updated_at: 2026-11-24T11:00:00Z
---

## Why

A few shared files are in almost every touch set, so Stage 3 admission keeps flows waiting on each other and merges of
`main` conflict on them. Flows waited 39.8 hours in total on other flows in the period.

## Evidence

Logged by the self-improvement audit of 2026-11-24 (first audit, period 2026-11-21 to 2026-11-24T11:00Z). The scripts
and their output are in the git-ignored audit folder `todo/self-improvement-audit-2026-11-24/`.

Files named in Stage 3 overlap refusals (count of refusal lines) and in unresolvable merge conflicts:

| File                                                                | Overlap refusals | Unresolvable conflicts |
| :------------------------------------------------------------------ | ---------------: | ---------------------: |
| `apps/sandbox-executor/README.md`                                   |              106 |                      0 |
| `apps/sandbox-executor/flow_module_budgets.json`                    |               67 |                      8 |
| `apps/sandbox-executor/src/sandbox_executor/flow/__init__.py`       |               53 |                      5 |
| `docs/environment_variables.md`                                     |               43 |                      0 |
| `apps/sandbox-executor/src/sandbox_executor/env_registry.py`        |               43 |                      0 |
| `docs/git_flow.md`                                                  |               34 |                      0 |
| `apps/sandbox-executor/src/sandbox_executor/flow/stages/execute.py` |               31 |                      0 |

- 50 of the 140 flow runs in the period ended at a Stage 3 overlap refusal; the 48 measured waits total 39.8 hours
  (median 1.1 minutes, longest 17.5 hours on execute-stage-object).
- Reviewers raised 20 documentation-drift findings (README key tables and module maps out of step with the code, for
  example "The README Accepted keys paragraph lists only 8 of the 14 PROJECT_REFUSED_KEYS").

## Proposed change

1. The README's module map and key tables, and `docs/environment_variables.md`, are generated from the code (the env
   registry, the package tree) by a script that CI checks for drift. A flow changes the registry, never the generated
   text by hand, so the README drops out of touch sets.
2. `flow_module_budgets.json` stops being a single shared file every refactor edits: per-package budget files, or
   budgets derived from a rule with only the exceptions listed. **Needs the maintainer's word before any change to the
   budget mechanism** (standing rule: the budget file is not touched without explicit instruction).
3. `flow/__init__.py` holds no logic and no growing re-export list (Bean 0379).
4. Admission treats a generated file as non-overlapping, since it is regenerated after a merge.

## Expected gain

The README alone appears in 106 refusals and the budget file in 67 refusals and 8 unresolvable conflicts. Removing them
from touch sets lets most of the 39.8 hours of overlap waiting run in parallel and removes the 20 drift findings.

## Cost

Medium: one generator script and a drift test in the target repository; the budget change is a maintainer decision.

## Notes

- Related: Bean 0379 (no logic in `__init__.py`), Bean 0380 (module budget on every package), Bean 0395 (work during the
  overlap wait), Bean 0376 (in-flow conflict resolver), Bean 0174 (environment variable documentation).
