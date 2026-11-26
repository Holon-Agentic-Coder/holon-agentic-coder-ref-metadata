---
# holon-agentic-coder-ref-metadata-0561
title: "Agents never hallucinate time: timestamps come from the clock, and a test proves it"
status: todo
type: bug
priority: high
tags:
  - harness
  - ledger
  - beans
  - timestamps
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-11-26T23:07:49Z
updated_at: 2026-11-26T23:07:49Z
---

## Instruction (maintainer, 2026-11-27 local)

"Create a bean so the agents never hallucinate the time. There should be a test to check that the agents never
hallucinate time."

## Evidence

At 2026-11-26T23:07:49Z (real UTC, from `date -u`):

- the newest entry in `.beans/self-improvement-audits.md` is stamped `2026-11-27T00:30:00Z`, after the real clock;
- coordinator failure ledger rows CF-0001 to CF-0009 are stamped `2026-11-27T00:00:00Z`, written before CF-0010
  (`2026-11-26T22:36:23Z`), so the file is out of order and in the future;
- several beans written today carry `created_at`/`updated_at` values such as `2026-11-27T00:20:00Z` (e.g. 0549,
  0550, 0560) that were made up rather than read from the clock.

The agents wrote the local date and an invented time, then labelled it UTC (`Z`). Post-merge agents counting "merges
since the newest audit" got 0 instead of 2, so audits and any "since" logic silently undercount.

## Rule

- Every timestamp an agent writes is read from the clock at write time (`date -u +%Y-%m-%dT%H:%M:%SZ`, or
  `datetime.now(timezone.utc)` in code) and is UTC with `Z`. Never typed, rounded, estimated or copied from another
  record. `session_date`-style local dates are labelled as local and never mixed with `Z` times.
- State it in `AGENTS.md` (hard rule), `.agents/rules.md`, the subagent git-safety/standing preamble
  (`.agents/subagents.md`), and every skill that writes a timestamp (post_pr_merge, holon_flow, self-improvement audit,
  bean writing in `workflows.md`).

## Tests (the guard)

A harness test, run by `uv run pytest` and the hygiene workflow, that fails when any agent-written timestamp is
hallucinated:

1. **Not in the future:** every timestamp in `.beans/*.md` frontmatter (`created_at`, `updated_at`),
   `.agents/ledger/*.jsonl` (`created_at`) and `.beans/self-improvement-audits.md` entries is <= now + 5 min skew.
2. **Not after its own commit:** for committed lines/files, the timestamp is <= the committer time of the commit that
   introduced it (`git log --format=%cI` / blame) + 5 min, and >= that commit time - a bounded window (e.g. 24 h for
   `created_at` of a new file), so a made-up value far from the real write time fails.
3. **Ordered:** append-only ledgers are non-decreasing in `created_at`; `updated_at` >= `created_at`.
4. **Format:** strict `YYYY-MM-DDTHH:MM:SSZ` UTC; round placeholder values (`T00:00:00Z`, `T00:30:00Z` patterns repeated
   across unrelated records) are flagged.
5. Wire the same checks into `.agents/scripts/check_failure_ledger.py` and the pre-commit hook, so a bad timestamp is
   refused at commit time, not only in CI.

Target repositories (via the holon flow, separately): the same not-in-future / not-after-commit / ordered checks on the
three append-only ledgers and KB records, as a hygiene test; the engine writes times only from the clock.

## Clean-up

- Correct the existing bad values to the real UTC write time (from the git commit that introduced each line/file),
  keeping append-only ledgers append-only by recording the correction as allowed by the validator (or a one-off
  correction commit authorised by this bean).

## Acceptance

- The test fails on today's evidence before the clean-up and passes after it.
- A new bean, ledger row or audit entry with a future or invented time is rejected at commit and in CI.
- Rule present in AGENTS.md, rules.md, subagents.md and the timestamp-writing skills.
- Related: Bean 0556, Bean 0559, CF ledger.
