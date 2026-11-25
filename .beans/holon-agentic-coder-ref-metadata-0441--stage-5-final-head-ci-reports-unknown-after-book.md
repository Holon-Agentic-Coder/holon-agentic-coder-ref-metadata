---
# holon-agentic-coder-ref-metadata-0441
title: "Stage 5 final_head_ci reports unknown on bookkeeping-gated or transient-probe heads"
status: todo
type: bug
priority: normal
tags:
  - flow
  - stage-5
  - ci
  - holon-agentic-coder
created_at: 2026-11-25T00:28:00Z
updated_at: 2026-11-25T00:28:00Z
---

## Problem

After `PR #272` (`ci_bookkeeping_gate`) merged on `2026-11-24T21:10:12Z`, Stage 5 `final_head_ci` settled cleanly as
`success` in `47.7–47.9 s` on some flows (`git-flow-self-doc`, `local-llm-self-doc`), but settled as `state: "unknown"`
(`reason: "CI checks were not measured on GitHub."`) on others (`knowledge-self-doc` in `46.6 s`, `review-meta-self-doc`
in `16.0 s`) even though `merged_head_ci` had passed all 11 checks and `CodeQL`/`Analyze` passed on the final
calibration head.

## Evidence (2026-11-24)

- Checkpoints after `21:10:12Z`:
  - `knowledge-self-doc` (`PR #290`): `merged_head_ci.state = "passed"` (`07239e02`, 11 checks), then `final_head_ci` on
    `57152552` returned
    `{"state": "unknown", "ci_wait": {"state": "settled", "waited_seconds": 46.591}, "reason": "CI checks were not measured on GitHub."}`
    while `CodeQL`, `Analyze (python)`, and `Analyze (actions)` completed `success` on `57152552`.
  - `review-meta-self-doc` (`PR #293`): `merged_head_ci.state = "passed"` (`0175c138`, 11 checks), then `final_head_ci`
    returned
    `{"state": "unknown", "ci_wait": {"state": "settled", "waited_seconds": 16.047}, "reason": "CI checks were not measured on GitHub."}`.
- In `apps/holon-agentic-coder/main/apps/sandbox-executor/src/sandbox_executor/flow/github/ci_final_head.py:155-156`,
  `classify_final_head` returns `"unknown"` whenever `ci_status.get("source") != "github_cli"`, including if a later
  poll inside `wait_for_pending_ci` returns a non-`github_cli` payload or if bookkeeping-gated workflows emit no
  `all_passed=True` probe result.

## Proposed change

1. Audit `wait_for_pending_ci` and `classify_final_head` in `ci_final_head.py` so transient non-`github_cli` poll errors
   are retried within the wait budget instead of overwriting an active `github_cli` poll and short-circuiting to
   `unknown`.
2. Ensure skipped-by-bookkeeping-gate checks on calibration-only commits (`conclusion: skipped` with `CodeQL`/`Analyze`
   passing) classify deterministically as `success` (or explicitly `bookkeeping_skipped`) rather than `unknown`.
3. Add a unit test in `tests/test_calibrate_final_head_ci.py` covering both transient poll hiccups and bookkeeping-gated
   final heads.

## Expected gain

Eliminates spurious `final head CI: unknown` warnings at the merge boundary and ensures Stage 5 completes cleanly once
`PR #272`'s bookkeeping gate skips redundant suites.

## Cost

Small: `ci_final_head.py` + unit test, delivered via the Holon flow.

## Notes

- Target repo change through the Holon flow (`holon-agentic-coder`).
- Related: Bean `0403` (`PR #272` bookkeeping gate), Bean `0401` (CI registration wait `unknown` on pushed head).
