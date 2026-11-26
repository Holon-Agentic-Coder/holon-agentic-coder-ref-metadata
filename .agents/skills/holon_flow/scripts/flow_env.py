"""The environment a `holon flow` child process needs, built from the stored token so no one exports it by hand.

A `claude-agent` container gets credentials only through `HOLON_AGENT_SETTINGS`: a JSON object whose `env` carries the
OAuth token, plus an echo pad that keeps the token past the planner (100 character) and executor (250 character) echo
truncation. A shell without it starts every Claude role container with no credentials, and the Stage 4 reviewers then
exit with code 1 within seconds. The token is read, placed in the child's environment and never printed or logged.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path

TOKEN_FILE = "claude-oauth-token"
ECHO_PAD = "x" * 300
CLAUDE_AGENTS = ("claude-agent",)
# Where the engine keeps the token since it moved out of the plaintext file: the OS secret store, under the same
# service and account names as `sandbox_executor.claude_keychain`.
KEYCHAIN_SERVICE = "holon"
KEYCHAIN_ACCOUNT = "claude-oauth-token"
KEYCHAIN_LOOKUP = {
    "darwin": ("security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-a", KEYCHAIN_ACCOUNT, "-w"),
    "linux": ("secret-tool", "lookup", "service", KEYCHAIN_SERVICE, "account", KEYCHAIN_ACCOUNT),
}
KEYCHAIN_TIMEOUT_SECONDS = 10
# The default 45-minute Stage 3 budget cuts a large plan off mid-execution, and the next attempt starts over. One
# week stands in for "no limit" until the engine takes an explicit unlimited budget.
EXECUTE_BUDGET_VARIABLE = "HOLON_STAGE_BUDGET_EXECUTE_MINUTES"
EXECUTE_BUDGET_MINUTES = "10080"
# Claude Code's experimental code mode, on for every Claude run. A value the caller already set (for example "0" to
# switch it off) is kept.
CODE_MODE_VARIABLE = "CLAUDE_CODE_EXPERIMENTAL_CODE_MODE"
CODE_MODE_DEFAULT = "1"


class AuthRouteMissing(RuntimeError):
    """No credentials for the requested runner; the message names exactly what is missing."""


def _keychain_token() -> str:
    """The token from the OS secret store, or an empty string when there is none or the store cannot be asked."""
    argv = KEYCHAIN_LOOKUP.get(
        "darwin" if sys.platform == "darwin" else "linux" if sys.platform.startswith("linux") else ""
    )
    if argv is None:
        return ""
    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=KEYCHAIN_TIMEOUT_SECONDS,
            check=False,
            stdin=subprocess.DEVNULL,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _claude_token(environ: Mapping[str, str], secrets_dir: Path) -> str:
    """The token from the environment, then the legacy secrets file, then the OS secret store."""
    token = environ.get("CLAUDE_CODE_OAUTH_TOKEN", "").strip()
    if token:
        return token
    path = secrets_dir / TOKEN_FILE
    try:
        token = path.read_text().strip()
    except OSError:
        token = ""
    if not token:
        token = _keychain_token()
    if not token:
        raise AuthRouteMissing(
            "claude-agent needs credentials, but none were found: set HOLON_AGENT_SETTINGS, set "
            f"CLAUDE_CODE_OAUTH_TOKEN, or store the long-lived token from `claude setup-token` in the OS keychain "
            f"(service '{KEYCHAIN_SERVICE}', account '{KEYCHAIN_ACCOUNT}'). The legacy file {path} is still read "
            "when it exists."
        )
    return token


def build_flow_env(
    agent: str,
    environ: Mapping[str, str] | None = None,
    secrets_dir: Path | None = None,
) -> dict[str, str]:
    """Return the child environment for ``agent``; raise :class:`AuthRouteMissing` when it cannot authenticate."""
    env = dict(os.environ if environ is None else environ)
    env.setdefault("PYTHONUNBUFFERED", "1")
    env.setdefault("HOLON_TOKEN_REDUCE", "0")
    env.setdefault(EXECUTE_BUDGET_VARIABLE, EXECUTE_BUDGET_MINUTES)
    if agent in CLAUDE_AGENTS:
        env.setdefault(CODE_MODE_VARIABLE, CODE_MODE_DEFAULT)
    if agent in CLAUDE_AGENTS and not env.get("HOLON_AGENT_SETTINGS", "").strip():
        token = _claude_token(env, secrets_dir if secrets_dir is not None else Path.home() / ".holon" / "secrets")
        env["HOLON_AGENT_SETTINGS"] = json.dumps(
            {
                "env": {
                    "HOLON_ECHO_PAD": ECHO_PAD,
                    "CLAUDE_CODE_OAUTH_TOKEN": token,
                    CODE_MODE_VARIABLE: env[CODE_MODE_VARIABLE],
                }
            }
        )
    return env
