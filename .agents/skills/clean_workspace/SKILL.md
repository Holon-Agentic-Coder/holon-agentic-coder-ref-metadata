---
name: clean-workspace
description:
  Audits, prunes, and safely deletes stale and merged Pull Requests, local Git branches, remote tracking refs,
  detached/merged worktrees, orphaned and superfluous local directories, stale PR review artifacts in local .subagent/,
  and temporary scratch files in todo/, across all managed repositories in the Holon ecosystem (holon-agentic-coder,
  holon-coherence, and holon-agentic-coder-ref-metadata). Activate this skill whenever the user asks to clean up the
  workspace, prune stale or merged branches/worktrees, remove leftover directories, purge .subagent review files, or
  tidy the todo directory.
---

# Clean Workspace Skill (`clean-workspace`)

This skill provides an end-to-end, multi-repository hygiene workflow for auditing, pruning, and safely removing obsolete
branches, merged worktrees, orphaned filesystem directories, intermediate subagent review artifacts, and transient
scratchpad files across the Holon Agentic Coder ecosystem.

---

## 📐 Architecture & Operational Principles

1. **Multi-Repository Ecosystem Scope**: The Holon workspace orchestrates multiple repositories linked via bare clones
   and worktrees:
   - **`holon-agentic-coder`**: Fractal intent evolution engine (bare repo: `apps/holon-agentic-coder/.git`, primary
     worktree: `apps/holon-agentic-coder/main`).
   - **`holon-coherence`**: Optimization proxy gateway & wire telemetry (bare repo: `apps/holon-coherence/.git`, primary
     worktree: `apps/holon-coherence/main`).
   - **`holon-agentic-coder-ref-metadata`**: Control plane, metadata store, and orchestration harness (repository root).
   - Any per-agent feature, task, or verification worktrees nested under `apps/<repo>/<branch-dir>`.

2. **Strict Base Branch & Worktree Protection**: The primary trunk branch (`main`) across all repositories is **strictly
   protected** and must **never** be deleted, force-reset, or modified by cleanup operations:
   - `origin/main` / `origin/HEAD`
   - Local `main` branch
   - Primary `main` worktree directories (`apps/holon-agentic-coder/main`, `apps/holon-coherence/main`, repository root)

3. **Multi-Layer Merge Verification**: A branch or worktree is eligible for deletion only when verified through multiple
   independent layers:
   - **GitHub Pull Request Merged**: Associated Pull Request is in state `MERGED` (verified via `gh pr view` or
     `gh pr list`).
   - **Direct Commit Ancestry**: The branch commits are fully reachable from `origin/main` (`git log origin/main..HEAD`
     is empty). Note that GitHub squash-merges create a new commit SHA on `main`, breaking ancestry checks;
     squash-merged branches must be verified using `gh pr list --state merged --json headRefName`.
   - **Closed / Abandoned PR**: The branch is associated with a `CLOSED` PR with no active work, or corresponds to a
     `completed` or `scrapped` bean in `.beans/` with all necessary code integrated.
   - **Remote Ref Gone**: Tracking ref deleted upstream on `origin` (`[gone]` in `git branch -vv`).

4. **Safe Worktree Teardown Sequence**: Git forbids deleting a local branch that is currently checked out in an active
   worktree. The teardown sequence is:
   1. Inspect worktree cleanliness: `git -C <worktree_dir> status -sb` (ensure no uncommitted or untracked changes).
   2. Unmount worktree: `git -C <repo_main_worktree> worktree remove <worktree_dir>`.
   3. Check physical directory on filesystem: if lingering untracked files (e.g. `.idea/`, `.vscode/`, `.venv/`,
      `__pycache__/`) prevented directory deletion, inspect contents and remove via `rm -rf <worktree_dir>`.
   4. Delete local branch: `git -C <repo_main_worktree> branch -D <branch_name>`.
   5. Prune administrative metadata: `git -C <repo_main_worktree> worktree prune`.

5. **Filesystem Is the Source of Truth for Directories**: `git worktree list` only reports registered worktrees. It
   cannot detect leftover directories whose registrations were already pruned, nor can it prevent directory litter.
   Directory hygiene requires an explicit **registry-vs-disk diff**:
   - Compare all physical directories on disk (`find apps/<repo> -mindepth 1 -maxdepth 1 -type d -not -name '.git'`)
     against `git worktree list --porcelain`.
   - Verify any unregistered directory is truly detached (`git -C <dir> status` fails), has no `.git` file/dir, contains
     only regenerable artifacts (IDE files, caches, virtual environments), and corresponds to a merged branch before
     deleting.

