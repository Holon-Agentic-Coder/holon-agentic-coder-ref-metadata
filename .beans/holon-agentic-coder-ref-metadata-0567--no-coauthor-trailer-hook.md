---
# holon-agentic-coder-ref-metadata-0567
title: "Check: commit-msg hook rejects co-author / attribution trailers"
status: completed
type: task
priority: normal
tags:
  - harness
  - git
  - invariants
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-11-26T23:09:56Z
updated_at: 2026-11-27T11:50:10Z
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

Delivered for `holon-coherence` via [PR #78](https://github.com/Holon-Agentic-Coder/holon-coherence/pull/78) and merged
into `main` (`010ffa26`):

- **Key Architectural Deliverables**: Added `.githooks/commit-msg`, `scripts/check_commit_trailers.py`,
  `.github/workflows/test-commit-trailers.yml`, and `tests/test_check_commit_trailers.py` (plus
  `tests/test_scripts_self_doc.py`).
- **Verification & Tests**: Verified trailer rejection on message files and commit ranges, executable hook behaviour,
  and CI workflow range checks.
- **Holon Flow Traversal**: Completed all 5 stages (`I-1795759572-coherence-commit-trailer-check`,
  `P-1795759593-ANA-G4N`, `E-1795776808-ANA-G4N`, Stage 4 consensus review, Stage 5 calibration), completing enforcement
  across the harness, `holon-agentic-coder`, and `holon-coherence`.
