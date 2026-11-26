---
# holon-agentic-coder-ref-metadata-0394
title: "No unnecessary waiting anywhere in the holon flow: recommendations"
status: todo
type: epic
priority: high
tags:
  - flow
  - performance
  - ci
  - holon-agentic-coder
created_at: 2026-11-24T08:25:00Z
updated_at: 2026-11-24T13:00:00Z
---

## Why

Maintainer, 2026-11-24: "you use you free will to make the whole process as frictionless as possible and there is no
unncessary waiting anywhere in the whole holon flow. put your recommendations!"

These are the agent's recommendations, ranked by time saved. Each is marked **measured** (from the flow logs or the
engine on `main`), **seen** (observed once, 2026-11-24) or **unverified** (to check when planned). Stage 4 and Stage 5
rules the maintainer already confirmed live in Bean 0383 and are not repeated.

## Principles (maintainer's hard rules)

1. Only success postings wait for the pipeline. Everything else runs as soon as its inputs exist.
2. Fail early: a failure is recognised and acted on the moment it can be known.
3. Resolve a conflict the moment it is found.
4. At the end of the review process only two things matter: the pipeline passes and the consensus passes. Everything
   else is churn (maintainer, 2026-11-24). A step is kept on the critical path only if it helps reach those two.

## Where the time goes (measured, all flow logs to 2026-11-24)

| Stage     | Median  | Longest   | What it is made of                             |
| :-------- | :------ | :-------- | :--------------------------------------------- |
| Intent    | 0.2 min | 0.3 min   | agent turn                                     |
| Plan      | 4.0 min | 25.3 min  | agent turn                                     |
| Execute   | 9.2 min | 141.8 min | agent turn and tests                           |
| Review    | 6.7 min | 69.7 min  | reviewers, resolver, then a CI wait            |
| Calibrate | 8.5 min | 12.6 min  | about 14 s of work; the rest is waiting for CI |
| CI wait   | 7.9 min | 11.9 min  | one pipeline run, 33 waits measured            |

Outside the stages: three flows waited about 3.5 hours at Stage 3 admission for a pull request that was approved and
only needed the maintainer's merge (**seen**), and a session restart stopped four flows until someone noticed
(**seen**).

## Recommendations

### A. Waits measured in hours

1. **Do not idle at Stage 3 admission; work during the overlap wait.** Today a plan whose touch set overlaps an open
   pull request does nothing until that pull request merges. On 2026-11-24 the overlap was partly on `README.md` alone.
   Apply the same rule as Stage 5: execute now on the current base, hold only the push, and when the blocking pull
   request merges, sync with the target and resolve on discovery (Bean 0376 supplies the resolver). Start with low-risk
   overlaps (documentation, registries, generated lists); keep strict waiting for overlaps on core engine files, where
   the maintainer earlier found sequential runs cheaper. **Measured** wait, **unverified** design.
2. **Flows survive the session that started them.** The wrapper runs as a child of the agent session, so a restart kills
   every flow and leaves role containers behind (Bean 0390). Run the wrapper under a supervisor that is independent of
   the session, with one lock per checkpoint, so a restart changes nothing. **Seen.**
3. **A resume adopts finished work.** A killed Stage 3 whose execution branch is complete and pushed is executed again
   from scratch (three wasted executions on Bean 0387). Resume should adopt it, as Bean 0360 did for plan branches.
   **Seen.**
4. **Stacked starts for dependent work (larger, optional).** A flow blocked only by an approved, calibrated pull request
   could branch from that pull request's head instead of waiting for the merge. **Unverified**; needs a maintainer
   decision because it changes what a flow's base is.

### B. Waits measured in minutes, every flow

5. **No full pipeline for bookkeeping-only commits** (Bean 0383, Goal 2). Commits touching only `plans/`, `executions/`
   and `holon-knowledge/` cannot change a test result. Saves one pipeline, about 8 minutes, in every flow. **Measured.**
6. **One push per step, never a push of bookkeeping by itself.** Stage 4 commits its ledger rows at once but pushes them
   with the next push that happens anyway (the resolver's, or Stage 5's single push). A lone ledger push restarts the
   pipeline the approval is waiting on. **Measured** from the engine's order of work.
