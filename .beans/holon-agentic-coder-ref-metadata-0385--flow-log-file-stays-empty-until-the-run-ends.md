---
# holon-agentic-coder-ref-metadata-0385
title: "The flow log file stays empty until the run ends, so a running flow cannot be followed"
status: todo
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
