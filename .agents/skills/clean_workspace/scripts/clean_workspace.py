#!/usr/bin/env python3
"""Workspace cleanup utility for the Holon Agentic Coder ecosystem.

Audits, prunes, and safely deletes merged worktrees, local/remote branches,
orphaned directories, .subagent review files, and transient files in todo/.
"""

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Callable, Dict, List, Optional, Set, Tuple

REPO_MAP: Dict[str, str] = {
    "holon-coherence": "Holon-Agentic-Coder/holon-coherence",
    "holon-agentic-coder": "Holon-Agentic-Coder/holon-agentic-coder",
    "holon-agentic-coder-ref-metadata": "Holon-Agentic-Coder/holon-agentic-coder-ref-metadata",
}


def format_rel(path: Path, root: Optional[Path]) -> str:
    """Format path relative to root to adhere to Rule 4."""
    if root is not None:
        try:
            return str(path.relative_to(root))
        except ValueError:
            pass
    return str(path)


def run_cmd(
    cmd: List[str], cwd: Optional[Path] = None, check: bool = False
) -> Tuple[int, str, str]:
    """Run a command and return (exit_code, stdout, stderr)."""
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            check=check,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def is_git_clean(worktree: Path) -> bool:
    """Check if a git worktree has uncommitted or untracked changes."""
    code, stdout, _ = run_cmd(["git", "status", "--porcelain"], cwd=worktree)
    return code == 0 and len(stdout.strip()) == 0


def get_pr_status(gh_repo: str, branch: str) -> Optional[str]:
    """Query GitHub PR state for a branch via gh CLI."""
    cmd = [
        "gh",
        "pr",
        "list",
        "--repo",
        gh_repo,
        "--head",
        branch,
        "--state",
        "all",
        "--json",
        "state",
        "--jq",
        ".[0].state",
    ]
    code, stdout, _ = run_cmd(cmd)
    if code == 0 and stdout:
        return stdout.strip()
    return None


def get_pr_status_by_number(gh_repo: str, pr_num: str) -> Optional[str]:
    """Query GitHub PR state for a PR number via gh CLI."""
    cmd = [
        "gh",
        "pr",
        "view",
        pr_num,
        "--repo",
        gh_repo,
        "--json",
        "state",
        "--jq",
        ".state",
    ]
    code, stdout, _ = run_cmd(cmd)
    if code == 0 and stdout:
        return stdout.strip()
    return None


def is_permanent_subagent_file(filename: str) -> bool:
    """Check if a file in .subagent/ is a permanent state file."""
    if filename == ".gitkeep":
        return True
    if filename == "coordination.json" or filename.endswith("_coordination.json"):
        return True
    if filename.endswith("_state.json"):
        return True
    if filename.endswith("_loop_history.md"):
        return True
    if filename.endswith("_posted_review.md"):
        return True
    if "_consensus_review_" in filename:
        return True
    return False


def get_merged_intent_trees(gh_repo: str, repo_worktree: Path) -> Set[str]:
    """Find intent prefixes (I-*) whose PRs are MERGED or CLOSED."""
    code, stdout, _ = run_cmd(
        ["git", "branch", "-r", "--list", "origin/I-*"], cwd=repo_worktree
    )
    if code != 0 or not stdout:
        return set()

    branches = [line.strip().replace("origin/", "") for line in stdout.splitlines() if line.strip()]
    prefixes: Set[str] = set()
    for b in branches:
        parts = b.split("/")
        if parts:
            prefixes.add(parts[0])

    merged_prefixes: Set[str] = set()
    for prefix in prefixes:
        cmd = [
            "gh",
            "pr",
            "list",
            "--repo",
            gh_repo,
            "--state",
            "all",
            "--search",
            f"{prefix} in:head",
            "--json",
            "state",
            "--jq",
            ".[].state",
        ]
        p_code, p_out, _ = run_cmd(cmd)
        if p_code == 0 and p_out:
            states = p_out.splitlines()
            if any(s in ("MERGED", "CLOSED") for s in states):
                merged_prefixes.add(prefix)

    return merged_prefixes


