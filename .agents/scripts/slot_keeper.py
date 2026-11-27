#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shlex
import subprocess
import sys
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

FLOW_SCRIPT = "run_holon_flow.py"
FLOW_SCRIPT_PATH = ".agents/skills/holon_flow/scripts/run_holon_flow.py"
OPTIONS_WITH_VALUE = frozenset(
    {"--target-worktree", "--agent", "--model", "--from-stage", "--checkpoint", "--bean", "--overlap-poll-seconds"}
)
DEFAULT_CAP = 8
DEFAULT_AGENT = "antigravity-agent"
DEFAULT_MODEL = "gemini-4-neon"
DEFAULT_TARGET_WORKTREE = "apps/holon-agentic-coder/main"
DEFAULT_REPOS = ("Holon-Agentic-Coder/holon-agentic-coder", "Holon-Agentic-Coder/holon-coherence")
HEARTBEAT_LIMIT_SECONDS = 120
TRIGGER_POLL_SECONDS = 5
CLOSED_BEAN_STATUSES = frozenset({"completed", "scrapped"})
TOUCH_SET_HEADING = "## Touch Set"
STAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


@dataclass(frozen=True)
class Entry:
    bean: str
    intent_path: str
    kind: str = "new"
    checkpoint: str | None = None
    blocked_by: tuple[str, ...] = ()
    target_worktree: str = DEFAULT_TARGET_WORKTREE
    own_pr: int | None = None


@dataclass(frozen=True)
class Holder:
    label: str
    files: frozenset[str]


@dataclass
class PassResult:
    timestamp: str
    live: int
    cap: int
    launched: list[str] = field(default_factory=list)
    held: list[tuple[str, str]] = field(default_factory=list)

    def log_line(self) -> str:
        launched = ",".join(self.launched) or "-"
        held = " ".join(f"{bean}:{reason}" for bean, reason in self.held) or "-"
        return f"{self.timestamp} live={self.live} cap={self.cap} launched={launched} held={held}"


@dataclass
class Environment:
    root: Path
    process_lines: Callable[[], list[str]]
    open_pr_files: Callable[[], dict[int, list[str]]]
    launch: Callable[[list[str], Path, Path], None]
    now: Callable[[], datetime]
    agent: str = DEFAULT_AGENT
    model: str = DEFAULT_MODEL
    cap: int = DEFAULT_CAP


def utc_now() -> datetime:
    return datetime.now(UTC)


def stamp(moment: datetime) -> str:
    return moment.strftime(STAMP_FORMAT)


def parse_queue(text: str) -> list[Entry]:
    data = json.loads(text)
    rows = data["queue"] if isinstance(data, dict) else data
    return [
        Entry(
            bean=str(row["bean"]),
            intent_path=row["intent_path"],
            kind=row.get("kind", "new"),
            checkpoint=row.get("checkpoint"),
            blocked_by=tuple(str(bean) for bean in row.get("blocked_by", [])),
            target_worktree=row.get("target_worktree", DEFAULT_TARGET_WORKTREE),
            own_pr=row.get("own_pr"),
        )
        for row in rows
    ]


def read_queue(path: Path) -> list[Entry]:
    if not path.exists():
        return []
    return parse_queue(path.read_text())


def write_queue(path: Path, entries: Iterable[Entry]) -> None:
    rows = [
        {key: value for key, value in vars(entry).items() if value not in (None, ())}
        | {"blocked_by": list(entry.blocked_by)}
        for entry in entries
    ]
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(rows, indent=2) + "\n")
    temporary.replace(path)


def flow_key(line: str) -> str | None:
    if FLOW_SCRIPT not in line:
        return None
    try:
        tokens = shlex.split(line)
    except ValueError:
        return None
    positional, checkpoint = None, None
    start = next((index for index, token in enumerate(tokens) if token.endswith(FLOW_SCRIPT)), None)
    if start is None:
        return None
    index = start + 1
    while index < len(tokens):
        token = tokens[index]
        if token in OPTIONS_WITH_VALUE:
            if token == "--checkpoint" and index + 1 < len(tokens):
                checkpoint = tokens[index + 1]
            index += 2
            continue
        if not token.startswith("--") and positional is None:
            positional = token
        index += 1
    return positional or checkpoint


