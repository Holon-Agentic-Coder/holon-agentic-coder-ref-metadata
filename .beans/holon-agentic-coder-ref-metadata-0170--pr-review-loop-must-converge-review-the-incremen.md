---
# holon-agentic-coder-ref-metadata-0170
title: "pr-review-loop must converge: review the increment, defer Nits on unchanged code, bound mutation work"
status: todo
type: task
priority: high
tags:
  - review-loop
  - skills
  - token-cost
created_at: 2026-10-27T12:10:02Z
updated_at: 2026-10-27T12:10:02Z
---

## Problem

The harness `pr-review-loop` run on holon-agentic-coder PR #97 (Bean 0159) did not converge in 33 iterations. The
maintainer raised the cap from 25 to 35, then merged at iteration 33 with Nits still open (Bean 0169). The loop records
are in `.subagent/holon-agentic-coder_pr97_{state.json,coordination.json,loop_history.md}`.

What the data shows:

- **The PR tripled under review.** The original execution was 16 files, +1192/-204. By the merge it was 33 files,
  +4015/-423 (excluding ledgers and plans), across 56 commits. The resolvers added about 2,800 lines, mostly tests and
  docs.
- **Real defects were rare.** There were no Critical findings after iteration 2, and only two Important ones (iterations
  6 and 31).
- **Nit counts never trended to zero.** Ensemble totals ran 4, 2, 2, 4, 4, 2, 16, 30, 26, 10 and 7. The spikes came from
  reviewers running fresh mutation batches over code the previous rounds had added.

Why it did not converge:

1. Every resolver adds new tests, docs and behaviour, and every reviewer re-reads the whole PR with fresh eyes. The
   review surface grew faster than findings were closed.
2. The approval bar requires three independent fresh reviewers each to find zero Nits on the same head, any push resets
   the votes, and every Nit must be dispositioned. On a 4,000-line diff that is very unlikely. The "same Nit three
   iterations running" brake never fires, because each round's Nits are new.
3. Mutation testing has no natural end. Each round, reviewers invent new mutants for code the earlier sweeps did not
   cover.
4. Docs restating behaviour in many places turn one change into drift across 3-5 files. The exit-code paragraph was
   reworked in iterations 26-28.
5. The rung-5 escape hatch ("re-scope oversized findings into a new bean") was under-used. The orchestrator also widened
   the scope mid-loop: a CI runtime fix, a main sync and full sweeps.

## Scope

Change `.agents/skills/pr_review_loop/SKILL.md` and `.agents/skills/pr_reviewer/SKILL.md` (harness files, editable
directly) so the loop converges:

1. **Increment-scoped review after the first full ensemble.** Later ensembles review the diff since the last voted head,
   plus any Critical or Important defect anywhere. New Nits in code the increment did not change are deferred to a
   follow-up bean (rung 5) instead of blocking approval. Record each deferral in the coordination ledger.
2. **Bounded mutation work.** Allow one systematic mutation sweep per area, recorded in a table. Later rounds mutate
   only the increment. A surviving mutant in unchanged, already-swept code is deferred, not blocking.
3. **Scope freeze.** Resolvers fix only the findings handed to them, and must not add unrelated tests or docs. The
   orchestrator must not add scope mid-loop without the maintainer's say-so.
4. **Single source for behaviour docs.** When a resolver finds the same behaviour described in several docs, it makes
   one authoritative section and turns the others into references to it.
5. **Convergence report.** The state file tracks the diff size against the original execution and the Nit count per
   ensemble. When both trend upward for three ensembles running, the orchestrator reports it to the maintainer with the
   options: increment-only review, split the PR, or merge with deferrals. It must not just keep iterating.
6. Keep the existing integrity rules: the Nit policy within the increment, unanimous votes at one head, no fabricated
   approvals.

## Notes

- Related: Bean 0160 (CI polling wasted iterations) and Bean 0144 (a sandboxed review loop with real reviewers should
  adopt the same convergence rules).
- Harness change only. Note that the harness is being deprecated (Bean 0156): carry the rules into whatever review loop
  replaces it in the target repositories.
