---
# holon-agentic-coder-ref-metadata-0026
title: Implement coding agent runners with automated background proxy in holon-coherence
status: completed
type: task
created_at: 2026-09-18T00:00:00Z
updated_at: 2026-09-22T00:00:00Z
---

Implement CLI subcommands in `holon-coherence` (e.g., `holon-coherence agy`, `holon-coherence claude`, etc.) that
automatically launch the optimization proxy Docker container in the background, configure and pass in all required proxy
routing and certificate environment variables (HTTP_PROXY, HTTPS_PROXY, NO_PROXY, SSL_CERT_FILE, NODE_EXTRA_CA_CERTS),
map and inject universal credentials (HOLON_AGENT_KEY), and execute the selected coding agent with wire telemetry and
token optimization enabled.

## Notes

- Target repository: holon-coherence (src/holon_coherence/cli.py and documentation)
- Execution Semantics: Host agent CLI tools run natively as host subprocesses (inheriting user environment and
  preserving config paths like ~/.gemini or ~/.claude.json), while the optimization proxy sidecar runs inside a
  background Docker container. Optional containerized agent mode can mount config paths if supported.
- Interactive TTY & Stdio Passthrough: Host runner child subprocess execution for interactive coding agents (claude,
  agy, etc.) must maintain standard interactive TTY attachment (stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr,
  or pty on POSIX systems) and terminal signal passthrough (SIGWINCH for window resizing, SIGINT for interrupt handling)
  so interactive prompts, ANSI styling, and cursor positioning are preserved.
- Docker Proxy Lifecycle and Teardown Policy:
  - Background daemon mode by default across invocations to minimize container startup latency.
  - Automatically starts the proxy container (if not already healthy) in detached mode prior to agent execution.
  - Provides `holon-coherence stop` CLI command to stop and remove the background proxy container on demand.
  - Supports optional `--ephemeral` flag to tear down the proxy container upon agent process exit.
  - Implements signal traps and process group signal forwarding (SIGINT, SIGTERM) to ensure child processes receive
    signals directly and can execute terminal cleanup before runner teardown, ensuring accurate child exit code
    propagation.
  - Supports configurable proxy port allocation (via `--port` CLI flag or `HOLON_PROXY_PORT` environment variable,
    defaulting to 8080) with port conflict detection during container startup.
  - Diagnostic error handling when Docker daemon is unreachable, reporting actionable guidance instead of raw client
    tracebacks.
- Sensitive Credential Redaction in Wire Telemetry: The proxy and telemetry logging layers must redact sensitive
  authentication credentials (e.g. `Authorization` bearer tokens, `x-api-key`, and credential query parameters) prior to
  persisting request dumps or streaming logs to disk.
- Universal Agent Credentials (HOLON_AGENT_KEY) & Native Auth Fallback: Invariant rule 5 - runners accept
  HOLON_AGENT_KEY on the host and map it to child process environment variables internally. If HOLON_AGENT_KEY is
  omitted, the host runner does not inspect or validate vendor API keys; it allows child subprocesses to transparently
  inherit native host auth sessions and existing credentials (e.g. ~/.gemini, ~/.claude.json):
  - 1. agy (Antigravity): maps HOLON_AGENT_KEY to GEMINI_API_KEY / AGY_USER_TOKEN internally for child process.
  - 2. claude (Claude Code / Anthropic): maps HOLON_AGENT_KEY to ANTHROPIC_API_KEY internally for child process.
  - 3. codex (OpenAI Codex / ChatGPT CLI): maps HOLON_AGENT_KEY to OPENAI_API_KEY internally for child process.
  - 4. opencode (OpenCode): maps HOLON_AGENT_KEY to OPENCODE_API_KEY internally for child process.
  - 5. pi (Inflection Pi / Pi Agent): maps HOLON_AGENT_KEY to PI_API_KEY internally for child process.
