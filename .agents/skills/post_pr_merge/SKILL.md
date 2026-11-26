---
name: post-pr-merge
description:
  Automates the complete post-merge lifecycle after a Pull Request merges to main (fast-forwarding main worktree,
  running install-holon/install-coherence, closing bean with resolution, pruning worktree/branches, updating triage
  matrix, and recommending the next bean). Activate this skill whenever the user announces a PR has been merged, or
  requests post-PR merge automation.
---

# Post-PR Merge Skill (`post-pr-merge`)

> [!NOTE] **Model tier: lowest.** This skill is mechanical, so run it in a dedicated subagent on the lowest-tier model,
> found by probing the harness as described in [`.agents/model-tiers.md`](../../model-tiers.md). Do not hard-code a
> model name here. Name the subagent `#<N> - post-merge` (see
> [subagents.md, "Subagent names"](../../subagents.md#subagent-names)).

This skill orchestrates the end-to-end post-merge lifecycle across the Holon ecosystem (`holon-agentic-coder`,
`holon-coherence`, and `holon-agentic-coder-ref-metadata`) once a Pull Request is merged into `main`.

---

## 📐 Architecture & Principles

1. **Human-Only Merge Invariant**: Agents never merge PRs that target `main` (`gh pr merge` is strictly forbidden for
   them; see [pr-merging.md](../../pr-merging.md) for PRs into other branches). This skill activates **only after** the
   human maintainer merges the Pull Request on GitHub.
2. **Deterministic Post-Merge Sequence**:
   - **Step 1: Sync Trunk (`main`)**: Fetch and fast-forward `origin/main` in the relevant `apps/<repo>/main` worktree.
   - **Step 2: Ecosystem Image & CLI Rebuild (`install-holon` / `install-coherence`)**: Rebuild Docker images via Buildx
     Bake and reinstall CLI tools to `~/.local/bin/` so subsequent flows run against latest code.
   - **Step 3: Close Bean with Resolution**: Mark the corresponding bean in `.beans/` as `status: completed` and
     document the merge commit SHA, PR link, and key technical changes.
   - **Step 4: Clean Up PR Worktree, Flow Branches & Stale Plans (`clean-workspace`)**: Remove the merged PR's worktree,
     its earlier attempts and its flow branches (local and remote), delete every stale plan left by other flows, and
     prune stale tracking refs.
   - **Step 5: Refresh Triage & Matrix (`prioritise-beans`)**: Run the triage script to update completion stats and the
     Active Beans Prioritisation Matrix.
   - **Step 6: Commit Harness State, Recommend & Backfill Next Task**: Commit all updated bean files and triage matrices
     to the current operational harness branch, report next priority beans, and automatically launch the next
     highest-priority ready bean via `holon-flow` whenever active concurrent flows are under 4 on hosted runtimes.

---

## 🛠️ Step-by-Step Execution Guide

### Step 1: Verify PR Merge State & Fast-Forward Trunk

Verify that the target PR is actually merged using the GitHub CLI:

```bash
gh pr view <pr_number_or_url> --repo <owner>/<repo> --json state,mergedAt,mergeCommit
```

If `state != "MERGED"`, halt and inform the user that the PR is still open.

Once confirmed merged, fetch and fast-forward `main` in the target repository. The `main` worktree must already be on
`main` and clean: flows run in their own `flow-<slug>` worktree and never leave it elsewhere. If it is on another branch
or has tracked changes, do not paper over it: report it, because something ran in the `main` worktree.

Run `uv run python .agents/scripts/check_main_worktrees.py` before the fast-forward and again after it; a non-zero exit
means something ran in a `main` worktree, so report it and record it in the failure ledger instead of continuing.

```bash
# For holon-agentic-coder
git -C apps/holon-agentic-coder/main fetch origin
git -C apps/holon-agentic-coder/main pull --ff-only origin main

# For holon-coherence
git -C apps/holon-coherence/main fetch origin
git -C apps/holon-coherence/main pull --ff-only origin main
```

Verify that `git -C apps/<repo>/main rev-parse HEAD` matches `mergeCommit.oid`. Step 4 also removes the flow's
`flow-<slug>` worktree and its branch.

---

### Step 2: Rebuild Images & Reinstall CLI Tools

Run the ecosystem build pipeline based on which repository was modified:

#### For `holon-agentic-coder` changes:

Run the automated installation orchestrator:

```bash
python3 .agents/skills/install_holon/scripts/install_holon.py
```

This rebuilds all 8 sandboxed role images (`holon/base`, `holon/orchestrator`, `holon/agent-*`) and reinstalls `holon`
via `uv tool install --force --reinstall --editable apps/holon-agentic-coder/main/apps/sandbox-executor`.

#### For `holon-coherence` changes:

Run the coherence install pipeline:

```bash
python3 .agents/skills/install_coherence/scripts/install_coherence.py
```

This rebuilds `holon-coherence:latest` and reinstalls `holon-coherence` via
`uv tool install --force --reinstall --editable apps/holon-coherence/main`.

Verify installed tools:

```bash
holon --version
holon-coherence -h
```

---

### Step 3: Transition Bean to Completed

Locate the bean corresponding to the merged work under `.beans/`.

1. Update frontmatter:
   ```yaml
   status: completed
   updated_at: <current_iso8601_timestamp>
   ```
2. Add or update the `## Resolution` section:
   ```markdown
   ## Resolution

   Delivered via [PR #<N>](https://github.com/<owner>/<repo>/pull/<N>) and merged into `main` (`<short_commit_sha>`):

   - **Key Architectural Deliverables**: Bullet points summarizing the implemented features, bug fixes, or refactors.
   - **Verification & Tests**: Summary of hermetic tests added and verification suites passed.
   - **Holon Flow Traversal**: Confirmation that all 5 stages (Intent -> Plan -> Execute -> Review Loop -> Calibration)
     completed successfully.
   ```

---

### Step 4: Clean Up PR Worktree & Branches

Remove the temporary worktree created for the flow/PR:

```bash
# 1. Remove the flow's worktree (`flow-<slug>`) or the PR worktree, and any leftover `build-images-<sha>` worktree
git -C apps/<repo> worktree remove apps/<repo>/flow-<slug>
git -C apps/<repo> worktree remove apps/<repo>/pr<N>-<slug>  # only if one was created
git -C apps/<repo> branch -D flow-<slug>

# 2. Prune any detached worktree refs
git -C apps/<repo> worktree prune

# 3. Prune deleted remote branches
git -C apps/<repo> fetch origin --prune
```

_Note: Never touch or remove `apps/<repo>/main`._

#### 4a. The merged flow's branches and earlier attempts

The squash merge leaves the flow's own branches behind; delete them, locally and on origin:

```bash
# Every branch of the merged intent: I-<ts>-<slug>/_, its P-.../_ and E-.../_ children and /calibrated
git -C apps/<repo> for-each-ref --format='%(refname:short)' "refs/heads/I-*-<slug>/" | xargs -n1 git -C apps/<repo> branch -D
git -C apps/<repo> for-each-ref --format='%(refname:lstrip=3)' "refs/remotes/origin/I-*-<slug>/" | xargs -n1 git -C apps/<repo> push origin --delete
```

Earlier attempts of the same bean (the same slug without its `-vN` suffix, e.g. `flow-layered-env-config` beside the
merged `flow-layered-env-config-v2`) are superseded by the merge: remove their worktrees (`worktree remove --force` when
the only leftovers are that attempt's own intent/plan/execution commits or ledger edits) and delete their `I-*-<slug>/`
branches the same way.

#### 4b. Delete stale plans (maintainer, 2026-11-23)

After every merge, any stale plan is deleted as well, whichever bean it belongs to. A flow worktree holds a **stale
plan** when all of these hold:

- its branch is an intent or plan branch (`I-.../_` or `I-.../P-.../_`): no execution branch was ever cut from it;
- it has no open pull request and no live process (`ps` shows no `holon flow` / `run_holon_flow.py` / role container
  naming its slug);
- `origin/main` has moved since it was cut (`git merge-base --is-ancestor origin/main HEAD` fails), so the plan was made
  against code that no longer exists.

For each one: remove the worktree (`--force`: uncommitted ledger rows or a stub plan file are part of the stale plan),
delete its `I-*-<slug>/` branches locally and on origin, delete its `flow-<slug>` branch, and set its bean back to
`status: todo` with a one-line note ("stale plan deleted after PR #<N> merged; restart from current main"). Keep the
bean's `todo/intent-*.json`; it is reused for the restart.

#### 4c. Delete stale worktrees (maintainer, 2026-11-23)

Stale worktrees are cleaned up as well, not only stale plans. A flow worktree is **stale** when all of these hold:

- it has no open pull request;
- no live process uses it (`ps` shows no `holon flow`, `run_holon_flow.py`, role container or usage-limit waiter naming
  its slug);
- `origin/main` has moved since it was cut;
- nothing has touched it for at least two hours (newest of its last commit and its `.holon/flow/checkpoint-*.json`
  mtime), so a flow that is merely between stages is never caught.

This covers superseded earlier attempts, interrupted execution branches of paused beans and detached leftovers. For each
one:

1. **Back up first.** If the worktree has commits that exist on no remote branch, or uncommitted changes, save them
   before deleting:
   `git -C apps/<repo> bundle create <harness>/todo/stale-worktree-backups/<slug>-<date>.bundle <its I-*-<slug>/ branches>`,
   and copy uncommitted files next to it. Name the bundle in the report.
2. Remove the worktree (`--force`), delete its `I-*-<slug>/` and `flow-<slug>` branches locally and on origin.
3. Set its bean back to `status: todo` (unless the bean is completed) with a one-line note naming the backup; the bean
   restarts from current `main` with a fresh `-vN` intent.

Never delete a worktree with an open PR or a live process, and never the `main` worktree. List what was deleted, what
was backed up and what was kept in the post-merge report.

---

### Step 5: Refresh Prioritisation Matrix

Run the prioritisation script to recompute project completion statistics and generate the updated triage matrix:

```bash
uv run python .agents/skills/prioritise_beans/scripts/prioritise_beans.py
```

Format the generated document with Prettier:

```bash
npx prettier --write .beans/bean-triage-prioritisation.md
```

---

### Step 6: Commit Harness State, Recommend & Backfill Next Task

1. Stage and commit harness changes by explicit path (never `git add .beans/`, `git add .` or `git add -A`; other agents
   may hold edits in the same tree):
   ```bash
   git add <each bean file closed this run> <any other harness file this run edited>
   git commit -m "docs(post-merge): complete bean XXXX following PR #<N> merge"
   git push origin <current_harness_branch>
   ```
2. Review the Active Beans Matrix in `.beans/bean-triage-prioritisation.md`.
3. **Backfill up to 8 concurrent `holon-flow` subagents (hosted runtimes; maintainer, 2026-11-24)**: first list parked
   flows (beans noted `parked <date>`) whose blocker was this PR or whose files this PR released, and recommend resuming
   them from checkpoint (`--checkpoint`) before any new bean (maintainer, 2026-11-26). Then count currently active
   background `holon-flow` subagents that are executing, reviewing or calibrating (parked or blocked flows do not count;
   `< 4` on hosted runtimes; local runtimes remain capped at 1). Pick up the highest-priority ready bean from the
   refreshed triage (honouring `blocked_by`, solo-sweep rules, and pairwise-disjoint touch sets with active flows; at
   most one bean touching a shared hotspot such as `flow.py` or `cli.py` per target) and launch it in the background via
   the `holon-flow` skill.
4. Provide the user with a concise summary of the post-merge actions completed, note any newly launched backfill flow
   (or why none could start), and recommend the next top-priority beans.

---

### Step 7: Self-Improvement Audit Check

Count the pull requests merged into `main` of `holon-agentic-coder` and `holon-coherence` since the newest entry in
`.beans/self-improvement-audits.md` (the first entry under `## Entries`):

```bash
gh pr list --repo <owner>/holon-agentic-coder --state merged --base main --json number,mergedAt
gh pr list --repo <owner>/holon-coherence --state merged --base main --json number,mergedAt
```

1. Count the merges with `mergedAt` after that entry's timestamp, across both repositories. If the log has no entry,
   count all merges of the last 7 days.
2. In the final report, state either "self-improvement audit due (N merges since the last audit)" when N is 5 or more,
   or "N of 5 merges since the last audit".
3. This skill does not run the audit. The receiving agent launches it per
   [`.agents/self-improvement-audit.md`](../../self-improvement-audit.md).
