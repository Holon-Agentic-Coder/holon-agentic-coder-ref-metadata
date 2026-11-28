#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ATTRIBUTION_LINE = re.compile(
    r"^\s*(?:co-authored-by|co-developed-by|generated-by|assisted-by|generated with \[?claude code)",
    re.IGNORECASE,
)


def find_attribution_lines(message: str) -> list[str]:
    return [line.strip() for line in message.splitlines() if not line.startswith("#") and ATTRIBUTION_LINE.match(line)]


def commit_messages(revision_range: str) -> dict[str, str]:
    listing = subprocess.run(
        ["git", "log", "--format=%H", revision_range], capture_output=True, text=True, check=True
    ).stdout.split()
    return {
        sha: subprocess.run(["git", "log", "-1", "--format=%B", sha], capture_output=True, text=True, check=True).stdout
        for sha in listing
    }


def report(offences: dict[str, list[str]]) -> int:
    for owner, lines in offences.items():
        for line in lines:
            print(f"attribution trailer in {owner}: {line}", file=sys.stderr)
    return 1 if offences else 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--message-file", type=Path)
    group.add_argument("--range", dest="revision_range")
    options = parser.parse_args(argv)
    if options.message_file:
        lines = find_attribution_lines(options.message_file.read_text())
        return report({str(options.message_file): lines} if lines else {})
    messages = commit_messages(options.revision_range)
    return report({sha[:12]: lines for sha, message in messages.items() if (lines := find_attribution_lines(message))})


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
