---
name: clean-branches
description:
  Audits, prunes, and safely deletes stale and merged Pull Requests, local Git branches, remote tracking refs, and
  detached worktrees across all managed repositories in the Holon ecosystem (holon-agentic-coder, holon-coherence, and
  holon-agentic-coder-ref-metadata). Activate this skill whenever the user asks to remove stale or merged branches,
  clean up completed PR branches, prune deleted remote refs, or clean worktrees across the workspace.
---

# Clean Branches & Worktrees Skill (`clean-branches`)

This skill automates the identification and safe deletion of stale, merged, and orphaned branches, worktrees, and Pull
Requests across all active projects within the Holon Agentic Coder workspace.

---

## 📐 Architecture & Operational Principles

1. **Multi-Repository Scope**: The Holon workspace manages several repositories with checkout worktrees:
   - **`holon-agentic-coder`**: Fractal intent evolution engine (worktree: `holon-agentic-coder/main`, bare repo:
     `holon-agentic-coder/.git`).
   - **`holon-coherence`**: Optimization proxy gateway & wire telemetry (worktree: `holon-coherence/main`, bare repo:
     `holon-coherence/.git`).
   - **`holon-agentic-coder-ref-metadata`**: Control plane, metadata store, and orchestration harness (repository root).

2. **Strict Base Branch Protection**: The primary trunk branch (`main` / `master`) across all repositories is **strictly
   protected** and must **never** be deleted or force-reset:
   - `origin/main`
   - Local `main`

3. **Multi-Layer Merge & Stale Verification**: A branch is considered eligible for deletion if:
   - **PR Merged on GitHub**: The branch has an associated Pull Request in state `MERGED` verified via `gh pr view` or
     `gh pr list`.
   - **Git Merged into Base**: The branch is fully merged into `origin/main` (`git branch --merged origin/main` or
     `git branch -r --merged origin/main`). Note that squash-merged PR branches do not share commit ancestry with
     `origin/main`; always check merged PRs via `gh pr list --state merged` to identify merged branches.
   - **Remote Pruned**: The remote tracking ref on `origin` was already deleted (prunable via `git fetch --prune`).

4. **Safe Worktree Deletion Order**: In a Git worktree layout, Git prohibits deleting a local branch that is currently
   checked out in an active worktree. The correct teardown sequence is:
   1. Identify target branch.
   2. Remove the associated worktree directory: `git -C <repo_main_worktree> worktree remove <path>`.
   3. Delete the local branch: `git -C <repo_main_worktree> branch -d <branch>` (or `-D` if squash-merged into `main`).
   4. Prune worktree administrative files: `git -C <repo_main_worktree> worktree prune`.

5. **Remote Deletion Protocol**: When cleaning remote branches on GitHub:
   - Verify the associated Pull Request is `MERGED` or `CLOSED` with no active unmerged work.
   - Delete from remote: `git -C <repo_worktree> push origin --delete <branch-name>`.
   - Prune tracking branches: `git -C <repo_worktree> fetch origin --prune`.

---

## 🛠️ Step-by-Step Execution Guide

When executing this skill, follow these sequential phases across all managed repositories:

### Step 1: Discover Active Repositories & Worktrees

Identify all repositories present in the current workspace:

```bash
# 1. Metadata root
git worktree list

# 2. holon-agentic-coder (if directory exists)
if [ -d "holon-agentic-coder/.git" ]; then
  git --git-dir=holon-agentic-coder/.git worktree list
fi

# 3. holon-coherence (if directory exists)
if [ -d "holon-coherence/.git" ]; then
  git --git-dir=holon-coherence/.git worktree list
fi
```

---

### Step 2: Fetch & Prune Remote Tracking Refs

Before checking merge ancestry or local branch status, synchronize tracking branches with remotes across all
repositories to ensure `origin/main` and remote tracking refs are fresh:

```bash
# For metadata repo
git fetch origin --prune

# For holon-agentic-coder
if [ -d "holon-agentic-coder/main" ]; then
  git -C holon-agentic-coder/main fetch origin --prune
fi

# For holon-coherence
if [ -d "holon-coherence/main" ]; then
  git -C holon-coherence/main fetch origin --prune
fi
```

---

### Step 3: Audit & Clean Up Worktrees

For each repository that has temporary feature or fix worktrees (e.g. `feat-*`, `fix-*`, `I-*`):

1. **Check Working Tree Status**: Ensure there are no uncommitted or untracked changes that need preservation:

   ```bash
   git -C <worktree_dir> status
   ```

2. **Verify Upstream Integration**: Check if the branch has been pushed and merged:

   ```bash
   # Check commit ancestry against fresh origin/main
   git -C <worktree_dir> log origin/main..HEAD --oneline

   # Or verify associated PR status on GitHub
   gh pr list --repo <owner>/<repo> --head <feature_branch_name> --state all
   ```

3. **Remove Worktree & Delete Local Branch**: Execute from the primary worktree of the target repository
   (`<repo_main_worktree>`, e.g., metadata root, `holon-agentic-coder/main`, or `holon-coherence/main`):

   ```bash
   # From the primary worktree of the target repository (e.g. git -C <repo_main_worktree> ...):
   git -C <repo_main_worktree> worktree remove <worktree_path>
   git -C <repo_main_worktree> branch -D <feature_branch_name>
   git -C <repo_main_worktree> worktree prune
   ```

