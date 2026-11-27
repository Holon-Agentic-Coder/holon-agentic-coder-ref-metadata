---
# holon-agentic-coder-ref-metadata-0598
title: "holon-coherence planner template has no Touch Set section, so every coherence flow is refused at Stage 3"
status: completed
type: bug
priority: critical
tags:
  - holon-coherence
  - holon-flow
  - planner
  - overlap
created_at: 2026-11-27T01:21:30Z
updated_at: 2026-11-27T05:20:22Z
---

## Cause

- The holon-coherence planner template (`apps/holon-coherence/main/holon-config/prompts/planner.template.md`) has no
  `## Touch Set` instruction and no `## Touch Set` block in its plan format example.
- The holon-agentic-coder planner template (`apps/holon-agentic-coder/main/holon-config/prompts/planner.template.md`)
  has both.
- Coherence plans therefore record `touch_set` as null, and Stage 3 admission refuses them with "plan has no ## Touch
  Set section".
- This blocks the coherence halves of beans holon-agentic-coder-ref-metadata-0563, holon-agentic-coder-ref-metadata-0564
  and holon-agentic-coder-ref-metadata-0567 (intents `todo/intent-0563-coherence-ledger-invariants.json`,
  `todo/intent-0564-coherence-no-harness-refs.json`, `todo/intent-0567-coherence-commit-trailer-check.json`).

## Fix

- Follow the slot keeper intent `todo/intent-0598-coherence-planner-touch-set.json` (scope:
  `holon-config/prompts/planner.template.md` and `tests/test_planner_template_touch_set.py`).
- Add the Touch Set instruction with the holon-agentic-coder wording: a `## Touch Set` section placed after the plan
  description and strategy section, listing files only, one backticked repository-relative path or glob per top-level
  bullet, excluding `plans/`, `executions/` and `holon-knowledge/`, and writing `- none` when no other file changes.
- Add the `## Touch Set` block with a `{repository_relative_path_or_glob}` placeholder to the plan format example.
- Keep every existing placeholder and section intact.
- Do not touch the module budget configuration.

## Acceptance

- The coherence planner template asks the planner for a `## Touch Set` section listing files only, using the same
  wording as the holon-agentic-coder template.
- A coherence plan generated from the template records a non-null touch set.
- A test in holon-coherence fails when the `## Touch Set` section is missing from the template.
- Stage 3 admission admits a coherence plan that carries a touch set, with no "plan has no ## Touch Set section"
  refusal.
- Self-explaining code invariant holds: no docstrings, and the only comments are `# why:` comments.

## Assumptions

- The holon-agentic-coder Touch Set wording is right for coherence. Validated by: a coherence plan generated from the
  updated template records a non-null touch set, and the template test asserts the heading, placement and exclusions.
- Coherence Stage 3 parses the same `## Touch Set` heading and bullet format as holon-agentic-coder. Validated by:
  reading the coherence admission parser and admitting a coherence plan fixture that carries the section.
- Coherence numbers its plan sections as `### 6. Plan Description & Strategy` rather than
  `## Plan Description & Strategy`, so the Touch Set placement is anchored on the strategy section, not on the heading
  level. Validated by: checking the rendered plan example places `## Touch Set` directly after the strategy section.

## Links

- holon-agentic-coder-ref-metadata-0563 (coherence ledger invariants)
- holon-agentic-coder-ref-metadata-0564 (coherence no harness references)
- holon-agentic-coder-ref-metadata-0567 (coherence commit trailer check)

## Resolution

Delivered via [PR #57](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/57) and merged into `main`
(`c26a0c11`):

- **Key Architectural Deliverables**: Added the `## Touch Set` instruction and `{repository_relative_path_or_glob}` plan
  format example block to `holon-config/prompts/planner.template.md` (excluding `plans/`, `executions/`, and
  `holon-knowledge/`, or `- none` when no other file changes), enabling Stage 3 touch-set admission for
  `holon-coherence` flows.
- **Verification & Tests**: Added `tests/test_planner_template_touch_set.py` and verified all 5 Holon flow stages
  (`I-1795742722-coherence-planner-touch-set/P-1795742758-CLA-CO5.5/E-1795742876-CLA-CO5.5/_`) including calibration
  (`P-1795742758-CLA-CO5.5_calibration.md`).
