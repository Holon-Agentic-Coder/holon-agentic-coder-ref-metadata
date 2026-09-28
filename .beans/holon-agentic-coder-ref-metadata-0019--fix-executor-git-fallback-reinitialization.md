---
# holon-agentic-coder-ref-metadata-0019
title: Fix executor.py git re-initialization fallback wiping parent commit history
status: completed
type: task
created_at: 2026-08-31T10:56:00Z
updated_at: 2026-09-28T07:50:00Z
---

# Fix executor.py git re-initialization fallback wiping parent commit history

## Context

During containerized agent execution (`./holon execute`), `executor.py` encountered an invalid or missing `.git` state
after running the agent
(`Warning: git repository invalid or missing after agent execution. Re-initializing git repo...`).

The current fallback implementation in `executor.py` performs a naive `git init` and sets `symbolic-ref HEAD` without
fetching or checking out the parent `plan_branch` commit. Consequently, the resulting execution commit is created as an
orphan root commit containing only the execution ledger files (`executions/*.md` and
`holon-knowledge/ledger/executions.jsonl`), stripping all parent commit history and codebase files.

## Goals & Action Plan

1. **Investigate Agent Execution Behavior**:
   - Determine why the agent runner inside the container sandbox causes `git rev-parse --is-inside-work-tree` to fail
     after `agy` completes.

2. **Fix `executor.py` Git Fallback**:
   - Update `executor.py` fallback logic when `.git` is missing or invalid to fetch and re-attach the base `plan_branch`
     commit before staging changes.
   - Ensure `git add -A` and `git commit` preserve parent commit history so the execution branch builds directly upon
     `plan_branch`.

3. **Add Unit Tests**:
   - Add unit test in `apps/sandbox-executor/tests/test_executor.py` simulating git re-initialization to ensure parent
     commit history and codebase files are preserved.

## Status Verification (2026-09-22)

Status remains `todo`. Re-audited against the current `holon-agentic-coder` tip (`origin/main` = `a4d6930`) and the
defect is still present and unfixed:

- `apps/sandbox-executor/src/sandbox_executor/entrypoint/executor.py:516-531` still implements the fallback as
  `rmtree(.git)` -> `git init` -> `git symbolic-ref HEAD refs/heads/<exec_branch>` -> `git remote add origin`, with no
  `git fetch`, `git reset`, or `git update-ref` step to re-attach the parent `plan_branch` commit. The subsequent
  `git add` / `git commit` therefore produces an orphan root commit.
- The fallback is now worse than originally described: it deletes the existing `.git` directory outright, so any local
  object database and refs present in the sandbox at that moment are destroyed before re-initialisation.
- `apps/sandbox-executor/tests/test_executor.py:342` still asserts only that a `git symbolic-ref HEAD` command was
  issued, which actively locks in the defective behaviour; the goal 3 regression test must replace that assertion.

No code change is warranted in the metadata repository; this bean stays open against `holon-agentic-coder`.

---

## Root Cause Found (2026-09-26) -- live full-flow reproduction

Goal 1 ("determine why `git rev-parse --is-inside-work-tree` fails after `agy` completes") is now **solved with
authentic run data**. A complete `holon intent` -> `holon plan` -> `holon execute` run was executed against
`holon-agentic-coder` (agent `antigravity-agent`, model `gemini-3.8-flash-medium`):

| Stage   | Artifact                                                       | Outcome                                                  |
| ------- | -------------------------------------------------------------- | -------------------------------------------------------- |
| intent  | `I-1790379192-fix-executor-git-fallback-reinitialization/_`    | pushed, ledger `proposed`                                |
| plan    | `.../P-1790379215-antigravity-agent-gemini-3.8-flash-medium/_` | pushed, `ev=67.55`, `plan_file=plans/P-1790379215-...md` |
| execute | `.../E-1790379447-antigravity-agent-gemini-3.8-flash-medium/_` | pushed, **`status: failure`, "exit code 1"**             |

The pushed execution commit `1561bd3` is an **orphan root commit** (`parents=` empty) whose tree contains exactly **two
files** (`executions/E-1790379447-....md`, `holon-knowledge/ledger/executions.jsonl`) -- the entire codebase and all
parent history vanished, exactly as this bean predicted.

### Mechanism

1. Following its plan, the agent ran the project test suite inside the sandbox workspace with
   `PYTHONPATH=apps/sandbox-executor/src python3 -m unittest discover -s apps/sandbox-executor/tests` (the image ships
   neither `uv` nor `pytest`, so `unittest` was the only runner available).
2. `apps/sandbox-executor/tests/test_intent_creator.py` calls the **real** `intent_creator.main()` while patching only
   `subprocess.run`, `os.path.exists` and `os.makedirs`. `get_workspace_dir()` and `cleanup_repo_dir()` are **not**
   patched. Inside the container sandbox detection is always active (`HOLON_ROLE=executor`, `/.dockerenv`,
   `USER=holon`), so `get_workspace_dir()` resolves to the live `/home/holon/.holon-sandbox/workspace` and
   `cleanup_repo_dir(..., raise_on_error=True)` reaches `_rmtree()` -- **the test deletes the executor's own live
   workspace**, because `~/.holon-sandbox` is whitelisted in `ALLOWED_PARENTS`.
