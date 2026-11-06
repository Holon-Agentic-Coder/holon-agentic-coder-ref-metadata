---
# holon-agentic-coder-ref-metadata-0218
title: "Port harness skills and guidance to bd and sequence the harness retirement"
status: todo
type: task
priority: normal
tags:
  - issue-tracking
  - beads
  - harness-deprecation
  - skills
blocked_by:
  - "0214"
  - "0216"
  - "0217"
created_at: 2026-10-30T00:00:00Z
updated_at: 2026-10-30T00:00:00Z
---

## Problem

Harness skills and guidance are written against the beans CLI and `.beans/`: `prioritise-beans` (triage matrix), bean
references in `pr-review-loop` and `.agents/workflows.md`, and the AGENTS.md beans section. Once both targets run beads,
these must be ported or retired, and the harness itself archived without a tracking gap.

## Scope

- Replace the `prioritise-beans` matrix workflow with `bd ready --json` + priorities + dependency graph; retire
  `bean-triage-prioritisation.md`.
- Update skills and `.agents/` docs that cite beans conventions to cite `bd` and target-native ids.
- Retirement order of operations (from Bean 0156): both pilots accepted → open beans imported (Bean 0215 routing) →
  skills ported → harness archived **read-only** (completed/scrapped beans freeze in its history; `harness-bean-0NNN`
  labels keep citations traceable). No deletion.

## Notes

- **Harness work** (this repository only; no Holon flow). Blocked by Beans 0214, 0216 and 0217.
- Related: Bean 0156 decision points 3 and 6 (closed-bean history, retirement trigger), Bean 0182 (event watcher may
  also retire or move with the harness — do not duplicate; reference only).