def live_flow_keys(lines: Iterable[str]) -> set[str]:
    return {key for key in map(flow_key, lines) if key}


def scope_of(intent_path: Path) -> list[str]:
    return list(json.loads(intent_path.read_text()).get("scope", []))


def slug_of(intent_path: Path) -> str:
    return str(json.loads(intent_path.read_text()).get("slug", intent_path.stem))


def plan_touch_set(root: Path, slug: str) -> set[str]:
    files: set[str] = set()
    for plan in root.glob(f"apps/*/flow-{slug}/plans/*/P-*.md"):
        if plan.name.endswith("_calibration.md"):
            continue
        files |= touch_set_in_plan(plan.read_text())
    return files


def touch_set_in_plan(text: str) -> set[str]:
    section = text.split(TOUCH_SET_HEADING, 1)
    if len(section) < 2:
        return set()
    body = re.split(r"^## ", section[1], maxsplit=1, flags=re.MULTILINE)[0]
    return set(re.findall(r"^\s*[-*]\s+`([^`]+)`", body, flags=re.MULTILINE))


def flow_files(root: Path, intent_path: Path) -> set[str]:
    resolved = intent_path if intent_path.is_absolute() else root / intent_path
    if not resolved.exists():
        return set()
    return set(scope_of(resolved)) | plan_touch_set(root, slug_of(resolved))


def paths_overlap(first: str, second: str) -> bool:
    return first == second or fnmatch.fnmatch(first, second) or fnmatch.fnmatch(second, first)


def first_overlap(files: Iterable[str], holders: Iterable[Holder]) -> tuple[str, str] | None:
    for holder in holders:
        for held in sorted(holder.files):
            for mine in sorted(files):
                if paths_overlap(mine, held):
                    return mine, holder.label
    return None


def intent_failure(root: Path, entry: Entry) -> str | None:
    path = Path(entry.intent_path)
    resolved = path if path.is_absolute() else root / path
    if not resolved.exists():
        return "check:intent-missing"
    try:
        scope = scope_of(resolved)
    except (json.JSONDecodeError, OSError):
        return "check:intent-unreadable"
    if not scope:
        return "check:scope-empty"
    if any(item.endswith("/") for item in scope):
        return "check:scope-has-directory"
    if entry.kind == "resume" and not (entry.checkpoint and (root / entry.checkpoint).exists()):
        return "check:checkpoint-missing"
    return None


def open_blocker(root: Path, entry: Entry) -> str | None:
    for bean in entry.blocked_by:
        status = bean_status(root, bean)
        if status not in CLOSED_BEAN_STATUSES:
            return bean
    return None


def bean_status(root: Path, bean: str) -> str | None:
    for path in sorted((root / ".beans").glob(f"*-{bean}-*.md")):
        match = re.search(r"^status:\s*(\S+)", path.read_text(), flags=re.MULTILINE)
        if match:
            return match.group(1).strip("\"'")
    return None


def flow_argv(environment: Environment, entry: Entry) -> list[str]:
    argv = [
        "uv",
        "run",
        "python",
        FLOW_SCRIPT_PATH,
        entry.intent_path,
        "--target-worktree",
        entry.target_worktree,
        "--agent",
        environment.agent,
        "--model",
        environment.model,
        "--no-wait-on-overlap",
    ]
    if entry.kind == "resume":
        return [*argv, "--checkpoint", str(entry.checkpoint)]
    return [*argv, "--bean", entry.bean]


def flow_log_path(environment: Environment, entry: Entry) -> Path:
    intent = Path(entry.intent_path)
    resolved = intent if intent.is_absolute() else environment.root / intent
    slug = slug_of(resolved) if resolved.exists() else entry.bean
    return environment.root / "todo" / f"flow-{slug}.log"