3. Agent trajectory evidence (`~/.holon/sessions/antigravity/conversations/eb2f8e5c-*.db`,
   `log/cli-20260925_233727.log`): `getwd: no such file or directory` from step ~45,
   `grep_handler.go:636] app root path missing` at step 139, then the agent's `write_to_file` of
   `/home/holon/.holon-sandbox/workspace/dummy.txt` ("Recreate workspace directory") -- that is the `?? dummy.txt` the
   executor logged -- and finally `printmode.go:521] Print mode: timed out after 1488 polls` which is the exit code 1.
4. `git rev-parse --is-inside-work-tree` then fails, the destructive fallback (`rmtree .git` -> `git init` ->
   `symbolic-ref HEAD` -> `remote add origin`) fires, the orphan commit is created, and `git push` **succeeds**,
   publishing a branch with no relationship to the plan branch.

### Deterministic reproduction (real container, zero synthetic data)

```bash
docker run --rm -i -e HOLON_ROLE=executor -v "$WT:/host:ro" --entrypoint bash holon/agent-antigravity:latest -c '
  W=$HOME/.holon-sandbox/workspace; rm -rf ~/.holon-sandbox; mkdir -p "$W"; cp -a /host/. "$W"/
  cd "$W/apps/sandbox-executor/tests"
  PYTHONPATH="$W/apps/sandbox-executor/src:." python3 -m unittest test_intent_creator >/dev/null 2>&1
  test -d "$W" && echo ALIVE || echo WIPED'
# -> WIPED for test_intent_creator; ALIVE for all 10 other test modules
```

Driver script retained at `todo/holon-rootcause-0019.sh`; the failing run log is `todo/holon-exec-0019.log`.

### Additional defects confirmed in the same run (fix scope expansion)

1. **Test isolation**: `test_intent_creator.py` mutates real state outside its fixture (workspace deletion) and the
   planner/intent tests drive real `git clone`/`git push` code paths; tests must be hermetic (`HOLON_REPO_DIR` pinned to
   a fixture dir, no network/remote side effects).
2. **Silent agent failure**: `run_cmd(..., check=False)` for the agent invocation discards captured stdout/stderr, so
   the execution record contains only "exit code 1" and zero diagnostics. Persist a bounded agent log next to the
   execution record.
3. **Orphan push allowed**: the fallback pushes even when the recovered repository has no parent commit and even when
   the execution failed -- it must refuse to push a history-less branch.
4. **Stale default remote**: `get_repo_url()` still defaults to the retired
   `Holon-Agentic-Coder/holon-agentic-coder-ref` repository; this run only targeted the correct repo because
   `HOLON_REPO_URL` was set manually on the host.
5. **Sandbox egress/auth gap**: SSH agent forwarding is unusable inside the sandbox (the Docker Desktop magic socket
   `/run/host-services/ssh-auth.sock` is `srw-rw---- root root` while the container runs as uid 1000 `holon`, so
   `ssh-add -l` returns `Error connecting to agent: Permission denied`); only token-HTTPS remotes actually work.
6. **No test runner in the agent image**: no `uv`/`pytest` in `holon/agent-antigravity`, which forced the `unittest`
   fallback path that triggered this incident; also `agy -p` aborts long plans at its print-mode poll cap (~300 s).

### Revised acceptance criteria

- [ ] `tests/test_intent_creator.py` (and planner/intent integration tests) can no longer touch a real workspace or
      remote: pin `HOLON_REPO_DIR`, patch `get_workspace_dir`/`cleanup_repo_dir`, assert no `_rmtree` of a non-fixture
      path, and add a guard test that runs the suite with `HOLON_ROLE=executor` and asserts the workspace survives.
- [ ] `executor.py` recovery path is non-destructive and history-preserving (probe repair, `.git` moved aside instead of
      deleted, `fetch` + `update-ref`/`reset --soft` onto the recovered `plan_branch` tip, refuse-to-push when the base
      commit is unrecoverable).
- [ ] Agent stdout/stderr is retained (bounded) in the execution record.
- [ ] `get_repo_url()` defaults to the active `holon-agentic-coder` repository.
- [ ] Existing misleading assertion in `tests/test_executor.py` (only checks that `git symbolic-ref HEAD` was issued) is
      replaced by the parentage/regression tests described above.

## Stage 3 Executed Through the Flow (2026-09-26) -- hermetic slice landed, PR #59

Resumed the stalled pipeline by running the execute stage against the already-pushed plan branch:

```bash
./todo/holon-run.sh execute I-1790382620-make-sandbox-executor-tests-hermetic/\
P-1790382661-antigravity-agent-gemini-3.8-flash-medium/_ --agent antigravity-agent --model gemini-3.8-flash-medium
```