6. **Holon Flow Intent Hierarchy Pruning (`I-.../**`)**: Holon flow runs create multi-level provenance trees on
   `origin`:
   - Intent branch: `I-<timestamp>-<slug>/_`
   - Plan branch: `I-.../P-<timestamp>-<agent>-<model>/_`
   - Execution branch: `I-.../P-.../E-<timestamp>-<agent>-<model>/_`
   - Calibration branch: `I-.../P-.../E-.../calibrated` Intermediate intent and plan branches never have their own PRs.
     When the flow PR (execution or calibrated branch) is merged into `main`, query by intent prefix
     (`I-<timestamp>-<slug>`) and batch delete all related parent and sibling branches from `origin` in a single
     operation.

7. **Local `.subagent/` Review Artifact Hygiene & Active PR Protection**: The multi-agent PR review ensemble
   (`pr-review-loop`, `pr-reviewer`, `pr-review-resolver`) stores intermediate review iterations, candidate diffs,
   reviewer votes, and state files under `.subagent/`. Per AGENTS.md Rule 11 and PR review loop state persistence
   invariants:
   - **STRICT PRESERVATION INVARIANT**:
     - `.subagent/.gitkeep`: Must **NEVER** be deleted.
     - **Active PR Files**: Any review artifacts belonging to open PRs (or unresolved loops) must **NEVER** be deleted.
     - **Permanent State Files**: Across all PRs (even merged/closed), essential loop state files must be preserved:
       `*_state.json`, `*_coordination.json` (and legacy `coordination.json`), `*_loop_history.md`,
       `*_posted_review.md`, and final consensus reports (`*_consensus_review_*.md`).
   - **PRUNABLE ARTIFACTS**:
     - Only when an associated PR is verified as `MERGED` or `CLOSED`, non-permanent intermediate reviewer drafts and
       ephemeral diff dumps (e.g. `*_reviewer_*_iter_*.md`, `*_diff.txt`, `*_meta.json`) may be safely pruned or moved
       to archive directories.

8. **`todo/` Scratchpad Tidy & Strict Preservation Invariant**: The `todo/` directory is a local, git-ignored scratchpad
   for transient notes, flow intents, and agent drafts.
   - **STRICT INVARIANT — PRESERVED FILES**:
     - `todo/.gitkeep`: Must **NEVER** be deleted.
     - `todo/bean-triage-*.md`: The living triage scorecard and priority backlog (e.g.,
       `todo/bean-triage-prioritisation-2026-10-03.md`) is a persistent document and must **NEVER** be deleted.
     - User-authored design specs, notes, or persistent scratchpads explicitly marked as retained.
   - **PRUNABLE TRANSIENT FILES**:
     - Temporary flow intent files (e.g., `todo/intent-*.json`) whose execution and PR lifecycle has fully merged.
     - Temporary debug dumps, one-off test scripts, or ephemeral terminal captures.

---

## 🛠️ Step-by-Step Execution Guide

Follow these sequential phases when executing workspace cleanup:

### Phase 1: Discover Repositories & Synchronize Remote Tracking Refs

Synchronize tracking refs with `origin` across all repositories to ensure `origin/main` and remote tracking refs are
fresh:

```bash
# 1. Metadata root
git fetch origin --prune

# 2. holon-agentic-coder
if [ -d "apps/holon-agentic-coder/main" ]; then
  git -C apps/holon-agentic-coder/main fetch origin --prune
fi

# 3. holon-coherence
if [ -d "apps/holon-coherence/main" ]; then
  git -C apps/holon-coherence/main fetch origin --prune
fi
```

---

### Phase 2: Detect & Delete Merged Remote Branches on GitHub

Inspect remote branches in `holon-agentic-coder` and `holon-coherence`:

#### 1. Standard Feature & Task Branches

Identify branches whose PR is in state `MERGED` or `CLOSED`:

```bash
repo="apps/holon-coherence/main"  # or apps/holon-agentic-coder/main
gh_repo="Holon-Agentic-Coder/holon-coherence"

# List remote branches excluding HEAD and main
git -C "$repo" branch -r | sed 's/^[ *]*origin\///' | grep -vE '^(HEAD|main)$' | while read -r branch; do
  # Check PR status
  pr_state=$(gh pr list --repo "$gh_repo" --head "$branch" --state all --json state --jq '.[0].state' 2>/dev/null)
  if [ "$pr_state" = "MERGED" ] || [ "$pr_state" = "CLOSED" ]; then
    echo "Deleting merged/closed remote branch: $branch"
    git -C "$repo" push origin --delete "$branch"
  fi
done
```

#### 2. Holon Flow Provenance Trees (`I-.../**`)

Group flow branches by intent prefix and delete obsolete hierarchies:

