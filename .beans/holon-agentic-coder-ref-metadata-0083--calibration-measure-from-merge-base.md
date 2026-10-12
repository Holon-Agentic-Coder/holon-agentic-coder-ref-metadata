---
# holon-agentic-coder-ref-metadata-0083
title: "Calibration measures from merge base so a main-sync merge cannot inflate actual metrics"
status: completed
type: task
priority: high
tags:
  - calibration
  - holon-flow
  - metrics
  - ledger
  - holon-agentic-coder
created_at: 2026-10-10T04:10:00Z
updated_at: 2026-10-12T18:40:00Z
---

## Summary

`parse_actual_metrics` in `apps/sandbox-executor/src/sandbox_executor/calibration.py` computes patch size with a
**two-dot** diff:

```python
diff_args = ["git", "diff", "--shortstat", f"{base_ref}..{target_ref}", "--"]
```

with `base_ref = plan_branch` and `target_ref = execution_branch`. That is correct only while the execution branch is a
straight line from the plan branch. When a flow branch falls behind and must be synced with `main` to become mergeable —
which is routine, and happened to PR #69 — the merge commit drags the whole of `main`'s intervening churn into the
measurement, and the ledger records somebody else's work as this execution's output.

Measured on PR #69 at head `609bb0b` (a forward merge of `origin/main`, which had gained Beans 0078/0064):

| Diff                                                | Result                    |
| --------------------------------------------------- | ------------------------- |
| `dd9078f..609bb0b` (two-dot, what calibration uses) | **36 files, +1186, −563** |
| `dd9078f..9e11928` (pre-merge execution head)       | **4 files, +298, −4**     |

`files_changed` and the insertions feed `ssa_obs`, which feeds `entropy`, which feeds `ev` — so a single main-sync merge
silently corrupts the EV accounting that the whole pipeline exists to produce.

## Requirements

1. Measure from the merge base (`git diff --shortstat $(git merge-base base target)..target`, or the three-dot form)
   rather than two-dot, so imported history is excluded by construction.
2. When the target branch contains merge commits that bring in other history, say so in the calibration report: record
   the base SHA used, the merge-base SHA, and the count of merged-in commits, so the number is auditable after the fact.
3. Keep the existing fail-loudly behaviour on a non-zero git exit, and keep the `target~1..target` fallback.
4. Tests: a fixture where the execution branch carries a merge of a third branch that changes unrelated files, asserting
   the reported patch size covers only the execution's own changes, plus a regression test that the pre-merge linear
   case is unchanged.

## Interim guidance for operators (until this lands)

Before running `holon calibrate` on any execution branch that has been synced with `main`, check the diff honestly:

```bash
git diff --shortstat <plan_commit>..<execution_head> --    # what calibration will record
git diff --shortstat <plan_commit>..<pre_merge_head> --    # what actually happened
```

If they differ materially, calibrate against the pre-sync head rather than recording inflated metrics.

## Origin

Raised by the orchestrator during iteration 3 of the PR #69 review loop, recorded as finding `O1` in
`.subagent/holon-agentic-coder_pr69_coordination.json`.

## Measured evidence (PR #69, Stage 5, 2026-10-10)

`./holon calibrate <execution_branch> --no-commit --json` against the post-sync head:

```
actual: files_changed 37, insertions 1677, deletions 568
```

The honest contribution of the same branch, `git diff --shortstat $(git merge-base origin/main 9e11928) 9e11928`:

```
7 files changed, 734 insertions(+), 4 deletions(-)
```

The merge commit alone (`git show 609bb0b --stat`): **35 files, +901/-572**. So the recorded run is ~2.3x on insertions
and ~5x on file count, and the excess is the merge, not the work. The `/calibrated` branch was therefore **not**
created: an EV record whose `actual` is dominated by an infrastructure merge is not a measurement, and it is append-only
once written.

Largest delta in the run is the useful one: `entropy_error 2.84`, driven by `ssa` predicted **0.6** against observed
**10.0** — spec ambiguity was understated by more than an order of magnitude, which is exactly what fourteen review
iterations on a two-check PR means. `delta_ev` of 0.05 says nothing about that. Fix the measurement basis first (this
bean); the spec-ambiguity miss is the finding worth carrying forward.

## Resolution

Executed as part of a batched Holon flow together with Bean 0086 on `holon-agentic-coder`:

- **Intent**: `I-1791787565-calibration-merge-base-and-docker-probe-unusable/_`
- **Plan**:
  `I-1791787565-calibration-merge-base-and-docker-probe-unusable/P-1791787590-antigravity-agent-gemini-3.8-flash-medium/_`
- **Execute**:
  `I-1791787565-calibration-merge-base-and-docker-probe-unusable/P-1791787590-antigravity-agent-gemini-3.8-flash-medium/E-1791788331-antigravity-agent-gemini-3.8-flash-medium/_`
- **Pull Request**: [PR #70](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/70)
- **Review Loop**: 3-agent ensemble review passed with unanimous `APPROVED` verdict; 10/10 GitHub Actions CI checks
  passed.
- **Stage 5 (Calibration)**: Executed pre-merge against execution branch
  `E-1791788331-antigravity-agent-gemini-3.8-flash-medium`. Measured actual EV: 80.11 vs predicted EV: 78.76 (ΔEV:
  +1.35). Base SHA: `b63a949`, merge-base SHA: `b63a949`, merge count: 0 recorded.
- **Calibrated Branch**:
  `I-1791787565-calibration-merge-base-and-docker-probe-unusable/P-1791787590-antigravity-agent-gemini-3.8-flash-medium/E-1791788331-antigravity-agent-gemini-3.8-flash-medium/calibrated`
  pushed to origin.
- **Merged**: PR #70 merged into `origin/main` on 2026-10-12 (merge commit `5214e6f763e94ce54459e224e6a78d989f4a80b6`).
