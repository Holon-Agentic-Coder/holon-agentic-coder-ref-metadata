---
# holon-agentic-coder-ref-metadata-0001
title: Define template and schema for .beans task files
status: completed
type: task
created_at: 2026-07-18T00:00:00Z
updated_at: 2026-07-18T00:00:00Z
---

Create a template or schema describing the standard structure for task files in the .beans/ directory. This ensures
consistency as agents and humans log and track tasks.

## Assignment

Assignee: `antigravity`

## Resolution

Created .beans/template.yml file containing standard fields (id, title, type, status, assignee, description, created_at,
updated_at, notes, resolution) for task files. That template now lives at `.beans/template.md` and carries only the
fields the `beans` CLI persists; see the format rules in [.agents/workflows.md](../.agents/workflows.md).
