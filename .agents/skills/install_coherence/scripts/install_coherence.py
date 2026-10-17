#!/usr/bin/env python3
"""install_coherence.py

Dedicated orchestrator script to build the holon-coherence Docker container image
via Docker Buildx Bake and install/update the holon-coherence CLI via uv tool install.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

COLOR_BOLD = "\033[1m"
COLOR_GREEN = "\033[1;32m"
COLOR_RED = "\033[1;31m"
COLOR_YELLOW = "\033[1;33m"
COLOR_RESET = "\033[0m"


def log_info(msg: str) -> None:
    print(f"{COLOR_BOLD}INFO:{COLOR_RESET} {msg}")


def log_success(msg: str) -> None:
    print(f"{COLOR_GREEN}SUCCESS:{COLOR_RESET} {msg}")


def log_warn(msg: str) -> None:
    print(f"{COLOR_YELLOW}WARNING:{COLOR_RESET} {msg}")


def log_error(msg: str) -> None:
    print(f"{COLOR_RED}ERROR:{COLOR_RESET} {msg}", file=sys.stderr)


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
    log_info("Validating system prerequisites for holon-coherence...")

    if not shutil.which("uv"):
        log_error("uv package runner is not found on PATH.")
        log_error("Install uv via: curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)
    uv_ver = subprocess.run(["uv", "--version"], capture_output=True, text=True).stdout.strip()
    log_success(f"Found uv: {uv_ver}")

    if not shutil.which("docker"):
        log_error("Docker CLI is not found on PATH.")
        sys.exit(1)

    res = subprocess.run(["docker", "info"], capture_output=True, text=True)
    if res.returncode != 0:
        log_error("Docker daemon is not running. Please start Docker Desktop or the Docker daemon.")
        sys.exit(1)
    log_success("Docker daemon is running.")

    res = subprocess.run(["docker", "buildx", "version"], capture_output=True, text=True)
    if res.returncode != 0:
        log_error("Docker Buildx plugin is not working.")
        sys.exit(1)
    log_success(f"Found Docker Buildx: {res.stdout.strip()}")


def sync_git_worktree(repo_path: Path, dry_run: bool = False) -> None:
    log_info(f"Syncing holon-coherence repository worktree at {repo_path}...")
    run_cmd(["git", "fetch", "origin"], cwd=repo_path, dry_run=dry_run)
    branch_res = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    current_branch = branch_res.stdout.strip()
    if current_branch == "main":
        run_cmd(["git", "pull", "--ff-only", "origin", "main"], cwd=repo_path, dry_run=dry_run, check=False)
    log_success(f"Synchronised holon-coherence on branch {current_branch}.")


def build_image(repo_path: Path, no_cache: bool = False, dry_run: bool = False) -> None:
    log_info("Building holon-coherence Docker container image via Buildx Bake...")
    build_script = repo_path / "build_image.sh"
    if not build_script.exists():
        log_error(f"Build script not found: {build_script}")
        sys.exit(1)

    cmd = [str(build_script)]
    if no_cache:
        cmd.append("--no-cache")
    run_cmd(cmd, cwd=repo_path, dry_run=dry_run)
    log_success("holon-coherence Docker image built and loaded.")


def install_cli(package_path: Path, editable: bool = True, dry_run: bool = False) -> None:
    log_info(f"Installing holon-coherence CLI from {package_path}...")
    cmd = ["uv", "tool", "install", "--force", "--reinstall"]
    if editable:
        cmd.append("--editable")
    cmd.append(str(package_path))
    run_cmd(cmd, dry_run=dry_run)
    log_success("holon-coherence CLI installed into ~/.local/bin/.")


def verify_installation(dry_run: bool = False) -> None:
    if dry_run:
        log_info("[DRY-RUN] Skipping verification.")
        return

    log_info("Verifying holon-coherence installation...")
    coherence_bin = shutil.which("holon-coherence")
    if coherence_bin:
        log_success(f"Executable holon-coherence resolved at: {coherence_bin}")
    else:
        log_error("Executable holon-coherence not found on PATH!")
        sys.exit(1)

    res = subprocess.run(["docker", "image", "inspect", "holon-coherence:latest"], capture_output=True, text=True)
    if res.returncode == 0:
        log_success("Docker image holon-coherence:latest is present locally.")
    else:
        log_warn("Docker image holon-coherence:latest was not found in local Docker store.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build Docker container image and install holon-coherence CLI via uv tool install."
    )
    parser.add_argument("--skip-image", action="store_true", help="Skip Docker image build")
    parser.add_argument("--skip-tool", action="store_true", help="Skip uv tool install step")
    parser.add_argument("--no-cache", action="store_true", help="Build Docker image without cache")
    parser.add_argument("--no-sync", action="store_true", help="Skip git fetch/pull")
    parser.add_argument("--non-editable", action="store_true", help="Install standard wheel instead of editable mode")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without modifying state")

    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    workspace_root = script_dir.parents[3]
    coherence_path = workspace_root / "apps" / "holon-coherence" / "main"

    if not coherence_path.exists():
        log_error(f"holon-coherence workspace not found at {coherence_path}")
        sys.exit(1)

    log_info("Starting holon-coherence Installation Pipeline")
    check_prerequisites()

    if not args.no_sync:
        sync_git_worktree(coherence_path, dry_run=args.dry_run)

    if not args.skip_image:
        build_image(coherence_path, no_cache=args.no_cache, dry_run=args.dry_run)

    if not args.skip_tool:
        install_cli(coherence_path, editable=not args.non_editable, dry_run=args.dry_run)

    verify_installation(dry_run=args.dry_run)
    log_success("holon-coherence installation completed successfully.")


if __name__ == "__main__":
    main()
