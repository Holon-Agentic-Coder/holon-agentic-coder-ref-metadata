---
# holon-agentic-coder-ref-metadata-0415
title: "Cap pytest workers inside containers to stop OOM SIGKILL (-9) failures"
status: todo
type: bug
priority: high
tags:
  - flow
  - stage-3
  - docker
  - tests
  - holon-agentic-coder
created_at: 2026-11-24T11:05:00Z
updated_at: 2026-11-24T11:05:00Z
---

## Why

With up to 4 concurrent `holon-flow` runs sharing the host Docker Desktop VM RAM, running
`uv run pytest -n auto --dist worksteal` across 6,856 tests inside each role container spawns unbounded worker processes
and hits the Linux OOM killer (`SIGKILL` / `exit code -9`), wasting ~30 minutes per failed turn and requiring a manual
resume.

## Evidence

- `todo/flow-ci-skip-bookkeeping-only-pushes.log` (Bean 0403, `2026-11-24T10:17:02Z`–`10:48:42Z`): Stage 3 ran for 30.5
  min and failed with
  `Execute stage failed: executor agent recorded status 'failure': Plan execution failed with exit code -9`
  (`entrypoint/executor/outcome.py:70`).
- On resume (`10:54:38Z`–`11:00:43Z`), partial code work was adopted and the suite completed in `5.7 min`
  (`6856 passed, 0 failed, 0 errored`).
- `holon-config/prompts/executor.template.md` and `holon-config/prompts/planner.template.md` instruct agents to run
  `-n auto --dist worksteal` with no worker cap or memory check inside the container.

## Proposed change

1. Bound pytest worker count inside role containers (e.g. a configurable `HOLON_PYTEST_WORKERS` / default `-n 4` cap
   derived from container/VM available memory when `-n auto` is used in Docker, or enforcing a max worker cap in
   `pytest` / container env).
2. Detect `returncode == -9` / `137` in `entrypoint/executor/outcome.py` and surface an explicit OOM / worker-cap
   diagnostic instead of a generic exit code `-9`.

## Expected gain

Prevents 30+ minute Stage 3 executor failures and manual resume cycles under 4-way concurrent flow execution.

## Cost

Small change in `holon-config/prompts/` and `apps/sandbox-executor/src/sandbox_executor/entrypoint/executor/outcome.py`.
