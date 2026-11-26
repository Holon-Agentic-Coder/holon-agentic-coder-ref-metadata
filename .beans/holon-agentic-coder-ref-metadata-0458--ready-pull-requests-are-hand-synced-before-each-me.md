---
# holon-agentic-coder-ref-metadata-0458
title: "Ready pull requests are hand-synced before each merge and merged before that pipeline ends"
status: todo
type: bug
priority: high
tags:
  - harness
  - pipeline
  - merge
  - churn
created_at: 2026-11-25T05:45:00Z
updated_at: 2026-11-25T05:45:00Z
---

## Problem

When the flow has ended, nothing keeps a ready pull request mergeable. Each merge into `main` makes every other ready
pull request conflict on the ledgers (Bean 0371), so before each merge someone runs the `resolve-conflict` skill
(`git merge origin/main`), which pushes a main-merge head and restarts the full pipeline. The merge then often does not
wait for that pipeline. The end state that matters is a passing pipeline and a passing consensus on the merged head;
this sequence spends a full pipeline per merge and still merges heads whose pipeline has not finished.

PR #283 (the flow resolves conflicts at every stage) does not help here: it acts only while a flow is running, and these
flows had finished hours earlier.

## Evidence (self-improvement audit, 2026-11-25T05:45Z; scripts in `todo/self-improvement-audit-2026-11-25a/`)

- Merge sweep #288 to #299, 03:35:55Z to 05:20:56Z: every PR got a `Merge remote-tracking branch 'origin/main'` commit
  (the message `resolve-conflict` leaves; the engine writes `sync: merge target ...` or `(conflict gate)`) a median of
  5.5 min before its merge (longest 34.6 min, #292). The flows behind them had ended at 18:52Z to 00:45Z. 13 such
  commits in all on #284 to #300 between 02:28Z and 05:23Z, after #283 had merged.
- 8 of the 12 (#289, #290, #293, #294, #295, #297, #298, #299) were merged before the pipeline on that final head had
  finished (#293, #294, #298 merged 1.1 to 1.2 min after the sync). All later passed, so nothing broke this time, but
  the merged head was not verified when it merged (`sweep.md`).
- Main-merge heads in the period: 28 of 78 PR heads, 409 runner-min (median 7.9 min wall), against 167 runner-min for
  the 13 code heads (`period-churn.txt`).
- Ready PRs waited a median of 335.7 min (longest 523.4 min, #288) between last approval and merge; in that time every
  merge to `main` made them conflict again.
- All 32 merged PRs from #268 to #299 show `mergedBy: thomashan`; the agents use the same account, so the log cannot
  tell whether a merge into `main` came from the maintainer or from an agent session. The hard rule says only the
  maintainer merges into `main`.

## Proposed change

1. Bean 0371 (ledger fragments) removes the conflicts. Until then the steps below make the merges cheap and verified.
2. Harness (`.agents/pr-merging.md`, `post-pr-merge`): after a merge, sync the other ready PRs in one batch, not one at
   a time just before each merge. Ledger-only conflicts are resolved mechanically. Each PR is left with a green pipeline
   on its final head, and the ready list shows which PRs are mergeable now.
3. Do not sync a PR that is already `MERGEABLE`; the main-push pipeline tests the merged result anyway.
4. When a PR has been synced, its merge waits for the pipeline on that head (`gh pr checks --watch`); the merge report
   states the head SHA and its pipeline result.
5. Make merges attributable: an agent session that merges a PR (only PRs into branches other than `main`) says so in a
   PR comment, so merges into `main` without one are the maintainer's.

## Expected gain

About 12 full pipelines per sweep of 12 (about 95 min of wall time, 230 runner-min). The serial gap between merges (6.6
min median, set by the sync pipeline) drops to the time it takes to click merge. No merge of an unverified head.

## Cost

Small, harness only (`.agents/pr-merging.md`, `.agents/skills/post_pr_merge/`, `.agents/skills/resolve_conflict/`).

## Notes

- Related: Bean 0454 (written at the same time by the other session: skip the full pipeline on mechanical merge heads;
  same sweep evidence, CI-side fix), Bean 0371 (ledger fragments, the structural fix), Bean 0423 (two sessions), Bean
  0398 (stacked start), Bean 0420 (PR merged while its flow runs).

## Audit evidence (2026-11-26T03:50Z, fifth-merge audit)

- `thomashan/dev-env#42` (`tmux-focus-events-on`): `Merge remote-tracking branch 'origin/main'` (`842a47cf`) was pushed
  at `2026-11-26T03:45:52Z` and merged **`29 s` later** at `03:46:21Z`, long before `Unit Tests` (`15–20 min`) or
  `Ubuntu Converge E2E` (`5–6 min`) completed.
