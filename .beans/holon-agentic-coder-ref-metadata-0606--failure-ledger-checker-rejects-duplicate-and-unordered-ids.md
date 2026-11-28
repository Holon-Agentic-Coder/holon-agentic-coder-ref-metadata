---
# holon-agentic-coder-ref-metadata-0606
title: "Failure ledger has two rows with id CF-0028 and rows out of id order; the checker passes it"
status: completed
type: bug
priority: medium
tags:
  - harness
  - ledger
  - coordinator-failure
  - check
created_at: 2026-11-27T04:33:33Z
updated_at: 2026-11-27T04:37:15Z
---

## Evidence

- `.agents/ledger/coordinator-failures.jsonl` holds two rows with id CF-0028: the 00:30:35Z intent-scope row (PR #362)
  and a 03:40:00Z resume-checkpoint row (bean 0153 self-doc-src-j, host push rejected, second execution branch). The
  second sits after CF-0037 (03:27:32Z) and before CF-0038 (04:23:55Z), so ids are neither unique nor increasing, and a
  reference "CF-0028" is ambiguous (the 00:57Z audit entry cites CF-0028 for the intent-scope row).
- `check_failure_ledger.py` exists and is wired to pre-commit and CI (invariant "clock-read-utc-timestamps"), but it did
  not flag this; the clock check covers timestamps only.

## Goal

1. `check_failure_ledger.py` fails on a duplicate id, a gap or an id that does not follow the previous row, and on a
   created_at that goes backwards.
2. Renumber the later row to the next free id (CF-0039 or above, after confirming no other writer holds it) in a harness
   commit by the scribe, and add the id to refs that cited it.
3. The ledger writer (coordinator scribe) takes the next id from the file under a lock, so two agents appending at once
   cannot collide.

## Expected gain and cost

Gain: audits can cite rows unambiguously and flag repeats by id; Cost: a few checks in an existing script plus one test.
Low.

## Resolution

Checker now refuses duplicate ids and ids that do not continue from the highest id so far. Row 38 (CF-0028, the legacy
duplicate) is allowed only at its line via `KNOWN_LEGACY_DUPLICATES` in `check_failure_ledger.py`; the ledger was not
renumbered (append-only). `resume-checkpoint` and `wall-clock` were added to the category vocabulary because rows 38-39
use them. Goal 3 (locked next-id for ledger writers) is not implemented here and needs its own bean.

## Notes

- Source: self-improvement audit 2026-11-27. Related: 0550 (clock checks).
