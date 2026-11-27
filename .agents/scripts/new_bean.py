#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import harness_lock  # noqa: E402

PREFIX = "holon-agentic-coder-ref-metadata"
BEAN_FILE = re.compile(rf"^{PREFIX}-(\d{{4}})--")
SLUG_LIMIT = 50
TYPES = ("task", "bug", "feature", "epic", "milestone")
PRIORITIES = ("critical", "high", "normal", "low", "deferred")


def slugify(title):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:SLUG_LIMIT].rstrip("-")
    if not slug:
        raise ValueError("title yields an empty slug")
    return slug


def next_bean_number(beans_directory):
    numbers = [int(match.group(1)) for path in beans_directory.glob("*.md") if (match := BEAN_FILE.match(path.name))]
    return max(numbers, default=0) + 1


def clock_read_stamp():
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def skeleton(number, title, bean_type, priority, tags, stamp):
    tag_lines = "".join(f"  - {tag}\n" for tag in tags)
    tag_block = f"tags:\n{tag_lines}" if tags else ""
    return (
        f'---\n# {PREFIX}-{number:04d}\ntitle: "{title}"\nstatus: todo\ntype: {bean_type}\npriority: {priority}\n'
        f"{tag_block}created_at: {stamp}\nupdated_at: {stamp}\n---\n\n## Notes\n\n## Resolution\n"
    )


def repo_root(start):
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=start, capture_output=True, text=True, check=True)
    return Path(top.stdout.strip())


def create_bean(repo, title, bean_type="task", priority="normal", tags=()):
    if '"' in title:
        raise ValueError("title must not contain double quotes")
    beans_directory = repo / ".beans"
    with harness_lock.exclusive_harness_lock(repo):
        number = next_bean_number(beans_directory)
        path = beans_directory / f"{PREFIX}-{number:04d}--{slugify(title)}.md"
        path.write_text(skeleton(number, title, bean_type, priority, tags, clock_read_stamp()))
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Allocate the next bean id and write its skeleton.")
    parser.add_argument("title")
    parser.add_argument("--type", choices=TYPES, default="task")
    parser.add_argument("--priority", choices=PRIORITIES, default="normal")
    parser.add_argument("--tag", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        path = create_bean(repo_root(Path.cwd()), args.title, args.type, args.priority, args.tag)
    except (ValueError, harness_lock.HarnessLockTimeout) as error:
        print(error, file=sys.stderr)
        return 1
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
