---
name: clean-branches
description:
  Audits, prunes, and safely deletes stale and merged Pull Requests, local Git branches, remote tracking refs, and
  detached worktrees, cleans up completed Holon flow intent hierarchy branches (I-.../_, P-.../_, E-.../calibrated), and
  detects orphaned or superfluous leftover directories that no git worktree command will report, across all managed
  repositories in the Holon ecosystem (holon-agentic-coder, holon-coherence, and holon-agentic-coder-ref-metadata).
  Activate this skill whenever the user asks to remove stale or merged branches, clean up completed PR branches, prune
  deleted remote refs, clean worktrees, or find leftover, stray, or superfluous directories in the workspace.
---

# Clean Branches & Worktrees Skill (`clean-branches`)

This skill automates the identification and safe deletion of stale, merged, and orphaned branches, worktrees, and Pull
Requests across all active projects within the Holon Agentic Coder workspace.

---

## 📐 Architecture & Operational Principles

1. **Multi-Repository Scope**: The Holon workspace manages several repositories with checkout worktrees:
   - **`holon-agentic-coder`**: Fractal intent evolution engine (worktree: `apps/holon-agentic-coder/main`, bare repo:
     `apps/holon-agentic-coder/.git`).
   - **`holon-coherence`**: Optimization proxy gateway & wire telemetry (worktree: `apps/holon-coherence/main`, bare
     repo: `apps/holon-coherence/.git`).
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

6. **Filesystem Is the Source of Truth for Directories**: `git worktree list` enumerates only _registered_ worktrees. It
   is blind in both directions: it cannot see a leftover directory whose registration was already pruned, and it still
   reports a registration whose directory was deleted by hand. Directory hygiene therefore requires an explicit
   **registry-vs-disk diff**, cross-checked against the bare repository's `.git/worktrees/` administrative metadata —
   three independent sources of truth. A cleanup that only calls `git worktree list` can announce a clean workspace
   while stale directories are still sitting on disk. See Step 3.5.

7. **No Unlinkable Directory May Be Deleted Blindly**: An orphaned directory is outside Git's reach, so `git status`
   cannot report whether it holds unsaved work. Its safety must be established by direct inspection — residual contents,
   absence of any `.git` gitfile, a detached-worktree probe, and the merged/closed state of the matching branch — never
   assumed from the directory name. If any residual file looks like authored work rather than a regenerable artefact,
   stop and surface it to the user instead of deleting it.

8. **Holon Flow Intent Hierarchy & Provenance Tree Cleanup**: Changes driven by the Holon flow create multi-stage
   provenance branches on `origin`:
   - Intent: `I-<timestamp>-<slug>/_`
   - Plan: `I-<timestamp>-<slug>/P-<timestamp>-<agent>-<model>/_`
   - Execution: `I-<timestamp>-<slug>/P-.../E-<timestamp>-<agent>-<model>/_`
   - Calibration: `I-<timestamp>-<slug>/P-.../E-.../calibrated` Only one branch in this hierarchy (typically the
     execution or calibrated branch) is submitted as a GitHub Pull Request. The intermediate intent and plan branches,
     as well as sibling execution/calibration branches, do **not** have their own GitHub PRs. When the flow PR is merged
     on GitHub (frequently via squash-merge) or closed, standard Git ancestry checks
     (`git branch -r --merged origin/main`) fail to detect these unlinked parent and sibling branches as merged, and
     querying `gh pr list --head <branch>` for `I-.../_` returns empty. Therefore, agents must group flow branches by
     their root intent identifier (`I-<timestamp>-<slug>`), determine if ANY branch under that intent was merged or
     closed, and prune the entire tree of related remote and local branches. See Step 4.3.

---

## 🛠️ Step-by-Step Execution Guide

When executing this skill, follow these sequential phases across all managed repositories:

### Step 1: Discover Active Repositories & Worktrees

Identify all repositories present in the current workspace:

```bash
# 1. Metadata root
git worktree list

# 2. holon-agentic-coder (if directory exists)
if [ -d "apps/holon-agentic-coder/.git" ]; then
  git --git-dir=apps/holon-agentic-coder/.git worktree list
fi

# 3. holon-coherence (if directory exists)
if [ -d "apps/holon-coherence/.git" ]; then
  git --git-dir=apps/holon-coherence/.git worktree list
fi
```

