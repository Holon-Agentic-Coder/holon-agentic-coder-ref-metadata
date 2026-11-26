---
# holon-agentic-coder-ref-metadata-0517
title: "Concurrent flows add the same knowledge-base or wisdom file, so their PRs conflict add/add"
status: in-progress
type: bug
priority: normal
tags:
  - flow
  - knowledge-base
  - merge-conflicts
  - holon-agentic-coder
created_at: 2026-11-26T12:40:00Z
updated_at: 2026-11-26T12:40:00Z
---

## Problem

Ledger rows no longer conflict (per-flow fragments, PR #314), and Bean 0244 (completed) made KB/WB facts append-only
records, yet Stage 5 promotion still writes shared knowledge-base and wisdom files whose names are content hashes. Two
flows that promote the same heuristic or pattern add the same path with different content: on 2026-11-26 open PRs #340
and #341 both add `holon-knowledge/wisdom/heuristics/WB-heuristic-84a6ddeb.json` (add/add conflict), and earlier #308
and main both added `holon-knowledge/kb/patterns/KB-pattern-dd1ab35f.json` (resolved by keeping the later `updated_ts`).
Whichever PR merges second needs a conflict pass, a push and a CI cycle.

## Proposed fix

- Write promoted KB/wisdom entries as per-flow fragments merged on main, as the ledgers now do; or
- give `resolve_known.py` a deterministic rule for add/add on KB/WB JSON (union of evidence, later `updated_ts` wins) so
  the conflict is settled mechanically without a subagent.
- Related: Bean 0244 (KB/WB facts append-only, completed), Bean 0371 (ledger fragments), Bean 0506 (KB-failure clutter).

## Audit evidence (2026-11-26T13:40Z)

- Frequency: three of the five merges in the window (#341 at 12:58Z, #340 at 13:04Z, #343 at 13:04Z, with #345 clean)
  add or rewrite `holon-knowledge/wisdom/heuristics/WB-heuristic-84a6ddeb.json`, five minutes apart, so each of the last
  two conflicted with the one before (add/add). 661 `holon-knowledge/kb|wisdom` json path touches in 59 main commits
  since 11-25.
- Cause is not hash collision: the file is the "Universal heuristic: main" wisdom entry whose payload carries run
  counters (`total_executions` 23, Wilson bound 0.857). Every flow's Stage 5 promotion rewrites it with a different
  counter, so any two concurrent PRs conflict. The real fix is to stop writing counter-bearing KB/WB files in the flow
  PR: derive them on `main` in the existing Promote Ledger workflow, as the ledgers now are. The `resolve_known.py` rule
  is only the fallback.
- Cost per conflict: a resolver pass, a push, a CI cycle and a rerun, see bean 0522 (about 12 to 26 min plus a full
  review).

## In progress

Flow kb-wisdom-deterministic-files launched 2026-11-27 (claude-agent, claude-opus-5-5); log
todo/flow-kb-wisdom-deterministic-files.log.
