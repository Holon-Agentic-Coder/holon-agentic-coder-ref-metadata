#!/usr/bin/env python3
"""
prioritise_beans.py - Triage and prioritise beans across the Holon ecosystem.

Parses all bean markdown files in .beans/, excludes completed and scrapped beans,
computes progress statistics, and generates/updates the standardized Active Beans
Triage and Prioritisation Matrix in .beans/bean-triage-prioritisation.md.

The Executive Summary narrative, the Key Milestones Completed items, the
Recommended Next Execution Sequence, and the per-bean triage overrides are
carried as inline data below. Per the skill's "Generator Maintenance" rule,
every run MUST refresh them so the generated document and the committed
document never diverge. Prose is stored unwrapped; the post-generation
`npx prettier --write` pass (proseWrap: always, printWidth 120) produces the
canonical hard-wrapped form.
"""

from __future__ import annotations

import argparse
import glob
import os
import re
import sys
from datetime import UTC, datetime
from typing import Any

# Narrative lead-in of the Executive Summary (before the statistics bullets).
# Inline data: update it at every checkpoint. When empty, a generic lead-in
# built from the previous checkpoint date is used instead.
EXECUTIVE_SUMMARY_NARRATIVE: list[str] = [
    (
        "Since the 2026-10-22 checkpoint, every bean that was active then and blocked on a runner has gone through "
        "the full 5-stage Holon flow and been merged by the maintainer:"
    ),
    "",
    "- holon-agentic-coder PRs #90, #91, #93, #94, #95 and #96",
    "- holon-coherence PR #27",
    "",
    (
        "Concurrent flows on overlapping files (#94, #95 and #96 all changed `flow.py` and `cli.py`) forced repeated "
        "syncs and re-reviews: 141 review-loop passes from the first sync onward, about 10M+ tokens. Beans 0151 and "
        "0152 address that, and overlapping flows now run one after another."
    ),
]

# Closing paragraph(s) of the Executive Summary (after the statistics bullets).
EXECUTIVE_SUMMARY_UPDATE: list[str] = [
    (
        "**2026-10-26:** the first full claude-agent `holon flow` runs (Beans 0151, 0159) exposed seven defects in "
        "the flow itself. They are logged as Beans 0157-0162, and Bean 0144 was raised to critical after its "
        "fabricated approval reached GitHub. Bean 0156 starts the investigation into moving issue tracking from "
        "harness beans to beads inside each target, ahead of deprecating this harness."
    ),
]

MILESTONES_HEADING = "## Key Milestones Completed (Beans 0080 – 0140)"

# Hand-authored replacement for the generated "Recommended Next Execution
# Sequence" section, used whenever active beans exist. Inline data: keep it in
# step with the matrix at every checkpoint.
NEXT_EXECUTION_SEQUENCE: list[str] = [
    (
        "**Rule (2026-10-25):** never run concurrent flows whose touched files overlap. Nearly every "
        "holon-agentic-coder bean touches `flow.py` or `cli.py`, so those flows run **one at a time**: merge one, "
        "then plan the next on the new `main`. Only disjoint work runs in parallel. Bean 0151 will make the flow "
        "enforce this; Bean 0152 will bring back parallelism."
    ),
    "",
    (
        "**Rule (2026-10-26):** no stage before the merge may halt for human review. The PR merge is the only human "
        "step, after consensus review and Stage 5 calibration."
    ),
    "",
    (
        "**Tooling (2026-10-26):** the installed `holon` and `holon/agent-claude:latest` are built from "
        "`fix/0143-claude-runner-skip-permissions` (rebased on `main` `e3bbd67`), not from `main`. Once 0143 and "
        "0159 are merged, reinstall `holon` and rebuild every image from `main`. Until 0157, 0158, 0160 and 0144 "
        "land, run flows with `HOLON_TOKEN_REDUCE=0`, restore `intents.jsonl` before Stage 4, wait for CI before "
        "resuming review, and run Stage 4 through the harness `pr-review-loop` skill."
    ),
    "",
    "Sequential lane, holon-agentic-coder (flow blockers first):",
    "",
    "1. **Bean 0159** (PR #97): finish the review loop, re-calibrate on the final head, then the maintainer merges.",
    "2. **Bean 0143**: the maintainer raises and merges the PR. Reinstall `holon` and rebuild images from `main`.",
    "3. **Bean 0144**: real reviewer containers for Stage 4. This removes the harness review dependency.",
    (
        "4. **Bean 0158**, **Bean 0160**, **Bean 0162**, **Bean 0157**: the remaining flow-integrity blockers, one "
        "at a time (all touch `flow.py`)."
    ),
    "5. **Bean 0149**, then **Bean 0151**: unique IDs, then touch-set admission. Re-plan 0151 on the new `main`.",
    "6. **Bean 0161**: decomposed-child chaining and the parent PR.",
    "7. **Bean 0155**, then **Bean 0148**: credential-redaction gaps (both touch `cli.py`).",
    "8. **Bean 0146**: calibration reads the correct predicted metrics.",
    "9. **Bean 0152**, then **Bean 0153**: decomposition and module split, then self-documenting code.",
    "",
    "Parallel lane (disjoint files):",
    "",
    "- **Bean 0163** (CI timing gate, workflows only, one flow per repository).",
    (
        "- **Bean 0156** (beads investigation, no target code). Its outcome decides how 0147 and the harness "
        "retirement proceed."
    ),
    "- **Bean 0145** (holon-coherence) and the holon-coherence half of **Bean 0147**.",
    "- **Bean 0154** and **Bean 0150** (tests only). Check their touch sets against the lane above first.",
    "- **Beans 0142 and 0141** (benchmarking and tuning, no code flow).",
]

