---
# holon-agentic-coder-ref-metadata-0256
title:
  "Resolver agent committing locally causes _commit_and_push_resolution to skip verification and git push, losing all
  fixes"
status: completed
type: bug
priority: high
tags:
  - flow
  - review-loop
  - stage-4
  - resolver
  - git
  - holon-agentic-coder
created_at: 2026-11-09T12:23:30Z
updated_at: 2026-11-09T08:10:00Z
---

## Problem

In `apps/sandbox-executor/src/sandbox_executor/entrypoint/review_loop.py` (`_commit_and_push_resolution`, around lines
483–489):

```python
initial_head = (_checked(["git", "rev-parse", "HEAD"], repo_dir, "resolve").stdout or "").strip()
status_proc = run_cmd(["git", "status", "--porcelain"], cwd=repo_dir, check=False)
has_worktree_changes = bool((status_proc.stdout or "").strip())
applied_items = [d for d in dispositions if d.disposition == "applied"]

if not applied_items or not has_worktree_changes:
    return dispositions, initial_head, False, False, False, None
```

`_commit_and_push_resolution` is called **after** `_run_resolver_agent` finishes:

1. Because the resolver prompt instructs the agent `"Do not run git push yourself"` (without forbidding `git commit`),
   the resolver agent (`agy` or `claude`) frequently runs `git add` and `git commit` inside the container before writing
   `dispositions.json`.
2. When `_commit_and_push_resolution` subsequently runs:
   - `initial_head` is captured **after** the agent has already committed (`HEAD` is already the new local commit SHA).
   - `git status --porcelain` is empty (`has_worktree_changes == False`) because the agent already committed its
     working-tree changes!
   - `_commit_and_push_resolution` immediately returns `(dispositions, initial_head, False, False, False, None)`
     (`pushed: false`, `lint_passed: false`, `tests_passed: false`), skipping `_verify_before_push`, skipping the
     canonical `Review-Iteration` git trailer commit, and **skipping `git push origin HEAD:refs/heads/<head_branch>`**!
3. Worse still, on the host side (`flow.py`), because the returned `head_sha` differs from the pre-resolver `HEAD`,
   `flow.py` logs:
   ```text
   [Review Loop] Resolver pushed new head 'fe68a5c2...' at iteration 1; proceeding to re-review in full.
   ```
   And at the start of the next iteration, the container runs `git checkout -B <branch> origin/<branch>`, **wiping out
   the unpushed local resolver commit** and causing the next iteration's reviewers to report the exact same missing
   files and findings all over again!

## Decision

Ensure `review_loop.py` captures `pre_resolver_head` **before** `_run_resolver_agent` runs and normalises any local
commits created by the resolver agent back into staged changes before verification, trailer commit creation, and push:

1. **Capture `pre_resolver_head` Before `_run_resolver_agent()`**:
   - Record `pre_resolver_head = git rev-parse HEAD` (or `refs/remotes/origin/<head_branch>`) prior to invoking
     `_run_resolver_agent()` and pass it into `_commit_and_push_resolution()`.
2. **Soft-Reset Any Local Resolver Commits (`HEAD != pre_resolver_head`)**:
   - At the start of `_commit_and_push_resolution()`, check if `current_head != pre_resolver_head`.
   - If the resolver agent created one or more local commits on top of `pre_resolver_head`, run
     `git reset --soft <pre_resolver_head>` so all changes authored by the resolver agent are back in the index/worktree
     relative to `pre_resolver_head` (and `git status --porcelain` is non-empty).
3. **Explicitly Instruct the Resolver Not to Run `git commit` or `git push`**:
   - Update `_build_resolver_prompt()` in `review_loop.py` to state:
     `"Do not run git commit or git push yourself; leave your edits in the working tree so the harness can verify, attach review trailers, commit, and push."`
4. **Honest `pushed` Check in `flow.py`**:
   - In `flow.py`, check `bool(resolve_payload.get("pushed"))` in addition to `new_head != prev_head` before logging
     `Resolver pushed new head ...`.

## Scope

1. `apps/sandbox-executor/src/sandbox_executor/entrypoint/review_loop.py`:
   - Pass `pre_resolver_head` into `_commit_and_push_resolution` (or soft-reset against `origin/<head_branch>` /
     `pre_resolver_head` when `HEAD != pre_resolver_head`).
   - Update `_build_resolver_prompt` to forbid both `git commit` and `git push`.
2. `apps/sandbox-executor/tests/test_review_loop.py`:
   - Add a unit test where `_run_resolver_agent` creates a local `git commit` during its turn, and verify that
     `_commit_and_push_resolution` soft-resets to `pre_resolver_head`, runs `_verify_before_push`, re-commits with the
     canonical `Review-Iteration:` git trailers, and pushes `HEAD:refs/heads/<head_branch>` with `pushed=True`.

## Notes & Forward Link to Bean 0262

> [!IMPORTANT] **Complete Removal of Obsolete In-Container Git Logic & Tests (Bean 0262)**: Bean 0256 resolved an urgent
> data-loss vulnerability caused by in-container git operations (`git reset --hard`, `git checkout -B`, unpushed
> resolver commits). However, patching in-container git plumbing was fundamentally a stopgap for running git clones
> inside containers. Under **Bean 0262**, the host harness directly bind-mounts a host worktree (`flow-<slug>`), making
> all in-container cloning, checkout, and reset plumbing (`_clone_or_fetch`, `_reset_reused_checkout`, `_ensure_head`,
> `_origin_matches`, `ReviewWorkspaceSession`) completely obsolete. **When implementing Bean 0262, ALL this legacy
> in-container git logic and its associated mock/unit tests MUST be completely purged.** Leaving obsolete in-container
> git code or stale tests lying around will cause confusion, false regressions, and serious maintenance hindrance.

## Resolution

Delivered via [PR #151](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/151) and merged into `main`
(`61796c65e7e1bc6becc7a25f275096dc30360a9e`):

- **Key Architectural Deliverables**:
  - Captured `pre_resolver_head` prior to running `_run_resolver_agent()`.
  - Added soft-reset (`git reset --soft pre_resolver_head`) in `_commit_and_push_resolution()` whenever the resolver
    agent authors local commits, restoring all edits cleanly to the staged index before pre-push verification.
  - Updated `_build_resolver_prompt()` to explicitly forbid both `git commit` and `git push`
    (`"Do not run git commit or git push yourself; leave your edits in the working tree..."`).
  - Added honest `pushed` check in `sandbox_executor.flow.review.loop` to avoid falsely logging that a new head was
    pushed when `pushed == False`.
- **Verification & Tests**:
  - Unit tests added in `apps/sandbox-executor/tests/test_review_loop.py`
    (`test_resolver_local_commit_soft_resets_and_pushes`, `test_build_resolver_prompt_forbids_commit_and_push`) and
    `apps/sandbox-executor/tests/flow/review/test_loop.py`
    (`test_honest_pushed_check_does_not_advance_target_when_unpushed`).
- **Holon Flow Traversal**:
  - Successfully traversed all 5 Holon flow stages (Intent $\rightarrow$ Plan $\rightarrow$ Execute $\rightarrow$ Review
    Loop $\rightarrow$ Calibration).
  - Achieved unanimous 3/3 review consensus approval with 0 open findings and passing CI.
  - Stage 5 calibration analysis committed and included in PR diff
    (`plans/P-1794205877-cbad6e47-antigravity-agent-gemini-3.8-flash-medium_calibration.md`, Predicted EV: 5.39, Actual
    EV: 5.92, $\Delta\text{EV} = +0.53$).
