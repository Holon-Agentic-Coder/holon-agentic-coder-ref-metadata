---
# holon-agentic-coder-ref-metadata-0228
title: "Stage 4 loop ownership: the flow engine owns max iterations; the review container is single-shot"
status: todo
type: refactor
priority: high
tags:
  - flow
  - review-loop
  - stage-4
  - holon-agentic-coder
created_at: 2026-11-05T00:30:00Z
updated_at: 2026-11-05T00:30:00Z
---

## Problem

Stage 4 has two stacked loop mechanisms whose counters mean different things. The flow engine runs its own review loop
(budget 25 iterations, checkpointed), and per iteration dispatches the containerised review-loop entrypoint — which has
its OWN internal iteration loop, built for standalone `holon review` use. The engine wires the two together by passing
its current iteration counter as the container's loop limit (`--max-iterations={iteration}` in `flow.py`'s
`_dispatch_review_ensemble`). On engine iteration 1 that reads as a mysterious `--max-iterations=1`; on a resumed engine
iteration N a fresh container is told it may loop N times internally over one head, so the engine's counter silently
changes the container's behaviour. Observed and ruled on by the maintainer during the 2026-11-04 manual end-to-end flow
run.

## Decision (maintainer, 2026-11-05)

One loop, the engine's. The engine owns max iterations, the per-iteration budget and the checkpointed counter; the
container is a single-shot worker.

## Scope

1. The engine always dispatches the review container for exactly ONE ensemble pass per engine iteration, and passes the
   engine's iteration number separately, for labelling only (ledger `review_iteration`, the posted "Iteration {n}"
   heading) — e.g. an explicit `--iteration=N` flag — never as the container's loop limit.
2. The container's internal multi-iteration loop remains only for standalone `holon review <branch>` invocations; its
   loop limit flag keeps its meaning there and is never derived from someone else's counter.
3. The engine's iteration budget (25) and per-iteration time budget stay the sole caps, persisted in the checkpoint so a
   `--from-stage review` resume continues the count instead of restarting it.
4. Tests (pytest only; no real Docker, gh, git remotes or LLM calls): the dispatch always requests one pass regardless
   of engine iteration; the labelling iteration number flows into the ledger entries and posted body; a resumed review
   continues the engine count.

## Notes

- Run through the Holon flow on holon-agentic-coder.
- Related: the native Stage 4 has no automatic resolver (findings stop the stage by design today), so engine
  iterations > 1 only occur via resume after external resolution; the resolver is decided and specified in the follow-up
  resolver bean (engine iterations become review+resolve).
