#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import harness_lock  # noqa: E402
import staged_validation  # noqa: E402

PROTECTED_BRANCHES = {"main", "master"}
INDEX_WAIT_SECONDS = 120
POLL_SECONDS = 0.5


class HarnessCommitError(RuntimeError):
    pass


def git(repo, *arguments, check=True):
    done = subprocess.run(["git", *arguments], cwd=repo, capture_output=True, text=True)
    if check and done.returncode != 0:
        raise HarnessCommitError(f"git {' '.join(arguments)} failed: {(done.stderr or done.stdout).strip()}")
    return done


def repo_root(start):
    return Path(git(start, "rev-parse", "--show-toplevel").stdout.strip())


def current_branch(repo):
    return git(repo, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()


def relative_paths(repo, paths):
    if not paths:
        raise HarnessCommitError("no paths given; name every file to commit")
    resolved = []
    for raw in paths:
        absolute = (Path(raw) if Path(raw).is_absolute() else repo / raw).resolve()
        if absolute.is_dir():
            raise HarnessCommitError(f"{raw} is a directory; name files explicitly")
        try:
            resolved.append(str(absolute.relative_to(repo.resolve())))
        except ValueError:
            raise HarnessCommitError(f"{raw} is outside the repository") from None
    return resolved


def index_is_empty(repo):
    return git(repo, "diff", "--cached", "--quiet", check=False).returncode == 0


def wait_for_empty_index(repo, timeout):
    deadline = time.monotonic() + timeout
    while not index_is_empty(repo):
        if time.monotonic() >= deadline:
            staged = git(repo, "diff", "--cached", "--name-only").stdout.split()
            raise HarnessCommitError(f"index not empty after {timeout}s (another agent staged: {staged})")
        time.sleep(POLL_SECONDS)


def prettier_format(repo, paths):
    markdown = [path for path in paths if path.endswith(".md") and (repo / path).exists()]
    if not markdown:
        return
    done = subprocess.run(["npx", "prettier", "--write", *markdown], cwd=repo, capture_output=True, text=True)
    if done.returncode != 0:
        raise HarnessCommitError(f"prettier failed: {(done.stderr or done.stdout).strip()}")


def unstage_everything(repo):
    git(repo, "reset", "-q", check=False)


def stage_named_paths(repo, paths):
    git(repo, "add", "--", *paths)
    if index_is_empty(repo):
        raise HarnessCommitError("nothing to commit for the named paths")


def refuse_invalid_staged_content(repo):
    problems = staged_validation.staged_problems(repo)
    if problems:
        raise HarnessCommitError("staged content failed validation:\n" + "\n".join(problems))


def push_with_rebase(repo, branch):
    pushed = git(repo, "push", "origin", branch, check=False)
    if pushed.returncode == 0:
        return
    git(repo, "pull", "--rebase", "origin", branch)
    git(repo, "push", "origin", branch)


def commit_and_push(repo, message, paths, push=True, formatter=prettier_format, index_wait=INDEX_WAIT_SECONDS):
    branch = current_branch(repo)
    if branch in PROTECTED_BRANCHES or branch == "HEAD":
        raise HarnessCommitError(f"refusing to commit on {branch}")
    named = relative_paths(repo, paths)
    with harness_lock.exclusive_harness_lock(repo):
        wait_for_empty_index(repo, index_wait)
        try:
            formatter(repo, named)
            stage_named_paths(repo, named)
            refuse_invalid_staged_content(repo)
            git(repo, "commit", "-q", "-m", message, "--", *named)
        except BaseException:
            unstage_everything(repo)
            raise
        sha = git(repo, "rev-parse", "--short", "HEAD").stdout.strip()
        if push:
            push_with_rebase(repo, branch)
    return sha


def main(argv=None):
    parser = argparse.ArgumentParser(description="Serialised commit path for the shared harness branch.")
    parser.add_argument("message")
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--no-push", action="store_true")
    args = parser.parse_args(argv)
    try:
        sha = commit_and_push(repo_root(Path.cwd()), args.message, args.paths, push=not args.no_push)
    except (HarnessCommitError, harness_lock.HarnessLockTimeout) as error:
        print(error, file=sys.stderr)
        return 1
    print(sha)
    return 0


if __name__ == "__main__":
    sys.exit(main())