def parked_holders(environment: Environment, entries: list[Entry], live_keys: set[str]) -> list[tuple[Entry, Holder]]:
    return [
        (entry, Holder(f"parked:{entry.bean}", frozenset(flow_files(environment.root, Path(entry.intent_path)))))
        for entry in entries
        if entry.kind == "resume" and entry.intent_path not in live_keys
    ]


def live_holders(environment: Environment, keys: set[str]) -> list[Holder]:
    return [
        Holder(f"live:{Path(key).stem}", frozenset(flow_files(environment.root, Path(key)))) for key in sorted(keys)
    ]


def pull_request_holders(pr_files: dict[int, list[str]], entry: Entry) -> list[Holder]:
    return [Holder(f"pr:{number}", frozenset(files)) for number, files in pr_files.items() if number != entry.own_pr]


def hold_reason(
    environment: Environment,
    entry: Entry,
    live_keys: set[str],
    launched_count: int,
    reserved: list[Holder],
    pr_holders: list[Holder],
) -> str | None:
    if entry.intent_path in live_keys or entry.checkpoint in live_keys:
        return "already-live"
    if len(live_keys) + launched_count >= environment.cap:
        return "cap"
    blocker = open_blocker(environment.root, entry)
    if blocker:
        return f"blocked_by:{blocker}"
    failure = intent_failure(environment.root, entry)
    if failure:
        return failure
    overlap = first_overlap(flow_files(environment.root, Path(entry.intent_path)), [*reserved, *pr_holders])
    return f"overlap:{overlap[0]}:{overlap[1]}" if overlap else None


def ordered(entries: list[Entry]) -> list[Entry]:
    return sorted(entries, key=lambda entry: entry.kind != "resume")


def run_pass(environment: Environment, entries: list[Entry]) -> tuple[PassResult, list[Entry]]:
    live_keys = live_flow_keys(environment.process_lines())
    result = PassResult(stamp(environment.now()), len(live_keys), environment.cap)
    reserved = live_holders(environment, live_keys)
    parked = parked_holders(environment, entries, live_keys)
    pr_files = environment.open_pr_files()
    remaining: list[Entry] = []
    launched_count = 0
    for entry in ordered(entries):
        own_parked = [holder for held_entry, holder in parked if held_entry is not entry]
        reason = hold_reason(
            environment,
            entry,
            live_keys,
            launched_count,
            [*reserved, *own_parked],
            pull_request_holders(pr_files, entry),
        )
        if reason:
            result.held.append((entry.bean, reason))
            remaining.append(entry)
            continue
        environment.launch(flow_argv(environment, entry), environment.root, flow_log_path(environment, entry))
        launched_count += 1
        result.launched.append(entry.bean)
        reserved.append(
            Holder(f"launched:{entry.bean}", frozenset(flow_files(environment.root, Path(entry.intent_path))))
        )
    return result, remaining


