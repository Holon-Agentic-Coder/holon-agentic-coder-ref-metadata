---
# holon-agentic-coder-ref-metadata-0482
title: "Estimate a performance change's saving from history before launching its flow"
status: todo
type: task
priority: high
tags:
  - harness
  - flow
  - performance
  - process
created_at: 2026-11-26T05:30:00Z
updated_at: 2026-11-26T05:30:00Z
---

## Problem

The first macOS-relevance gate flow (PR #315, closed 2026-11-26) ran about 6 h end to end and passed review and
calibration, but its own replay showed its neutral-list rule would have skipped the macOS leg on 0 of 74 merged PRs
(#241 to #314). It saves nothing on code PRs. The coordinator's intent left the form of the rule to the flow, so the
flow built a gate that could not pay off. The replacement flow is `macos-unit-sensitive-paths-only` (Bean 0400).

## Proposed rule

Add to the intent guidance in `.agents/holon-flow.md` and to the `holon_flow` skill: an intent whose goal is speed or
cost must

- state the measured baseline and an expected saving computed from historical data (replay over recent merged PRs or CI
  runs) before launch;
- have that measurement done by a cheap read-only subagent, not by the flow itself;
- include re-measuring the result in its acceptance criteria;
- fix the design choices that decide whether any saving exists (for example which paths skip a CI leg) instead of
  leaving them to the flow.

## Acceptance

- The rule is in `.agents/holon-flow.md` and the `holon_flow` skill, short and token-cheap.
- A launch of a speed or cost intent without a baseline and expected saving is refused by the skill's checklist.

## Notes

- Evidence: PR #315 (closed), Bean 0400, flow time audit 2026-11-26 (`todo/flow-time-audit-2026-11-26.md`).
