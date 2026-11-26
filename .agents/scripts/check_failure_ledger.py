#!/usr/bin/env python3
"""Validate the append-only coordinator failure ledger."""

import json
import subprocess
import sys
from pathlib import Path

LEDGER = Path(__file__).resolve().parents[1] / "ledger" / "coordinator-failures.jsonl"
REQUIRED = ("id", "created_at", "session_date", "category", "failure", "my_part", "cost", "rule", "refs")
CATEGORIES = {
    "brief",
    "readiness-check",
    "overlap-scheduling",
    "intent-scope",
    "measurement",
    "conflict-handling",
    "bookkeeping",
    "verification",
}


def check_lines(lines):
    errors = []
    for n, line in enumerate(lines, 1):
        try:
            obj = json.loads(line)
        except ValueError:
            errors.append(f"line {n}: invalid JSON")
            continue
        missing = [k for k in REQUIRED if k not in obj]
        if missing:
            errors.append(f"line {n}: missing {missing}")
            continue
        if obj["id"] != f"CF-{n:04d}":
            errors.append(f"line {n}: id {obj['id']} not sequential")
        if obj["category"] not in CATEGORIES:
            errors.append(f"line {n}: bad category {obj['category']}")
        if not isinstance(obj["refs"], list):
            errors.append(f"line {n}: refs must be a list")
    return errors


def check_append_only(lines, head_lines):
    if lines[: len(head_lines)] != head_lines:
        return ["ledger edits or deletes lines present at git HEAD (append-only)"]
    return []


def head_version(path=LEDGER):
    repo = path.parent
    rel = subprocess.run(
        ["git", "ls-files", "--full-name", path.name], cwd=repo, capture_output=True, text=True
    ).stdout.strip()
    if not rel:
        return []
    out = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=repo, capture_output=True, text=True)
    return out.stdout.splitlines() if out.returncode == 0 else []


def main():
    lines = [x for x in LEDGER.read_text().splitlines() if x.strip()]
    errors = check_lines(lines) + check_append_only(lines, head_version())
    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