def clean_remotes(
    repo_worktree: Path, gh_repo: str, dry_run: bool
) -> List[str]:
    """Audit and delete merged remote branches."""
    deleted: List[str] = []
    # 1. Check intent hierarchies
    merged_intents = get_merged_intent_trees(gh_repo, repo_worktree)
    for intent in merged_intents:
        code, stdout, _ = run_cmd(
            ["git", "branch", "-r", "--list", f"origin/{intent}*"],
            cwd=repo_worktree,
        )
        if code == 0 and stdout:
            for line in stdout.splitlines():
                b = line.strip().replace("origin/", "")
                if b and not b.startswith("HEAD") and b != "main":
                    if dry_run:
                        deleted.append(f"[dry-run] origin/{b}")
                    else:
                        d_code, _, _ = run_cmd(
                            ["git", "push", "origin", "--delete", b],
                            cwd=repo_worktree,
                        )
                        if d_code == 0:
                            deleted.append(f"origin/{b}")

    # 2. Check standard non-base branches
    code, stdout, _ = run_cmd(["git", "branch", "-r"], cwd=repo_worktree)
    if code == 0 and stdout:
        for line in stdout.splitlines():
            b = line.strip().replace("origin/", "")
            if (
                not b
                or b.startswith("HEAD")
                or b == "main"
                or any(b.startswith(mi) for mi in merged_intents)
            ):
                continue
            pr_state = get_pr_status(gh_repo, b)
            if pr_state in ("MERGED", "CLOSED"):
                if dry_run:
                    deleted.append(f"[dry-run] origin/{b}")
                else:
                    d_code, _, _ = run_cmd(
                        ["git", "push", "origin", "--delete", b],
                        cwd=repo_worktree,
                    )
                    if d_code == 0:
                        deleted.append(f"origin/{b}")

    if not dry_run and deleted:
        run_cmd(["git", "fetch", "origin", "--prune"], cwd=repo_worktree)

    return deleted


def clean_worktrees(
    bare_dir: Path,
    main_worktree: Path,
    gh_repo: str,
    dry_run: bool,
    root: Optional[Path] = None,
) -> Tuple[List[str], List[str]]:
    """Unmount merged worktrees and delete their branches."""
    removed_worktrees: List[str] = []
    deleted_branches: List[str] = []

    code, stdout, _ = run_cmd(
        ["git", "--git-dir", str(bare_dir), "worktree", "list", "--porcelain"]
    )
    if code != 0 or not stdout:
        return removed_worktrees, deleted_branches

    # Parse porcelain output
    worktree_blocks = stdout.strip().split("\n\n")
    for block in worktree_blocks:
        lines = block.splitlines()
        wt_path: Optional[Path] = None
        branch_ref: Optional[str] = None
        for l in lines:
            if l.startswith("worktree "):
                wt_path = Path(l.replace("worktree ", "").strip())
            elif l.startswith("branch "):
                branch_ref = l.replace("branch ", "").strip()

        if not wt_path or not branch_ref:
            continue

        # Skip main worktree and bare repo itself
        if wt_path == main_worktree or wt_path == bare_dir:
            continue

        branch_name = branch_ref.replace("refs/heads/", "")
        rel_wt = format_rel(wt_path, root)

        # Check if worktree is clean
        if not is_git_clean(wt_path):
            print(
                f"⚠️  Skipping dirty worktree with uncommitted changes: {rel_wt}"
            )
            continue

        # Check if branch is merged or closed
        is_safe = False
        pr_state = get_pr_status(gh_repo, branch_name)
        if pr_state in ("MERGED", "CLOSED"):
            is_safe = True
        else:
            # Check commit ancestry
            a_code, a_out, _ = run_cmd(
                ["git", "log", "origin/main..HEAD", "--oneline"], cwd=wt_path
            )
            if a_code == 0 and not a_out.strip():
                is_safe = True

        if is_safe:
            if dry_run:
                removed_worktrees.append(f"[dry-run] {rel_wt}")
                deleted_branches.append(f"[dry-run] {branch_name}")
            else:
                # Remove worktree with --force to handle untracked/ignored files like .venv
                r_code, _, _ = run_cmd(
                    ["git", "worktree", "remove", "--force", str(wt_path)], cwd=main_worktree
                )
                # Delete lingering directory if any
                if wt_path.exists():
                    shutil.rmtree(wt_path, ignore_errors=True)

                if r_code == 0 or not wt_path.exists():
                    removed_worktrees.append(rel_wt)

                # Delete branch
                b_code, _, _ = run_cmd(
                    ["git", "branch", "-D", branch_name], cwd=main_worktree
                )
                if b_code == 0:
                    deleted_branches.append(branch_name)

    if not dry_run:
        run_cmd(["git", "worktree", "prune"], cwd=main_worktree)

    return removed_worktrees, deleted_branches


