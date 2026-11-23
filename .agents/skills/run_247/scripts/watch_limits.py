#!/usr/bin/env python3
"""Watch the flow logs for usage-limit messages and, with --relaunch, resume the stopped flow after the reset.

This runs outside any Claude session, so it keeps working when the session's own tokens are gone. Every poll it scans
the new bytes of ``.subagent/flow_*.log`` and ``todo/flow-*.log``. A limit message that names a reset time (see
``limit_reset.py``) is logged once with its ``resume_at``. A message that names none is credit exhaustion: the watcher
then probes the account with one tiny ``claude -p`` call every ``--probe-interval`` seconds until it answers, which
is the credit reset. Nothing is sent through ntfy: the only ntfy message is the flow runner's "calibration done". With
``--relaunch`` a flow whose process is not running is relaunched from its checkpoint once ``resume_at`` has passed or
the probe succeeds, on the same agent and model (claude-agent only, with the OAuth token read from the secrets file,
never printed). Review loops are conversation-driven, so they are logged but not resumed.

Usage:
    watch_limits.py [--interval 60] [--probe-interval 600] [--relaunch] [--once] [--dry-run]
    watch_limits.py --self-test
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[4]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(HARNESS / ".agents" / "skills" / "holon_flow" / "scripts"))

from limit_reset import describe  # noqa: E402

# (directory under the harness, glob): the older flow logs and the ones the holon-flow skill writes today.
LOG_SOURCES = ((".subagent", "flow_*.log"), ("todo", "flow-*.log"))
PROBE_PROMPT = "Reply with the single word OK."
PROBE_TIMEOUT_SECONDS = 180
STATE_FILE = Path.home() / ".holon" / "limit-watch" / "state.json"
LOCK_FILE = STATE_FILE.with_name("watch.lock")
TOKEN_FILE = Path.home() / ".holon" / "secrets" / "claude-oauth-token"
LIMIT_RE = re.compile(
    r"hit your (?:session|weekly|daily|usage|5-hour)? ?limit|reached your \w+ limit|session limit reached|"
    r"usage limit reached|5-hour limit reached|"
    r"insufficient_quota|resource_exhausted|rate_limit_exceeded|http 429|status 429|credit balance is too low",
    re.IGNORECASE,
)
RESUME_RE = re.compile(
    r"holon flow (?P<intent>\S+) --target-worktree (?P<worktree>\S+) --agent (?P<agent>\S+) --model (?P<model>\S+)"
)


def load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text())
    except (OSError, ValueError):
        return {"offsets": {}, "events": {}}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=1))


def scan(path: Path, offset: int) -> tuple[list[str], int]:
    """Return the limit lines after ``offset`` (each with the next line, for the reset) and the new offset."""
    size = path.stat().st_size
    if size < offset:  # the log was truncated by a relaunch
        offset = 0
    with path.open("rb") as handle:
        handle.seek(offset)
        text = handle.read().decode("utf-8", "replace")
    lines = text.splitlines()
    found = []
    for index, line in enumerate(lines):
        if LIMIT_RE.search(line):
            found.append(" ".join(lines[index : index + 2]))
    return found, size


def log_paths() -> list[Path]:
    """Every flow log the watcher follows, across the log directories."""
    paths: list[Path] = []
    for directory, pattern in LOG_SOURCES:
        paths.extend(sorted((HARNESS / directory).glob(pattern)))
    return paths


def log_key(path: Path) -> str:
    """The log's path relative to the harness (``todo/flow-x.log``), the stable part of an event key."""
    return path.relative_to(HARNESS).as_posix()


def log_from_key(key: str) -> Path:
    """The log file of an event key; keys written before 2026-11-23 hold a bare name under ``.subagent``."""
    name = key.split(":", 1)[0]
    return HARNESS / name if "/" in name else HARNESS / ".subagent" / name


def resume_command(path: Path) -> dict[str, str] | None:
    """Parse the flow's own 'resume manually' line from its log: intent, worktree, agent and model."""
    text = re.sub(r"\x1b\[[0-9;]*m", "", path.read_text(errors="replace"))
    matches = list(RESUME_RE.finditer(text))
    if not matches:
        return None
    info = matches[-1].groupdict()
    info["allow_overlap"] = "1" if "--allow-overlap" in text else ""
    return info


