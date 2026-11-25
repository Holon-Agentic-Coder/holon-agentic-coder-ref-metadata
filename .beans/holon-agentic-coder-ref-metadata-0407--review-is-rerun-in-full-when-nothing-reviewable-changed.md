---
# holon-agentic-coder-ref-metadata-0407
title: "The full review ensemble is re-run when nothing reviewable changed"
status: in-progress
type: feature
priority: critical
tags:
  - flow
  - stage-4
  - review
  - performance
  - holon-agentic-coder
created_at: 2026-11-24T10:55:00Z
updated_at: 2026-11-25T02:34:00Z
---

## Why

Maintainer, 2026-11-24: "it looks like the most time consuming pr review process is called over and over. is there a
churn on this process? is there something we can improve to not call review process if it's a simple mechanical merge,
pipeline failure, etc?" And earlier the same day: at the end of the review process only the pipeline pass and the
consensus pass matter; everything else is churn.

## Evidence (2026-11-24)

A full review iteration is the most expensive step of the flow: three reviewers on the whole diff, 26.6 minutes for
iteration 1 of the re-review on pull request #270.

- **#270** (ledger temp worktree cleanup): approved 3/3 at 09:07Z after four iterations. The macOS unit job then failed
  its timing ceiling on a head that had added only calibration commits (runner variance, Bean 0404). Stage 5 withdrew
  the approval. `main` was merged in (ledger rows only). The whole ensemble ran again for 26.6 minutes on a diff it had
  already approved, and one reviewer that had approved now raised a new nit, so the resolver and another iteration
  followed. No line of the change had been touched since the approval. Verified: the pull request's own diff against
  `main`, bookkeeping excluded, is byte-identical at the approved head `8605f54d` and at the re-reviewed head `4ec2e848`
  (4 files, 710 insertions, 20 deletions; same hash). The only commits between them are calibration rows, a merge of
  `main` and review ledger rows.
- **#271** (Claude token in the OS keychain): approved 3/3 at 09:03Z, approval withdrawn for the same timing failure on
  a bookkeeping-only head.
- **#269** (flow end-to-end test): eleven review iterations in under six hours; several ended "CI signal suppressed:
  pull request has merge conflicts", each time another pull request merged, and the next iteration reviewed everything
  again.

The rule that produces this is in Stage 5's merged-head gate: when the approval fingerprint still matches, the approval
is kept only if CI passes on the merged head; "when they differ, or CI fails, it withdraws the consensus and restarts
Stage 4". A pipeline failure is treated as if the review were wrong.

## Goal

The review ensemble runs on the whole diff once per version of the change, and never because of something the reviewers
cannot judge.

1. **An approval belongs to the pull request's own diff.** It is withdrawn only when that diff changes. It is not
   withdrawn by a merge of the target that leaves the diff unchanged, by bookkeeping commits, or by a pipeline result.
2. **A pipeline failure after approval goes to the pipeline, not to the reviewers.**
   - Noise (timing gate, runner or infrastructure failure, a cancelled run): rerun the job; the approval stands.
   - A real failing test: the resolver fixes it. The approval of everything else stands, and only the resolver's fix is
     reviewed (see 4).
3. **A merge of the target goes to the conflict gate, not to the reviewers.** A mechanical merge (no conflict, or ledger
   and knowledge-base files only) changes nothing reviewable. A resolved code conflict is reviewed as a delta (see 4).
4. **Scoped re-review.** When the change does move after a review (a resolver fix for findings, a fix for a failing
   test, a resolved code conflict), the next pass reviews the delta since the reviewed head together with the findings
   it answers: are they resolved, and does the delta introduce a defect? Parts of the diff that were reviewed and did
   not change are not reviewed again, so a reviewer cannot raise a new nit on code it has already passed.
5. **Consensus is the conjunction of the two gates.** The flow records "consensus on diff D" and "pipeline green on head
   H" separately and is ready when both hold for the current head; losing one does not erase the other.
6. **Churn is counted.** Each flow summary and calibration report says how many full reviews, scoped reviews and
   pipeline runs it took, and how many were caused by something other than a defect in the change.

## Notes

- Overlap: Bean 0409 covers the rejected-finding and no-change resolver cases of the same skip. This bean owns the skip
  rule.
- Builds on Bean 0372 (approval survives a merge of main with an unchanged diff; the fingerprint exists) and Bean 0376
  (conflicts resolved in the flow, with scoped re-review named in its plan). This bean extends the same idea to pipeline
  failures and to resolver fixes.
