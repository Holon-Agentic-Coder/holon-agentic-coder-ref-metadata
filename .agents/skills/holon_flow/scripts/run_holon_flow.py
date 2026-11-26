#!/usr/bin/env python3
"""run_holon_flow.py

Automated orchestrator script to execute and monitor the 5-stage Holon flow
(Intent -> Plan -> Execute -> Review Loop -> Calibration) across managed target
repositories (holon-agentic-coder and holon-coherence) from a subagent or shell.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from flow_env import AuthRouteMissing, build_flow_env  # noqa: E402

# Terminal formatting
COLOR_BOLD = "\033[1m"
COLOR_GREEN = "\033[1;32m"
COLOR_RED = "\033[1;31m"
COLOR_YELLOW = "\033[1;33m"
COLOR_CYAN = "\033[1;36m"
COLOR_RESET = "\033[0m"

# Model fallback ladders (.agents/holon-flow.md)
FALLBACK_LADDER_CLAUDE = [
    "claude-fable-5-2",
    "claude-opus-5-5",
    "claude-sonnet-4-6",
    "claude-haiku-4-5",
]

FALLBACK_LADDER_ANTIGRAVITY = [
    "gemini-4-neon",
    "gemini-4-argon",
    "gemini-4-hydrogen",
    "gemini-3.8-flash",
]

# How often an overlap wait re-checks the overlapping pull requests (or, for a local flow with none, re-runs admission).
OVERLAP_POLL_SECONDS = 60
OVERLAP_REFUSAL = "Stage 3 refused: the touch set overlaps"

QUOTA_ERROR_PATTERNS = [
    "hit your session limit",
    "session limit reached",
    "insufficient_quota",
    "resource_exhausted",
    "quota exceeded",
    "quota exhausted",
    "quota_exhausted",
    "usage limit reached",
    "hit your usage limit",
    "hit your limit",
    "rate_limit_exceeded",
    "too many requests",
    "http 429",
    "status 429",
    "credit balance is too low",
    "monthly spend limit",
    "spend limit",
]


def enable_line_buffering() -> None:
    """Make stdout and stderr line-buffered so each wrapper line reaches a redirected log as it is printed."""
    for stream in (sys.stdout, sys.stderr):
        with contextlib.suppress(AttributeError, ValueError, OSError):
            stream.reconfigure(line_buffering=True)  # type: ignore[union-attr]


def log_info(msg: str) -> None:
    print(f"{COLOR_BOLD}INFO:{COLOR_RESET} {msg}")


def log_success(msg: str) -> None:
    print(f"{COLOR_GREEN}✅ {msg}{COLOR_RESET}")


def log_warn(msg: str) -> None:
    print(f"{COLOR_YELLOW}⚠️  {msg}{COLOR_RESET}")


def log_error(msg: str) -> None:
    print(f"{COLOR_RED}❌ {msg}{COLOR_RESET}", file=sys.stderr)


def log_stage(msg: str) -> None:
    print(f"\n{COLOR_CYAN}{COLOR_BOLD}=== {msg} ==={COLOR_RESET}\n")


QUOTA_SCAN_TAIL_LINES = 200


def is_quota_error(text: str) -> bool:
    """Check if the end of the output contains quota, credit, or session limit error indicators.

    Only the last ``QUOTA_SCAN_TAIL_LINES`` lines are scanned: a limit error ends the run, so it is near the end, while
    the top of the output echoes the intent text, which can mention limits in prose. On 2026-11-23 the bare pattern
    "usage limit" matched an intent's sentence about "named-reset usage limits" and stepped a flow down from opus to
    sonnet although no limit had been hit (PR #257).
    """
    tail = "\n".join(text.splitlines()[-QUOTA_SCAN_TAIL_LINES:]).lower()
    return any(pattern in tail for pattern in QUOTA_ERROR_PATTERNS)


def resolve_next_model(agent: str, current_model: str) -> tuple[str, str] | None:
    """Determine next fallback runner and model tier when quota is exhausted.

    Returns (new_agent, new_model) or None if all ladders are exhausted.
    """
    if "claude" in agent.lower():
        ladder = FALLBACK_LADDER_CLAUDE
        try:
            idx = ladder.index(current_model)
            if idx + 1 < len(ladder):
                return agent, ladder[idx + 1]
        except ValueError:
            # Current model not in ladder, fall back to second tier
            return agent, ladder[1]

        # Never switch runner on our own: the maintainer decides (no auto-switch to antigravity/gemini).
        log_warn("Claude ladder exhausted; not switching runner without the maintainer's go-ahead.")
        return None

    elif "antigravity" in agent.lower() or "gemini" in agent.lower():
        ladder = FALLBACK_LADDER_ANTIGRAVITY
        base_model = re.sub(r"-(?:xhigh|high|medium|low)$", "", current_model)
        lookup = current_model if current_model in ladder else base_model
        try:
            idx = ladder.index(lookup)
            if idx + 1 < len(ladder):
                return agent, ladder[idx + 1]
        except ValueError:
            return agent, ladder[1]

        # Never switch runner on our own: the maintainer decides.
        log_warn("Antigravity ladder exhausted; not switching runner without the maintainer's go-ahead.")
        return None

    return None


def run_prerequisites_check(target_worktree: Path) -> None:
    """Validate system tools and worktree state before launching the flow."""
    log_info("Validating system prerequisites...")

    # Check holon CLI binary
    holon_bin = shutil.which("holon")
    if not holon_bin:
        log_error(
            "The 'holon' CLI was not found in PATH (~/.local/bin/holon).\n"
            "Run 'python3 .agents/skills/install_holon/scripts/install_holon.py' to install."
        )
        sys.exit(1)
    log_success(f"Found holon CLI at: {holon_bin}")

    # Check Docker daemon
    try:
        res = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode != 0:
            log_error("Docker daemon is not running. Please start Docker.")
            sys.exit(1)
        log_success("Docker daemon is running.")
    except FileNotFoundError:
        log_error("Docker executable not found in PATH.")
        sys.exit(1)

    # Check target worktree
    if not target_worktree.exists():
        log_error(f"Target worktree does not exist: {target_worktree}")
        sys.exit(1)

    git_dir = target_worktree / ".git"
    if not git_dir.exists():
        log_error(f"Target worktree is not a valid git repository: {target_worktree}")
        sys.exit(1)

    log_success(f"Target worktree verified: {target_worktree}")


def truncate_slug(slug: str, limit: int = 32) -> str:
    if len(slug) <= limit:
        return slug
    head = slug[: limit + 1]
    cut = head[:limit] if "-" not in head[1:] else head[: head.rindex("-")]
    return cut[:limit].rstrip("-") or slug[:limit]


def directory_scope_entries(scope, base: Path | None = None) -> list[str]:
    """Scope entries that name a directory (trailing slash, or an existing directory under base)."""
    if not isinstance(scope, list):
        return []
    found = []
    for entry in scope:
        if not isinstance(entry, str):
            continue
        if entry.endswith("/") or (base is not None and (base / entry).is_dir()):
            found.append(entry)
    return found


def parse_intent_file(intent_path: Path) -> dict[str, str]:
    """Parse and validate intent JSON specification."""
    if not intent_path.exists():
        log_error(f"Intent file not found: {intent_path}")
        sys.exit(1)

    try:
        with open(intent_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        log_error(f"Failed to parse intent JSON '{intent_path}': {exc}")
        sys.exit(1)

    required_fields = ["slug", "goal"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        log_error(f"Intent file missing required fields: {', '.join(missing)}")
        sys.exit(1)

    return data


def find_flow_pr(target_worktree: Path, slug: str) -> dict | None:
    """Return the open pull request (number, headRefName, title, url) whose head branch or title names the slug."""
    res = subprocess.run(
        ["gh", "pr", "list", "--state", "open", "--json", "number,headRefName,title,url"],
        cwd=target_worktree,
        capture_output=True,
        text=True,
        check=True,
    )
    prs = json.loads(res.stdout)
    return next((pr for pr in prs if slug in pr["headRefName"] or slug in pr["title"].lower()), None)


CHECKS_TIMEOUT_SECONDS = 45 * 60
CHECKS_POLL_SECONDS = 30
STATE_DIR = Path(__file__).resolve().parents[4] / ".subagent"


def _gh_json(args: list[str], cwd: Path):
    """Run `gh`; return its parsed JSON stdout, or None when unreadable (a pending-checks exit still prints JSON)."""
    res = subprocess.run(["gh", *args], cwd=cwd, capture_output=True, text=True, check=False)
    try:
        return json.loads(res.stdout) if res.stdout.strip() else None
    except ValueError:
        return None


def find_flow_pr_any_state(target_worktree: Path, slug: str) -> dict | None:
    """The flow's pull request in any state, an open one preferred (a merged one is a clean finish)."""
    res = subprocess.run(
        ["gh", "pr", "list", "--state", "all", "--json", "number,headRefName,title,url,state", "--limit", "100"],
        cwd=target_worktree,
        capture_output=True,
        text=True,
        check=True,
    )
    matches = [pr for pr in json.loads(res.stdout) if slug in pr["headRefName"] or slug in pr["title"].lower()]
    matches.sort(key=lambda pr: (pr.get("state") != "OPEN", -pr["number"]))
    return matches[0] if matches else None


def wait_for_pending_checks(
    pr_number: int,
    target_worktree: Path,
    timeout: float = CHECKS_TIMEOUT_SECONDS,
    poll: float = CHECKS_POLL_SECONDS,
    sleep=None,
) -> tuple[list[dict], bool]:
    """Poll the pull request's checks until none is pending or ``timeout`` seconds passed; (checks, still_pending)."""
    import time

    sleep = sleep or time.sleep
    waited = 0.0
    while True:
        checks = _gh_json(["pr", "checks", str(pr_number), "--json", "name,state,bucket"], target_worktree) or []
        pending = [c for c in checks if c.get("bucket") == "pending"]
        if not pending:
            return checks, False
        if waited >= timeout:
            return checks, True
        log_info(f"PR #{pr_number}: {len(pending)} check(s) still pending ({', '.join(c['name'] for c in pending)}).")
        sleep(poll)
        waited += poll


def verify_pr_and_calibration(
    target_worktree: Path,
    slug: str,
    dry_run: bool = False,
    checks_timeout: float = CHECKS_TIMEOUT_SECONDS,
    checks_poll: float = CHECKS_POLL_SECONDS,
    sleep=None,
) -> dict:
    """Verify the flow's pull request, calibration report, mergeability and checks; return the result.

    The result has ``ok`` (False when any problem was found), ``problems`` (strings), ``pr`` (the pull request dict or
    None), ``calibration`` (calibration files in the diff), ``mergeable``, ``merge_state`` and ``checks``. A merged pull
    request is a clean finish. A dry run skips every check and is ok.
    """
    result: dict = {
        "ok": True,
        "problems": [],
        "pr": None,
        "calibration": [],
        "mergeable": None,
        "merge_state": None,
        "checks": [],
    }
    if dry_run:
        log_info("[DRY-RUN] Skipping post-flow PR verification.")
        return result

    def problem(message: str) -> None:
        log_error(message)
        result["ok"] = False
        result["problems"].append(message)

    log_stage("Verifying Pull Request & Calibration Integrity")

    try:
        pr = find_flow_pr_any_state(target_worktree, slug)
    except Exception as exc:  # noqa: BLE001 - an unverifiable flow is not a finished flow
        problem(f"Could not query GitHub PRs: {exc}")
        return result
    if pr is None:
        problem(f"No pull request found matching slug '{slug}'.")
        return result
    result["pr"] = pr

    pr_number = pr["number"]
    log_success(f"Found flow PR #{pr_number}: {pr['url']} ({pr['headRefName']}, {pr.get('state', 'OPEN')})")
    if pr.get("state") == "MERGED":
        result["merge_state"] = "MERGED"
        log_success(f"PR #{pr_number} is already merged; nothing more to verify.")
        return result
    if pr.get("state") == "CLOSED":
        result["merge_state"] = "CLOSED"
        problem(f"PR #{pr_number} is closed without merging.")
        return result

    diff_res = subprocess.run(
        ["gh", "pr", "diff", str(pr_number), "--name-only"],
        cwd=target_worktree,
        capture_output=True,
        text=True,
        check=False,
    )
    if diff_res.returncode != 0:
        problem(f"Could not read the diff of PR #{pr_number}; the calibration report is unverified.")
    else:
        result["calibration"] = [f for f in diff_res.stdout.splitlines() if "_calibration.md" in f]
        if result["calibration"]:
            log_success(f"Calibration report included in PR diff: {', '.join(result['calibration'])}")
        else:
            problem(
                f"PR #{pr_number} diff does not contain a '_calibration.md' report. "
                "Ensure Stage 5 calibration was committed and pushed to the PR branch."
            )

    info = _gh_json(["pr", "view", str(pr_number), "--json", "mergeable,mergeStateStatus"], target_worktree)
    if info is not None:
        result["mergeable"], result["merge_state"] = info.get("mergeable"), info.get("mergeStateStatus")
        log_info(f"PR #{pr_number} Mergeable: {result['mergeable']}, State: {result['merge_state']}")
        if result["mergeable"] == "CONFLICTING" or result["merge_state"] == "DIRTY":
            problem(
                f"PR #{pr_number} has merge conflicts against the target branch (CONFLICTING/DIRTY). "
                "Fetch origin/main, keep main's ledger rows in main's order and append only the branch's new rows, "
                "commit, and push."
            )
    else:
        problem(f"Could not read the mergeability of PR #{pr_number}.")

    checks, still_pending = wait_for_pending_checks(pr_number, target_worktree, checks_timeout, checks_poll, sleep)
    result["checks"] = checks
    if still_pending:
        problem(f"PR #{pr_number} still has pending checks after waiting {int(checks_timeout)} s.")
    return result


def execute_flow_process(
    cmd: list[str],
    dry_run: bool = False,
    env: dict[str, str] | None = None,
) -> tuple[int, str]:
    """Execute command streaming output to stdout and capturing combined log."""
    if dry_run:
        print(f"  [DRY-RUN] {' '.join(cmd)}")
        return 0, ""

    print(f"\n{COLOR_BOLD}Executing command:{COLOR_RESET} {' '.join(cmd)}\n", flush=True)
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env,
    )

    output_lines: list[str] = []
    assert proc.stdout is not None
    for line in proc.stdout:
        print(line, end="", flush=True)
        output_lines.append(line)

    proc.wait()
    combined_output = "".join(output_lines)
    return proc.returncode, combined_output


