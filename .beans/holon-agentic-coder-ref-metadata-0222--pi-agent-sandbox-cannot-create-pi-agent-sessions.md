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

Give the `pi-agent` runner a writable `~/.pi` inside the sandbox, so a flow dispatched with `--agent pi-agent` gets past
its own CLI startup instead of dying in the pre-flight gate.

## Context

Found 2026-11-02 launching the `render-review-consensus-comment-from-reviewer-data` intent with this harness session's
runner and model (`--agent pi-agent`, `--model` = `PI_MODEL`). The pre-flight gate failed closed:

```
Pre-flight pi-agent (JANGQ-AI/Qwen3.8-Flash-Next-JANG_4M) via holon/agent-pi: UNKNOWN
  exit code: 1
  hint: The probe failed for an unrecognised reason; check the output below. ...
    EACCES, mkdir '/home/holon/.pi/agent/sessions/--home-holon--'
        at getDefaultSessionDir (…/@earendil-works/pi-coding-agent/dist/bundle/…)
Aborting before any branch, checkpoint or ledger write.
```

Nothing was created - no branch, no checkpoint, no ledger row.

## Root cause (reproduced)

`get_agent_session_mounts` (`apps/sandbox-executor/src/sandbox_executor/cli/__init__.py:507`) gives pi **one file
mount** and nothing else, by explicit design recorded in the source comment at line 566:

```python
# Only pi's models.json is mounted, never the whole agent directory: that directory also holds auth.json,
# sessions/ and run-history.jsonl, none of which a sandboxed agent needs.
"pi": [
    (os.path.join(home, ".pi/agent/models.json"), "/home/holon/.pi/agent/models.json"),
    (os.path.join(home, ".config/pi/models.json"), "/home/holon/.config/pi/models.json"),
],
```

Mounting a file whose parent directories do not exist makes Docker create those parents **as root**, and pi then runs as
uid 1000 and cannot create `sessions/` underneath them:

```
$ docker run --rm -v "$HOME/.pi/agent/models.json:/home/holon/.pi/agent/models.json:ro" \
      --entrypoint sh holon/agent-pi -lc 'id; ls -ld /home/holon/.pi /home/holon/.pi/agent; \
      mkdir -p /home/holon/.pi/agent/sessions/x'
uid=1000(holon) gid=1000(holon) groups=1000(holon)
drwxr-xr-x 3 root root 4096 Nov  2 04:20 /home/holon/.pi
drwxr-xr-x 2 root root 4096 Nov  2 04:20 /home/holon/.pi/agent
mkdir: cannot create directory '/home/holon/.pi/agent/sessions': Permission denied

# without that mount the image starts fine, because nothing pre-creates the tree
$ docker run --rm --entrypoint sh holon/agent-pi -lc 'mkdir -p /home/holon/.pi/agent/sessions/x'   -> OK
```

`antigravity-agent` does not have this problem because its branch of the same function pairs the read-only session bind
with writable overlays (`--tmpfs /home/holon/.gemini/config:uid=1000,gid=1000` and the `log`/`cache` subpaths, lines
525-527 and 545-547). Pi has no equivalent. Same defect family as #0112 (Codex `$HOME/.tmp`), #0114, #0168 and #0194 -
sandbox home state that the tool must write but was never given somewhere writable to write.

The distinction that fixes it is **file bind vs directory bind** - a directory bind at the same path is writable and
creates no root-owned parents:

```
$ docker run --rm -v /tmp/pi-agent-probe:/home/holon/.pi/agent:rw --entrypoint sh holon/agent-pi \
      -lc 'mkdir -p /home/holon/.pi/agent/sessions/x && echo OK'
drwxr-xr-x 3 root   root   4096 /home/holon/.pi
drwxr-xr-x 2 holon holon     64 /home/holon/.pi/agent
OK
```

Which is also why host-local model mode avoids this bug: it stops mounting host config (`cli/__init__.py:581`) and binds
generated agent directories instead (`local_llm.pi_agent_dirs`, `local_llm.prepare_agent_dir`).

## Second gap this exposed

Even with a writable `sessions/` directory, a flow cannot inherit this session's model, because the sandbox has no
credential path for it: `~/.pi/agent/auth.json` is deliberately never mounted, and pi has no `HOLON_AGENT_KEY`-style
injection (antigravity supports one). The fix must state how a session-inherited model authenticates inside the sandbox,
or the pre-flight gate must say so distinctly instead of reporting `UNKNOWN`. Host-local model mode is the designed
route for a local/vmlx model, but `vmlx` is not installed on this host and `holon` does not self-provision it - that is
Bean 0143.

## Acceptance criteria

1. `holon flow <intent.json> --agent pi-agent --model <model>` passes pre-flight and completes Stage 1 against a clean
   workspace, verified by reading the created `I-*/_` branch and its `intents.jsonl` row, not by exit code alone.
2. Pi's `~/.pi/agent/sessions` is writable for uid 1000 in the container that the flow actually builds, provisioned
   through the existing mount mechanism (a writable tmpfs or a dedicated `~/.holon/sessions/pi` bind, mirroring the
   antigravity pattern) - not an image-local `chmod`, and not by mounting the whole host `~/.pi`.
3. The security posture in the line-566 comment still holds: `auth.json`, host `sessions/` and `run-history.jsonl` stay
   out of the sandbox. If a credential path is added for inherited models, it is named, scoped to that one purpose, and
   covered by a test.
4. A probe that dies on filesystem permissions or missing credentials is classified with an actionable remediation hint
   instead of `UNKNOWN` plus a Node stack trace.
5. `uv run pytest` passes and `uv run task lint` is clean.

## Notes

- `--skip-preflight` is not a fix: Stage 1 hits the same `mkdir` inside the real role container.
- Blocks any flow that inherits this harness session's runner, including Bean 0221 part B as currently briefed.
