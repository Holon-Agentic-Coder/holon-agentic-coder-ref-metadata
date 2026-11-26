---
# holon-agentic-coder-ref-metadata-0215
title: "Deterministic beans-to-GitHub-Issues importer and real-data dry run"
status: in-progress
type: task
priority: high
tags:
  - issue-tracking
  - github-issues
  - migration
  - harness
created_at: 2026-10-30T00:00:00Z
updated_at: 2026-11-23T14:27:43Z
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

Open-bean count refreshed: about 40 active beans, not 50 (after the recent completions). Bean 0333 completed (PR #258),
so no blocker remains.

## Progress (2026-11-24)

- Built `.agents/scripts/beans_to_issues.py` (standard library; `gh` for the real import) and
  `tests/test_beans_to_issues.py`. Default is a dry run that renders payloads, labels, dependencies and a report under
  `todo/beans-to-issues-dry-run/`; `--apply` is the real import and has not been run. No issue or label was created.
- Dry run on the real corpus: 41 open beans, 35 to migrate (holon-agentic-coder 31, holon-coherence 4), 6 not migrated
  (harness-only), 0 mapped dependencies (the only open edges point at this bean, which is not migrated), 0 sub-issues,
  40 bean references become `#N`, 158 references to unmigrated beans are reworded, 31 harness paths removed.
- Open decisions for the maintainer: see the dry-run report and the reply that accompanied this bean.