def resolve_flow_worktree(target_worktree: Path, slug: str, dry_run: bool = False) -> Path:
    """Return the worktree the flow runs in; a ``main`` target becomes a dedicated ``flow-<slug>`` worktree.

    A ``flow-<name>`` target that does not exist yet, beside a ``main`` worktree, is created the same way.

    The ``main`` worktree must stay on ``main`` and identical to ``origin/main``, but stages 4 and 5 check out the
    execution branch and commit in the target worktree. A sibling ``flow-<slug>`` worktree is cut from ``origin/main``
    (the name and branch ``holon flow`` derives itself) and used instead; it is reused when it already exists.
    """
    target_worktree = target_worktree.resolve()
    if target_worktree.name != "main":
        main_worktree = target_worktree.parent / "main"
        if target_worktree.exists() or not target_worktree.name.startswith("flow-") or not main_worktree.exists():
            return target_worktree
        # A missing flow-<name> worktree next to the main worktree is cut from origin/main, like a main target.
        target_worktree, slug = main_worktree, target_worktree.name.removeprefix("flow-")
    clean_slug = re.sub(r"[^a-zA-Z0-9_\-]+", "-", slug.strip()).strip("-") or "flow"
    flow_worktree = target_worktree.parent / f"flow-{clean_slug}"
    if flow_worktree.exists():
        log_info(f"Reusing flow worktree {flow_worktree} (the 'main' worktree stays untouched).")
        return flow_worktree
    log_info(f"Creating flow worktree {flow_worktree} from origin/main (the 'main' worktree stays untouched).")
    if dry_run:
        return flow_worktree
    for cmd in (
        ["git", "-C", str(target_worktree), "fetch", "origin", "main"],
        [
            "git",
            "-C",
            str(target_worktree),
            "worktree",
            "add",
            "--no-track",
            "-b",
            f"flow-{clean_slug}",
            str(flow_worktree),
            "origin/main",
        ],
    ):
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            log_error(f"{' '.join(cmd)} failed: {(result.stderr or result.stdout).strip()}")
            sys.exit(1)
    return flow_worktree


