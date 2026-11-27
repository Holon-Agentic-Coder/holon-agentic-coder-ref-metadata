#!/usr/bin/env python3
"""Validate the append-only coordinator failure ledger."""

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import timestamps  # noqa: E402

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
    "post-merge",
    "resume-checkpoint",
    "wall-clock",
}
# why: bean 0606; row 38 reuses CF-0028, committed before the duplicate-id check
# why: existed, and the append-only ledger cannot be renumbered
KNOWN_LEGACY_DUPLICATES = {(38, "CF-0028")}


def ledger_number(cf_id):
    match = re.fullmatch(r"CF-(\d{4})", str(cf_id))
    return int(match.group(1)) if match else 0


def check_lines(lines, written_at=None, now=None):
    errors = []
    now = now or timestamps.utc_now()
    previous = None
    highest = 0
    seen = set()
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
        if (n, obj["id"]) not in KNOWN_LEGACY_DUPLICATES:
            number = ledger_number(obj["id"])
            if obj["id"] in seen:
                errors.append(f"line {n}: duplicate id {obj['id']}")
            elif number != highest + 1:
                errors.append(f"line {n}: id {obj['id']} not sequential (expected CF-{highest + 1:04d})")
            seen.add(obj["id"])
            highest = max(highest, number)
        if obj["category"] not in CATEGORIES:
            errors.append(f"line {n}: bad category {obj['category']}")
        if not isinstance(obj["refs"], list):
            errors.append(f"line {n}: refs must be a list")
        written = written_at[n - 1] if written_at and n - 1 < len(written_at) else None
        errors += timestamps.stamp_problems(f"line {n} created_at", obj["created_at"], now, written_at=written)
        stamp = timestamps.parse_strict(obj["created_at"])
        if stamp and previous and stamp < previous:
            errors.append(
                f"line {n}: created_at {obj['created_at']} precedes the previous row (ledger must be ordered)"
            )
        previous = stamp or previous
    return errors


APPEND_ONLY_MESSAGE = (
    "ledger edits lines present at git HEAD (append-only); "
    "only a created_at that postdates its own commit may be corrected"
)


def is_timestamp_correction(line, head_line, head_written):
    try:
        new, old = json.loads(line), json.loads(head_line)
    except ValueError:
        return False
    if {k: v for k, v in new.items() if k != "created_at"} != {k: v for k, v in old.items() if k != "created_at"}:
        return False
    old_stamp = timestamps.parse_strict(old.get("created_at"))
    return head_written is not None and (old_stamp is None or old_stamp > head_written + timestamps.SKEW)


def check_append_only(lines, head_lines, head_written=None):
    if len(lines) < len(head_lines):
        return ["ledger deletes lines present at git HEAD (append-only)"]
    for n, head_line in enumerate(head_lines):
        if lines[n] == head_line:
            continue
        written = head_written[n] if head_written and n < len(head_written) else None
        if not is_timestamp_correction(lines[n], head_line, written):
            return [APPEND_ONLY_MESSAGE]
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
    repo = LEDGER.parents[2]
    rel = str(LEDGER.relative_to(repo))
    shallow = timestamps.is_shallow(repo)
    written = None if shallow else timestamps.blame_times(repo, rel)
    head_written = None if shallow else timestamps.blame_times(repo, rel, "HEAD")
    errors = check_lines(lines, written) + check_append_only(lines, head_version(), head_written)
    for e in errors:
        print(e, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
