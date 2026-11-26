---
# holon-agentic-coder-ref-metadata-0545
title: "Backfill picker launches flows that park at admission; pre-check touch sets and record each pick"
status: todo
type: task
priority: medium
tags:
  - flow
  - scheduling
  - backfill
  - holon-agentic-coder
created_at: 2026-11-26T21:10:00Z
updated_at: 2026-11-26T21:10:00Z
---

## Problem

The backfill rule (keep 4 flows running, honouring disjoint touch sets) is applied from intent scope by hand. The real
Stage 3 check uses the plan's touch set, which is wider (bean 0541), so a pick can be refused only after Stage 1 and 2
have run, and the slot then idles in a parked flow.

## Evidence (window 13:40Z to 21:05Z)

- 4 of the 5 flows in flight in this window (`module-budget-default-350`, `single-runner-per-checkpoint`,
  `flow-references-github-issues`, `admission-remote-in-flight`) parked at first Stage 3 admission on PR #342 or an
  older parked flow, after 9 to 70 min of Stage 1 to 3 work (e.g. `admission-remote-in-flight` started 14:23:32Z,
  refused 14:28:21Z). They held 4 backfill slots for 6.2 h to 7.7 h each: about 29 slot-hours of the roughly 31
  slot-hours the 4 slots offered between 13:30Z and 21:00Z produced no merge.
- Only one flow of that set (`prune-single-flow-kb-failures`) reached Stage 4 without parking; the five merges in the
  window (#347, #342, #346, #348, #349) came from flows already past Stage 3.
- Cost not measured: the pick decisions themselves are not logged (no `picked_at`, blockers considered, or predicted
  overlap), so idle slot time per decision cannot be read from `todo/` or the flow logs.

## Proposed change

1. Before launching a pick, run a dry admission (`holon flow --admission-dry-run <intent>`): the intent's scope against
   open PRs, live flows and the generated hub list (bean 0543); launch only when it reports no overlap, or launch a
   different bean.
2. Never fill a slot with a bean whose scope contains a known hub (lazy exports, `docs/architecture.md`, shared ledgers)
   while another PR or live flow holds it; queue it behind that PR instead of parking a process.
3. Append a one-line record per pick (time, bean, slots in use, predicted blockers) to a flow-launch log so idle-slot
   cost becomes measurable (the audit currently lists it as not measured).

## Expected gain

Frees 4 slots from long parks; each pick that would have parked starts another bean instead. The record turns "idle slot
cost" into a table next audit.

## Cost

A read-only dry-run mode over existing admission code; a log line per launch. Depends on 0541 so intent scope matches
the plan.

## Acceptance

- The dry run exits non-zero and names the blocker for the 2026-11-26 `admission-remote-in-flight` intent against open
  PR #342.
- A launch log with one entry per pick exists and is read by the post-merge skill.
