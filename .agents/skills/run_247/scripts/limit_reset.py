#!/usr/bin/env python3
"""Work out when a coding-agent usage limit (Claude, Antigravity, Codex, ...) resets from the message that announced it.

The limit message names the reset in one of a few shapes, for a session window, a daily window or a weekly window:

    resets 5:40pm (Australia/Melbourne)
    resets Nov 14 at 9am (Australia/Melbourne)
    resets Thursday 9am (Australia/Melbourne)
    resets in 3 hours 20 minutes

Usage:
    limit_reset.py "You've hit your session limit - resets 5:40pm (Australia/Melbourne)"
    limit_reset.py --self-test

Prints JSON: reset, resume (reset + 1 min), seconds until then, and the window kind. Kind is the message's own label
("weekly limit"), else the label of --runner's single entry in resets.json (loaded at startup) when that entry's reset matches
this one, else "unknown". Each labelled message replaces the runner's entry. Exits 1 with {"resume_at": null} when no reset is named
(credit exhaustion).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta, tzinfo
from zoneinfo import ZoneInfo

RESUME_DELAY = timedelta(minutes=1)
REGISTRY_PATH = Path(__file__).resolve().parent.parent / "resets.json"
MATCH_TOLERANCE = timedelta(minutes=1)
_NOT_LABELS = {"usage", "rate", "the", "your", "a", "this", "any", "no", "token", "credit"}
MONTHS = {
    name: number
    for number, names in enumerate(
        ["jan january", "feb february", "mar march", "apr april", "may", "jun june", "jul july", "aug august",
         "sep sept september", "oct october", "nov november", "dec december"],
        start=1,
    )
    for name in names.split()
}
WEEKDAYS = {
    name: number
    for number, names in enumerate(
        ["mon monday", "tue tues tuesday", "wed wednesday", "thu thur thurs thursday", "fri friday", "sat saturday",
         "sun sunday"]
    )
    for name in names.split()
}
_TIME = r"(?P<hour>\d{1,2})(?::(?P<minute>\d{2}))?\s*(?P<ampm>am|pm)"
_ZONE = r"(?:\s*\((?P<tz>[^)]+)\))?"


def _zone(name: str | None) -> tzinfo | None:
    try:
        return ZoneInfo(name.strip()) if name else None
    except Exception:  # noqa: BLE001 - an unknown zone name falls back to local time
        return None


def _clock(match: re.Match[str]) -> tuple[int, int]:
    hour = int(match.group("hour")) % 12 + (12 if match.group("ampm").lower() == "pm" else 0)
    return hour, int(match.group("minute") or 0)


def parse_reset(message: str, now: datetime | None = None) -> datetime | None:
    """Return the reset named in ``message`` (timezone-aware when the message names a zone), or None."""
    found = re.search(r"resets?\s+(?:at\s+)?(?P<rest>[^\n]*)", message, re.I)
    if not found:
        return None
    rest = found.group("rest").strip()

    relative = re.match(r"in\s+(?:(?P<h>\d+)\s*h(?:ours?|rs?)?)?\s*(?:and\s*)?(?:(?P<m>\d+)\s*m(?:in(?:ute)?s?)?)?", rest, re.I)
    if relative and (relative.group("h") or relative.group("m")):
        base = now or datetime.now().astimezone()
        return base + timedelta(hours=int(relative.group("h") or 0), minutes=int(relative.group("m") or 0))

    zone_match = re.search(r"\((?P<tz>[^)]+)\)", rest)
    zone = _zone(zone_match.group("tz")) if zone_match else None
    current = now.astimezone(zone) if now and zone else (now or datetime.now(zone) if zone else datetime.now().astimezone())
    if now and not zone:
        current = now
    time_match = re.search(_TIME, rest, re.I)
    hour, minute = _clock(time_match) if time_match else (0, 0)

    month_day = re.search(r"(?P<month>[A-Za-z]{3,9})\.?\s+(?P<day>\d{1,2})\b", rest)
    if month_day and month_day.group("month").lower() in MONTHS:
        month, day = MONTHS[month_day.group("month").lower()], int(month_day.group("day"))
        reset = current.replace(month=month, day=day, hour=hour, minute=minute, second=0, microsecond=0)
        if reset <= current:
            reset = reset.replace(year=reset.year + 1)
        return reset

    weekday = next((WEEKDAYS[w.lower()] for w in re.findall(r"[A-Za-z]+", rest) if w.lower() in WEEKDAYS), None)
    if weekday is not None:
        ahead = (weekday - current.weekday()) % 7
        reset = (current + timedelta(days=ahead)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        if reset <= current:
            reset += timedelta(days=7)
        return reset

    if time_match:
        reset = current.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if reset <= current:
            reset += timedelta(days=1)
        return reset
    return None


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, dict[str, str]]:
    """Load each runner's last-seen reset ({runner: {label, reset_at}}); empty when absent or unreadable."""
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def save_registry(registry: dict[str, dict[str, str]], path: Path = REGISTRY_PATH) -> None:
    path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n")


