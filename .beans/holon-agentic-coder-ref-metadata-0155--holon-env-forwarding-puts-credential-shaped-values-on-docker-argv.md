---
# holon-agentic-coder-ref-metadata-0155
title: "General HOLON_* env forwarding puts credential-shaped non-URL values on the docker argv"
status: in-progress
type: bug
priority: high
tags:
  - security
  - redaction
  - holon-agentic-coder
created_at: 2026-10-25T12:06:22Z
updated_at: 2026-11-23T09:00:00+11:00
---

## Problem

Found by the PR #94 iteration-18 resolver on 2026-10-25. The behaviour is already on `main` and is not caused by #94.

The general `HOLON_*` forwarding loop in `sandbox_executor/cli.py` (around line 1335) passes accepted non-URL `HOLON_*`
settings to the container as `-e NAME=value` on the docker command line. It also prints them in the `Executing:` echo.
#96 routes URL values that carry userinfo, and known secret variables, through the 0600 env-file. A credential-shaped
value in any other forwarded setting still reaches the host argv and the echo, where `ps` on the host and the logs can
see it. Example: a budget variable that ignores the bad value and falls back to its default, but is still forwarded.

## Scope

- Decide the rule:
  - **Default:** forward every `HOLON_*` value through the 0600 env-file, so none reach the argv.
  - **Narrower alternative:** run the canonical `redact_agent_secrets` classifier on every forwarded value and send
    anything credential-shaped through the env-file.
- Apply it to the main run and the pre-flight probe.
- Keep the `Executing:` echo masked.
- Tests: run the URL/message fuzz matrix values through every forwarded `HOLON_*` name, and assert neither argv (main
  run or probe) nor the echo contains a fragment of the value.

## Notes

- Run through the Holon flow on holon-agentic-coder.
- Related: Bean 0148 (redaction gaps in ledger `error_context`).

## Audit (2026-11-20)

Done: `add_env()` (`cli/__init__.py`) sends anything `is_secret_env_item()` flags (secret name, masked value, URL
password) to the 0600 env-file. Remaining: a bare non-URL secret under an arbitrary `HOLON_*` name is not flagged, and
the fuzz test still skips the `TIMEOUT`/`BUDGET` names instead of running every forwarded name against argv, probe and
echo.

## Run (2026-11-23)

- Earlier attempt (intent `holon-env-all-via-env-file`, flow branch `flow-holon-env-all-via-env-file`) stopped at Stage
  2 with no PR; not resumed because main has moved (PRs #235-#240). Its P- branch and worktree are left for cleanup.
- Fresh intent: `todo/intent-0155-holon-env-all-via-env-file-v2.json`, run via `holon flow` on holon-agentic-coder with
  claude-agent / claude-opus-5-5 and `--allow-overlap`.
- Fresh flow (`holon-env-all-via-env-file-v2`): PR https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/243.
  Plan, execute and calibrate ok; Stage 4 review approved 3/3 (iterations 2 and 3) on the pre-merge head.
- Blocked: main moved (#241 moved the env routing to `launcher/env_files.py` and `launcher/containers.py`). PR #243 is
  now CONFLICTING on code in `cli/__init__.py`, `preflight.py` and three tests. The resolve-conflict skill escalates
  logic conflicts, so the change needs re-planning on current main; the review gate refuses to post consensus while the
  branch conflicts. Not hand-ported (sole change path).
- Cleanup: earlier worktree `flow-holon-env-all-via-env-file` and branch `I-1795388466-holon-env-all-via-env-file/*` are
  left over.
