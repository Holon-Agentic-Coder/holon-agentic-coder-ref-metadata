---
# holon-agentic-coder-ref-metadata-0383
title: "Stage 5 waits for CI twice and always overruns its 10-minute budget; no per-step timing breakdown"
status: todo
type: feature
priority: high
tags:
  - flow
  - stage-5
  - ci
  - performance
  - holon-agentic-coder
created_at: 2026-11-23T12:40:00Z
updated_at: 2026-11-28T00:03:58Z
---

## Problem

On PR #260 (2026-11-23) Stage 5 took 22.5 minutes against its 10-minute budget, and the calibration work itself took 14
seconds. From the flow log (UTC):

- 12:01:29 to 12:13:26 (11 min 57 s): the merged-head CI gate waits for CI on the head that the conflict gate's merge of
  `main` and the ledger commit produced.
- 12:13:26 to 12:13:40 (14 s): calibration report, reconciliation, knowledge promotion (three commits).
- 12:14:06 to 12:24:00 (9 min 54 s): the final-head check waits for CI again, because the calibration commits moved the
  head.

So Stage 5 is two full CI runs back to back. The same overrun was logged on PR #250, #251, #253, #256 and #258 ("ran
10.6 to 10.9 min against its 10 min budget") and the flow keeps the success, so the budget has no meaning. The
maintainer noticed the gap from the PR timeline and had no way to see where the time went.

## Goal

1. **One CI wait instead of two (maintainer decision needed).** After a merge of the target, calibrate at once, push the
   merge and the calibration commits together, and wait for CI once on the final head; a failed check withdraws the
   consensus as today. This relaxes PR #250's rule that no calibration commit is pushed before CI passed on the merged
   head.
