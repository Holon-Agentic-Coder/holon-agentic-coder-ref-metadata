---
# holon-agentic-coder-ref-metadata-0567
title: "Check: commit-msg hook rejects co-author / attribution trailers"
status: in-progress
type: task
priority: normal
tags:
  - harness
  - git
  - invariants
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-11-26T23:09:56Z
updated_at: 2026-11-26T23:16:46Z
---

## Instruction (maintainer, 2026-11-27 local)

"For the invariants that are not explicitly checked or there's no tests, create a bean so the invariants NEVER slip
through." Parent: Bean 0562.

## Invariant

No attribution trailers (`Co-Authored-By:` and similar) in any commit (maintainer rule, recorded in
`.agents/workflows.md`).

## Check

- `commit-msg` hook in the harness and both target repos rejecting the trailer; the same check in CI over the PR's
  commits (catches commits made without hooks).
- The flow engine's own commits pass the check (test).

## Common acceptance

- The check runs automatically (pre-commit hook and/or CI, and the flow gate where it applies); no agent has to remember
  it.
- The check is proven to fail on a real or reconstructed violation (a test with today's evidence) before it is trusted,
  and passes on the cleaned state.
- Self-explaining code invariant in anything written: no docstrings, no comments except `# why:`.
- Target-repository work goes through `holon flow`; the intent never names harness paths or bean ids.

## Resolution

Done for the harness: `commit-msg` hook (`.agents/hooks/commit-msg`, installed into the git hooks dir) and a PR-commit
check in the hygiene workflow, both via `check_commit_trailers.py`, tested. Remaining: the same hook in
holon-agentic-coder and holon-coherence, and a test that flow-engine commits pass it (a flow job).
