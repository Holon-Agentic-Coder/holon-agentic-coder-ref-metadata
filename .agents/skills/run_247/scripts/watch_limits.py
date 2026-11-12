#!/usr/bin/env python3
"""Watch the flow logs for usage-limit messages and, with --relaunch, resume the stopped flow after the reset.

This runs outside any Claude session, so it keeps working when the session's own tokens are gone. Every
poll it scans the new bytes of ``.subagent/flow_*.log``. A limit message that names a reset time (see
``limit_reset.py``) is announced once through ntfy with its ``resume_at``; a message that names none is announced as
credit exhaustion and left alone. With ``--relaunch`` a flow whose process is not running is relaunched from its
checkpoint once ``resume_at`` has passed, on the same agent and model (claude-agent only, with the OAuth token read
from the secrets file, never printed). Review loops are conversation-driven, so they are announced but not resumed.

Usage:
    watch_limits.py [--interval 60] [--relaunch] [--once] [--dry-run]
    watch_limits.py --self-test
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import shlex
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
from notify_ntfy import notify  # noqa: E402

LOG_GLOB = "flow_*.log"
STATE_FILE = Path.home() / ".holon" / "limit-watch" / "state.json"
LOCK_FILE = STATE_FILE.with_name("watch.lock")
TOKEN_FILE = Path.home() / ".holon" / "secrets" / "claude-oauth-token"
LIMIT_RE = re.compile(
    r"hit your (?:session|weekly|daily|usage)? ?limit|reached your \w+ limit|session limit reached|"
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


def resume_command(path: Path) -> dict[str, str] | None:
    """Parse the flow's own 'resume manually' line from its log: intent, worktree, agent and model."""
    matches = list(RESUME_RE.finditer(re.sub(r"\x1b\[[0-9;]*m", "", path.read_text(errors="replace"))))
    return matches[-1].groupdict() if matches else None


def flow_running(intent: str) -> bool:
    out = subprocess.run(["pgrep", "-f", f"holon.*flow.*{Path(intent).name}"], capture_output=True, text=True)
    return bool(out.stdout.split())


def relaunch(info: dict[str, str], dry_run: bool) -> str:
    if info["agent"] != "claude-agent":
        return "not relaunched: only claude-agent is supported"
    worktree = Path(info["worktree"])
    slug = Path(info["intent"]).stem.split("-")[-1]
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
    cmd += ["--checkpoint", str(checkpoint)] if checkpoint.exists() else []
    if dry_run:
        return "would run: " + shlex.join(cmd)
    token = TOKEN_FILE.read_text().strip()
    env = dict(os.environ, HOLON_TOKEN_REDUCE="0")
    env["HOLON_AGENT_SETTINGS"] = json.dumps({"env": {"HOLON_ECHO_PAD": "x" * 300, "CLAUDE_CODE_OAUTH_TOKEN": token}})
    log = (HARNESS / ".subagent" / f"flow_{slug}.log").open("ab")
    subprocess.Popen(cmd, cwd=HARNESS, env=env, stdout=log, stderr=log, start_new_session=True)
    return "relaunched from checkpoint"


def poll(state: dict, relaunch_on: bool, dry_run: bool, now: datetime | None = None) -> None:
    first_run = not state["offsets"]  # history before the first poll is not announced
    for path in sorted((HARNESS / ".subagent").glob(LOG_GLOB)):
        start = state["offsets"].get(str(path), path.stat().st_size if first_run else 0)
        found, state["offsets"][str(path)] = scan(path, start)
        for message in found:
            info = describe(message, now)
            key = f"{path.name}:{info.get('resume_at')}"
            if key in state["events"]:
                continue
            state["events"][key] = {"resume_at": info.get("resume_at"), "done": info.get("resume_at") is None}
            slug = path.stem.removeprefix("flow_")
            text = (
                f"{slug}: limit hit, resumes {info['resume_at']}"
                if info.get("resume_at")
                else f"{slug}: credit exhausted (no reset named)"
            )
            print(text, flush=True)
            if not dry_run:
                notify("Usage limit", text, priority="high", tags="warning")
    if not relaunch_on:
        return
    stamp = now or datetime.now().astimezone()
    for key, event in state["events"].items():
        if event["done"] or datetime.fromisoformat(event["resume_at"]) > stamp:
            continue
        path = HARNESS / ".subagent" / key.split(":", 1)[0]
        info = resume_command(path)
        if info is None or flow_running(info["intent"]):
            event["done"] = info is not None
            continue
        event["done"] = True
        print(f"{path.name}: {relaunch(info, dry_run)}", flush=True)


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
        }
    print("ok")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--interval", type=int, default=60)
    parser.add_argument("--relaunch", action="store_true", help="resume stopped claude-agent flows after the reset")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="print instead of notifying or relaunching")
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
        poll(state, args.relaunch, args.dry_run)
        if not args.dry_run:
            save_state(state)
        if args.once:
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
