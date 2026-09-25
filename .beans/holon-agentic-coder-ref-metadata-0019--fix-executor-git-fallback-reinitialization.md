---
# holon-agentic-coder-ref-metadata-0019
title: Fix executor.py git re-initialization fallback wiping parent commit history
status: in-progress
type: task
created_at: 2026-08-31T10:56:00Z
updated_at: 2026-09-26T19:20:00Z
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

## Stage 4 (PR review loop) -- iteration 1 incomplete, blocked on child latency

Iteration 1 against pinned head `ed7600e`, dry-run (nothing posted; posting gate honoured):

| Lane                             | Result                                                                         |
| -------------------------------- | ------------------------------------------------------------------------------ |
| guard-test value + scope honesty | **completed in 874 s** -> `CHANGES_REQUESTED` (0 Critical, 3 Important, 3 Nit) |
| hermetic mechanism               | **timed out** at 900 s                                                         |
| red-CI diagnosis                 | **timed out** at 900 s                                                         |

Ensemble rule is 3/3 unanimous; with two `FAILED` lanes the verdict cannot be `APPROVED` in any case, and CI is red, so
nothing was posted. Artifacts: `.subagent/pr59_consensus_iter_1_lane_guard-scope_ed7600e.md`,
`.subagent/pr59_consensus_iter_1_summary.md`.

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

## Still open in this bean

- Stage 4 for PR #59 is mid-flight (iteration 1 incomplete, see above) and stage 5 (`holon calibrate`) is still pending.
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

### Remaining acceptance criteria vs provenance

The pushed intent covers acceptance criterion 1 (hermetic tests) only. Criteria 2-5 (non-destructive history-preserving
`executor.py` recovery, bounded agent stdout/stderr in the execution record, `get_repo_url()` default pointing at
`holon-agentic-coder`, replacing the misleading `tests/test_executor.py:342` assertion) still need their own intent(s)
through the flow after the hermetic-tests execution lands -- the executor recovery fix must not be authored by hand.

### Housekeeping

Branches produced by this diagnostic run still exist on the remote and should be deleted once the fix lands
(`I-1790379192-*/_`, `.../P-1790379215-*/_`, `.../E-1790379447-*/_` -- the last is the junk orphan branch).
