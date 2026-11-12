---
# holon-agentic-coder-ref-metadata-0282
title: "The Stage 4 review fetches from origin inside the container, which has no ssh; every flow fails at review"
status: completed
type: bug
priority: critical
tags:
  - flow
  - review-loop
  - sandbox
  - holon-agentic-coder
created_at: 2026-11-12T02:00:00Z
updated_at: 2026-11-12T03:00:00Z
---

## Problem

The Stage 4 review runs in the `review-loop` role container. Its diff check (`review_target.classify_review_diff` ->
`_fetched_branch_ref` -> `flow/git_refs._fetch_refspecs_error`) runs `git fetch` from `origin` whenever an origin remote
exists. `origin` is the ssh URL and the container has no `ssh`, so the fetch fails with
`error: cannot run ssh: No such file or directory` / `fatal: unable to fork` and Stage 4 refuses to create or update the
PR ("could not verify the execution diff"). Seen on the `ids` flow (Bean 0278) on 2026-11-12 on every resume, with the
host environment correct (`/usr/bin/ssh` present, `git ls-remote origin` fine from the host). The host already fetches
branches before dispatch (the `creds` flow reported "the host fetches it before dispatch"), so the in-container fetch is
redundant as well as impossible.

## Action

Run through the Holon flow, with Stage 4 and Stage 5 driven from the host by hand because Stage 4 is the stage under
repair (maintainer authorised, 2026-11-12). In a mounted workspace (the role container) the review code must not fetch
from origin: it resolves the refs the host fetched, and the host fetches the plan, execution and base branches before
dispatching the review container. Without a mounted workspace the behaviour is unchanged. Hermetic tests cover both
paths; the container path must never invoke `ssh`.

## Follow-up

After it merges: rebuild images (`install-holon --holon-only`), then resume the `ids` flow (Bean 0278) and the `creds`
flow (Bean 0224) from the review stage and close PR #169's stray state as the engine sees fit.

## Resolution

Delivered via [PR #171](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/171) and merged into `main`
(`5d30bda`, 2026-11-12):

- **Key Architectural Deliverables**: in a mounted-workspace role container the review diff path no longer fetches from
  origin; the host fetches the plan, execution and base branches before dispatching the review-loop container.
- **Verification & Tests**: hermetic tests for the container and host paths; review loop 5 iterations to a clean 3/3 at
  `09c77e5` (21 Nits applied, 5 rejected with reasons), CI green.
- **Holon Flow Traversal**: Intent, Plan and Execute ran in the engine on `claude-sonnet-5-5` with
  `HOLON_TOKEN_REDUCE=0`. Stage 4 failed in-container on the very bug repaired, so the review loop and `holon calibrate`
  were driven from the host (maintainer authorised). Calibration: predicted EV 42.50, actual EV -13.81, delta -56.31.
- **Other findings**: the token-reduction proxy's `cache_control` injection makes `claude-sonnet-5-5` planner calls fail
  with an API 400 that the engine writes into the plan file; `HOLON_TOKEN_REDUCE=0` is the workaround until Beans 0227
  and 0157 land. Worth a bean for failing loudly on an API error instead of treating it as a plan.