```bash
repo="apps/holon-coherence/main"
gh_repo="Holon-Agentic-Coder/holon-coherence"

# Extract unique root intent identifiers
intent_prefixes=$(git -C "$repo" branch -r --list 'origin/I-*' | sed 's/^[ *]*origin\///' | sed -E 's/^(I-[0-9]+-[^\/]+).*/\1/' | sort -u)

for intent in $intent_prefixes; do
  # Check if any PR under this intent was merged or closed
  is_merged=$(gh pr list --repo "$gh_repo" --state all --search "$intent in:head" --json state --jq '.[] | select(.state == "MERGED" or .state == "CLOSED") | .state' 2>/dev/null | head -n 1)
  if [ -n "$is_merged" ]; then
    echo "Intent $intent is $is_merged. Pruning remote hierarchy..."
    branches_to_delete=$(git -C "$repo" branch -r --list "origin/$intent*" | sed 's/^[ *]*origin\///')
    if [ -n "$branches_to_delete" ]; then
      echo "$branches_to_delete" | xargs git -C "$repo" push origin --delete
    fi
  fi
done

git -C "$repo" fetch origin --prune
```

---

### Phase 3: Audit & Safely Remove Merged Git Worktrees

For each repository, inspect registered worktrees:

```bash
repo="apps/holon-coherence"  # bare repo directory
main_worktree="apps/holon-coherence/main"

git --git-dir="$repo/.git" worktree list
```

For every feature or task worktree (excluding `main`):

1. **Safety Check**: Verify clean status:
   ```bash
   git -C "$worktree_path" status -sb
   ```
   If uncommitted changes exist, stop and report to user.
2. **Unmount Worktree**:
   ```bash
   git -C "$main_worktree" worktree remove "$worktree_path"
   ```
3. **Physical Directory Check**:
   ```bash
   if [ -d "$worktree_path" ]; then
     echo "Removing lingering directory $worktree_path..."
     rm -rf "$worktree_path"
   fi
   ```
4. **Delete Local Branch**:
   ```bash
   git -C "$main_worktree" branch -D "$branch_name"
   ```
5. **Prune Administrative Files**:
   ```bash
   git -C "$main_worktree" worktree prune
   ```

---

### Phase 4: Registry-vs-Disk Diff & Orphan Directory Purge

Derive the complete directory truth by diffing the filesystem against `git worktree list`:

```bash
for repo_dir in apps/holon-agentic-coder apps/holon-coherence; do
  [ -d "$repo_dir/.git" ] || continue

  find "$PWD/$repo_dir" -mindepth 1 -maxdepth 1 -type d -not -name '.git' | sort > /tmp/on_disk.txt
  git --git-dir="$repo_dir/.git" worktree list --porcelain | sed -n 's/^worktree //p' | grep -Fxv "$PWD/$repo_dir" | sort > /tmp/registered.txt

  # Find on disk, but NOT registered
  orphans=$(comm -23 /tmp/on_disk.txt /tmp/registered.txt)
  for d in $orphans; do
    echo "Found orphan candidate: $d"
    # Pre-check: must be detached and contain no .git
    if [ ! -e "$d/.git" ] && git -C "$d" status 2>&1 | grep -q "must be run in a work tree"; then
      echo "Verified detached orphan directory. Residual contents:"
      ls -la "$d"
      rm -rf "$d"
      echo "Removed orphan directory: $d"
    else
      echo "⚠️ WARNING: Directory $d is not an orphan or contains a git repository. Preserving."
    fi
  done
done
```

---

### Phase 5: Clean Local Stale & Tracking Branches

In each repository's primary worktree:

1. **Delete Gone Tracking Branches**:
   ```bash
   git -C <repo_main_worktree> branch -vv | grep ': gone]' | awk '{print $1}' | xargs -r git -C <repo_main_worktree> branch -D
   ```
2. **Delete Local Flow Hierarchy Branches**:
   ```bash
   git -C <repo_main_worktree> branch --list 'I-*' | xargs -r git -C <repo_main_worktree> branch -D
   ```
3. **Delete Merged Feature Branches**:
   ```bash
   git -C <repo_main_worktree> branch --merged origin/main | grep -vE '^\*|main$' | xargs -r git -C <repo_main_worktree> branch -D
   ```

---

### Phase 6: Sync & Fast-Forward Base Branches

Fast-forward the `main` worktree in each repository to `origin/main`:

```bash
# Metadata repo root
git pull --ff-only origin main

# apps/holon-agentic-coder
if [ -d "apps/holon-agentic-coder/main" ]; then
  git -C apps/holon-agentic-coder/main pull --ff-only origin main
fi

# apps/holon-coherence
if [ -d "apps/holon-coherence/main" ]; then
  git -C apps/holon-coherence/main pull --ff-only origin main
fi
```

