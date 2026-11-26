---
# holon-agentic-coder-ref-metadata-0565
title: "Check: intent scope lists files only, never directories or globs"
status: todo
type: task
priority: high
tags:
  - invariants
  - intent
  - overlap
  - holon-agentic-coder
created_at: 2026-11-26T23:09:56Z
updated_at: 2026-11-26T23:09:56Z
---

## Instruction (maintainer, 2026-11-27 local)

"For the invariants that are not explicitly checked or there's no tests, create a bean so the invariants NEVER slip
through." Parent: Bean 0562.

## Invariant

Intent scope lists files. Directories and globs widen the touch set and block every other flow at Stage 3.

## Check

- `holon intent-check` fails on a scope entry that is a directory, ends in `/`, or contains glob characters; it also
  warns on known hub files (`flow/lazy_exports.py`, `conftest.py`, `docs/*.md`, `scripts/pre_commit_check.py`).
- Stage 1 refuses such an intent the same way (not only the CLI check).

## Common acceptance

- The check runs automatically (pre-commit hook and/or CI, and the flow gate where it applies); no agent has to remember
  it.
- The check is proven to fail on a real or reconstructed violation (a test with today's evidence) before it is trusted,
  and passes on the cleaned state.
- Self-explaining code invariant in anything written: no docstrings, no comments except `# why:`.
- Target-repository work goes through `holon flow`; the intent never names harness paths or bean ids.
