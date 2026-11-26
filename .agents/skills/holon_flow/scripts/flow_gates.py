"""Refusals for flags and intents that only the maintainer may authorise."""

from __future__ import annotations

import hmac
import os
from collections.abc import Mapping
from pathlib import Path

AUTH_ENV = "HOLON_MAINTAINER_AUTH"
AUTH_TOKEN_FILE = Path(".config") / "holon-maintainer" / "auth-token"
BUDGET_FILE = "module_budgets.json"
NEVER_ALLOWED = ("skip_review",)
MAINTAINER_ONLY = ("skip_preflight", "allow_overlap")


def maintainer_authorised(environ: Mapping[str, str] | None = None, home: Path | None = None) -> bool:
    environ = os.environ if environ is None else environ
    offered = environ.get(AUTH_ENV, "").strip()
    token_file = (home or Path.home()) / AUTH_TOKEN_FILE
    if not offered or not token_file.is_file():
        return False
    expected = token_file.read_text(encoding="utf-8").strip()
    return bool(expected) and hmac.compare_digest(offered.encode(), expected.encode())


def forbidden_flag_refusal(
    flags: Mapping[str, bool], environ: Mapping[str, str] | None = None, home: Path | None = None
) -> str | None:
    for name in NEVER_ALLOWED:
        if flags.get(name):
            return f"--{name.replace('_', '-')} is never allowed: a failing review halts the flow and is reported."
    requested = [name for name in MAINTAINER_ONLY if flags.get(name)]
    if requested and not maintainer_authorised(environ, home):
        names = ", ".join("--" + name.replace("_", "-") for name in requested)
        return f"{names} needs maintainer authorisation ({AUTH_ENV} matching the token in ~/{AUTH_TOKEN_FILE})."
    return None


def budget_change_refusal(intent: Mapping[str, object]) -> str | None:
    touches_budgets = BUDGET_FILE in str(intent.get("scope", []))
    if touches_budgets and not str(intent.get("module_budget_change", "")).strip():
        return (
            f"Intent scope touches {BUDGET_FILE} without a module_budget_change field; only the maintainer's quoted "
            "instruction may be written there, agents never author it."
        )
    return None
