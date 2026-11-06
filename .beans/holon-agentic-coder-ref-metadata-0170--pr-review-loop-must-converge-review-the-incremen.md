---
# holon-agentic-coder-ref-metadata-0170
title: "pr-review-loop must converge: review the increment, defer Nits on unchanged code, bound mutation work"
status: completed
type: task
priority: high
tags:
  - review-loop
  - skills
  - token-cost
created_at: 2026-10-27T12:10:02Z
updated_at: 2026-10-29T12:30:00Z
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

- 2026-10-30: implemented on harness branch `feat/0182-0170-event-watcher-and-loop-convergence` (`f14c2f0`, no PR yet),
  which also adds this bean's summary of changes and closes it on that branch. Here it stays `todo` until that branch
  lands; the status change is the maintainer's step.
- Related: Bean 0160 (CI polling wasted iterations) and Bean 0144 (a sandboxed review loop with real reviewers should
  adopt the same convergence rules).
- Harness change only. Note that the harness is being deprecated (Bean 0156): carry the rules into whatever review loop
  replaces it in the target repositories.

## Summary of Changes (2026-10-29)

Harness skill change, edited directly. `pr_review_loop/SKILL.md` gains principle 12, "Convergence Rules (Bean 0170)",
wired into the ensemble prompt, the resolver prompt, Phase D and the final summary; `pr_reviewer/SKILL.md` gains Step 2a
(Full vs Increment-Scoped Mode).

1. **Increment-scoped review**: the first complete ensemble reviews the whole PR and sets `voted_head` in `_state.json`;
   later dry runs and ensembles review `git diff <voted_head>..HEAD` and still report Critical and Important defects
   anywhere. A new Nit on code the increment did not change does not block approval.
2. **Bounded mutation work**: one sweep per area, recorded in `mutation_sweeps` (area, iteration, head, mutants,
   survivors); later rounds mutate only the increment; a survivor in unchanged, swept code is deferred.
3. **Scope freeze**: resolvers fix only the findings handed to them; the orchestrator adds no scope without the
   maintainer.
4. **Single source for behaviour docs**: one authoritative section, other copies become references.
5. **Convergence report**: `convergence.original` and `convergence.ensembles` (diff size and Nit count per ensemble).
   When both rise at three ensembles running, the loop writes `<repo>_pr<N>_convergence_report.md` with the three
   options (increment-only review, split the PR, merge with deferrals), posts nothing to GitHub, reports to the
   maintainer and stops. Principle 3 lists this as the third terminal exit; it is a report, not a pause.
6. **Integrity rules kept**: Nit policy inside the increment, unanimous votes at one head, any push voids votes, no
   fabricated approvals.

## Decision: "Defer" Is a Recorded Disposition, Not a Wave-Through

The maintainer ruling that every Nit (surviving mutants included) is applied or rejected with a reason still holds. A
deferred Nit or mutant still goes to the resolver, which dispositions it `rejected` with reason
`deferred: unchanged code -> <bean id>`, appends it to `deferred_findings` in `<repo>_pr<N>_coordination.json` and to
`residual_risks`, and lists it in one follow-up bean per loop (`deferral_bean` in `_state.json`, created on the first
deferral). Recording a deferral touches only the harness ledger and bean, so it does not move the PR head or void votes.

## Not Done Here

- Bean 0144's sandboxed review loop and the replacement for the deprecated harness loop (Bean 0156) still need to carry
  these rules; that happens through the Holon flow in the target repositories.