def intent_slug(intent: str) -> str:
    """The flow slug: the intent JSON's ``slug``, else the last dash-separated word of the file name (legacy)."""
    path = Path(intent) if Path(intent).is_absolute() else HARNESS / intent
    try:
        slug = json.loads(path.read_text()).get("slug")
    except (OSError, ValueError, AttributeError):
        slug = None
    return str(slug) if slug else Path(intent).stem.split("-")[-1]


def flow_running(intent: str) -> bool:
    out = subprocess.run(["pgrep", "-f", f"holon.*flow.*{Path(intent).name}"], capture_output=True, text=True)
    return bool(out.stdout.split())


def agent_env() -> dict[str, str]:
    """Environment for a relaunched flow or a probe: no token reduction, a stall window Fable survives, the token."""
    token = TOKEN_FILE.read_text().strip()
    env = dict(os.environ, HOLON_TOKEN_REDUCE="0")
    env.setdefault("HOLON_TURN_STALL_SECONDS", "600")
    env["HOLON_AGENT_SETTINGS"] = json.dumps({"env": {"HOLON_ECHO_PAD": "x" * 300, "CLAUDE_CODE_OAUTH_TOKEN": token}})
    env["CLAUDE_CODE_OAUTH_TOKEN"] = token
    return env


def credit_available(model: str) -> bool:
    """Probe the account with one tiny ``claude -p`` call: True once it answers without a limit message."""
    claude = shutil.which("claude")
    if claude is None:
        print("probe skipped: no 'claude' on PATH", flush=True)
        return False
    try:
        out = subprocess.run(
            [claude, "-p", PROBE_PROMPT, "--model", model],
            capture_output=True,
            text=True,
            env=agent_env(),
            cwd=str(Path.home()),
            timeout=PROBE_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return out.returncode == 0 and not LIMIT_RE.search(out.stdout + out.stderr)


def relaunch(info: dict[str, str], dry_run: bool, log_path: Path | None = None) -> str:
    if info["agent"] != "claude-agent":
        return "not relaunched: only claude-agent is supported"
    worktree = Path(info["worktree"])
    slug = intent_slug(info["intent"])
    checkpoint = worktree / ".holon" / "flow" / f"checkpoint-{slug}.json"
    cmd = [
        sys.executable,
        str(HARNESS / ".agents/skills/holon_flow/scripts/run_holon_flow.py"),
        info["intent"],
        "--target-worktree",
        str(worktree),
        "--agent",
        info["agent"],
        "--model",
        info["model"],
    ]
    cmd += ["--allow-overlap"] if info.get("allow_overlap") else []
    cmd += ["--checkpoint", str(checkpoint)] if checkpoint.exists() else []
    if dry_run:
        return "would run: " + shlex.join(cmd)
    log = (log_path or HARNESS / "todo" / f"flow-{slug}.log").open("ab")
    subprocess.Popen(cmd, cwd=HARNESS, env=agent_env(), stdout=log, stderr=log, start_new_session=True)
    return "relaunched from checkpoint"


def _due(event: dict, stamp: datetime, probe_interval: int, model: str) -> bool:
    """Whether the event's limit is over: its named reset has passed, or (no reset named) a probe just answered."""
    if event.get("resume_at"):
        return datetime.fromisoformat(event["resume_at"]) <= stamp
    last = event.get("last_probe")
    if last and (stamp - datetime.fromisoformat(last)).total_seconds() < probe_interval:
        return False
    event["last_probe"] = stamp.isoformat()
    return credit_available(model)


def poll(state: dict, relaunch_on: bool, dry_run: bool, now: datetime | None = None, probe_interval: int = 600) -> None:
    first_run = not state["offsets"]  # history before the first poll is not announced
    for path in log_paths():
        # History is never replayed: not on the first poll, and not for the todo/ logs the first time they are watched.
        skip_history = first_run or (path.parent.name == "todo" and not state.get("todo_seen"))
        start = state["offsets"].get(str(path), path.stat().st_size if skip_history else 0)
        found, state["offsets"][str(path)] = scan(path, start)
        for message in found:
            info = describe(message, now)
            key = f"{log_key(path)}:{info.get('resume_at')}"
            if key in state["events"] and (info.get("resume_at") or not state["events"][key]["done"]):
                continue
            # No reset named: credit exhaustion. With --relaunch the watcher probes for the reset; without it, log only.
            state["events"][key] = {
                "resume_at": info.get("resume_at"),
                "done": not relaunch_on and not info.get("resume_at"),
            }
            slug = path.stem.removeprefix("flow_").removeprefix("flow-")
            text = (
                f"{slug}: limit hit, resumes {info['resume_at']}"
                if info.get("resume_at")
                else f"{slug}: credit exhausted (no reset named); probing every {probe_interval} s for the reset"
            )
            print(text, flush=True)
    state["todo_seen"] = True
    if not relaunch_on:
        return
    stamp = now or datetime.now().astimezone()
    for key, event in state["events"].items():
        if event["done"]:
            continue
        path = log_from_key(key)
        info = resume_command(path) if path.exists() else None
        if info is None:
            event["done"] = True
            continue
        if flow_running(info["intent"]):
            event["done"] = True
            continue
        if not _due(event, stamp, probe_interval, info["model"]):
            continue
        event["done"] = True
        if not event.get("resume_at"):
            print(f"{path.name}: credit is back (probe answered)", flush=True)
        print(f"{path.name}: {relaunch(info, dry_run, path)}", flush=True)


def _self_test() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        log = Path(tmp) / "flow_x.log"
        log.write_text("fine\nYou've hit your session limit - resets 5:40pm (Australia/Melbourne)\nmore\n")
        found, size = scan(log, 0)
        assert len(found) == 1 and "resets 5:40pm" in found[0], found
        assert scan(log, size) == ([], size)
        log.write_text("HTTP 429 too many requests\n")
        found, _ = scan(log, size)
        assert len(found) == 1 and describe(found[0])["resume_at"] is None
        log.write_text(
            "holon flow todo/i-x.json --target-worktree /w/flow-x --agent claude-agent "
            "--model claude-sonnet-5-5 --from-stage <stage>\n"
        )
        assert resume_command(log) == {
            "intent": "todo/i-x.json",
            "worktree": "/w/flow-x",
            "agent": "claude-agent",
            "model": "claude-sonnet-5-5",
            "allow_overlap": "",
        }
        intent = Path(tmp) / "intent-0001-some-long-slug.json"
        intent.write_text(json.dumps({"slug": "some-long-slug"}))
        assert intent_slug(str(intent)) == "some-long-slug"
        assert intent_slug("todo/i-x.json") == "x"
        assert log_from_key("todo/flow-a.log:None") == HARNESS / "todo" / "flow-a.log"
        assert log_from_key("flow_a.log:2026-11-23T10:00:00+11:00") == HARNESS / ".subagent" / "flow_a.log"
        named = {"resume_at": "2026-11-23T10:00:00+11:00"}
        assert _due(named, datetime.fromisoformat("2026-11-23T10:01:00+11:00"), 600, "m")
        assert not _due(named, datetime.fromisoformat("2026-11-23T09:59:00+11:00"), 600, "m")
        recent = {"resume_at": None, "last_probe": "2026-11-23T10:00:00+11:00"}
        assert not _due(recent, datetime.fromisoformat("2026-11-23T10:05:00+11:00"), 600, "m")
    print("ok")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--interval", type=int, default=60)
    parser.add_argument(
        "--probe-interval",
        type=int,
        default=600,
        help="seconds between account probes while credit is exhausted with no reset named",
    )
    parser.add_argument("--relaunch", action="store_true", help="resume stopped claude-agent flows after the reset")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="print instead of relaunching")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        return 0
    if not (args.once or args.dry_run):  # one long-running watcher at a time; a second one exits at once
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        lock = LOCK_FILE.open("w")
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return 0
    state = load_state()
    while True:
        poll(state, args.relaunch, args.dry_run, probe_interval=args.probe_interval)
        if not args.dry_run:
            save_state(state)
        if args.once:
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