- Proxy Environment Variables Injected:
  - HTTP_PROXY=http://127.0.0.1:<port> (default: 8080)
  - HTTPS_PROXY=http://127.0.0.1:<port> (default: 8080)
  - ALL_PROXY=http://127.0.0.1:<port> (default: 8080)
  - NO_PROXY=localhost,127.0.0.1,::1,169.254.169.254,api.github.com,github.com
  - Lowercase equivalents (http_proxy, https_proxy, all_proxy, no_proxy)
  - SSL_CERT_FILE / REQUESTS_CA_BUNDLE / CURL_CA_BUNDLE pointing to a merged CA certificate bundle on the host
    (combining system/certifi CA roots and Holon proxy root CA, ensuring direct connections via NO_PROXY succeed without
    TLS failures)
  - NODE_EXTRA_CA_CERTS for Node.js-based agents (e.g. Claude CLI)
- CLI Interface Design: Support direct aliases (`holon-coherence <agent> [agent_args...]`) as well as
  `holon-coherence run-agent <agent> [agent_args...]`.
- Test Coverage & Error Handling: Add unit and integration tests in `holon-coherence/tests/test_cli.py` covering child
  process exit code propagation, credential mapping, fallback to native auth, proxy lifecycle flags, interactive TTY/PTY
  stdio passthrough, signal forwarding, and clean diagnostic error reporting when the Docker daemon is unreachable.
- Documentation: Update holon-coherence/README.md and AGENTS.md documenting agent invocation, required credentials, and
  proxy lifecycle.
- Merged: holon-coherence PR #4 (2026-09-22), squash commit c374760 on origin/main.
- Post-merge audit 2026-09-22: worktree holon-coherence/feat-0026-coding-agent-runners and local branch removed (content
  diff vs origin/main was empty); remote ref already gone.
- Post-merge defect 2026-09-22: first real-world use (holon-coherence pi against a local vMLX server) exposed that the
  proxy container cannot reach host-local LLM endpoints. Measured, root-caused, and tracked as Bean 0027; the related
  --native proxy/port-conflict gap in ensure_proxy_running is tracked as Bean 0028.

## Assignment

Assignee: `antigravity-agent`

## Resolution

Implemented coding agent runners with automated background proxy in holon-coherence on dedicated worktree
feat-0026-coding-agent-runners (branch feat/0026-coding-agent-runners):

- Updated `src/holon_coherence/cli.py` to support direct agent aliases (`holon-coherence agy`, `holon-coherence claude`,
  `holon-coherence codex`, `holon-coherence opencode`, `holon-coherence pi`, and `antigravity`) as well as
  `holon-coherence run-agent <agent> [agent_args...]`.
- Implemented background proxy lifecycle with health checking, port conflict detection, and default persistent daemon
  mode across runs.
- Added `--ephemeral` flag to tear down and remove the proxy container upon agent process exit.
- Updated `holon-coherence stop` command to stop and remove the container on demand.
- Implemented `get_or_create_merged_ca_bundle` combining system/certifi CA roots with the Holon Root CA, ensuring
  NO_PROXY traffic and intercepted proxy traffic succeed without TLS failures.
- Injected all required proxy routing (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, `NO_PROXY`, and lowercase variants) and
  CA bundle variables (`SSL_CERT_FILE`, `REQUESTS_CA_BUNDLE`, `CURL_CA_BUNDLE`, `NODE_EXTRA_CA_CERTS`).
- Implemented universal credential mapping from `HOLON_AGENT_KEY` to child vendor keys, with transparent fallback to
  native host auth sessions (`~/.gemini`, `~/.claude.json`) when omitted (no vendor key checks or validations).
- Maintained standard interactive TTY attachment (`stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr`) and signal
  traps (`SIGINT`, `SIGTERM`, `SIGWINCH`) with clean child exit code propagation.
- Added comprehensive test suite in `tests/test_cli.py` (36 new unit and integration tests, all 62 tests passing).
- Updated `README.md` and `AGENTS.md` in holon-coherence.
- Formatted all markdown using Prettier and squashed changes into a single commit on feat/0026-coding-agent-runners.
