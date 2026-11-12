---
# holon-agentic-coder-ref-metadata-0283
title: "An agent's API error output is written as the plan and reported as a metrics failure"
status: todo
type: bug
priority: high
tags:
  - flow
  - planner
  - token-reduction
  - holon-agentic-coder
created_at: 2026-11-12T03:00:00Z
updated_at: 2026-11-12T03:00:00Z
---

## Problem

On 2026-11-12 the planner for the `ids` and `creds` flows (`claude-sonnet-5-5`) received an Anthropic API 400
(`system.2.cache_control.ttl: a ttl='1h' cache_control block must not come after a ttl='5m' cache_control block`) and
the engine wrote that single line to `plans/P-*.md` as if it were the plan. The metrics check then failed with "missing
or non-numeric overall metrics", hiding the real error, and the stray untracked file had to be deleted by hand before a
resume. The underlying clash is the token-reduction proxy's `payload_cleaner` injecting `cache_control` into the
Anthropic payload next to the claude CLI's own blocks; `HOLON_TOKEN_REDUCE=0` avoids it (see Beans 0227 and 0157).

## Action

Run through the Holon flow. (1) The planner entrypoint detects an API error in the agent's output (`API Error:`, a 4xx
or 5xx status line) and fails the stage with that text, never writing it to the plan path. (2) A failed plan attempt
leaves no untracked plan file behind. (3) Make `payload_cleaner` leave existing `cache_control` blocks alone and inject
only consistent ones (a `1h` block never after a `5m` block), with a hermetic test. Keep exactly the three ledgers.
