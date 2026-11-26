---
# holon-agentic-coder-ref-metadata-0413
title: "Coding rules from what the reviewers keep finding, given to the planner and executor up front"
status: todo
type: task
priority: normal
tags:
  - coding-standards
  - review
  - flow
  - holon-agentic-coder
created_at: 2026-11-24T11:00:00Z
updated_at: 2026-11-24T13:00:00Z
---

## Why

Every finding a reviewer raises costs a resolver pass and a full re-review. Findings that recur across flows point at
rules the planner and executor could follow from the start.

## Evidence

Logged by the self-improvement audit of 2026-11-24 (first audit, period 2026-11-21 to 2026-11-24T11:00Z). The scripts
and their output are in the git-ignored audit folder `todo/self-improvement-audit-2026-11-24/`.

249 distinct findings in the resolver results of the period's flow logs (126 important, 121 nits, 2 critical; 216
applied, 26 rejected, 7 open). Recurring kinds:

| Kind                                                     | Findings | Example                                                                                                  |
| :------------------------------------------------------- | -------: | :------------------------------------------------------------------------------------------------------- |
| A file already over 1,000 lines grows                    |       25 | "executor.py, already over 1,000 lines, grows from 1580 to 1852 lines"                                   |
| Documentation out of step with the code                  |       20 | README key tables and module maps listing removed or missing items                                       |
| The pull request does not state what the intent asks for |       18 | "the PR description omits the confirmed cause" (one flow)                                                |
| A failing check found during the review                  |       17 | "CI checks failed in iteration N: local_tests"                                                           |
| A deny-list misses another repository-controlled key     |       12 | "PROJECT_REFUSED_KEYS omits HOLON_COHERENCE_IMAGE" (PR #251, found one key at a time over 11 iterations) |
| Helper copied instead of reused                          |       12 | "_MARKER_PREFIXES and _has_markers duplicate flow/target_sync_merge.py verbatim"                         |
| New tests added to an oversized test module              |       13 | "Grows test_review_loop.py from 2679 to 2723 lines"                                                      |
| Lint errors                                              |       10 | ruff E501, F401, I001, E402, RUF022                                                                      |

## Proposed change

Add these rules to the target repository's own agent guidance that the planner and executor prompts include
(target-native wording only, no harness paths):

1. Never grow a file over 1,000 lines; put new code and new tests in a new focused module.
2. Inputs a repository controls are checked against an allow-list, never a deny-list.
3. Reuse an existing helper; never copy one.
4. Documentation that lists code items (keys, modules, commands) is generated or drift-tested, never hand-maintained.
5. When the intent asks for a stated outcome (a cause, a seed, a measurement), the pull request description states it.
6. Run lint and the tests of the touched area before ending the turn (made mechanical by Bean 0408).

## Expected gain

The recurring kinds above are about 120 of 249 findings; each avoided finding saves a resolver pass and part of a
re-review (median iteration 6.7 minutes).

## Cost

Small: one guidance document and prompt includes in the target repository, delivered by a flow.

## Notes

- Related: Bean 0408 (local gate), Bean 0409 (rejected findings), Bean 0410 (generated docs), Bean 0380 (module
  budgets).
