---
# holon-agentic-coder-ref-metadata-0559
title: "Resolver-halt runbook and ledger line until bean 0549 lands"
status: todo
type: task
priority: normal
tags:
  - harness
  - review-loop
  - runbook
created_at: 2026-11-26T22:59:59Z
updated_at: 2026-11-26T22:59:59Z
---

## Problem

Three flows halted on the same two resolver pre-push tests on 2026-11-26 (beans 0547, 0548), and each was diagnosed by
hand: read the log, name the failing tests, reproduce, fix, resume. One resume lost uncommitted edits (bean 0551) and
one subagent used `git stash` (CF-0014). Time lost per halt is **not measured**: neither the flow log nor the failure
ledger records when a halt began and when it was cleared. Bean 0549 will automate the loop in the engine, but is not
landed.

## Proposal (harness only, cheap, removed when 0549 lands)

1. A short runbook in `.agents/workflows.md` for a resolver halt: (a) save the worktree diff as a patch file; (b) make a
   temporary WIP commit on the flow branch only if the resume needs a clean tree (never stash; see bean 0556); (c) read
   the failing test ids from the log and reproduce them with `uv run pytest <ids>` in the flow worktree, in both a clean
   environment and the review-loop environment; (d) fix or log the bug; (e) resume `--from-stage review`; (f) confirm
   the fix is in the pushed head (bean 0551).
2. A coordinator-ledger line per halt with the failing test ids, the cause class, and halt and clear timestamps, so the
   time lost is measured and 0549's classifier has real cases.

## Expected gain

Fewer lost edits and stash-style breaches, and the first measurement of halt cost. Cost: one section and one ledger
convention.

## Resolution