- Nits are still actioned by the resolver, applied or rejected with a reason; this bean changes what is reviewed
  afterwards, not whether a nit is handled.
- Related: Bean 0404 (timing ceiling fails on runner variance), Bean 0403 (no full CI for bookkeeping-only pushes), Bean
  0383 (Stage 4 and 5 ordering), Bean 0394 (principles).
- Risk to weigh when planning: a scoped review can miss an interaction between the delta and unchanged code. Mitigate by
  giving the scoped reviewer the whole file around the delta, and by one full review if the delta exceeds a size limit.

## Measured (self-improvement audit)

Self-improvement audit of 2026-11-24, period 2026-11-21 to 2026-11-24T11:00Z, from the 35 flow logs with timestamps in
the period (scripts and output in the git-ignored `todo/self-improvement-audit-2026-11-24/`, `review_iterations.py`).
Flows of the period whose logs were not kept (all `holon-coherence` flows, 14 `holon-agentic-coder` pull requests) are
not counted; see Bean 0412.

**Totals.** 126 full review iterations in 26 flows; 125 with a duration: median 6.7 minutes, longest 26.6 minutes (PR
#270), 934 minutes in all. After each flow's first iteration, the reason the next one ran:

| Reason the iteration ran                                                                                                                                         | Iterations | Minutes |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------: | ------: |
| Reviewer findings fixed by the resolver (a new head)                                                                                                             |         52 |     406 |
| Conflict with `main` or merge of `main` (approval re-earned, "CI signal suppressed")                                                                             |         17 |     127 |
| Resolver pass that pushed no new head, so the same head was reviewed again (18), or another stop and resume (old safety halt 2, interrupted run 2, other stop 4) |         26 |     160 |
| Approval withdrawn for a CI failure or unknown CI after approval                                                                                                 |          2 |      30 |
| Infrastructure failure (reviewer API error, stall, session limit)                                                                                                |          3 |      22 |

Of the 100 repeat iterations, only the 52 in the first row were caused by a change to the code under review; the other
48 (339 minutes) were churn by the maintainer's definition.

- 4 iterations ended with all three reviewers APPROVED (0/0/0) and still "reviewer container reported ensemble verdict
  CHANGES_REQUESTED" because the pull request was conflicting (`DIRTY`); each was followed by a merge of `main` and
  another full iteration (flows checkpoint-and-ledger-ownership twice, ci-gate-after-main-merge,
  no-fallback-calibration-report). The mergeability probe ran after the reviewers instead of before them, and the log
  does not say why the container verdict differs.
- Per flow (columns after the second count only iterations after the first):

| Flow                            | Full review iterations | Minutes in reviews | After the first: findings fixed | conflict / main merge | CI failure | infrastructure | other churn |
| :------------------------------ | ---------------------: | -----------------: | ------------------------------: | --------------------: | ---------: | -------------: | ----------: |
| admission-uses-actual-pr-files  |                      3 |                 12 |                               2 |                     0 |          0 |              0 |           0 |
| antigravity-tmpfs-empty-diff    |                      3 |                 18 |                               1 |                     1 |          0 |              0 |           0 |
| approval-survives-main-merge    |                      7 |                 46 |                               3 |                     2 |          1 |              0 |           0 |
| calibration-report-correctness  |                      3 |                 23 |                               0 |                     2 |          0 |              0 |           0 |
| checkpoint-and-ledger-ownership |                     19 |                156 |                               6 |                     1 |          0 |              1 |          10 |
| ci-gate-after-main-merge        |                      7 |                 34 |                               3 |                     2 |          0 |              1 |           0 |
| claude-code-mode-default-on     |                      1 |                  2 |                               0 |                     0 |          0 |              0 |           0 |
| claude-token-os-keychain-only   |                      2 |                 45 |                               1 |                     0 |          0 |              0 |           0 |
| derive-kb-index                 |                      1 |                 10 |                               0 |                     0 |          0 |              0 |           0 |
| document-env-variables-v3       |                      3 |                 23 |                               1 |                     1 |          0 |              0 |           0 |
| execute-stage-object            |                      2 |                 13 |                               1 |                     0 |          0 |              0 |           0 |
| executor-execution-run          |                      8 |                 74 |                               4 |                     0 |          0 |              0 |           3 |
| flow-no-auto-sidecar-spawn-v2   |                     14 |                 85 |                               3 |                     2 |          0 |              0 |           8 |
| github-issues-replace-beads     |                      2 |                 15 |                               0 |                     0 |          0 |              0 |           1 |
| intent-plan-stage-decomposition |                      3 |                  8 |                               0 |                     0 |          0 |              1 |           1 |
| layered-env-config-v2           |                     11 |                 70 |                               6 |                     3 |          0 |              0 |           1 |
| ledger-query-knowledge-index    |                      1 |                  8 |                               0 |                     0 |          0 |              0 |           0 |
| ledger-temp-worktree-cleanup    |                      6 |                 89 |                               3 |                     1 |          1 |              0 |           0 |
| name-and-seed-redaction-tests   |                      2 |                 22 |                               1 |                     0 |          0 |              0 |           0 |
| no-fallback-calibration-report  |                      4 |                 45 |                               1 |                     1 |          0 |              0 |           1 |
| remove-token-reduction-copy     |                      5 |                 24 |                               3 |                     1 |          0 |              0 |           0 |
| resolve-conflicts-in-flow       |                     12 |                 76 |                              10 |                     0 |          0 |              0 |           1 |
| resolver-honours-turn-budgets   |                      3 |                 13 |                               2 |                     0 |          0 |              0 |           0 |
| review-approved-and-fresh-tests |                      1 |                  4 |                               0 |                     0 |          0 |              0 |           0 |
| stale-calibration-warning-fix   |                      1 |                 11 |                               0 |                     0 |          0 |              0 |           0 |
| unlimited-stage-budgets         |                      2 |                  8 |                               1 |                     0 |          0 |              0 |           0 |
| total                           |                    126 |                934 |                              52 |                    17 |          2 |              3 |          26 |

- Pipeline runs per pull request in the same period (from GitHub check runs, 47 merged pull requests): 422 runs, 302 of
  them (72 percent) on heads that differed from the previous tested head only in bookkeeping files (230), by a merge of
  `main` (57) or were job re-runs (15). Median 6 runs per pull request, of which 2 on heads with a code change.
- Resolver passes without a new head and rejected findings that come back are logged separately in Bean 0409.

## Timing findings (self-improvement audit, added at the maintainer's request)

From the first self-improvement audit (2026-11-24), period 2026-11-21 to 2026-11-24T11:00Z: 35 flow logs, 140 flow runs,
47 merged pull requests. Full tables and scripts are in the git-ignored `todo/self-improvement-audit-2026-11-24/`
(`timing.md`, `pipelines.md`, `churn.md`, `review-iterations.md`).

### Every step of the flow

| Step                                          | Count | Median (min) | Longest (min) |
| :-------------------------------------------- | ----: | -----------: | ------------: |
| Intent agent turn                             |    29 |          0.1 |           0.2 |
| Planner agent turn                            |    34 |          4.0 |          34.3 |
| Stage 3 admission check                       |    49 |          0.1 |           0.2 |
| Stage 3 overlap wait (refusal, then relaunch) |    48 |          1.1 |          1053 |
| Executor turn (including tests)               |    39 |         10.5 |         102.5 |
| Pull request create or edit                   |    61 |          0.1 |           0.2 |
| Reviewer ensemble turn (3 reviewers)          |   121 |          6.6 |          26.5 |
| Local test run after reviewers                |    32 |          1.3 |           2.6 |
| Resolver turn (including push)                |    83 |          3.0 |          22.0 |
| Ledger commit                                 |   148 |          0.1 |           8.5 |
| CI registration wait                          |    26 |          0.0 |           0.3 |
| CI wait                                       |    35 |          7.9 |          18.0 |
| Calibration work and promotion                |    37 |          0.2 |           0.4 |
| Reconciliation                                |     8 |          0.2 |           0.3 |
| Final-head check                              |    36 |          0.0 |           3.8 |
| Idle after a review failure, until resume     |    28 |          1.1 |           129 |
| Waiting for the maintainer's merge            |    10 |          1.9 |          26.8 |

### Each stage, split by what the time was spent on (hours)

| Stage     | Working | Waiting on CI | Waiting on another flow | Waiting on a human | Idle |
| :-------- | ------: | ------------: | ----------------------: | -----------------: | ---: |
| Intent    |    0.07 |             0 |                       0 |                  0 |    0 |
| Plan      |    3.56 |             0 |                       0 |                  0 |    0 |
| Execute   |    9.72 |             0 |                    39.8 |                  0 |  1.6 |
| Review    |    20.9 |          0.44 |                       0 |                  0 |  9.2 |
| Calibrate |    0.16 |           5.1 |                       0 |               0.75 |    0 |

### What the timing says about churn

- **Review is the largest block of working time**: 20.9 hours, more than planning and execution together (13.3 hours).
  The reviewer ensemble ran 121 times against 39 executor turns and 34 planner turns, about three reviews per execution.
  Of the 100 repeat iterations, 48 (339 minutes) were not caused by a change to the code under review (table in the
  section above).
- **Review also carries 9.2 hours of idle time**: a review failure stops the flow, and the median 1.1 minutes until a
  resume hides a longest gap of 129 minutes. Each such stop was followed by another full iteration.
- **Calibrate is almost entirely waiting**: 0.16 hours of work against 5.1 hours waiting on CI. The CI wait (median 7.9
  minutes) runs on a head that changed only bookkeeping.
- **Pipelines**: 422 runs for the 47 merged pull requests, a median of 6 per pull request, of which 2 were on a head
  with a code change. 302 runs (72 percent) were churn: 230 on heads that differed from the last tested head only in
  bookkeeping files, 57 on heads produced by a merge of `main`, 15 job re-runs. 20 of the 33 failed heads were churn
  heads, and each failed churn head can withdraw an approval and start another full review.
- **The reviewers ran before the conflict check** in 4 iterations: all three approved, the pull request was conflicting,
  and the whole iteration was repeated after a merge of `main`.
- **Execute waits on other flows, not on itself**: 39.8 hours of overlap waiting against 9.72 hours of work (Beans 0395
  and 0410). This is not review churn but it is the largest single wait in the table.
- **Not on the critical path**: the maintainer's merge (median 1.9 minutes), calibration work (about 14 seconds), CI
  registration (near zero).

### What this means for this bean's goals

| Goal of this bean                                | Measured cost it removes                                           |
| :----------------------------------------------- | :----------------------------------------------------------------- |
| Approval belongs to the diff (goal 1)            | 17 re-reviews after a conflict or merge of `main`, 127 minutes     |
| Pipeline failure goes to the pipeline (goal 2)   | 2 re-reviews after a CI failure, 30 minutes; 20 failed churn heads |
| Merge goes to the conflict gate (goal 3)         | the 4 approved-but-conflicting iterations, and part of the 17      |
| Scoped re-review (goal 4)                        | shortens the 52 legitimate repeat iterations, 406 minutes in full  |
| Unchanged head is not reviewed again (Bean 0409) | 18 re-reviews of a head the resolver did not move                  |

### Not measured

Pre-flight, each push, each conflict probe and merge of `main`, each individual reviewer, and the overlap wait inside a
run could not be timed from the logs; 22 of the 47 merged pull requests (all of `holon-coherence`, 14 of
`holon-agentic-coder`) left no flow log and were counted from GitHub only. Bean 0412 makes the engine and the wrapper
record these.

## Audit evidence, 2026-11-24T12:58Z (self-improvement audit, fifth merge)

- PR #272 iteration 3 (12:18:50Z to 12:44:21Z): two reviewers approved, one raised a single documentation nit; the
  resolver fixed it in 3.4 minutes and the loop started a full three-reviewer iteration 4 at 12:47:53Z. On
  `claude-fable-5-2` a full iteration takes a median of 18.4 minutes (Bean 0425); a scoped check of the one-line fix
  would take a few minutes.

## Audit evidence, 2026-11-25T00:28Z (self-improvement audit, fifth merge)

- **PR #276 (`launcher-proxy-self-doc`):** `unit (macos-latest)` `CI Timing Gate (compare with main)` failures on
  bookkeeping-only ledger commits (`c1f20b9e`, `f5baea47`) triggered `FIND-CI-002` and `FIND-CI-004`, forcing two extra
  resolver passes and full ensemble re-reviews (6 iterations total).
- **PR #292 (`config-env-self-doc`):** reached 3/3 consensus approval three separate times (`20:39:44Z`, `23:05:50Z`,
  `00:11:00Z`) across 7 review iterations (30 commits: 20 bookkeeping, 4 `main`-merges) driven by `main`-merge and
  timing-gate failures (`fa8df26b`, `d0632b67`, `7eed7d7f`).
- **PR #290 (`knowledge-self-doc`):** `unit (macos-latest)` timing-gate failures on bookkeeping-only commits
  (`9b4d2bd4`, `b15549be`) triggered `FIND-CI-002` / `FIND-CI-003` and 4 review iterations.
- **PR #283 (`resolve-conflicts-in-flow`):** conflict-merge commit `221f9d73` caused consensus withdrawal on `e1e7150`
  (`PR-own change changed since approval`) after adapting a test added on `main`.

> 2026-11-25: launched `holon-agentic-coder` flow (`no-unneeded-full-review`, intent
> `todo/intent-0407-no-unneeded-full-review.json`) via `antigravity-agent` / `gemini-4-neon`.
