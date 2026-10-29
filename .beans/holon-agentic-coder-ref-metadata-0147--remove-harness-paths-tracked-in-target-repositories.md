---
# holon-agentic-coder-ref-metadata-0147
title: "Remove harness paths (todo/, .subagent/) tracked in the target repositories"
status: in-progress
type: bug
priority: normal
tags:
  - harness-isolation
  - hygiene
  - holon-agentic-coder
  - holon-coherence
created_at: 2026-10-24T01:41:18Z
updated_at: 2026-10-30T02:00:00Z
---

## Problem

AGENTS.md item 12 says the target repositories must never know about harness directories or conventions (`.beans/`,
`todo/`, `.agents/`), and `.subagent/` falls under the same principle. The Stage 4 review loops of 2026-10-24 found
these tracked on `origin/main`:

| Repository          | Path                                                                         | Introduced by      |
| ------------------- | ---------------------------------------------------------------------------- | ------------------ |
| holon-agentic-coder | `todo/ab_measure_all_methods.py`, `todo/ab_real_api_results.{json,md}`       | PR #52 (`e87e017`) |
| holon-agentic-coder | `.subagent/.gitkeep`                                                         | PR #53 (`54a2af1`) |
| holon-agentic-coder | `docs/optimisation/token_reduction_ab_testing.md` points at a `todo/` script | PR #52             |
| holon-coherence     | `todo/mitm_wire_logs` default path in `mitm_addon.py` and `metrics.py`       | pre-existing       |

Both repositories also track `.agents/AGENTS.md`. That is the target's own agent guide, not the harness's, so it is out
of scope unless it references harness paths.

## Scope

- Move the A/B measurement script and results to a target-native location (for example `scripts/` and
  `holon-knowledge/`), or delete them if superseded, and update the doc that references them.
- Remove `.subagent/.gitkeep` and any `.subagent/` ignore or reference in the target.
- Change coherence's wire-log default to a target-native path (`.holon/` or similar), with a migration note.
- Add a hygiene test or pre-commit check in each target that fails if tracked files live under, or reference, `todo/`,
  `.subagent/` or `.beans/`.

## Notes

- Run through the Holon flow, once per target repository.
- Found by: PR #92 resolver iteration 3, PR #95 dry-run iteration 1, PR #27 dry-run iteration 5.

- **Bean ids in target code and docs (found 2026-10-27 during PR #97 review):** `main` also carries harness bean
  references in holon-agentic-coder source, CLI help and docs, for example `README.md:850,865` ("Bean 0034"),
  `apps/sandbox-executor/docs/hermetic_testing.md:7` ("Bean 0019"), `sandbox_executor/budgets.py:1` ("Bean 0139"), and
  `sandbox_executor/cli.py:1346,1402,1479,1547,2080,2084` (Beans 0139, 0049, 0092, 0140, 0118, the last one in
  user-visible `--help` text). Replace each with a plain description of the behaviour. Add a hygiene check that fails on
  `Bean [0-9]{4}` and on review-loop finding ids in target files. During PR #97, its review loop had already removed
  about 120 review-loop finding ids from lines the PR added.

## Progress (2026-10-29)

- **`holon-coherence` half — MERGED (PR #29):**
  - Flow: `I-1793246735-coherence-remove-harness-path-and-task-id-leaks` → `P-1793246750-claude-agent-claude-opus-5-5` →
    `E-1793246939-claude-agent-claude-opus-5-5` (worktree `apps/holon-coherence/flow-0147-remove-harness-path-leaks`).
  - PR #29 (https://github.com/Holon-Agentic-Coder/holon-coherence/pull/29): was in the Stage 4 review loop when it
    merged (superseded by the next bullet): iteration 6 resolver pushed `e1139ac`, and a calibration commit `e8e0833`
    followed, but no consensus review was posted.
- PR #29: ledger conflicts after PRs #28 and #30 resolved as `d83af38` (851 tests, 7/7 CI green); merged by the
  maintainer as squash `68fdf67` (2026-10-29T11:51:44Z) before its consensus review was posted. A post-merge review loop
  ran in `apps/holon-coherence/review-pr29-harness-leak-removal-post-merge`; its findings went to the hand-authored PR
  #31 (next bullet) rather than the follow-up flow first planned.
- **`holon-agentic-coder` half — TODO:** pending its own Holon flow run.

- **Post-merge review follow-up (2026-10-29):** holon-coherence PR #31
  (https://github.com/Holon-Agentic-Coder/holon-coherence/pull/31), hand-authored at the maintainer's explicit
  instruction, was in review iteration 10 at `add885c` (ensemble running) when first logged. The loop continued to
  iteration 18 (`52a843b`), and the maintainer squash-merged the PR as `b52c7e1` (2026-10-29T23:24:46Z).

- **`holon-coherence` half done (2026-10-30):** PR #29 (`68fdf67`) plus the post-merge follow-up PR #31, merged as
  `b52c7e1` after 19 review iterations (all CI green; merged during the last ensemble, so no consensus review was
  posted). Two documentation Nits left open are Bean 0211. The `holon-agentic-coder` half is still to do.