Then inventory what is **actually on disk**, independently of the registry above. Do not defer this to the cleanup step
and do not filter by branch-name pattern — stale directories frequently do not match `feat-*` / `fix-*` / `I-*`:

```bash
for r in apps/holon-agentic-coder apps/holon-coherence; do
  [ -d "$r" ] && { echo "== $r =="; find "$PWD/$r" -mindepth 1 -maxdepth 1 -type d -not -name '.git' | sort; }
done
```

Any directory appearing here but missing from `worktree list` is an orphan candidate and must be carried into Step 3.5.

---

### Step 2: Fetch & Prune Remote Tracking Refs

Before checking merge ancestry or local branch status, synchronize tracking branches with remotes across all
repositories to ensure `origin/main` and remote tracking refs are fresh:

```bash
# For metadata repo
git fetch origin --prune

# For holon-agentic-coder
if [ -d "apps/holon-agentic-coder/main" ]; then
  git -C apps/holon-agentic-coder/main fetch origin --prune
fi

# For holon-coherence
if [ -d "apps/holon-coherence/main" ]; then
  git -C apps/holon-coherence/main fetch origin --prune
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
   (`<repo_main_worktree>`, e.g., metadata root, `apps/holon-agentic-coder/main`, or `apps/holon-coherence/main`):

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

5. **Detect & Clean Orphaned, Dangling, and Superfluous Directories**:

   > [!IMPORTANT] **`git worktree list` is not a directory inventory.** Reporting "no worktrees to clean" does not mean
   > the workspace has no stale directories. Derive the truth by diffing the filesystem against the registry, as
   > follows.

   **a. Build the registry-vs-disk diff.** Enumerate every directory on disk and every registered worktree, then
   compare. Run this from the **workspace root**, since `$PWD/$repo` is absolute while `--git-dir="$repo/.git"` is
   relative:

   ```bash
   repo=apps/holon-coherence
   find "$PWD/$repo" -mindepth 1 -maxdepth 1 -type d -not -name '.git' | sort > /tmp/on_disk.txt
   git --git-dir="$repo/.git" worktree list --porcelain \
     | sed -n 's/^worktree //p' | grep -Fxv "$PWD/$repo" | sort > /tmp/registered.txt

   echo "== on disk, NOT registered -> orphan / superfluous directory =="
   comm -23 /tmp/on_disk.txt /tmp/registered.txt
   echo "== registered, NOT on disk -> dangling registration (prunable) =="
   comm -13 /tmp/on_disk.txt /tmp/registered.txt
   ```

   Classify every entry before deleting anything:

   | Condition                   | Classification                   | Action                                               |
   | :-------------------------- | :------------------------------- | :--------------------------------------------------- |
   | On disk **and** registered  | Active worktree                  | Tear down via Sub-steps 1–3; never `rm -rf` directly |
   | On disk, **not** registered | Orphaned / superfluous directory | Verify per (c), then `rm -rf`                        |
   | Registered, **not** on disk | Dangling registration            | `git worktree prune`, then re-verify                 |

   **b. Cross-check the administrative metadata (third source of truth).** `git worktree list` reads this state, but
   reading it directly exposes entries the command may already hide:

   ```bash
   ls -1 apps/holon-agentic-coder/.git/worktrees apps/holon-coherence/.git/worktrees 2>/dev/null
   ```

   Any `.git/worktrees/<name>` entry with no matching on-disk directory is stale administrative state, cleared by
   `git worktree prune` from the repository's primary worktree.

   **c. Orphan safety pre-check — mandatory before any `rm -rf`.** Git cannot report an orphan's dirtiness, so establish
   it:

   ```bash
   d=<orphaned_dir>
   ls -la "$d"                                            # what is actually left inside?
   [ -e "$d/.git" ] && echo "LINKED — DO NOT DELETE"      # gitfile or .git dir => real/leftover worktree, not an orphan
   git -C "$d" status -sb 2>&1 | head -n 2                # 'must be run in a work tree' => truly detached
   gh pr list --repo <owner>/<repo> --head <branch> --state all   # MERGED / CLOSED / empty?
   ```

   Proceed only when **all** of these hold:
   1. The path is absent from the registry and has no `.git` gitfile and no `.git` directory of its own.
   2. `git -C "$d" status` fails with _"this operation must be run in a work tree"_, so Git was not tracking any
      uncommitted or untracked change inside it.
   3. The matching branch shows `MERGED`, `CLOSED`, or no PR at all on GitHub — never an open PR with live work.
   4. You have **listed the residual contents** and confirmed they are regenerable IDE, build, or cache artefacts —
      typically `.idea/`, `*.iml`, `.vscode/`, `__pycache__/`, `.venv/`, `dist/` — with no unique source, notes, or
      data. These artefacts are usually the entire reason `git worktree remove` left the directory behind. If anything
      looks authored, stop and report it instead of deleting.

   **d. Portability trap — `find` flags differ between GNU and BSD.** `-printf` and several other GNU extensions do not
   exist on macOS/BSD `find`. Pairing such a flag with `2>/dev/null` makes the probe fail _silently_, which is easily
   misread as "no stale directories found". Use portable predicates and keep stderr visible while probing:

   ```bash
   for f in "$d"/.git "$d"/.vscode; do [ -e "$f" ] && echo "found: $f"; done
   du -sh "$d"
   stat -c '%n %s bytes' "$d" 2>/dev/null || stat -f '%N %z bytes' "$d"   # GNU first: BSD errors out, but GNU -f would falsely succeed with filesystem stats
   ```

   **e. Remove, then re-verify.** Confirm the path is non-empty, exists, and is neither a repository root nor a base
   worktree:

   ```bash
   if [ -n "<orphaned_dir>" ] && [ -d "<orphaned_dir>" ]; then
     rm -rf "<orphaned_dir>" || echo "ERROR: Failed to remove orphaned directory <orphaned_dir>"
   fi
   ```

   Re-run the scan in (a) afterwards: the directory must be gone, and every remaining directory must still be
   registry-backed. Route any failure into **⚠️ Unremovable Directories / Attention Required**.

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

2. **Process Non-Base Feature & Docs Branches**: For each candidate remote branch (strip `origin/` prefix; ignore
   `origin/HEAD` and `origin/main`):

   - **Extract Remote Branch Name**:
     ```bash
     # Strip remote prefix (e.g. origin/feat-123 -> feat-123, origin/docs/0058-... -> docs/0058-...)
     branch_name="${raw_branch#origin/}"
     ```
   - **Ignore Base Branches**: Skip if `$branch_name` is `HEAD`, `main`, or `master`.
   - **Verify PR Status via GitHub CLI**:
     ```bash
     gh pr list --repo <owner>/<repo> --head "$branch_name" --state all
     ```
   - **Verify Direct or Squash-Merged Status / Completed Bean**: If the associated PR is `MERGED` or `CLOSED` with no
     active work, or if the commit diff is fully contained in `main` (or its associated `.beans/` task is
     `completed`/`scrapped` and the branch is abandoned), the remote branch is stale.
   - **Delete Merged Remote Branch**:
     ```bash
     git -C <repo_worktree> push origin --delete "$branch_name"
     git -C <repo_worktree> fetch origin --prune
     ```

3. **Detect & Prune Holon Flow Provenance Trees (`I-.../**`)**:

   > [!IMPORTANT] **Intent branches and plan branches never have their own PRs.** The Holon flow creates `I-.../_`,
   > `I-.../P-.../_`, and `I-.../P-.../E-.../_` or `.../calibrated`. Only the PR head branch is registered on GitHub.
   > When that PR merges into `main` (often via squash-merge), neither `git branch -r --merged` nor `gh pr list --head`
   > on the parent intent/plan branches will report them as merged. They must be resolved hierarchically by intent
   > prefix.

   **a. Identify Holon flow candidate branches on remote**:

   ```bash
   git -C <repo_worktree> branch -r --list 'origin/I-*' | sed 's/^[ *]*origin\///'
   ```

   **b. Extract unique intent prefixes**: Each flow branch root begins with `I-<timestamp>-<slug>`:

   ```bash
   # Extract unique root intent identifiers
   intent_prefixes=$(git -C <repo_worktree> branch -r --list 'origin/I-*' | sed 's/^[ *]*origin\///' | sed -E 's/^(I-[0-9]+-[^\/]+).*/\1/' | sort -u)
   ```

   **c. Check PR status for each intent tree**: For each `$intent_prefix`, find any Pull Request whose head branch
   contains that prefix:

   ```bash
   gh pr list --repo <owner>/<repo> --state all --search "$intent_prefix in:head" --json number,state,headRefName
   ```

   Alternatively, search merged and closed PRs across the repository:

   ```bash
   gh pr list --repo <owner>/<repo> --state all --json number,state,headRefName \
     --jq '.[] | select(.headRefName | startswith("I-")) | select(.state == "MERGED" or .state == "CLOSED") | .headRefName'
   ```

   **d. Batch delete all branches under merged or closed intent trees**: If the PR for an intent is `MERGED` or `CLOSED`
   (and stage 5 calibration was completed prior to merge per the flow rules), all remote branches belonging to that
   intent tree (`I-<timestamp>-<slug>/**`: intent `/_`, plan `P-.../_`, execution `E-.../_`, and calibration
   `/calibrated`) are obsolete and safe to delete:

   ```bash
   # List all remote branches under this intent prefix
   branches_to_delete=$(git -C <repo_worktree> branch -r --list "origin/$intent_prefix*" | sed 's/^[ *]*origin\///')

   # Delete matched remote branches in a single push call
   if [ -n "$branches_to_delete" ]; then
     echo "$branches_to_delete" | xargs git -C <repo_worktree> push origin --delete
     git -C <repo_worktree> fetch origin --prune
   fi
   ```

---

### Step 5: Clean Local Merged & Stale Branches

Inspect local branches in each repository:

```bash
git -C <repo_worktree> branch -vv
```

1. **Delete Branches with Gone Remotes**: Delete any local branches whose upstream tracking ref is marked `[gone]`:

   ```bash
   git -C <repo_worktree> branch -vv | grep ': gone]' | awk '{print $1}' | xargs -r git -C <repo_worktree> branch -D
   ```

2. **Clean Local Holon Flow Hierarchy Branches (`I-.../**`)**: Flow runs check out or create local
   plan/execution/calibration branches (e.g. `.../calibrated` or `.../_`). Once the remote branches have been pruned and
   the PR is merged, delete these local branches:

   ```bash
   git -C <repo_worktree> branch --list 'I-*' | xargs -r git -C <repo_worktree> branch -D
   ```

3. **Clean Local Feature, Harness & Documentation Branches**: Delete local topic branches (e.g., `docs/0058-...`,
   `docs/bean-updates-...`) once their changes have merged into `main` or their corresponding bean task is completed:
   ```bash
   git -C <repo_worktree> branch -D <stale_local_branch>
   ```

---

### Step 6: Sync & Fast-Forward Base Branches

Ensure the baseline `main` worktree in each repository is fast-forwarded to `origin/main`:

```bash
# Metadata repo root
git pull --ff-only origin main

# apps/holon-agentic-coder
git -C apps/holon-agentic-coder/main pull --ff-only origin main

# apps/holon-coherence
git -C apps/holon-coherence/main pull --ff-only origin main
```

---

### Step 7: Verify Repository Hygiene & Report Summary

Run a final verification across all repositories:

```bash
git status
git branch -a
```

Re-run the Step 3.5(a) disk scan and the Step 3.5(b) metadata listing one final time, and confirm that the two
comparison lists are empty: **every directory on disk is registry-backed, and every registration has a directory.** A
clean report that was derived only from `git worktree list` is not sufficient evidence of hygiene.

Format a concise summary report for the user detailing:

- **Repositories Audited**: All repositories scanned.
- **Worktrees & Directories Removed**: Any temporary worktrees unmounted and physical directories deleted on disk.
- **Orphaned / Superfluous Directories Removed**: Directories present on disk without a worktree registration, what
  remained inside them (e.g. `.idea/`, `*.iml`, caches), and the evidence relied on to prove no unpushed work was
  destroyed.
- **Dangling Worktree Registrations**: Registry entries and `.git/worktrees/<name>` metadata cleared by
  `git worktree prune`, or "None".
- **Remote Branches Deleted**: Remote branches pruned or deleted on GitHub.
- **Local Branches Deleted**: Local stale tracking branches removed.
- **⚠️ Unremovable Directories / Attention Required**: Explicitly itemize any directories that could not be deleted,
  including their path, ownership, and error reason (or state "None" if all directories were cleanly deleted). Also list
  any directory deliberately **kept** because it contained authored work, with its contents.
- **Current Active State**: Table showing clean `main` branches and worktrees.
