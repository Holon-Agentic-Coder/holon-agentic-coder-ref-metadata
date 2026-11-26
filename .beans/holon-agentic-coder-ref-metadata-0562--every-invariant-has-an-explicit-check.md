---
# holon-agentic-coder-ref-metadata-0562
title: "Every invariant has an explicit, automatic check (umbrella)"
status: todo
type: task
priority: critical
tags:
  - harness
  - invariants
  - tests
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-11-26T23:09:56Z
updated_at: 2026-11-26T23:09:56Z
---

## Instruction (maintainer, 2026-11-27 local)

"For the invariants that are not explicitly checked or there's no tests, create a bean so the invariants NEVER slip
through." Parent: Bean 0562.

## Goal

No invariant relies on an agent reading and obeying a rule. Each one has a check that fails closed.

## Children

| Invariant                                                                     | Bean                    |
| :---------------------------------------------------------------------------- | :---------------------- |
| Self-explaining code (gate fails closed)                                      | 0558 (and gate PR #357) |
| Timestamps read from the clock, UTC                                           | 0561                    |
| Exactly three append-only ledgers                                             | 0563                    |
| Target never references harness paths or bean ids                             | 0564                    |
| Intent scope lists files, never directories/globs                             | 0565                    |
| Git safety: no stash, --no-verify, add -A, force-push/rebase of flow branches | 0566                    |
| No co-author trailers                                                         | 0567                    |
| Main worktrees untouched                                                      | 0568                    |
| Never --skip-review (and other forbidden flags)                               | 0569                    |
| Budget changes only with maintainer authorisation                             | 0570                    |
| Bean files: sequential ids, valid status, frontmatter                         | 0571                    |
| Every review finding (incl. Nits, mutants) applied or rejected with reason    | 0572                    |
| Invariant registry: every hard rule maps to its check                         | 0573                    |

## Acceptance

- Every child completed; the registry test (0573) passes with no hard rule unmapped.

## Common acceptance

- The check runs automatically (pre-commit hook and/or CI, and the flow gate where it applies); no agent has to remember
  it.
- The check is proven to fail on a real or reconstructed violation (a test with today's evidence) before it is trusted,
  and passes on the cleaned state.
- Self-explaining code invariant in anything written: no docstrings, no comments except `# why:`.
- Target-repository work goes through `holon flow`; the intent never names harness paths or bean ids.