def clean_orphaned_dirs(
    bare_dir: Path, apps_dir: Path, dry_run: bool, root: Optional[Path] = None
) -> List[str]:
    """Diff filesystem against worktree registry to find and purge orphans."""
    purged: List[str] = []
    if not apps_dir.exists():
        return purged

    # Get registered paths
    code, stdout, _ = run_cmd(
        ["git", "--git-dir", str(bare_dir), "worktree", "list", "--porcelain"]
    )
    registered: Set[Path] = set()
    if code == 0 and stdout:
        for line in stdout.splitlines():
            if line.startswith("worktree "):
                registered.add(Path(line.replace("worktree ", "").strip()))

    # Find directories on disk
    for item in apps_dir.iterdir():
        if (
            not item.is_dir()
            or item.name == ".git"
            or item.name == "main"
            or item in registered
        ):
            continue

        # Pre-check orphan safety
        git_probe = item / ".git"
        if git_probe.exists():
            continue

        s_code, _, s_err = run_cmd(["git", "status"], cwd=item)
        if "must be run in a work tree" in s_err or s_code != 0:
            rel_item = format_rel(item, root)
            if dry_run:
                purged.append(f"[dry-run] {rel_item}")
            else:
                shutil.rmtree(item, ignore_errors=True)
                purged.append(rel_item)

    return purged


def clean_subagent_files(
    root: Path,
    dry_run: bool,
    pr_status_fn: Optional[Callable[[str, str], Optional[str]]] = None,
) -> List[str]:
    """Prune stale PR review and intermediate files in .subagent/."""
    if pr_status_fn is None:
        pr_status_fn = get_pr_status_by_number

    purged: List[str] = []
    subagent_dirs = [
        root / ".subagent",
        root / "apps" / "holon-agentic-coder" / "main" / ".subagent",
        root / "apps" / "holon-coherence" / "main" / ".subagent",
    ]
    pr_cache: Dict[Tuple[str, str], Optional[str]] = {}

    for s_dir in subagent_dirs:
        if not s_dir.exists() or not s_dir.is_dir():
            continue
        for f in s_dir.iterdir():
            if not f.is_file():
                continue
            if is_permanent_subagent_file(f.name):
                continue

            # Extract repo and PR number
            m = re.search(r"^([a-zA-Z0-9-]+)_pr(\d+)_", f.name)
            if m:
                repo_key = m.group(1)
                pr_num = m.group(2)
                gh_repo = REPO_MAP.get(repo_key, f"Holon-Agentic-Coder/{repo_key}")
                cache_key = (gh_repo, pr_num)
                if cache_key not in pr_cache:
                    pr_cache[cache_key] = pr_status_fn(gh_repo, pr_num)
                pr_state = pr_cache[cache_key]

                # Protect active or unknown PR files
                if pr_state not in ("MERGED", "CLOSED"):
                    continue
            else:
                # If file is not associated with a PR, preserve it to protect active session state
                continue

            rel_path = format_rel(f, root)
            if dry_run:
                purged.append(f"[dry-run] {rel_path}")
            else:
                try:
                    f.unlink()
                    purged.append(rel_path)
                except OSError:
                    pass
    return purged


