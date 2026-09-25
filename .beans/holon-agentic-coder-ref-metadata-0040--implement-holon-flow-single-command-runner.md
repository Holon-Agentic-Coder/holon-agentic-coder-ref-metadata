---
# holon-agentic-coder-ref-metadata-0040
title: "Implement holon flow unified single command CLI runner"
status: todo
type: task
priority: normal
tags:
  - cli
  - holon-flow
  - developer-experience
created_at: 2026-09-26T09:20:00Z
updated_at: 2026-09-26T15:20:00Z
---

Implement the `holon flow <intent_file>` subcommand in `sandbox_executor.cli` to trigger the end-to-end Holon lifecycle
(Intent -> Plan -> Execute -> PR Review Loop -> Calibrate) via a single CLI command.

## Context

With individual subcommands (`holon intent`, `holon plan`, `holon execute`, `holon calibrate`) and the flow
orchestration pipeline (Bean 0039), operators and agents need a streamlined single command entrypoint (`holon flow`) to
trigger full lifecycle runs with a single command line invocation.

## Acceptance Criteria

1. Implement `holon flow` subcommand in `apps/sandbox-executor/src/sandbox_executor/cli.py`:
   - Argument: `intent_file` (positional, required: path to intent JSON definition).
   - Option: `--agent <name>` (default: `antigravity-agent`).
   - Option: `--model <name>` (default: `gemini-3.5-flash`).
   - Option: `--token-reduce` (route sandbox network through local mitmproxy sidecar for prompt caching and context
     deduplication).
   - Option: `--mitm-web` (enable real-time mitmweb traffic inspector dashboard).
   - Option: `--skip-review` (flag to bypass the PR review loop stage).
   - Option: `--skip-calibrate` (flag to bypass post-execution calibration).
   - Option: `--max-review-iterations <N>` (pass-through iteration cap to review loop, default: 25).
2. Wire `holon flow` to invoke the automated pipeline engine from Bean 0039.
3. Stream structured progress indicators to stdout (e.g. `[1/5] Creating Intent...`, `[2/5] Generating Plan...`,
   `[3/5] Executing Plan...`, `[4/5] Running Review Loop...`, `[5/5] Calibrating Metrics...`).
4. Update `apps/sandbox-executor/README.md` and CLI `--help` text documenting `holon flow` usage, flags, and workflow.
5. Add unit and CLI argument parsing tests in `apps/sandbox-executor/tests/test_cli.py`.

## Status Verification (2026-09-26) -- largely delivered by Bean 0039, re-scoped to the remainder

Bean 0039 (merged as PR #58) already landed the `holon flow` subcommand and the pipeline engine it was meant to wrap, so
most of this bean's acceptance criteria are satisfied on `origin/main`:

| Original criterion                           | State on `origin/main`                                                                                                                                                                                   |
| -------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `holon flow` subcommand in `cli.py`          | done -- `cli.py:809` (`flow` parser), dispatched at `cli.py:862`, engine in `sandbox_executor/flow.py`                                                                                                   |
| Wire to the Bean 0039 pipeline engine        | done                                                                                                                                                                                                     |
| Structured stage progress on stdout          | done                                                                                                                                                                                                     |
| Unit + CLI parsing tests                     | done, but in `tests/test_flow.py` (`test_cli_flow_help`, `test_cli_flow_dry_run_dispatch`, `test_cli_flow_missing_intent_file`, `test_cli_flow_missing_checkpoint_file`) rather than `tests/test_cli.py` |
| `--agent`, `--model`                         | done (defaults `antigravity-agent` / `gemini-3.8-flash-medium`, not the `gemini-3.5-flash` written in this bean)                                                                                         |
| `--token-reduce`                             | **missing** as a CLI flag -- `FlowContext.token_reduce` exists in `flow.py` but is not exposed on `holon flow`                                                                                           |
| `--mitm-web`                                 | **missing**                                                                                                                                                                                              |
| `--skip-review` / `--skip-calibrate`         | **missing** (only `--from-stage` / `--checkpoint` can skip ahead)                                                                                                                                        |
| `--max-review-iterations <N>`                | **missing**                                                                                                                                                                                              |
| `apps/sandbox-executor/README.md` usage docs | **missing** -- that README does not exist, and `holon flow` is documented nowhere in the repo README or the `./holon` wrapper                                                                            |

Remaining scope for this bean is therefore: expose the five missing flags, plumb `--skip-review` / `--skip-calibrate`
into the engine's stage selection, document `holon flow`, and extend the CLI-surface tests. Extra flags already present
and worth keeping: `--from-stage`, `--checkpoint`, `--dry-run`, `--json`, `--repo-dir`, `--skip-push`.

Status stays `todo` (nothing in flight); it is now substantially smaller than originally scoped.

## Notes

- Target repository: `apps/holon-agentic-coder/`
- Target files:
  - `apps/sandbox-executor/src/sandbox_executor/cli.py`
  - `apps/sandbox-executor/README.md`
  - `apps/sandbox-executor/tests/test_cli.py`
- Dependencies: Bean 0038 (`holon calibrate`) and Bean 0039 (`automate holon flow`).
