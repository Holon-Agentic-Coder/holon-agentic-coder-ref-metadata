---
# holon-agentic-coder-ref-metadata-0191
title: "One GitHub adapter owns every gh call (PR create/update, CI probe, mergeability, review posting)"
status: todo
type: task
priority: high
tags:
  - refactor
  - ports-and-adapters
  - github
  - holon-agentic-coder
blocked_by:
created_at: 2026-10-29T12:20:00Z
updated_at: 2026-11-21T01:20:00+11:00
---

## Problem

Spawned by Bean 0177. `flow.py` (`993b686`) issues 14 raw `gh` invocations spread over `create_or_update_pr`,
`probe_ci_checks` (CC 24), `check_pr_mergeability` (192 lines, CC 28), `post_pr_review_consensus` (185 lines, CC 40),
`generate_semantic_pr_metadata` (CC 46), `_wait_for_ci_registration` and `_wait_for_pending_ci`. GitHub I/O, polling
policy and domain decisions are interleaved, so tests must patch module globals and every review-loop change edits the
same functions.

## Scope

1. `adapters/github.py`: a `GitHubPullRequests` class (repo-scoped) with intention-revealing methods (`open_or_update`,
   `ci_checks`, `mergeability`, `post_review`), the only place that runs `gh`. It keeps the existing write guard and
   token redaction.
2. Pure decision functions (CI verdict, mergeability verdict, consensus body, semantic PR title/body) move to
   `flow/review_policy.py`-style modules with no I/O; the adapter returns plain data.
3. A `FakeGitHub` in `tests/` replaces `patch` on `subprocess`/module globals in the affected tests.
4. Every function in the touched code within the 0185 limits.

## Touch set

`flow/github.py` (becomes `adapters/github.py` plus pure modules), call sites in `flow/review_loop.py` and
`flow/stages/review.py` (call lines only), `review_target.py` if it shells out to `gh`, matching tests.

## Dependencies

Blocked by 0187. Blocks 0192. Sequence with 0160 (CI polling) and 0179.

## Notes

- Run through the Holon flow on holon-agentic-coder. Tests never call real `gh`.

## Audit (2026-11-20)

Blocker Bean 0187 was scrapped (the `flow/` split landed via #147/#163); the `flow.py` references above are stale. The
`gh` calls now sit under `flow/github/` plus `review_target.py`, `calibration.py` and `flow/review/loop.py`; there is
still no single adapter.

## Audit (2026-11-21)

Touch set refreshed against `origin/main`: the `gh` calls live in
`flow/github/{pr,ci,ci_wait,ci_final_head,ci_reverify,merge,merge_method,review_post}.py`, `flow/in_flight.py`
(`gh pr list`/`pr diff`), `review_target.py` and `calibration.py`; call sites in `flow/review/loop.py` and
`flow/stages/review.py`. Tests mirror under `tests/flow/github/` and `tests/flow/review/`. `flow/github/pr.py` is 515
lines, so the module budget (Beans 0264, 0340) applies to any new adapter module.
