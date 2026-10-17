#!/usr/bin/env python3
"""install_holon.py

Automated orchestrator script to build Docker container images via Docker Buildx Bake
and install/update the latest versions of the holon and holon-coherence CLIs via uv tool install.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Terminal colors
COLOR_BOLD = "\033[1m"
COLOR_GREEN = "\033[1;32m"
COLOR_RED = "\033[1;31m"
COLOR_YELLOW = "\033[1;33m"
COLOR_RESET = "\033[0m"


def log_info(msg: str) -> None:
    print(f"{COLOR_BOLD}INFO:{COLOR_RESET} {msg}")


def log_success(msg: str) -> None:
    print(f"{COLOR_GREEN}✅ {msg}{COLOR_RESET}")


def log_warn(msg: str) -> None:
    print(f"{COLOR_YELLOW}⚠️  {msg}{COLOR_RESET}")


def log_error(msg: str) -> None:
    print(f"{COLOR_RED}❌ {msg}{COLOR_RESET}", file=sys.stderr)


def run_cmd(
    cmd: list[str],
    cwd: Path | str | None = None,
    dry_run: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    cmd_str = " ".join(cmd)
    if dry_run:
        print(f"  [DRY-RUN] (cwd={cwd or '.'}) {cmd_str}")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    print(f"  --> {cmd_str}")
    res = subprocess.run(cmd, cwd=cwd, text=True, capture_output=False)
    if check and res.returncode != 0:
        log_error(f"Command failed with exit code {res.returncode}: {cmd_str}")
        sys.exit(res.returncode)
    return res


def check_prerequisites() -> None:
    log_info("Validating system prerequisites...")

    # 1. uv
    if not shutil.which("uv"):
        log_error("uv package runner is not installed or not on PATH.")
        log_error("Install uv via: curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)
    uv_ver = subprocess.run(["uv", "--version"], capture_output=True, text=True).stdout.strip()
    log_success(f"Found uv: {uv_ver}")

    # 2. docker
    if not shutil.which("docker"):
        log_error("Docker CLI is not found on PATH.")
        sys.exit(1)

    # 3. docker daemon
    res = subprocess.run(["docker", "info"], capture_output=True, text=True)
    if res.returncode != 0:
        log_error("Docker daemon is not running. Please start Docker.")
        sys.exit(1)
    log_success("Docker daemon is active and responsive.")

    # 4. docker buildx
    res = subprocess.run(["docker", "buildx", "version"], capture_output=True, text=True)
    if res.returncode != 0:
        log_error("Docker Buildx plugin is not installed or not working.")
        sys.exit(1)
    log_success(f"Found Docker Buildx: {res.stdout.strip()}")


def sync_git_worktree(repo_path: Path, dry_run: bool = False) -> None:
    log_info(f"Syncing repository worktree at {repo_path}...")
    if not (repo_path / ".git").exists() and not (repo_path.parent / ".git").exists():
        log_warn(f"Directory {repo_path} does not appear to be a Git repository; skipping fetch.")
        return

    run_cmd(["git", "fetch", "origin"], cwd=repo_path, dry_run=dry_run)
    # Check if currently on main
    branch_res = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    current_branch = branch_res.stdout.strip()
    if current_branch == "main":
        run_cmd(["git", "pull", "--ff-only", "origin", "main"], cwd=repo_path, dry_run=dry_run, check=False)
    log_success(f"Synchronised {repo_path.name} on branch {current_branch}.")


def build_holon_agentic_coder_images(repo_path: Path, no_cache: bool = False, dry_run: bool = False) -> None:
    log_info("Building Docker images for holon-agentic-coder via Buildx Bake...")
    build_script = repo_path / "apps" / "sandbox-executor" / "build_all_images.sh"
    if not build_script.exists():
        log_error(f"Build script not found: {build_script}")
        sys.exit(1)

    cmd = [str(build_script)]
    if no_cache:
        cmd.append("--no-cache")
    run_cmd(cmd, cwd=repo_path, dry_run=dry_run)
    log_success("All holon-agentic-coder Docker images built and loaded.")


def build_holon_coherence_images(repo_path: Path, no_cache: bool = False, dry_run: bool = False) -> None:
    log_info("Building Docker image for holon-coherence via Buildx Bake...")
    build_script = repo_path / "build_image.sh"
    if not build_script.exists():
        log_error(f"Build script not found: {build_script}")
        sys.exit(1)

    cmd = [str(build_script)]
    if no_cache:
        cmd.append("--no-cache")
    run_cmd(cmd, cwd=repo_path, dry_run=dry_run)
    log_success("holon-coherence Docker image built and loaded.")


def install_holon_cli(package_path: Path, editable: bool = True, dry_run: bool = False) -> None:
    log_info(f"Installing holon CLI from {package_path}...")
    cmd = ["uv", "tool", "install", "--force", "--reinstall"]
    if editable:
        cmd.append("--editable")
    cmd.append(str(package_path))
    run_cmd(cmd, dry_run=dry_run)
    log_success("holon CLI installed successfully.")


def install_holon_coherence_cli(package_path: Path, editable: bool = True, dry_run: bool = False) -> None:
    log_info(f"Installing holon-coherence CLI from {package_path}...")
    cmd = ["uv", "tool", "install", "--force", "--reinstall"]
    if editable:
        cmd.append("--editable")
    cmd.append(str(package_path))
    run_cmd(cmd, dry_run=dry_run)
    log_success("holon-coherence CLI installed successfully.")


def verify_installation(dry_run: bool = False) -> None:
    if dry_run:
        log_info("[DRY-RUN] Skipping verification.")
        return

    log_info("Verifying installed tools and built images...")
    # Verify uv tool list
    res = subprocess.run(["uv", "tool", "list"], capture_output=True, text=True)
    print(res.stdout)

    # Check binaries
    for tool_name in ["holon", "holon-coherence"]:
        tool_bin = shutil.which(tool_name)
        if tool_bin:
            log_success(f"Executable {tool_name} is resolved at: {tool_bin}")
        else:
            log_error(f"Executable {tool_name} was NOT found on PATH!")

    # Check images
    images = [
        "holon/base:latest",
        "holon/orchestrator:latest",
        "holon/agent-antigravity:latest",
        "holon-coherence:latest",
    ]
    for img in images:
        res = subprocess.run(["docker", "image", "inspect", img], capture_output=True, text=True)
        if res.returncode == 0:
            log_success(f"Docker image {img} is present locally.")
        else:
            log_warn(f"Docker image {img} was not found in local image store.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build Docker images and install latest holon and holon-coherence CLIs via uv tool install."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", default=True, help="Build and install both components (default)")
    group.add_argument("--holon-only", action="store_true", help="Build and install holon-agentic-coder only")
    group.add_argument("--coherence-only", action="store_true", help="Build and install holon-coherence only")

    parser.add_argument("--skip-images", action="store_true", help="Skip Docker image builds")
    parser.add_argument("--skip-tools", action="store_true", help="Skip uv tool install steps")
    parser.add_argument("--no-cache", action="store_true", help="Build Docker images without cache")
    parser.add_argument("--no-sync", action="store_true", help="Skip git fetch/pull")
    parser.add_argument("--non-editable", action="store_true", help="Install standard wheels instead of editable mode")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without modifying state")

    args = parser.parse_args()

    # Determine workspace root
    script_dir = Path(__file__).resolve().parent
    workspace_root = script_dir.parents[3]  # .agents/skills/install_holon/scripts/ -> workspace root

    holon_agentic_coder_path = workspace_root / "apps" / "holon-agentic-coder" / "main"
    holon_coherence_path = workspace_root / "apps" / "holon-coherence" / "main"
    holon_package_path = holon_agentic_coder_path / "apps" / "sandbox-executor"

    build_holon = not args.coherence_only
    build_coherence = not args.holon_only
    editable = not args.non_editable

    log_info("Starting Holon Ecosystem Installation & Build Pipeline")
    check_prerequisites()

    # 1. Sync
    if not args.no_sync:
        if build_holon and holon_agentic_coder_path.exists():
            sync_git_worktree(holon_agentic_coder_path, dry_run=args.dry_run)
        if build_coherence and holon_coherence_path.exists():
            sync_git_worktree(holon_coherence_path, dry_run=args.dry_run)

    # 2. Build Docker images
    if not args.skip_images:
        if build_holon and holon_agentic_coder_path.exists():
            build_holon_agentic_coder_images(holon_agentic_coder_path, no_cache=args.no_cache, dry_run=args.dry_run)
        if build_coherence and holon_coherence_path.exists():
            build_holon_coherence_images(holon_coherence_path, no_cache=args.no_cache, dry_run=args.dry_run)

    # 3. Install CLIs via uv tool install
    if not args.skip_tools:
        if build_holon and holon_package_path.exists():
            install_holon_cli(holon_package_path, editable=editable, dry_run=args.dry_run)
        if build_coherence and holon_coherence_path.exists():
            install_holon_coherence_cli(holon_coherence_path, editable=editable, dry_run=args.dry_run)

    # 4. Verify
    verify_installation(dry_run=args.dry_run)
    log_success("All tasks completed successfully!")


if __name__ == "__main__":
    main()
