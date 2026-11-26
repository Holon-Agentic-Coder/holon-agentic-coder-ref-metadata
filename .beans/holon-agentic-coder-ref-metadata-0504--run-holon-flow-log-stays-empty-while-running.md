---
title: "run_holon_flow.py log file stays empty while the flow runs when stdout is redirected"
status: scrapped
type: bug
priority: normal
tags:
  - harness
  - holon-flow
  - observability
created_at: 2026-11-26T10:12:00Z
updated_at: 2026-11-26T10:12:00Z
---

# run_holon_flow.py log file stays empty while the flow runs when stdout is redirected

## Problem

Bean 0475 (flow `flow-docker-build-concurrency-group`) was launched with
`run_holon_flow.py ... > todo/flow-docker-build-concurrency-group.log 2>&1`. For the whole run (about 20 minutes,
through intent, plan, execute, review and calibrate) the log file stayed at 0 bytes. The complete summary appeared only
when the process exited. The checkpoint and `.subagent` state were written correctly, so the flow itself was running.

The wrapper does not set `PYTHONUNBUFFERED` for itself and does not flush its own prints (grep of
`.agents/skills/holon_flow/scripts/run_holon_flow.py` for `PYTHONUNBUFFERED`, `flush` and `-u` returns nothing), so
Python block-buffers stdout when it is redirected to a file. Monitoring a live flow through its log is therefore blind
until the end.

## Proposed Change

1. Have `run_holon_flow.py` write its progress lines with `flush=True` or re-exec under `python3 -u`, so a redirected
   log shows stage transitions while the flow runs.
2. Add a short note to the holon_flow skill that the redirected log fills only as stages finish until this is fixed, and
   that the checkpoint and `.subagent/flow_<slug>_state.json` are the live signals.

## Notes

- Found while driving `flow-docker-build-concurrency-group` (PR #329, merged by the maintainer on 2026-11-26).
- Not yet confirmed as the only cause: the `holon flow` child may also buffer its own output.

## Scrapped (coordinator, 2026-11-26)

Duplicate of Bean 0385 (flow log file stays empty until the run ends). Its evidence is folded into 0385.
