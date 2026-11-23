---
# holon-agentic-coder-ref-metadata-0342
title: "Stage 5 logs a running total of promoted knowledge candidates as if this flow promoted them"
status: completed
type: bug
priority: low
tags:
  - flow
  - calibration
  - knowledge
  - logging
  - holon-agentic-coder
created_at: 2026-11-20T20:40:00+11:00
updated_at: 2026-11-20T23:35:00+11:00
---

## Problem

Stage 5 logs "Stage 5 promoted N knowledge/wisdom candidate(s)" (`flow/stages/calibrate.py`, about line 297) using the
length of whatever `promote_pending_candidates` returns. That function goes through every qualifying candidate in
`holon-knowledge/.index/action_index.db` (at least 2 trials), so N is a running total: on 2026-11-20 it climbed across
flows (576, 587, 593, …, 632, 640) while one flow actually added about 11 failure-mode files.

## Action

Through the Holon flow on `holon-agentic-coder`: log only the candidates this run newly promoted (and, separately if
useful, the total), with a hermetic test. Check that promotion itself is not repeating work on already promoted
candidates on every flow.

## Progress

- 2026-11-20: Holon flow started (slug `promoted-count-this-run-only`, claude-agent / claude-opus-5-5, worktree
  `apps/holon-agentic-coder/flow-promoted-count-this-run-only`).
- 2026-11-20: Flow complete. PR #216 (https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/216) APPROVED 3/3
  at review iteration 6, calibration report in the PR diff, EV predicted 40.70 / actual 53.52 (+12.82), MERGEABLE/CLEAN,
  all checks green; awaiting human merge. Stage 3 waited about 1 h 45 min on the overlap with PR #215. Stage 4 stopped
  once on a ledger-only conflict with main (plans/executions.jsonl), which was resolved by merging origin/main (lint and
  4801 tests pass) before resuming. Finding: promotion already wrote files idempotently but re-evaluated every promoted
  candidate on every run; it now skips candidates whose artefacts exist, and Stage 5 logs only this run's new
  promotions.

## Resolution

Delivered via [PR #216](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/216) and merged into `main`
(`eaaabaa`):

- **Key Architectural Deliverables**: Stage 5 logs only the candidates this run newly promoted. Promotion skips
  candidates whose artefacts already exist instead of re-evaluating every promoted candidate on each run. A new
  `flow/calibrate_promotion.py` keeps the promotion budgets unchanged.
- **Verification & Tests**: hermetic tests `test_calibrate_promoted_count.py` and `test_promotion_idempotence.py`, plus
  CLI coverage in `test_promote_cli.py`.
- **Holon Flow Traversal**: all 5 stages completed (Intent -> Plan -> Execute -> Review Loop -> Calibration), approved
  3/3 at review iteration 6. Calibration: expected value 40.70, actual 53.52.
