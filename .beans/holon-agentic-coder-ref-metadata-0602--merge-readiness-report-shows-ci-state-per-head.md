---
# holon-agentic-coder-ref-metadata-0602
title: "Readiness report to the maintainer shows per-head CI state; five PRs were merged with checks still pending"
status: completed
type: task
priority: high
tags:
  - harness
  - pr-merging
  - ci
  - reporting
created_at: 2026-11-27T04:33:33Z
updated_at: 2026-11-27T23:13:03Z
---

## Evidence

`gh pr list --state merged` rollups taken at 04:32Z: #395, #397, #399, #400 and #401 show checks still not COMPLETED
(#397: integration, ledger-invariants, unit on both OS, build on macOS, CodeQL Python; #399: 12 jobs; #400: 11 jobs;
#401: macOS unit). They were merged between 04:26Z and 04:31Z, about 10 minutes after their heads were pushed. #373
(named in the brief) now shows all complete, so its pending state at merge time cannot be proven: **not measured**,
because nothing records the CI state at the moment of merge. All ten merged PRs had exactly one review each and none had
a failed check.

`pr-merging.md` already says a PR is ready only when CI is green; the failure is in what is reported. The maintainer
merges, so the readiness message is the only gate between a pending head and main.

## Goal

1. The readiness report for every PR that targets `main` carries one fixed block: head SHA, review verdict on that SHA,
   Stage 5 calibration state (`P-*_calibration.md` present on the PR diff and `calibrate=success`), and the CI table
   (job, state, conclusion). Any job not COMPLETED/SUCCESS prints the PR as **not ready: CI pending**, and any missing
   Stage 5 calibration report prints **not ready: Stage 5 calibration missing**, in the first line, never as ready with
   a footnote.
2. A small harness script (`gh pr checks`, PR files for `P-*_calibration.md`, and the head SHA) generates the block, so
   the coordinator pastes it; the same script runs in `post-pr-merge` to record the merge-time CI state in the bean
   resolution.
3. Because CI is a post-review gate (bean 0235), the report says which of the gates (consensus, Stage 5 calibration,
   pipeline) is outstanding.

## Expected gain and cost

Gain: removes the class of merge-on-pending without adding a wait; the merge-time record makes it measurable. Cost: one
script and a paragraph in the readiness checklist.

## Notes

- Source: self-improvement audit 2026-11-27.
- Related: 0235, 0160.

## Audit evidence, 2026-11-27T07:49Z (fifth-merge audit)

- **`#404` (`05:13:02Z`) and `#405` (`05:13:20Z`):** merged to `origin/main` while `Test - Hygiene` was failing on
  `knowledge/wisdom.py` (`45944464931`, `45944497911`), poisoning `origin/main` for `2 h 11 min` until `#403` merged at
  `07:24:46Z` (`8+` wasted iterations across `#403,#406,#407,#408,#409,#410`).
- **Pending-CI merges continued:** `#403`, `#406`, `#407`, `#409`, `#410`, `#411` all merged right after hand
  `Merge branch 'main'` commits while `unit (macos-latest)` / `unit (ubuntu-latest)` were `QUEUED`/`IN_PROGRESS`; `#410`
  also merged with `reviews: []` (`0` GitHub reviews) and no calibration commit.

## Audit evidence, 2026-11-27T11:52Z (fifth-merge audit)

- **`HAC #419` (`measure-ci-head-durations`, `b366a559e`, `11:41:58Z`):** Merged `33 s` after Stage 5 pushed `2bf82d86`
  (`sync: merge target origin/main` + `chore(review): record review ledger rows (stage 5 carry-over)`) while
  `flow-measure-ci-head-durations` was still running in `stage: calibrate` and `2` checks
  (`unit (macos-latest, shard 1 of 2)`, `unit (macos-latest, shard 2 of 2)`) remained pending (`1` check still
  incomplete in head check-runs). As a result, `#419` landed on `origin/main` with **no
  `P-1795777767-ANA-G4N_calibration.md`**, no Stage 5 reconciliation, and no knowledge/wisdom commits, and left its
  worktree checkpoint stranded at `stage: calibrate`. The `0602` readiness script must block on both pending CI and
  missing `P-*_calibration.md`.

## Resolution

Implemented deterministic per-head readiness checking and merge-time CI/calibration recording:

- **Script**: [`.agents/scripts/pr_readiness.py`](.agents/scripts/pr_readiness.py) fetches `gh pr view` metadata
  (`headRefOid`, `reviews`, `files`, `statusCheckRollup`, `mergeable`, `mergeStateStatus`), evaluates `consensus`,
  `calibration` (`plans/*/P-*_calibration.md` plus optional `--checkpoint`), and `pipeline` gates, prints either
  `READY: ...` or `not ready: ... (outstanding gates: ...)` on line 1 alongside the sorted CI job table, and exits `1`
  when unready (or `0` under `--record` for post-merge logging).
- **Workflow Wiring**: Updated [`.agents/pr-merging.md`](.agents/pr-merging.md) to require running `pr_readiness.py`
  before reporting a PR ready, and updated
  [`.agents/skills/post_pr_merge/SKILL.md`](.agents/skills/post_pr_merge/SKILL.md) to capture `pr_readiness.py --record`
  output in bean resolutions.
- **Verification**: `uv run pytest tests/test_pr_readiness.py tests/test_invariant_registry.py` passed (`30/30`), and
  live smoke tests verified `READY:` (exit `0`) on HAC `PR #455` (`79ed5987`, `16/16` CI pass) and `not ready:` on HAC
  `PR #457` (`1a8ce158`, missing consensus/calibration + `3/16` CI failures).
