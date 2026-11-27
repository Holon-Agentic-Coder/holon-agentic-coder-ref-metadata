#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_failure_ledger  # noqa: E402
import timestamps  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
BEANS = ROOT / ".beans"
LEDGER = check_failure_ledger.LEDGER
STAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
LEDGER_FIELDS = ("failure", "my_part", "cost", "rule")


def current_stamp():
    return timestamps.utc_now().strftime(STAMP_FORMAT)


def bean_file(bean_id, beans_dir=BEANS):
    matches = sorted(beans_dir.glob(f"*-{bean_id}-*.md"))
    if len(matches) != 1:
        raise SystemExit(f"stamp: expected exactly one bean file for {bean_id}, found {len(matches)}")
    return matches[0]


def set_frontmatter_stamp(path, field, value):
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    if lines[0].strip() != "---":
        raise SystemExit(f"stamp: {path.name} has no frontmatter")
    closing = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if closing is None:
        raise SystemExit(f"stamp: {path.name} frontmatter is not closed")
    pattern = re.compile(rf"^{field}:\s*.*$")
    for i in range(1, closing):
        if pattern.match(lines[i]):
            lines[i] = f"{field}: {value}"
            break
    else:
        lines.insert(closing, f"{field}: {value}")
    path.write_text("\n".join(lines), encoding="utf-8")


def ledger_rows(ledger=LEDGER):
    return [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]


def next_failure_id(rows):
    numbers = [int(row["id"].removeprefix("CF-")) for row in rows]
    return f"CF-{max(numbers, default=0) + 1:04d}"


def ledger_row(rows, category, fields, refs, stamp):
    if category not in check_failure_ledger.CATEGORIES:
        allowed = ", ".join(sorted(check_failure_ledger.CATEGORIES))
        raise SystemExit(f"stamp: unknown category {category!r}; allowed: {allowed}")
    empty = [name for name in LEDGER_FIELDS if not fields[name].strip()]
    if empty:
        raise SystemExit(f"stamp: empty ledger fields: {empty}")
    return {
        "id": next_failure_id(rows),
        "created_at": stamp,
        "session_date": stamp[:10],
        "category": category,
        **fields,
        "refs": refs,
    }


def append_ledger_row(category, fields, refs, ledger=LEDGER):
    row = ledger_row(ledger_rows(ledger), category, fields, refs, current_stamp())
    existing = ledger.read_text(encoding="utf-8")
    separator = "" if existing.endswith("\n") or not existing else "\n"
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(separator + json.dumps(row, ensure_ascii=False) + "\n")
    return row


def build_parser():
    parser = argparse.ArgumentParser(prog="stamp.py")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("now")
    touch = commands.add_parser("touch")
    touch.add_argument("bean_id")
    created = commands.add_parser("created")
    created.add_argument("bean_id")
    ledger = commands.add_parser("ledger-append")
    ledger.add_argument("category")
    for name in LEDGER_FIELDS:
        ledger.add_argument(f"--{name.replace('_', '-')}", dest=name, required=True)
    ledger.add_argument("--ref", dest="refs", action="append", default=[])
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "now":
        print(current_stamp())
    elif args.command == "touch":
        stamp = current_stamp()
        set_frontmatter_stamp(bean_file(args.bean_id), "updated_at", stamp)
        print(stamp)
    elif args.command == "created":
        stamp = current_stamp()
        path = bean_file(args.bean_id)
        set_frontmatter_stamp(path, "created_at", stamp)
        set_frontmatter_stamp(path, "updated_at", stamp)
        print(stamp)
    else:
        fields = {name: getattr(args, name) for name in LEDGER_FIELDS}
        print(append_ledger_row(args.category, fields, args.refs)["id"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
