---
# holon-agentic-coder-ref-metadata-0215
title: "Deterministic beans-to-GitHub-Issues importer and real-data dry run"
status: todo
type: task
priority: high
tags:
  - issue-tracking
  - github-issues
  - migration
  - harness
blocked_by:
  - "0333"
created_at: 2026-10-30T00:00:00Z
updated_at: 2026-11-21T01:20:00+11:00
---

## Problem

Migrating from harness beans to GitHub Issues (decision in Bean 0333; this bean was the beans-to-beads converter) needs
a deterministic importer: bean frontmatter and Markdown body to an issue created with `gh`. No importer exists.

## Scope

- Map each open bean to one issue: title → title; body → body; `type` → `type:` label; `priority` → `priority:P0`-`P3`
  (the 7 invalid `medium` values → P2); tags → labels, dropping the routing tags; `blocked_by`/`blocking` → GitHub issue
  dependencies; `parent` → sub-issue; `in-progress` → open with the in-progress status.
- Strip harness references from what is written to a target: no bean ids and no `.beans/`, `todo/` or `.agents/` paths
  in titles or bodies. References to other beans become `#N` links once those beans have issues, so the import runs in
  two passes (create, then link).
- Routing: tags and mentions route each open bean to `holon-agentic-coder` or `holon-coherence`; emit a "not migrated"
  list for harness-only and dev-env beans.
- Keep the mapping (bean id → repository and issue number) in a harness file, so reruns are idempotent (no duplicate
  issues) and citations stay traceable after the harness is archived.
- Dry run on the **real** `.beans/` corpus (no synthetic data): render every issue payload, label set and dependency
  link to files without calling the API, and report per-field fidelity and anything that could not be mapped.
- Default scope migrates only open beans (about 40: todo, draft and in-progress). Closed history stays frozen in the
  harness.

## Notes

- **Harness work**: the importer lives in harness tooling; no Holon flow needed. Creating issues is an outward-facing
  write to public repositories, so the real import runs only on the maintainer's word, after the dry-run report.
- Creates the label set in each repository before the first import.
- Related: Bean 0333 (decision and field defaults), Bean 0216 (the flow uses the issue numbers), Bean 0317 (board).

## Audit (2026-11-21)

Open-bean count refreshed: about 40 active beans, not 50 (after the recent completions). Still blocked by Bean 0333.
