---
# holon-agentic-coder-ref-metadata-0571
title: "Check: bean files have sequential ids, valid status and frontmatter"
status: completed
type: task
priority: normal
tags:
  - harness
  - beans
  - invariants
created_at: 2026-11-26T23:09:56Z
updated_at: 2026-11-26T23:19:28Z
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

## Resolution

Done for the harness. `check_beans.py` enforces file name and id match, sequential ids (legacy gaps 0456, 0457,
0553-0555 listed as known), no duplicates, valid status, required fields, `blocked_by` targets exist, and timestamps
(see bean 0561). Runs in `uv run pytest` (real-repo test), `.agents/hooks/pre-commit` and the hygiene workflow. Three
legacy beans fixed (0031 id comment, 0222 missing stamps, 0256 updated before created).
