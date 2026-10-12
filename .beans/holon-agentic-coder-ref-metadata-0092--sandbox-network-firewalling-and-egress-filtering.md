---
# holon-agentic-coder-ref-metadata-0092
title: "Sandbox network firewalling and egress filtering"
status: completed
type: task
priority: high
tags:
  - security
  - sandbox
  - network
  - firewall
  - docker
created_at: 2026-10-14T13:40:00Z
updated_at: 2026-10-15T15:38:00Z
---

# Bean 0092: Sandbox Network Firewalling and Egress Filtering

- **Bean ID:** 0092
- **Title:** Sandbox Network Firewalling and Egress Filtering
- **Status:** completed
- **Priority:** high
- **Category:** security
- **Components:** `apps/sandbox-executor/cli.py`, `apps/sandbox-executor/Dockerfile`, network isolation
- **Created At:** 2026-10-14
- **Parent Audit Finding:** SEC-01

---

## 1. Context & Motivation

During the codebase security audit (Finding SEC-01 in `docs/audit_report.md`), an isolation gap was identified in direct
egress mode. When the `holon-coherence` token reduction proxy is inactive or disabled, the sandbox container runs on the
default Docker bridge network (`bridge`) with unrestricted outbound connectivity to the internet and local network
subnets.

Under the Holon security specification (`docs/safety.md` §2 and `holon-config/world/constraints.md` §2), agent processes
must operate within strictly isolated network boundaries to prevent accidental or malicious data exfiltration,
unauthorized network scanning, or unmonitored external egress.

---

## 2. Problem Statement

1. In `apps/sandbox-executor/src/sandbox_executor/cli.py`, when `token_reduce=False` or when fallback occurs, no
   firewall rules or egress restrictions are applied to the spawned Docker container.
2. An agent running untrusted third-party dependencies or executing arbitrary scripts could connect to unauthorized
   remote hosts, bypassing logging and security guardrails.

---

## 3. Proposed Remediation

1. **Dedicated Isolated Bridge Network:** Create a dedicated user-defined Docker bridge network (`holon-sandbox-net`)
   configured with iptables egress filtering.
2. **Domain/IP Whitelisting:** Allow egress exclusively to pre-approved endpoints:
   - Git remotes (e.g. `github.com`)
   - Authorized LLM provider API domains (e.g. `generativelanguage.googleapis.com`, `api.anthropic.com`,
     `api.openai.com`)
   - Package repositories (`pypi.org`, `registry.npmjs.org`)
3. **Block Non-Whitelisted Outbound Connections:** Explicitly drop or reject connections to all other external IP ranges
   or local host metadata endpoints (`169.254.169.254`).
4. **Fallback Containment:** In direct fallback mode, enforce strict network egress policy rather than allowing
   arbitrary egress.

---

## 4. Acceptance Criteria

- [x] Running a container without `--token-reduce` attaches to an isolated network with egress controls.
- [x] Connections to unwhitelisted public IP addresses or loopback ports fail immediately with `EPERM` or connection
      timeout.
- [x] Authorized LLM endpoints and git commands continue to resolve and function without degradation.
- [x] Unit and integration tests verify network isolation policies.

---

## 5. Verification Commands

```bash
# Verify unit tests for network isolation argument builders
uv run pytest apps/sandbox-executor/tests/test_cli.py -k "test_network"

# Verify linting and formatting
uv run ruff check .
npx prettier --check .beans/holon-agentic-coder-ref-metadata-0092--sandbox-network-firewalling-and-egress-filtering.md
```

---

## 6. Resolution

- Implemented `build_network_isolation_args` in `apps/sandbox-executor/src/sandbox_executor/cli.py` to enforce
  `--cap-drop=NET_RAW` and cloud metadata sinkholes (`169.254.169.254:127.0.0.1`, `metadata.google.internal:127.0.0.1`,
  `instance-data:127.0.0.1`) across all network modes, including direct fallback and `token_reduce=True`.
- Added unit tests in `test_cli.py` verifying isolation flags and metadata blocking.
- Validated via Holon flow lifecycle stages 1-5; PR #77 achieved 3/3 unanimous ensemble consensus approval, 10/10 green
  CI checks, and pre-merge calibration ($\Delta EV$ +4.30); merged to `main` at commit
  `29aa1c14d060c4b90657803f046c964c6beb54e3`.
