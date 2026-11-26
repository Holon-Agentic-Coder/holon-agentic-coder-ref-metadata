---
# holon-agentic-coder-ref-metadata-0540
title: "Split conftest.py: each test module owns its setup"
status: todo
type: task
priority: high
tags:
  - tests
  - holon-agentic-coder
  - architecture
  - merge-conflicts
  - hermetic
created_at: 2026-11-26T14:00:00Z
updated_at: 2026-11-26T14:00:00Z
blocked_by:
  - "0197"
---

## Instruction (maintainer, 2026-11-26)

"we need to split conftest.py. the design for this is all test should isolate as much set up as possible so different
tests don't rely on the same conftest.py"

## Problem

`apps/sandbox-executor/tests/conftest.py` (442 lines, 20 fixtures, 18 autouse) and `tests/flow/conftest.py` (139 lines,
6 fixtures, 3 autouse) are touch-set magnets: any flow that changes a fixture lists a conftest, so flows block each
other at Stage 3 admission (0390 parked twice on `tests/flow/conftest.py`, behind 0405 batch 2 and 0197; bean 0520
records the pattern). Every autouse fixture also runs for every one of the 8,878 unit tests though few need it, and
fixtures that live in a directory conftest are the cause of the subset-run failures in 0491 (and 0511, scrapped into
it).

## Measurements (origin/main f1e18bcd, detached worktree, removed afterwards)

Three conftest files, 594 lines: `tests/conftest.py` 442, `tests/flow/conftest.py` 139,
`tests/flow/stages/conftest.py` 13. 318 test files; 8,909 collected, 8,878 unit tests run after the stress and
integration marks and bean 0469's host-only test are deselected.

Who needs each autouse fixture: "ablation" = the fixture removed from the closure of every test, files with at least one
failure; "called" = files in which a recording wrapper saw the stub invoked in a full run. Both on the 318 files.

| Fixture (autouse unless noted)                                                                                                                                                                                         |                         Files that need it | Evidence                                                             |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -----------------------------------------: | :------------------------------------------------------------------- |
| `stub_stage3_admission`                                                                                                                                                                                                |                                         19 | called; 60 tests fail without it                                     |
| `stub_executor_test_measurement`                                                                                                                                                                                       |                                         10 | called; 1 test fails without it                                      |
| `stub_review_local_test_measurement`                                                                                                                                                                                   |                                         10 | called; 0 fail (real run of the test task is the cost)               |
| `stub_review_workspace_head`                                                                                                                                                                                           |                                         20 | called; 54 tests fail without it                                     |
| `_listed_feature_worktree_cwd` + table                                                                                                                                                                                 |                   5 files, 6 table entries | 1 test fails on a detached checkout; the table names tests by string |
| `_sandboxed_clean_reviewers` (flow)                                                                                                                                                                                    |                                         13 | ablation; 93 tests fail                                              |
| `_no_real_prettier` (flow): npx fake                                                                                                                                                                                   |                                          2 | called                                                               |
| `_no_real_prettier` (flow): mergeability probe                                                                                                                                                                         |                                         12 | called                                                               |
| `_knowledge_index_without_disk_wait` (flow)                                                                                                                                                                            |                                         33 | called (performance only)                                            |
| `fake_keychain`                                                                                                                                                                                                        |                                         11 | ablation; 143 tests fail                                             |
| `isolated_env_file_dir`                                                                                                                                                                                                |                                          5 | ablation; 227 tests fail (218 in test_preflight.py)                  |
| `isolated_layered_config`                                                                                                                                                                                              | 2 fail, 27 call `cli.main` or `config_env` | ablation; the rest leak silently                                     |
| `flow_repos` / `_flow_repos_template` (not autouse)                                                                                                                                                                    |                                         24 | fixture parameter                                                    |
| `stage_start` (not autouse)                                                                                                                                                                                            |                                          6 | fixture parameter                                                    |
| `no_origin_reconcile` (stages conftest, not autouse)                                                                                                                                                                   |                                          3 | fixture parameter                                                    |
| `feature_worktree_cwd` (not autouse)                                                                                                                                                                                   |                 1 direct + 5 via the table |                                                                      |
| Guards: `hermetic_git_config`, `no_ambient_credentials`, `isolated_claude_home`, `_isolate_agent_defaults`, `checkout_*` x3, `holon_dir_session_guard`, `gh_write_guard` (14 fail without it), `network_guard_fixture` |                            all (universal) | removing the three checkout guards fails nothing by design           |

Result by category:

- Used by one file: none. Fewest users: `no_origin_reconcile` 3 files, the npx fake 2, `stage_start` 6.
- Used by one directory: every flow fixture (all 103 flow files get three autouse wrappers; 37 flow files need any of
  them). The four root stubs reach 48 files (28 inside `flow/`).
- Autouse paid by all but needed by few: all four root stubs, the table-driven cwd fixture, `fake_keychain`,
  `isolated_env_file_dir`, and the three flow autouse fixtures.
- Genuinely universal: the guards in the last row of the table (about 10 fixtures, roughly 190 lines once their long
  bodies move to a helper).
- Global-state couplings: `hermetic_git_config` and `isolated_layered_config` write `os.environ` directly (undone by
  hand, not by monkeypatch); `_listed_feature_worktree_cwd` matches tests by path and class-name strings;
  `pytest_configure` replaces numbered temp dirs for the session; `gh_write_guard` and `network_guard_fixture` chain on
  `subprocess.Popen` (the second depends on the first); `_no_real_prettier` replaces `subprocess.run` for every flow
  test; the session fixture `_flow_repos_template` is visible only below `tests/flow` in a conftest.
