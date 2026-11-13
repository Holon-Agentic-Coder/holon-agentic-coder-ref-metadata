"""The environment a `holon flow` child process needs, built from the secrets file so no one exports it by hand.

A `claude-agent` container gets credentials only through `HOLON_AGENT_SETTINGS`: a JSON object whose `env` carries the
OAuth token, plus an echo pad that keeps the token past the planner (100 character) and executor (250 character) echo
truncation. A shell without it starts every Claude role container with no credentials, and the Stage 4 reviewers then
exit with code 1 within seconds. The token is read, placed in the child's environment and never printed or logged.
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from pathlib import Path

TOKEN_FILE = "claude-oauth-token"
ECHO_PAD = "x" * 300
CLAUDE_AGENTS = ("claude-agent",)


class AuthRouteMissing(RuntimeError):
    """No credentials for the requested runner; the message names exactly what is missing."""


def _claude_token(environ: Mapping[str, str], secrets_dir: Path) -> str:
    token = environ.get("CLAUDE_CODE_OAUTH_TOKEN", "").strip()
    if token:
        return token
    path = secrets_dir / TOKEN_FILE
    try:
        token = path.read_text().strip()
    except OSError:
        token = ""
    if not token:
        raise AuthRouteMissing(
            f"claude-agent needs credentials, but none were found: set HOLON_AGENT_SETTINGS, set "
            f"CLAUDE_CODE_OAUTH_TOKEN, or put the long-lived token in {path} (mode 600, from `claude setup-token`)."
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
    if agent in CLAUDE_AGENTS and not env.get("HOLON_AGENT_SETTINGS", "").strip():
        token = _claude_token(env, secrets_dir if secrets_dir is not None else Path.home() / ".holon" / "secrets")
        env["HOLON_AGENT_SETTINGS"] = json.dumps(
            {"env": {"HOLON_ECHO_PAD": ECHO_PAD, "CLAUDE_CODE_OAUTH_TOKEN": token}}
        )
    return env
