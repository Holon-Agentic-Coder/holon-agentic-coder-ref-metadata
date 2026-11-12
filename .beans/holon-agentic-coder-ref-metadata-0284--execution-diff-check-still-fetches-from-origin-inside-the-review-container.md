---
# holon-agentic-coder-ref-metadata-0284
title:
  "The execution-diff check still fetches from origin inside the review container; Stage 4 fails again after Bean 0282"
status: completed
type: bug
priority: critical
tags:
  - flow
  - review-loop
  - sandbox
  - holon-agentic-coder
created_at: 2026-11-12T03:10:00Z
updated_at: 2026-11-12T04:10:00Z
---

## Problem

PR #171 (Bean 0282) stopped `review_target._fetched_branch_ref` and the reviewed-commit lookup from fetching in a
mounted role container, but `flow/git_refs._execution_effective_diff` (called by `classify_review_diff` for execution
branches at the start of Stage 4) still runs `git fetch` of the plan and execution branches whenever an origin remote
exists. The review-loop container has no `ssh`, so the `ids` and `creds` flows (Beans 0278 and 0224) fail again at Stage
4 with `could not verify the execution diff (fetching '<P>/_' and '<E>/_' from origin failed: cannot run ssh)`,
confirmed independently by both flow agents on 2026-11-12 with the images rebuilt from `main` at `5d30bda`.

## Action

Run through the Holon flow, Stage 4 and 5 driven from the host by hand because Stage 4 is the stage under repair
(maintainer authorised). In a mounted workspace `_execution_effective_diff` must not fetch: it resolves the refs the
host fetched (`refs/remotes/origin/...`) and refuses with a message naming the branch when one is missing; the host
fetch before dispatch (Bean 0282) already provides them. Audit every other `_fetch_refspecs_error` / `git fetch` caller
reachable from the review-loop container and give each the same mounted-workspace rule, with hermetic tests that no
`ssh` is invoked in the container path. Host (unmounted) behaviour is unchanged.

## Follow-up

After it merges: rebuild images (`install-holon --holon-only`) and resume anything still on hold.

## Resolution

Delivered via [PR #172](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/172) and merged into `main`
(`0181186`, 2026-11-12):

- **Key Architectural Deliverables**: `flow/git_refs._execution_effective_diff` no longer fetches from origin in a
  mounted role container; it compares the refs the host fetched and reports an unverifiable result naming the missing
  branch. With Bean 0282 this closes the in-container fetch on the Stage 4 review path.
- **Verification & Tests**: hermetic tests for the mounted and host paths; review loop 4 iterations to a clean 3/3 at
  `60b4bcf`, CI green at the merged head.
- **Holon Flow Traversal**: Intent, Plan and Execute ran in the engine on `claude-sonnet-5-5` with
  `HOLON_TOKEN_REDUCE=0`. Stage 4 failed in-container on the bug repaired, so the review loop and `holon calibrate` were
  driven from the host (maintainer authorised). Calibration: predicted EV 52.45, actual EV -9.29, delta -61.74.
- **Follow-up**: Stage 4 should now run in the container; the next flow is the first real proof. The two earlier
  host-driven calibration deltas (about -55 to -62) are all negative and worth a look in the calibration beans.
