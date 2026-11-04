---
# holon-agentic-coder-ref-metadata-0223
title: "Audit holon CLI flag / HOLON_* env var overlap: one resolution helper, logged source, uniform naming"
status: todo
type: task
priority: normal
tags:
  - cli
  - configuration
  - holon-agentic-coder
  - documentation
created_at: 2026-11-04T00:00:00Z
updated_at: 2026-11-04T00:00:00Z
---

## Problem

Several holon CLI flags duplicate a `HOLON_*` environment variable (for example `--skip-preflight` /
`HOLON_SKIP_PREFLIGHT=1`), but the pairing is ad hoc: some pairs are documented in `--help`, some are not; precedence is
only stated for `--agent`/`--model`; boolean env parsing differs between call sites; some knobs exist only as env vars
and some only as flags, with no stated reason.

Initial analysis on `main` (`922289f`), from `git grep` over `apps/sandbox-executor/src`:

| Kind                                                            | Pairs / names                                                                                                                                                                                                                                                                                                                                         |
| --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Flag ↔ env overlap                                              | `--agent`/`HOLON_AGENT`, `--model`/`HOLON_MODEL`, `--skip-preflight`/`HOLON_SKIP_PREFLIGHT`, `--token-reduce`/`HOLON_TOKEN_REDUCE`, `--repo-dir`/`HOLON_REPO_DIR`, `--skip-push`/`HOLON_SKIP_PUSH`, `--review-severity`/`HOLON_REVIEW_SEVERITY`, `--web-port`/`HOLON_MITM_WEB_PORT`, preflight `--timeout`/`HOLON_PREFLIGHT_TIMEOUT`                  |
| Env-only (operational knobs)                                    | `HOLON_STAGE_BUDGET_SECONDS` (and the per-stage minute variants), `HOLON_TURN_TIMEOUT_SECONDS`, `HOLON_TURN_STALL_SECONDS`, `HOLON_KEEP_WORKSPACE`, `HOLON_REPLAN_FEEDBACK`, `HOLON_PROXY_URL`/`HOLON_PROXY_PORT`, `HOLON_LOCAL_*`, `HOLON_GIT_LOCK_AGE_SECONDS`, `HOLON_CONTEXT_RESERVE_TOKENS`, `HOLON_AGENT_LOG_BYTES`, `HOLON_PASSIVE_MONITORING` |
| Env-only (credentials / runner config — correctly env-only)     | `HOLON_AGENT_KEY`, `HOLON_AGENT_SETTINGS`, `HOLON_AGENT_PROVIDER`, `HOLON_AGENT_EFFORT`, `HOLON_AGENT_SKIP_PERMISSIONS`, `HOLON_SECRET_BUNDLE_PATH`, `HOLON_MITM_WEB_PASSWORD`/`HOLON_MITM_USER`                                                                                                                                                      |
| Env-only (container-internal markers — must never become flags) | `HOLON_ROLE`, `HOLON_IN_SANDBOX`, `HOLON_REPO_URL`, `HOLON_AGENT_ID`, `HOLON_AGENT_MODE`, `HOLON_ACTION_ORIGIN`                                                                                                                                                                                                                                       |
| Flag-only (per-invocation, no env wanted)                       | `--from-stage`, `--checkpoint`, `--dry-run`, `--skip-review`, `--skip-calibrate`, `--max-review-iterations`, `--ensemble-size`, `--auto-pr`/`--no-auto-pr`, `--json`, `--local`                                                                                                                                                                       |

## Recommendation (to be confirmed by the audit)

Keep **both** layers — this is deliberate twelve-factor-style layering, not accidental duplication:

- Flags express explicit per-invocation intent; env vars are the only workable channel for CI, wrappers, containers and
  secrets (the sandbox side receives configuration exclusively through env, so env cannot be removed).
- The defect is not the duplication but the inconsistency. Standardise instead of removing:
  1. One resolution helper (`flag > env > default-or-error`) used by every paired option, logging its source the way
     agent/model resolution already does (`source: flag, --agent`) — that existing pattern is the model.
  2. Uniform naming `HOLON_<FLAG_IN_SNAKE_CASE>`, with legacy names accepted through a deprecation window.
  3. One shared truthy parser for boolean env values.
  4. `--help` text auto-derives the "env: HOLON_X does the same" sentence from the option registration, so the docs
     cannot drift from the code.
  5. Credentials and container-internal markers are explicitly documented as env-only and never gain flags; purely
     per-invocation flags (`--from-stage`, `--checkpoint`, `--dry-run`) are documented as flag-only.
  6. A reference table of every knob (flag, env, default, scope, precedence) in the CLI docs.

## Scope

- Audit every `HOLON_*` read and every `add_argument` across `apps/sandbox-executor/src` (the table above is the
  starting inventory, not the proof), classify each knob into the five kinds, and implement the standardisation above.
- Tests (pytest only): precedence per paired option; truthy parsing; deprecation aliases; help text contains the env
  sentence for every paired option.
- Run through the Holon flow on holon-agentic-coder. Touches the `cli/` package and option helpers, so sequence with
  other `cli/` beans.

## Notes

- Spawned from the 0221b end-to-end test: the pre-flight hint also recommends `HOLON_AGENT_KEY` first, which is exactly
  the route that fails for a Claude subscription token — fold that hint correction in here.
- Related: 0172 (budget envs get explicit values/flags), 0219 (mandatory --agent/--model, merged), 0173 (layered .env).
