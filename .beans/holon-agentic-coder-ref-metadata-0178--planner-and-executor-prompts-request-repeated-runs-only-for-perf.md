---
# holon-agentic-coder-ref-metadata-0178
title: "Planner and executor prompts request repeated test runs only for performance work, N runs each under xdist"
status: completed
type: task
priority: high
tags:
  - holon-flow
  - prompts
  - tests
  - token-cost
  - holon-agentic-coder
created_at: 2026-10-28T12:07:13Z
updated_at: 2026-10-29T06:40:00Z
---

## Problem

The harness now has invariant 19 in `.agents/rules.md`: repeated test runs are requested only when a change is
absolutely required to measure performance or timing behaviour, with an explicit N, and every repetition runs under
pytest-xdist (`-n auto --dist worksteal`). It governs how harness intents are written, but the in-container planner and
executor in `holon-agentic-coder` never see it. A plan or an executing agent can still choose serial repeats by itself.

Real cost (Bean 0168, Stage 3 attempt 4, 75.7 minutes): about 55 minutes went on test runs, 27 minutes of them on 50
serial runs of two test files under CPU load (about 30 s each). Under `-n auto` the same files ran in 16.97 s.

## Goal

Through the Holon flow on `holon-agentic-coder`:

1. Add the rule to `holon-config/prompts/planner.template.md` and `holon-config/prompts/executor.template.md`
   (target-native wording, no harness paths or bean ids):
   - Plan and run repeated test runs only when the intent requires measuring performance or timing behaviour; otherwise
     run the affected tests first, then the full suite once.
   - When repetition is required, take N from the intent (or state N and the reason in the plan); never open-ended.
   - Each repetition runs with `-n auto --dist worksteal`, including runs under CPU load. Serial runs only when serial
     behaviour is itself the measurement, and then once.
   - Record every run's pass/fail count and pytest-reported time plus the median in the execution notes, from real runs
     only; never re-measure a commit that already has a recorded figure.
2. Document the rule in the testing docs (`apps/sandbox-executor/docs/testing_guide.md` or the planner/executor docs).
3. Tests (pytest only): the rendered planner and executor prompts contain the rule.

## Notes

- Prompt and docs change only; disjoint from `flow.py`/`cli.py`, so it can run in the parallel lane. Check its touch set
  against Bean 0144, which extends `holon-config/prompts/review_loop.template.md`.
- Related: Bean 0168 (origin), harness invariant 19.

## Resolution

Completed through the 5-stage Holon flow on `holon-agentic-coder`:

- **Flow**: `I-1793246276-prompts-repeat-test-runs-only-for-performance-under-xdist` →
  `P-1793246292-claude-agent-claude-opus-5-5` → `E-1793246422-claude-agent-claude-opus-5-5`.
- **PR #105** (https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/105): updated
  `holon-config/prompts/planner.template.md`, `holon-config/prompts/executor.template.md` (including step-by-step
  executor commit guidance), `docs/testing/testing_guide.md`, and `tests/test_prompt_templates.py`. Converged in 2
  review-loop iterations (3/3 ensemble approval at `98d3bc5`, review `5692781712`, 10/10 CI green), Stage 5 calibrated
  (`8fd40d4`, EV 54.59 predicted / 64.57 actual, Prettier-formatted in `e41bcd0`), and merged by the maintainer as
  `c9825b8` (2026-10-29T04:56:20Z).
