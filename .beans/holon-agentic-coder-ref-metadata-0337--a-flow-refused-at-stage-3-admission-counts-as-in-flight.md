---
# holon-agentic-coder-ref-metadata-0337
title: "A flow refused at Stage 3 admission still counts as in flight, so two waiting flows block each other forever"
status: completed
type: bug
priority: high
tags:
  - flow
  - stage-3
  - admission
  - concurrency
  - holon-agentic-coder
created_at: 2026-11-20T11:30:00+11:00
updated_at: 2026-11-20T15:37:23+11:00
---

## Problem

`local_in_flight_flows` (`flow/in_flight.py`) counts any flow whose checkpoint in another worktree sits at `execute` or
`review`. A flow refused at Stage 3 admission saves its checkpoint at `execute` (seen on `flow-resumetip`, 2026-11-20:
`current_stage: execute`, `completed_stages: [intent, plan]`) although it never ran an executor. Two flows that overlap
each other and are both refused therefore list each other as in flight, and neither is ever admitted. The harness runner
now waits out an overlap and re-checks admission (2026-11-20), so this turns into a silent deadlock when several flows
are started at once.

A second, smaller race: when an overlapping pull request merges, every flow waiting on it re-checks admission in the
same poll window, and two of them can be admitted together before either is visible to the other.

## Decision (maintainer, 2026-11-20)

A refused flow gets an explicit state of its own: **in flight but blocked**, with references to what blocks it. It is
not "in flight" for anyone else's admission, and it is not stopped.

## Action

Through the Holon flow on `holon-agentic-coder`:

- **Blocked state in the checkpoint.** A Stage 3 admission refusal for a touch-set overlap records
  `admission: {state: "blocked", blocked_by: [...], blocked_since: <timestamp>}`. Each `blocked_by` entry names its kind
  and reference: `{"kind": "pull_request", "number": 207, "branch": "..."}` or
  `{"kind": "local_flow", "plan_branch": "...", "worktree": "..."}`, with the overlapping files. An admitted flow
  records `state: "admitted"`.
- **Only admitted flows are in flight.** `local_in_flight_flows` skips checkpoints whose admission state is `blocked`. A
  blocked flow therefore blocks no one, and `blocked_by` only ever points at admitted flows or open pull requests, so no
  cycle (deadlock) can form. A flow with an open pull request stays in flight whatever its checkpoint says.
- **Ordered, atomic admission.** Admission runs under a per-repository file lock in the shared git directory, held from
  the check until the admitted state is recorded. When several blocked flows are clear, the oldest `blocked_since` is
  admitted first; the others re-check and see it.
- **Readable by tools.** `holon flow status` (or the checkpoint JSON) shows blocked flows and their blockers, so the
  harness runner polls exactly those references instead of parsing log text, and re-checks when a referenced pull
  request merges or closes or a referenced local flow leaves `admitted`.
- **Hermetic tests:** two mutually overlapping refused flows, one is admitted on retry and the other stays blocked by
  it; two simultaneous retries admit exactly one; a blocked flow does not appear in another flow's in-flight list; the
  `blocked_by` references are written and cleared correctly.

## Notes

- Related: Bean 0151 (touch-set admission), Bean 0331 (override record), Bean 0264 (`flow_module_budgets.json` makes
  most flows overlap).

## Progress

- 2026-11-20: Flow `blockedflow` started (claude-agent, claude-opus-5-5, worktree `flow-blockedflow`). Stage 1
  `I-1795138413-blockedflow/_`; Stage 2 `I-1795138413-blockedflow/P-1795138429-CLA-CO5.5/_` (EV 35.30). Stage 3 refused
  on PR #207 and on local flow `resumetip`; #207 merged at ~12:42, after which the bug this bean describes reproduced
  live: `resumetip` (refused 12:40:25, citing `blockedflow`) and `blockedflow` (refused 12:42:17, citing `resumetip`)
  each list the other as in flight, both checkpoints sit at `execute` with no executor run, and both runners re-check
  every 300 s forever. Deadlock; neither runner stopped. Breaking it needs a maintainer decision (e.g. admit `resumetip`
  with `--allow-overlap`, or stop `blockedflow` until `resumetip` opens its PR). Log: `todo/flow-blockedflow.log`.
- 2026-11-20 (14:44): The deadlock was broken outside this flow: `resumetip` opened PR #208, which merged, and
  `blockedflow` was admitted at 14:28. Stage 3 finished in 15.7 min (4471 tests passed) and pushed
  `I-1795138413-blockedflow/P-1795138429-CLA-CO5.5/E-1795145288-CLA-CO5.5/_` (e30ac9fe). The executor started from the
  plan tip cabbebff, which was cut before #207 and #208 merged, so the branch conflicts with origin/main in
  `flow_module_budgets.json`, `flow/__init__.py`, `flow/admission.py`, `tests/flow/stages/test_decomposition.py` and
  `tests/flow/test_admission.py`. Stage 4 stopped at once ("Unresolvable merge conflicts detected in stage 'review'").
  No PR is open yet. Blocked: merge origin/main into the execution branch, deciding how the `admission.py` and
  `__init__.py` changes from #208 combine with the new admission-state code, then resume with `--checkpoint`.

## Resolution

Delivered via [PR #209](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/209) and merged into `main`
(`7dc0342`) on 2026-11-20:

- **Blocked admission state**: a Stage 3 admission refusal for a touch-set overlap records
  `admission: {state: "blocked", blocked_by: [...], blocked_since: <timestamp>}`. Each `blocked_by` entry names its kind
  and reference (pull request or local flow) and the overlapping files. An admitted flow records `state: "admitted"`.
- **Only admitted flows are in flight**: `local_in_flight_flows` skips checkpoints whose admission state is `blocked`,
  so a blocked flow blocks no one and no admission cycle can form. A flow with an open pull request stays in flight.
- **Per-repository admission lock**: admission runs under a file lock in the shared git directory, held from the check
  until the admitted state is recorded. When several blocked flows are clear, the oldest `blocked_since` is admitted
  first.
- **Readable by tools**: blocked flows and their blockers are visible in the checkpoint and `holon flow status`, so the
  harness runner polls the named references and re-checks when they change.
- **Verification & Tests**: hermetic tests for mutual overlap, simultaneous retries admitting exactly one flow, blocked
  flows excluded from in-flight lists, and `blocked_by` write and clear. The flow's Stage 3 run passed 4471 tests (see
  Progress).
- **Holon Flow Traversal**: the `blockedflow` flow ran Stage 1 to Stage 3 (admitted 2026-11-20 14:28 local time after
  the overlapping flows merged), then its execution branch was merged with `origin/main` by hand and merged through PR
  #209.
