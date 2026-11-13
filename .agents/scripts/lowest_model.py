#!/usr/bin/env python3
"""Probe a harness for the lowest-tier model it offers right now.

The mapping from "lowest tier" to a model changes as each harness ships models, so nothing here names a model. The
harness is asked what it offers (``agy models``, ``holon models --json``, or a list the caller read from its own
tool), and each model is ranked by generic size markers in its name (``nano``, ``lite``, ``flash``, ``haiku``, ...)
and then by effort suffix (``low`` before ``high``). A model whose name carries no marker is listed as unranked and is
never chosen as the lowest, so an opaque codename cannot be picked by accident.

    lowest_model.py --probe antigravity
    lowest_model.py --probe holon --runner claude-agent
    lowest_model.py --candidates haiku,sonnet,opus      # Claude Code: the Agent tool's own model options

Prints JSON with ``lowest``, the full ``ranked`` list and the ``unranked`` ones. Exit 0 with a model, 1 when the
probe fails or nothing could be ranked (the caller then runs inline on its active model and says so).
"""

import argparse
import json
import re
import subprocess
import sys

# Generic size markers, smallest first. Matching is on name tokens, never on a full model name or version.
FAMILY_RANKS = (
    ("nano", "tiny", "lite", "mini"),
    ("flash", "haiku", "small"),
    ("sonnet",),
    ("pro", "opus", "ultra", "large", "fable"),
)
EFFORT_RANKS = ("minimal", "low", "medium", "high", "xhigh")


def tokens(name: str) -> list[str]:
    return [t for t in re.split(r"[^a-z0-9]+", name.lower()) if t]


def family_rank(name: str) -> int | None:
    parts = tokens(name)
    for rank, markers in enumerate(FAMILY_RANKS):
        if any(marker in parts for marker in markers):
            return rank
    return None


def effort_rank(name: str) -> int:
    parts = tokens(name)
    for rank, effort in enumerate(EFFORT_RANKS):
        if effort in parts:
            return rank
    return len(EFFORT_RANKS)


def rank(models: list[str]) -> dict:
    ranked = [(family_rank(m), effort_rank(m), m) for m in models]
    usable = sorted((r for r in ranked if r[0] is not None), key=lambda r: (r[0], r[1], r[2]))
    return {
        "lowest": usable[0][2] if usable else None,
        "ranked": [{"model": m, "family_rank": f, "effort_rank": e} for f, e, m in usable],
        "unranked": sorted(m for f, e, m in ranked if f is None),
    }


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} exited {result.returncode}: {result.stderr.strip()[:200]}")
    return result.stdout


def probe_antigravity() -> list[str]:
    """``agy models`` prints ``<id>\\t<display name>`` per line after a status line."""
    return [line.split("\t")[0] for line in run(["agy", "models"]).splitlines() if "\t" in line]


def probe_holon(runner: str | None) -> list[str]:
    cmd = ["holon", "models", "--json"] + (["--agent", runner] if runner else [])
    return sorted({entry["canonical_model"] for entry in json.loads(run(cmd))})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--probe", choices=("antigravity", "holon"), help="ask this harness what it offers")
    source.add_argument("--candidates", help="comma-separated models the caller read from its own harness")
    parser.add_argument("--runner", help="with --probe holon: restrict to one runner, e.g. claude-agent")
    args = parser.parse_args()
    try:
        if args.candidates:
            models = [m.strip() for m in args.candidates.split(",") if m.strip()]
        elif args.probe == "antigravity":
            models = probe_antigravity()
        else:
            models = probe_holon(args.runner)
    except (OSError, RuntimeError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"lowest": None, "error": str(error)}))
        return 1
    result = rank(models)
    print(json.dumps(result, indent=2))
    return 0 if result["lowest"] else 1


if __name__ == "__main__":
    sys.exit(main())
