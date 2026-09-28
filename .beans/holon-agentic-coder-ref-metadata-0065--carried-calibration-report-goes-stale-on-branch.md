---
# holon-agentic-coder-ref-metadata-0065
title: "The calibration report carried on the execution branch silently goes stale as review commits land"
status: todo
type: bug
priority: normal
tags:
  - flow
  - calibration
  - review-loop
  - provenance
created_at: 2026-10-03T12:10:00Z
updated_at: 2026-10-03T12:10:00Z
---

Stage 5 measures the change, and `be01f21` (PR #61) also **carries that measurement on the execution branch itself**, as
`plans/P-…_calibration.md`, so the report ships inside the PR diff. Once committed it is a frozen snapshot of a branch
that keeps moving: the review loop lands commits afterwards, and **nothing regenerates the carried copy and nothing can
detect that it went stale** — the report records an `Evaluation Timestamp` but **no head SHA**, so the file cannot even
be checked against the tree it describes. The merged history therefore contains a flow self-report that contradicts the
flow's own diffstat.

## Measured evidence (PR #61, merged 2026-10-03 as `7ef651c`)

The carried report was generated at `be01f21` (`2026-09-28T07:51:00Z`), before review commits `c0bdc52..496d7b6` grew
the branch:

| Field                    | Carried on the branch | Truth at `496d7b6`      |
| ------------------------ | --------------------- | ----------------------- |
| Files modified (SSA obs) | `7` → SSA `5.9`       | **`13` → SSA `10.0`**   |
| Entropy $\Delta S$       | `1.80` (err `0.90`)   | **`3.04` (err `2.14`)** |
| Accuracy rating          | `High (≤ 1.0)`        | **`Moderate`**          |
| EV actual                | `73.76`               | **`73.39`**             |
| $\Delta EV$              | `+3.78`               | **`+3.41`**             |

It was fixed only by hand, at the operator's explicit instruction, in commit `a614938` (1 file, `+6 −6`, pushed as a
fast forward, CI 10/10). `run_calibrate()` is deterministic ledger arithmetic with **no model call**, so regenerating is
free and exact: a fresh run at `496d7b6` reproduced the `/calibrated` record (`ad95cd2`) differing by exactly one line,
the timestamp. The cost of the manual fix was a new head on an already-approved PR plus a full CI cycle — all of it
avoidable.

Note the direction of the error: the stale report **flattered** the run. It understated entropy by 68% on a PR that took
thirteen review iterations, and the accuracy rating it earned itself (`High`) was one the true numbers do not support.

## Why this is not Bean 0054 or Bean 0060

Both concern **generating** the report; neither concerns **invalidating** one that was correct when written.

- **Bean 0054** — `holon calibrate` cannot run at the moment `STAGE_ORDER` calls for it, because merging deletes the
  `E-…` branch. Availability of stage 5. (Still live: the `E-…` branch of PR #61 was in fact deleted on merge.)
- **Bean 0060** — `holon calibrate` resolves branch names against stale **local refs**, so it can score the wrong change
  at the instant it runs. Input freshness.
- **This bean** — the report is generated correctly and then becomes false underneath itself, because the execution
  branch advanced after stage 4 landed commits. No fetch fixes this, and no run-ordering fixes this; only regeneration
  or an invalidation check does.

## Acceptance criteria

1. The report records the **head SHA it measured**, not only a timestamp.
2. Staleness is then mechanically detectable, and is acted on: either the review loop **regenerates the carried report
   as its last action** before declaring the PR ready, or the merge boundary refuses a carried report whose recorded SHA
   is not the branch head.
3. Alternatively, stop carrying it on the execution branch and treat `…/calibrated` as the single source of record — but
   note PR #61's rationale for carrying it was review visibility, so this needs an explicit decision, not a default.
4. A test that fails if a carried report's recorded head differs from the branch head it is committed on.

## Notes

- Target repository: `holon-agentic-coder`; every change to it goes through the five-stage flow
  ([AGENTS.md](../AGENTS.md), "Sole Change Path"). This bean was logged from the harness because the harness is not
  reachable by the flow.
- Today's manual refresh (`a614938`) is a **one-off repair, not a mechanism** — PR #62 will reproduce this defect.
- The `/calibrated` branch for PR #61 is preserved locally as tags `pr61-calibration-final` (`ad95cd2`) and
  `pr61-final-reviewed-head` (`a614938`). Its remote ref is knowingly stale at `a41627b`: publishing the current commit
  would require a force-push onto a flow provenance branch, which is prohibited.
- Related: bean 0019, bean 0054, bean 0060, bean 0063, PR #61.

## Resolution

Open.
