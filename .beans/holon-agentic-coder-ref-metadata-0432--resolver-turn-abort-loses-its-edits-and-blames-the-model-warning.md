---
# holon-agentic-coder-ref-metadata-0432
title: "A resolver turn aborted with code -6 leaves unsalvaged edits and an error that blames a harmless warning"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-4
  - salvage
  - holon-agentic-coder
created_at: 2026-11-24T17:45:00Z
updated_at: 2026-11-25T07:20:00Z
---

## Problem

On 2026-11-24 the Stage 4 resolver turn for bean 0405 (PR #275, `claude-fable-5-2`) ran 221 min and exited with code -6
(SIGABRT) at about 17:26Z. Three defects showed up together:

1. **Edits are not salvaged.** The resolver had modified 18 test files (835 insertions, 422 deletions) and committed
   nothing. The Stage 3 salvage (`flow/partial_salvage.py`, bean 0397) only covers a killed executor. After a failed
   resolver turn the host just records ledger rows and leaves the dirty worktree ("uncommitted changes remain ... they
   are carried over"). Any `git clean`, worktree prune or fresh run would lose three hours of work.
2. **The error blames the wrong thing.** `_run_resolver_agent` reports `Resolver agent exited with code -6` and the
   output tail holds only the line "Claude Code doesn't recognize the model claude-fable-5-2 ... assumes a context
   window of 200k tokens". That is a warning printed on every run (PRs #270, #271, #272 and #278 all passed on the same
   image), so the flow summary points operators at a non-cause. No signal name, no last agent output and no turn
   duration are reported.
3. **Timing of the failure is unexplained.** The container died at 17:26:20Z but the host logged the failure at
   17:32:22Z, six minutes later, with no log line in between.

## Fix direction

- On a failed or aborted resolver turn, commit the leftover edits as labelled partial work on the execution branch
  (reuse `partial_salvage`), or at least write a patch to a stable path and log it, before the stage returns.
- Name a negative exit code as its signal (`-6` as SIGABRT) and keep the last non-warning lines of agent output in the
  tail; drop known benign warnings from the tail.
- Log what the host does between container exit and the failure line.

## Notes

- Cause of the SIGABRT is unconfirmed: no OOM event, no usage-limit text, no output after the warning. Most likely the
  runner process aborting (for example a heap or resource failure) after hours of test output with no turn bound (bean
  0430). The warning only means the assumed window was 200k tokens; it did not itself abort the process.
- Related: 0397, 0430, 0405. Target repository: holon-agentic-coder, flow `unit-suite-slowest-tests-speedup`.

## Occurrence (2026-11-25, flow of pull request #308)

- The iteration-4 resolver of `workspace-survival-job-parallel` died with exit 1 on "API Error: Can't reach the API
  server ... (ENOTFOUND)" (a network outage) and left 5 tracked and 4 untracked files of partial work in the worktree.
- A resume with `--from-stage review` now stops at once: "Review stage failed at flow_start: target sync ... was
  blocked: the worktree has uncommitted tracked changes; commit them before the target sync". The target sync added with
  pull request #283 refuses a dirty worktree, so a flow whose resolver died mid-turn cannot be resumed at all without a
  person committing or discarding the dead turn's edits.
- Wanted: on resume, the engine salvages a dead resolver turn's edits itself (for example commits them as a "resolver
  partial work" commit that the next review sees as a delta, or stashes them under a recorded name and hands them to the
  next resolver turn), and a resolver turn that fails on a network error is retried in place before the stage is failed
  (Bean 0424).
