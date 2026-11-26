---
# holon-agentic-coder-ref-metadata-0174
title: "Document every environment variable holon reads, in one generated and CI-checked reference"
status: completed
type: task
priority: high
tags:
  - docs
  - configuration
  - holon-agentic-coder
created_at: 2026-10-27T14:08:31Z
updated_at: 2026-11-23T08:33:00Z
---

## Problem

There is no single reference for the environment variables that `holon` and its sandboxes read. An inventory of
holon-agentic-coder `main` (`fbd3b35`, 2026-10-28) covered `apps/sandbox-executor/src`, `entrypoint/`, the Dockerfile,
the bake file, the `Makefile` and `.github/workflows`. It found:

- **101 distinct environment variable names** in code and infrastructure, of which **61 are `HOLON_*`**. The rest are
  agent credentials and provider variables (`CLAUDE_*`, `ANTHROPIC_*`, `OPENAI_*`, `GEMINI_*`, `PI_*`, `CODEX_*`, …),
  GitHub (`GITHUB_TOKEN`, `GH_*`), proxy (`HTTP(S)_PROXY`, `NO_PROXY`) and `GIT_*`.
- **44 `HOLON_*` names mentioned in docs**, spread over at least 10 files (`README.md`, `docs/budgets.md`,
  `docs/agents.md`, `docs/executor/agent_credentials_requirements.md`, the execution spec, `git_flow.md`, the intent
  spec, `ledger_schema.md`, the token-reduction A/B doc, an audit report).
- **19 `HOLON_*` variables read in code but named in no doc**, for example `HOLON_ACTION_LOGGING`,
  `HOLON_ACTION_ORIGIN`, `HOLON_AGENT_ID`, `HOLON_AGENT_LOG_BYTES`, `HOLON_AGENT_SKIP_PERMISSIONS`,
  `HOLON_ANTIGRAVITY_SESSION_DIR`, `HOLON_CA_BUNDLE_PATH`, `HOLON_CA_SOURCES`, `HOLON_GIT_FETCH_RETRIES`,
  `HOLON_GIT_LOCK_AGE_SECONDS`, `HOLON_MITM_USER` and `HOLON_PR_HEAD_SHA`.

During the October flow runs this cost real time. Behaviour-changing settings were found by reading source:
`HOLON_TOKEN_REDUCE` (Bean 0157), the `HOLON_STAGE_BUDGET_*` variables (Beans 0171/0172), `HOLON_AGENT_SETTINGS`, and
`HOLON_AGENT_KEY` versus OAuth.

## Scope

1. **Inventory.** Enumerate every variable read or written by `holon` on the host, by the role containers (Python and
   `role_dispatcher.sh`), by the agent images, by CI and by the `Makefile`. Include non-`HOLON_` variables that holon
   reads, maps or forwards: credentials, provider, proxy, git.
2. **One reference doc** (for example `docs/environment_variables.md`, linked from the README and `docs/budgets.md`).
   One row per variable:
   - name;
   - purpose;
   - type and allowed values;
   - default;
   - unset behaviour, and how invalid values are handled;
   - which side reads it (host, container, both, CI);
   - whether it is forwarded to containers, and how (env-file or argv);
   - **secret: yes/no**;
   - since or related change.

   Group the rows by area: runner and agent, budgets, token reduction and proxy, git, ledger and actions, review loop,
   logging, CI-only. Mark internal or test-only variables as such instead of hiding them.

3. **Single source and a drift check.** Prefer a machine-readable registry in code (for example a typed table that
   `budgets.py`, `cli.py` and the agent runner use instead of string literals), with the doc generated from it. At
   minimum, add a hygiene-test that fails when code reads a `HOLON_*` name missing from the reference, or the reference
   lists one the code no longer reads. Run it in CI.
4. **Consistency fixes surfaced by the inventory.** Fix inconsistent naming (`_SECONDS` versus `_MINUTES`), duplicated
   parsing, and variables that are read but never forwarded to the containers that need them. Record any larger change
   as its own bean, not here.
5. Keep secret values out of examples, and use placeholders.

## Notes

- Run through the Holon flow on holon-agentic-coder. It is docs-heavy, plus a registry and a check. If a code registry
  is chosen, it overlaps `cli.py` and `budgets.py`, so sequence it accordingly.
- Natural precursor to Bean 0173: a layered `.env` needs the allow-list and the secret flags this reference defines.
  Also related: Beans 0172 (`unlimited` budgets), 0155 (forwarding on the docker argv) and 0157 (`HOLON_TOKEN_REDUCE`
  default).
- Inventory command used, for reproduction: grep for
  `(HOLON|GITHUB|GH|CLAUDE|ANTHROPIC|OPENAI|GEMINI|PI|CODEX|OPENCODE|AGY|HTTP|HTTPS|NO|GIT)_[A-Z0-9_]+` across those
  paths, and compare against the `HOLON_*` names in `docs/`, `README.md` and `apps/sandbox-executor/docs`.

- Progress (2026-11-23, flow resume): resumed Stage 3 from checkpoint with claude-agent / claude-opus-5-5 via
  `run_holon_flow.py --allow-overlap`. Blocked: the executor found no failed execution with partial work, then ran
  `git checkout -b` for a new E branch off the plan tip, and that failed, leaving the existing E-1795413310 branch (five
  execution commits, steps 1-5, no executions.jsonl row) and one uncommitted `executions/E-1795413310-CLA-CO5.5.md` in
  place. Stage 3 halted with no PR opened. Flow log: `todo/flow-document-env-variables-v2.log`. Not resolved by hand;
  needs the maintainer or a flow-resume fix before the flow can continue.

## Progress note (flow document-env-variables-v3)

- New flow from current main (intent document-env-variables-v3, claude-agent / claude-opus-5-5). The v2 attempt was left
  untouched.
- Intent, plan and execute completed. Review halted once on the conflict gate after main moved (PR #253 merge). Resumed
  from checkpoint; the new head approved 3/3 with CI green.
- Calibration included in PR diff. PR #256 is OPEN, MERGEABLE, CLEAN on head b62672ec. Awaiting human merge into main
  (not merged by the agent).

## Resolution

Delivered via [PR #256](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/256) and merged into `main`
(`c941d78`):

- **Key Architectural Deliverables**: one generated, CI-checked reference of every `HOLON_*` environment variable the
  sandbox executor reads, linked from the docs.
- **Flow history**: the first attempt (`document-env-variables-v2`) halted at Stage 3 with no PR. Its five unmerged
  execution commits and one uncommitted execution file were backed up to
  `todo/stale-worktree-backups/document-env-variables-v2-2026-11-23.bundle` and
  `todo/stale-worktree-backups/document-env-variables-v2-E-1795413310-CLA-CO5.5.uncommitted.md`, then its worktree and
  branches were removed. The v3 flow worktree and its branches were removed after the merge.
- **Holon Flow Traversal**: the v3 flow ran intent, plan and execute; review passed 3/3 after a resume from checkpoint;
  calibration was included in the PR.
