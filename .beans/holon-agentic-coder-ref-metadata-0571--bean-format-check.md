---
# holon-agentic-coder-ref-metadata-0571
title: "Check: bean files have sequential ids, valid status and frontmatter"
status: todo
type: task
priority: normal
tags:
  - harness
  - beans
  - invariants
created_at: 2026-11-26T23:09:56Z
updated_at: 2026-11-26T23:09:56Z
---

## Instruction (maintainer, 2026-11-27 local)

"For the invariants that are not explicitly checked or there's no tests, create a bean so the invariants NEVER slip
through." Parent: Bean 0562.

## Invariant

Bean ids are strictly sequential 4-digit integers (next = highest + 1), file names match ids, status is one of
`draft|todo|in-progress|completed|scrapped`, required frontmatter present, `blocked_by` refers to existing beans,
timestamps valid (with 0561).

## Check

- `uv run pytest` test over `.beans/` plus the pre-commit hook; no gaps or duplicates among new ids, no random base36
  ids.

## Common acceptance

- The check runs automatically (pre-commit hook and/or CI, and the flow gate where it applies); no agent has to remember
  it.
- The check is proven to fail on a real or reconstructed violation (a test with today's evidence) before it is trusted,
  and passes on the cleaned state.
- Self-explaining code invariant in anything written: no docstrings, no comments except `# why:`.
- Target-repository work goes through `holon flow`; the intent never names harness paths or bean ids.
