---
# holon-agentic-coder-ref-metadata-0422
title:
  "An --allow-overlap override is sticky: kept in the checkpoint and inherited by every later sub-intent and resume"
status: todo
type: bug
priority: high
tags:
  - flow
  - admission
  - holon-agentic-coder
created_at: 2026-11-24T12:58:00Z
updated_at: 2026-11-25T03:08:00Z
---

## Problem

`holon flow --allow-overlap` is meant to admit one refused Stage 3 run. The engine stores it in the checkpoint and never
clears it:

- `cli/commands/flow.py:259`:
  `context.allow_overlap = bool(context.allow_overlap or getattr(args, "allow_overlap", False))`, so a resume without
  the flag keeps a value loaded from the checkpoint (`flow/context.py:221` and `:262`).
- `flow/stages/children.py:76` copies it into every decomposed child.

## Evidence (self-improvement audit, 2026-11-24T12:58Z)

- Every checkpoint of the `resolve-conflicts-in-flow` flow (Bean 0376) holds `"allow_overlap": true` (the main
  checkpoint and sub-intents 1 to 4); only `checkpoint-parent.json` holds `false`. The running wrapper (launched
  2026-11-24T10:46Z from the Antigravity session) passes no `--allow-overlap`.
- Sub-intent 4 (PR #273) was admitted at 11:12Z with `override: true` over two flows that did not exist when the
  override was first given: PR #270 (`tests/flow/test_git_refs.py`) and the live local flow of Bean 0405
  (`tests/flow/stages/test_decomposition.py`, `tests/test_calibrate_rerun.py`), launched from the other agent session.
- Consequences in this period: PR #273 and PR #275 now both change `tests/test_calibrate_rerun.py`, so whichever merges
  second gets a code conflict; and admission, which treats #273 as in flight, keeps Bean 0399 refused since 11:42:16Z.

## Goal

- An override admits exactly the run it was given to. It is not written back as a standing flag; the checkpoint records
  the overridden conflicts (already done) for the record only.
- A resume or a child re-checks admission without an override unless the flag is passed again.
- A regression test: a checkpoint saved with `allow_overlap` true, resumed without the flag against a new overlapping
  flow, is refused.

## Notes

- Same class as completed Bean 0356 (resume inherited `--skip-review` and the agent from the checkpoint).
- Related: Bean 0423 (two sessions launching flows in one workspace), Bean 0395 (work during the overlap wait).
- Through the Holon flow (target change).

## Audit evidence, 2026-11-25T00:28Z (self-improvement audit, fifth merge)

- **14 of 23** active `holon-agentic-coder` flows in the `2026-11-24T12:59Z–2026-11-25T00:19Z` window ran with
  `allow_overlap=True` in their checkpoints, contributing to `main`-merge churn (e.g. `PR #292`: 4 merges, `PR #293`: 3
  merges, `PR #296`: 3 merges plus an unresolvable conflict in `cli/__init__.py` against `PR #276`).

## Audit evidence, 2026-11-25T02:54Z (self-improvement audit, fifth merge)

- **11 of 13** `holon-agentic-coder` checkpoints active in `2026-11-25T00:28Z–02:54Z` (`split-cli-init-modules`,
  `touch-set-self-doc`, `in-flight-pr-files-fallback`, `decomposition-rule-self-doc`, `preflight-self-doc`,
  `review-report-self-doc`, `agent-defaults-self-doc`, `github-ci-self-doc`, `git-refs-self-doc`,
  `github-pr-merge-self-doc`, `github-misc-self-doc`) ran with `allow_overlap=True` (triggered by the `#283` HTTP 406
  storm; see Bean `0433`).