# Manual triage overrides for every active bean: display title, priority,
# impact, sizing, domain and notes, so each matrix cell reads as a triage
# judgement rather than a truncated first paragraph. Insertion order is the
# matrix row order (priority blocks, hand-curated within each block).
OVERRIDES: dict[str, dict[str, str]] = {
    "0159": {
        "title": "Executor honours the intent entropy budget; no fabricated sub-intents; no Stage 3 halt",
        "priority": "**P0**",
        "impact": "High",
        "sizing": "M",
        "domain": "Holon Flow / Executor",
        "notes": (
            "PR #97 in the harness review loop (iteration 9, head `c479dd4`). Unblocks 0151. Merge, then reinstall "
            "from `main`."
        ),
    },
    "0144": {
        "title": "Review loop runs no reviewer and posts a fabricated ensemble approval",
        "priority": "**P0**",
        "impact": "High",
        "sizing": "L",
        "domain": "Review Loop",
        "notes": (
            "Reached GitHub on #97. Real reviewer containers needed. Until then Stage 4 runs through the harness "
            "`pr-review-loop` skill."
        ),
    },
    "0158": {
        "title": "A flow run reorders existing rows of the append-only `intents.jsonl`",
        "priority": "**P0**",
        "impact": "High",
        "sizing": "S",
        "domain": "Ledger / Holon Flow",
        "notes": (
            "Breaks Stage 4 checkout on every unattended run. Workaround: `git restore` the file, then "
            "`--from-stage review`."
        ),
    },
    "0160": {
        "title": "Review loop burns its iteration budget polling pending CI, then reports test failures",
        "priority": "**P0**",
        "impact": "High",
        "sizing": "S",
        "domain": "Review Loop / CI",
        "notes": "Every unattended Stage 4 runs out of iterations before review. Workaround: wait for CI, then resume.",
    },
    "0151": {
        "title": "Planner estimates the touch set; overlapping concurrent flows are blocked",
        "priority": "**P0**",
        "impact": "High",
        "sizing": "L",
        "domain": "Holon Flow / Concurrency",
        "notes": (
            "Plan `P-1792988757` exists. Blocked by 0159; re-plan on the new `main`. Wants 0149 for reliable "
            "in-flight IDs."
        ),
    },
    "0143": {
        "title": "Claude runner passes the permission bypass as CLI parameters",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "S",
        "domain": "Agent Runner",
        "notes": (
            "Rebased (`e7149a9`), pushed, no PR yet. All claude-agent flows currently run on this build. "
            "Maintainer's PR and merge."
        ),
    },
    "0162": {
        "title": "Stage 5 calibration commits a report that fails the `hygiene` Prettier check",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "S",
        "domain": "Calibration / CI",
        "notes": "Turns every flow PR red after calibration.",
    },
    "0157": {
        "title": "`holon flow` auto-enables the mitmproxy sidecar; role containers cannot reach it",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "S",
        "domain": "Holon Flow / Proxy",
        "notes": "Workaround: `HOLON_TOKEN_REDUCE=0`. Related to 0130.",
    },
    "0161": {
        "title": "Decomposed sub-intents have no flow path to `main` and do not build on each other",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "M",
        "domain": "Holon Flow",
        "notes": "Deferred from #97 (F2(b) plus resume safety F4). After 0159.",
    },
    "0149": {
        "title": "Plan and execution IDs collide across concurrently planned intents",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "M",
        "domain": "Provenance / Planner",
        "notes": "#91 and #92 shared `P-1792765112`. Prerequisite for 0151.",
    },
    "0155": {
        "title": "General `HOLON_*` forwarding puts credential-shaped values on the docker argv",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "M",
        "domain": "Security",
        "notes": "Already on main. Default fix: send every `HOLON_*` value through the 0600 env-file.",
    },
    "0148": {
        "title": "Redact before truncating ledger `error_context`; close `CredentialRedactor` gaps",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "M",
        "domain": "Security / Ledger",
        "notes": "Route those rows through `redact_agent_secrets`.",
    },
    "0146": {
        "title": "Plans-ledger correction rows; calibration picks the right predicted metrics",
        "priority": "**P1**",
        "impact": "Medium",
        "sizing": "M",
        "domain": "Calibration / Ledger",
        "notes": "Every calibration last cycle needed a manual annotation (7 PRs).",
    },
    "0156": {
        "title": "Investigate moving issue tracking from harness beans to beads inside each target",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "L",
        "domain": "Issue Tracking",
        "notes": (
            "Investigation only, no target code. Can run in parallel with any flow. Precedes deprecating the harness."
        ),
    },
    "0163": {
        "title": "CI timing regression gate: fail builds whose duration regresses beyond a tolerance",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "M",
        "domain": "CI / Performance",
        "notes": (
            "macOS unit already over 10 min on `main` (662 s). Baseline on a rolling median; same code varies "
            "about ±20%. Both repos."
        ),
    },
    "0152": {
        "title": "Audit long files; decompose oversized functions (flow.py, cli.py first)",
        "priority": "**P1**",
        "impact": "High",
        "sizing": "XL",
        "domain": "Refactor / Concurrency",
        "notes": "`cli.main` is 1062 lines; `flow.py` is 4400+. Run only while no other flow touches those files.",
    },
    "0154": {
        "title": "Fix the flaky URL fuzz leak check that can match temp-file names",
        "priority": "**P1**",
        "impact": "Medium",
        "sizing": "S",
        "domain": "Tests",
        "notes": (
            "Turned #97's macOS CI red on 2026-10-26 (second occurrence). Tests only; parallel with flows that "
            "don't touch the fuzz test."
        ),
    },
    "0153": {
        "title": "Remove comments and docstrings from all code; make it self-documenting",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "XL",
        "domain": "Readability",
        "notes": "Runs with or after 0152.",
    },
    "0147": {
        "title": "Remove harness paths tracked in the target repositories",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "S",
        "domain": "Hygiene",
        "notes": (
            "One flow per repository. The coherence part can run in parallel. Fold into 0156's plan if "
            "beads lands first."
        ),
    },
    "0150": {
        "title": "Flow tests write the real checkout's `action_index.db`",
        "priority": "**P2**",
        "impact": "Low",
        "sizing": "S",
        "domain": "Tests",
        "notes": "Unblocked.",
    },
    "0145": {
        "title": "Pin holon-coherence to Python 3.13",
        "priority": "**P2**",
        "impact": "Medium",
        "sizing": "S",
        "domain": "Build / coherence",
        "notes": "coherence only; parallel with holon-agentic-coder flows.",
    },
    "0142": {
        "title": "Real-workload benchmark: Qwen3.8-27B dense vs Flash-Next MoE",
        "priority": "**P2**",
        "impact": "High",
        "sizing": "L",
        "domain": "Model Selection",
        "notes": "Real data only (AGENTS.md item 10).",
    },
    "0141": {
        "title": "Tune vmlx prefill/decode levers for both Qwen3.8 models, crash-safe",
        "priority": "**P3**",
        "impact": "Medium",
        "sizing": "M",
        "domain": "vmlx / Performance",
        "notes": "Pairs with 0142.",
    },
}


