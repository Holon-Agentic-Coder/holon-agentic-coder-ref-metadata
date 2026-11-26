---
# holon-agentic-coder-ref-metadata-0583
title: "Leftover review-loop items from 0557: planner/reviewer environment rule and readiness prompt lines"
status: todo
type: task
priority: high
tags:
  - review-loop
  - prompts
  - holon-agentic-coder
created_at: 2026-11-26T23:53:24Z
updated_at: 2026-11-26T23:53:24Z
---

## Problem

Bean 0557 was closed after PR #359 merged, but two items from its "What would have caught it earlier" list were not
delivered. PR #359 only shipped the contract test. Source:
[Bean 0557](holon-agentic-coder-ref-metadata-0557--flow-engine-prs-run-the-affected-suites-under-the-review-loop-environment.md),
whose Resolution section records these as "Not in #359 ... No bean tracks them yet". Related:
[Bean 0562](holon-agentic-coder-ref-metadata-0562--every-invariant-has-an-explicit-check.md), the umbrella for
invariants that must have explicit checks.

## Leftover items

1. Planner/reviewer rule, quoted from 0557: "A planner/reviewer rule: a diff that sets, overlays or removes environment
   variables, cwd or git config for a process that spawns children must list the child processes affected and carry a
   test that runs one under the new environment."
2. Readiness prompt lines, quoted from 0557: "A readiness step for changes to the flow engine: run the affected suite
   inside the review environment (CF-0006 rule) as a recorded command and its result in the readiness note."

## Goal

Deliver both items so a flow-engine change that overlays environment, cwd or git config for child processes is planned,
reviewed and checked under that environment before it merges, as the #350 regression class requires.

## Scope

- Planner and reviewer prompts: add the environment rule from item 1.
- Readiness prompt: add the recorded-suite step from item 2.
- Prompt text only; no change to the contract test from PR #359.
