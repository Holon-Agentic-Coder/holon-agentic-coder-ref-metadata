---
# holon-agentic-coder-ref-metadata-0027
title: Fix agent runner proxy unable to reach host-local LLM endpoints (Ollama, vMLX, LM Studio, vLLM)
status: todo
type: task
created_at: 2026-09-22T00:00:00Z
updated_at: 2026-09-22T00:00:00Z
---

Discovered on 2026-09-22 during the first real-world use of the Bean 0026 coding agent runners (`holon-coherence pi`)
against a local inference server. Every LLM call failed with HTTP 502 / timeout.

Root cause: `holon-coherence <agent>` runs the agent binary on the host but the optimization proxy inside a Docker
container, and forces `HTTP_PROXY`/`HTTPS_PROXY`/`ALL_PROXY=http://127.0.0.1:<port>` into the child environment. The
agent therefore hands the upstream target to mitmproxy, and that target is resolved inside the container's network
namespace. Loopback resolves to the container itself, and the host's own LAN address is not routable from the Docker
Desktop VM. `NO_PROXY_HOSTS` (`src/holon_coherence/cli.py:23`) only exempts
`localhost,127.0.0.1,::1,169.254.169.254,api.github.com,github.com`, so a host-local model server addressed by LAN IP is
intercepted and then dropped. Neither `docker run` site (`cli.py:409`, `cli.py:1000`) passes
`--add-host=host.docker.internal:host-gateway`, and `mitm_addon.py` performs no upstream address rewriting, so there is
currently no working path from proxy to a host-local model.

Measured evidence on macOS (host LAN IP 192.168.2.15 = the host itself, vMLX listening on `*:8081`):

| Probe                                                                | Result                                                |
| -------------------------------------------------------------------- | ----------------------------------------------------- |
| host -> `http://192.168.2.15:8081/v1/models`                         | 200 OK (1.6 ms)                                       |
| host -> same URL via `-x http://127.0.0.1:8080`                      | timeout, http=000                                     |
| inside container -> TCP `192.168.2.15:8081`                          | timeout (packets silently dropped)                    |
| inside container -> TCP `127.0.0.1:8081`                             | connection refused (container loopback)               |
| inside container -> TCP `host.docker.internal:8081` (192.168.65.254) | OK                                                    |
| `docker logs holon-coherence`                                        | `CONNECT 192.168.2.15:8081` then `<< 502 Bad Gateway` |

The container can reach the host, but only through the Docker gateway address, never through the address the agent
actually requests. Today the only workaround is `NO_PROXY=<llm-host>`, which bypasses payload cleaning, caching and wire
telemetry for the entire session and therefore defeats the purpose of the gateway.

## Notes

- Target repository: holon-coherence (src/holon_coherence/cli.py and src/holon_coherence/mitm_addon.py). Work in a
  dedicated worktree off origin/main, never in apps/holon-coherence/main.
- Related: Bean 0026 (runners), Bean 0028 (native proxy gap in the same startup path).
- Recommended fix step 1: add `--add-host=host.docker.internal:host-gateway` to both docker run command builders in
  cli.py so the gateway name resolves on Docker Desktop and on Linux alike.
- Recommended fix step 2: add a mitmproxy `server_connect` hook in mitm_addon.py that rewrites `server.conn.address` to
  the resolved host.docker.internal IP when the requested authority is loopback or an explicitly declared host-local
  host, e.g. driven by a new `HOLON_HOST_LOCAL_HOSTS` container environment variable.
- Recommended fix step 3: have the CLI detect the host primary LAN address and pass it in via `HOLON_HOST_LOCAL_HOSTS`,
  so users keep natural base URLs such as http://localhost:11434/v1 or http://192.168.2.15:8081/v1 in native agent
  config while traffic stays intercepted.
- Safety invariant: never blanket-rewrite all RFC1918 ranges. A genuinely remote inference box on the same LAN would be
  silently redirected onto the host. Rewrite only loopback plus an explicit allow list.
- Known constraint: `pi` parses NO_PROXY with exact hostname/origin or `*.`/`.` suffix matching only, with no CIDR
  support, so range-based exemptions are not a portable workaround for any agent.
- Acceptance criteria: `holon-coherence pi` (and at least one other runner) completes a chat round trip against a
  host-local OpenAI-compatible server addressed as both localhost and host LAN IP, with the request visible in the wire
  logs and token reduction stats recorded.
- Test coverage: extend tests/test_docker_integration.py and tests/test_cli.py for the add-host flag, the rewriting hook
  decision table (loopback, allow-listed host, genuine LAN host, public host), and the diagnostics emitted when the
  gateway name does not resolve.

## Assignment

Assignee: `unassigned`
