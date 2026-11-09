---
name: post-pr-merge
description:
  Automates the complete post-merge lifecycle after a Pull Request merges to main (fast-forwarding main worktree,
  running install-holon/install-coherence, closing bean with resolution, pruning worktree/branches, updating triage
  matrix, and recommending the next bean). Activate this skill whenever the user announces a PR has been merged, or
  requests post-PR merge automation.
---

# Post-PR Merge Skill (`post-pr-merge`)

This skill orchestrates the end-to-end post-merge lifecycle across the Holon ecosystem (`holon-agentic-coder`,
`holon-coherence`, and `holon-agentic-coder-ref-metadata`) once a Pull Request is merged into `main`.

---

## 📐 Architecture & Principles

1. **Human-Only Merge Invariant**: Agents never merge PRs that target `main` (`gh pr merge` is strictly forbidden for
   them; see `AGENTS.md` for PRs into other branches). This skill activates **only after** the human maintainer merges
   the Pull Request on GitHub.
2. **Deterministic Post-Merge Sequence**:
   - **Step 1: Sync Trunk (`main`)**: Fetch and fast-forward `origin/main` in the relevant `apps/<repo>/main` worktree.
   - **Step 2: Ecosystem Image & CLI Rebuild (`install-holon` / `install-coherence`)**: Rebuild Docker images via Buildx
     Bake and reinstall CLI tools to `~/.local/bin/` so subsequent flows run against latest code.
   - **Step 3: Close Bean with Resolution**: Mark the corresponding bean in `.beans/` as `status: completed` and
     document the merge commit SHA, PR link, and key technical changes.
   - **Step 4: Clean Up PR Worktree & Remote Refs (`clean-workspace`)**: Safely remove the disposable PR worktree and
     prune stale tracking refs.
   - **Step 5: Refresh Triage & Matrix (`prioritise-beans`)**: Run the triage script to update completion stats and the
     Active Beans Prioritisation Matrix.
   - **Step 6: Commit Harness State & Recommend Next Task**: Commit all updated bean files and triage matrices to the
     current operational harness branch and recommend the next priority bean.

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

### Step 6: Commit Harness State & Recommend Next Task

1. Stage and commit harness changes:
   ```bash
   git add .beans/
   git commit -m "docs(post-merge): complete bean XXXX following PR #<N> merge"
   git push origin <current_harness_branch>
   ```
2. Review the Active Beans Matrix in `.beans/bean-triage-prioritisation.md`.
3. Provide the user with a concise summary of the post-merge actions completed and recommend the next top-priority bean.
