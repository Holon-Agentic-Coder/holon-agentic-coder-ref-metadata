#!/usr/bin/env python3
"""
prioritise_beans.py - Triage and prioritise beans across the Holon ecosystem.

Parses all bean markdown files in .beans/, excludes completed and scrapped beans,
computes progress statistics, and generates/updates the standardized Active Beans
Triage and Prioritisation Matrix in .beans/bean-triage-prioritisation.md.
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from datetime import UTC, datetime
from typing import Any


def parse_frontmatter(content: str) -> dict[str, Any]:
    """Parse YAML frontmatter using standard library regex."""
    parts = content.split("---")
    if len(parts) < 3:
        return {}
    fm_text = parts[1]
    res: dict[str, Any] = {}
    for line in fm_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([a-zA-Z0-9_-]+):\s*(.*?)\s*$", line)
        if m:
            key, val = m.group(1), m.group(2)
            # Strip quotes if any
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            res[key] = val
    return res


def extract_bean_metadata(filepath: str) -> dict[str, Any] | None:
    """Extract bean ID, frontmatter, and contextual metadata from file."""
    basename = os.path.basename(filepath)
    if basename == "template.md" or not basename.endswith(".md"):
        return None

    # Match ID: e.g. holon-agentic-coder-ref-metadata-0118--...
    m = re.search(r"(\d{4})--", basename)
    if not m:
        return None
    bean_num = m.group(1)

    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    fm = parse_frontmatter(content)
    status = fm.get("status", "todo").lower()
    priority = fm.get("priority", "normal").lower()
    title = fm.get("title", "")

    # Priority mapping
    priority_level = "P1"
    if priority == "high":
        priority_level = "P0" if int(bean_num) in (115, 118) else "P1"
    elif priority in ("normal", "medium"):
        priority_level = "P1"
    elif priority in ("low", "minor"):
        priority_level = "P2"

    # Known domain and sizing heuristics
    impact = "Medium"
    sizing = "M"
    domain = "General"
    notes = ""

    # Determine domain from tags or content
    content_lower = content.lower()
    if "holon-flow" in content_lower or "sandbox_executor" in content_lower:
        domain = "Flow / Architecture"
        impact = "High"
    elif "metrics" in content_lower or "telemetry" in content_lower:
        domain = "CLI / Telemetry"
    elif "makefile" in content_lower or "build" in content_lower:
        domain = "Build / DevEx"
    elif "license" in content_lower:
        domain = "Legal / Governance"
        impact = "Medium"
        sizing = "S"
    elif "spelling" in content_lower:
        domain = "Standards / Style"
        impact = "Low"
        sizing = "S"
    elif "audit" in content_lower:
        domain = "Architecture / Quality"
        impact = "High"
        sizing = "L"
    elif "skill" in content_lower:
        domain = "Skills / Tooling"
    elif "ledger" in content_lower or "executions.jsonl" in content_lower:
        domain = "Ledger / Observability"
        impact = "High"

    # Extract summary sentence for notes if available (with fallback to ## Context)
    summary_m = re.search(r"## Summary\s*\n+([^\n#]+)", content)
    if not summary_m:
        summary_m = re.search(r"## Context\s*\n+([^\n#]+)", content)
    if summary_m:
        notes = summary_m.group(1).strip()
        # Truncate if too long for clean table display
        if len(notes) > 130:
            notes = notes[:127].rsplit(" ", 1)[0] + "..."

    return {
        "bean_num": bean_num,
        "title": title,
        "status": status,
        "priority_raw": priority,
        "priority_level": priority_level,
        "impact": impact,
        "sizing": sizing,
        "domain": domain,
        "notes": notes,
        "filepath": filepath,
    }


def read_previous_checkpoint(output_path: str) -> str | None:
    """Read the ``**Last Updated:**`` date from an existing triage document, if present."""
    try:
        with open(output_path, encoding="utf-8") as f:
            head = f.read(4096)
    except OSError:
        return None
    m = re.search(r"\*\*Last Updated:\*\*\s*(\d{4}-\d{2}-\d{2})", head)
    return m.group(1) if m else None


def scan_beans(beans_dir: str) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Scan all beans in directory, returning active list and count statistics."""
    files = sorted(glob.glob(os.path.join(beans_dir, "holon-agentic-coder-ref-metadata-*.md")))
    total_tracked = 0
    completed_count = 0
    scrapped_count = 0
    active_beans: list[dict[str, Any]] = []

    # Map of custom manual overrides for existing active beans to preserve triage depth
    overrides = {
        "0129": {
            "priority": "**P1**",
            "impact": "Medium",
            "sizing": "M",
            "domain": "CLI / Telemetry",
            "notes": (
                "Exposes the plain mitmweb inspection UI by default in holon-coherence start with port "
                "fallback, and prints every endpoint (proxy, Coherence dashboard, mitmweb + token) from "
                "status, metrics and holon flow --token-reduce."
            ),
        },
        "0132": {
            "priority": "**P1**",
            "impact": "High",
            "sizing": "M",
            "domain": "Ledger / Provenance",
            "notes": (
                "Stage 4/5 never append ACT-REV/ACT-FIND/ACT-POST in holon-coherence (0 matches vs 159 in "
                "holon-agentic-coder); fix the writer or correct AGENTS.md rule 14. No backfill."
            ),
        },
        "0133": {
            "priority": "**P2**",
            "impact": "Low",
            "sizing": "S",
            "domain": "CLI / Reliability",
            "notes": (
                "wait_for_proxy_ready() bounds its poll with a wall-clock time.time() deadline while sibling "
                "loops use time.monotonic(); NTP slew can stall or short-circuit cold-start readiness."
            ),
        },
        "0116": {
            "priority": "**P1**",
            "impact": "Medium",
            "sizing": "M",
            "domain": "Build / DevEx",
            "notes": (
                "Adds bidirectional build-image / build-images aliases and ports tools "
                "and lint-* targets to holon-coherence."
            ),
        },
        "0113": {
            "priority": "**P1**",
            "impact": "High",
            "sizing": "M",
            "domain": "Ledger / Observability",
            "notes": (
                "Extends flow engine and review loop to append discrete actions and "
                "PR review/resolver events to executions.jsonl."
            ),
        },
        "0119": {
            "priority": "**P1**",
            "impact": "High",
            "sizing": "S",
            "domain": "Flow / PR Review",
            "notes": (
                "Posts consensus to gh pr comment for conversation visibility; handles "
                "GitHub author self-approval restrictions gracefully."
            ),
        },
        "0120": {
            "priority": "**P1**",
            "impact": "Medium",
            "sizing": "S",
            "domain": "Skills / Automation",
            "notes": "Generates and maintains active beans triage matrix in .beans/, filtering completed beans.",
        },
        "0121": {
            "priority": "**P1**",
            "impact": "High",
            "sizing": "M",
            "domain": "Flow / Concurrency",
            "notes": "Proactive conflict detection and automated resolution across all 5 Holon flow stages.",
        },
        "0104": {
            "priority": "**P1**",
            "impact": "Medium",
            "sizing": "S",
            "domain": "Legal / Governance",
            "notes": (
                "Standardised in holon-agentic-coder (PR #79); outstanding task: add LICENSE to metadata repository."
            ),
        },
        "0105": {
            "priority": "**P1**",
            "impact": "Low",
            "sizing": "S",
            "domain": "Standards / Style",
            "notes": "Standardised in holon-agentic-coder (PR #79); ongoing enforcement across ecosystem docs.",
        },
        "0106": {
            "priority": "**P1**",
            "impact": "High",
            "sizing": "L",
            "domain": "Architecture / Quality",
            "notes": (
                "Holistic multi-dimensional audit of architecture, hermeticity, error handling, and test boundaries."
            ),
        },
        "0107": {
            "priority": "**P1**",
            "impact": "Medium",
            "sizing": "S",
            "domain": "CI / Testing",
            "notes": (
                "Integrates pytest tests/ and ruff check into GitHub Actions for holon-agentic-coder-ref-metadata."
            ),
        },
        "0110": {
            "priority": "**P1**",
            "impact": "High",
            "sizing": "M",
            "domain": "Security / Git Hooks",
            "notes": "Prevents API keys (Google AI, GitHub PATs) and ephemeral scratch paths from being staged.",
        },
        "0111": {
            "priority": "**P2**",
            "impact": "Medium",
            "sizing": "M",
            "domain": "Documentation / DevEx",
            "notes": "Slims root README.md to under 60-second read; moves deep specs to docs/architecture-overview.md.",
        },
        "0108": {
            "priority": "**P2**",
            "impact": "Low",
            "sizing": "S",
            "domain": "Hygiene / Tooling",
            "notes": "Relocates completed PR review intermediates into _archive/ with 30-day retention pruning.",
        },
        "0109": {
            "priority": "**P2**",
            "impact": "Medium",
            "sizing": "M",
            "domain": "Flow / Automation",
            "notes": (
                "Auto-generates conventional titles (feat(...), fix(...)) and rich Markdown "
                "descriptions from flow intent/plan metadata."
            ),
        },
    }

    for fpath in files:
        b = extract_bean_metadata(fpath)
        if not b:
            continue
        total_tracked += 1
        status = b["status"]
        if status in ("completed", "done"):
            completed_count += 1
        elif status == "scrapped":
            scrapped_count += 1
        else:
            # Active bean (todo, in-progress, draft)
            bnum = b["bean_num"]
            if bnum in overrides:
                ov = overrides[bnum]
                b["priority_display"] = ov["priority"]
                b["impact"] = ov["impact"]
                b["sizing"] = ov["sizing"]
                b["domain"] = ov["domain"]
                b["notes"] = ov["notes"]
            else:
                b["priority_display"] = f"**{b['priority_level']}**"
            active_beans.append(b)

    # Sort active beans: P0 -> P1 -> P2 -> P3, then by bean number descending
    priority_order = {"**P0**": 0, "**P1**": 1, "**P2**": 2, "**P3**": 3}
    active_beans.sort(key=lambda x: (priority_order.get(x["priority_display"], 9), -int(x["bean_num"])))

    stats = {
        "total_tracked": total_tracked,
        "completed": completed_count,
        "scrapped": scrapped_count,
        "active": len(active_beans),
    }
    return active_beans, stats


