---
# holon-agentic-coder-ref-metadata-0569
title: "Check: flow wrapper refuses --skip-review and other forbidden flags"
status: todo
type: task
priority: high
tags:
  - harness
  - holon-flow
  - invariants
created_at: 2026-11-26T23:09:56Z
updated_at: 2026-11-26T23:09:56Z
---

## Instruction (maintainer, 2026-11-27 local)

"For the invariants that are not explicitly checked or there's no tests, create a bean so the invariants NEVER slip
through." Parent: Bean 0562.

## Invariant

Never `--skip-review` (maintainer, 2026-11-21); `--skip-preflight` and `--allow-overlap` only with explicit maintainer
permission.

## Check

- `run_holon_flow.py` refuses `--skip-review` outright and refuses the other two unless a maintainer-only authorisation
  (env var or file outside agent reach) is present; tests for each.
- `holon flow` itself logs any such flag into the execution ledger so a bypass is visible in the PR.

## Common acceptance

- The check runs automatically (pre-commit hook and/or CI, and the flow gate where it applies); no agent has to remember
  it.
- The check is proven to fail on a real or reconstructed violation (a test with today's evidence) before it is trusted,
  and passes on the cleaned state.
- Self-explaining code invariant in anything written: no docstrings, no comments except `# why:`.
- Target-repository work goes through `holon flow`; the intent never names harness paths or bean ids.
