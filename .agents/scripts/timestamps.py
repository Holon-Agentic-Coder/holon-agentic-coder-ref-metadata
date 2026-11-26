#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path

STRICT_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
SKEW = timedelta(minutes=5)
MAX_BEFORE_WRITE = timedelta(hours=24)
STRICT_FROM = datetime(2026, 11, 26, tzinfo=UTC)


def parse_strict(value):
    if not isinstance(value, str) or not STRICT_UTC.match(value):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError:
        return None


def parse_lenient(value):
    try:
        parsed = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def stamp_problems(label, value, now, written_at=None, strict=True, introduced_at=None):
    parsed = parse_strict(value)
    if parsed is None:
        if strict:
            return [f"{label}: {value!r} is not strict UTC YYYY-MM-DDTHH:MM:SSZ"]
        parsed = parse_lenient(value)
        if parsed is None:
            return [f"{label}: {value!r} is not a timestamp"]
    problems = []
    if parsed > now + SKEW:
        problems.append(f"{label}: {value} is in the future (now {now:%Y-%m-%dT%H:%M:%SZ})")
    if written_at is not None and strict:
        if parsed > written_at + SKEW:
            problems.append(f"{label}: {value} is after the commit that wrote it ({written_at:%Y-%m-%dT%H:%M:%SZ})")
        elif written_at == introduced_at and parsed < written_at - MAX_BEFORE_WRITE:
            problems.append(
                f"{label}: {value} is over 24h before the commit that wrote it ({written_at:%Y-%m-%dT%H:%M:%SZ})"
            )
    return problems


def is_shallow(repo):
    out = subprocess.run(["git", "rev-parse", "--is-shallow-repository"], cwd=repo, capture_output=True, text=True)
    return out.stdout.strip() == "true"


def blame_times(repo, rel_path, rev=None):
    cmd = ["git", "blame", "--line-porcelain"] + ([rev] if rev else []) + ["--", rel_path]
    out = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
    if out.returncode != 0:
        return None
    return [
        datetime.fromtimestamp(int(line.split()[1]), UTC)
        for line in out.stdout.splitlines()
        if line.startswith("committer-time ")
    ]


def commit_times(repo):
    out = subprocess.run(
        ["git", "log", "--name-only", "--format=@%ct"], cwd=repo, capture_output=True, text=True
    ).stdout
    latest, first = {}, {}
    current = None
    for line in out.splitlines():
        if line.startswith("@"):
            current = datetime.fromtimestamp(int(line[1:]), UTC)
        elif line.strip():
            latest.setdefault(line, current)
            first[line] = current
    return latest, first


def utc_now():
    return datetime.now(UTC)


def repo_root_of(path):
    return Path(path).resolve().parents[1]
