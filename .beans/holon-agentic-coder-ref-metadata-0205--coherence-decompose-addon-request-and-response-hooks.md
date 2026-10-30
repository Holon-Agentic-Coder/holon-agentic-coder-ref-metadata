---
# holon-agentic-coder-ref-metadata-0205
title: "holon-coherence: decompose MitmproxyAddon.request and response into named pipeline steps"
status: in-progress
type: task
priority: normal
tags:
  - refactor
  - complexity
  - proxy
  - holon-coherence
blocked_by:
  - holon-agentic-coder-ref-metadata-0204
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-10-30T12:40:00Z
---

## Problem

Spawned by Bean 0177. Measured on `68fdf67`: `MitmproxyAddon.request` **209 lines, CC 65**, `MitmproxyAddon.response`
187 lines, CC 43, `_dump_flow_transaction` 109 lines, CC 28. Every proxy feature (cache, cleaning, routing, dashboard,
passive mode) adds branches to the same two hooks.

## Scope

1. `request` and `response` become ordered lists of small step objects or functions (`serve_dashboard`,
   `route_local_target`, `apply_cache`, `clean_payload`, `record_metrics` ...), each owning one concern and its tests.
2. Passive-monitoring short-circuit and error handling expressed once, around the pipeline.
3. All functions within the 0186 limits; wire-level behaviour unchanged (existing SSE and addon tests green).

## Touch set

`proxy/addon.py`, new `proxy/steps/` (or equivalent), mirrored tests.

## Dependencies

Blocked by 0204. Parallel-safe with 0206 once their step and provider modules are separate; sequence if both edit
`addon.py`.

## Notes

- Run through the Holon flow on holon-coherence.

## Progress (2026-10-30)

- Taken over from the interrupted session: intent `I-1793355582-coherence-decompose-addon-hooks/_` pushed, checkpoint
  shows only Stage 1 complete. Resumed with `holon flow --checkpoint … --from-stage plan` (antigravity-agent /
  gemini-3.8-flash-medium, worktree `apps/holon-coherence/flow-0205-decompose-addon-hooks`).