2. **No full CI for calibration-only commits.** Commits touching only `plans/`, `executions/` and `holon-knowledge/`
   cannot change a test result: path filters let the workflows finish in seconds for them (or the engine treats such
   commits as bookkeeping and reuses the previous head's result).
3. **A budget that means something.** Stage 5's budget covers its own work; time spent waiting for external CI is
   accounted separately (it already has a 1800 s CI wait budget) and does not produce an overrun warning.
4. **Timing breakdown.** Every flow summary and the PR's final comment show time per stage split into agent turns, CI
   waits, git/merge work and idle time between resumes; `holon flow --timeline <checkpoint>` prints the same from the
   checkpoint log. (A harness-side script over the checkpoint logs can provide this before the engine does.)

## Maintainer direction (2026-11-24)

For Goal 1 the maintainer prefers this shape: generate the calibration report (and the reconciliation and promotion
commits) in the background while CI runs on the merged head, keep them local, and commit and push them the moment CI
passes. PR #250's rule stays intact (no calibration commit is pushed before CI passed on the merged head); only the 14 s
of calibration work moves into the wait. If CI fails, the prepared commits are discarded and the consensus is withdrawn
as today. This does not remove the second wait (the final-head check after the calibration commits move the head); that
still needs Goal 2.

## Maintainer direction, extended (2026-11-24, later)

Maintainer's words: "for posting and calibration report add the promotion of knowledge and wisdom doesn't need to wait
either. we can commit when the pipelines is finished".

- None of the Stage 5 work waits for CI: posting, the calibration report and the promotion of knowledge and wisdom all
  run while the pipeline is still running. Only the commit (and its push) waits, and it happens once the pipeline has
  finished.
- This adds knowledge and wisdom promotion, and posting, to the work named in the direction above.
- Corrected by the maintainer (2026-11-24): "posting" here does not mean the Stage 4 consensus review. In Stage 4 the
  review is posted only after the pipeline passes (see the Stage 4 section). The agent's remaining reading, unconfirmed:
  in Stage 5 "posting" is the posting of the calibration result to the pull request.

## Maintainer direction, scope confirmed (2026-11-24, later still)

Maintainer's words: "yes, execution reconciliation, calibration branch prep, stale warning call can be done straight
away. only the commit/push needs to wait for the pipeline pass."

Work that starts at once in Stage 5, without waiting for the merged-head CI gate:

- the calibration report;
- the execution reconciliation rows (`executions.jsonl`);
- the promotion of knowledge and wisdom;
- the preparation of the `/calibrated` branch (checkout of the execution branch, creation of the branch);
- the stale-warning supersede call;
- posting of the calibration result (agent's reading, unconfirmed; the Stage 4 review post is not in this list).

Only the commit and the push wait, and they happen when the pipeline passes. If it fails, the prepared work is discarded
and the consensus is withdrawn as today.

Stage 4 was brought into scope by the maintainer afterwards; see the next section. Still unconfirmed: preparing the flow
summary before the final-head CI wait ends.

## Stage 4: work that does not wait for the pipeline (2026-11-24)

Maintainer's words: "review loop can do a lot of things before the pipelines pass as well. add your notes to phase 4 as
well". This puts Stage 4 in scope; the notes below are the agent's, from reading `flow/review/loop.py`,
`flow/review/posting.py`, `flow/review/ledger_commit.py` and `flow/github/ci_wait.py` on `main`.

Today, when every reviewer approves cleanly, the iteration does this in order: wait for CI registration, wait for
pending checks (budget 1800 s), decide the verdict, then build finding ids and trailers, write the ledger rows, build
the consensus data and the approval fingerprint, post the review, check calibration freshness, write the summary row,
and commit and push the ledger rows at stage exit. Everything after the two waits is held up by them although little of
it depends on CI. An iteration where a reviewer objects already probes CI once and does not wait, and the resolver does
not wait either; those paths need no change.

Work to start as soon as the reviewers return, while CI is still running:

- **Reviewer rows**: the per-reviewer ledger rows, reviewer finding ids, severity and the adjudication of rejected nits
  depend only on the reviewer results.
- **Approval fingerprint and consensus data**: the PR-own fingerprint, the reviewer summaries, dispositions and the
  review title and body depend on the diff and the reviewers; only the CI line and the final verdict are filled in when
  CI settles.
- **Conflict gate before the wait**: mergeability against the target is checked, and the target merged when needed,
  before waiting for CI rather than at posting time. Today a conflict found at posting sends the approval back to be
  re-earned on the merged head, which costs a second full CI wait. (Inferred from the `conflict_gate` branch after
  `post_review_consensus`; confirm when planning.)
- **Calibration freshness check** and the **summary row** of the loop.
- **Stage 5 fail-early checks** (replaces "prepare Stage 5 during the Stage 4 wait"; maintainer, 2026-11-24: "yes that
  sounds correct. do it"): see "Stage 5 pre-flight during Stage 4" below.

What waits for the pipeline to pass:

- the final verdict and the outcome field of the iteration row (`success` or `failure`), and a `FIND-CI` finding when a
  check failed;
- **posting**: the consensus review is posted to the pull request only after the pipeline passes (maintainer,
  2026-11-24: "for phase 4 only the posting and commit/push is done after the pipeline passes"). The review body is
  prepared during the wait and posted on the pass;
- nothing else. Commits do not wait (maintainer, 2026-11-24: "bring stage 4 inline"). The review ledger rows are
  committed at once but never pushed by themselves: a lone bookkeeping push would restart the pipeline the approval is
  waiting on. They go out with the next push that happens anyway, the resolver's or Stage 5's single push (agent's
  refinement under the maintainer's "use your free will", 2026-11-24; see Bean 0394, recommendation 6).

If CI fails, the prepared rows are kept as the record of the iteration with outcome `failure`, the Stage 5 preparation
is discarded, and the loop continues to the resolver as today.

## Posting rule: failures early, successes after the push (2026-11-24)

Maintainer's words: "we you usual tell if it's stale even before the pipelines passes right? the only posting that can
be done after the push is the success (pr concensus approve, calibration done) posting. The failures can fail early".

This rule replaces the per-item posting notes above, for Stage 4 and Stage 5 alike:

- **Success postings wait**: the consensus approval review and the "calibration done" result are posted only after the
  pipeline has passed and the commits are pushed. The same holds for editing the stale-calibration warning to
  "superseded", because it states that a fresh report covers the head (agent's classification).
- **Failure postings go out as soon as the failure is known**, without waiting for the pipeline: a stale calibration
  report (staleness is known from the evaluated commit and the head, before CI finishes), a terminal review that is not
  an approval, a withdrawn consensus, a conflict that cannot be resolved, a failed check (as soon as the first check
  fails, without waiting for the rest).
- Unchanged: intermediate review iterations are still not posted (Bean 0260); "failure posting" means the postings the
  flow already makes, made earlier.

Agent's notes for planning, not yet confirmed by the maintainer:

- Reconciliation and promotion also write a local index database that is not in git
  (`holon-knowledge/.index/action_index.db`), so on a CI failure the prepared rows are kept uncommitted for the next run
  (the engine already commits rows a failed calibration left behind) rather than discarded.
- The time is in the number of CI runs, not in the prepared work (14 s on PR #260): the conflict gate before the Stage 4
  wait, one push for ledger rows and Stage 5 commits, and Goal 2 are what save minutes and should be planned first.

## Stage 5 pre-flight during Stage 4 (maintainer-confirmed, 2026-11-24)

Calibration can only be done on an approved head, so Stage 5 is not prepared during Stage 4. Instead Stage 4 runs these
as fail-early checks, so a Stage 5 failure surfaces while reviewers or CI are still running:

- **Trial calibration, no commit**: generate the calibration report for the reviewed head and run its self-check,
  without creating `/calibrated`, writing the report, appending the ledger row or committing. `run_calibrate` already
  generates and self-checks before any branch checkout or file write, so the trial does not disturb the worktree Stage 4
  is using. The part of the self-check that needs the approved head cannot run yet. A trial that fails is a failure and
  is reported early (see the posting rule).
- **Tooling pre-flight**: at the start of Stage 4, confirm the Prettier check can run (Stage 5 fails closed when it
  cannot) and that the pull request number resolves.
- **Fetch and conflict gate**: fetch origin and merge the target before the CI wait (already listed above).

Still done only once the approved head exists: creating `/calibrated` at the approved commit, the real report, the
ledger row, reconciliation and promotion. The real report is regenerated on the approved head and the trial is never
reused, because Stage 4's ledger-row commit moves the head after the trial ran.

## Conflict gate: resolve on discovery (maintainer, 2026-11-24)

Maintainer's words: "conflict gate: as soon as you find a conflict resolve it straight away".

- A conflict with the target is resolved the moment it is found, in whichever stage finds it, and never deferred to
  posting time or to the next stage. Nothing waits for the pipeline first: the merge produces the head CI has to run on,
  so resolving at once is also what keeps it to one CI wait.
- This settles the open point in the Stage 4 section ("Conflict gate before the wait"): whether or not a conflict found
  at posting costs a second CI wait today, the gate runs on discovery.
- Agent's notes: the check should run at the start of each review iteration and again when reviewers return, so a target
  that moved during the review is merged before the CI wait begins. Resolution itself (ledgers mechanically, other files
  through the conflict-resolver role, scoped re-review when the PR's own diff changed) is Bean 0376's work; this bean
  only fixes when the gate runs. An unresolvable conflict is a failure and is posted early (see the posting rule).

## Hard rule for the calibration report (maintainer, 2026-11-24)

Maintainer's words: "calibration report, only success report can be posted after pipeline passes. that is the hard rule.
everything else can be done before that".

- **Hard rule**: the success posting of the calibration report (the "calibration done" result on the pull request) is
  made only after the pipeline has passed. No other Stage 5 step is bound to the pipeline by this rule: generating the
  report, its self-check and Prettier check, the ledger row, reconciliation, promotion, branch preparation and every
  failure posting run before it.
- This closes the open point on whether the report reads anything from the CI run: the report is generated before the
  pipeline finishes, so it must not depend on that run's result; the success posting carries the CI outcome.
- **Open, asked of the maintainer**: whether the commit and push of the calibration commits also stop waiting. The
  earlier direction in this bean says "only the commit/push needs to wait for the pipeline pass"; read literally, the
  hard rule leaves only the success posting waiting. Pushing the calibration commits together with the merge of the
  target, and waiting for CI once on that final head, is Goal 1 as first written and removes the second CI run, but it
  relaxes PR #250's rule that no calibration commit is pushed before CI passed on the merged head. Until answered, the
  commit and push keep waiting.

## Hard rule: fail early (maintainer, 2026-11-24)

Maintainer's words, on "Reconciliation and promotion on a CI failure": "failures should be recognised as soon as
possible and actions should be taken as soon as possible. this is a hard rule. fail early".

- **Hard rule, every stage**: a failure is recognised at the earliest moment it can be known, and the action it calls
  for starts at once. Nothing waits for the rest of a pipeline, the end of a stage or a budget to run out once the
  outcome is already a failure.
- Applied to a CI failure while Stage 5 work is prepared: the first failed check is the failure. The flow stops waiting
  for the remaining checks, posts the failure, withdraws the consensus and hands the failure to the resolver (Stage 4
  restarts) immediately. The prepared report is abandoned at that moment, not at the end of the wait.
- Applied elsewhere in this bean: a failed trial calibration or tooling pre-flight, a stale report, an unresolvable
  conflict and a non-approving terminal review are each acted on when found (see the posting rule and the conflict
  gate).
- Agent's note on the prepared reconciliation and promotion rows, still to confirm at planning: the action on failure is
  immediate either way; what remains a design choice is whether the rows already written (ledger file and the local
  index database outside git) are rolled back or left uncommitted for the next run, which the engine already picks up.
  Leaving them is the smaller change; they do not depend on the CI result.

## Only the success posting waits (maintainer, 2026-11-24)

Maintainer's words: "you don't need superseded post to wait for the pipeline to pass. you can detect this early. yes
only sucess posting is waiting for the pipeline to pass. every failure is existed or posted early."

- The "superseded" edit of the stale-calibration warning does not wait for the pipeline; it is made as soon as a fresh
  report covers the head. This overrides the agent's classification of it as a success posting in the posting rule.
- The only things that wait for the pipeline to pass are the two success postings: the consensus approval and the
  "calibration done" result. Every failure exits or is posted early.
- Agent's reading of "only success posting is waiting", applied to the question left open under the hard rule for the
  calibration report: the commit and push of the calibration commits no longer wait either. They go out with the merge
  of the target and CI is waited for once on the final head (Goal 1 as first written), which relaxes PR #250's rule that
  no calibration commit is pushed before CI passed on the merged head. Reported to the maintainer as the reading taken;
  reverse it here if that was not meant.

### Reconciliation and promotion after a failure (agent's recommendation, asked by the maintainer; not yet confirmed)

- **Reconciliation rows: neither roll back nor hold back; keep them.** The ledgers are append-only, so a written row is
  never removed. The row records the execution's own verdict (from the Stage 3 result), which a later CI failure on a
  merged head does not make false, and Stage 5 already treats a second run as "already recorded". If a later outcome
  changes the verdict, a correcting row is appended. The local index database is derived from the ledger and needs no
  rollback of its own.
- **Promotion: roll back.** Promoted knowledge and wisdom files are derived, cheap to regenerate and the one output that
  does harm if it lingers: a lesson promoted on the strength of a run that then failed would steer later plans. On a
  failure the new files are deleted at once (fail early) and promotion runs again on the head that finally passes.

## One push, one pipeline (maintainer-confirmed, 2026-11-24)

Maintainer's words: "when you merge main into the pull request, can't you push the report, reconcilation, promotion at
the same time then you only have one ci pipeline running for the whole thing".

- Confirmed: Stage 5 merges the target locally, generates the report on the merged head, writes the reconciliation rows
  and the promotion, and pushes all of it in one push. One pipeline runs on that final head; only the "calibration done"
  posting waits for it. This is Goal 1 as first written and replaces PR #250's rule that no calibration commit is pushed
  before CI passed on the merged head. The agent's reading in the previous section is no longer a reading.
- When no merge of the target is needed, Stage 4's pipeline has already passed on the approved head, and the calibration
  push still starts one more pipeline on commits that only touch bookkeeping files. Goal 2 (no full CI for such commits)
  removes that one.
- Consequence for a failure after the push (agent's note, to confirm): the calibration commits are already on the
  branch. Reconciliation rows stay (append-only). Promotion is rolled back with a revert commit, not by deleting
  uncommitted files, and the report is regenerated on the head that finally passes.

## Stage 4 in line; report regenerated on the passing commit (maintainer-confirmed, 2026-11-24)

Maintainer's words: "bring stage 4 inline. regenerate the report on the commit that finally passes."

- Stage 4 follows the same rule as Stage 5: only its success posting (the consensus approval) waits for the pipeline.
  Its commits and pushes are not held back. The Stage 4 section above is corrected accordingly.
- After a failure that follows the calibration push, the calibration report is regenerated on the commit that finally
  passes. This confirms that part of the agent's note under "One push, one pipeline". Keeping the reconciliation rows
  and undoing the promotion with a revert commit remain the agent's recommendation, not yet confirmed.

## After a failure that follows the push (maintainer-confirmed, 2026-11-24)

Maintainer's words: "keep the reconciliation row and undo the promotion with a revert commit".

- **Reconciliation rows are kept.** The ledger is append-only; nothing is removed or rewritten.
- **Promotion is undone with a revert commit** on the pull request branch, made as soon as the failure is known (fail
  early). No history is rewritten and nothing is force-pushed.
- **The report is regenerated** on the commit that finally passes (confirmed earlier), and promotion runs again there.

This settles the agent's recommendation under "Only the success posting waits" and the note under "One push, one
pipeline"; the earlier wording about deleting uncommitted promotion files no longer applies.

## Split (2026-11-24)

Goal 2 (no full CI for bookkeeping-only commits) is now Bean 0403 so it can run by itself; it changes workflow files,
not the flow engine. The other recommendations for the whole flow are listed in Bean 0394.

## Notes

- Overlap: Bean 0412 records timing for every step, including the Stage 5 breakdown in Goal 4. This bean owns the double
  CI wait and the budget; Bean 0412 owns the timing breakdown.
- **Audit evidence (`2026-11-27T10:55Z`):** Coherence `#72` (`coherence-abtest-leaks-deps`) ran Stage 5 `27.0 min`
  (`1619.1 s` vs `10 min` budget) and `#73` (`coherence-ca-logging-and-image`) ran Stage 5 `17.6 min` (`1056.1 s` vs
  `10 min` budget), both logging `WARNING: Stage 'calibrate' ran ... against its 10 min budget` solely from merged-head
  and final-head CI waits after `2` target-merge carry-overs (`#74` incurred `8` CI heads / `56` CI runs across `2`
  target-merge carry-overs).
- **Audit evidence (`2026-11-27T15:46Z`, `8` merged PRs `#415,#424–#426` and `#83,#67,#84,#85`):** All `5/8`
  target-syncing PRs waited **twice** for CI in Stage 5 — first `164–740 s` (`median 438 s` / `7.30 min`) on
  `stage 5 carry-over` after `sync: merge target`, then `100–330 s` (`median 178.5 s` across all 8 PRs) on
  `chore(calibration)` — even though calibration work itself took only `16–29 s` (`median 20.0 s`). Stage 5 overran its
  10-minute budget on `HAC #425` (`14.9 min`, `886 s`), `HAC #426` (`11.7 min`, `692 s`), and `COH #85` (`13.7 min`,
  `822 s`; `COH #84` `8.8 min`, `COH #67` `7.5 min`).
- **Audit evidence (`2026-11-28T00:01Z`, `31` merged PRs `#428..#456` and `#86..#94`):** With `0` target merges during
  `15:55Z–23:38Z`, Stage 5 calibration work took `19–36 s` (`median 27.0 s`), yet final-head CI wait on
  `chore(calibration)` took **`median 303.0 s` (`5.05 min`)**, **`max 933.0 s` (`15.55 min`, `COH #88`)** (Stage 5 total
  `median 5.87 min`, `max 16.73 min`). Even on `HAC #456`, where `ci_bookkeeping_gate` skipped all test jobs on
  `94835ba84`, Stage 5 still waited `14 s` registration + `148 s` (`162 s` / `2.7 min` total) for GitHub to spin up and
  skip 16 workflow jobs.