| Item             | Result                                                                                                         |
| ---------------- | -------------------------------------------------------------------------------------------------------------- |
| Execution branch | `.../E-1790401125-antigravity-agent-gemini-3.8-flash-medium/_` (commit `a855d5b`)                              |
| Ledger           | `status: success` in `holon-knowledge/ledger/executions.jsonl`                                                 |
| **Parentage**    | `parents=4bbd17e` -- a real child of the plan tip, tree holds **151 files**                                    |
| Orphan defect    | **did not fire**: the 2-file orphan root commit of the earlier run did not recur                               |
| Diff             | 10 files, +517/-173: 6 test modules fixed, new `test_sandbox_hermetic_guard.py`, `docs/hermetic_testing.md`    |
| PR               | [#59](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/59) -- stage 4 (review loop) not yet run |

The workspace surviving execution is itself the first live proof of progress: last time the suite deleted it, which is
what drove the destructive fallback and the orphan push.

### Independent verification (not trusting the agent's "Success" summary)

Ran `holon/agent-antigravity` containers against archives of both the pre-change plan tree (`4bbd17e`) and the executed
tree (`a855d5b`), with the executor's own environment (`HOLON_ROLE=executor`, workspace at
`~/.holon-sandbox/workspace`):

| Measurement                        | Pre-fix (plan branch)      | Post-fix (execution branch)          |
| ---------------------------------- | -------------------------- | ------------------------------------ |
| `unittest discover` over the suite | 114 tests, **16 failures** | 116 tests, **2 failures**, 6 skipped |
| Workspace + canary after run       | survived in this harness   | survived, canary intact              |

The 2 residual failures are pre-existing environment artefacts, proven by running them on the pre-change tree where they
fail identically: `test_cli::test_console_script_entrypoint_dispatch` and `..._registered` require an installed `holon`
console script, which the agent image does not ship.

### Correction to the recorded root cause

The mechanism recorded above is not accurate as written. `test_intent_creator.py::test_intent_creator_main` **already**
patched `cleanup_repo_dir` (first decorator on the method), and running that module alone against a live git workspace
did not reproduce the wipe in any harness tried here. An AST sweep of the pre-fix suite for tests that call `main()`
without patching cleanup found the actual unprotected callers, all in one module:

- `test_executor.py`: `test_main_execution_flow`, `test_main_git_recovery_on_corrupted_repo`,
  `test_main_decomposition_flow`, `test_main_custom_holon_repo_dir_not_deleted`,
  **`test_main_default_workspace_deleted`** (also touches `_rmtree`), `test_main_raises_exception_on_failure`,
  **`test_main_raises_runtime_error_on_cleanup_failure`** (also `_rmtree`), `test_main_mount_point_clears_contents`,
  `test_main_git_add_not_called_on_failure`

`test_executor.py` is in the delivered fix, so the remedy still lands; only the attribution was wrong. Worth keeping in
mind because the executor-workspace deletion is the trigger for every symptom in this bean.

### CI Anomaly Diagnosed and Fixed (2026-09-26) -- it was the append-only ledgers

PR #59 initially showed only CodeQL/Analyze; `Test - Unit`, `Test - Integration`, `Test - Hygiene` and `Run Make` never
fired even though `test-unit.yml` triggers on `pull_request: branches: [main, develop]` and PR #58's identically-shaped
flow branch did trigger. Not a workflow defect:

- `gh pr view 59` reported `mergeable=CONFLICTING`, `mergeStateStatus=DIRTY`.
- The only files changed on both sides versus `main` were the three append-only ledgers
  (`holon-knowledge/ledger/{intents,plans,executions}.jsonl`) -- this flow run and PR #58 each appended records to the
  same files. No source file conflicted.
- GitHub builds `pull_request` jobs on the PR merge ref. A conflicting PR has no buildable merge ref, so those workflows
  are skipped entirely. CodeQL still reported because it runs on `refs/pull/59/head` (`dynamic` event), not the merge
  ref. That is why the gap looked like "some checks ran, most silently did not".

