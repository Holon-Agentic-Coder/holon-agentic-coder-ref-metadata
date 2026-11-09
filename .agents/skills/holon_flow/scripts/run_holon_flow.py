#!/usr/bin/env python3
"""run_holon_flow.py

Automated orchestrator script to execute and monitor the 5-stage Holon flow
(Intent -> Plan -> Execute -> Review Loop -> Calibration) across managed target
repositories (holon-agentic-coder and holon-coherence) from a subagent or shell.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

# Terminal formatting
COLOR_BOLD = "\033[1m"
COLOR_GREEN = "\033[1;32m"
COLOR_RED = "\033[1;31m"
COLOR_YELLOW = "\033[1;33m"
COLOR_CYAN = "\033[1;36m"
COLOR_RESET = "\033[0m"

# Model fallback ladders (AGENTS.md)
FALLBACK_LADDER_CLAUDE = [
    "claude-fable-5",
    "claude-opus-5-5",
    "claude-sonnet-4-6",
    "claude-haiku-4-5",
]

FALLBACK_LADDER_ANTIGRAVITY = [
    "gemini-3.8-pro-high",
    "gemini-3.8-pro",
    "gemini-3.8-flash-medium",
    "gemini-3.8-flash",
]

QUOTA_ERROR_PATTERNS = [
    "hit your session limit",
    "session limit reached",
    "insufficient_quota",
    "resource_exhausted",
    "rate_limit_exceeded",
    "too many requests",
    "http 429",
    "status 429",
    "credit balance is too low",
]


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


def is_quota_error(text: str) -> bool:
    """Check if output contains quota, credit, or session limit error indicators."""
    lower_text = text.lower()
    return any(pattern in lower_text for pattern in QUOTA_ERROR_PATTERNS)


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

        # Cross-runner fallback to antigravity
        log_warn("Claude ladder exhausted; switching runner to antigravity-agent.")
        return "antigravity-agent", FALLBACK_LADDER_ANTIGRAVITY[0]

    elif "antigravity" in agent.lower() or "gemini" in agent.lower():
        ladder = FALLBACK_LADDER_ANTIGRAVITY
        try:
            idx = ladder.index(current_model)
            if idx + 1 < len(ladder):
                return agent, ladder[idx + 1]
        except ValueError:
            return agent, ladder[1]

        # Cross-runner fallback to claude
        log_warn("Antigravity ladder exhausted; switching runner to claude-agent.")
        return "claude-agent", FALLBACK_LADDER_CLAUDE[0]

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
    if target_worktree.name == "main":
        log_error(
            f"Refusing to run the flow in the 'main' worktree: {target_worktree}. Create a dedicated worktree "
            "(git worktree add --no-track -b task/<bean-id>-<slug> ../task-<bean-id>-<slug> origin/main) and pass that."
        )
        sys.exit(1)

    if not target_worktree.exists():
        log_error(f"Target worktree does not exist: {target_worktree}")
        sys.exit(1)

    git_dir = target_worktree / ".git"
    if not git_dir.exists():
        log_error(f"Target worktree is not a valid git repository: {target_worktree}")
        sys.exit(1)

    log_success(f"Target worktree verified: {target_worktree}")


def parse_intent_file(intent_path: Path) -> dict[str, str]:
    """Parse and validate intent JSON specification."""
    if not intent_path.exists():
        log_error(f"Intent file not found: {intent_path}")
        sys.exit(1)

    try:
        with open(intent_path, "r", encoding="utf-8") as f:
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


def verify_pr_and_calibration(
    target_worktree: Path,
    slug: str,
    dry_run: bool = False,
) -> None:
    """Verify that the flow opened a PR and that the calibration report is included."""
    if dry_run:
        log_info("[DRY-RUN] Skipping post-flow PR verification.")
        return

    log_stage("Verifying Pull Request & Calibration Integrity")

    # Locate PR using gh CLI
    try:
        res = subprocess.run(
            ["gh", "pr", "list", "--state", "open", "--json", "number,headRefName,title,url"],
            cwd=target_worktree,
            capture_output=True,
            text=True,
            check=True,
        )
        prs = json.loads(res.stdout)
    except Exception as exc:
        log_warn(f"Could not query GitHub PRs: {exc}")
        return

    matching_prs = [
        pr for pr in prs if slug in pr["headRefName"] or slug in pr["title"].lower()
    ]
    if not matching_prs:
        log_warn(f"No open PR found matching slug '{slug}'.")
        return

    pr = matching_prs[0]
    pr_number = pr["number"]
    pr_url = pr["url"]
    head_branch = pr["headRefName"]
    log_success(f"Found active flow PR #{pr_number}: {pr_url} ({head_branch})")

    # Verify calibration report exists in PR diff
    diff_res = subprocess.run(
        ["gh", "pr", "diff", str(pr_number), "--name-only"],
        cwd=target_worktree,
        capture_output=True,
        text=True,
        check=False,
    )
    if diff_res.returncode == 0:
        files = diff_res.stdout.splitlines()
        calib_files = [f for f in files if "_calibration.md" in f]
        if calib_files:
            log_success(f"Calibration report included in PR diff: {', '.join(calib_files)}")
        else:
            log_warn(
                f"PR #{pr_number} diff does not yet contain a '_calibration.md' report.\n"
                "Ensure Stage 5 calibration was committed and pushed to the PR branch."
            )

    # Check mergeability status against target branch
    view_res = subprocess.run(
        ["gh", "pr", "view", str(pr_number), "--json", "mergeable,mergeStateStatus"],
        cwd=target_worktree,
        capture_output=True,
        text=True,
        check=False,
    )
    if view_res.returncode == 0:
        pr_info = json.loads(view_res.stdout)
        mergeable = pr_info.get("mergeable")
        status = pr_info.get("mergeStateStatus")
        log_info(f"PR #{pr_number} Mergeable: {mergeable}, State: {status}")
        if mergeable == "CONFLICTING":
            log_error(
                f"PR #{pr_number} has merge conflicts against target branch! "
                "Per AGENTS.md Invariant 14, fetch origin/main, resolve ledger conflicts "
                "by chronological interleaving, commit, and push."
            )


def execute_flow_process(
    cmd: list[str],
    dry_run: bool = False,
) -> tuple[int, str]:
    """Execute command streaming output to stdout and capturing combined log."""
    if dry_run:
        print(f"  [DRY-RUN] {' '.join(cmd)}")
        return 0, ""

    print(f"\n{COLOR_BOLD}Executing command:{COLOR_RESET} {' '.join(cmd)}\n")
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    output_lines: list[str] = []
    assert proc.stdout is not None
    for line in proc.stdout:
        print(line, end="")
        output_lines.append(line)

    proc.wait()
    combined_output = "".join(output_lines)
    return proc.returncode, combined_output


def run_flow(
    intent_path: Path,
    target_worktree: Path,
    agent: str,
    model: str,
    from_stage: str | None = None,
    checkpoint: Path | None = None,
    auto_fallback: bool = True,
    dry_run: bool = False,
) -> int:
    """Run holon flow with optional automatic fallback ladder on quota errors."""
    run_prerequisites_check(target_worktree)
    intent_data = parse_intent_file(intent_path)
    slug = intent_data["slug"]

    current_agent = agent
    current_model = model
    current_from_stage = from_stage
    current_checkpoint = checkpoint

    while True:
        cmd = ["holon", "flow", str(intent_path)]
        cmd.extend(["--target-worktree", str(target_worktree)])
        cmd.extend(["--agent", current_agent])
        cmd.extend(["--model", current_model])

        if current_from_stage:
            cmd.extend(["--from-stage", current_from_stage])
        if current_checkpoint:
            cmd.extend(["--checkpoint", str(current_checkpoint)])

        log_stage(
            f"Launching Holon Flow: {slug} (Agent: {current_agent}, Model: {current_model})"
        )

        returncode, output = execute_flow_process(cmd, dry_run=dry_run)

        if returncode == 0:
            log_success(f"Holon flow for '{slug}' completed successfully!")
            verify_pr_and_calibration(target_worktree, slug, dry_run=dry_run)
            return 0

        # Flow failed. Check for quota or session exhaustion
        log_error(f"Holon flow exited with non-zero code {returncode}.")

        if auto_fallback and is_quota_error(output):
            log_warn("Detected model credit, quota, or session limit exhaustion.")
            fallback = resolve_next_model(current_agent, current_model)
            if fallback:
                next_agent, next_model = fallback
                log_info(
                    f"Applying AGENTS.md fallback ladder: "
                    f"stepping down to Agent='{next_agent}', Model='{next_model}'."
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run and monitor the 5-stage Holon flow from a subagent or terminal."
    )
    parser.add_argument(
        "intent",
        type=Path,
        help="Path to intent JSON specification file.",
    )
    parser.add_argument(
        "--target-worktree",
        type=Path,
        required=True,
        help=(
            "Path to a dedicated git worktree for this flow, e.g. apps/holon-agentic-coder/task-<bean-id>-<slug>. "
            "The 'main' worktree is never a valid target: the flow checks out and commits on branches there."
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
        default="gemini-3.8-flash-medium",
        help="Model tier for the agent runner (default: gemini-3.8-flash-medium).",
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
        "--dry-run",
        action="store_true",
        help="Simulate execution without running docker or mutating git state.",
    )

    args = parser.parse_args()

    exit_code = run_flow(
        intent_path=args.intent,
        target_worktree=args.target_worktree,
        agent=args.agent,
        model=args.model,
        from_stage=args.from_stage,
        checkpoint=args.checkpoint,
        auto_fallback=not args.no_fallback,
        dry_run=args.dry_run,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
