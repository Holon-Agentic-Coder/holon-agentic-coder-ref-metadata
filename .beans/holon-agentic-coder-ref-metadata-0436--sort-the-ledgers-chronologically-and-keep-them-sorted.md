---
# holon-agentic-coder-ref-metadata-0436
title: "Sort the three ledgers into chronological order once, and keep them sorted"
status: in-progress
type: task
priority: high
tags:
  - ledger
  - flow
  - conflicts
  - holon-agentic-coder
created_at: 2026-11-24T23:15:00Z
updated_at: 2026-11-26T20:59:53Z
---

## Why

Maintainer, 2026-11-24: "create another bean to sort the ledgers in chronological order".

## Problem

The three append-only ledgers on `main` of holon-agentic-coder (`holon-knowledge/ledger/executions.jsonl`,
`intents.jsonl`, `plans.jsonl`) are not strictly in `created_at` order. Measured on `main` at 2026-11-24T23:12Z:

| Ledger             |  Rows | Adjacent rows out of order | Timestamp styles |
| :----------------- | ----: | -------------------------: | :--------------- |
| `executions.jsonl` | 8,832 |                         13 | `Z` and `+00:00` |
| `intents.jsonl`    |   205 |                          3 | `Z`              |
| `plans.jsonl`      |   206 |                          2 | `Z`              |

Every row has a `created_at`. The disorder comes from merges that appended one side's rows after the other's, and from
rows written with a `+00:00` offset next to rows written with `Z`, which sort differently as strings.

The cost was seen on pull request #275 the same day: resolving its ledger conflict, an agent interleaved the rows by
`created_at` as the harness rule says, and because `main`'s files were not already in that order the sort moved existing
rows. The pull request's diff showed 310 ledger lines removed and 418 added where a merge should only add, no row was
lost (verified), and every other open pull request touching the ledgers is set up to conflict over the moved lines. As
long as the base is unsorted, the rule "interleave by `created_at`" and the rule "append-only" contradict each other.

## Goal

1. **One-time normalisation on `main`**, through the Holon flow: sort each ledger by `created_at` parsed as a UTC
   datetime (not as a string), with a stable tie-break (the existing order within the same instant), and write every
   `created_at` in one canonical form (`Z`). The change is a pure reordering and reformatting: the set of rows is
   identical before and after, proved by a test or a check script that compares the parsed rows.
2. **Keep them sorted from then on**:
   - every writer (`record_*`, the ledger step, the reconcilers) writes `created_at` in the canonical form;
   - the conflict reconcilers (`flow/ledger_reconcile.py`, `flow/ledger_interleave.py`, `ledger/reconcile.py`) produce a
     merge that keeps the base's rows in place and only inserts the incoming rows, so a merge is additions only;
   - a hygiene check fails a pull request whose ledger diff removes or moves any row of `main`, or that leaves a ledger
     out of order.
3. **Timing**: the normalisation commit touches every row, so land it when few pull requests are open, and resolve the
   open ones once against it; say so in the pull request.

## Notes

- The one-time reorder is a deliberate exception to the append-only rule, authorised by the maintainer's request above.
  After it, the append-only rule holds without exception.
- Overlaps Bean 0371 (per-flow ledger fragments), which removes most ledger conflicts by design. This bean is smaller
  and independent: it makes the existing files and merges well-formed now, and stays useful if 0371 keeps the canonical
  files. If 0371 lands first, apply goal 1 to whatever canonical ledgers remain.
- Intent note for the flow: do not name harness paths or bean ids in the intent text.

- Progress (2026-11-25): the harness docs now say a ledger conflict keeps main's file in main's order and appends only
  the branch's rows. `.agents/skills/resolve_conflict/scripts/resolve_known.py` still inserts the branch's rows among
  main's by `created_at`; its code is unchanged, and it must keep main's order (append the branch's rows after main's)
  once this bean is done. `.agents/skills/holon_flow/scripts/run_holon_flow.py` also carries a prompt string saying
  "resolve ledger conflicts by chronological interleaving".
- Progress (2026-11-25): `resolve_known.py` now appends: main's ledger file is kept byte for byte and only the branch's
  new rows are appended, sorted by `created_at` (UTC, `Z` or `+00:00`); the flow prompt string was reworded to match;
  tests in `tests/test_resolve_known.py`.

- Flow started 2026-11-26T12:04Z: `ledgers-sorted-chronologically` (intent
  `todo/intent-0436-ledgers-sorted-chronologically.json`, log `todo/flow-ledgers-sorted-chronologically.log`,
  claude-agent / claude-opus-5-5). Scope: normalise script, three canonical ledgers, three reconcilers; writers left out
  (follow-up).

- 2026-11-26T14:08Z: flow `ledgers-sorted-chronologically` produced PR #342: 3/3 consensus at review iteration 6 (after
  a code conflict in `flow/__init__.py` resolved via resolve-conflict and a rerun from review), calibrated,
  MERGEABLE/CLEAN, green CI. Awaiting maintainer merge. Not in scope and still open: writers of `created_at` (many
  review modules) to canonical `Z` form; keep the bean open for that remainder.

- 2026-11-26T20:58Z: PR #342 merged into `main` (`57a8aa38`). `scripts/normalise_ledgers.py --check` exits 0 on `main`;
  the three conflict reconcilers keep the base's rows in place and insert only the incoming rows. Bean stays in-progress
  for the remaining scope: `created_at` writers in the review modules (canonical `Z` form).