4. **Verify & Clean Up Worktree Directories on Filesystem**:
   - `git worktree remove` may leave behind the directory if untracked files (such as `.idea/`, `.vscode/`, build
     artifacts, or caches) exist within it.
   - Always verify whether the physical directory still exists on disk:
     ```bash
     if [ -n "<worktree_path>" ] && [ -d "<worktree_path>" ]; then
       echo "Worktree directory still exists on disk: <worktree_path>. Removing..."
       rm -rf "<worktree_path>" || echo "ERROR: Failed to remove directory <worktree_path>"
     fi
     ```
   - **Mandatory Failure Reporting**: If `rm -rf` fails (e.g. due to permissions, file locks, or active root mounts):
     1. Do **NOT** silently ignore the error.
     2. Inspect the file permissions and owning process using `ls -la "<worktree_path>"` or `lsof +D "<worktree_path>"`.
     3. Explicitly document and report the failure, directory path, and reason to the user in the execution summary
        report under a **⚠️ Unremovable Directories / Attention Required** section.

5. **Clean Orphaned & Detached Directories**: Scan repository parent folders for stale directories matching branch
   patterns (e.g. `feat-*`, `fix-*`, `I-*`) that lack an active Git worktree registration (`git worktree list`):
   ```bash
   # 1. Scan candidate directories matching branch prefixes with proper operator grouping
   find holon-agentic-coder/ holon-coherence/ -maxdepth 1 -type d \( -name "feat-*" -o -name "fix-*" -o -name "I-*" \)
   ```
   **Safety Pre-check**: For each candidate directory:
   1. Verify it is **NOT** present in `git worktree list` (or `git --git-dir=<repo>/.git worktree list`). If it is an
      active registered worktree, follow Sub-steps 1–3 instead.
   2. Confirm directory path is non-empty, safe, exists, and is not the repo root:
   ```bash
   if [ -n "<orphaned_dir>" ] && [ -d "<orphaned_dir>" ]; then
     rm -rf "<orphaned_dir>" || echo "ERROR: Failed to remove orphaned directory <orphaned_dir>"
   fi
   ```
   Report any directories that could not be removed.

---

### Step 4: Detect & Delete Merged Remote Branches on GitHub

For each repository, inspect remote branches that are merged into `origin/main` or whose PR has merged:

1. **Identify Merged Remote Branches**:
   - **Direct ancestry merge**:
     ```bash
     git -C <repo_worktree> branch -r --merged origin/main
     ```
   - **Squash-merged PRs**: Many workflows squash-merge PRs, which produces a new commit SHA on `main` and breaks Git's
     ancestry checks (`git branch -r --merged origin/main`). To detect squash-merged remote branches, query merged PR
     head branch names via GitHub CLI:
     ```bash
     gh pr list --repo <owner>/<repo> --state merged --json headRefName --jq '.[].headRefName'
     ```

2. **Process Non-Base Branches**: For each candidate remote branch (strip `origin/` prefix; ignore `origin/HEAD` and
   `origin/main`):

   - **Extract Remote Branch Name**:
     ```bash
     # Strip remote prefix (e.g. origin/feat-123 -> feat-123)
     branch_name="${raw_branch#origin/}"
     ```
   - **Ignore Base Branches**: Skip if `$branch_name` is `HEAD`, `main`, or `master`.
   - **Verify PR Status via GitHub CLI**:
     ```bash
     gh pr list --repo <owner>/<repo> --head "$branch_name" --state all
     ```
   - **Delete Merged Remote Branch**:
     ```bash
     git -C <repo_worktree> push origin --delete "$branch_name"
     git -C <repo_worktree> fetch origin --prune
     ```

---

### Step 5: Clean Local Merged & Stale Branches

Inspect local branches in each repository:

```bash
git -C <repo_worktree> branch -vv
```

Delete any local branches whose upstream is `[gone]` or that are fully merged into `main`:

```bash
git -C <repo_worktree> branch -D <stale_local_branch>
```

---

### Step 6: Sync & Fast-Forward Base Branches

Ensure the baseline `main` worktree in each repository is fast-forwarded to `origin/main`:

```bash
# Metadata repo root
git pull --ff-only origin main

# holon-agentic-coder
git -C holon-agentic-coder/main pull --ff-only origin main

# holon-coherence
git -C holon-coherence/main pull --ff-only origin main
```

---

### Step 7: Verify Repository Hygiene & Report Summary

Run a final verification across all repositories:

```bash
git status
git branch -a
```

Format a concise summary report for the user detailing:

- **Repositories Audited**: All repositories scanned.
- **Worktrees & Directories Removed**: Any temporary worktrees unmounted and physical directories deleted on disk.
- **Remote Branches Deleted**: Remote branches pruned or deleted on GitHub.
- **Local Branches Deleted**: Local stale tracking branches removed.
- **⚠️ Unremovable Directories / Attention Required**: Explicitly itemize any directories that could not be deleted,
  including their path, ownership, and error reason (or state "None" if all directories were cleanly deleted).
- **Current Active State**: Table showing clean `main` branches and worktrees.
