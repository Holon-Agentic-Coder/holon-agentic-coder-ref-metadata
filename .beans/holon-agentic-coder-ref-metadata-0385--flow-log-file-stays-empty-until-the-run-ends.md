---
# holon-agentic-coder-ref-metadata-0385
title: "The flow log file stays empty until the run ends, so a running flow cannot be followed"
status: completed
type: bug
priority: normal
tags:
  - harness
  - holon-flow
  - logging
created_at: 2026-11-23T12:40:00Z
updated_at: 2026-11-24T13:00:00Z
---

## Problem

The harness wrapper's log (`todo/flow-<slug>.log`) is often 0 bytes for the whole run and gets its content only when the
process exits (seen on 2026-11-23: `flow-github-issues-replace-beads.log` "empty while the flow ran",
`flow-resume-adopts-pushed-plan-branch.log` 0 lines 15 minutes into the run, `flow-document-env-variables-v2.log` 0
bytes after the host died, so the whole log was lost). Output is block-buffered when stdout is a file, and some agents
launch the wrapper with `nohup`/redirects that buffer again. Progress and failure causes were read from the checkpoint's
`context.logs` instead.

## Goal

- `run_holon_flow.py` writes the flow's output to its log line by line as it happens (unbuffered child, `flush` on every
  line, or `PYTHONUNBUFFERED=1` for the child and line-buffered file).
- The skill tells flow subagents one way to launch and log, so no second layer of buffering is added.
- A killed run leaves everything it printed up to that point in the log.
- Harness-only change (`.agents/skills/holon_flow/`).

## Notes

- Overlap: Bean 0412 (every flow step timed, every flow keeps its log). This bean owns the log flushing; Bean 0412 owns
  the step timings and the log for every flow.

## More evidence (2026-11-26)

Seen on almost every flow run on 2026-11-26 (beans 0496, 0501, 0504 were logged as duplicates and scrapped): the
wrapper's redirected log stays 0 bytes until the flow exits, for runs of 30-80 minutes, so nobody can monitor a running
flow from its log. The wrapper has no unbuffered or flush handling for the child's output.

## Resolution (2026-11-26)

Cause: the wrapper read the child line by line (child already had `PYTHONUNBUFFERED=1`), but its own `print` calls went
to a block-buffered stdout once redirected to a file, so nothing reached the log until exit. Fix in `run_holon_flow.py`:
`enable_line_buffering()` reconfigures stdout and stderr line-buffered at the start of `main`, and the child-output loop
and the command echo print with `flush=True`. Hermetic test: `tests/test_flow_log_streaming.py`. Takes effect on the
next launch. Duplicates 0496, 0501 and 0504 were scrapped earlier.
