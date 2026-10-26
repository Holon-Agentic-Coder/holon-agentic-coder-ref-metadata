---
# holon-agentic-coder-ref-metadata-0134
title: "holon flow dispatches no role agent and produces empty-diff pull requests"
status: completed
type: bug
priority: high
tags:
  - holon-flow
  - cli
  - orchestration
  - provenance
created_at: 2026-10-22T02:40:00Z
updated_at: 2026-10-26T02:33:21Z
---

## Problem

`holon flow <intent.json>` drives the branch, ledger, PR, review-loop and calibration machinery, but **never dispatches
a role agent**, so it cannot author a change. A complete run reports `INTENT/PLAN/EXECUTE/CALIBRATE: SUCCESS` while
producing an execution branch with zero source lines changed.

Evidence on `holon-agentic-coder` `origin/main` (`3bef6f7`):

- `apps/sandbox-executor/src/sandbox_executor/flow.py` contains no reference to `run_docker_container` (the helper that
  launches role agents). The per-stage commands do: `cli.py:2106-2121` dispatches `holon/agent-<runner>` for `execute`,
  and `cli.py:2088-2105` for `plan`/`intent`.
- The plan stage writes a hard-coded template rather than asking the planner: `flow.py:2158-2176` emits
  `1. Implementation step for {slug}.` as the entire plan.
- The execute stage runs only `uv run pytest apps/sandbox-executor/tests/test_cli.py` and commits whatever is already in
  the tree: `flow.py:2366-2380`. No agent is invoked, so the commit is empty.

Reproduced on 2026-10-22: `holon flow todo/intent-0132-stage-4-5-ledger-actions.json` completed in 205 seconds (intent
5s, plan 5s, execute 5s), started no container, and pushed branches plus pull request
[#89](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/89) whose full diff is three ledger files, a stub
plan and a calibration report. The PR was closed by the harness; the empty branches (`I-1792634419-.../_`,
`.../P-1792634424-.../_`, `.../E-1792634429-.../_`, `.../calibrated`) are still on `origin`.

Two further consequences:

1. **The runner is documented as equivalent to manual invocation and it is not.** `AGENTS.md` ("Ordering ... whether the
   pipeline is driven by hand or by automation is irrelevant") and `.agents/workflows.md` present
   `holon flow <intent.json>` as a drop-in for stage-by-stage invocation. For authoring stages that claim is false, and
   an agent that trusts it will silently ship an empty PR that still carries a "success" ledger record and a calibration
   report.
2. **No guard against a no-op execution.** Stage 3 records `status: success` with `test_pass_rate: 1.0` even when the
   diff is empty, so a run that authored nothing is indistinguishable from a clean run in the ledger.

## Scope

- Decide and implement the dispatch contract: either (a) make the flow's intent/plan/execute stages dispatch the same
  containerised role agents the per-stage commands use (via `run_docker_container`), or (b) make the runner refuse to
  run authoring stages and fail loudly with a message pointing at `holon intent` / `holon plan` / `holon execute`.
- Never fabricate a plan document from a template. If no planner agent ran, the plan stage must fail, not write a stub.
- Add a stage-3 guard: an execution whose diff against the plan branch is empty must be recorded as a failure (and must
  not open or update a PR claiming success).
- Correct `AGENTS.md` and `.agents/workflows.md` in the harness so the documented equivalence matches whatever the
  implementation guarantees (harness files, edited directly, not flow-managed).
- Tests: a flow run with a stubbed dispatcher must assert the dispatcher is invoked for the authoring stages; an empty
  execution diff must produce `status: failed` and no PR creation.

## Acceptance criteria

- A `holon flow` run either produces the same authored diff as the manual five-stage invocation, or exits with a clear
  error instead of an empty PR.
- No plan document is committed that was not produced by a planner agent.
- `uv run pytest` passes in `apps/sandbox-executor`; harness docs match behaviour.

## Source

Observed directly during the 2026-10-22 attempt to execute Bean 0132 through `holon flow`. Related: Bean 0039 (pipeline
engine), Bean 0040 (single-command runner, whose re-scoped notes already record the runner as incomplete).

## Resolution

- **Pull Request**:
  [Holon-Agentic-Coder/holon-agentic-coder#95](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/95)
- **5-Stage Provenance**:
  - Intent: `I-1792765428-flow-dispatch-role-agents-and-empty-diff-guard/_`
  - Plan: `P-1792788551-claude-agent-claude-opus-5-5`
  - Execution: `E-1792788838-claude-agent-claude-opus-5-5`
  - Review: 3-agent ensemble consensus `APPROVED` (3/3) at `5e2aa6e` (review 5638047023) after 21 iterations. It was
    then synced with `main` after #96 (`8fd2d81`); that merge-verification dry run (iteration 22) was `APPROVED`. The
    maintainer merged before the follow-up 3-agent pass finished.
  - Calibration: report `cdc6639` plus Bean 0146 annotation `5a5e766` (Predicted EV 4.22 from the wrong row; Overall
    25.60 | Actual EV 4.39).
- **CI Status**: 10/10 passing, CodeQL 0 open alerts. Merged by the maintainer on 2026-10-25 as `b3e2727`.
- **Outcome**:
  - `holon flow` dispatches the role-agent containers for Stages 1–3.
  - An empty execution diff fails, and the guard refusal fails closed.
  - Unmeasured tests are recorded as `null`, never as a pass.
  - A bounded CI-registration wait is followed by a single `not_measured` stop.
  - `--skip-push` is rejected on every non-dry run.
  - A suite-wide test guard blocks real `gh` writes.
- **Follow-ups**: Bean 0144 (guard skipped for PR-number targets and without `--auto-pr`), Bean 0150 (tests write the
  real `action_index.db`).
