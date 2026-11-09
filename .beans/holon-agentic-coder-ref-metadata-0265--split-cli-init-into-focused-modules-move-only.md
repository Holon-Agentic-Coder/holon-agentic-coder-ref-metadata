---
# holon-agentic-coder-ref-metadata-0265
title: "Split `cli/__init__.py` into focused modules (move only), like the `flow/` package"
status: todo
type: task
priority: high
tags:
  - cli
  - refactor
  - architecture
  - concurrency
  - holon-agentic-coder
created_at: 2026-11-09T10:30:00Z
updated_at: 2026-11-09T10:30:00Z
---

## Problem

`apps/sandbox-executor/src/sandbox_executor/cli/__init__.py` is **2,026 lines**: 80 top-level definitions and constants,
35 imports, and a 70-line `__all__`. Bean 0188 turned `cli.py` into a package with one module per subcommand under
`cli/commands/` (the largest, `flow.py`, is 335 lines), but everything those commands share stayed in `__init__.py`:
container launching, the token-reduction proxy sidecar, credentials, repository resolution, mounts, env files, the
doctor report and role dispatch. The largest definitions are `run_docker_container` (253 lines),
`setup_token_reduction_proxy` (188), `get_agent_session_mounts` (85), `run_doctor` (74), `detect_holon_coherence` (74),
`_attach_external_proxy` (62), `report_budgets_and_envelope` (58) and `get_host_proxy_envs` (52).

Consequences, as `flow.py` showed before Bean 0254:

- Any change to container launch, the proxy sidecar, credentials or the doctor report edits this one file, so concurrent
  flows touching different parts still collide (7 commits since 2026-10-01).
- 63 modules and tests import from `sandbox_executor.cli`, and tests patch **96** `sandbox_executor.cli.<name>` targets
  (`run_flow_pipeline` 21, `run_preflight_probe` 16, `detect_holon_coherence` 16, `run_docker_container` 14,
  `resolve_target_repo` 9, `get_agent_session_mounts` 8, ...). `tests/test_cli.py` is 2,427 lines.
- Reviewers and resolvers load 2,000 lines to change a 30-line function.

## Scope

### 1. Turn the contents of `cli/__init__.py` into focused modules, moving code only

No function, class or constant changes. Proposed layout (line ranges as of `main` at `61796c6`; the planner confirms the
boundaries and keeps each cluster together):

