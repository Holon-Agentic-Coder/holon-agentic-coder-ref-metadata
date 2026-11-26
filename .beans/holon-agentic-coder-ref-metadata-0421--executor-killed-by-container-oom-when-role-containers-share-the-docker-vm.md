---
# holon-agentic-coder-ref-metadata-0421
title: "Executor killed with exit code -9 when concurrent role containers exhaust the shared Docker VM memory"
status: completed
type: bug
priority: high
tags:
  - flow
  - docker
  - reliability
  - holon-agentic-coder
created_at: 2026-11-24T12:20:00Z
updated_at: 2026-11-24T13:00:00Z
---

## Problem

The Stage 3 executor of the flow for Bean 0403 failed at 10:47:34Z on 2026-11-24 with
`Plan execution failed with exit code -9`, 30.5 minutes into execution and after four plan steps were committed. The
wrapper exited 1 and no pull request existed.

## Evidence

- Docker Desktop's VM has 7.75 GiB and 18 CPUs, shared by every role container; no per-container memory limit is set on
  the role containers (only the sidecar sets `--memory=256m`).
- `docker events` for 10:40Z to 10:52Z shows `oom` events on four `holon/agent-claude` containers, including the
  executor's own container (started 10:17:03Z, the execution id E-1795515423) at 10:42:11Z and 10:44:51Z. That container
  then ended with exit 0 at 10:47:34Z, the instant the engine recorded -9: the kernel killed the agent process inside
  the VM and the entrypoint exited cleanly, so the host saw only a SIGKILL status.
- At that time six or more role containers ran at once (Antigravity and Claude, two of them near 1.7 GiB each while
  running test suites). Host memory was healthy (96 percent free, no swap), so the pressure was inside the Docker VM.
- The turn supervisor did not kill the turn: no stall, budget or timeout line sits in the flow log before the failure.

Not confirmed: which process inside the container held the memory at the moment of the kill (no per-process figures were
captured).

## Goal

- Raise the concurrency guard so that the number of concurrent role containers (or their summed memory) is checked
  against the Docker VM's `MemTotal` before Stage 3 starts a container.
- Give each role container an explicit `--memory` limit so that one container is killed alone rather than starving
  others, and report an OOM kill (`docker inspect` `OOMKilled`) as its own failure reason instead of `exit code -9`.
- Treat an OOM kill as resumable: the resume should adopt the committed steps (it did on 2026-11-24, finishing Stage 3
  in 6 minutes).

## Notes

- The 0403 resume at 10:54Z, with four containers running, completed Stage 3 without a further kill.
- Related: Bean 0396 (flow runs and sessions), Bean 0418 (preserving a passing execution).

## Notes

- 2026-11-24: the maintainer raised Docker Desktop's memory from 8 GB to 32 GB at about 12:50Z, removing the shared-VM
  memory pressure recorded above. Overlaps with Bean 0415 (same cause, scrapped).

## Resolution

Completed 2026-11-24. The cause (the shared Docker VM having 7.75 GiB for six or more concurrent role containers) was
removed when the maintainer raised its memory from 8 GB to 32 GB at about 12:50Z. Reopen this bean if an exit code -9
kill recurs at 32 GB.
