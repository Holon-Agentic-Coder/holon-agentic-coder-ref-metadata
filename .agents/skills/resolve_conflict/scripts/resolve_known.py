#!/usr/bin/env python3
"""Resolve the append-only conflicts that need no judgement, inside a merge in progress.

Handles ``*.jsonl`` ledgers (the base branch's file kept byte for byte, only the branch's new rows appended by
``created_at``), the knowledge-base and wisdom ``index.json`` files (union of ``entries`` by ``kb_id`` or
``wb_id``), and a knowledge file that both sides created with the same content (its id is a content hash) and that
differs only in ``created_ts``: the base branch's copy is kept. Both sides only ever add rows, so nothing is dropped.
Every other conflicted path is listed and left untouched for a human-style decision.
"""

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime


def git(*args: str, cwd: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


def stage(n: int, path: str, cwd: str) -> str:
    return git("show", f":{n}:{path}", cwd=cwd)


def _stamp(line: str) -> datetime:
    """Parse ``created_at`` (``Z`` or an offset) as UTC; a missing or unparsable value sorts first."""
    raw = json.loads(line).get("created_at") or ""
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return datetime.min.replace(tzinfo=UTC)
    return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed.astimezone(UTC)


def merge_ledger_text(main_text: str, branch_text: str) -> tuple[str, int, int]:
    """Keep main's text exactly as it is and append only the branch's rows that main lacks, by ``created_at``."""
    main = [line for line in main_text.splitlines() if line.strip()]
    ours = [line for line in branch_text.splitlines() if line.strip()]
    remaining: dict[str, int] = {}
    for line in main:
        remaining[line] = remaining.get(line, 0) + 1
    extra = []
    for line in ours:
        if remaining.get(line, 0) > 0:
            remaining[line] -= 1
        else:
            extra.append(line)

    extra.sort(key=_stamp)  # stable: equal stamps keep the branch's order
    head = main_text if main_text.endswith("\n") or not main_text else main_text + "\n"
    return head + "".join(line + "\n" for line in extra), len(main), len(extra)


def merge_jsonl(path: str, cwd: str, base_stage: int = 3) -> tuple[int, int]:
    """Merging origin/main into a branch: stage 3 is main (kept as is), stage 2 the branch; ``base_stage=2`` flips."""
    text, kept, added = merge_ledger_text(stage(base_stage, path, cwd), stage(5 - base_stage, path, cwd))
    with open(f"{cwd}/{path}", "w") as handle:
        handle.write(text)
    return kept, added


def merge_kb_index(path: str, cwd: str, key: str = "kb_id") -> tuple[int, int]:
    main = json.loads(stage(3, path, cwd))
    ours = json.loads(stage(2, path, cwd))
    seen = {entry[key] for entry in main["entries"]}
    extra = [entry for entry in ours["entries"] if entry[key] not in seen]
    main["entries"] += extra
    main["updated_ts"] = max(ours.get("updated_ts", ""), main.get("updated_ts", ""))
    with open(f"{cwd}/{path}", "w") as handle:
        json.dump(main, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return len(main["entries"]) - len(extra), len(extra)


def _without_created_ts(text: str) -> dict:
    data = json.loads(text)
    data.pop("created_ts", None)
    return data


def keep_base_copy_when_only_created_ts_differs(path: str, cwd: str) -> bool:
    """Both sides added the same knowledge file; take the base branch's copy when nothing but ``created_ts`` differs."""
    try:
        same = _without_created_ts(stage(3, path, cwd)) == _without_created_ts(stage(2, path, cwd))
    except (subprocess.CalledProcessError, ValueError):
        return False
    if same:
        with open(f"{cwd}/{path}", "w") as handle:
            handle.write(stage(3, path, cwd))
    return same


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="worktree with a merge in progress")
    parser.add_argument(
        "--base-stage",
        type=int,
        choices=(2, 3),
        default=3,
        help="stage kept as is: 3 (default) merging origin/main into the branch, 2 merging the branch into main",
    )
    args = parser.parse_args()
    conflicted = git("diff", "--name-only", "--diff-filter=U", cwd=args.repo).split()
    left = []
    for path in conflicted:
        if path.endswith(".jsonl"):
            kept, added = merge_jsonl(path, args.repo, args.base_stage)
        elif path.endswith("index.json") and "/kb/" in path:
            kept, added = merge_kb_index(path, args.repo)
        elif path.endswith("index.json") and "/wisdom/" in path:
            kept, added = merge_kb_index(path, args.repo, key="wb_id")
        elif (
            path.startswith("holon-knowledge/")
            and path.endswith(".json")
            and keep_base_copy_when_only_created_ts_differs(path, args.repo)
        ):
            kept, added = 1, 0
        else:
            left.append(path)
            continue
        git("add", path, cwd=args.repo)
        print(f"resolved {path}: {kept} from the base branch, {added} added from this branch")
    for path in left:
        print(f"NEEDS-JUDGEMENT {path}")
    return 1 if left else 0


if __name__ == "__main__":
    sys.exit(main())