def generate_triage_document(
    active_beans: list[dict[str, Any]],
    stats: dict[str, int],
    date_str: str,
    timestamp_str: str | None = None,
    previous_checkpoint: str | None = None,
) -> str:
    """Generate Markdown document adhering strictly to the ecosystem triage format."""
    total = stats["total_tracked"]
    completed = stats["completed"]
    scrapped = stats["scrapped"]
    active = stats["active"]

    completed_pct = (completed / total * 100) if total else 0
    scrapped_pct = (scrapped / total * 100) if total else 0
    active_pct = (active / total * 100) if total else 0

    ts = timestamp_str or datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines: list[str] = [
        "# Holon Ecosystem Bean Triage and Prioritisation Matrix",
        "",
        f"**Last Updated:** {ts}",
        "",
        "## Executive Summary",
        "",
        (
            f"Since the previous triage checkpoint on {previous_checkpoint}, the Holon ecosystem has progressed "
            "through automated Holon flow cycles, multi-agent consensus review loops, and infrastructure hardening."
            if previous_checkpoint
            else (
                "As of this checkpoint, the Holon ecosystem has progressed through automated Holon flow cycles, "
                "multi-agent consensus review loops, and infrastructure hardening."
            )
        ),
        "",
        f"- **Total Tracked Beans**: {total} (excluding template)",
        f"- **Completed**: {completed} ({completed_pct:.1f}%)",
        f"- **Scrapped / Superseded**: {scrapped} ({scrapped_pct:.1f}%)",
        f"- **Active / Todo**: {active} ({active_pct:.1f}%)",
        "",
        "---",
        "",
        "## Key Milestones Completed (Beans 0080 – 0131)",
        "",
        "1. **Holon Flow and Automation Engine**:",
        "   - `0084`: Fixed CI check name collisions in review gates.",
        "   - `0087`: Permitted autonomous PR creation in Holon flow stage 3.",
        "   - `0089`: Auto-routed all flow stages through Holon Coherence proxy for token deduplication and caching.",
        "   - `0093`: Atomic ledger locking with exponential backoff and `flock`.",
        "   - `0094`: Checkpoint schema versioning and automated state migration.",
        "2. **Action Knowledge Base and Wisdom (Bean 0052 / PR #78)**:",
        (
            "   - Full integration of the SQLite FTS5 inverted index over the canonical `executions.jsonl` ledger "
            "(the auxiliary `actions.jsonl` was later retired by Bean 0123)."
        ),
        "   - Pre-action wisdom consult (`holon consult`) across intent, planning, execution, and review stages.",
        "   - Statistical Wilson score promotion ladder and deterministic failure veto engine.",
        "3. **Multi-Agent Review Loop and Hygiene (PR #52)**:",
        "   - `0099`: Write-capable children and nested Prettier formatting guards.",
        (
            "   - `0103`: Implemented `clean-workspace` skill and Python automation (`clean_workspace.py`) "
            "covering worktrees, branches, orphan directories, `.subagent/` review caches, and `todo/` scratchpads."
        ),
        "   - Passed 100% unanimous 3/3 ensemble consensus approval on PR #52.",
        "4. **Agent Container Modernisation and Buildx Bake Integration (Beans 0112 and 0114 / PR #80)**:",
        (
            "   - Upgraded all container images (`@anthropic-ai/claude-code@2.1.302`, `@openai/codex@0.163.0`, "
            "`@google/gemini-cli@0.64.0`, `opencode-ai@1.19.3`, `@earendil-works/pi-coding-agent@1.3.0`)."
        ),
        "   - Added hardened writable tmpfs overlays for Antigravity and Codex session logs and caches.",
        "   - Fully automated Buildx Bake builds across all 8 role/orchestrator images with layer caching.",
        "5. **Ecosystem Build and Installation Automation (Bean 0117)**:",
        (
            "   - Implemented `install-holon` and `install-coherence` skills (`.agents/skills/install_holon/SKILL.md`, "
            "`.agents/skills/install_coherence/SKILL.md`) and companion Python orchestrators (`install_holon.py`, "
            "`install_coherence.py`)."
        ),
        (
            "   - Automates building Docker images via Buildx Bake and installing/updating `holon` and "
            "`holon-coherence` via `uv tool install`."
        ),
        "6. **Native Review Loop and Metrics Alignment (Beans 0115 and 0118 / PR #23 & PR #81)**:",
        (
            "   - `0115`: Stripped all emojis from `holon-coherence metrics` terminal table and aligned colon "
            "spacing at column 31. Raised PR #23 on `holon-coherence`, passed 3-agent ensemble review."
        ),
        (
            "   - `0118`: Implemented explicit native `holon review-loop` CLI step (Stage 4) in `holon-agentic-coder`. "
            "Raised PR #81, resolved findings in iteration 1, passed 3-agent ensemble review, "
            "and completed Stage 5 calibration."
        ),
        (
            "7. **Makefile Alignment, PR Metadata, and Ledger Enhancements (Beans 0116, 0113, 0119, 0109 / "
            "PR #25 & PR #82)**:"
        ),
        (
            "   - `0116`: Added `build-images` alias, `tools`, and `lint` targets in `holon-coherence` (PR #25); "
            "added `build-image` alias in `holon-agentic-coder` (PR #82)."
        ),
        (
            "   - `0109`: Automated conventional commit PR titles (`feat(...)`, `fix(...)`) and structured Markdown "
            "bodies with Summary, Changes, and Beans."
        ),
        (
            "   - `0119`: Dual-posting review consensus (top-level comment + official review) with HTTP 422 author "
            "self-approval fallback."
        ),
        (
            "   - `0113`: Granular action logging in `executions.jsonl` recording evaluations, findings, resolver "
            "triggers, and consensus posting."
        ),
        ("8. **Decoupled Architecture and Canonical 3-Ledger Consolidation (Beans 0122 and 0123 / PR #85)**:"),
        ("   - Purged all harness-specific metadata paths (`.beans/`, `todo/`, `.agents/`) from target repositories."),
        (
            "   - Retired auxiliary `actions.jsonl` ledger; interleaved all discrete micro-actions "
            "(`entry_type: 'action'`) "
            "and run summaries (`entry_type: 'summary'`) inside `executions.jsonl` under `LedgerLock`."
        ),
        (
            "   - Codified harness isolation, test execution constraints (strictly `uv run pytest`), "
            "and ledger invariants "
            "across ecosystem instructions."
        ),
        ("9. **Unified Git Abstraction, Unprivileged Containers, and Hardened Locking (Beans 0124 – 0127 / PR #86)**:"),
        (
            "   - `0124`: Implemented unified Git abstraction in `sandbox_executor.git` with custom "
            "exceptions and strict stderr diagnostics."
        ),
        ("   - `0125`: Australian English spelling hygiene across documentation and codebase comments."),
        ("   - `0126`: Enforced unprivileged Docker execution via `--cap-drop=ALL` with selective capability drops."),
        ("   - `0127`: Hardened `LedgerLock` concurrency file locking with exponential backoff and timeouts."),
        (
            "10. **Documentation Gap Remediation and Container `gh` Availability (Beans 0128 and 0131 / PR #87 & "
            "PR #88)**:"
        ),
        (
            "    - `0128`: Closed documentation drift across `holon-agentic-coder` (PR #87) and the harness, so flow "
            "stage, ledger, and worktree instructions match the implemented behaviour."
        ),
        (
            "    - `0131`: Installed the GitHub CLI into `holon-base` so every agent image and the Stage 4 review-loop "
            "container can post consensus reviews, plus container availability tests (PR #88, Stage 5 calibrated)."
        ),
        ("11. **Proxy Cold-Start Readiness and Agent Runner Tests (Bean 0130 / holon-coherence PR #26)**:"),
        (
            "    - Replaced the fixed-sleep readiness probe with HTTP readiness polling, deduplicated the proxy "
            "`chmod` handling, routed readiness probes around the proxy, and added agent runner integration tests."
        ),
        (
            "    - Traversed all 5 Holon flow stages and passed unanimous 3/3 ensemble consensus at iteration 4; "
            "residual nits were deferred to Beans 0132 and 0133 instead of being dropped."
        ),
        "",
        "---",
        "",
        "## Active Beans Triage and Prioritisation Matrix",
        "",
        "| Priority | Status | Impact | Sizing | Bean # | Title | Domain | Dependencies / Notes |",
        "| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- |",
    ]

    for b in active_beans:
        row = (
            f"| {b['priority_display']} | {b['status']} | {b['impact']} | {b['sizing']} "
            f"| {b['bean_num']} | {b['title']} | {b['domain']} | {b['notes']} |"
        )
        lines.append(row)

    lines.extend(
        [
            "",
            "---",
            "",
            "## Recommended Next Execution Sequence",
            "",
        ]
    )
    if not active_beans:
        total = stats.get("total_tracked", 0)
        lines.extend(
            [
                (
                    f"All tracked beans in the active backlog (Beans 0001 – {total:04d}) have been completed "
                    "across all managed repositories:"
                ),
                "",
                (
                    "- `holon-agentic-coder` and `holon-coherence`: the most recent flow pull requests have traversed "
                    "all 5 Holon flow stages (Stage 4 consensus APPROVED, Stage 5 calibration report included in the "
                    "PR diff); see the Key Milestones section above for the current PR numbers."
                ),
                (
                    f"- `holon-agentic-coder-ref-metadata`: All beans up to Bean {total:04d} are "
                    "finalised and marked completed."
                ),
                "",
                (
                    "The ecosystem backlog is empty and any open pull request awaits manual human maintainer review "
                    "and merge; agents never merge (AGENTS.md, PR Merging — Human-Only)."
                ),
                "",
            ]
        )
    else:
        for i, b in enumerate(active_beans[:5], 1):
            lines.append(f"{i}. **{b['title']} (Bean {b['bean_num']})**:")
            if b.get("notes") and b["notes"].strip():
                lines.append(f"   - {b['notes'].strip()}")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Triage and prioritise beans across the Holon ecosystem.")
    parser.add_argument("--beans-dir", default=".beans", help="Path to .beans/ directory")
    parser.add_argument("--output", help="Explicit output file path")
    parser.add_argument("--date", help="Date string for title and filename (defaults to current date)")
    parser.add_argument("--dry-run", action="store_true", help="Print output to stdout without writing to disk")
    args = parser.parse_args()

    date_str = args.date or datetime.now(UTC).strftime("%Y-%m-%d")
    active_beans, stats = scan_beans(args.beans_dir)

    prior_output = args.output or os.path.join(args.beans_dir, "bean-triage-prioritisation.md")
    doc = generate_triage_document(
        active_beans, stats, date_str, previous_checkpoint=read_previous_checkpoint(prior_output)
    )

    if args.dry_run:
        print(doc)
        return 0

    output_path = args.output or os.path.join(args.beans_dir, "bean-triage-prioritisation.md")
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(doc)

    print(f"✅ Generated triage document with {len(active_beans)} active beans at: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
