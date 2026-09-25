---
# holon-agentic-coder-ref-metadata-0028
title: "Agent runner startup path has no native proxy fallback and hard-exits on port conflicts"
status: todo
type: task
priority: normal
created_at: 2026-09-22T13:52:43Z
updated_at: 2026-09-22T13:52:43Z
---

Discovered while root-causing Bean 0027 and referenced as "Bean 0028" from both Bean 0026 and Bean 0027, but never
actually filed. This bean is that missing record.

`holon-coherence <agent>` (the coding agent runner path) can only talk to a Docker-hosted proxy, and aborts the whole
process if the proxy port is occupied. The `--native` escape hatch exists but is unreachable from this code path.

## Confirmed state of the code

Verified against `holon-coherence` `origin/main` = `c374760`:

- `run_agent()` (`src/holon_coherence/cli.py:692`) is the runner entry point. At `cli.py:730` it calls
  `ensure_proxy_running(port=port)` unconditionally. That function only knows how to start a Docker container.
- `--native` ("Run natively using host mitmproxy instead of Docker") is registered for the `start` command at
  `cli.py:841` and honoured at `cli.py:960` (`if is_in_container() or args.native:`). It is **not** reachable from the
  runner path: `RunnerFlags` (`cli.py:634`) carries only `ephemeral` and `port`, and `extract_runner_flags()`
  (`cli.py:643`) parses no `--native` flag. So `holon-coherence agy --native ...` cannot use a host mitmproxy.
- `ensure_proxy_running()` (`cli.py:341`) hard-fails when the port is busy. If `is_port_in_use(port)` is true and the
  holder is not the healthy `holon-coherence` container, it prints
  `Error: Port {port} is already in use by another process.` (`cli.py:362`) and calls `sys.exit(1)`. There is no
  alternate-port selection and no fallback to a native proxy, even though `internal/portalloc` style allocation and a
  working native mode both conceptually exist.
- The failure is a bare `sys.exit(1)` from inside a helper, while its caller `run_agent()` reports failures by returning
  an integer exit code. The helper therefore terminates the process (and skips the `finally` teardown of an ephemeral
  container) instead of propagating an error to the caller.

## Why it matters

A port conflict is the common case, not the edge case: `8080` collides with local dev servers, other proxies, and with
Bean 0027's host-local model servers. Today the runner refuses to start rather than picking a free port or using the
native proxy the `start` command already supports.

## Goals & Action Plan

1. **Expose native mode to runners**: add `native` to `RunnerFlags` and parse `--native` in `extract_runner_flags()`,
   then thread it into the startup path so `holon-coherence <agent> --native` uses host mitmproxy the same way
   `holon-coherence start --native` does.
2. **Do not hard-exit on a busy port**: give `ensure_proxy_running()` a result/error return contract so `run_agent()`
   decides what to do, and either auto-select a free port (reporting the chosen port back to the generated proxy
   environment) or fail with actionable guidance. Do not silently pick a different port from the one advertised to the
   agent.
3. **Preserve teardown semantics**: ensure returning an error instead of `sys.exit(1)` keeps the `finally` block in
   `run_agent()` able to stop an ephemeral container it started.

## Acceptance criteria

- `holon-coherence pi --native -- <args>` runs the agent against a host mitmproxy with no Docker container started.
- With port `8080` occupied by an unrelated process, a runner invocation either proceeds on a reported free port or
  exits with the actionable message; it must not emit a traceback or leave an orphan container.
- An ephemeral runner that fails during proxy startup does not leak a running container.

## Test coverage

Extend `tests/test_cli.py` with: `--native` flag extraction and pass-through, runner behaviour when the port is held by
a foreign process, the error-return (rather than `SystemExit`) contract from `ensure_proxy_running()`, and ephemeral
teardown on startup failure.

## Notes

- Target repository: `holon-coherence` (`src/holon_coherence/cli.py`). Work in a dedicated worktree off `origin/main`,
  never in `apps/holon-coherence/main`.
- Related: Bean 0026 (the runners that own this startup path) and Bean 0027 (host-local LLM endpoints unreachable
  through the containerized proxy). Bean 0027's fix (adding `--add-host=host.docker.internal:host-gateway` and upstream
  address rewriting) is independent of this one; native mode and port allocation are not a substitute for it.
