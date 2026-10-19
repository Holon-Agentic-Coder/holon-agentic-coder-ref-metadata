#!/usr/bin/env python3
"""Pre-commit credential leakage and ephemeral scratch file detector (Bean 0110).

Scans staged git files (or explicit file paths) for:
1. Disallowed ephemeral scratch paths (tmp/*, *.tmp, *.log, .index/*).
2. Secret credential patterns (Google AI API keys AIza..., GitHub PATs ghp_/github_pat_/gho_,
   OpenAI keys sk-..., Anthropic keys sk-ant-...).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from fnmatch import fnmatch
from pathlib import Path

SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("Google AI API Key", re.compile(r"AIza[0-9A-Za-z\-_]{30,40}")),
    ("GitHub Personal Access Token", re.compile(r"(?:ghp|gho)_[0-9A-Za-z]{30,50}")),
    ("GitHub Fine-Grained PAT", re.compile(r"github_pat_[0-9A-Za-z_]{40,100}")),
    ("Anthropic API Key", re.compile(r"sk-ant-[0-9A-Za-z\-_]{20,}")),
    ("OpenAI API Key", re.compile(r"sk-(?:proj-)?[0-9A-Za-z\-_]{24,}")),
]

DISALLOWED_PATH_GLOBS: tuple[str, ...] = (
    "tmp/*",
    "*/tmp/*",
    "*.tmp",
    "*.log",
    ".index/*",
    "*/.index/*",
)


def get_staged_files(repo_root: Path | None = None) -> list[str]:
    """Return relative file paths currently staged in git."""
    cmd = ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"]
    proc = subprocess.run(
        cmd,
        cwd=str(repo_root) if repo_root else None,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def is_disallowed_scratch_path(rel_path: str) -> str | None:
    """Return matching disallowed glob pattern if rel_path is an ephemeral scratch file."""
    normalized = rel_path.replace("\\", "/").removeprefix("./")
    for pattern in DISALLOWED_PATH_GLOBS:
        if fnmatch(normalized, pattern):
            return pattern
    return None


def scan_file_for_secrets(file_path: Path, display_path: str | None = None) -> list[str]:
    """Scan a single file line-by-line for credential patterns."""
    findings: list[str] = []
    label = display_path or str(file_path)
    if not file_path.exists() or not file_path.is_file():
        return findings

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return findings

    for line_no, line in enumerate(content.splitlines(), start=1):
        for secret_name, regex in SECRET_PATTERNS:
            if regex.search(line):
                findings.append(f"{label}:{line_no}: detected {secret_name}")
    return findings


def audit_paths(paths: list[str], repo_root: Path | None = None) -> tuple[list[str], list[str]]:
    """Audit a list of relative or absolute paths for disallowed scratch files and secrets.

    Returns:
        Tuple of (path_violations, secret_violations).
    """
    base = repo_root or Path.cwd()
    path_violations: list[str] = []
    secret_violations: list[str] = []

    for rel in paths:
        matched_glob = is_disallowed_scratch_path(rel)
        if matched_glob:
            path_violations.append(f"{rel}: disallowed ephemeral scratch path (matches '{matched_glob}')")

        full_path = Path(rel) if Path(rel).is_absolute() else (base / rel)
        secret_violations.extend(scan_file_for_secrets(full_path, display_path=rel))

    return path_violations, secret_violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scan staged files for credential leakage and disallowed scratch artifacts."
    )
    parser.add_argument(
        "--files",
        nargs="*",
        help="Explicit file paths to scan instead of git staged files.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repository root directory.",
    )
    args = parser.parse_args(argv)

    target_files = args.files if args.files is not None else get_staged_files(args.repo_root)
    if not target_files:
        return 0

    path_violations, secret_violations = audit_paths(target_files, repo_root=args.repo_root)
    if not path_violations and not secret_violations:
        return 0

    print("❌ Pre-commit security and hygiene check failed:", file=sys.stderr)
    for violation in path_violations:
        print(f"  [SCRATCH FILE] {violation}", file=sys.stderr)
    for violation in secret_violations:
        print(f"  [CREDENTIAL]   {violation}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