def clean_todo_files(root: Path, dry_run: bool) -> Tuple[List[str], List[str]]:
    """Clean transient scratch files in todo/ while preserving persistent documents."""
    todo_dir = root / "todo"
    purged: List[str] = []
    preserved: List[str] = []

    if not todo_dir.exists() or not todo_dir.is_dir():
        return purged, preserved

    for item in todo_dir.iterdir():
        if item.name == ".gitkeep" or item.name.startswith("bean-triage-"):
            preserved.append(item.name)
            continue

        # Delete transient patterns
        if item.is_file() and (
            item.name.startswith("intent-")
            or item.suffix in (".tmp", ".log", ".bak")
        ):
            if dry_run:
                purged.append(f"[dry-run] {item.name}")
            else:
                try:
                    item.unlink()
                    purged.append(item.name)
                except OSError:
                    pass
        else:
            preserved.append(item.name)

    return purged, preserved


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean up merged worktrees, branches, directories, .subagent, and todo."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform an audit without making any destructive changes",
    )
    parser.add_argument(
        "--git-only",
        action="store_true",
        help="Clean only git branches, remotes, and worktrees",
    )
    parser.add_argument(
        "--subagent-only",
        action="store_true",
        help="Clean only .subagent review files",
    )
    parser.add_argument(
        "--todo-only",
        action="store_true",
        help="Clean only transient files in todo/",
    )
    args = parser.parse_args()

    root = Path.cwd()
    clean_all = not (args.git_only or args.subagent_only or args.todo_only)

    print("═════════════════════════════════════════════════════════════════════")
    print(
        f"🧹  Holon Ecosystem Workspace Cleanup {'[DRY RUN]' if args.dry_run else ''}"
    )
    print("═════════════════════════════════════════════════════════════════════")

    managed_repos = [
        (
            "holon-coherence",
            root / "apps" / "holon-coherence" / ".git",
            root / "apps" / "holon-coherence" / "main",
            root / "apps" / "holon-coherence",
            "Holon-Agentic-Coder/holon-coherence",
        ),
        (
            "holon-agentic-coder",
            root / "apps" / "holon-agentic-coder" / ".git",
            root / "apps" / "holon-agentic-coder" / "main",
            root / "apps" / "holon-agentic-coder",
            "Holon-Agentic-Coder/holon-agentic-coder",
        ),
    ]

    # 1. Git cleanups
    if clean_all or args.git_only:
        print("\n▶ Synchronizing and cleaning Git targets...")
        # Root metadata repo
        run_cmd(["git", "fetch", "origin", "--prune"], cwd=root)

        for name, bare, main_wt, apps_dir, gh_repo in managed_repos:
            if not bare.exists() or not main_wt.exists():
                continue
            print(f"\n─── Auditing {name} ───")
            run_cmd(["git", "fetch", "origin", "--prune"], cwd=main_wt)

            # Clean remotes
            del_remotes = clean_remotes(main_wt, gh_repo, args.dry_run)
            if del_remotes:
                print(f"  • Deleted remote branches: {', '.join(del_remotes)}")

            # Clean worktrees
            rm_wt, del_br = clean_worktrees(
                bare, main_wt, gh_repo, args.dry_run, root=root
            )
            if rm_wt:
                print(f"  • Unmounted worktrees: {', '.join(rm_wt)}")
            if del_br:
                print(f"  • Deleted local branches: {', '.join(del_br)}")

            # Clean orphans
            purged_orphans = clean_orphaned_dirs(bare, apps_dir, args.dry_run, root=root)
            if purged_orphans:
                print(
                    f"  • Purged orphaned directories: {', '.join(purged_orphans)}"
                )

            # Fast forward main
            if not args.dry_run:
                ff_code, _, _ = run_cmd(
                    ["git", "pull", "--ff-only", "origin", "main"], cwd=main_wt
                )
                if ff_code == 0:
                    print("  • Fast-forwarded main to origin/main")

    # 2. Subagent cleanups
    if clean_all or args.subagent_only:
        print("\n▶ Auditing .subagent review artifacts...")
        purged_subagent = clean_subagent_files(root, args.dry_run)
        if purged_subagent:
            print(
                f"  • Cleaned {len(purged_subagent)} file(s): {', '.join(purged_subagent)}"
            )
        else:
            print("  • .subagent directories are already clean.")

    # 3. Todo cleanups
    if clean_all or args.todo_only:
        print("\n▶ Auditing todo/ scratchpad...")
        purged_todo, preserved_todo = clean_todo_files(root, args.dry_run)
        if purged_todo:
            print(
                f"  • Cleaned {len(purged_todo)} transient file(s): {', '.join(purged_todo)}"
            )
        else:
            print("  • Zero transient scratch files in todo/.")
        print(f"  • Preserved persistent files: {', '.join(preserved_todo)}")

    print("\n═════════════════════════════════════════════════════════════════════")
    print("✅  Workspace cleanup audit completed.")
    print("═════════════════════════════════════════════════════════════════════\n")


if __name__ == "__main__":
    main()
