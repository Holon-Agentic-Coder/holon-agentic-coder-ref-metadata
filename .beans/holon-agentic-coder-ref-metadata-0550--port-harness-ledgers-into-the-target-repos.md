---
# holon-agentic-coder-ref-metadata-0550
title: "Reshape the harness failure ledger into the target repositories' existing ledger and knowledge base"
status: todo
type: task
priority: high
tags:
  - ledger
  - knowledge-base
  - harness
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-11-26T22:54:22Z
updated_at: 2026-11-26T22:54:22Z
---

## Instruction (maintainer, 2026-11-27)

"We also need the `.agents/ledger` inside the repos themselves, not in the harness. Make a bean to port over all harness
ledgers to repo ledgers." Then: "No, exactly three append-only ledgers is correct. You need to find the correct place to
port it to. Target repo never references harness paths. You need to reshape the ledger!"

## Constraints (unchanged rules)

- A target repository keeps **exactly three** append-only ledgers: `intents`, `plans`, `executions`. No fourth ledger.
- A target repository **never references harness paths** (`.beans/`, `todo/`, `.agents/`) or bean ids.

## Source

The harness ledger `.agents/ledger/coordinator-failures.jsonl` (CF-0001 onwards; fields id, created_at, session_date,
category, failure, my_part, cost, rule, refs), its validator `.agents/scripts/check_failure_ledger.py` and
`tests/test_failure_ledger.py`.

## Where it goes (maintainer, 2026-11-27: "the knowledge base failure mode is the best place")

Each harness row becomes one **knowledge-base failure mode** under `holon-knowledge/kb/failure_modes/` (the store agents
already consult before planning and reviewing), in the existing `failure_mode` shape:

- `kb_type`: `failure_mode`, tagged `process` plus the row's category (brief, readiness check, overlap scheduling,
  intent scope, measurement, conflict handling, bookkeeping, verification);
- `payload`: `name` (short), `description` (the failure), `action` (the preventive rule), `symptoms` (how it showed:
  halts, parks, wasted runs), and the cost;
- `evidence.ledger_refs`: the existing execution / intent action ids of the flows it affected (every row so far maps to
  a flow or PR: #315, #319, #321, #334, #340, #343, #350, #351 and others); `failure_count` from the number of
  occurrences;
- written with the deterministic stable envelope from PR #349, so concurrent flows do not conflict;
- no harness path and no bean id anywhere; the harness CF id is dropped (or kept only as an opaque external id if it
  carries no harness meaning).

No new ledger and no new execution event type are needed: the three ledgers stay exactly as they are.

## Plan

1. **Shape and loading (holon-agentic-coder, via a flow):** allow the `process` failure-mode tag and payload fields in
   the KB schema and its validator; make knowledge consult hand process failure modes to the planner, executor, reviewer
   and resolver as standing guidance.
2. **Port:** a one-off migration writes every harness CF row as a KB failure mode, sanitised.
3. **Write path afterwards:** the coordinator and the flow engine record new process failures as KB failure modes —
   through the flow's own PR, or a small dedicated PR for coordinator-only failures. Bean 0549's recurring test-failure
   signatures promote into the same failure modes.
4. **Harness:** retire `.agents/ledger/coordinator-failures.jsonl` and its validator (pointer note, then removal) and
   point the harness instructions (`AGENTS.md` checklist step and hard rule, `coordination.md` section 8,
   `self-improvement-audit.md`) at the target repository's process failure modes.
5. **holon-coherence:** the same, through its own flow.

## Acceptance

- Still exactly three ledgers in each target repository; no harness path or bean id in any ported row.
- Every harness CF row exists as a KB failure mode (tag `process`) with evidence refs to real flow action ids.
- Agents receive the lessons through knowledge consult in every stage that plans or reviews.
- The harness no longer keeps its own failure ledger.
- Related: Bean 0549, Bean 0371, Bean 0517, Bean 0244.
