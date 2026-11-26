---
# holon-agentic-coder-ref-metadata-0466
title: "A flow stage that needs Docker aborts the moment the daemon is down instead of waiting"
status: todo
type: bug
priority: normal
tags:
  - flow
  - preflight
  - docker
created_at: 2026-11-25T22:49:00Z
updated_at: 2026-11-25T22:49:00Z
---

## Problem

Stage 5 of `calibration-merge-adapted-file` entered CALIBRATE at 07:01:44Z, then at 07:01:45Z the wrapper printed
"Docker daemon is not running. Please start Docker." and the run ended. The same log shows the daemon running at line 4
and line 310, so the daemon went away mid-run (an image rebuild or a restart; compare Bean 0402). The resume line says
"Pre-flight probe skipped: no remaining stage from 'calibrate' dispatches an agent runner", yet calibration still runs
containers, so the skip hides that Docker is needed.

## Evidence (self-improvement audit, 2026-11-25T22:49Z)

- `todo/flow-calibration-merge-adapted-file.log` lines 4, 310, 325 (PR #309, still open, `MERGEABLE`, approved head
  waiting for CI).
- `todo/flow-workspace-survival-job-parallel.log` lines 1078 to 1090: the daemon was back 12 s after the failure there,
  so the outage is short.
- Bean 0432 and the DNS bean cover resolver aborts; none covers the daemon check.

## Proposed change

- The Docker probe retries for a bounded time (for example 5 min at 15 s) before it fails the stage, and the probe runs
  for any remaining stage that starts a container, calibrate included.
- A failure after the wait names the stage so the flow resumes from it without redoing finished work.

## Expected gain and cost

Removes a manual resume for a seconds-long outage. Cost: a small retry loop in the wrapper pre-flight.
