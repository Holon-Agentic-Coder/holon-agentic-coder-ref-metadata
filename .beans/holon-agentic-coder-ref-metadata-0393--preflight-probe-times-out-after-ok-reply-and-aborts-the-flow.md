---
# holon-agentic-coder-ref-metadata-0393
title: "Pre-flight probe that replied OK but exited late is classed UNKNOWN and aborts the flow"
status: in-progress
type: bug
priority: high
tags:
  - flow
  - preflight
  - holon-agentic-coder
created_at: 2026-11-24T08:12:00Z
updated_at: 2026-11-24T11:34:00Z
---

## Problem

On 2026-11-24 at about 07:45Z the flows `flow-references-github-issues` (Bean 0216) and `split-calibration-package`
(Bean 0197) left their Stage 3 overlap wait when PR #268 merged, resumed, and aborted at once:

```text
Pre-flight claude-agent (claude-fable-5-2) via holon/agent-claude: UNKNOWN
  hint: The probe did not finish within 60s; the runner may be waiting on an interactive login. ...
  output (redacted):
    OK
    Claude Code doesn't recognize the model "claude-fable-5-2", so it assumes a context window of 200k tokens. ...
Aborting before any branch, checkpoint or ledger write. Use --skip-preflight to bypass this check.
```

The probe had already printed the expected `OK` reply; the container only failed to exit within 60 s. Twenty-five
minutes later the same probe (`holon doctor --agent claude-agent --model claude-fable-5-2`, same image, same
credentials) returned OK in 4.8 s with code mode on and 4.1 s with it off, so the model id, the credentials and code
mode are not the cause. The `holon/agent-claude` image was rebuilt at 07:45:07Z (post-merge install after PR #268), at
the moment the two flows resumed; a Docker daemon busy with the build is the probable cause of the slow exit (not
confirmed).

## Defects

1. `preflight._run_probe` returns UNKNOWN on a timeout without looking at the output it captured. A probe whose output
   carries the expected `OK` reply has proved the runner, the credentials and the model; only the exit was slow.
2. The hint blames an interactive login and the excerpt shows the unrecognised-model warning, so the abort reads as a
   model-id problem. The flow subagent reported it that way.
3. A transient pre-flight result ends the whole wrapper run. `run_holon_flow.py` waits out limits and overlaps but
   treats one UNKNOWN probe as terminal, so a flow that waited hours for its overlap died in its first minute.
4. Flows that leave an overlap wait when a pull request merges restart at the same moment the post-merge image rebuild
   runs.

## Goal

- A timed-out probe whose output contains the expected reply is classed OK (with a note that the exit was slow).
- An UNKNOWN probe is retried (for example three attempts with a pause) before the flow aborts, in the engine or the
  wrapper.
- The hint for a timeout names the timeout and does not suggest a login when a reply was received.
- Flows resuming after a merge do not race the image rebuild, or the probe tolerates it.

## Notes

- Found while driving Beans 0216 and 0197; both are relaunched from their checkpoints.
- Related: Bean 0385 (flow log empty while the wrapper waits; the overlap wait was invisible in the logs here too).

> 2026-11-24: launched `preflight-ok-reply-slow-exit-and-retry` (intent
> `todo/intent-0393-preflight-ok-reply-slow-exit-and-retry.json`) via `antigravity-agent` / `gemini-4-neon`.
