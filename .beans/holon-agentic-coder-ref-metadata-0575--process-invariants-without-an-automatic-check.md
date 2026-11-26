---
# holon-agentic-coder-ref-metadata-0575
title: "Process invariants still without an automatic check (registry gaps)"
status: todo
type: task
priority: high
tags:
  - harness
  - invariants
  - tests
created_at: 2026-11-26T23:22:20Z
updated_at: 2026-11-26T23:22:20Z
---

## Origin

The invariant registry (Bean 0573, `.agents/invariants.yml`) lists these hard rules as `missing` or `partial` with no
dedicated bean. Parent: Bean 0562.

## Gaps

- Sole change path: no check that a target-repository change came from a flow (for example a server-side ruleset that
  rejects pushes to non-flow branches, plus a PR-body gate).
- Default Holon coding model and the Subagents model tiers: no gate that a launch used the named ladder.
- Never merge a PR that targets `main`: no server-side guard (branch protection requiring a human reviewer).
- Tests only via `uv run pytest`: no scan of skills, scripts and docs for bare `pytest`, `unittest` or `PYTHONPATH`.
- Flow concurrency and merge backfill: no counter that refuses a fifth concurrent flow.
- Coordinator failure ledger: format is checked, but not that every halt, park or wasted run produced a row.
- Self-improvement audit: ordering is checked, but not that one ran at session start or after every fifth merge.
- Git hooks: installed by hand until the installer is run; no check that a clone has them.

## Check

Each gap gets its check, proven to fail on a reconstructed violation and to pass on the clean state, then its registry
entry moves to `enforced`.

## Common acceptance

- The check runs automatically; no agent has to remember it.
- Self-explaining code invariant in anything written: no docstrings, no comments except `# why:`.
- Target-repository work goes through `holon flow`; the intent never names harness paths or bean ids.
