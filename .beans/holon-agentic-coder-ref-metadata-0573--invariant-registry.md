---
# holon-agentic-coder-ref-metadata-0573
title: "Invariant registry: every hard rule maps to an automatic check"
status: todo
type: task
priority: critical
tags:
  - harness
  - invariants
  - tests
created_at: 2026-11-26T23:09:56Z
updated_at: 2026-11-26T23:09:56Z
---

## Instruction (maintainer, 2026-11-27 local)

"For the invariants that are not explicitly checked or there's no tests, create a bean so the invariants NEVER slip
through." Parent: Bean 0562.

## Invariant (meta)

An invariant is not done until its check exists.

## Check

- `.agents/invariants.yml` (harness) listing every hard rule from `AGENTS.md` and the maintainer invariants, each with
  the check that enforces it (test id, hook, CI job, or flow gate) and where it runs.
- `uv run pytest` test: every hard-rule bullet in `AGENTS.md` has a registry entry; every entry's check exists (test id
  resolvable, hook installed, workflow job present). Unmapped or dangling entries fail.
- `AGENTS.md` hard rule: "a new invariant lands together with its check and registry entry".

## Common acceptance

- The check runs automatically (pre-commit hook and/or CI, and the flow gate where it applies); no agent has to remember
  it.
- The check is proven to fail on a real or reconstructed violation (a test with today's evidence) before it is trusted,
  and passes on the cleaned state.
- Self-explaining code invariant in anything written: no docstrings, no comments except `# why:`.
- Target-repository work goes through `holon flow`; the intent never names harness paths or bean ids.