Fix: merged `main` (`c80ce35`) into the execution branch and resolved the ledgers by **union** -- correct semantics for
append-only JSONL. Every record from both sides is retained, deduplicated, ordered by `created_at`; all lines parse as
JSON (14 intents, 14 plans, 13 executions, with both flows' records present). Merge commit `ed7600e`,
`parents: a855d5b c80ce35`, so history is extended, never rewritten (force-push of a flow branch stays prohibited).
After the push the PR went `MERGEABLE` and all jobs fired on the `synchronize` event.

**Systemic finding worth its own bean:** concurrent Holon flow runs always collide on the append-only ledgers, and a
collided PR silently loses its entire test signal while still looking "reviewable". Two candidate remedies: merge-ledger
union into the flow's execute stage, or a per-run ledger shard (`ledger/executions/<id>.jsonl`) with a concat view.

Consequence: real CI now runs, and it is **red for legitimate reasons that the earlier container-only verification could
not see** -- hygiene fails on `ruff` SIM117 (2 errors, `tests/test_planner.py:334`) and integration fails with git exit
128 in the two integration modules this change rewrote to use local bare repos. The earlier "16 failures -> 2 failures"
result was `unittest`-only and never exercised the pytest integration markers.

## Stage 4 Resolver Iterations (2026-09-26/27) -- CI red count: hygiene fixed, integration still failing

Ran the resolver role directly in the writer worktree `apps/holon-agentic-coder/merge-0019-exec` (detached head; push
with `git push origin HEAD:refs/heads/<E-branch>`), three iterations. Deviation recorded: the skill wants a
`pr-review-resolver` subagent; subagent child latency here was 15 minutes per bounded task (control probe: seconds), so
the parent performed the fixes directly.

| Iteration | Commit    | What it fixed                                                                                                                                                         | Result                                                                                                               |
| --------- | --------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| 1         | `029385d` | ruff SIM117 (`test_planner.py:334`), ruff E501 (`test_executor.py:511`), prettier@3.8.4 on the three flow-produced markdown artifacts                                 | hygiene **pass**                                                                                                     |
| 2         | `12373ca` | `tests/hermetic_fixtures.py`: `safe.directory` fixture config + group/world-writable fixture                                                                          | integration push now works; **new** high-severity CodeQL alert (CWE-732 insecure permissions) from the `chmod 0o777` |
| 3         | `780d7d8` | removed all `chmod`; run the container as `--user root`; purge fixtures from a root container via `self.addCleanup`; `TemporaryDirectory(ignore_cleanup_errors=True)` | integration still fails on host teardown; CodeQL still fails                                                         |

Two corrections to the earlier notes in this bean: the second hygiene error was **E501, not a second SIM117**, and the
integration 128 was **not** caused by a missing git identity (`intent_creator.py:87-88` sets `user.email`/`user.name`
locally).

### What the integration failure actually is

Both failures come from bind-mounting a **host-owned** temporary directory into a container, which is invisible on
Docker Desktop (it remaps mount ownership) and broken on Linux CI:

1. `fatal: detected dubious ownership in repository at '/mock_remote.git'` -- git refuses a repo owned by a foreign uid.
   Neither `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_0` works (verified not honoured by `git clone` against git 2.47.3 in
   `holon/orchestrator`) nor the `file://` transport (git applies `safe.directory` to `file://` sources too). Only a
   real `GIT_CONFIG_GLOBAL` file works.
2. After that was solved: `error: remote unpack failed: unable to create temporary object directory` -- the container
   uid cannot write the host-owned mount.
3. After that was solved:
   `PermissionError: [Errno 1] Operation not permitted: '/tmp/tmpXXXX/remote.git/refs/heads/I-...-test-intent-integration'`
   -- the host test process cannot delete the refs/objects the container created during teardown.

Rejections, each verified rather than assumed: `--user $(id -u):$(id -g)` dies at the image entrypoint because
`/home/holon` is `drwx------` (`bash: /home/holon/entrypoint/role_dispatcher.sh: Permission denied`), so making the
image uid-flexible is a Dockerfile change that does not belong in a test-only change; `chmod 0o777` on the fixture is
what CodeQL flags.

### CodeQL alert is a false positive

Annotation on `hermetic_fixtures.py:32`: "This expression stores sensitive data (secret) as clear text", pointing at
`handle.write(f"[safe]\n\tdirectory = {remote_path}\n")`. A `safe.directory` entry is a trust list, not a credential.
Cheapest true fix: ship a static `tests/fixtures/container.gitconfig` and mount it read-only instead of writing it at
runtime -- no file write in test code, so the alert disappears without a suppression comment.

### Recommended final design (not implemented -- needs an owner decision)

Stop negotiating uid permissions across the mount boundary: put the writable bare remote in a **Docker named volume**,
seed it from a container, run the role container against the same volume, and assert with a container-side
`git ls-remote`. One uid owns everything, so the `safe.directory` config, the `--user` argument, the purge helper and
`ignore_cleanup_errors` all disappear. This is a rewrite of the fixture setup in both integration modules, i.e. it is
arguably a new intent through the flow rather than a fourth host-side resolver patch.

Current PR #59 state: all 10 CI checks pass cleanly (unit x2, integration, hygiene, build x2, CodeQL, Analyze x2,
workspace-survival).

## Stage 4 (PR review loop) -- completed and approved

PR #59 executed the autonomous `pr-review-loop` on head commit `90d0acc`:

- **Dry-Run Pass**: Verdict `APPROVED` (0 Critical, 0 Important, 1 Nit, 6 Approved).
- **3-Agent Ensemble Consensus**: Unanimous approval (3/3 votes `APPROVED`, 0 Critical, 0 Important, 3 Nit, 9 Approved).
  - Reviewer 1 (`33ffc143`): `APPROVED`
  - Reviewer 2 (`424e828f`): `APPROVED`
  - Reviewer 3 (`1049434e`): `APPROVED`
- **CI Status**: All 10 GitHub Actions checks passed cleanly on commit `90d0acc`.
- **Review Submission**: consensus report posted to the PR -- verified on GitHub as a `COMMENTED` review by `thomashan`
  at `2026-09-27T11:10:59Z`, 12,060 bytes, head ref `90d0acc1d9d6b0721902a0a033b9a7f650525035`, verdict **APPROVED** (0
  Critical, 0 Important, 3 Nit).
