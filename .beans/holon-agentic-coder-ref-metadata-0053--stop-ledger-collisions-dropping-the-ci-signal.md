---
# holon-agentic-coder-ref-metadata-0053
title: "Stop concurrent flow ledger collisions from silently dropping the whole CI signal"
status: todo
type: bug
priority: high
tags:
  - flow
  - ledger
  - ci
  - provenance
created_at: 2026-09-27T11:35:00Z
updated_at: 2026-09-27T11:35:00Z
---

Every Holon flow run appends to the same three files -- `holon-knowledge/ledger/{intents,plans,executions}.jsonl`. Two
flows in flight therefore conflict on those files and nothing else. GitHub builds `pull_request` jobs on the PR merge
ref; a conflicting PR has **no buildable merge ref**, so `Test - Unit`, `Test - Integration`, `Test - Hygiene` and
`Run Make` are skipped entirely, while the PR page still looks reviewable.

## Measured evidence (Bean 0019, PR #59)

- `gh pr view 59` reported `mergeable=CONFLICTING`, `mergeStateStatus=DIRTY` with **only** the three ledger files
  overlapping against `main` -- no source file conflicted.
- Only CodeQL reported during that window, because it runs on `refs/pull/59/head` (`dynamic` event) rather than the
  merge ref. The gap looks like "some checks ran, most silently did not", which reads as a workflow defect and is not
  one.
- Workaround applied by hand: merged `main` into the execution branch and resolved the ledgers by **union** (correct
  semantics for append-only JSONL) -- deduplicated, ordered by `created_at`, all lines valid JSON. Merge commit
  `ed7600e`, `parents: a855d5b c80ce35`; history extended, never rewritten.

## Why it matters

The failure mode is invisible in exactly the situation where test signal matters most: two agents landing overlapping
work. A flow branch can reach review with zero test coverage evidence and a green-looking check list.

## Candidate remedies (needs an owner decision)

1. Make the execute stage merge-and-union the ledgers before pushing, so the flow branch is never in conflict on them.
2. Shard the ledgers per run (`ledger/executions/<execution_id>.jsonl`) with a concat view for readers, so appends never
   touch the same blob.
3. Minimum viable guard: have the flow (or a CI job) detect `mergeStateStatus=DIRTY` and surface "test workflows are not
   running on this PR" instead of leaving it silent.

## Notes

- Discovered while closing Bean 0019 stage 4; recorded there as "systemic finding worth its own bean".
- Target repository: `holon-agentic-coder`, work under `apps/sandbox-executor/src/sandbox_executor/flow.py` and
  `executor.py`. Changes must go through the flow, not a host-side hand edit.
