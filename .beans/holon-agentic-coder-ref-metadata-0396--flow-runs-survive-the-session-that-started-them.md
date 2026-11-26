---
# holon-agentic-coder-ref-metadata-0396
title: "A flow run survives the agent session that started it"
status: todo
type: feature
priority: high
tags:
  - flow
  - wrapper
  - harness
  - reliability
created_at: 2026-11-24T08:30:00Z
updated_at: 2026-11-26T05:25:00Z
---

## Problem

`run_holon_flow.py` runs as a child of the agent session that launched it. On 2026-11-24 a session restart at about
07:19Z killed four wrappers at once (Beans 0387, 0197, 0216, 0225), left a role container running without an owner, and
the flows stayed stopped until the maintainer asked for them to be resumed. An earlier network outage did the same to
the watchers.

## Goal

- A flow is started under a supervisor that does not depend on any agent session, so a restart, a crash or a closed
  terminal changes nothing for the flow.
- One runner per checkpoint, enforced by a lock that also sees live role containers (Bean 0390).
- Any session can list the supervised flows, attach to their logs and ask one to stop.
- The driving subagent becomes a watcher: it can die and be replaced without touching the flow.

## Notes

- Occurrence (2026-11-24, about 12:50Z): the Docker restart that applied the memory increase killed every running flow's
  containers and stopped two flows. A flow supervisor that survives such events would have restarted or reported them.
- Logged from Bean 0394 (no unnecessary waiting in the holon flow), on the maintainer's word of 2026-11-24.
- Harness-side first (the wrapper and the skill); an engine-side `holon flow --detach` can follow.
- Related: Bean 0390 (two runners on one checkpoint), Bean 0385 (flow log empty while the wrapper waits).

## Audit evidence, 2026-11-26 (flow time audit)

Flow time audit (`todo/flow-time-audit-2026-11-26.md`): one network outage on 2026-11-25 about 06:24 to 07:01Z stopped
three flows (pre-flight UNKNOWN in the overlap poll of `ledger-fragments-and-promotion`, resolver ENOTFOUND in
`workspace-survival-job-parallel`, Docker down in the `calibration-merge-adapted-file` resync). None was relaunched
until 22:47 to 23:11Z: about 16.5 h idle each, 67 % of all measured flow time in the sample. See Bean 0480 for the
wrapper-side wait-and-retry; this bean's supervisor is what would relaunch after it gives up.
