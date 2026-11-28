#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import timestamps  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
BEANS = REPO / ".beans"
PREFIX = "holon-agentic-coder-ref-metadata"
NAME = re.compile(rf"^{PREFIX}-(\d{{4}})--[a-z0-9][a-z0-9-]*\.md$")
STATUSES = {"draft", "todo", "in-progress", "completed", "scrapped"}
REQUIRED = ("title", "status", "created_at", "updated_at")
STAMPS = ("created_at", "updated_at")


def parse_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fields, positions, heading_id, key = {}, {}, None, None
    for n, line in enumerate(lines[1:], 2):
        if line.strip() == "---":
            return {"fields": fields, "positions": positions, "heading_id": heading_id}
        if line.startswith("# "):
            heading_id = line[2:].strip()
        elif line.startswith("  - ") and key:
            fields[key].append(line[4:].strip().strip('"'))
        elif ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            value = value.strip().strip('"')
            fields[key] = [] if value == "" else value
            positions[key] = n
    return None


def bean_files(beans_dir):
    return sorted(p for p in beans_dir.glob("*.md") if p.name.startswith(PREFIX))


def line_times_for(repo, rel, latest, first, dirty, shallow):
    if shallow:
        return None
    if rel in dirty or rel not in latest or latest[rel] >= timestamps.STRICT_FROM:
        return {"times": timestamps.blame_times(repo, rel), "introduced": first.get(rel)}
    return None


def stamp_problems(key, raw, position, now, line_times):
    value = timestamps.parse_strict(raw) or timestamps.parse_lenient(raw)
    strict = value is None or value >= timestamps.STRICT_FROM
    written = introduced = None
    times = line_times["times"] if line_times else None
    if times and position - 1 < len(times):
        written, introduced = times[position - 1], line_times["introduced"]
    found = timestamps.stamp_problems(key, raw, now, written_at=written, strict=strict, introduced_at=introduced)
    return found, value


def check_bean(path, text, now, line_times):
    problems = []
    name = path.name
    match = NAME.match(name)
    if not match:
        return [f"{name}: file name must be {PREFIX}-NNNN--slug.md"]
    parsed = parse_frontmatter(text)
    if parsed is None:
        return [f"{name}: missing frontmatter"]
    fields = parsed["fields"]
    if parsed["heading_id"] and parsed["heading_id"] != f"{PREFIX}-{match.group(1)}":
        problems.append(f"{name}: frontmatter id {parsed['heading_id']} does not match file name")
    for key in REQUIRED:
        if key not in fields:
            problems.append(f"{name}: missing {key}")
    if fields.get("status") not in STATUSES:
        problems.append(f"{name}: invalid status {fields.get('status')!r}")
    created = updated = None
    for key in STAMPS:
        if key not in fields:
            continue
        found, value = stamp_problems(key, fields[key], parsed["positions"][key], now, line_times)
        problems += [f"{name}: {p}" for p in found]
        if key == "created_at":
            created = value
        else:
            updated = value
    if created and updated and updated < created:
        problems.append(f"{name}: updated_at precedes created_at")
    return problems


def check_collection(entries, now):
    problems = []
    ids = {}
    for path, text, line_times in entries:
        problems += check_bean(path, text, now, line_times)
        match = NAME.match(path.name)
        if match:
            ids.setdefault(int(match.group(1)), []).append(path.name)
    for number, names in ids.items():
        if len(names) > 1:
            problems.append(f"duplicate bean id {number:04d}: {names}")
    if ids:
        missing = sorted(set(range(1, max(ids) + 1)) - set(ids))
        problems += [f"bean id {n:04d} is missing (ids must be sequential)" for n in missing if n not in KNOWN_GAPS]
    known = {f"{PREFIX}-{n:04d}" for n in ids}
    for path, text, _ in entries:
        parsed = parse_frontmatter(text)
        for ref in (parsed["fields"].get("blocked_by") if parsed else None) or []:
            ref = ref if ref.startswith(PREFIX) else f"{PREFIX}-{ref}"
            if ref not in known:
                problems.append(f"{path.name}: blocked_by {ref} does not exist")
    return problems


KNOWN_GAPS = {456, 457, 553, 554, 555}


def load(repo=REPO):
    beans_dir = repo / ".beans"
    shallow = timestamps.is_shallow(repo)
    latest, first = timestamps.commit_times(repo)
    dirty = {
        line[3:].strip()
        for line in subprocess.run(
            ["git", "status", "--porcelain", "--", ".beans"], cwd=repo, capture_output=True, text=True
        ).stdout.splitlines()
    }
    entries = []
    for path in bean_files(beans_dir):
        rel = f".beans/{path.name}"
        entries.append((path, path.read_text(), line_times_for(repo, rel, latest, first, dirty, shallow)))
    return entries


AUDITS = BEANS / "self-improvement-audits.md"
AUDIT_HEADING = re.compile(r"^### (\d{4}-\d{2}-\d{2}T[0-9:]+Z)\b")


def check_audits(text, now, written_at=None):
    problems = []
    previous = None
    for n, line in enumerate(text.splitlines(), 1):
        match = AUDIT_HEADING.match(line)
        if not match:
            continue
        value = timestamps.parse_strict(match.group(1))
        strict = value is None or value >= timestamps.STRICT_FROM
        written = written_at[n - 1] if written_at and n - 1 < len(written_at) else None
        problems += [
            f"self-improvement-audits.md line {n}: {p}"
            for p in timestamps.stamp_problems("entry", match.group(1), now, written_at=written, strict=strict)
        ]
        if strict and value and previous and value > previous:
            problems.append(
                f"self-improvement-audits.md line {n}: entry {match.group(1)} is newer than the entry above it"
            )
        previous = value or previous
    return problems


def load_audits(repo=REPO):
    audits = repo / ".beans" / "self-improvement-audits.md"
    written = None if timestamps.is_shallow(repo) else timestamps.blame_times(repo, ".beans/self-improvement-audits.md")
    return audits.read_text(), written


def main():
    now = timestamps.utc_now()
    audit_text, audit_written = load_audits()
    problems = check_collection(load(), now) + check_audits(audit_text, now, audit_written)
    for problem in problems:
        print(problem, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
