---
title: "pi-agent sandbox cannot create ~/.pi/agent/sessions, so pi-runner flows die at pre-flight"
status: todo
type: task
priority: P1
labels: [sandbox-executor, agent-pi, sandbox-hardening, preflight]
blocked-by: []
blocks: [holon-agentic-coder-ref-metadata-0221]
---

## Task

Make the `pi-agent` runner usable for a real Holon Flow run: the container must be able to create and write the state
its CLI needs at startup (currently `~/.pi/agent/sessions/...`), under the same uid and home-persistence model the flow
applies to every runner.

## Context

Discovered 2026-11-02 while starting the `render-review-consensus-comment-from-reviewer-data` flow with the harness
session's own runner and model (`--agent pi-agent --model <session model>`, resolved from `PI_MODEL`). The run died in
the pre-flight gate:

```
Agent runner resolved to pi-agent (source: flag, --agent)
Model resolved to JANGQ-AI/Qwen3.8-Flash-Next-JANG_4M (source: flag, --model)
Pre-flight pi-agent (JANGQ-AI/Qwen3.8-Flash-Next-JANG_4M) via holon/agent-pi: UNKNOWN
  exit code: 1
  hint: The probe failed for an unrecognised reason; check the output below. ...
    EACCES, mkdir '/home/holon/.pi/agent/sessions/--home-holon--'
        at getDefaultSessionDir (.../@earendil-works/pi-coding-agent/dist/bundle/...)
Aborting before any branch, checkpoint or ledger write. Use --skip-preflight to bypass this check.
```

The gate behaved correctly - fail-closed before any branch, checkpoint or ledger write - the runner underneath it did
not work.

## Evidence

```
# image: no ~/.pi at all, and $HOME is 0700 holon:holon
docker run --rm --entrypoint sh holon/agent-pi -lc 'id; ls -ld /home/holon /home/holon/.pi'
uid=1000(holon) gid=1000(holon)
ls: cannot access '/home/holon/.pi': No such file or directory
drwx------ 1 holon holon 4096 Oct 31 09:12 /home/holon

# as the image's own uid the write succeeds
docker run --rm --entrypoint sh holon/agent-pi -lc 'mkdir -p /home/holon/.pi/agent/sessions/x'   -> OK

# as a non-1000 uid it fails exactly as the flow reported
docker run --rm --user 501:20 --entrypoint sh holon/agent-pi -lc 'mkdir -p /home/holon/.pi/agent/sessions/x'
mkdir: cannot create directory '/home/holon': Permission denied
```

So the pi home is not writable for the identity the flow actually runs the container as. `antigravity-agent` and
`codex-agent` survive this because their home state is overlaid with writable tmpfs mounts; the pi runner has no
equivalent, and `~/.pi` is not in the centralised persisted-home-state list (`DEFAULT_HOME_DIRS_PERSISTED`) that
`ensure_home_state_mounts` auto-mounts - which is the same defect family as #0112 (Codex `$HOME/.tmp`), #0114, #0168 and
#0194.

## Acceptance criteria

1. `holon flow <intent.json> --agent pi-agent --model <model>` passes the pre-flight gate and completes Stage 1 against
   a clean workspace - verified by reading the created `I-*/_` branch and the `intents.jsonl` row, not by the exit code
   alone.
2. The pi runner's required home state (`~/.pi`, at minimum `~/.pi/agent/sessions`) is writable under the flow's
   execution identity, provisioned through the shared home-persistence mechanism rather than an image-local `chmod`.
3. A pre-flight probe that dies on filesystem permissions is classified as a recognised failure reason with an
   actionable remediation hint, instead of `UNKNOWN` plus a raw Node stack trace.
4. `uv run pytest` passes and `uv run task lint` is clean.

## Notes

- Blocks any flow that inherits this harness session's runner (`pi-agent`); a workaround launch must pick another runner
  explicitly, which is the maintainer's call.
- `--skip-preflight` is not a fix: Stage 1 would hit the same `mkdir` inside the real role container.