def launch_detached(argv: list[str], cwd: Path, log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("ab") as log:
        subprocess.Popen(
            argv,
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            env=os.environ.copy(),
        )


def list_process_lines() -> list[str]:
    output = subprocess.run(["ps", "-axo", "command"], capture_output=True, text=True, check=False)
    return output.stdout.splitlines()


def fetch_open_pr_files() -> dict[int, list[str]]:
    files: dict[int, list[str]] = {}
    for repo in DEFAULT_REPOS:
        output = subprocess.run(
            ["gh", "pr", "list", "--repo", repo, "--state", "open", "--limit", "100", "--json", "number,files"],
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        if output.returncode != 0:
            raise RuntimeError(f"gh pr list failed for {repo}: {output.stderr.strip()}")
        for pull_request in json.loads(output.stdout or "[]"):
            files[pull_request["number"]] = [item["path"] for item in pull_request.get("files", [])]
    return files


def append_log(path: Path, line: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as log:
        log.write(line + "\n")


def pass_once(environment: Environment, queue_path: Path, log_path: Path, dry_run: bool = False) -> PassResult:
    entries = read_queue(queue_path)
    try:
        result, remaining = run_pass(environment, entries)
    except RuntimeError as failure:
        result = PassResult(stamp(environment.now()), 0, environment.cap, held=[("all", f"check:{failure}")])
        append_log(log_path, result.log_line())
        return result
    if not dry_run:
        write_queue(queue_path, remaining)
    append_log(log_path, result.log_line())
    return result


def last_pass_time(log_path: Path) -> datetime | None:
    if not log_path.exists():
        return None
    lines = [line for line in log_path.read_text().splitlines() if line.strip()]
    if not lines:
        return None
    try:
        return datetime.strptime(lines[-1].split()[0], STAMP_FORMAT).replace(tzinfo=UTC)
    except ValueError:
        return None


def heartbeat_problem(log_path: Path, now: datetime) -> str | None:
    last = last_pass_time(log_path)
    if last is None:
        return "slot keeper has never logged a pass"
    silent = (now - last).total_seconds()
    if silent > HEARTBEAT_LIMIT_SECONDS:
        return f"slot keeper silent for {int(silent)}s (limit {HEARTBEAT_LIMIT_SECONDS}s), last pass {stamp(last)}"
    return None


def check_heartbeat(log_path: Path, alert_path: Path, now: datetime) -> int:
    problem = heartbeat_problem(log_path, now)
    if problem is None:
        return 0
    append_log(alert_path, f"{stamp(now)} {problem}")
    print(problem, file=sys.stderr)
    return 3


def state_snapshot(state_dir: Path) -> dict[str, float]:
    return (
        {path.name: path.stat().st_mtime for path in state_dir.glob("flow_*_state.json")} if state_dir.exists() else {}
    )


def flow_finished_since(previous: dict[str, float], state_dir: Path) -> tuple[bool, dict[str, float]]:
    current = state_snapshot(state_dir)
    return current != previous, current


def loop_forever(
    run_one_pass: Callable[[], object],
    state_dir: Path,
    interval_seconds: int,
    sleep: Callable[[float], None] = time.sleep,
    clock: Callable[[], float] = time.monotonic,
    max_ticks: int | None = None,
) -> None:
    snapshot = state_snapshot(state_dir)
    next_due = clock()
    ticks = 0
    while max_ticks is None or ticks < max_ticks:
        finished, snapshot = flow_finished_since(snapshot, state_dir)
        if finished or clock() >= next_due:
            run_one_pass()
            next_due = clock() + interval_seconds
        ticks += 1
        sleep(TRIGGER_POLL_SECONDS)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="One slot-keeper pass: refill flow slots from the queue file.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--queue", type=Path, default=None)
    parser.add_argument("--log", type=Path, default=None)
    parser.add_argument("--cap", type=int, default=DEFAULT_CAP)
    parser.add_argument("--agent", default=DEFAULT_AGENT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--check-heartbeat", action="store_true")
    parser.add_argument("--loop-seconds", type=int, default=0)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    queue_path = args.queue or root / "todo" / "slot-queue.json"
    log_path = args.log or root / "todo" / "slot-keeper.log"
    if args.check_heartbeat:
        return check_heartbeat(log_path, log_path.with_name("slot-keeper-alerts.log"), utc_now())
    environment = Environment(
        root=root,
        process_lines=list_process_lines,
        open_pr_files=fetch_open_pr_files,
        launch=(lambda *_: None) if args.dry_run else launch_detached,
        now=utc_now,
        agent=args.agent,
        model=args.model,
        cap=args.cap,
    )
    run_one_pass = lambda: pass_once(environment, queue_path, log_path, args.dry_run)  # noqa: E731
    if args.loop_seconds:
        loop_forever(run_one_pass, root / ".subagent", args.loop_seconds)
        return 0
    run_one_pass()
    return 0


if __name__ == "__main__":
    sys.exit(main())
