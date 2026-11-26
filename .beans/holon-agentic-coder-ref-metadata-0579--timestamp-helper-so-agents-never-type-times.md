---
# holon-agentic-coder-ref-metadata-0579
title: "Timestamp helper: bean touch and ledger append read the clock, agents type no time"
status: todo
type: task
priority: high
tags:
  - harness
  - timestamps
  - tooling
created_at: 2026-11-26T23:51:36Z
updated_at: 2026-11-26T23:51:36Z
---

## Evidence

- CF-0020 recorded invented times; bean 0561 and the pre-commit check (`check_beans.py`, `timestamps.py`) landed
  afterwards, yet this session still saw bean 0572 `updated_at` at `00:00:00Z` and bean 0489 with a millisecond value
  (both caught only at commit time, one of them blocked another agent's commit; see 0577).
- Cause: every bean edit needs a hand-typed `updated_at` and every ledger row a hand-typed `created_at`; the agent has
  the clock only if it remembers to run `date -u`. The check detects after the fact and rejects, it does not remove the
  reason to type a time. `timestamps.py` has `utc_now()` but no command-line entry.
- Ledger category `bookkeeping` has repeated (CF-0007, CF-0010, CF-0020).

## Change

- `.agents/scripts/stamp.py` with subcommands: `touch <bean-id>` (rewrites `updated_at` from the clock),
  `create <id> <slug> ...` (fills `created_at`/`updated_at` and next sequential id), `ledger-append <category> ...`
  (next CF id, `created_at` from the clock, validates the row before appending), `audit-entry` (heading time from the
  clock).
- Rules and briefs say: never edit a timestamp field by hand; run the helper.
- Pre-commit failure message names the helper command.
- Test: helper output passes `check_beans.py` and `check_failure_ledger.py`.

## Expected gain

Removes the cause of invented times and the refused commits they trigger; shorter briefs. Cost: one small script and its
tests.
