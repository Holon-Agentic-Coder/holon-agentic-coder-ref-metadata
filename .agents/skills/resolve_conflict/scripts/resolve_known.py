#!/usr/bin/env python3
"""Resolve the append-only conflicts that need no judgement, inside a merge in progress.

Handles ``*.jsonl`` ledgers (union of both sides, interleaved by ``created_at``), the knowledge-base and wisdom
``index.json`` files (union of ``entries`` by ``kb_id`` or ``wb_id``), and a knowledge file that both sides created
with the same content (its id is a content hash) and that differs only in ``created_ts``: the base branch's copy is
kept. Both sides only ever add rows, so nothing is dropped and nothing is de-duplicated. Every other conflicted path
is listed and left untouched for a human-style decision.
"""

import argparse
import json
import subprocess
import sys


def git(*args: str, cwd: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


def stage(n: int, path: str, cwd: str) -> str:
    return git("show", f":{n}:{path}", cwd=cwd)


def merge_jsonl(path: str, cwd: str) -> tuple[int, int]:
    """Main's rows keep their order; the branch's own rows are inserted by ``created_at``."""
    main = [line for line in stage(3, path, cwd).splitlines() if line.strip()]
    ours = [line for line in stage(2, path, cwd).splitlines() if line.strip()]
    remaining: dict[str, int] = {}
    for line in main:
        remaining[line] = remaining.get(line, 0) + 1
    extra = []
    for line in ours:
        if remaining.get(line, 0) > 0:
            remaining[line] -= 1
        else:
            extra.append(line)

    def stamp(line: str) -> str:
        return json.loads(line).get("created_at") or ""

    out = list(main)
    for line in extra:
        i = len(out)
        while i > 0 and stamp(out[i - 1]) > stamp(line):
            i -= 1
        out.insert(i, line)
    with open(f"{cwd}/{path}", "w") as handle:
        handle.write("\n".join(out) + "\n")
    return len(main), len(extra)


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
    args = parser.parse_args()
    conflicted = git("diff", "--name-only", "--diff-filter=U", cwd=args.repo).split()
    left = []
    for path in conflicted:
        if path.endswith(".jsonl"):
            kept, added = merge_jsonl(path, args.repo)
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
