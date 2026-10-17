---
# holon-agentic-coder-ref-metadata-0120
title: "Implement prioritise-beans skill and triage matrix generator"
status: completed
type: task
priority: normal
tags:
  - skills
  - beans
  - triage
  - automation
  - tooling
created_at: 2026-10-17T13:10:00Z
updated_at: 2026-10-17T13:25:00Z
---

## Summary

Implement the `prioritise-beans` agent skill (`.agents/skills/prioritise_beans/SKILL.md`) and a companion Python
automation script (`scripts/prioritise_beans.py`) that scans the repository's `.beans/` directory, extracts metadata,
computes progress metrics, filters out all completed and scrapped beans, and generates/updates the standardized Active
Beans Triage and Prioritisation Matrix in `todo/bean-triage-prioritisation-<YYYY-MM-DD>.md`.

## Context & Problem Statement

Prioritizing and triaging beans across the Holon ecosystem has historically been performed manually or semi-manually,
leading to formatting drift, outdated milestone metrics, inconsistent column ordering, and bulky file-URL clutter. A
dedicated skill and script guarantees:

1. Strict adherence to the triage schema:
   `| Priority | Status | Impact | Sizing | Bean # | Title | Domain | Dependencies / Notes |`
2. Exclusion of all completed or scrapped beans from the active triage matrix.
3. Clean 4-digit bean numbers instead of bulky URLs.
4. Deterministic sorting by Priority (`P0` -> `P1` -> `P2` -> `P3`) and Status.

## Tasks & Scope

- [x] Create `.agents/skills/prioritise_beans/SKILL.md` documenting the skill invocation, schema, and rules.
- [x] Implement `.agents/skills/prioritise_beans/scripts/prioritise_beans.py` with CLI flags (`--output`, `--date`,
      `--dry-run`).
- [x] Verify parsing, exclusion of completed beans, and formatting.
- [x] Run script to produce `todo/bean-triage-prioritisation-2026-10-18.md`.

## Resolution Summary

1. Implemented `.agents/skills/prioritise_beans/scripts/prioritise_beans.py` using standard library Python.
2. Built frontmatter and markdown extractor that calculates completion percentages, excludes completed and scrapped
   beans from the matrix, and formats table with clean 4-digit bean numbers.
3. Created `.agents/skills/prioritise_beans/SKILL.md` defining core invariants and CLI options.
4. Generated clean triage matrix at `todo/bean-triage-prioritisation-2026-10-18.md` and updated
   `todo/bean-triage-prioritisation-2026-10-17.md`.