def parse_relative_limit_reset(output: str):
    """Return the datetime of a relative reset such as "Resets in 51m58s" or "resets in 1h 2m", or None."""
    from datetime import datetime, timedelta

    m = re.search(r"resets\s+in\s+(?:(\d+)\s*h)?\s*(?:(\d+)\s*m)?\s*(?:(\d+)\s*s)?", output, re.I)
    if not m or not any(m.groups()):
        return None
    hours, minutes, seconds = (int(part or 0) for part in m.groups())
    return datetime.now().astimezone() + timedelta(hours=hours, minutes=minutes, seconds=seconds)


def parse_limit_reset(output: str):
    """Return the datetime of the usage-limit reset named in ``output`` (e.g. "resets 5:40pm (Australia/Melbourne)").

    Returns None when no reset time is named. A relative reset ("Resets in 51m58s", as Antigravity prints) is that far
    from now. The next occurrence of a named wall-clock time in the named timezone is used (today if still ahead,
    otherwise tomorrow), so daily windows resolve exactly and a weekly reset that names a time resolves to its next
    daily occurrence, which is always sooner than doing nothing.
    """
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo

    relative = parse_relative_limit_reset(output)
    if relative is not None:
        return relative
    m = re.search(r"resets\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)(?:\s*\(([^)]+)\))?", output, re.I)
    if not m:
        return None
    hour, minute, ampm, tz_name = int(m.group(1)), int(m.group(2) or 0), m.group(3).lower(), m.group(4)
    hour = hour % 12 + (12 if ampm == "pm" else 0)
    try:
        tz = ZoneInfo(tz_name) if tz_name else None
    except Exception:  # noqa: BLE001 - an unknown zone name falls back to local time
        tz = None
    now = datetime.now(tz)
    reset = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if reset <= now:
        reset += timedelta(days=1)
    return reset