def parse_label(message: str) -> str | None:
    """Return the window label the message names ("session", "weekly", "5-hour", ...), or None."""
    for found in re.finditer(r"\b(?P<label>[A-Za-z0-9-]+)\s+(?:usage\s+)?limit\b", message, re.I):
        label = found.group("label").lower()
        if label not in _NOT_LABELS:
            return label
    return None


def classify(label: str | None, reset: datetime, entry: dict[str, str] | None) -> tuple[str, str]:
    """Return (kind, source): the message's own label, else the runner's entry label when its reset is this reset."""
    if label:
        return label, "message"
    try:
        if entry and abs(datetime.fromisoformat(entry["reset_at"]) - reset) <= MATCH_TOLERANCE:
            return entry["label"], "registry"
    except (KeyError, ValueError, TypeError):
        pass
    return "unknown", "none"


def observe(registry: dict[str, dict[str, str]], runner: str, label: str, reset: datetime) -> dict[str, dict[str, str]]:
    """Replace the runner's single entry with the labelled reset just seen."""
    return {**registry, runner: {"label": label, "reset_at": reset.isoformat()}}


def describe(
    message: str,
    now: datetime | None = None,
    runner: str | None = None,
    registry: dict[str, dict[str, int]] | None = None,
) -> dict[str, object]:
    reset = parse_reset(message, now)
    if reset is None:
        return {"resume_at": None, "reason": "the message names no reset time (credit exhaustion): step down a model tier"}
    clock = now.astimezone(reset.tzinfo) if now and reset.tzinfo else (now or datetime.now(reset.tzinfo))
    resume = reset + RESUME_DELAY
    seconds = max(0.0, (resume - clock).total_seconds())
    label = parse_label(message)
    kind, source = classify(label, reset, (registry or {}).get(runner or ""))
    return {
        "reset_at": reset.isoformat(),
        "resume_at": resume.isoformat(),
        "seconds_until_resume": int(seconds),
        "kind": kind,
        "kind_source": source,
        "label": label,
    }


def _self_test() -> None:
    zone = ZoneInfo("Australia/Melbourne")
    now = datetime(2026, 11, 12, 8, 0, tzinfo=zone)  # a Thursday
    registry = {"claude": {"label": "weekly", "reset_at": "2026-11-17T06:00:00+11:00"}}
    cases = [
        ("resets 9:20am (Australia/Melbourne)", "2026-11-12T09:20", "unknown", "none"),
        ("resets Nov 17 at 6am (Australia/Melbourne)", "2026-11-17T06:00", "weekly", "registry"),
        ("resets Monday 6am (Australia/Melbourne)", "2026-11-16T06:00", "unknown", "none"),
        ("You've hit your daily limit - resets 9:05am (Australia/Melbourne)", "2026-11-12T09:05", "daily", "message"),
    ]
    for message, expected, kind, source in cases:
        out = describe(message, now, "claude", registry)
        assert str(out["reset_at"]).startswith(expected), (message, out)
        assert (out["kind"], out["kind_source"]) == (kind, source), (message, out)
    # Another runner, or none, has no learned resets: unknown rather than a guess.
    assert describe("resets 9:20am (Australia/Melbourne)", now, "codex", registry)["kind"] == "unknown"
    assert parse_label("You've reached your Fable limit") == "fable"
    assert parse_label("Rate limit reached, resets 5pm") is None
    reset = datetime(2026, 11, 17, 6, 0, tzinfo=zone)
    assert observe({}, "codex", "weekly", reset) == {"codex": {"label": "weekly", "reset_at": reset.isoformat()}}
    assert observe(registry, "claude", "session", reset)["claude"]["label"] == "session"
    relative = describe("resets in 3 hours 20 minutes", now)
    assert relative["seconds_until_resume"] == 3 * 3600 + 20 * 60 + 60, relative
    assert describe("You've reached your Fable limit. Run /usage-credits to continue", now)["resume_at"] is None
    print("limit_reset self-test passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("message", nargs="?", help="the usage-limit message text")
    parser.add_argument("--runner", help="runner name (claude, codex, antigravity, ...) whose last-seen resets to use")
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH, help="last-seen-resets file (default: resets.json)")
    parser.add_argument("--no-record", action="store_true", help="do not update the registry from this message")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        _self_test()
        return 0
    if not args.message:
        parser.error("give the limit message, or --self-test")
    registry = load_registry(args.registry)
    out = describe(args.message, runner=args.runner, registry=registry)
    if args.runner and out.get("label") and out["resume_at"] and not args.no_record:
        save_registry(observe(registry, args.runner, str(out["label"]), datetime.fromisoformat(str(out["reset_at"]))), args.registry)
    print(json.dumps(out))
    return 0 if out["resume_at"] else 1


if __name__ == "__main__":
    sys.exit(main())
