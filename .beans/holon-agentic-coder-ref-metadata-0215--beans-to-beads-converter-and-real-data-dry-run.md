---
# holon-agentic-coder-ref-metadata-0215
title: "Deterministic beans-to-beads JSONL converter and real-data dry run"
status: todo
type: task
priority: high
tags:
  - issue-tracking
  - beads
  - migration
  - harness
blocked_by:
  - "0214"
created_at: 2026-10-30T00:00:00Z
updated_at: 2026-10-30T00:00:00Z
---

## Problem

Migrating from harness beans to target-native beads needs a deterministic converter: bean frontmatter + Markdown body to
beads JSONL consumable by `bd import` (which reads JSONL from file or stdin). Bean 0156 recorded the field mapping; no
converter exists.

## Scope

- Implement the converter per the mapping table in Bean 0156 (statuses, types, priorities incl. the 7 invalid `medium`
  values → P2, tags → labels, `parent`/`blocked_by`/`blocking` → deps, body → description, Resolution → close reason,
  bean id → `harness-bean-0NNN` label).
- Routing rules: tags/mentions route each open bean to `hac-` or `hcoh-`; emit a "not migrated" list for harness-only
  beans.
- Dry run with `bd import` into a scratch workspace on the **real** `.beans/` corpus (rule 10 — no synthetic data);
  report per-field conversion fidelity.
- Default scope migrates only open beans (~47: todo + in-progress); importing closed history is maintainer decision
  point 3 in Bean 0156.

## Notes

- **Harness work** (converter lives in harness tooling or `todo/` scratch; it writes nothing into targets — the actual
  import into a target happens under Bean 0214/0217 acceptance). No Holon flow needed.
- Depends on Bean 0214 for the final prefix/config; the converter and dry run can start against the documented JSONL
  schema beforehand.
- Sources: https://github.com/steveyegge/beads/blob/main/docs/CLI_REFERENCE.md (`bd import`, `bd export`).