- Test-time effect: per-test cost of all autouse setup is about 1 ms (suite audit of 2026-11-26), so moving seven stubs
  saves a few CPU seconds across 8,878 tests (well under a second of wall time on 18 workers, about 2 s on the two CI
  workers). Baseline on this host: 91.6 s wall, 8,878 passed, `-n auto`; a later run under four live flows took 158 s,
  so local wall times cannot resolve this and the acceptance check is "no slower". The point of the split is conflicts
  and isolation, not speed.
- A subset run with the module-level import design needs no conftest discovery, so 0491's failure disappears for the
  moved fixtures. `pytest_plugins` in a test module was tested and rejected: the plugin (autouse fixtures too) applies
  to every module collected after it, so order matters (reproduced with two files in both orders).
- Module budgets: they cover `apps/*/src/` and `scripts/` only (default 400, stepping to 250 by 0489); tests and
  conftests are not budgeted. The new helper modules stay under 200 lines each (rule 15). Budget file frozen.

Open pull requests and live or parked flows touching a conftest.py today: none of the four open PRs (#342, #344, #345,
#346) and none of the nine flow worktrees has a conftest.py in its diff against origin/main. Parked 0390 lists
`tests/flow/conftest.py` in its planned touch set. Test files in the batches below that are also in someone's diff now:
#342 and flow `ledgers-sorted-chronologically` (`flow/review/test_conflict_gate.py`, `test_ledger_append_only.py`;
batches 3 and 6), flow `split-calibration-package` (`flow/test_calibrate_nested_refs.py`, `flow/test_dispatch.py`,
`test_calibration.py`; batches 4 and 7), #345 (`test_partial_salvage.py`; batch 7).

## Design

1. Each test module owns its setup. Shared setup is a plain install function plus a non-autouse fixture in a small
   helper module (`tests/flow/support/` for flow setup, `tests/support/` for the rest), imported by name into the module
   that needs it and applied with `pytestmark = pytest.mark.usefixtures(...)`.
2. `pytest_plugins` is not used in test modules (global, order-dependent, autouse leaks).
3. `tests/conftest.py` keeps only universal safety guards (hermetic git config, ambient credentials, claude home, agent
   defaults, layered config, the checkout guards, gh write guard, network guard), with long bodies in
   `tests/support/guards.py`, under 200 lines. `tests/flow/conftest.py` and `tests/flow/stages/conftest.py` are deleted.
4. No autouse fixture unless every test needs it; a new fixture goes in the test module or an imported helper.
5. During the series each conftest keeps a thin autouse wrapper per fixture that calls the same install function, so
   unmigrated modules work and the series can merge step by step; the last user's step removes the wrapper.
6. `isolated_layered_config` stays a guard for now (27 modules call `cli.main` or `config_env`; only 2 fail without it
   but the rest would leak env silently). `fake_keychain` moves to its 11 users and a guard in the conftest refuses
   `security`/`secret-tool` for any test that did not apply it.
7. Rule recorded in `.agents/engineering-rules.md` (rule 17) and the PR review prompt.

## Batches (sequential; each ≤ ~15 files, files-only scope, disjoint; one flow at a time)

| Step | Intent                              | Files                            |
| ---: | :---------------------------------- | :------------------------------- |
|    1 | `intent-0540-conftest-split-1.json` | 3 test files, 3 conftest, 5 new  |
|    2 | `intent-0540-conftest-split-2.json` | 11 test files                    |
|    3 | `intent-0540-conftest-split-3.json` | 11 test files                    |
|    4 | `intent-0540-conftest-split-4.json` | 10 test files                    |
|    5 | `intent-0540-conftest-split-5.json` | 11 test files, 1 conftest        |
|    6 | `intent-0540-conftest-split-6.json` | 10 test files                    |
|    7 | `intent-0540-conftest-split-7.json` | 12 test files                    |
|    8 | `intent-0540-conftest-split-8.json` | 13 test files, 1 conftest, 1 new |
|    9 | `intent-0540-conftest-split-9.json` | 0 test files, 1 conftest, 2 new  |

Expected effect on line counts (estimates): `tests/flow/conftest.py` 139 to under 60 after step 1 and deleted in step 5;
`tests/flow/stages/conftest.py` deleted in step 1; `tests/conftest.py` 442 to about 410 after step 1, about 385 after
step 8, under 200 after step 9. The first step takes the fewest-user fixtures (`no_origin_reconcile`, 3 users) out and
relocates the rest of `tests/flow/conftest.py`; no flow fixture has a single user (see the table), so "single user" is
read as "fewest users".

## Dependencies and coordination

- Run after flow `split-calibration-package` (0197) merges (it touches `flow/test_calibrate_nested_refs.py`,
  `flow/test_dispatch.py`, `test_calibration.py`, and its planner may list `tests/flow/conftest.py`).
- Coordinate with parked 0390: both list `tests/flow/conftest.py`. Either 0390 runs first, or its intent drops the
  conftest from its scope (a new fixture goes into the module under test) and step 1 runs after it.
- Steps 3 and 6 wait for #342 (flow `ledgers-sorted-chronologically`); step 7 waits for #345.
- Overlaps 0537 item 2 (the `_FEATURE_WORKTREE_CWD_TESTS` allowlist): step 7 and 9 do it with in-place marks; 0537 drops
  that item. Fixes 0491 for every moved fixture (close it when step 5 merges). Uses 0469's deselect until that is fixed.
- The knowledge pattern about conftest guards (0538) stays true for the guards that remain; update it after step 9.

## Notes

- Measurement scripts and the ablation plugin were throwaway files in the detached worktree; raw counts are in this
  bean.
- Intents: `todo/intent-0540-conftest-split-1.json` to `-9.json` (git-ignored, never name harness paths).
