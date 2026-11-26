#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MAIN_WORKTREES = ("apps/holon-agentic-coder/main", "apps/holon-coherence/main")
ALLOWED_UNTRACKED = {"?? todo/"}


def git(worktree: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "--no-optional-locks", "-C", str(worktree), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )


def check_worktree(worktree: Path) -> list[str]:
    if not worktree.is_dir():
        return [f"{worktree}: missing"]
    violations: list[str] = []
    branch = git(worktree, "symbolic-ref", "--short", "-q", "HEAD").stdout.strip()
    if branch != "main":
        violations.append(f"{worktree}: on {branch or 'a detached HEAD'}, not main")
    dirty = [
        line for line in git(worktree, "status", "--porcelain").stdout.splitlines() if line not in ALLOWED_UNTRACKED
    ]
    violations.extend(f"{worktree}: not clean: {line}" for line in dirty)
    if git(worktree, "merge-base", "--is-ancestor", "HEAD", "origin/main").returncode != 0:
        violations.append(f"{worktree}: HEAD is not an ancestor of, or equal to, origin/main")
    return violations


def main(argv: list[str]) -> int:
    root = Path(argv[0]) if argv else REPOSITORY_ROOT
    violations = [violation for relative in MAIN_WORKTREES for violation in check_worktree(root / relative)]
    for violation in violations:
        print(violation, file=sys.stderr)
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
