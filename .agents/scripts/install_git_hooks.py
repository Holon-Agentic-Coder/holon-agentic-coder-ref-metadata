#!/usr/bin/env python3
from __future__ import annotations

import shutil
import stat
import subprocess
import sys
from pathlib import Path

SOURCE_DIRECTORY = Path(__file__).resolve().parents[1] / "hooks"


def git_hooks_directory(repository: Path) -> Path:
    resolved = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "--path-format=absolute", "--git-path", "hooks"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return Path(resolved)


def install_hooks(source_directory: Path, target_directory: Path) -> list[str]:
    target_directory.mkdir(parents=True, exist_ok=True)
    changed = []
    for source in sorted(source_directory.iterdir()):
        if not source.is_file():
            continue
        target = target_directory / source.name
        if not target.is_file() or target.read_bytes() != source.read_bytes():
            shutil.copyfile(source, target)
            changed.append(source.name)
        target.chmod(target.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return changed


def main() -> int:
    repository = SOURCE_DIRECTORY.parents[1]
    target_directory = git_hooks_directory(repository)
    changed = install_hooks(SOURCE_DIRECTORY, target_directory)
    print(f"installed: {', '.join(changed)}" if changed else "hooks already up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
