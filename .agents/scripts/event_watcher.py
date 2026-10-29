#!/usr/bin/env python3
"""Persistent GitHub event watcher for the harness (Bean 0182).

The watcher only detects and records; it never acts. It polls the open pull requests of the managed repositories with
conditional requests (``If-None-Match`` / ETag, which GitHub does not count against the rate limit when nothing
changed) and appends one JSON line per change to an append-only event log, ``.subagent/events.jsonl`` by default.

Event types: ``head_moved``, ``ci_pending``, ``ci_passed``, ``ci_failed``, ``review_posted``, ``pr_merged``,
``pr_closed``. Every event carries ``seq`` (monotonic, survives rotation), ``id`` (a stable dedupe key), ``type``,
``repo``, ``pr``, ``sha``, ``time`` and ``detail``.

Subcommands:

``watch``    poll forever (or ``--max-cycles N``) and append events. The first successful read of each repository is a
             silent baseline, so starting the watcher never floods the log with history, and a failed first read
             (auth, network) does not consume the baseline.
``consume``  print the events after the consumer's cursor and advance it (``--peek`` leaves the cursor alone), so a
             session that starts later processes the backlog exactly once.

Rules mapping events to harness actions live in ``.agents/watcher/README.md``. Every byte this script writes goes
through ``wait_for.redact``.
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import subprocess
import sys
import time
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wait_for import redact  # noqa: E402

DEFAULT_REPOS: tuple[str, ...] = (
    "Holon-Agentic-Coder/holon-agentic-coder",
    "Holon-Agentic-Coder/holon-coherence",
)


def default_events_dir(script: Path) -> Path:
    """The harness ``.subagent/`` when run from ``.agents/scripts/``; ``./.subagent`` for a shallow install path."""
    parents = script.resolve().parents
    return parents[2] / ".subagent" if len(parents) > 2 else Path(".subagent")


DEFAULT_DIR = default_events_dir(Path(__file__))
DEFAULT_MAX_BYTES = 5 * 1024 * 1024
DEFAULT_KEEP = 5

FAILED_CONCLUSIONS = frozenset({"failure", "cancelled", "timed_out", "action_required", "startup_failure", "stale"})

GhRunner = Callable[[Sequence[str]], subprocess.CompletedProcess[str]]


def now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_gh(args: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["gh", *args], capture_output=True, text=True, timeout=120, check=False)


# --------------------------------------------------------------------------------------------------------------------
# Conditional GitHub client
# --------------------------------------------------------------------------------------------------------------------


@dataclass
class Response:
    status: int
    etag: str | None
    body: object


class GitHubError(RuntimeError):
    """A request that returned neither 2xx nor 304."""


def parse_include_output(text: str) -> tuple[int, dict[str, str], str]:
    """Split ``gh api -i`` output into (status, lower-cased headers, body)."""
    normalised = text.replace("\r\n", "\n")
    head, _, body = normalised.partition("\n\n")
    lines = head.split("\n")
    status = 0
    if lines and lines[0].startswith("HTTP/"):
        parts = lines[0].split()
        if len(parts) >= 2 and parts[1].isdigit():
            status = int(parts[1])
    headers: dict[str, str] = {}
    for line in lines[1:]:
        name, sep, value = line.partition(":")
        if sep:
            headers[name.strip().lower()] = value.strip()
    return status, headers, body


class GitHubClient:
    """``gh api`` wrapper that remembers ETags per path and sends ``If-None-Match``."""

    def __init__(self, etags: dict[str, str], runner: GhRunner = run_gh) -> None:
        self.etags = etags
        self.runner = runner

    def get(self, path: str, conditional: bool = True) -> Response:
        args = ["api", "-i", path]
        etag = self.etags.get(path) if conditional else None
        if etag:
            args += ["-H", f"If-None-Match: {etag}"]
        proc = self.runner(args)
        status, headers, body = parse_include_output(proc.stdout or "")
        if status == 304:
            return Response(304, etag, None)
        if not 200 <= status < 300:
            detail = redact((proc.stderr or "").strip() or f"HTTP {status}")
            raise GitHubError(f"GET {path} failed: {detail}")
        new_etag = headers.get("etag")
        if new_etag and conditional:
            self.etags[path] = new_etag
        try:
            parsed = json.loads(body) if body.strip() else None
        except json.JSONDecodeError as exc:
            raise GitHubError(f"GET {path} returned invalid JSON") from exc
        return Response(status, new_etag, parsed)


# --------------------------------------------------------------------------------------------------------------------
# Event log (append-only, size-rotated) and state
# --------------------------------------------------------------------------------------------------------------------


def rotated_paths(log_path: Path, keep: int) -> list[Path]:
    """Oldest first: ``events.jsonl.<keep>`` ... ``events.jsonl.1``, then ``events.jsonl``."""
    return [log_path.with_name(f"{log_path.name}.{i}") for i in range(keep, 0, -1)] + [log_path]


def rotate_if_needed(log_path: Path, max_bytes: int, keep: int) -> None:
    if not log_path.exists() or log_path.stat().st_size < max_bytes:
        return
    oldest = log_path.with_name(f"{log_path.name}.{keep}")
    if oldest.exists():
        oldest.unlink()
    for i in range(keep - 1, 0, -1):
        src = log_path.with_name(f"{log_path.name}.{i}")
        if src.exists():
            src.rename(log_path.with_name(f"{log_path.name}.{i + 1}"))
    log_path.rename(log_path.with_name(f"{log_path.name}.1"))


def read_events(log_path: Path, keep: int = DEFAULT_KEEP) -> Iterator[dict]:
    for path in rotated_paths(log_path, keep):
        if not path.exists():
            continue
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue  # a torn final line from a killed writer is skipped, not fatal


def load_json(path: Path, default: dict) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        print(redact(f"warning: {path} is not valid JSON; starting from an empty state"), file=sys.stderr)
        return default


def write_json_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.partial")
    tmp.write_text(redact(json.dumps(data, indent=2, sort_keys=True)) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def event_id(event_type: str, repo: str, pr: int, sha: str | None, key: str) -> str:
    raw = f"{event_type}|{repo}|{pr}|{sha}|{key}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


# --------------------------------------------------------------------------------------------------------------------
# Watcher
# --------------------------------------------------------------------------------------------------------------------


def check_runs_path(repo: str, sha: str | None) -> str:
    return f"repos/{repo}/commits/{sha}/check-runs?per_page=100"


def summarise_check_runs(body: object) -> tuple[str, list[str]]:
    """Aggregate check runs to ``ci_passed`` / ``ci_failed`` / ``ci_pending`` plus the failing job names."""
    runs = body.get("check_runs", []) if isinstance(body, dict) else []
    if not runs:
        return "ci_pending", []
    failing = sorted(r.get("name", "?") for r in runs if (r.get("conclusion") or "") in FAILED_CONCLUSIONS)
    if failing:
        return "ci_failed", failing
    if any(r.get("status") != "completed" for r in runs):
        return "ci_pending", []
    return "ci_passed", []


class Watcher:
    def __init__(
        self,
        repos: Sequence[str],
        log_path: Path,
        state_path: Path,
        runner: GhRunner = run_gh,
        max_bytes: int = DEFAULT_MAX_BYTES,
        keep: int = DEFAULT_KEEP,
        clock: Callable[[], str] = now_iso,
    ) -> None:
        self.repos = list(repos)
        self.log_path = log_path
        self.state_path = state_path
        self.max_bytes = max_bytes
        self.keep = keep
        self.clock = clock
        self.state = load_json(state_path, {})
        self.state.setdefault("baselined", [])
        self.state.setdefault("next_seq", 1)
        self.state.setdefault("etags", {})
        self.state.setdefault("prs", {})
        self.client = GitHubClient(self.state["etags"], runner)
        self.emitted: list[dict] = []

    # -- output ------------------------------------------------------------------------------------------------------

    def emit(self, event_type: str, repo: str, pr: int, sha: str | None, detail: dict, key: str = "") -> None:
        if repo not in self.state["baselined"]:
            return  # first successful read of this repository records state silently
        event = {
            "seq": self.state["next_seq"],
            "id": event_id(event_type, repo, pr, sha, key),
            "type": event_type,
            "repo": repo,
            "pr": pr,
            "sha": sha,
            "time": self.clock(),
            "detail": detail,
        }
        self.state["next_seq"] += 1
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        rotate_if_needed(self.log_path, self.max_bytes, self.keep)
        line = redact(json.dumps(event, sort_keys=True)) + "\n"
        with self.log_path.open("a", encoding="utf-8") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
        self.emitted.append(event)

    # -- polling -----------------------------------------------------------------------------------------------------

    def poll_once(self) -> list[dict]:
        """Run one cycle over every repository and persist state. Returns the events emitted."""
        self.emitted = []
        for repo in self.repos:
            try:
                self.poll_repo(repo)
            except GitHubError as exc:
                print(redact(f"{self.clock()} {repo}: {exc}"), file=sys.stderr, flush=True)
        write_json_atomic(self.state_path, self.state)
        return self.emitted

    def poll_repo(self, repo: str) -> None:
        known: dict[str, dict] = self.state["prs"].setdefault(repo, {})
        listing = self.client.get(f"repos/{repo}/pulls?state=open&per_page=100")
        if listing.status != 304 and isinstance(listing.body, list):
            open_now = {str(pr["number"]): pr["head"]["sha"] for pr in listing.body}
            for number in sorted(set(known) - set(open_now), key=int):
                self.handle_gone(repo, int(number), known.pop(number))
            for number, sha in open_now.items():
                entry = known.get(number)
                if entry is None:
                    known[number] = {"sha": sha, "ci": None, "reviews": []}
                    self.emit("head_moved", repo, int(number), sha, {"from": None, "to": sha}, key="opened")
                elif entry["sha"] != sha:
                    previous = entry["sha"]
                    self.state["etags"].pop(check_runs_path(repo, previous), None)
                    entry.update({"sha": sha, "ci": None})
                    self.emit("head_moved", repo, int(number), sha, {"from": previous, "to": sha})
        for number, entry in known.items():
            try:
                self.poll_ci(repo, int(number), entry)
                self.poll_reviews(repo, int(number), entry)
            except GitHubError as exc:
                # One unreadable PR must not hide the others; it is retried next cycle.
                print(redact(f"{self.clock()} {repo}#{number}: {exc}"), file=sys.stderr, flush=True)
        if repo not in self.state["baselined"]:
            self.state["baselined"].append(repo)

    def handle_gone(self, repo: str, pr: int, entry: dict) -> None:
        response = self.client.get(f"repos/{repo}/pulls/{pr}", conditional=False)
        body = response.body if isinstance(response.body, dict) else {}
        sha = (body.get("head") or {}).get("sha") or entry.get("sha")
        if body.get("merged_at"):
            detail = {"merge_commit": body.get("merge_commit_sha"), "merged_at": body.get("merged_at")}
            self.emit("pr_merged", repo, pr, sha, detail)
        else:
            self.emit("pr_closed", repo, pr, sha, {"closed_at": body.get("closed_at")})
        stale = [p for p in self.state["etags"] if p.startswith(f"repos/{repo}/pulls/{pr}/")]
        stale.append(check_runs_path(repo, entry.get("sha")))
        for path in stale:
            self.state["etags"].pop(path, None)

    def poll_ci(self, repo: str, pr: int, entry: dict) -> None:
        sha = entry["sha"]
        response = self.client.get(check_runs_path(repo, sha))
        if response.status == 304:
            return
        state, failing = summarise_check_runs(response.body)
        if entry.get("ci") == state:
            return
        entry["ci"] = state
        detail = {"failing_jobs": failing} if failing else {}
        self.emit(state, repo, pr, sha, detail)

    def poll_reviews(self, repo: str, pr: int, entry: dict) -> None:
        response = self.client.get(f"repos/{repo}/pulls/{pr}/reviews?per_page=100")
        if response.status == 304 or not isinstance(response.body, list):
            return
        seen = set(entry.get("reviews", []))
        for review in response.body:
            review_id = review.get("id")
            if review_id is None or review_id in seen:
                continue
            seen.add(review_id)
            detail = {
                "review_id": review_id,
                "state": review.get("state"),
                "user": (review.get("user") or {}).get("login"),
                "url": review.get("html_url"),
            }
            self.emit("review_posted", repo, pr, review.get("commit_id"), detail, key=str(review_id))
        entry["reviews"] = sorted(seen)


# --------------------------------------------------------------------------------------------------------------------
# Consumer
# --------------------------------------------------------------------------------------------------------------------


def consume(log_path: Path, cursor_path: Path, peek: bool = False, keep: int = DEFAULT_KEEP) -> list[dict]:
    """Return events with ``seq`` above the cursor, oldest first, and advance the cursor unless ``peek``."""
    cursor = load_json(cursor_path, {"seq": 0}).get("seq", 0)
    events = [e for e in read_events(log_path, keep) if isinstance(e.get("seq"), int) and e["seq"] > cursor]
    events.sort(key=lambda e: e["seq"])
    if events and not peek:
        write_json_atomic(cursor_path, {"seq": events[-1]["seq"], "updated": now_iso()})
    return events


# --------------------------------------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dir", type=Path, default=Path(os.environ.get("HOLON_EVENTS_DIR", DEFAULT_DIR)))
    sub = parser.add_subparsers(dest="command", required=True)

    watch = sub.add_parser("watch", help="poll GitHub and append events")
    watch.add_argument("--repo", action="append", dest="repos", help="OWNER/REPO (repeatable; default: managed repos)")
    watch.add_argument("--interval", type=float, default=60.0, help="seconds between cycles (default 60)")
    watch.add_argument("--max-cycles", type=int, default=0, help="stop after N cycles (0 = forever)")
    watch.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES, help="rotate the log above this size")
    watch.add_argument("--keep", type=int, default=DEFAULT_KEEP, help="rotated generations to keep")

    cons = sub.add_parser("consume", help="print events after the cursor and advance it")
    cons.add_argument("--cursor", type=Path, help="cursor file (default <dir>/events.cursor.json)")
    cons.add_argument("--peek", action="store_true", help="do not advance the cursor")
    cons.add_argument("--keep", type=int, default=DEFAULT_KEEP)
    return parser


def main(
    argv: Sequence[str] | None = None, runner: GhRunner = run_gh, sleep: Callable[[float], None] = time.sleep
) -> int:
    args = build_parser().parse_args(argv)
    log_path = args.dir / "events.jsonl"
    if args.command == "consume":
        cursor = args.cursor or args.dir / "events.cursor.json"
        for event in consume(log_path, cursor, peek=args.peek, keep=args.keep):
            print(json.dumps(event, sort_keys=True))
        return 0

    watcher = Watcher(
        args.repos or DEFAULT_REPOS,
        log_path,
        args.dir / "events_watcher_state.json",
        runner=runner,
        max_bytes=args.max_bytes,
        keep=args.keep,
    )
    cycles = 0
    with contextlib.suppress(KeyboardInterrupt):
        while True:
            watcher.poll_once()
            cycles += 1
            if args.max_cycles and cycles >= args.max_cycles:
                break
            sleep(args.interval)
    return 0


if __name__ == "__main__":
    sys.exit(main())