def wait_for_limit_reset(reset, slug: str) -> None:
    """Sleep until one minute after ``reset``, then return so the flow resumes itself."""
    import time
    from datetime import datetime, timedelta

    resume_at = reset + timedelta(minutes=1)
    log_warn(f"Usage limit hit; the flow will resume itself at {resume_at.strftime('%H:%M %Z') or resume_at}.")
    while True:
        remaining = (resume_at - datetime.now(resume_at.tzinfo)).total_seconds()
        if remaining <= 0:
            return
        time.sleep(min(remaining, 60))


def is_overlap_refusal(output: str) -> bool:
    """Whether ``output`` is a Stage 3 touch-set overlap refusal (not a missing touch set or failed discovery)."""
    return OVERLAP_REFUSAL in output


def parse_overlapping_prs(output: str) -> list[int]:
    """Pull request numbers named by the newest Stage 3 overlap refusal in ``output``; empty for local flows only."""
    refusals = [line for line in output.splitlines() if OVERLAP_REFUSAL in line]
    if not refusals:
        return []
    return sorted({int(number) for number in re.findall(r"pull request #(\d+)", refusals[-1])})


def pr_state(number: int, repo_dir: Path) -> str | None:
    """The state of pull request ``number`` (``OPEN``, ``MERGED``, ``CLOSED``), or None when gh could not tell."""
    try:
        result = subprocess.run(
            ["gh", "pr", "view", str(number), "--json", "state", "--jq", ".state"],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    state = result.stdout.strip().upper()
    return state if result.returncode == 0 and state else None


def wait_for_overlapping_prs(numbers: list[int], repo_dir: Path, poll_seconds: int = OVERLAP_POLL_SECONDS) -> None:
    """Poll each overlapping pull request until none is open (merged or closed), then return so Stage 3 is retried."""
    import time

    pending = set(numbers)
    log_warn(
        "Waiting for overlapping pull request(s) "
        + ", ".join(f"#{n}" for n in sorted(pending))
        + f" to merge or close; polling every {poll_seconds} s."
    )
    while pending:
        for number in sorted(pending):
            state = pr_state(number, repo_dir)
            if state is None:
                log_warn(f"Could not read the state of pull request #{number}; will poll again.")
            elif state != "OPEN":
                log_info(f"Overlapping pull request #{number} is {state.lower()}.")
                pending.discard(number)
        if pending:
            time.sleep(poll_seconds)


def run_flow(
    intent_path: Path,
    target_worktree: Path,
    agent: str,
    model: str,
    from_stage: str | None = None,
    checkpoint: Path | None = None,
    allow_overlap: bool = False,
    auto_fallback: bool = True,
    dry_run: bool = False,
    wait_on_overlap: bool = True,
    overlap_poll_seconds: int = OVERLAP_POLL_SECONDS,
    outcome: dict | None = None,
) -> int:
    """Run holon flow with optional automatic fallback ladder on quota errors."""
    intent_data = parse_intent_file(intent_path)
    slug = intent_data["slug"]
    directories = directory_scope_entries(intent_data.get("scope"), target_worktree)
    if directories:
        log_error(
            "Intent scope must list files, never directories (a directory becomes broad touch-set globs that block "
            f"every concurrent flow at Stage 3 admission): {', '.join(directories)}"
        )
        return 2
    outcome = outcome if outcome is not None else {}
    effective_intent_path = intent_path
    modified = False

    if len(slug) > 32:
        truncated_slug = truncate_slug(slug, 32)
        intent_data["slug"] = truncated_slug
        slug = truncated_slug
        modified = True

    if "0380" in intent_path.name or "module_budgets.json" in str(intent_data.get("scope", [])):
        if "module_budget_change" not in intent_data:
            intent_data["module_budget_change"] = (
                "Budget should be enforced to all packages, including new packages, not just to flow."
            )
            modified = True

    if modified:
        temp_intent_path = intent_path.parent / f"intent-modified-{slug}.json"
        with open(temp_intent_path, "w", encoding="utf-8") as f:
            json.dump(intent_data, f, indent=2)
        effective_intent_path = temp_intent_path

    target_worktree = resolve_flow_worktree(target_worktree, slug, dry_run=dry_run)
    run_prerequisites_check(target_worktree)

    current_agent = agent
    current_model = model
    current_from_stage = from_stage
    current_checkpoint = checkpoint
    current_allow_overlap = allow_overlap

    while True:
        cmd = ["holon", "flow", str(effective_intent_path)]
        cmd.extend(["--target-worktree", str(target_worktree)])
        cmd.extend(["--agent", current_agent])
        cmd.extend(["--model", current_model])

        if current_from_stage:
            cmd.extend(["--from-stage", current_from_stage])
        if current_checkpoint:
            cmd.extend(["--checkpoint", str(current_checkpoint)])
        if current_allow_overlap:
            cmd.append("--allow-overlap")

        log_stage(f"Launching Holon Flow: {slug} (Agent: {current_agent}, Model: {current_model})")

        try:
            flow_env = None if dry_run else build_flow_env(current_agent)
        except AuthRouteMissing as exc:
            log_error(str(exc))
            return 1

        returncode, output = execute_flow_process(cmd, dry_run=dry_run, env=flow_env)
        outcome.update(slug=slug, output=output, agent=current_agent, model=current_model, worktree=target_worktree)

        if returncode == 0:
            log_success(f"Holon flow for '{slug}' completed successfully!")
            verification = verify_pr_and_calibration(target_worktree, slug, dry_run=dry_run)
            outcome["verification"] = verification
            if not verification["ok"]:
                log_error(
                    "The flow exited 0 but its deliverables are incomplete: " + "; ".join(verification["problems"])
                )
                return 1
            return 0

        # Flow failed. Check for quota or session exhaustion
        log_error(f"Holon flow exited with non-zero code {returncode}.")

        # An admission refusal is never overridden here: the override is the caller's decision, and every
        # --allow-overlap admission moves the plan tip, which makes the engine discard a failed attempt's partial work.
        # A touch-set overlap is waited out instead: poll the overlapping pull requests until they merge or close
        # (a local flow with no pull request is re-checked by re-running admission), then resume from the checkpoint.
        if "or rerun with --allow-overlap" in output and not current_allow_overlap:
            refusal = next((line.strip() for line in output.splitlines() if "Stage 3 refused" in line), "")
            if wait_on_overlap and is_overlap_refusal(output) and not dry_run:
                if refusal:
                    print(refusal)
                numbers = parse_overlapping_prs(output)
                if numbers:
                    wait_for_overlapping_prs(numbers, target_worktree, overlap_poll_seconds)
                else:
                    import time

                    log_warn(
                        f"The overlap is a local flow with no pull request; re-checking admission in "
                        f"{overlap_poll_seconds} s."
                    )
                    time.sleep(overlap_poll_seconds)
                chk_path = target_worktree / f".holon/flow/checkpoint-{slug}.json"
                if chk_path.exists():
                    current_checkpoint = chk_path
                    current_from_stage = None
                else:
                    current_from_stage = "execute"
                log_info("Overlap cleared; resuming Stage 3 (admission is checked again).")
                continue
            log_error(
                "Stage 3 admission refused for a touch-set overlap; not retrying. Wait for the overlapping flow to "
                "merge, or rerun with --allow-overlap if the maintainer accepts the overlap."
            )
            if refusal:
                print(refusal)
            return returncode

        if auto_fallback and is_quota_error(output):
            log_warn("Detected model credit, quota, or session limit exhaustion.")
            # A limit that names its reset time is waited out and resumed on the SAME model (maintainer rule,
            # 2026-11-11); the fallback ladder is for exhaustion with no reset time in sight.
            reset = parse_limit_reset(output)
            if reset is not None:
                chk_path = target_worktree / f".holon/flow/checkpoint-{slug}.json"
                if chk_path.exists():
                    current_checkpoint = chk_path
                    current_from_stage = None
                wait_for_limit_reset(reset, slug)
                log_info("Usage limit window reset; resuming the flow from its checkpoint.")
                continue
            fallback = resolve_next_model(current_agent, current_model)
            if fallback:
                next_agent, next_model = fallback
                log_info(
                    f"Applying AGENTS.md fallback ladder: stepping down to Agent='{next_agent}', Model='{next_model}'."
                )

                # Locate checkpoint file to resume from
                chk_path = target_worktree / f".holon/flow/checkpoint-{slug}.json"
                if chk_path.exists():
                    current_checkpoint = chk_path
                    current_from_stage = None
                    log_info(f"Resuming from checkpoint: {current_checkpoint}")
                else:
                    log_info("No checkpoint found; continuing with intent specification.")

                current_agent = next_agent
                current_model = next_model
                continue

        # If not quota error or fallbacks exhausted, report resume instructions
        log_warn("Flow execution stopped. To resume this flow manually, use:")
        chk_path = target_worktree / f".holon/flow/checkpoint-{slug}.json"
        if chk_path.exists():
            print(
                f"\n  holon flow {intent_path} --target-worktree {target_worktree} "
                f"--agent {current_agent} --model {current_model} --checkpoint {chk_path}\n"
            )
        else:
            print(
                f"\n  holon flow {intent_path} --target-worktree {target_worktree} "
                f"--agent {current_agent} --model {current_model} --from-stage <stage>\n"
            )
        return returncode


def _calibration_done(target_worktree: Path, slug: str) -> bool:
    """True when the flow's checkpoint records Stage 5 (calibration) as completed."""
    try:
        checkpoint = json.loads((target_worktree / f".holon/flow/checkpoint-{slug}.json").read_text())
        return "calibrate" in checkpoint.get("completed_stages", [])
    except (OSError, ValueError):
        return False


def _notify_outcome(intent_path: Path, exit_code: int, target_worktree: Path) -> None:
    """Tell the maintainer (ntfy.sh, if configured) that calibration is done; send nothing otherwise.

    A flow that stops, fails or waits on a limit stays silent: the only notification is the one that says the pull
    request is calibrated and ready for the maintainer's merge. Never fails the flow.
    """
    try:
        from notify_ntfy import notify

        slug = parse_intent_file(intent_path)["slug"]
        if exit_code == 0 and _calibration_done(target_worktree, slug):
            try:
                pr = find_flow_pr(target_worktree, slug)
            except Exception:  # noqa: BLE001 - the PR number is a nicety; still notify without it
                pr = None
            ref = f"PR #{pr['number']}" if pr else "the PR"
            notify(
                f"Holon flow calibrated: {ref} ({slug})" if pr else f"Holon flow calibrated: {slug}",
                f"Calibration is done and in {ref}. Review and merge it when you are ready.",
                tags="white_check_mark",
            )
    except Exception:  # noqa: BLE001 - a notification must never break a flow
        pass


def build_flow_state(slug: str, exit_code: int, outcome: dict, worktree: Path | None) -> dict:
    """The deterministic state record a resuming driver reads (``.subagent/flow_<slug>_state.json``)."""
    import re as _re

    output = outcome.get("output") or ""
    verification = outcome.get("verification") or {}
    pr = verification.get("pr") or {}
    stages: list[str] = []
    if worktree is not None:
        with contextlib.suppress(OSError, ValueError):
            stages = json.loads((worktree / f".holon/flow/checkpoint-{slug}.json").read_text()).get(
                "completed_stages", []
            )
    consensus = next(
        (line.strip() for line in reversed(output.splitlines()) if _re.search(r"consensus", line, _re.I)), None
    )
    ev = None
    for match in _re.finditer(r"\bEV\b\s*[:=]?\s*(-?\d+(?:\.\d+)?)", output):
        ev = float(match.group(1))
    merge_state = verification.get("merge_state")
    problems = verification.get("problems", [])
    if exit_code == 0 and merge_state == "MERGED":
        next_action = "run post-pr-merge"
    elif exit_code == 0:
        next_action = "maintainer merges the pull request"
    elif problems:
        next_action = "fix: " + "; ".join(problems)
    else:
        next_action = "diagnose the flow failure and resume from the checkpoint"
    return {
        "slug": slug,
        "status": "completed" if exit_code == 0 else "failed",
        "exit_code": exit_code,
        "pr_number": pr.get("number"),
        "pr_url": pr.get("url"),
        "stage_reached": stages[-1] if stages else None,
        "completed_stages": stages,
        "consensus": consensus,
        "calibration_ev": ev,
        "calibration_files": verification.get("calibration", []),
        "mergeable": verification.get("mergeable"),
        "merge_state": merge_state,
        "agent": outcome.get("agent"),
        "model": outcome.get("model"),
        "problems": problems,
        "next_action": next_action,
    }


def write_flow_state(
    slug: str, exit_code: int, outcome: dict, worktree: Path | None, state_dir: Path | None = None
) -> Path:
    """Write the state file for the flow; returns its path. Never raises into the caller's exit code."""
    state_dir = state_dir or STATE_DIR
    state_dir.mkdir(parents=True, exist_ok=True)
    path = state_dir / f"flow_{slug}_state.json"
    path.write_text(json.dumps(build_flow_state(slug, exit_code, outcome, worktree), indent=2) + "\n")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run and monitor the 5-stage Holon flow from a subagent or terminal.")
    parser.add_argument(
        "intent",
        type=Path,
        help="Path to intent JSON specification file.",
    )
    parser.add_argument(
        "--target-worktree",
        type=Path,
        default=Path("apps/holon-agentic-coder/main"),
        help=(
            "Target repository worktree (default: apps/holon-agentic-coder/main). Naming the 'main' worktree selects "
            "the repository and base branch only: the flow runs in a dedicated flow-<slug> worktree branched off "
            "origin/main, and the 'main' worktree itself is never touched."
        ),
    )
    parser.add_argument(
        "--agent",
        type=str,
        default="antigravity-agent",
        help="Agent runner binary/container (default: antigravity-agent).",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=FALLBACK_LADDER_ANTIGRAVITY[0],
        help="Model tier for the agent runner (default: gemini-4-neon).",
    )
    parser.add_argument(
        "--from-stage",
        type=str,
        choices=["intent", "plan", "execute", "review", "calibrate"],
        help="Resume pipeline from a specific stage.",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        help="Path to checkpoint JSON file to resume from.",
    )
    parser.add_argument(
        "--no-fallback",
        action="store_true",
        help="Disable automatic model fallback on quota exhaustion.",
    )
    parser.add_argument(
        "--allow-overlap",
        action="store_true",
        help="Admit Stage 3 even when the plan's touch set overlaps a flow in flight or is undeclared.",
    )
    parser.add_argument(
        "--no-wait-on-overlap",
        action="store_true",
        help="Stop on a Stage 3 touch-set overlap refusal instead of waiting for the overlapping flows to finish.",
    )
    parser.add_argument(
        "--overlap-poll-seconds",
        type=int,
        default=OVERLAP_POLL_SECONDS,
        help=f"How often an overlap wait polls the overlapping pull requests (default: {OVERLAP_POLL_SECONDS}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate execution without running docker or mutating git state.",
    )

    args = parser.parse_args()

    # Redirected to a file, stdout is block-buffered and the log stays empty until exit; flush every line instead.
    enable_line_buffering()

    outcome: dict = {}
    exit_code = run_flow(
        intent_path=args.intent,
        target_worktree=args.target_worktree,
        agent=args.agent,
        model=args.model,
        from_stage=args.from_stage,
        checkpoint=args.checkpoint,
        allow_overlap=args.allow_overlap,
        auto_fallback=not args.no_fallback,
        dry_run=args.dry_run,
        wait_on_overlap=not args.no_wait_on_overlap,
        overlap_poll_seconds=args.overlap_poll_seconds,
        outcome=outcome,
    )
    if not args.dry_run:
        slug = parse_intent_file(args.intent)["slug"]
        flow_worktree = resolve_flow_worktree(args.target_worktree, slug)
        try:
            write_flow_state(outcome.get("slug", slug), exit_code, outcome, flow_worktree)
        except Exception as exc:  # noqa: BLE001 - the state file must not change the exit code
            log_warn(f"Could not write the flow state file: {exc}")
        _notify_outcome(args.intent, exit_code, flow_worktree)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
