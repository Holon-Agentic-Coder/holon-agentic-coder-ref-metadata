---
# holon-agentic-coder-ref-metadata-0129
title: "Expose plain mitmweb web interface to inspect live requests and responses"
status: todo
type: task
priority: normal
tags:
  - coherence
  - mitmproxy
  - mitmweb
  - observability
  - devex
created_at: 2026-10-20T07:11:00Z
updated_at: 2026-10-20T07:11:00Z
---

Expose the plain `mitmweb` interface in `holon-coherence` so developers and agents can inspect actual intercepted
HTTP/HTTPS requests, headers, and responses in real time.

## Context

`holon-coherence` serves as the network optimization proxy and telemetry gateway, intercepting LLM API calls for
deduplication, prompt caching, and wire logging. Currently, while `mitm_addon.py` provides custom metrics at `/holon/`
(port 8080), the full `mitmweb` interactive inspection dashboard (port 8081) requires explicitly passing `--web` to
`holon-coherence start`. When started without `--web`, the container only runs `mitmdump`, leaving developers unable to
view the raw request/response streams in a browser.

To improve developer observability and debugging during flow executions, `mitmweb` should be exposed as a standard or
easily enabled feature, allowing users to view:

- Exact request methods, URLs, headers, and request body payloads.
- Response status codes, headers, and parsed/streaming response bodies.
- Flow interception timings, TLS details, and cache status.

## Tasks

- [ ] Configure `holon-coherence start` to expose the `mitmweb` web UI by default (or via seamless configuration) on
      port 8081 with host port conflict fallback.
- [ ] Explicitly output all exposed ports and endpoints (proxy port, Coherence live dashboard, and plain mitmweb
      inspection dashboard with token) as part of both `holon-coherence status` and `holon-coherence metrics`.
- [ ] Ensure `holon-coherence status` and `start` output the plain mitmweb URL
      (`http://127.0.0.1:<web_port>/?token=...`) clearly indicating raw request/response inspection.
- [ ] In `holon flow`, ensure `--token-reduce` coordinates with `--mitm-web` so request/response inspection is
      accessible during sandbox flow executions.
- [ ] Verify security safeguards: ensure password token authentication is preserved, and sensitive credential scrub
      patterns (`_SECRET_DICT_KEY_PATTERN`) protect logged requests/responses.
- [ ] Update documentation in `docs/` and `README.md` explaining how to inspect live requests and responses via the
      plain `mitmweb` UI and how exposed ports are displayed.

## Execution status (2026-10-22)

Not started: Stage 1 could not run because no agent runner on this host has usable credentials (antigravity quota
exhausted until 2026-10-24, `claude` not logged in, `codex` refresh token revoked, `opencode` key expired, and
`pi-agent` on the host-local vMLX gateway failed a planner run with
`Response was truncated: the model reached its output token limit`). See Bean 0132 for the full runner inventory.
Prepared and ready to run: worktree `apps/holon-coherence/flow-0129-0133-coherence-mitmweb-monotonic-clock` (branch
`flow/0129-0133-coherence-mitmweb-monotonic-clock` from `origin/main` at `29b7e50`, own virtualenv) and combined intent
file `todo/intent-0129-0133-coherence-mitmweb-monotonic.json`, which pairs this bean with Bean 0133 in one execution.
