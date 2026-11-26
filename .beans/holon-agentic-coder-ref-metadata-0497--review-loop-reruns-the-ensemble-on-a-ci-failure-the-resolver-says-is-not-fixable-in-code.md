---
# holon-agentic-coder-ref-metadata-0497
title: "Review loop re-runs the full ensemble 9 times on a CI failure the resolver reported as not fixable in code"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-4
  - review
  - resolver
  - churn
created_at: 2026-11-26T08:55:00Z
updated_at: 2026-11-26T08:55:00Z
---

## Evidence

Self-improvement audit 2026-11-26 (fifth merge). Flow `module-line-budget-all-packages` (PR #317,
`todo/flow-module-line-budget-all-packages.log`): iterations 1 to 9 (05:16:53Z to 06:22:10Z, 65 min of a 112 min review
loop, 12 iterations in all) each ran 3 reviewers (about 3.7 min), a resolver turn, a ledger commit and a push. From
iteration 1 the resolver's own finding evidence said the same thing every time: the hygiene job fails only because the
frozen budget file differs from the merge base and the PR lacks the maintainer label; "no code fix exists". Its finding
`recommendation` stayed the boilerplate "Run linters and tests locally, apply fixes, and commit the changes", and
disposition stayed `open`. Every ledger-row push restarted the pipeline (PR #317: 100 workflow runs, 14 failures, 16
cancelled, 70 successes). Iteration 9 also found a second, fixable cause (branch behind main, missing the #319 scripts)
that no earlier iteration acted on. The end state (pipeline passes, consensus passes) was reached only once an
authorisation was supplied at iteration 10.

Related: 0485/0486 (the cause), 0409 (resolver pass that changed nothing), 0407 (scoped re-review). This bean is the
loop-level guard none of them states: they remove one cause; the loop would repeat for the next unfixable cause.

## Proposed change

- The resolver result carries a `blocked_on` field (`authorisation`, `external`, `behind-main`, `none`) in place of the
  generic recommendation.
- When the previous iteration's resolver pushed no code change and the failing check set and evidence are unchanged, the
  loop does not start the ensemble. It waits on the cheap condition (label present, env set, main merged) at a fixed
  poll, with a cap of 2 repeats, then reports the stuck cause in the flow log.
- `behind-main` is handled by the engine (merge origin/main, push once) before the next review, not left to a reviewer
  note.

## Expected gain and cost

About 8 iterations x 10.8 min (audit of 2026-11-26 blocked-iteration cost) = about 85 min and 8 pipeline restarts on
that flow, plus roughly 24 reviewer-agent turns. Cost: one result field, one loop guard, tests; no change to approval
semantics.
