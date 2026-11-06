#!/usr/bin/env python3
"""Shared wait primitive for the harness (Bean 0182).

Replaces the hand-written polling loops that sessions used to re-type for every wait. Waiting costs zero model
tokens: the caller runs this as one blocking (or background) command and branches on its exit status.

Subcommands and exit codes:

``ci <repo> <pr> [--sha SHA]``
    Wraps ``gh pr checks <pr> --repo <repo> --watch``.
    0 all checks passed, 1 a check failed, 2 timeout, 3 the PR head is not (or is no longer) ``--sha``.

``merged <repo> <pr>``
    Bounded poll of ``gh pr view <pr> --repo <repo> --json state,mergeCommit``.
    0 merged, 1 closed without merging, 2 timeout.

Exit code 4 is reserved for usage and ``gh`` errors that are not a CI result (for example authentication failure).
Every line this script prints is passed through :func:`redact`, so a token echoed by ``gh`` never reaches a log.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from collections.abc import Callable, Sequence

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_TIMEOUT = 2
EXIT_SUPERSEDED = 3
EXIT_ERROR = 4

TOKEN_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"gh[opsur]_[0-9A-Za-z]{16,}"),
    re.compile(r"github_pat_[0-9A-Za-z_]{20,}"),
    re.compile(r"sk-ant-[0-9A-Za-z\-_]{10,}"),
)
REDACTED = "[REDACTED]"

NO_CHECKS_MARKER = "no checks reported"
OUTPUT_TAIL_LINES = 40

Runner = Callable[[Sequence[str], float | None], subprocess.CompletedProcess[str]]


def redact(text: str) -> str:
    """Replace every GitHub or Anthropic token in ``text`` with a fixed marker."""
    for pattern in TOKEN_PATTERNS:
        text = pattern.sub(REDACTED, text)
    return text


def run_gh(args: Sequence[str], timeout: float | None = None) -> subprocess.CompletedProcess[str]:
    """Run ``gh`` with captured text output. Raises ``subprocess.TimeoutExpired`` on timeout."""
    return subprocess.run(["gh", *args], capture_output=True, text=True, timeout=timeout, check=False)


def emit(message: str, stream=None) -> None:
    """Print a redacted message (stdout by default)."""
    print(redact(message), file=stream or sys.stdout, flush=True)


def pr_head(repo: str, pr: int, runner: Runner) -> str | None:
    """Return the PR's current head SHA, or ``None`` when ``gh`` cannot read it."""
    proc = runner(["pr", "view", str(pr), "--repo", repo, "--json", "headRefOid"], 60)
    if proc.returncode != 0:
        emit(f"gh pr view failed: {proc.stderr.strip()}", sys.stderr)
        return None
    try:
        return json.loads(proc.stdout)["headRefOid"]
    except (json.JSONDecodeError, KeyError, TypeError):
        emit("gh pr view returned unparsable output", sys.stderr)
        return None


def wait_ci(
    repo: str,
    pr: int,
    sha: str | None,
    timeout: float,
    interval: int,
    runner: Runner = run_gh,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
) -> int:
    """Block until the PR's checks finish; see the module docstring for exit codes."""
    deadline = clock() + timeout
    if sha is not None:
        head = pr_head(repo, pr, runner)
        if head is None:
            return EXIT_ERROR
        if head != sha:
            emit(f"superseded: PR head is {head}, not {sha}")
            return EXIT_SUPERSEDED

    while True:
        remaining = deadline - clock()
        if remaining <= 0:
            emit(f"timeout: checks for {repo}#{pr} did not finish within {int(timeout)}s")
            return EXIT_TIMEOUT
        args = ["pr", "checks", str(pr), "--repo", repo, "--watch", "--fail-fast", "--interval", str(interval)]
        try:
            proc = runner(args, remaining)
        except subprocess.TimeoutExpired:
            emit(f"timeout: checks for {repo}#{pr} did not finish within {int(timeout)}s")
            return EXIT_TIMEOUT
        output = (proc.stdout or "") + (proc.stderr or "")
        if NO_CHECKS_MARKER in output.lower():
            # A fresh push has not registered its check runs yet: wait and ask again until the deadline.
            sleep(min(interval, max(deadline - clock(), 0)))
            continue
        if output.strip():
            # Watch mode reprints the table on every refresh; the last snapshot is the result.
            emit("\n".join(output.strip().splitlines()[-OUTPUT_TAIL_LINES:]))
        if proc.returncode not in (0, 1) or (proc.returncode == 1 and not (proc.stdout or "").strip()):
            # Exit 1 with no checks table is a gh error (auth, unknown PR), not a failed check.
            emit(f"gh pr checks exited {proc.returncode} without a result", sys.stderr)
            return EXIT_ERROR
        break

    if sha is not None:
        head = pr_head(repo, pr, runner)
        if head != sha:
            emit(f"superseded: PR head moved to {head} while waiting on {sha}")
            return EXIT_SUPERSEDED
    if proc.returncode == 0:
        emit(f"ci passed: {repo}#{pr}")
        return EXIT_OK
    emit(f"ci failed: {repo}#{pr}")
    return EXIT_FAILED


def wait_merged(
    repo: str,
    pr: int,
    timeout: float,
    interval: int,
    runner: Runner = run_gh,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
) -> int:
    """Poll until the PR is merged or closed; see the module docstring for exit codes."""
    deadline = clock() + timeout
    while True:
        proc = runner(["pr", "view", str(pr), "--repo", repo, "--json", "state,mergeCommit"], 60)
        if proc.returncode == 0:
            try:
                data = json.loads(proc.stdout)
            except json.JSONDecodeError:
                data = {}
            state = str(data.get("state", "")).upper()
            if state == "MERGED":
                commit = (data.get("mergeCommit") or {}).get("oid", "")
                emit(f"merged: {repo}#{pr} merge_commit={commit}")
                return EXIT_OK
            if state == "CLOSED":
                emit(f"closed without merge: {repo}#{pr}")
                return EXIT_FAILED
        else:
            # A transient gh failure is not a verdict: keep polling until the deadline.
            emit(f"gh pr view failed (will retry): {proc.stderr.strip()}", sys.stderr)
        remaining = deadline - clock()
        if remaining <= 0:
            emit(f"timeout: {repo}#{pr} still open after {int(timeout)}s")
            return EXIT_TIMEOUT
        sleep(min(interval, remaining))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    ci = sub.add_parser("ci", help="wait for a PR's CI checks (0 pass, 1 fail, 2 timeout, 3 superseded)")
    ci.add_argument("repo", help="OWNER/REPO")
    ci.add_argument("pr", type=int)
    ci.add_argument("--sha", help="only accept a result for this head SHA")
    ci.add_argument("--timeout", type=float, default=3600, help="seconds (default 3600)")
    ci.add_argument("--interval", type=int, default=30, help="refresh interval in seconds (default 30)")

    merged = sub.add_parser("merged", help="wait for a PR to merge (0 merged, 1 closed, 2 timeout)")
    merged.add_argument("repo", help="OWNER/REPO")
    merged.add_argument("pr", type=int)
    merged.add_argument("--timeout", type=float, default=86400, help="seconds (default 86400)")
    merged.add_argument("--interval", type=int, default=60, help="poll interval in seconds (default 60)")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "ci":
        return wait_ci(args.repo, args.pr, args.sha, args.timeout, args.interval)
    return wait_merged(args.repo, args.pr, args.timeout, args.interval)


if __name__ == "__main__":
    sys.exit(main())