| Module                   | Definitions moved                                                                                                                                                                                                                             |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cli/log.py`             | `logger`, `PACKAGE_LOGGER_NAME`, `_CurrentStderrHandler`, `configure_cli_logging` (84–118). Not named `logging.py`, which would shadow the standard library.                                                                                  |
| `cli/constants.py`       | CA, proxy and env-flag constants (`CONTAINER_CA_DIR` ... `_EXPLICIT_OPT_OUT_VALUES`, 121–146), `INTENT_CREATOR_*`, `_AGENT_FLOW_STAGES`, `ENV_FILE_PREFIX`, `GIT_CREDENTIAL_HELPER`                                                           |
| `cli/network.py`         | `BLOCKED_METADATA_HOSTS`, `SINKHOLE_IP`, `build_network_isolation_args`, `_ensure_network`, `_published_loopback_port`, `_proxy_gateway_url`, `_gateway_host_args`, `_proxy_host_port`                                                        |
| `cli/credentials.py`     | `find_github_token`, `strip_url_credentials`, `credential_host`, `redact_cli_error`, `_url_env_credential_parts`, and their regex constants                                                                                                   |
| `cli/repo_resolution.py` | `normalize_repo_remote`, `_resolve_target_repo`, `resolve_target_repo`, `resolve_target_repo_url`, `_find_git_root`                                                                                                                           |
| `cli/mounts.py`          | `get_ssh_auth_mounts`, `get_agent_session_mounts`, `_container_ca_path`, `_ca_mount_args`, `_mitm_proxy_ca_paths`, `get_token_reduction_mounts_and_envs`                                                                                      |
| `cli/proxy_sidecar.py`   | `_SidecarState`, `_sidecar_state`, `_build_proxy_envs`, `detect_holon_coherence`, `_token_reduce_opt_in`, `_wait_for_proxy`, `setup_token_reduction_proxy`, `teardown_token_reduction_proxy`, `_attach_external_proxy`, `get_host_proxy_envs` |
| `cli/env_files.py`       | `env_file_dir`, `sweep_stale_env_files`, `write_env_file`, `is_secret_env_item`                                                                                                                                                               |
| `cli/containers.py`      | `_run_docker`, `run_docker_container`                                                                                                                                                                                                         |
| `cli/doctor.py`          | `print_encodable`, `_doctor_section_failed`, `report_budgets_and_envelope`, `_report_budgets`, `_report_gateways`, `run_doctor`                                                                                                               |
| `cli/role_dispatch.py`   | `resolve_role_image`, `dispatch_role_agent`, `resolve_runner_and_model`, `flow_dispatches_agent`, `preflight_gate`                                                                                                                            |
| `cli/parser.py`          | `build_parser`, `main`                                                                                                                                                                                                                        |
| `cli/__init__.py`        | Re-exports only (and the imports the commands read through `cli.<name>`), with `__all__`; no logic.                                                                                                                                           |

Module-level imports go to the module that uses them. Shared constants go in `cli/constants.py`. Avoid import cycles
between the new modules. Any module that still ends up over 200 lines (`proxy_sidecar.py` and `containers.py` will) is
recorded in the module size budget configuration at its post-split size and decomposed by later beans.

### 2. Keep every caller working

- `cli/__init__.py` re-exports every public name and every private name that other modules or tests import today, so the
  63 importing modules and tests need no edits in this PR.
- **Patch targets move.** Code in a new module looks names up in its own namespace, so patching the re-export at
  `sandbox_executor.cli.<name>` no longer intercepts calls made inside another submodule. Move each of the 96
  `mock.patch("sandbox_executor.cli.<name>")` targets to the module where the patched name is looked up at runtime
  (commands that call `cli.<name>(...)` through the package still resolve through the re-export and may keep patching
  it; the planner decides per name). Add a guard test that fails when a test patches a name at the package that a
  submodule looks up in its own namespace, as `tests/flow/test_patch_targets.py` does for the flow package.

### 3. Prove it is only a move, without leaving a snapshot behind

Do **not** commit an `ast.dump` snapshot or a permanent move-proof test: that pattern caused friction after the
`flow.py` split (see Bean 0263). Instead, ship a throwaway verification script (not part of the test suite and not
committed to the test directories) that parses the base branch's `cli/__init__.py` (`git show origin/main:<path>`, after
`git fetch origin main`, since sandbox clones are shallow) and every new module, and compares `ast.dump` of each
function, class and constant keyed by qualified name, reporting zero differences and zero missing or extra definitions.
The executor runs it and records the result in the execution notes, and the reviewers re-run it. Permanent tests are
limited to the patch-target guard and a re-export test whose expectations come from the package itself.

### 4. Split the tests to match

Split `tests/test_cli.py` (2,427 lines) into `tests/cli/test_<module>.py` mirroring the new layout, keeping
`tests/test_cli_options.py` where it is. The test count stays the same or grows, and the full suite passes via
`uv run pytest`.

### 5. Stop it growing back

Record the post-split sizes of the new `cli/` modules in the repository's module size budget mechanism (extend it to
cover the `cli` package; use whichever mechanism exists when this runs), and update `docs/architecture.md` with the
module map and a one-line responsibility per module.

## Touch set

`apps/sandbox-executor/src/sandbox_executor/cli/__init__.py` (reduced to re-exports), the new `cli/` modules,
`apps/sandbox-executor/tests/test_cli.py` (split into `tests/cli/`), the module size budget configuration,
`docs/architecture.md`.

## Dependencies and sequencing

- **Run alone with respect to `cli/` and `tests/test_cli.py`.** Hold until PR #152 (Bean 0262) merges: it edits
  `cli/commands/flow.py`, and Beans 0263 and 0264 edit `tests/flow/`, `docs/architecture.md` and the budget mechanism,
  so run this after them (or rebase onto them) to avoid conflicts.
- **Unblocks Bean 0189.** That bean moves container launch, role dispatch and the sidecar out of the CLI into a
  `launcher/` package and breaks the `flow`-`cli` import cycle. After this split, `cli/containers.py`,
  `cli/proxy_sidecar.py`, `cli/role_dispatch.py`, `cli/mounts.py`, `cli/env_files.py`, `cli/network.py` and
  `cli/credentials.py` are the modules it relocates, a much smaller and cleaner move. Re-read 0189's scope against the
  new layout before starting it. Sequence with Beans 0155, 0157 and 0227, which change the same functions.
- Does not change behaviour, so it does not conflict with Bean 0259's flow worktree rules.

## Acceptance criteria

1. `cli/__init__.py` holds only re-exports and `__all__`, and every existing import of `sandbox_executor.cli` still
   resolves.
2. The throwaway verification reports zero body differences and zero missing or extra definitions, and no snapshot or
   move-proof test is committed.
3. `tests/test_cli.py` is split into `tests/cli/`, with an equal or higher test count, and `uv run pytest` passes.
4. `uv run task lint` and `uv run task lint-docs` pass, including the size budget check at the recorded baseline.
5. No behaviour change: all CI checks pass.

## Notes

- Target repository changes in `holon-agentic-coder` must be delivered through the 5-stage Holon flow.
- Stage 3 output is large. Set `HOLON_STAGE_BUDGET_EXECUTE_MINUTES` generously.
- The intent JSON must not mention bean IDs or harness paths, because it is copied into `intents.jsonl`.
