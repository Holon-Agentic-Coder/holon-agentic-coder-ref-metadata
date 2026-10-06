---
# holon-agentic-coder-ref-metadata-0053
title: "Stop concurrent flow ledger collisions from silently dropping the whole CI signal"
status: completed
type: bug
priority: high
tags:
  - flow
  - ledger
  - ci
  - provenance
created_at: 2026-09-27T11:35:00Z
updated_at: 2026-10-06T11:30:00Z
---

Every Holon flow run appends to the same three files -- `holon-knowledge/ledger/{intents,plans,executions}.jsonl`. Two
flows in flight therefore conflict on those files and nothing else. GitHub builds `pull_request` jobs on the PR merge
ref; a conflicting PR has **no buildable merge ref**, so `Test - Unit`, `Test - Integration`, `Test - Hygiene` and
`Run Make` are skipped entirely, while the PR page still looks reviewable.

## Measured evidence (Bean 0019, PR #59)

- `gh pr view 59` reported `mergeable=CONFLICTING`, `mergeStateStatus=DIRTY` with **only** the three ledger files
  overlapping against `main` -- no source file conflicted.
- Only CodeQL reported during that window, because it runs on `refs/pull/59/head` (`dynamic` event) rather than the
  merge ref. The gap looks like "some checks ran, most silently did not", which reads as a workflow defect and is not
  one.
- Workaround applied by hand: merged `main` into the execution branch and resolved the ledgers by **union** (correct
  semantics for append-only JSONL) -- deduplicated, ordered by `created_at`, all lines valid JSON. Merge commit
  `ed7600e`, `parents: a855d5b c80ce35`; history extended, never rewritten.

## Why it matters

The failure mode is invisible in exactly the situation where test signal matters most: two agents landing overlapping
work. A flow branch can reach review with zero test coverage evidence and a green-looking check list.

## Candidate remedies (needs an owner decision)

1. Make the execute stage merge-and-union the ledgers before pushing, so the flow branch is never in conflict on them.
2. Shard the ledgers per run (`ledger/executions/<execution_id>.jsonl`) with a concat view for readers, so appends never
   touch the same blob.
3. Minimum viable guard: have the flow (or a CI job) detect `mergeStateStatus=DIRTY` and surface "test workflows are not
   running on this PR" instead of leaving it silent.

## Notes

- Discovered while closing Bean 0019 stage 4; recorded there as "systemic finding worth its own bean".
- Target repository: `holon-agentic-coder`, work under `apps/sandbox-executor/src/sandbox_executor/flow.py` and
  `executor.py`. Changes must go through the flow, not a host-side hand edit.

## Resolution

Resolved via the complete 5-stage Holon flow in Pull Request
[#66](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/66):

1. **Stage 1 (Intent)**:
   - Created Intent `I-1791281538-stop-ledger-collisions` and logged to `holon-knowledge/ledger/intents.jsonl`.
   - Pushed branch `I-1791281538-stop-ledger-collisions/_` to `origin`.

2. **Stage 2 (Plan)**:
   - Generated Plan `P-1791281550-antigravity-agent-gemini-3.8-flash-medium` via containerized `planner-agent`.
   - Logged in `plans.jsonl` and committed plan artifact
     `plans/P-1791281550-antigravity-agent-gemini-3.8-flash-medium.md`.
   - Pushed branch `I-1791281538-stop-ledger-collisions/P-1791281550-antigravity-agent-gemini-3.8-flash-medium/_` to
     `origin`.

3. **Stage 3 (Execute)**:
   - Executed plan via containerized `executor-agent` (Execution ID:
     `E-1791282286-antigravity-agent-gemini-3.8-flash-medium`).
   - Implemented deterministic JSONL union reconciliation utilities (`reconcile_ledger_file`, `reconcile_ledgers`,
     `reconcile_ledger_rows`) in `flow.py`.
   - Implemented pre-push divergence synchronization and automatic conflict reconciliation
     (`sync_and_reconcile_pre_push`) in `executor.py`.
   - Added mergeability validation guards (`check_pr_mergeability`) in `flow.py` to detect `DIRTY` / `CONFLICTING` merge
     states and prevent suppressed CI signals.
   - Committed and logged execution record `executions/E-1791282286-antigravity-agent-gemini-3.8-flash-medium.md`.
   - Pushed branch `I-1791281538-.../P-1791281550-.../E-1791282286-.../_` to `origin`.

4. **Stage 4 (PR Review Loop)**:
   - Opened PR [#66](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/66).
   - **Iteration 1**:
     - Dry-run review passed with `APPROVED` (0 🔴, 0 🟡, 1 🟢; 10/10 CI checks passing).
     - 3-agent ensemble review flagged 4 Important issues (defensive `None` handling for `ledger_revision`, post-merge
       global ledger reconciliation, GitHub CLI polling short-circuit, and shallow clone deepening).
     - Resolver subagent resolved all 4 issues, added defensive fallbacks, expanded unmerged conflict prefixes,
       implemented atomic file writes, added 7 unit tests, and pushed commit `582bffd`.
   - **Iteration 2**:
     - Dry-run review passed with `APPROVED` (0 🔴, 0 🟡, 0 🟢; 10/10 CI checks passing).
     - 3-agent ensemble review achieved unanimous approval: Reviewer 1 (`APPROVED`), Reviewer 2 (`APPROVED`), Reviewer 3
       (`APPROVED`) (0 Critical, 0 Important, 0 Nit; 10/10 CI checks passing).
     - Posted consolidated consensus approval review to PR #66 on GitHub
       ([receipt](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/66#pullrequestreview-5427648642)).

5. **Stage 5 (Calibration)**:
   - Ran `holon calibrate` against the execution branch.
   - Generated calibration report: Predicted EV: `83.18`, Actual EV: `85.20` ($\Delta\text{EV}: +2.02$).
   - Pushed `/calibrated` branch to `origin`: `I-1791281538-.../P-1791281550-.../E-1791282286-.../calibrated`.
   - Committed updated calibration report directly on top of PR #66 branch (`10d14d6`) and pushed to `origin`.

6. **Human-Only Merge Hand-off**:
   - In accordance with the immutable Human-Only PR Merging Invariant, all agent activity ceases upon posting approval
     and pushing calibration. Ready for manual human review and merge at
     https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/66.