---

### Phase 7: Clean or Archive Stale `.subagent/` Review Files

Clean up or archive stale intermediate multi-agent review artifacts from merged/closed PRs while strictly preserving
active review loops and permanent state files:

```bash
# Relocate completed intermediate artifacts for closed/merged PRs into .subagent/<repo>_pr<N>_archive/
# and prune archived intermediate bundles older than 30 days:
python3 .agents/skills/clean_workspace/scripts/clean_workspace.py --subagent-only --archive --retention-days 30

# Or delete completed intermediate files immediately:
python3 .agents/skills/clean_workspace/scripts/clean_workspace.py --subagent-only
```

> [!CAUTION] **Strict Preservation Rule**: Never run blanket deletion commands (such as `rm -rf .subagent/*` or
> `find .subagent -type f -delete`). Active PR review loops and permanent state files (`*_state.json`,
> `*_coordination.json`, `*_loop_history.md`, `*_posted_review.md`, and consensus reports) must remain intact.

---

### Phase 8: Clean Transient Scratch Files in `todo/`

Clean completed one-off scratch files while strictly preserving tracking documents:

```bash
if [ -d "todo" ]; then
  # 1. Identify and delete completed intent JSON files
  find todo -mindepth 1 -maxdepth 1 -name "intent-*.json" -type f -exec rm -v {} +

  # 2. Identify ephemeral debug logs or scrap files (e.g. *.tmp, *.log)
  find todo -mindepth 1 -maxdepth 1 \( -name "*.tmp" -o -name "*.log" \) -type f -exec rm -v {} +

  # 3. VERIFY PRESERVATION of persistent files
  [ -f "todo/.gitkeep" ] || touch "todo/.gitkeep"
  echo "Active files remaining in todo/:"
  ls -la todo/
fi
```

> [!CAUTION] **Strict Preservation Rule**: `todo/bean-triage-*.md` and `todo/.gitkeep` must **NEVER** be deleted by any
> cleanup command. If `rm -rf todo/*` is ever considered, **STOP**. Always target specific transient file patterns
> (`intent-*.json`, `*.tmp`, `*.log`).

---

### Phase 9: Verification & Summary Reporting

Verify workspace cleanliness across all targets:

```bash
# 1. Git status check
git status
git -C apps/holon-agentic-coder/main status
git -C apps/holon-coherence/main status

# 2. Worktree lists
git worktree list
git --git-dir=apps/holon-agentic-coder/.git worktree list
git --git-dir=apps/holon-coherence/.git worktree list

# 3. Final disk vs registry diff
for repo in apps/holon-agentic-coder apps/holon-coherence; do
  find "$PWD/$repo" -mindepth 1 -maxdepth 1 -type d -not -name '.git' | sort > /tmp/on_disk.txt
  git --git-dir="$repo/.git" worktree list --porcelain | sed -n 's/^worktree //p' | grep -Fxv "$PWD/$repo" | sort > /tmp/registered.txt
  echo "== $repo orphans =="
  comm -23 /tmp/on_disk.txt /tmp/registered.txt
done
```

Present a formatted Markdown report to the user summarizing:

- **Repositories Audited**: Scanned paths.
- **Worktrees Unmounted & Removed**: Closed/merged worktrees.
- **Remote Branches Pruned**: Remote tracking branches deleted on GitHub.
- **Local Branches Cleaned**: Deleted local branches.
- **Orphaned Directories Purged**: Residual filesystem folders deleted.
- **`.subagent/` Artifacts Purged**: Count and location of purged review files.
- **`todo/` Files Cleaned & Preserved**: Transient files removed vs persistent docs preserved.
- **Current Active State**: Table showing clean `main` branches.

---

## 🤖 Automated Script Execution

This skill includes an automated utility script at `.agents/skills/clean_workspace/scripts/clean_workspace.py`.

### Dry-Run Audit (Default / Safe Mode)

Inspects everything on disk, remotes, worktrees, `.subagent/`, and `todo/` without making changes:

```bash
uv run python .agents/skills/clean_workspace/scripts/clean_workspace.py --dry-run
```

### Active Cleanup Mode

Executes the full 9-phase cleanup with safety confirmations:

```bash
uv run python .agents/skills/clean_workspace/scripts/clean_workspace.py
```

### Specific Target Cleanup

Clean only specific areas:

```bash
# Clean only .subagent review artifacts and todo scratch files
uv run python .agents/skills/clean_workspace/scripts/clean_workspace.py --subagent-only --todo-only

# Clean only git branches and worktrees
uv run python .agents/skills/clean_workspace/scripts/clean_workspace.py --git-only
```
