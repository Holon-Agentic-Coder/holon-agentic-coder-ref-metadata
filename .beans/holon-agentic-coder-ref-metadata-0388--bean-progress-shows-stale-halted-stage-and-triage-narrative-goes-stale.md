---
# holon-agentic-coder-ref-metadata-0388
title: "Bean progress shows a stale 'Halted' stage while a role is live, and the triage narrative goes stale"
status: todo
type: bug
priority: normal
tags:
  - harness
  - bean-progress
  - prioritise-beans
created_at: 2026-11-23T12:40:00Z
updated_at: 2026-11-24T13:00:00Z
---

## Problem

Two harness reporting defects seen on 2026-11-23:

1. **bean_progress Stage column.** While a review round was running, the Stage cell still read "Stage 4 (Halted iter N)"
   from the last checkpoint (Bean 0191, 0367, 0378 rows), although the script's own Last Activity cell said "now: review
   iter N+1 running". The maintainer was told "halted" for flows that were live.
2. **Triage narrative.** `prioritise_beans.py` keeps hand-written narrative strings (Executive Summary, per-bean notes).
   After a day of merges the matrix said HAC PRs #243, #244 and #245 were open and recommended Bean 0333 as "ready now"
   after it had merged (PR #258). The counts are computed; the prose is not.

## Goal

- `bean_progress.py`: when a role container is live for the flow, the Stage cell shows the live stage and iteration (for
  example "Stage 4 (Review iter 3)"); "Halted" appears only when nothing is running.
- `prioritise_beans.py`: statements about open PRs, the current `main` commit and "ready now" recommendations are
  derived from `gh` and the bean files at generation time, or the script fails when a hand-written note names a PR or
  bean whose state no longer matches. No recommendation ever names a completed bean.
- Harness-only change.
