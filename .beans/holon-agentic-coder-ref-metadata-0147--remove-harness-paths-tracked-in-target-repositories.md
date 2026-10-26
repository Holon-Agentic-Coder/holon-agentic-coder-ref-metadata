---
# holon-agentic-coder-ref-metadata-0147
title: "Remove harness paths (todo/, .subagent/) tracked in the target repositories"
status: todo
type: bug
priority: normal
tags:
  - harness-isolation
  - hygiene
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-10-24T01:41:18Z
updated_at: 2026-10-24T01:41:18Z
---

## Problem

AGENTS.md item 12 says the target repositories must never know about harness directories or conventions (`.beans/`,
`todo/`, `.agents/`), and `.subagent/` falls under the same principle. The Stage 4 review loops of 2026-10-24 found
these tracked on `origin/main`:

| Repository          | Path                                                                         | Introduced by      |
| ------------------- | ---------------------------------------------------------------------------- | ------------------ |
| holon-agentic-coder | `todo/ab_measure_all_methods.py`, `todo/ab_real_api_results.{json,md}`       | PR #52 (`e87e017`) |
| holon-agentic-coder | `.subagent/.gitkeep`                                                         | PR #53 (`54a2af1`) |
| holon-agentic-coder | `docs/optimisation/token_reduction_ab_testing.md` points at a `todo/` script | PR #52             |
| holon-coherence     | `todo/mitm_wire_logs` default path in `mitm_addon.py` and `metrics.py`       | pre-existing       |

Both repositories also track `.agents/AGENTS.md`. That is the target's own agent guide, not the harness's, so it is out
of scope unless it references harness paths.

## Scope

- Move the A/B measurement script and results to a target-native location (for example `scripts/` and
  `holon-knowledge/`), or delete them if superseded, and update the doc that references them.
- Remove `.subagent/.gitkeep` and any `.subagent/` ignore or reference in the target.
- Change coherence's wire-log default to a target-native path (`.holon/` or similar), with a migration note.
- Add a hygiene test or pre-commit check in each target that fails if tracked files live under, or reference, `todo/`,
  `.subagent/` or `.beans/`.

## Notes

- Run through the Holon flow, once per target repository.
- Found by: PR #92 resolver iteration 3, PR #95 dry-run iteration 1, PR #27 dry-run iteration 5.
