---
title: "Overlap wait is silent in the flow log: the wrapper prints only 'exited with non-zero code 1' while it waits"
status: todo
type: bug
priority: normal
tags:
  - harness
  - holon-flow
  - logging
created_at: 2026-11-26T06:16:00Z
updated_at: 2026-11-26T06:16:00Z
---

## Problem

When Stage 3 admission is refused on a touch-set overlap, `scripts/run_holon_flow.py` waits for the overlapping pull
requests (poll every 60 s). During that wait the flow log `todo/flow-<slug>.log` holds only the line
`Holon flow exited with non-zero code 1.` and nothing that says the wrapper is waiting, which pull request it waits on,
or when it will re-check. The only evidence is the checkpoint's `admission` block and the live wrapper process.

Seen on `macos-unit-sensitive-paths-only` (2026-11-26): refused against PR #315, log silent from 05:06Z to 06:13Z (wait
released when #315 closed, flow resumed at 16:13 local).

## Goal

- Log each overlap refusal (the overlapping PR numbers and files) and each poll result (state of each PR) to the flow
  log, so the log shows the wait.
- Keep the wait behaviour unchanged.