7. **React to pipeline events instead of polling.** The CI wait backs off to one poll every 120 s, so each wait can idle
   up to 2 minutes after the pipeline has finished; the logs show check results arriving in 2-minute steps. Use the
   event stream (Bean 0352) or cap the poll at 15 s. The same applies to the 60 s overlap poll and the 15 s registration
   poll. **Measured.**
8. **Cancel superseded pipelines and fail fast inside the pipeline.** A push that replaces a head should cancel the run
   on the old head, and a failed job should stop its siblings, so the engine learns of a failure in the first failing
   job's time. **Unverified** whether the workflows already do this.
9. **Shorten the pipeline itself.** Median 7.9 minutes; the last checks to finish are `Workspace survival` and
   `unit (macos-latest)`. Cache dependencies, split or shard the slow jobs, and run the macOS job only where the change
   can affect it. **Measured** duration, **unverified** remedy.
10. **Start the resolver on the first objection.** Consensus needs every reviewer, so one objection already decides the
    iteration. Hand findings to the resolver as each reviewer returns instead of waiting for the slowest one (Bean
    0255). **Unverified** saving.
11. **Registration wait that ends unknown.** "The PR head did not match the pushed head before the registration wait ran
    out" leaves CI unverified after a 180 s wait (**seen** twice on 2026-11-23). Wait on the event for the pushed
    commit, and retry once before reporting unknown.

### C. Failures that stop a flow when they need not

12. **Pre-flight: a slow exit is not a failure, and one bad probe is retried** (Bean 0393). **Seen.**
13. **Stage 3 ledger merge after the admission wait resolves itself** (Bean 0391) instead of stopping the stage.
14. **Image rebuilds do not disturb running flows.** The post-merge rebuild replaces `latest` while flows are starting
    containers. Build to a new tag and switch when the build is done; a running flow keeps the image it started with.
    **Seen** (probable cause of Bean 0393).
15. **Stall budget per model.** The 90 s default cut every Fable reviewer until the wrapper was told 600 s. The default
    should come from the model, not from whoever launches the flow. **Seen** (2026-11-23).

### D. Seeing a wait is half of removing it

16. **Budgets that mean something and a timing breakdown** (Bean 0383, Goals 3 and 4): agent time, CI wait, git work and
    idle time per stage, in the flow summary and on the pull request.
17. **Unbuffered wrapper logs** (Bean 0385). An overlap wait is invisible in the log today, so a stalled flow and a
    waiting flow look the same.

## Suggested order

5, 6 and 7 first (every flow, small changes, about 10 minutes each flow), then 2 and 3 (they turn hours of unnoticed
stoppage into nothing), then 1 (largest saving, largest change), then the rest. 5 and 6 belong in Bean 0383's flow.

## Notes

- Overlap: Beans 0395 (work during the overlap wait), 0399 (CI waits react in seconds), 0397 (resume adopts a pushed
  execution branch) and 0396 (flow survives the session) were split from this bean. This bean is the umbrella and
  recommendation list; each of those owns its own fix.
- Not removable: the maintainer's merge of pull requests into `main`. Recommendation 1 and 4 only stop other flows from
  idling behind it.
- Each recommendation becomes its own bean and flow when taken up; this bean is the list.

## Beans logged for these recommendations (2026-11-24)

| Rec. | Bean | Note                                                                                 |
| :--- | :--- | :----------------------------------------------------------------------------------- |
| 1    | 0395 | new                                                                                  |
| 2    | 0396 | new; with 0390                                                                       |
| 3    | 0397 | new                                                                                  |
| 4    | 0398 | new, draft: needs a maintainer decision                                              |
| 5    | 0403 | new, split out of 0383 Goal 2                                                        |
| 6    | 0383 | in the Stage 4 section                                                               |
| 7    | 0399 | new; event stream is 0352                                                            |
| 8    | 0400 | folded in: superseded runs are already cancelled; only `fail-fast` is left to decide |
| 9    | 0400 | new; with 0168 and 0166                                                              |
| 10   | 0255 | existing                                                                             |
| 11   | 0401 | new                                                                                  |
| 12   | 0393 | existing                                                                             |
| 13   | 0391 | existing                                                                             |
| 14   | 0402 | new                                                                                  |
| 15   | 0384 | existing                                                                             |
| 16   | 0383 | Goals 3 and 4                                                                        |
| 17   | 0385 | existing                                                                             |

Correction to recommendation 8: the workflows already cancel a superseded run on pull requests (`cancel-in-progress`),
so that half needs nothing.
