---
# holon-agentic-coder-ref-metadata-0173
title: "holon loads layered .env files (specific overrides broad) that every sandbox stage inherits"
status: todo
type: feature
priority: high
tags:
  - configuration
  - holon-flow
  - security
  - holon-agentic-coder
created_at: 2026-10-27T14:07:56Z
updated_at: 2026-10-27T14:10:09Z
---

## Problem

Every `holon flow` run in October 2026 depended on settings passed by hand through the harness wrapper
`todo/holon-stage.sh` and ad-hoc `export`s:

- **`HOLON_TOKEN_REDUCE=0`:** without it, the flow auto-starts an unreachable mitmproxy sidecar (Bean 0157).
- **Budget overrides:** `HOLON_STAGE_BUDGET_EXECUTE_MINUTES=120`, then `10080`, after Stage 3 hit its 45-minute budget
  (Beans 0171 and 0172).
- **The Claude OAuth token:** it is smuggled in as
  `HOLON_AGENT_SETTINGS='{"env":{"HOLON_ECHO_PAD":"<300 chars>","CLAUDE_CODE_OAUTH_TOKEN":"…"}}'`. The padding exists
  only to keep the token out of truncated command echoes, and `HOLON_AGENT_KEY` has to be unset.
- **The agent and model:** chosen on each command line.

`holon` has no configuration file. The only env-file in the code is the per-run, 0600 `docker --env-file` from #96,
which keeps forwarded values off the docker argv. Nothing persists a user's or a project's settings, so:

- every run has to repeat them;
- a forgotten variable silently changes behaviour (the sidecar);
- secrets travel through brittle workarounds.

## Scope

1. **Layered `.env` files, where the more specific environment always overrides the broader one** (maintainer rule,
   2026-10-28). Use the standard file name `.env` at every level.
   - **Resolution:** use the project's `.env`, falling back to the broader `.env` for any key the project file doesn't
     set. Each variable is resolved independently: the most specific layer that defines it wins, and broader layers only
     supply the keys it leaves unset.
   - **Layers, from broadest to most specific:**
     1. built-in defaults;
     2. user-wide `~/.holon/.env` (0600, outside any repository);
     3. project `<repo-root>/.env` (the target repository's own file, git-ignored);
     4. optional finer layers, if adopted, for example `<repo-root>/.env.<runner>` (such as `.env.claude-agent`) and
        `<repo-root>/.env.<stage>` (such as `.env.execute`). Define and document their order, each more specific than
        the project `.env`;
     5. the process environment;
     6. explicit CLI flags.
   - **Nothing broad overrides anything specific.** A user-wide value never beats a project value, and a file value
     never beats an exported variable or a flag.
   - **Unset versus empty:** an unset key falls back to the broader layer. Decide and document whether an empty value
     (`KEY=`) also falls back, or explicitly means "unset or default here" (relevant for Bean 0172's `unlimited`).
   - **Reporting:** `holon doctor` (and `--json`) prints every effective `HOLON_*` setting with the layer it came from
     and the layers it shadowed. It never prints secret values; it shows them as `set (layer)`.
2. **Format and parsing.** Use a strict `KEY=VALUE` dotenv subset: comments, blank lines, and optional single or double
   quotes. Do not expand variables or execute anything. Accept only `HOLON_*` keys plus an explicit allow-list of
   documented secret mappings. Reject anything else with a warning that names the key and never the value.
3. **Secrets out of the shared file.** Store credentials only in the user-level secrets location (today
   `~/.holon/secrets/`, 0600), referenced by name, for example
   `HOLON_AGENT_OAUTH_TOKEN_FILE=~/.holon/secrets/claude- oauth-token`. Add a first-class mapping from
   `HOLON_AGENT_OAUTH_TOKEN` to `CLAUDE_CODE_OAUTH_TOKEN` in the role dispatcher, replacing the `HOLON_AGENT_SETTINGS`
   and `HOLON_ECHO_PAD` workaround. If the project `.env` holds secrets, it must be git-ignored. Warn, or refuse, when
   it is tracked by git, and warn on group- or world-readable files at any layer.
4. **Inheritance by every sandbox.** Resolve the effective configuration once per `holon` invocation. Hand it to every
   role container (intent creator, planner, executor, review, calibration) and to nested invocations. Use the existing
   0600 env-file, never `-e KEY=value` on the argv (Bean 0155), and redact it in every echo and log.
5. **Template and docs.**
   - `holon init` scaffolds a commented `.env.example` and adds `.env` (and any finer `.env.*` layer, except
     `.env.example`) to `.gitignore`.
   - Document every supported key, its default, and whether it is secret.
   - Retire the need for the harness wrapper's env plumbing.
6. **Tests**, with temporary files only and no real credentials:
   - precedence across every layer, including a key set only in the broad layer, only in the specific layer, in both,
     and empty in the specific layer;
   - parsing edge cases;
   - the allow-list and rejection rules;
   - secret handling, including permission checks, no echo, and a redacted env-file;
   - the doctor source report;
   - container inheritance;
   - nested invocations.

## Notes

- Run through the Holon flow on holon-agentic-coder. It touches `cli.py`, `role_dispatcher.sh`, the agent runner and the
  docs, so run it sequentially and check for overlap with Beans 0155, 0157 and 0172.
- Related:
  - Bean 0143: its OAuth-mapping follow-up becomes part of this bean.
  - Bean 0155: credential values on the docker argv.
  - Bean 0157: sidecar auto-enable; with a `.env`, `HOLON_TOKEN_REDUCE` can be set once.
  - Bean 0172: an explicit `unlimited` budget, which would live in this file.
  - Bean 0156: if issue tracking moves to the targets, configuration should be target-native too.
