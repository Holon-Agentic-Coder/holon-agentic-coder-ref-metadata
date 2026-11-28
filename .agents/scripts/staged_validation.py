#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_beans  # noqa: E402
import check_failure_ledger  # noqa: E402
import timestamps  # noqa: E402

LEDGER_PATH = ".agents/ledger/coordinator-failures.jsonl"
AUDITS_PATH = ".beans/self-improvement-audits.md"


def git_output(repo, *arguments):
    return subprocess.run(["git", *arguments], cwd=repo, capture_output=True, text=True)


def staged_paths(repo):
    listing = git_output(repo, "diff", "--cached", "--name-only", "--diff-filter=ACMRD")
    return [line for line in listing.stdout.splitlines() if line]


def staged_blob(repo, path):
    shown = git_output(repo, "show", f":{path}")
    return shown.stdout if shown.returncode == 0 else None


def head_blob(repo, path):
    shown = git_output(repo, "show", f"HEAD:{path}")
    return shown.stdout if shown.returncode == 0 else None


def indexed_paths(repo, prefix):
    listing = git_output(repo, "ls-files", "--cached", "--", prefix)
    return [line for line in listing.stdout.splitlines() if line]


def line_times_for_staged(repo, path, text, now):
    if head_blob(repo, path) == text:
        return None
    count = len(text.splitlines())
    introduced = now if head_blob(repo, path) is None else None
    return {"times": [now] * count, "introduced": introduced}


def staged_bean_entries(repo, now):
    entries = []
    for path in indexed_paths(repo, ".beans"):
        name = Path(path).name
        if not name.startswith(check_beans.PREFIX):
            continue
        text = staged_blob(repo, path)
        entries.append((Path(path), text, line_times_for_staged(repo, path, text, now)))
    return entries


def staged_bean_problems(repo, now):
    problems = check_beans.check_collection(staged_bean_entries(repo, now), now)
    audits = staged_blob(repo, AUDITS_PATH)
    if audits is not None:
        problems += check_beans.check_audits(audits, now)
    return problems


def staged_ledger_problems(repo, now):
    text = staged_blob(repo, LEDGER_PATH)
    if text is None:
        return []
    lines = [line for line in text.splitlines() if line.strip()]
    head_text = head_blob(repo, LEDGER_PATH) or ""
    head_lines = head_text.splitlines()
    head_written = timestamps.blame_times(repo, LEDGER_PATH, "HEAD") if head_lines else None
    return check_failure_ledger.check_lines(lines, None, now) + check_failure_ledger.check_append_only(
        lines, head_lines, head_written
    )


def touches_beans(paths):
    return any(path.startswith(".beans/") for path in paths)


def staged_problems(repo, now=None):
    now = now or timestamps.utc_now()
    paths = staged_paths(repo)
    problems = []
    if touches_beans(paths):
        problems += staged_bean_problems(repo, now)
    if LEDGER_PATH in paths:
        problems += staged_ledger_problems(repo, now)
    return problems


def main():
    repo = Path(git_output(Path.cwd(), "rev-parse", "--show-toplevel").stdout.strip())
    problems = staged_problems(repo)
    for problem in problems:
        print(problem, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
