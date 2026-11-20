---
# holon-agentic-coder-ref-metadata-0218
title: "Port harness skills and guidance to GitHub Issues and sequence the harness retirement"
status: todo
type: task
priority: normal
tags:
  - issue-tracking
  - github-issues
  - harness-deprecation
  - skills
blocked_by:
  - "0215"
  - "0216"
  - "0217"
created_at: 2026-10-30T00:00:00Z
updated_at: 2026-11-19T11:30:00Z
---

## Problem

Harness skills and guidance are written against `.beans/`: `prioritise-beans` (triage matrix), the bean steps in
`post-pr-merge`, bean references in `pr-review-loop` and `.agents/workflows.md`, and the AGENTS.md beans section. Once
both targets track work in GitHub Issues (Bean 0333; this bean was written for `bd`), these must be ported or retired,
and the harness itself archived without a tracking gap.

## Scope

- Replace the `prioritise-beans` matrix with a query over issues (`gh issue list --json`, priority labels, dependencies)
  that lists what is open and unblocked; retire `bean-triage-prioritisation.md`. The overlap lanes ("these touch the
  same files") need a home, since GitHub has no field for them: a label per lane or a note on the Project.
- `post-pr-merge`: drop the bean-closing step (the merge closes the issue through `Closes #N`); keep the fast-forward,
  reinstall, clean-up and next-work recommendation.
- Update skills and `.agents/` docs that cite beans conventions to cite issues and `#N`.
- Decide where harness-only work lives until retirement: remaining beans, or issues in the harness repository.
- Retirement order: importer run for both targets (Beans 0215, 0217) → flow linkage live (Bean 0216) → skills ported →
  harness archived **read-only** (completed and scrapped beans freeze in its history; the bean-to-issue mapping file
  keeps citations traceable). No deletion.

## Notes

- **Harness work** (this repository only; no Holon flow). Blocked by Beans 0215, 0216 and 0217.
- Related: Bean 0333 (decision), Bean 0182 (event watcher may also retire or move with the harness; reference only).
