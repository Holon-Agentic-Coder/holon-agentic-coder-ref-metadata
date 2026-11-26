# Self-Improvement Audit

A standing instruction from the maintainer (2026-11-24): the harness audits itself and proposes improvements, at the
start of every session and after every fifth merge.

---

## When it runs

1. **At the start of a session**, as part of the incoming agent checklist in [AGENTS.md](../AGENTS.md), before new work
   is picked up.
2. **After every fifth merge.** Count pull requests merged into `main` of `holon-agentic-coder` and `holon-coherence`
   since the last audit recorded in the audit log (below). The `post-pr-merge` skill checks the count at the end of each
   run and reports when an audit is due; the agent that receives that report launches the audit.

An audit that is due is not skipped because flows are running; it is read-only apart from the beans it writes.

## How it runs

- **In a subagent, never inline.** The main agent spawns one dedicated subagent and returns to its work.
- **The brief says what it is.** The prompt states plainly that this is a comprehensive audit carried out for the
  self-improvement of the harness and of the Holon flow, that it is not a task on any bean, and that its output is a set
  of suggestions, each logged as a bean.
- **Model tier**: the session model or one tier below it; the audit needs judgement, so not the lowest tier
  ([model-tiers.md](model-tiers.md)).
- **Read-only** on target repositories, flows, worktrees, branches and pull requests. It writes only new beans, the
  audit log, and nothing else. It never launches a flow and never edits another bean's scope.

## What it audits

The evidence is what happened since the last audit: the merged pull requests and their review threads, the flow logs and
checkpoints in `todo/`, the calibration reports, CI run times and failures, the beans opened and closed, and the bugs
logged along the way.

It looks for improvements of at least these kinds:

| Area                   | Examples                                                                                     |
| :--------------------- | :------------------------------------------------------------------------------------------- |
| Pipeline               | slow or flaky jobs, runs that test nothing new, checks that fail on noise                    |
| Flow                   | any rearrangement of the Holon flow: waits that can go, work that can start earlier, steps   |
|                        | that repeat, failures recognised late, resumes that redo finished work                       |
| Coding standards       | defects the reviewers keep finding, rules that would have prevented them, tests that add     |
|                        | cost without protection                                                                      |
| Architecture standards | modules that keep conflicting or growing, boundaries that flows keep crossing, duplicated    |
|                        | mechanisms                                                                                   |
| Harness                | instructions that were unclear or contradicted each other, skills that failed, steps a human |
|                        | had to repeat by hand                                                                        |

## The end state that matters

At the end of the review process only two things matter: **the pipeline passes** and **the consensus passes**
(maintainer, 2026-11-24: "the only important things is the pipeline pass and concensus passes. Everything else is a
churn").

- Every pipeline and flow suggestion is judged against that end state: does the step help reach a passing pipeline and a
  passing consensus sooner, or with fewer attempts? A step that does neither is churn, and the audit proposes removing
  it, moving it out of the critical path or making it free.
- Examples of churn to look for: commits and pushes that restart the pipeline without changing code, repeated pipeline
  runs on code already tested, review iterations spent on a head that later moves, postings and bookkeeping done between
  the two gates and redone when one of them fails, and waits that neither gate needs.
- The audit counts, per flow, how many pipeline runs and how many review iterations it took to reach both passes, and
  how many of them were made necessary by churn and not by a defect in the change.

## Timing for flow improvements

A flow improvement is proposed from measurements, never from impression (maintainer, 2026-11-24: "for the flow
improvements, comprehensive timing around all the steps are to be done").

- For every flow that ran since the last audit, the audit builds a timing table of **every step**, not only the five
  stages: pre-flight, each stage's agent turn, admission and overlap waits, each conflict check and merge, each push,
  each CI registration wait and CI wait, each review iteration (reviewers, resolver, ledger commit), calibration,
  reconciliation, promotion, publishing, the final-head check, and the idle time between a stop and its resume.
- Sources: the timestamps in the flow logs and checkpoints, the stage summaries, commit times on the flow branches, and
  pull request and check-run times from GitHub.
- The table gives, per step, the count, the median and the longest time, and splits each stage into working time,
  waiting on CI, waiting on another flow, waiting on a human, and idle.
- A step whose time cannot be read from the evidence is listed as **not measured**, and the audit logs a bean to make
  the engine or the wrapper record it. Missing timing is itself a finding.
- Each flow suggestion names the step it removes, shortens or moves, and the time it is expected to save according to
  the table.

## What it produces

- **One bean per suggestion**, with the evidence (pull request, log line, timing), the proposed change, the expected
  gain and the cost. Before writing a bean it searches `.beans/` and adds to an existing open bean instead of
  duplicating it.
- **A short report** to the main agent: the suggestions ranked by value, the beans created or extended, and what was
  examined but found in order.
- **An entry in the audit log**, `.beans/self-improvement-audits.md`: the date and time (UTC), the trigger (session
  start or fifth merge), the last merged pull request of each target repository at that moment, and the beans created.
  The next count of five starts from that entry.

The main agent passes the ranked suggestions to the maintainer and regenerates the triage matrix. It does not start work
on a suggestion without the usual priority order or the maintainer's word.

## Coordinator failure ledger

The audit also reads `.agents/ledger/coordinator-failures.jsonl` and flags repeats (the same category recurring, or a
rule already recorded being broken again) as high-priority beans.
