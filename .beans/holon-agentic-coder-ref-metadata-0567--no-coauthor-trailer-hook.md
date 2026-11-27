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
updated_at: 2026-11-27T01:06:58Z
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
check in the hygiene workflow, both via `check_commit_trailers.py`, tested. Delivered for holon-agentic-coder by PR #371
(merged at `e189a89`): `.githooks/commit-msg`, `.github/workflows/test-commit-trailers.yml`, and tests
`test_check_commit_trailers.py` plus `test_flow_commit_messages_have_no_attribution.py` (the flow-engine commit check).
Remaining: the same hook and workflow in holon-coherence.
