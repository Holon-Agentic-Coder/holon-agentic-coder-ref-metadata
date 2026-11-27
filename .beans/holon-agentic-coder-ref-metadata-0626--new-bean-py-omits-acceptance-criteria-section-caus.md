---
# holon-agentic-coder-ref-metadata-0626
title: "new_bean.py omits Acceptance Criteria section causing run_holon_flow pre-flight exit 2"
status: todo
type: bug
priority: normal
tags:
  - harness
  - beans
  - preflight
created_at: 2026-11-27T10:55:04Z
updated_at: 2026-11-27T10:56:02Z
---

## Notes

### Evidence (2026-11-27T07:49Z–10:49Z fifth-merge audit)

- **`CF-0049` (`08:09:17Z`):** Audit-created bean `0617` was generated via `.agents/scripts/new_bean.py`, whose
  `skeleton()` (`lines 38–44`) emits only `## Notes` and `## Resolution`, omitting `## Acceptance Criteria`.
- Because `run_holon_flow.py` pre-flight runs `intent_coverage.py` (`0589`, which rejects beans lacking an `Acceptance`
  / `Acceptance Criteria` section with exit code `2`), launching `0617` halted immediately at pre-flight (`<1 min`)
  until `## Acceptance Criteria` was manually patched into `0617` and `0618`.

### Proposed Change

1. Update `skeleton()` in `.agents/scripts/new_bean.py` to include an explicit `## Acceptance Criteria` section (between
   `## Notes` and `## Resolution`) with a checklist placeholder.
2. Add a check in `.agents/scripts/check_beans.py` / `staged_validation.py` warning or rejecting new
   `todo`/`in-progress` beans that lack an `## Acceptance` or `## Acceptance Criteria` heading.

### Expected Gain & Cost

- Eliminates immediate `run_holon_flow.py` pre-flight exit-2 halts (`CF-0049`) on newly created audit and coordinator
  beans.
- Cost: ~10 lines in `new_bean.py`, `staged_validation.py` / `check_beans.py`, and harness tests.

## Acceptance Criteria

- [ ] `uv run python .agents/scripts/new_bean.py` emits a `## Acceptance Criteria` section in every newly generated bean
      file.
- [ ] `uv run pytest` passes for harness script tests verifying the new skeleton and acceptance-heading validation.

## Resolution