def parse_frontmatter(content: str) -> dict[str, Any]:
    """Parse YAML frontmatter using standard library regex.

    Supports plain single-line scalars and quoted scalars folded onto the
    following indented line(s), e.g.::

        title:
          "A long title that continues
          on the next line"
    """
    parts = content.split("---")
    if len(parts) < 3:
        return {}
    fm_text = parts[1]
    res: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in fm_text.splitlines():
        if raw_line[:1] in (" ", "\t") and current_key is not None:
            cont = raw_line.strip()
            if not cont or cont.startswith("- "):
                # Blank line or list item: not a scalar continuation.
                current_key = None
                continue
            prev = res[current_key]
            res[current_key] = f"{prev} {cont}" if prev else cont
            continue
        current_key = None
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([a-zA-Z0-9_-]+):\s*(.*?)\s*$", line)
        if m:
            key, val = m.group(1), m.group(2)
            res[key] = val
            current_key = key
    for key, val in list(res.items()):
        # Strip paired quotes once the full (possibly folded) scalar is joined.
        quoted = len(val) >= 2 and (
            (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'"))
        )
        if quoted:
            res[key] = val[1:-1]
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
    if priority == "critical":
        priority_level = "P0"
    elif priority in ("high", "normal", "medium"):
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
    in_progress_count = 0
    active_beans: list[dict[str, Any]] = []

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
            if status == "in-progress":
                in_progress_count += 1
            bnum = b["bean_num"]
            if bnum in OVERRIDES:
                ov = OVERRIDES[bnum]
                b["title"] = ov.get("title", b["title"])
                b["priority_display"] = ov["priority"]
                b["impact"] = ov["impact"]
                b["sizing"] = ov["sizing"]
                b["domain"] = ov["domain"]
                b["notes"] = ov["notes"]
            else:
                b["priority_display"] = f"**{b['priority_level']}**"
            active_beans.append(b)

    # Sort active beans: curated OVERRIDES order first (its insertion order is
    # the matrix row order), then any bean without an override by priority
    # (P0 -> P1 -> P2 -> P3) and bean number descending.
    override_order = {bnum: i for i, bnum in enumerate(OVERRIDES)}
    priority_order = {"**P0**": 0, "**P1**": 1, "**P2**": 2, "**P3**": 3}
    active_beans.sort(
        key=lambda x: (
            0 if x["bean_num"] in override_order else 1,
            override_order.get(x["bean_num"], 0),
            priority_order.get(x["priority_display"], 9),
            -int(x["bean_num"]),
        )
    )

    stats = {
        "total_tracked": total_tracked,
        "completed": completed_count,
        "scrapped": scrapped_count,
        "active": len(active_beans),
        "in_progress": in_progress_count,
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
    in_progress = stats.get("in_progress", 0)
    todo = active - in_progress

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
    ]
    if EXECUTIVE_SUMMARY_NARRATIVE:
        lines.extend(EXECUTIVE_SUMMARY_NARRATIVE)
    else:
        lines.append(
            f"Since the previous triage checkpoint on {previous_checkpoint}, the Holon ecosystem has progressed "
            "through automated Holon flow cycles, multi-agent consensus review loops, and infrastructure hardening."
            if previous_checkpoint
            else (
                "As of this checkpoint, the Holon ecosystem has progressed through automated Holon flow cycles, "
                "multi-agent consensus review loops, and infrastructure hardening."
            )
        )
    lines.extend(
        [
            "",
            f"- **Total Tracked Beans**: {total} (excluding template)",
            f"- **Completed**: {completed} ({completed_pct:.1f}%)",
            f"- **Scrapped / Superseded**: {scrapped} ({scrapped_pct:.1f}%)",
            f"- **Active**: {active} ({active_pct:.1f}%), of which {in_progress} are in progress and {todo} are todo",
        ]
    )
    if EXECUTIVE_SUMMARY_UPDATE:
        lines.append("")
        lines.extend(EXECUTIVE_SUMMARY_UPDATE)
    lines.extend(
        [
            "",
            "---",
            "",
            MILESTONES_HEADING,
            "",
            "1. **Holon Flow and Automation Engine**:",
            "   - `0084`: Fixed CI check name collisions in review gates.",
            "   - `0087`: Permitted autonomous PR creation in Holon flow stage 3.",
            (
                "   - `0089`: Auto-routed all flow stages through Holon Coherence proxy for token deduplication "
                "and caching."
            ),
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
                "   - Implemented `install-holon` and `install-coherence` skills "
                "(`.agents/skills/install_holon/SKILL.md`, "
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
                "   - `0118`: Implemented explicit native `holon review-loop` CLI step (Stage 4) in "
                "`holon-agentic-coder`. "
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
                "   - `0109`: Automated conventional commit PR titles (`feat(...)`, `fix(...)`) and structured "
                "Markdown "
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
            "8. **Decoupled Architecture and Canonical 3-Ledger Consolidation (Beans 0122 and 0123 / PR #85)**:",
            (
                "   - Purged all harness-specific metadata paths (`.beans/`, `todo/`, `.agents/`) from target "
                "repositories."
            ),
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
            (
                "9. **Unified Git Abstraction, Unprivileged Containers, and Hardened Locking (Beans 0124 – 0127 / "
                "PR #86)**:"
            ),
            (
                "   - `0124`: Implemented unified Git abstraction in `sandbox_executor.git` with custom "
                "exceptions and strict stderr diagnostics."
            ),
            "   - `0125`: Australian English spelling hygiene across documentation and codebase comments.",
            "   - `0126`: Enforced unprivileged Docker execution via `--cap-drop=ALL` with selective capability drops.",
            "   - `0127`: Hardened `LedgerLock` concurrency file locking with exponential backoff and timeouts.",
            (
                "10. **Documentation Gap Remediation and Container `gh` Availability (Beans 0128 and 0131 / PR #87 & "
                "PR #88)**:"
            ),
            (
                "    - `0128`: Closed documentation drift across `holon-agentic-coder` (PR #87) and the harness, "
                "so flow "
                "stage, ledger, and worktree instructions match the implemented behaviour."
            ),
            (
                "    - `0131`: Installed the GitHub CLI into `holon-base` so every agent image and the Stage 4 "
                "review-loop "
                "container can post consensus reviews, plus container availability tests (PR #88, Stage 5 calibrated)."
            ),
            "11. **Proxy Cold-Start Readiness and Agent Runner Tests (Bean 0130 / holon-coherence PR #26)**:",
            (
                "    - Replaced the fixed-sleep readiness probe with HTTP readiness polling, deduplicated the proxy "
                "`chmod` handling, routed readiness probes around the proxy, and added agent runner integration tests."
            ),
            (
                "    - Traversed all 5 Holon flow stages and passed unanimous 3/3 ensemble consensus at iteration 4; "
                "residual nits were deferred to Beans 0132 and 0133 instead of being dropped."
            ),
            "12. **Ecosystem install refresh and flow-integrity audit (2026-10-22)**:",
            (
                "    - Rebuilt all nine container images via Buildx Bake and reinstalled `holon` / `holon-coherence` "
                "editable from `origin/main` (`holon-agentic-coder` `3bef6f7`, `holon-coherence` `29b7e50`)."
            ),
            (
                "    - Attempted the three remaining beans through the Holon flow and recorded why they could not "
                "complete: Bean 0134 (the unified `holon flow` runner dispatches no role agent and opened the "
                "now-closed empty PR #89), Bean 0135 (mergeability verdict fabricated from a missing ref), and a "
                "full inventory of unusable agent runners."
            ),
            (
                "    - Logged Beans 0137-0140 against the root causes: hard-coded default runner, single-response "
                "artifact authoring, absent turn/stage budgets, and an undisclosed sandbox output ceiling. Declared "
                "`maxTokens` explicitly in the host pi config so the cap is visible."
            ),
            (
                "    - Contained the credential leak in CLI command echoes (Bean 0136): token rotated, old value "
                "verified rejected."
            ),
            "",
            "13. **Five-stage flow cycle on every runner-blocked bean (2026-10-23 to 2026-10-26)**:",
            (
                "    - All seven PRs were driven with the `claude-agent` runner (`claude-opus-5-5`) through intent, "
                "plan, execute, the 3-agent review loop and Stage 5 calibration. Every consensus review was posted; "
                "merging stayed with the maintainer."
            ),
            "    - `0135` (#91): a missing branch ref reports `MISSING_REF`, not a false conflict.",
            (
                "    - `0129` + `0133` (holon-coherence #27): mitmweb inspector, plus a monotonic proxy readiness "
                "deadline."
            ),
            "    - `0132` (#90): Stage 4/5 `ACT-*` rows in `executions.jsonl`, plus a calibration success gate.",
            "    - `0137` (#93): the runner is inherited from the harness, with a pre-flight credential probe.",
            (
                "    - `0136` (#96, superseding #92 after a plan-ID collision): canonical redaction module; "
                "credentials off the docker argv through a 0600 env-file; `redact_cli_error`; URL-message fuzz tests."
            ),
            (
                "    - `0134` (#95): `holon flow` dispatches role agents. Empty diffs are refused fail-closed, "
                "unmeasured tests are never counted as a pass, and tests have a `gh` write guard."
            ),
            (
                "    - `0138` + `0139` + `0140` (#94): incremental artefacts, turn/stage budgets handed to every "
                "container, an explicit model envelope, a unified `holon doctor`, a validated `models.json` loader, "
                "and malformed-config and UTF-8 hardening."
            ),
            (
                "    - Every calibration report read its predicted metrics from the wrong `plans.jsonl` row. Each "
                "got an annotation commit (Bean 0146 has the table)."
            ),
            "",
            "14. **First claude-agent `holon flow` runs and the defects they surfaced (2026-10-26)**:",
            (
                "    - The claude runner fix (Bean 0143) was rebased onto `main`, installed as `holon` and baked into "
                "`holon/agent-claude`. Role containers run the image's code, not the host install."
            ),
            (
                "    - Bean 0151 reached a sound plan (EV 19.82). Stage 3 then fabricated two placeholder sub-intents "
                "and halted for a human (Bean 0159). Maintainer decision: no stage before merge may halt for human "
                "review."
            ),
            (
                "    - Bean 0159 ran intent -> plan -> execute -> review -> calibrate (PR #97). On the way it hit "
                "the following:"
            ),
            (
                "      - Bean 0157: the mitmproxy sidecar auto-starts because its image exists, and role containers "
                "cannot reach it."
            ),
            "      - Bean 0158: every run reorders `intents.jsonl`, which also breaks Stage 4 checkout.",
            "      - Bean 0160: CI polling consumes review iterations and is then reported as test failures.",
            '      - Bean 0144: the native review loop posted a fabricated "3-Agent Ensemble" approval to GitHub.',
            "      - Bean 0162: Stage 5 commits a report that fails the `hygiene` check.",
            (
                "    - PR #97 then went through the real harness `pr-review-loop` (3 blind reviewers plus a resolver "
                "per iteration). Nine iterations applied ledger, design, test-coverage and parser fixes. "
                "Decomposed-child aggregation was deferred to Bean 0161."
            ),
            "",
            "---",
            "",
            "## Active Beans Triage and Prioritisation Matrix",
            "",
            "| Priority | Status | Impact | Sizing | Bean # | Title | Domain | Dependencies / Notes |",
            "| :--- | :--- | :---: | :---: | :--- | :--- | :--- | :--- |",
        ]
    )

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
        lines.extend(NEXT_EXECUTION_SEQUENCE)
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
    previous_checkpoint = read_previous_checkpoint(prior_output)
    doc = generate_triage_document(active_beans, stats, date_str, previous_checkpoint=previous_checkpoint)

    if args.dry_run:
        print(doc)
        return 0

    output_path = args.output or os.path.join(args.beans_dir, "bean-triage-prioritisation.md")
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(doc)

    if previous_checkpoint:
        print(f"Previous triage checkpoint: {previous_checkpoint}")
    print(f"✅ Generated triage document with {len(active_beans)} active beans at: {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
