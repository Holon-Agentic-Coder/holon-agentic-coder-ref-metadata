---
# holon-agentic-coder-ref-metadata-0480
title: "A network outage at pre-flight ends the flow wrapper and the flow idles until someone relaunches it"
status: in-progress
type: bug
priority: high
tags:
  - flow
  - harness
  - preflight
  - resilience
  - holon-agentic-coder
created_at: 2026-11-26T05:25:00Z
updated_at: 2026-11-26T08:49:00Z
---

## Problem

The wrapper (`.agents/skills/holon_flow/scripts/run_holon_flow.py`) runs the engine pre-flight probe before every
relaunch, including every relaunch of the Stage 3 overlap poll. The probe retries a transient UNKNOWN only
`DEFAULT_MAX_ATTEMPTS = 3` times with a 2 s pause (`sandbox_executor/preflight.py:26-30,417-435`), so a network outage
of more than about three minutes ends the wrapper with exit 1. Nothing relaunches it: the flow sits idle until a person
or a later session notices.

## Evidence

Evidence: flow time audit of 2026-11-26 (git-ignored `todo/flow-time-audit-2026-11-26.md`, scripts and data in
`todo/flow-time-audit-2026-11-26/`), sample PRs #296 to #316 of holon-agentic-coder.

- 2026-11-25 about 06:24Z (DNS outage): `ledger-fragments-and-promotion` (Bean 0371) was polling a Stage 3 overlap; the
  relaunch printed "Pre-flight probe ... returned transient UNKNOWN on attempt 1/3 ... 2/3 ... UNKNOWN; The probe did
  not finish within 60s" and exited. Next relaunch: 22:52:42Z, **16.5 h** later.
- The same outage failed the `workspace-survival-job-parallel` resolver at 06:29:51Z ("API Error: Can't reach the API
  server ... ENOTFOUND", Bean 0424's class); its resume came at 23:11:31Z (**16.7 h**). The
  `calibration-merge-adapted-file` resync at 07:01:44Z then hit "Docker daemon is not running" (Bean 0466's class) and
  idled to 22:47:59Z.
- Idle after failures with no auto-resume is 2178 of 3260 measured flow-minutes in the sample (67 %): the time between a
  failure and a manual relaunch (this outage, plus 3 h on PR #308 after a `gh pr diff` HTTP 406 discovery failure, Bean
  0433).

## Proposed change

1. The wrapper classifies a pre-flight UNKNOWN whose cause is connectivity (DNS failure, connection refused or reset,
   probe timeout with no reply) as transient and waits with backoff (for example 30 s doubling to 5 min, up to 60 min),
   re-probing, before it gives up. The overlap poll does not re-run the model probe at all when the previous launch
   passed it less than an hour ago.
2. When it does give up, the wrapper exits with a distinct code that the flow supervisor (Bean 0396) treats as "relaunch
   from checkpoint later", not as a terminal failure, and the log says so with a timestamp.
3. Same policy for the engine's role-container failures (Bean 0424) and the Docker probe (Bean 0466), so one outage
   window is handled identically at every point of the flow.

## Expected gain

Turns a multi-hour idle after any outage into the outage's own length plus one backoff step. In this sample: about 16 h
on each of three flows.

## Cost

Small in the wrapper and `preflight.py` (classification and backoff loop); the supervisor hook depends on Bean 0396.

## Notes

- Not a duplicate of Bean 0393 (completed: 3 quick retries and the slow-exit OK case) or Bean 0466 (Docker probe only).
- One-off trigger (the outage), structural cost (no wait-and-resume).

## Progress

- 2026-11-26: in-progress. Flow `flow-preflight-outage-wait-resume` (intent
  `todo/intent-0480-preflight-outage-wait-resume.json`, slug `preflight-outage-wait-resume`), pre-flight scope only
  (wait and resume in `sandbox_executor/cli/preflight.py` via a new `preflight_outage.py`). Wrapper-side and stage-level
  parts are not in this flow.
- 2026-11-26 07:10Z: flow `flow-preflight-outage-wait-resume` (intent slug `preflight-outage-wait-resume`) completed
  Stages 1 to 5 with exit 0. PR #320, head 2ea483bb, consensus APPROVED 3/3 at review iteration 2 (iteration 1
  CHANGES_REQUESTED, fixed by the resolver), calibration report in the PR diff (EV 65.24), MERGEABLE/CLEAN. Human merge
  pending. Scope: `cli/preflight.py`, new `preflight_outage.py`, new test file. The resolver also added a public
  `is_model_error` to `sandbox_executor/preflight.py` (+4 lines, 548 to 552), outside the intent scope; it will trip the
  frozen override once the module-budget PR lands, so rebase or adjust before merging that one. Still open after this
  PR: the wrapper side (distinct exit code for a relaunch-later outcome, skipping the model probe in the overlap poll)
  and stage-level outages (Bean 0424 territory).
- 2026-11-26 08:49Z: PR #320 merged into `main` (`0cd63e0`, 08:46:12Z). `install-holon` rebuilt the images and
  reinstalled `holon` and `holon-coherence`. Flow worktree, its branches and `origin` branches removed.

## Resolution

Partly delivered via [PR #320](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/320), merged into `main`
(`0cd63e0`):

- **Pre-flight outage wait** (`sandbox_executor/cli/preflight.py`, new `preflight_outage.py`): a pre-flight UNKNOWN
  caused by DNS, connection refused or reset, network unreachable, Docker daemon or probe timeout is re-run with backoff
  (30 s doubling to a 300 s cap, giving up after 3600 s cumulative). Auth, quota, expired-key, not-logged-in,
  model-name, missing-CLI and unsupported-runner results never wait. A public `is_model_error` was added to
  `sandbox_executor/preflight.py`.
- **Verification**: hermetic `test_preflight_outage.py`. Flow `flow-preflight-outage-wait-resume` completed Stages 1 to
  5 (consensus APPROVED 3/3 at review iteration 2).

Still open (bean stays `in-progress`):

- Wrapper side: `run_holon_flow.py` exits with a distinct "relaunch from checkpoint later" code when the wait gives up,
  and the Stage 3 overlap poll skips the model probe when the previous launch passed it under an hour ago.
- Stage-level outages (Bean 0424 territory).