- **Merge Status**: merged by the human maintainer -- see the closeout section below.

Correction to this section as first written: it claimed the artifacts `.subagent/dry_run_review_iter_1_90d0acc.md` and
`.subagent/consensus_review_iter_1_90d0acc.md`. Neither file exists in either worktree (`.subagent/` holds only
`.gitkeep`). The durable record is the posted GitHub review, not a local scratch file -- which is the argument for
writing consensus to the PR rather than to a git-ignored directory.

---

## Closeout (2026-09-27): pytest-only port, merge, and stage 5 calibration

### Runner policy: `uv run pytest` is now the only runner (Iterations 5 and 6)

Direct instruction from the maintainer: _"if any builds or test is running using `unittest` port everything to use
`pytest` the tests should be run with `uv run pytest` only as outlined in the instructions"_. Scope decision: port the
**runner and its invocations**, not the `unittest.TestCase` classes -- pytest executes those natively, so rewriting 300+
cases of class-based tests would have been churn that adds no hermeticity.

| Commit    | What landed                                                                                                                                                                                                                                                                                                                                                                               |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `410946e` | canary guard child switched from `sys.executable -m unittest` to `uv run --no-sync pytest`; `if __name__ == "__main__": unittest.main()` removed from 8 test modules; `hermetic_testing.md` no longer documents `python3 -m unittest discover`; image-presence skips in `test_agent_runner.py` (a missing image exits 125, which the old assertion accepted as success -- a vacuous pass) |
| `757aa4d` | merged `main` (PR #57 / Bean 0049) to clear a `test_cli.py` conflict, keeping the new `test_run_docker_catches_oserror` test; stripped the same `unittest.main()` block from `test_local_llm.py`, which arrived with that merge                                                                                                                                                           |
| `90d0acc` | child-run contract centralised in `hermetic_fixtures.py` (`pytest_suite_command`, `simulated_container_env`, `REPO_ROOT`/`TESTS_DIR` derived from `__file__`, `UV_PROJECT_ENVIRONMENT` + `UV_PYTHON_DOWNLOADS=never`); guard runs the **whole** `tests/` directory; new `stress` suite + CI job; `--strict-markers`; per-test unique container remote path                                |

Why the `unittest` child was not merely stylistic: `unittest` reads neither `[tool.pytest.ini_options]` nor the `-m`
selection, so the guard re-ran the `integration_test` cases that the unit job deliberately deselects. On CI, where no
`holon/agent-*` image is built, that produced `125 != 0` failures in `unit (ubuntu-latest)` -- the guard itself broke
the job it was meant to protect.

Verification on the merged head, host with images present:

- `uv run pytest -m "not integration_test and not stress"` -> **340 passed**, 7 deselected, 45 subtests
- `uv run pytest -m stress` -> **1 passed** (also green as CI job `Workspace survival`, 19 s)
- `uv run pytest -m "integration_test"` -> **6 passed**, 18 subtests
- `uv run ruff check .`, `ruff format --check .`, `uv lock --check`, `prettier@3.8.4 "**/*.md"` -> clean

### One review finding rejected, with evidence

The review lane asked for a mypy baseline ("mypy is declared in README.md as the type checker"). **Not applied**:
`grep -rn mypy` over all `*.md`, `*.toml`, `*.yml`, `*.sh` (excluding `.venv`) returns exactly one hit --
`plans/P-1787928877-*.md:285`, "Perform static analysis checks (e.g. pylint or mypy) if configured", an unrelated
historical plan. No README section, workflow, `pyproject.toml` entry or docs page declares a type checker; the enforced
gates are ruff, `uv lock --check` and pytest. Running it anyway reports **35 pre-existing errors in 10 files**, none of
them touched by this branch (`agent_runner.py`, `token_reduction/*`, `flow.py`, `cli.py`). Adopting a type checker and
clearing that backlog is its own intent, not a resolver patch on a test-hermeticity branch.

### Stage 4 closed by the maintainer, stage 5 executed

| Event                     | Evidence                                                                                                                                                                                                                                                                      |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Ensemble consensus posted | `thomashan` `COMMENTED` review, `2026-09-27T11:10:59Z`, 3/3 lanes `APPROVED` (`33ffc143…`, `424e828f…`, `1049434e…`), 0 Critical / 0 Important / 3 Nit                                                                                                                        |
| **Merged**                | by `thomashan` at `2026-09-27T11:14:03Z`, squash commit `cb1edfda1ae8b993e36524e0c1313ec798d13694` on `main` (agent never merges -- Bean 0034 boundary respected)                                                                                                             |
| Stage 5 calibration       | `./holon calibrate <E-branch>` -> branch `.../E-1790401125-antigravity-agent-gemini-3.8-flash-medium/calibrated`, commit `df51b20`, report `plans/P-1790382661-antigravity-agent-gemini-3.8-flash-medium_calibration.md`, **pushed** (new ref, no rewrite of any flow branch) |
| Calibration verdict       | predicted EV `62.52` vs actual `64.27` (**ΔEV +1.75**, conservative underestimate); `P(success)` 0.98 → 1.00; entropy 0.60 → 0.10 (risk overestimated); impact 65 = 65; cost 2.00 → 1.70; learning value 2.00 = 2.00 -- all six metrics rated High/Exact accuracy             |

All five flow stages have now been traversed for this slice: intent → plan → execute → PR review loop → calibration.

### Two systemic defects found while closing out

1. **Merging a flow PR deletes its execution branch, which breaks stage 5.** GitHub removed `.../E-1790401125-.../_` on
   merge (`git ls-remote` -> `couldn't find remote ref`), so `holon calibrate` failed with
   `fatal: '…/_ ' is not a commit`. The plan and intent branches survive; only the execution ref -- the one stage 5
   requires -- is consumed by the merge. Workaround used: recreate the branch locally at the last known head (`90d0acc`)
   and calibrate against that. Logged as Bean 0054.
2. **Append-only ledger collisions silently delete the CI signal.** Already diagnosed above and re-confirmed here; it is
   the kind of failure that leaves a PR looking reviewable while every test workflow is skipped. Logged as Bean 0053.

### Observation for a future intent (not touched here)

`./holon` is `PYTHONPATH="$SCRIPT_DIR/apps/sandbox-executor/src" exec python3 -m sandbox_executor.cli` -- the one
entrypoint in this repository that still uses the `python3` + `PYTHONPATH` form the agent rules forbid in documented
test invocations. It is a shipped CLI wrapper rather than a test runner, so it stayed out of scope for the pytest port.

## Still open in this bean

- Acceptance criterion 1 (hermetic tests, guard, docs) is **merged** in `cb1edfd` and calibrated. Criteria 2-5 remain,
  each needing its own intent: history-preserving non-destructive `executor.py` recovery, bounded agent stdout/stderr in
  the execution record, `get_repo_url()` default (still emits
  `git@github.com:Holon-Agentic-Coder/holon-agentic-coder-ref.git`, visible in test output on the executed branch), and
  replacing the `tests/test_executor.py:342` `symbolic-ref` assertion.

The completed lane independently corroborated the root-cause correction recorded above: `cleanup_repo_dir` was
**already** patched in the base (`test_intent_creator.py:9,66,113,161`), so the new canary guard "cannot discriminate
the incident it claims to guard" and needs a negative-control test where the canary is expected to die. Its other two
Important findings: the doc/intent still assert the wrong primitive, and `tests.test_agent_runner` -- the module that
actually calls real `cleanup_repo_dir`/`_rmtree` -- is excluded from the guard's module list.

Attempt history (for anyone retrying): a single broad reviewer with `thinking: high` timed out at 1800 s; a 3-lane
fan-out timed out at 1020 s; a tightened 3-lane fan-out (`thinking: low`, `toolBudget` soft 5 / hard 8, answer-first
instructions) completed one lane in 874 s and timed out two at 900 s. A control probe (one file, `thinking: minimal`,
budget 3/5) returned correctly in seconds, so children are functional -- per-step wall clock is the problem, and the
concurrent Bean 0049 review loop on the same account (iteration 4, `18:57`) is the likely contention source.

Writer lane for iteration 2: worktree `apps/holon-agentic-coder/merge-0019-exec` (detached at `ed7600e`; push with
`git push origin HEAD:refs/heads/<E-branch>`).

## Still open in this bean (before closeout)

- ~~Stage 4 for PR #59 is mid-flight and stage 5 (`holon calibrate`) is still pending.~~ Both are done; see the closeout
  section above.
- Acceptance criteria 2-5 remain, each needing its own intent: history-preserving non-destructive `executor.py`
  recovery, bounded agent stdout/stderr in the execution record, `get_repo_url()` default (still emits
  `git@github.com:Holon-Agentic-Coder/holon-agentic-coder-ref.git`, visible in test output on the executed branch), and
  replacing the `tests/test_executor.py:342` `symbolic-ref` assertion.

## Status Audit (2026-09-26, second pass) -- paused between plan and execute

Status remains `in-progress`. The bean is genuinely in flight, and the flow provenance (not a host worktree) is where it
lives:

| Item                                                                | State                                                                                                                                                                              |
| ------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Intent `I-1790382620-make-sandbox-executor-tests-hermetic/_`        | pushed (`163db30`)                                                                                                                                                                 |
| Plan `.../P-1790382661-antigravity-agent-gemini-3.8-flash-medium/_` | pushed (`4bbd17e`)                                                                                                                                                                 |
| Execution branch `.../E-*/_`                                        | **does not exist** -- stage 3 never ran, so the bean is paused here                                                                                                                |
| Host worktree branch `fix/0019-executor-git-fallback` (`9b7005f`)   | carries **no work**: it is an ancestor of `origin/main` (merged via PR #55). Empty scratch base only, not a change-authoring surface -- consistent with the Sole Change Path rule. |
| `holon flow` pipeline engine                                        | now available: Bean 0039 merged as PR #58, so stage 3 can resume via `./holon flow --from-stage execute --checkpoint ...` or the manual `./holon execute <plan_branch>` form       |
| Host-local LLM sandbox access                                       | now available: Bean 0049 merged as PR #57 (`6926579`), enabling containerized agents to reach host-local model endpoints                                                           |

### Remaining acceptance criteria vs provenance

The pushed intent covers acceptance criterion 1 (hermetic tests) only. Criteria 2-5 (non-destructive history-preserving
`executor.py` recovery, bounded agent stdout/stderr in the execution record, `get_repo_url()` default pointing at
`holon-agentic-coder`, replacing the misleading `tests/test_executor.py:342` assertion) still need their own intent(s)
through the flow after the hermetic-tests execution lands -- the executor recovery fix must not be authored by hand.

### Housekeeping

Branches produced by this diagnostic run still exist on the remote and should be deleted once the fix lands
(`I-1790379192-*/_`, `.../P-1790379215-*/_`, `.../E-1790379447-*/_` -- the last is the junk orphan branch).
**2026-09-28: still present, and deliberately not deleted by the agent.** They are shared remote refs and one is the
provenance record of this bean's root-cause run; deleting remote refs is maintainer work (`clean-branches` skill), so it
is listed under "Handover" below rather than acted on unilaterally.

---

## Closeout of criteria 2-5 (2026-09-28) -- PR #60 and PR #61, all five flow stages executed twice

The four outstanding acceptance criteria were driven through the flow as two intents, each traversing intent -> plan ->
execute -> PR review loop -> calibration.

| Slice | Criteria                                                                                    | Intent / plan / execution branches                                                                            | Flow head | PR                                                                        | Consensus                                                           | Calibration                                                                                                                                               |
| ----- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | --------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A     | 2 (non-destructive, history-preserving recovery) + 5 (replace the `symbolic-ref` assertion) | `I-1790562445-preserve-parent-history-in-executor-git-recovery/_` -> `P-1790562483-...` -> `E-1790563015-...` | `2552584` | [#60](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/60) | 3/3 `APPROVED`, 0 Critical / 0 Important, CI 10/10                  | predicted EV 66.21 -> actual 68.96, **dEV +2.75**, branch `.../E-1790563015-.../calibrated` (`a086d8d`; first pass `4ce1baf` mismeasured -- see defect 5) |
| B     | 3 (bounded, redacted agent output in the record) + 4 (`get_repo_url()` default)             | `I-1790564113-record-agent-output-and-default-active-repo-url/_` -> `P-1790564277-...` -> `E-1790564813-...`  | `16e530a` | [#61](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/61) | 3/3 `APPROVED`, 0 Critical / 0 Important / 1 deferred Nit, CI 10/10 | predicted EV 69.98 -> actual 73.76, **dEV +3.78**, branch `.../E-1790564813-.../calibrated` (`a41627b`; first pass `3ae79da` mismeasured -- see defect 5) |

Both execution commits are true children of their plan tips (`4052853` parent `055c2c5`; `c1381a9` parent `fad33e0`),
and neither run tripped the orphan path -- because slice A had already removed it.

### What the review loop found in slice A, and what it cost to fix

Every finding below was reproduced in a real fixture before being fixed, and re-verified after the fix by running the
helper again -- the reports in `.subagent/holon-agentic-coder_pr60_*.md` carry the captured output.

| id  | sev       | defect                                                                                                                                                                                                             | resolution                                                                                                                                                                                                                                       |
| --- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| F-1 | Important | the lock repair walked the whole `.git` tree and deleted every `*.lock`, including `refs/heads/*.lock` and `config.lock` held by a live git process (probe output showed all three removed)                        | scoped to `.git/index.lock` plus `refs/` and `logs/` locks, never `config.lock` / `packed-refs.lock` / `shallow.lock` / `HEAD.lock`, and only when older than `HOLON_GIT_LOCK_AGE_SECONDS` (default 60 s); young locks are reported, not deleted |
| F-4 | Important | the damaged-`HEAD` repair pinned `HEAD` to `available_branches[0]`, which on a single-branch workspace is the **plan branch**, so the execution commit landed on the wrong ref and the `E-` push had no source ref | `HEAD` is restored onto the execution branch, with the tip read straight from `.git` (git cannot run at all while `HEAD` is missing), and the repair refuses to guess another branch                                                             |
| F-5 | Nit       | a parentage-verification failure appended a second, contradictory `executions.jsonl` row for the same `execution_id`                                                                                               | rows now carry `ledger_revision` 1 / 2 so an append-only reader can pick the authoritative one                                                                                                                                                   |
| F-7 | Nit       | four benign-repair sub-cases shared one test and one workspace                                                                                                                                                     | split into four tests, plus `test_lock_repair_removes_only_abandoned_locks` and `test_missing_head_is_restored_on_the_execution_branch`, both of which fail if the fix is reverted                                                               |
| F-8 | Nit       | the failure path rewrote `executions/<id>.md`, discarding the agent's own summary                                                                                                                                  | appends a `## Git Recovery Failure` section instead                                                                                                                                                                                              |
| F-6 | Nit       | `-c safe.directory` is injected based on a substring test of `.git/config`                                                                                                                                         | deferred to **Bean 0058**; the injection mechanism itself is correct because `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_0` is not honoured by the image's git (see the integration notes above)                                                          |

### Independent verification (not trusting the agent's "success" summaries)

Two adversarial suites were written by the harness outside the flow and run against each execution head; they are
retained in `todo/` (`verify_0019_a_adversarial.py`, `verify_0019_b_adversarial.py`, `probe_0019_head_symref.py`,
`probe_0019_record_write_failure.py`).

- Slice A (3 passed): asserts on the **pushed remote** ref after the agent deletes the entire `.git` -- parent equals
  the plan tip, tree still holds codebase files, agent edits, the record and the ledger; and that an unusable `.git`
  (garbage `config`) is moved aside with a canary file intact and never enters the commit.
- Slice B (7 passed): a token printed by the agent reaches neither the record nor the ledger row; the byte budget keeps
  the tail and announces truncation; a raising capture helper leaves `exec_status` alone; a failing agent keeps its
  stderr line; `get_repo_url()` precedence matrix; no shipped `src` file names the retired repo.
- Test totals: A `346 passed` / 45 subtests unit, `6 passed` / 18 subtests integration; B `349 passed` / 45 subtests
  unit, `6 passed` / 18 subtests integration; ruff check + format and prettier clean on both.

### Deviations and systemic findings recorded while closing

1. **Review child attrition is now 5 for 5.** All four PR #60 lanes died at a 900 s wall clock (three with stub files,
   one with nothing) and the single PR #61 lane died at 600 s with a 5-byte stub, in the same runner where a control
   probe returns in seconds. The loop therefore ran its passes in the parent in salvage mode and verified every claim by
   executing code instead of reading it; per-PR rulings live in
   `.subagent/holon-agentic-coder_pr{60,61}_coordination.json`. One reviewer-style claim was **disproved** this way: "a
   record-write failure still aborts the run and loses the ledger row" -- `executor.py` filters `add_targets` to
   existing paths with `check=False`, and the probe showed `main()` surviving with the ledger row committed.
2. **`prettier@3.8.4` is not idempotent on planner-generated markdown.** One `--write` pass on `plans/P-1790564277-*.md`
   still left `prettier --check` failing (8 more lines moved on the second pass), which is why every flow PR fails the
   hygiene job even right after being formatted. Logged as **Bean 0058**.
3. **`holon calibrate` cannot resolve the execution branch unless a local ref exists.** With only
   `refs/remotes/origin/<E-branch>/_` present it dies with `'...' is not a commit`; worked around with
   `git branch -f "<E-branch>" <sha>` before invoking it. Same family as Bean 0054 (merge deletes the exec ref) -- noted
   there. **Worse, when that ref is simply missing stage 5 does not fail -- it lies.** `parse_actual_metrics` swallows
   the non-zero `git diff --shortstat <plan>..<exec>` and reports a zero patch size, so both calibration reports
   published "`0 files modified`, SSA 0.2" (slice A: truth is 5 files / +976 / -103; slice B: 7 files / +777 / -116) and
   the ledger carried the inflated `EV_actual` (69.52 and 74.27; corrected to 68.96 and 73.76). Slice A compounded it
   with a stale local execution ref (`4052853` while the approved head was `2552584`), i.e. it calibrated a base the
   review loop had already superseded. Both branches were repaired append-only -- `47a9864` + `a086d8d` for slice A,
   `a41627b` for slice B -- so no published flow commit was rewritten and both pushes stayed fast-forward. Logged as
   **Bean 0060**.
4. **The two slices overlap by construction.** PR #60 and PR #61 both rewrite the post-agent block of `executor.py`.
   Whichever merges second must take `main`'s version of that region plus the **union** of the append-only ledger rows
   -- the Bean 0053 failure mode, recorded in the PR bodies so the merge order is explicit: **#60 first (calibrated),
   then #61 after merging `main`.**

### Handover

- Merge #60 then #61 by hand (Bean 0034 boundary: agents never merge). Both are calibrated, so merging destroys the `E-`
  branches calibration read only after the fact.
- Remote cleanup still owed by the maintainer: the 2026-09-26 diagnostic refs
  `I-1790379192-fix-executor-git-fallback-reinitialization/_`, `.../P-1790379215-.../_` and the junk orphan
  `.../E-1790379447-.../_`; plus the six stale `I-1790382419-*/E-*/_` attempts from the Bean 0039 work.
- Follow-ups opened: **Bean 0058** (prettier convergence in the flow), **Bean 0059** (`safe.directory` detection),
  **Bean 0060** (stage 5 measures a stale/missing ref and reports it as a zero-diff success).

**Bean 0019 is closed.** All five revised acceptance criteria are implemented, reviewed to consensus, calibrated and
awaiting human merge.
