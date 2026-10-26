---
# holon-agentic-coder-ref-metadata-0148
title: "Redact before truncating executor ledger error_context and remaining stderr logs"
status: todo
type: bug
priority: high
tags:
  - security
  - redaction
  - ledger
created_at: 2026-10-24T01:41:18Z
updated_at: 2026-10-24T01:41:18Z
---

## Problem

Found in the Stage 4 review of holon-agentic-coder PR #92 (Bean 0136), iteration 4 (finding C4-N3). Reviewers 2 and 3
reproduced it with fake tokens:

- `apps/sandbox-executor/src/sandbox_executor/entrypoint/executor.py` (around lines 1196 and 1384) cuts agent stderr to
  500 characters **before** running `redact_text`. `redact_text` alone also misses bare `gh*_` tokens. A token prefix
  can therefore reach `error_context` in `holon-knowledge/ledger/executions.jsonl`, which is committed and pushed.
- PR #90 found a related line: `calibration.py` logs `"Git commit output: %s"` with git stderr unredacted. It predates
  that PR and was left alone.

This was deferred out of PR #92 because Bean 0136's intent (goal 4) and acceptance criteria require existing ledger and
wire-log redaction behaviour to stay unchanged.

## Scope

- Redact with the canonical redactor first, then truncate, for every executor `error_context` writer. That redactor is
  `redact_agent_secrets` from `sandbox_executor/redaction.py` (merged in PR #96).
- Redact the `calibration.py` git-stderr log line.
- Sweep the remaining ledger writers and log lines that carry subprocess or exception text, and route each through the
  same redactor.
- Regression tests that place a fake token across the truncation boundary. Build fake values at runtime under neutral
  variable names so CodeQL doesn't raise clear-text-logging false positives.
- Found in PR #96's merge-verification review (finding R4-N1, 2026-10-24): #90's `CredentialRedactor`, used for the
  Stage 4/5 warnings and `error_context` rows, leaves six classes unmasked. All of them are on main:
  - `gho_`/`ghu_`/`ghs_`/`ghr_` tokens
  - `ghp_` values that are not exactly 36 characters
  - `sk-ant-` keys shorter than 20 characters
  - https URL userinfo passwords
  - the literal values of `GITHUB_TOKEN` and `HOLON_AGENT_SETTINGS`

  Route those rows through `redact_agent_secrets` (a strict superset), with a regression test per class.

## Notes

- PRs #90 and #96 have merged, so this can now run through the Holon flow on holon-agentic-coder.
