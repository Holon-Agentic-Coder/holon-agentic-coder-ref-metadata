---
# holon-agentic-coder-ref-metadata-0151
title: "Planner estimates the files a change will touch, and overlapping flows are blocked from running concurrently"
status: in-progress
type: feature
priority: critical
tags:
  - holon-flow
  - concurrency
  - planning
  - token-cost
  - holon-agentic-coder
created_at: 2026-10-25T07:34:25Z
updated_at: 2026-10-26T04:22:09Z
---

## Problem

Running several flows concurrently on overlapping files costs more than running them one after another. Each merge to
`main` forces every open overlapping PR to sync. Each sync moves the PR head past its approval, so the whole review loop
(dry run, 3-reviewer ensemble, resolver, re-post) has to run again. Each further merge repeats this for the PRs still
open.

### Evidence (2026-10-23 to 2026-10-25, holon-agentic-coder PRs #94, #95, #96)

All three changed `sandbox_executor/flow.py` and `sandbox_executor/cli.py`; #94 and #96 also both changed
`local_llm.py`. #90 and #93, which merged during the run, touched the same files.

| PR  | Syncs with `main`            | Review-loop passes from its first sync onward |
| --- | ---------------------------- | --------------------------------------------- |
| #94 | 4 (after #90, #93, #96, #95) | 43, plus a fourth sync still in progress      |
| #95 | 3 (after #90, #93, #96)      | 62                                            |
| #96 | 1 (after #90 and #93)        | 36                                            |

That is 141 review-loop passes from the first sync onward. At about 70k–180k tokens per subagent pass, that is around
10M+ tokens. Every sync also had to reconcile semantic overlap by hand:

- `holon doctor` was implemented twice.
- #94's and #96's URL redaction had to be reconciled.
- #95's container dispatch versus #94's stage-budget hand-down.

Some post-sync passes did catch real defects that only appeared once another PR's code arrived (for example #93's
pre-flight argv leak inside #96). That interaction would also have been caught, more cheaply, by building the second PR
on top of the first.

Ledger append conflicts (`holon-knowledge/ledger/*.jsonl`) are out of scope. They are mechanical to resolve as exact
unions, and the maintainer chose to keep the ledger layout.

## Scope

1. **Estimate (Stage 2, planner):** the planning agent writes an estimated touch set: every file or glob it expects to
   create, modify or delete, and the main symbols it expects to change in very large modules. It goes in the plan file
   (a machine-readable section) and in the `plans.jsonl` row (a `touch_set` field, documented in
   `docs/ledger_schema.md`). Flow metadata (`plans/`, `executions/`, ledgers) is excluded.
2. **Admission (before Stage 3, hard block):** before an execution worktree or container starts, compare the touch set
   with:
   - the declared touch set of every in-flight flow (open flow PRs and executions running locally);
   - the actual changed files of every open flow PR (`gh pr diff --name-only`).

   On any overlap, **refuse to start**. Stage 3 fails fast with a clear message naming the conflicting PR or branch and
   the overlapping files, before any agent tokens are spent. The default is sequential: the operator reruns once the
   blocking PR merges, and then plans on top of the new `main`. An explicit override flag (for example
   `--allow-overlap`) exists for deliberate exceptions, and its use is recorded in the ledger.

3. **Enforcement (after Stage 3):** if the real diff changes files outside the declared touch set (ignoring flow
   metadata), the stage fails, or the run goes back to re-planning with the touch set widened and admission re-checked.
   This keeps the estimate honest and sits next to the empty-diff guard (#95).
4. **Calibration (Stage 5):** record the predicted touch set against the actual one (precision and recall) in the
   calibration report and metrics, so estimation quality is measured over time.
5. **Harness orchestration:** the harness rule is not to launch concurrent flows whose touch sets overlap. Add this to
   `.agents/workflows.md` / AGENTS.md once the target supports it, and follow it by hand until then.
6. **Tests:** overlap against declared sets, against open-PR diffs and against local in-flight executions; the override
   flag; out-of-set enforcement; no false blocks for metadata-only overlap. Tests must never call real `gh`, which the
   suite's write guard already enforces.

## Notes

- Run through the Holon flow on holon-agentic-coder.
- Related: Bean 0152 (decompose oversized functions, split `flow.py` and `cli.py`). Until that lands, most work overlaps
  on those two files, so admission will correctly make most flows sequential. 0152 is what brings parallelism back.
- Related: Bean 0149 (unique plan and execution IDs), needed so in-flight flows can be identified reliably.

- **2026-10-26 flow run (claude-agent, runner from `fix/0143`):** intent
  `I-1792988604-touch-set-estimate-and-overlap-admission/_` and plan `P-1792988757-claude-agent-claude-opus-5-5` (EV
  19.82, entropy 12.6, touch-set design included) pushed. Stage 3 halted on Bean 0159 (executor ignores the intent
  entropy budget and fabricates placeholder sub-intents). Blocked by 0159; re-plan on `main` after it merges. Logs
  `todo/logs/0151-flow*.log`, intent `todo/intent-0151-touch-set-admission.json`.

## Resolution
