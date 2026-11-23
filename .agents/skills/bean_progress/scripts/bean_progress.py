#!/usr/bin/env python3
"""bean_progress.py - Live read-only dashboard of in-flight Holon beans.

Correlates `.beans/`, `todo/intent-*.json`, git flow worktrees (`.holon/flow/checkpoint-*.json`),
open GitHub pull requests (`gh pr list`), and running host/Docker flow processes (`ps`)
to print a single Markdown table of all beans currently in flight, strictly excluding
completed and scrapped beans.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

EXCLUDED_STATUSES = frozenset({"completed", "scrapped"})
BEAN_FILE_RE = re.compile(r"^holon-agentic-coder-ref-metadata-(\d{4})--(.+)\.md$")
INTENT_FILE_RE = re.compile(r"^intent-((?:\d{4}-)+)(.+)\.json$")
WORKTREE_BEAN_RE = re.compile(r"(?:^|-)bean-(\d{4})(?:-|$)")
BRANCH_SLUG_RE = re.compile(r"^I-\d+-([^/]+)/")
BRANCH_TS_RE = re.compile(r"^I-(\d+)-")
VERSION_SUFFIX_RE = re.compile(r"-v\d+$")
STAGE_ORDER = ["intent", "plan", "execute", "review", "calibrate", "completed"]
LEDGER_REL = Path("holon-knowledge") / "ledger" / "intents.jsonl"
GITHUB_REMOTE_RE = re.compile(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$")

STAGE_LABELS = {
    "intent": "Stage 1 (Intent)",
    "plan": "Stage 2 (Plan)",
    "execute": "Stage 3 (Execute)",
    "review": "Stage 4 (Review)",
    "calibrate": "Stage 5 (Calibrate)",
}


@dataclass
class BeanRecord:
    """Metadata parsed from a `.beans/` Markdown file."""

    bean_num: str
    slug: str
    title: str
    status: str
    priority: str
    bean_type: str
    tags: list[str]
    blocked_by: list[str]
    path: Path


@dataclass
class IntentMapping:
    """Mapping from `todo/intent-*.json` to bean IDs and flow slug."""

    path: Path
    slug: str
    bean_nums: list[str]
    file_slug: str = ""


@dataclass
class RepoTarget:
    """Managed repository inspected for flow worktrees and open PRs."""

    name: str
    root: Path
    multi_worktree: bool
    github_repo: str | None = None


@dataclass
class WorktreeFlow:
    """Flow checkpoint and git status for a single feature/flow worktree."""

    repo_name: str
    path: Path
    dir_name: str
    slug: str
    current_stage: str | None
    completed_stages: list[str]
    timestamp: str | None
    agent: str | None
    model: str | None
    execution_branch: str | None
    plan_branch: str | None
    intent_branch: str | None
    review_iterations_done: int
    admission: dict[str, Any]
    stage_results: dict[str, Any]
    dirty_count: int = 0
    has_calibration_file: bool = False
    checkpoint_path: Path | None = None
    embedded_bean_nums: list[str] = field(default_factory=list)
    stage_started: datetime | None = None
    flow_started: datetime | None = None
    checkpoint_time: datetime | None = None
    last_log: str = ""
    last_commit_time: datetime | None = None
    last_commit_subject: str = ""


@dataclass
class PullRequestInfo:
    """Open pull request metadata and rolled-up CI/review state."""

    repo_name: str
    number: int
    title: str
    url: str
    head_ref_name: str
    mergeable: str
    is_draft: bool
    reviews_count: int
    comments_count: int
    ci_summary: str


@dataclass
class ProcessInfo:
    """Single row from `ps -eo`."""

    pid: int
    ppid: int
    etime: str
    stat: str
    command: str


@dataclass
class LiveFlowTree:
    """Consolidated host + Docker live process tree targeting one flow worktree."""

    root_pid: int
    etime: str
    kind: str  # "running" | "polling" | "waiter"
    session_owner: str
    worktree_path: str | None
    slug: str | None
    bean_nums: list[str]
    agent: str | None
    model: str | None
    docker_role: str | None
    docker_resolve: bool
    docker_iteration: int | None
    duplicate_trees: int = 1


@dataclass
class InFlightRow:
    """Rendered table row and machine-readable JSON fields."""

    bean_nums: list[str]
    target: str
    title: str
    stage: str
    pr_ci: str
    live_runner: str
    notes: str
    sort_bucket: int
    time_in_stage: str = "—"
    total_time: str = "—"
    source: str = ""
    rank: tuple[float, ...] = ()
    agent: str = "—"
    model: str = "—"
    last_activity: str = "—"

    def notes_cell(self) -> str:
        """Notes column: live/idle state with PID and session first, then the former status notes."""
        parts = [p for p in (self.live_runner, self.notes if self.notes != "—" else "") if p]
        return "; ".join(parts) if parts else "—"

    def as_dict(self) -> dict[str, Any]:
        """Serialize row fields cleanly for `--json` output."""
        return {
            "bean_nums": self.bean_nums,
            "target": self.target,
            "title": self.title,
            "agent": self.agent,
            "model": self.model,
            "stage": self.stage,
            "time_in_stage": self.time_in_stage,
            "pr_ci": self.pr_ci,
            "total_time": self.total_time,
            "last_activity": self.last_activity,
            "live_runner": self.live_runner,
            "notes": self.notes_cell(),
        }


def parse_iso(text: Any) -> datetime | None:
    """Parse an ISO-8601 timestamp (`Z` or offset) into an aware UTC datetime."""
    if not isinstance(text, str) or not text:
        return None
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def branch_started(branch: str | None) -> datetime | None:
    """Epoch seconds embedded in an `I-<ts>-<slug>/...` branch name."""
    m = BRANCH_TS_RE.match(branch or "")
    if not m:
        return None
    try:
        return datetime.fromtimestamp(int(m.group(1)), tz=UTC)
    except (ValueError, OverflowError, OSError):
        return None


def root_slug_of(*branches: str | None) -> str | None:
    """Parent (root) intent slug from the first flow branch name that carries one."""
    for branch in branches:
        m = BRANCH_SLUG_RE.match(branch or "")
        if m:
            return m.group(1)
    return None


def derive_stage_started(
    current_stage: str | None, stage_results: dict[str, Any], timestamp: str | None, mtime: datetime | None
) -> datetime | None:
    """When the current stage began: its recorded start_time, else the previous stage's latest end_time,
    else the checkpoint timestamp, else the checkpoint file mtime."""
    cur = stage_results.get(current_stage) if current_stage else None
    if isinstance(cur, dict):
        started = parse_iso(cur.get("start_time"))
        if started:
            return started
    ends = [parse_iso(v.get("end_time")) for v in stage_results.values() if isinstance(v, dict)]
    ends_ok = [t for t in ends if t]
    if ends_ok:
        return max(ends_ok)
    return parse_iso(timestamp) or mtime


def ledger_first_created(ledger: Path, root_slug: str | None) -> datetime | None:
    """Earliest `created_at` among intents.jsonl rows whose branch belongs to the root intent."""
    if not root_slug or not ledger.is_file():
        return None
    pattern = re.compile(rf"^I-\d+-{re.escape(root_slug)}/")
    earliest: datetime | None = None
    try:
        lines = ledger.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in lines:
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if not isinstance(row, dict) or not pattern.match(str(row.get("branch") or "")):
            continue
        created = parse_iso(row.get("created_at"))
        if created and (earliest is None or created < earliest):
            earliest = created
    return earliest


def earliest_of(*candidates: datetime | None) -> datetime | None:
    present = [c for c in candidates if c]
    return min(present) if present else None


def format_duration(start: datetime | None, now: datetime) -> str:
    """Compact elapsed time (`45s`, `12m`, `1h05m`, `2d3h`); `—` when unknown."""
    if start is None:
        return "—"
    secs = max(0, int((now - start).total_seconds()))
    if secs < 60:
        return f"{secs}s"
    if secs < 3600:
        return f"{secs // 60}m"
    if secs < 86400:
        return f"{secs // 3600}h{(secs % 3600) // 60:02d}m"
    return f"{secs // 86400}d{(secs % 86400) // 3600}h"


def _strip_paired_quotes(text: str) -> str:
    if len(text) >= 2 and (
        (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'"))
    ):
        return text[1:-1]
    return text


def parse_frontmatter(content: str) -> dict[str, Any]:
    """Parse YAML frontmatter scalars, folded multiline scalars, and sequence lists."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    fm_lines: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        fm_lines.append(line)

    result: dict[str, Any] = {}
    i = 0
    while i < len(fm_lines):
        raw = fm_lines[i]
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue

        key_match = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", raw)
        if not key_match:
            i += 1
            continue

        key = key_match.group(1)
        rest = key_match.group(2).strip()
        if rest:
            result[key] = _strip_paired_quotes(rest)
            i += 1
            continue

        j = i + 1
        list_items: list[str] = []
        folded_parts: list[str] = []
        is_list = False
        while j < len(fm_lines):
            nxt = fm_lines[j]
            if not nxt.strip() or not nxt[0].isspace():
                break
            item_match = re.match(r"^\s+-\s*(.*)$", nxt)
            if item_match:
                is_list = True
                item_val = _strip_paired_quotes(item_match.group(1).strip())
                if item_val:
                    list_items.append(item_val)
            elif not is_list:
                folded_parts.append(nxt.strip())
            j += 1

        if is_list:
            result[key] = list_items
        elif folded_parts:
            result[key] = _strip_paired_quotes(" ".join(folded_parts))
        else:
            result[key] = ""
        i = j

    return result


def scan_beans(beans_dir: Path) -> dict[str, BeanRecord]:
    """Load all sequential 4-digit beans from `.beans/`."""
    beans: dict[str, BeanRecord] = {}
    if not beans_dir.is_dir():
        return beans

    for entry in sorted(beans_dir.iterdir()):
        match = BEAN_FILE_RE.match(entry.name)
        if not match or not entry.is_file():
            continue
        bean_num, slug = match.group(1), match.group(2)
        try:
            content = entry.read_text(encoding="utf-8")
        except OSError:
            continue

        fm = parse_frontmatter(content)
        raw_tags = fm.get("tags")
        tags = raw_tags if isinstance(raw_tags, list) else []
        raw_blocked = fm.get("blocked_by")
        blocked_by = raw_blocked if isinstance(raw_blocked, list) else []

        beans[bean_num] = BeanRecord(
            bean_num=bean_num,
            slug=slug,
            title=str(fm.get("title") or slug.replace("-", " ")),
            status=str(fm.get("status") or "todo").strip().lower(),
            priority=str(fm.get("priority") or "normal").strip().lower(),
            bean_type=str(fm.get("type") or "task").strip().lower(),
            tags=tags,
            blocked_by=blocked_by,
            path=entry,
        )
    return beans


def scan_intents(todo_dir: Path) -> list[IntentMapping]:
    """Discover `todo/intent-<bean>-<slug>.json` mappings."""
    intents: list[IntentMapping] = []
    if not todo_dir.is_dir():
        return intents

    for entry in sorted(todo_dir.iterdir()):
        match = INTENT_FILE_RE.match(entry.name)
        if not match or not entry.is_file():
            continue
        bean_nums = re.findall(r"\d{4}", match.group(1))
        slug = match.group(2)
        try:
            data = json.loads(entry.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("slug"), str) and data["slug"]:
                slug = data["slug"]
        except (OSError, ValueError):
            # Unreadable or malformed intent JSON: keep the slug parsed from the file name.
            pass
        intents.append(IntentMapping(path=entry, slug=slug, bean_nums=bean_nums, file_slug=match.group(2)))
    return intents


def _read_github_repo(git_dir: Path) -> str | None:
    if not git_dir.exists():
        return None
    try:
        proc = subprocess.run(
            ["git", "-C", str(git_dir), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    match = GITHUB_REMOTE_RE.search(proc.stdout.strip())
    return match.group(1) if match else None


def discover_repos(repo_root: Path) -> list[RepoTarget]:
    """Discover managed Holon repositories and their GitHub `owner/repo` slugs."""
    candidates = [
        ("HAC", repo_root / "apps" / "holon-agentic-coder", True),
        ("Coherence", repo_root / "apps" / "holon-coherence", True),
        ("dev-env", repo_root.parent / "dev-env", True),
        ("harness", repo_root, False),
    ]
    repos: list[RepoTarget] = []
    for name, root, multi in candidates:
        if not root.is_dir():
            continue
        remote_probe = (root / "main") if (multi and (root / "main").is_dir()) else root
        if multi and not remote_probe.exists() and (root / ".git").exists():
            remote_probe = root / ".git"
        repos.append(
            RepoTarget(
                name=name,
                root=root,
                multi_worktree=multi,
                github_repo=_read_github_repo(remote_probe),
            )
        )
    return repos


def _git_dirty_count(worktree_dir: Path) -> int:
    try:
        proc = subprocess.run(
            ["git", "-C", str(worktree_dir), "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return 0
    if proc.returncode != 0:
        return 0
    return sum(1 for line in proc.stdout.splitlines() if line.strip())


def _git_last_commit(worktree_dir: Path) -> tuple[datetime | None, str]:
    """Commit time and subject of the worktree's HEAD; (None, "") when git cannot tell."""
    try:
        res = subprocess.run(
            ["git", "-C", str(worktree_dir), "log", "-1", "--format=%ct%x09%s"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None, ""
    stamp, _, subject = res.stdout.strip().partition("\t")
    if res.returncode != 0 or not stamp.isdigit():
        return None, ""
    return datetime.fromtimestamp(int(stamp), tz=UTC), subject.strip()


def _last_checkpoint_log(ctx: dict[str, Any]) -> str:
    """The newest line of the checkpoint's flow log, without its leading `[timestamp]`."""
    logs = ctx.get("logs")
    if not isinstance(logs, list) or not logs:
        return ""
    return re.sub(r"^\[[^\]]*\]\s*", "", str(logs[-1]).strip())


def scan_worktrees(repos: list[RepoTarget]) -> list[WorktreeFlow]:
    """Inspect non-`main` worktrees and their Holon flow checkpoints."""
    worktrees: list[WorktreeFlow] = []
    for repo in repos:
        if not repo.multi_worktree or not repo.root.is_dir():
            continue
        for entry in sorted(repo.root.iterdir()):
            if not entry.is_dir() or entry.name in {"main", ".git"}:
                continue

            flow_dir = entry / ".holon" / "flow"
            checkpoints = (
                sorted(
                    flow_dir.glob("checkpoint-*.json"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True,
                )
                if flow_dir.is_dir()
                else []
            )

            data: dict[str, Any] = {}
            ckpt_path: Path | None = checkpoints[0] if checkpoints else None
            if ckpt_path is not None:
                try:
                    loaded = json.loads(ckpt_path.read_text(encoding="utf-8"))
                    if isinstance(loaded, dict):
                        data = loaded
                except (OSError, ValueError):
                    data = {}

            ctx = data.get("context") if isinstance(data.get("context"), dict) else {}
            slug = str(
                data.get("intent_slug")
                or (ctx.get("intent_data") or {}).get("slug")
                or (entry.name.removeprefix("flow-") if entry.name.startswith("flow-") else entry.name)
            )
            admission = data.get("admission") if isinstance(data.get("admission"), dict) else ctx.get("admission")
            if not isinstance(admission, dict):
                admission = {}
            stage_results = ctx.get("stage_results") if isinstance(ctx.get("stage_results"), dict) else {}
            completed_raw = data.get("completed_stages")
            completed = [str(s) for s in completed_raw] if isinstance(completed_raw, list) else []

            cal_glob = (
                list((entry / "plans").glob(f"I-*-{slug}/*_calibration.md")) if (entry / "plans").is_dir() else []
            )
            intent_branch = ctx.get("intent_branch")
            plan_branch = ctx.get("plan_branch")
            exec_branch = ctx.get("execution_branch")
            root_slug = root_slug_of(intent_branch, plan_branch, exec_branch)
            if root_slug:
                slug = root_slug
            mtime = datetime.fromtimestamp(ckpt_path.stat().st_mtime, tz=UTC) if ckpt_path else None
            stage_started = (
                derive_stage_started(data.get("current_stage"), stage_results, data.get("timestamp"), mtime)
                if ckpt_path
                else None
            )
            flow_started = earliest_of(
                branch_started(intent_branch or plan_branch or exec_branch),
                ledger_first_created(entry / LEDGER_REL, slug),
            )
            commit_time, commit_subject = _git_last_commit(entry)
            embedded_beans = WORKTREE_BEAN_RE.findall(entry.name)
            if ckpt_path is not None:
                embedded_beans.extend(re.findall(r"(?:^|-)(\d{4})(?:-|$)", ckpt_path.stem))

            worktrees.append(
                WorktreeFlow(
                    repo_name=repo.name,
                    path=entry.resolve(),
                    dir_name=entry.name,
                    slug=slug,
                    current_stage=data.get("current_stage"),
                    completed_stages=completed,
                    timestamp=data.get("timestamp"),
                    agent=ctx.get("agent"),
                    model=ctx.get("model"),
                    execution_branch=ctx.get("execution_branch"),
                    plan_branch=ctx.get("plan_branch"),
                    intent_branch=ctx.get("intent_branch"),
                    review_iterations_done=int(ctx.get("review_iterations_done") or 0),
                    admission=admission,
                    stage_results=stage_results,
                    dirty_count=_git_dirty_count(entry),
                    has_calibration_file=bool(cal_glob),
                    checkpoint_path=ckpt_path,
                    embedded_bean_nums=sorted(set(embedded_beans)),
                    stage_started=stage_started,
                    flow_started=flow_started,
                    checkpoint_time=(parse_iso(data.get("timestamp")) or mtime) if ckpt_path else None,
                    last_log=_last_checkpoint_log(ctx),
                    last_commit_time=commit_time,
                    last_commit_subject=commit_subject,
                )
            )
    return worktrees


def summarize_checks(rollup: Any) -> str:
    """Aggregate GitHub `statusCheckRollup` entries into a compact status string."""
    if not isinstance(rollup, list) or not rollup:
        return "no checks"

    passed = 0
    failed = 0
    pending = 0
    for item in rollup:
        if not isinstance(item, dict):
            continue
        if "status" in item or "conclusion" in item:
            status = str(item.get("status") or "").upper()
            conclusion = str(item.get("conclusion") or "").upper()
            if status != "COMPLETED":
                pending += 1
            elif conclusion in {"SUCCESS", "NEUTRAL", "SKIPPED"}:
                passed += 1
            else:
                failed += 1
        else:
            state = str(item.get("state") or "").upper()
            if state == "SUCCESS":
                passed += 1
            elif state in {"", "PENDING", "EXPECTED"}:
                pending += 1
            else:
                failed += 1

    total = passed + failed + pending
    if total == 0:
        return "no checks"
    if failed == 0 and pending == 0:
        return f"{passed}/{total} pass"

    parts = [f"{passed}/{total} pass"]
    if failed:
        parts.append(f"{failed} fail")
    if pending:
        parts.append(f"{pending} running")
    return ", ".join(parts)


def fetch_open_prs(repos: list[RepoTarget], *, no_gh: bool = False) -> list[PullRequestInfo]:
    """Fetch open PRs via `gh pr list` across all managed GitHub repositories."""
    if no_gh:
        return []

    prs: list[PullRequestInfo] = []
    seen_gh: set[str] = set()
    for repo in repos:
        if not repo.github_repo or repo.github_repo in seen_gh:
            continue
        seen_gh.add(repo.github_repo)
        try:
            proc = subprocess.run(
                [
                    "gh",
                    "pr",
                    "list",
                    "--repo",
                    repo.github_repo,
                    "--state",
                    "open",
                    "--json",
                    "number,title,url,headRefName,mergeable,isDraft,reviews,comments,statusCheckRollup",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if proc.returncode != 0 or not proc.stdout.strip():
            continue

        try:
            raw_list = json.loads(proc.stdout)
        except ValueError:
            continue
        if not isinstance(raw_list, list):
            continue

        for item in raw_list:
            if not isinstance(item, dict):
                continue
            prs.append(
                PullRequestInfo(
                    repo_name=repo.name,
                    number=int(item["number"]),
                    title=str(item.get("title") or ""),
                    url=str(item.get("url") or ""),
                    head_ref_name=str(item.get("headRefName") or ""),
                    mergeable=str(item.get("mergeable") or ""),
                    is_draft=bool(item.get("isDraft")),
                    reviews_count=len(item.get("reviews") or []),
                    comments_count=len(item.get("comments") or []),
                    ci_summary=summarize_checks(item.get("statusCheckRollup")),
                )
            )
    return prs


def scan_processes(*, no_ps: bool = False) -> list[ProcessInfo]:
    """Read running host processes via `ps -eo pid=,ppid=,etime=,stat=,command=`."""
    if no_ps:
        return []
    try:
        proc = subprocess.run(
            ["ps", "-eo", "pid=,ppid=,etime=,stat=,command="],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if proc.returncode != 0:
        return []

    items: list[ProcessInfo] = []
    for line in proc.stdout.splitlines():
        m = re.match(r"^\s*(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(.*)$", line)
        if not m:
            continue
        items.append(
            ProcessInfo(
                pid=int(m.group(1)),
                ppid=int(m.group(2)),
                etime=m.group(3),
                stat=m.group(4),
                command=m.group(5),
            )
        )
    return items


def detect_session_owner(pid: int, by_pid: dict[int, ProcessInfo]) -> str:
    """Walk strictly ancestor processes (never `pid` itself) to identify the harness session."""
    current = by_pid.get(pid)
    visited: set[int] = set()
    hops = 0
    while current and hops < 12:
        ppid = current.ppid
        if ppid <= 1 or ppid in visited:
            break
        visited.add(ppid)
        ancestor = by_pid.get(ppid)
        if ancestor is None:
            break
        cmd_lower = ancestor.command.lower()
        first_token = Path(cmd_lower.split()[0]).name if cmd_lower.split() else ""
        if "antigravity" in cmd_lower or first_token == "agy":
            return "Antigravity"
        if first_token == "claude" or "/claude" in cmd_lower:
            return "Claude Code"
        if first_token == "codex" or "/codex" in cmd_lower:
            return "Codex"
        current = ancestor
        hops += 1
    return "terminal"


def _extract_flag_value(tokens: list[str], flag: str) -> str | None:
    for idx, tok in enumerate(tokens):
        if tok == flag and idx + 1 < len(tokens):
            return tokens[idx + 1]
        if tok.startswith(f"{flag}="):
            return tok.split("=", 1)[1]
    return None


def _parse_docker_flow_info(tokens: list[str]) -> tuple[str | None, str | None, bool, int | None]:
    worktree: str | None = None
    role: str | None = None
    resolve = False
    iteration: int | None = None

    for idx, tok in enumerate(tokens):
        if tok in {"-v", "--volume"} and idx + 1 < len(tokens):
            mount = tokens[idx + 1]
            if ":/home/holon/.holon-sandbox/workspace" in mount:
                host_path = mount.split(":", 1)[0]
                worktree = os.path.realpath(host_path)
        elif tok == "-e" and idx + 1 < len(tokens) and tokens[idx + 1].startswith("HOLON_ROLE="):
            role = tokens[idx + 1].split("=", 1)[1]
        elif tok == "--resolve":
            resolve = True
        elif tok.startswith("--iteration="):
            with contextlib.suppress(ValueError):
                iteration = int(tok.split("=", 1)[1])
    return worktree, role, resolve, iteration


def _is_flow_process(cmd: str) -> str | None:
    if "run_holon_flow.py" in cmd or re.search(r"(?:^|/|\s)holon\s+flow(?:\s|$)", cmd):
        return "flow"
    if "docker run" in cmd and ("HOLON_ROLE=" in cmd or "holon/agent-" in cmd):
        return "docker"
    if ("sleep " in cmd or "wait_for.py" in cmd) and ("flow-" in cmd or "holon-agentic-coder/pull" in cmd):
        return "waiter"
    return None


def match_live_flows(
    processes: list[ProcessInfo],
    worktrees: list[WorktreeFlow],
    intents: list[IntentMapping],
) -> dict[str, LiveFlowTree]:
    """Group live host/Docker flow processes per target worktree path (fallback: slug)."""
    by_pid = {p.pid: p for p in processes}
    wt_by_path = {str(w.path): w for w in worktrees}
    wt_by_slug = {w.slug: w for w in worktrees}
    intent_by_name = {i.path.name: i for i in intents}

    flow_procs: dict[int, tuple[ProcessInfo, str]] = {}
    for proc in processes:
        kind = _is_flow_process(proc.command)
        if kind:
            flow_procs[proc.pid] = (proc, kind)

    def find_root_pid(pid: int) -> int:
        cur = pid
        seen: set[int] = set()
        while cur in by_pid and cur not in seen:
            seen.add(cur)
            ppid = by_pid[cur].ppid
            if ppid in flow_procs:
                cur = ppid
                continue
            parent = by_pid.get(ppid)
            if (
                parent
                and ppid > 1
                and ("/bin/sh" in parent.command or "zsh" in parent.command or "bash" in parent.command)
            ):
                if ppid in flow_procs:
                    cur = ppid
                    continue
                grand = parent.ppid
                if grand in flow_procs:
                    cur = grand
                    continue
            break
        return cur

    trees_by_root: dict[int, list[tuple[ProcessInfo, str]]] = {}
    for pid, entry in flow_procs.items():
        root = find_root_pid(pid)
        trees_by_root.setdefault(root, []).append(entry)

    result: dict[str, LiveFlowTree] = {}
    for root_pid, members in trees_by_root.items():
        root_proc = by_pid[root_pid]
        session_owner = detect_session_owner(root_pid, by_pid)

        wt_path: str | None = None
        slug: str | None = None
        bean_nums: list[str] = []
        agent: str | None = None
        model: str | None = None
        docker_role: str | None = None
        docker_resolve = False
        docker_iteration: int | None = None
        has_docker = False
        has_waiter_only = all(k == "waiter" for _, k in members)

        for proc, kind in sorted(members, key=lambda m: m[0].pid):
            try:
                tokens = shlex.split(proc.command)
            except ValueError:
                tokens = proc.command.split()

            if kind == "flow":
                raw_wt = _extract_flag_value(tokens, "--target-worktree")
                if raw_wt:
                    wt_path = os.path.realpath(raw_wt)
                agent = _extract_flag_value(tokens, "--agent") or agent
                model = _extract_flag_value(tokens, "--model") or model
                for tok in tokens:
                    base = Path(tok).name
                    if base in intent_by_name:
                        slug = intent_by_name[base].slug
                        bean_nums.extend(intent_by_name[base].bean_nums)
                    elif INTENT_FILE_RE.match(base):
                        im = INTENT_FILE_RE.match(base)
                        if im:
                            bean_nums.extend(re.findall(r"\d{4}", im.group(1)))
                            slug = slug or im.group(2)
            elif kind == "docker":
                has_docker = True
                d_wt, d_role, d_res, d_iter = _parse_docker_flow_info(tokens)
                wt_path = wt_path or d_wt
                docker_role = d_role or docker_role
                docker_resolve = docker_resolve or d_res
                docker_iteration = d_iter if d_iter is not None else docker_iteration
                # Runner and model appear as trailing positional args after image name.
                for tok in tokens:
                    if tok in {"claude-agent", "antigravity-agent", "codex-agent"} and not agent:
                        agent = tok
            elif kind == "waiter":
                m_slug = re.search(r"(?:flow-|intent-(?:\d{4}-)+)([a-z0-9-]+)", proc.command)
                if m_slug:
                    slug = slug or m_slug.group(1)

        if wt_path and wt_path in wt_by_path:
            slug = slug or wt_by_path[wt_path].slug
        elif not wt_path and slug and slug in wt_by_slug:
            wt_path = str(wt_by_slug[slug].path)

        key = wt_path or (f"slug:{slug}" if slug else f"pid:{root_pid}")
        if has_docker:
            flow_kind = "running"
        elif has_waiter_only:
            flow_kind = "waiter"
        else:
            # Determine if the flow process itself is blocked polling admission or running a host step.
            wt_obj = wt_by_path.get(wt_path) if wt_path else None
            flow_kind = "polling" if wt_obj and wt_obj.admission.get("state") == "blocked" else "running"

        new_tree = LiveFlowTree(
            root_pid=root_pid,
            etime=root_proc.etime,
            kind=flow_kind,
            session_owner=session_owner,
            worktree_path=wt_path,
            slug=slug,
            bean_nums=sorted(set(bean_nums)),
            agent=agent,
            model=model,
            docker_role=docker_role,
            docker_resolve=docker_resolve,
            docker_iteration=docker_iteration,
            duplicate_trees=1,
        )

        if key in result:
            existing = result[key]
            existing.duplicate_trees += 1
            if new_tree.kind == "running" and existing.kind != "running":
                new_tree.duplicate_trees = existing.duplicate_trees
                result[key] = new_tree
        else:
            result[key] = new_tree

    return result


def format_etime(etime: str) -> str:
    """Format `ps` elapsed time (`DD-HH:MM:SS`, `HH:MM:SS`, `MM:SS`) compactly."""
    days = 0
    rest = etime.strip()
    if "-" in rest:
        d_str, rest = rest.split("-", 1)
        try:
            days = int(d_str)
        except ValueError:
            days = 0
    parts = rest.split(":")
    try:
        nums = [int(p) for p in parts]
    except ValueError:
        return etime
    if len(nums) == 3:
        hours, mins, secs = nums
    elif len(nums) == 2:
        hours, mins, secs = 0, nums[0], nums[1]
    else:
        return etime

    total_hours = days * 24 + hours
    if total_hours > 0:
        return f"{total_hours}h{mins:02d}m"
    if mins > 0:
        return f"{mins}m"
    return f"{secs}s"


def _truncate(text: str, limit: int = 64) -> str:
    collapsed = " ".join(text.split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 1].rstrip() + "…"


def _escape_cell(text: str) -> str:
    return " ".join(text.split()).replace("|", "\\|")


def _infer_target_from_bean(bean: BeanRecord) -> str:
    tags = set(bean.tags)
    if "dev-env" in tags:
        return "dev-env"
    if "holon-coherence" in tags or "coherence" in tags:
        return "Coherence"
    if "holon-agentic-coder" in tags:
        return "HAC"
    if "harness" in tags or "beans" in tags or "skill" in tags:
        return "harness"
    return "HAC"


def _clean_halt_error(error: str) -> str:
    if not error:
        return ""
    msg = error.replace("Autonomous review halted: ", "").replace("Autonomous review failed: ", "")
    msg = msg.replace("Stage 4 failed: ", "").replace("Stage 3 refused: ", "")
    return _truncate(msg, 72)


def _match_pr_for_unit(
    wt: WorktreeFlow | None,
    slug: str | None,
    bean_nums: list[str],
    prs: list[PullRequestInfo],
) -> PullRequestInfo | None:
    if wt and wt.execution_branch:
        for pr in prs:
            if pr.head_ref_name == wt.execution_branch:
                return pr
    if slug:
        slug_re = re.compile(rf"^I-\d+-{re.escape(slug)}/")
        for pr in prs:
            if slug_re.match(pr.head_ref_name):
                return pr
    for bnum in bean_nums:
        num_re = re.compile(rf"(?<!\d){bnum}(?!\d)")
        for pr in prs:
            if num_re.search(pr.head_ref_name) or f"Bean {bnum}" in pr.title or f"#{bnum}" in pr.title:
                return pr
    return None


def _derive_stage(wt: WorktreeFlow | None, live: LiveFlowTree | None, has_pr: bool) -> str:
    if live and live.docker_role == "review-loop":
        mode = "Resolve" if live.docker_resolve else "Review"
        iter_part = f" iter {live.docker_iteration}" if live.docker_iteration is not None else ""
        return f"Stage 4 ({mode}{iter_part})"
    if live and live.docker_role == "executor":
        return "Stage 3 (Executing)"
    if live and wt and wt.admission.get("state") == "blocked":
        blockers = wt.admission.get("blocked_by") or []
        nums = [f"#{b['number']}" for b in blockers if isinstance(b, dict) and b.get("number") is not None]
        blocker_str = ", ".join(nums) if nums else "overlap"
        return f"Stage 3 (Blocked: {blocker_str})"

    if wt is None:
        return "Stage 4 (Review)" if has_pr else "Not started"

    sr = wt.stage_results
    cal_status = (sr.get("calibrate") or {}).get("status") if isinstance(sr.get("calibrate"), dict) else None
    rev_status = (sr.get("review") or {}).get("status") if isinstance(sr.get("review"), dict) else None
    exec_status = (sr.get("execute") or {}).get("status") if isinstance(sr.get("execute"), dict) else None

    if cal_status == "success":
        if rev_status == "skipped":
            return "Stage 5 (Calibrated; review skipped)"
        return "Stage 5 (Calibrated)"

    if wt.admission.get("state") == "blocked" and exec_status != "success":
        blockers = wt.admission.get("blocked_by") or []
        nums = [f"#{b['number']}" for b in blockers if isinstance(b, dict) and b.get("number") is not None]
        blocker_str = ", ".join(nums) if nums else "overlap"
        return f"Stage 3 (Blocked: {blocker_str})"

    if wt.current_stage == "review" and rev_status == "failed":
        iter_part = f" iter {wt.review_iterations_done}" if wt.review_iterations_done else ""
        return f"Stage 4 (Halted{iter_part})"

    if wt.current_stage:
        return STAGE_LABELS.get(wt.current_stage, f"Stage ({wt.current_stage})")
    return "Not started"


def _attempt_rank(wt: WorktreeFlow | None, live: LiveFlowTree | None, pr: PullRequestInfo | None) -> tuple[float, ...]:
    live_score = 2.0 if live and live.kind == "running" else 1.0 if live else 0.0
    stage_score = float(STAGE_ORDER.index(wt.current_stage)) if wt and wt.current_stage in STAGE_ORDER else -1.0
    recency = wt.stage_started.timestamp() if wt and wt.stage_started else 0.0
    return (live_score, 1.0 if pr else 0.0, stage_score, recency)


def _derive_agent_model(wt: WorktreeFlow | None, live: LiveFlowTree | None) -> tuple[str, str]:
    """The flow's runner agent and model: the live process first, then the worktree checkpoint; "—" when unknown."""
    agent = (live.agent if live else None) or (wt.agent if wt else None) or ""
    model = (live.model if live else None) or (wt.model if wt else None) or ""
    if not agent and model:
        agent = (
            "claude-agent"
            if model.startswith("claude-")
            else "antigravity-agent"
            if model.startswith("gemini-")
            else ""
        )
    return agent or "—", model or "—"


def _derive_last_activity(wt: WorktreeFlow | None, live: LiveFlowTree | None, now: datetime) -> str:
    """What the flow is doing or last did: the live role container, then the newest of HEAD commit and checkpoint.

    The live part comes from the running role container (role, review iteration, resolver). The commit part is the
    worktree's HEAD (role agents commit step by step, so it is the closest thing to live work progress). The checkpoint
    part is the last line the flow engine logged when it last saved its checkpoint.
    """
    parts: list[str] = []
    if live and live.kind == "running" and (live.docker_role or live.docker_iteration is not None):
        fallback = "review" if live.docker_iteration is not None else "role container"
        role = "resolver" if live.docker_resolve else (live.docker_role or fallback)
        iteration = f" iter {live.docker_iteration}" if live.docker_iteration is not None else ""
        parts.append(f"now: {role}{iteration} running")
    dated: list[tuple[datetime, str]] = []
    if wt and wt.last_commit_time and wt.last_commit_subject:
        ago = format_duration(wt.last_commit_time, now)
        dated.append((wt.last_commit_time, f"commit {ago} ago: {_truncate(wt.last_commit_subject, 70)}"))
    if wt and wt.checkpoint_time and wt.last_log:
        ago = format_duration(wt.checkpoint_time, now)
        dated.append((wt.checkpoint_time, f"checkpoint {ago} ago: {_truncate(wt.last_log, 70)}"))
    parts.extend(text for _, text in sorted(dated, key=lambda item: item[0], reverse=True))
    return "; ".join(parts) if parts else "—"


def _derive_live_runner(wt: WorktreeFlow | None, live: LiveFlowTree | None) -> str:
    if live:
        model = "live"
        elapsed = format_etime(live.etime)
        if live.kind == "polling":
            blockers = (wt.admission.get("blocked_by") or []) if wt else []
            nums = [f"#{b['number']}" for b in blockers if isinstance(b, dict) and b.get("number") is not None]
            target_pr = ", ".join(nums) if nums else "PR"
            return f"polling {target_pr}: {model} · {elapsed} (PID {live.root_pid}, {live.session_owner})"
        if live.kind == "waiter":
            return f"waiter · {elapsed} (PID {live.root_pid}, {live.session_owner})"
        return f"{model} · {elapsed} (PID {live.root_pid}, {live.session_owner})"

    return "idle"


def _derive_pr_ci(pr: PullRequestInfo | None) -> str:
    if pr is None:
        return "—"
    parts = [f"[#{pr.number}]({pr.url})", pr.ci_summary, f"{pr.reviews_count} rev"]
    if pr.mergeable == "CONFLICTING":
        parts.append("CONFLICTING")
    if pr.is_draft:
        parts.append("DRAFT")
    return " · ".join(parts)


def _derive_notes(
    group_beans: list[BeanRecord],
    wt: WorktreeFlow | None,
    pr: PullRequestInfo | None,
    live: LiveFlowTree | None,
) -> str:
    notes: list[str] = []
    if live and live.duplicate_trees > 1:
        notes.append(f"⚠️ {live.duplicate_trees} processes on worktree")

    todo_statuses = [b.status for b in group_beans if b.status != "in-progress"]
    if todo_statuses and (wt is not None or pr is not None or live is not None):
        notes.append(f"bean status: {todo_statuses[0]}")

    if wt:
        sr = wt.stage_results
        rev_stage = sr.get("review") if isinstance(sr.get("review"), dict) else {}
        cal_stage = sr.get("calibrate") if isinstance(sr.get("calibrate"), dict) else {}
        rev_status = rev_stage.get("status")
        cal_status = cal_stage.get("status")

        if cal_status == "success" and rev_status == "skipped":
            notes.append("Ready for review (Stage 4 skipped via --skip-review)")
        elif cal_status == "success":
            notes.append("Ready for maintainer merge")
        elif wt.admission.get("state") == "blocked" and (sr.get("execute") or {}).get("status") != "success":
            blockers = wt.admission.get("blocked_by") or []
            files: list[str] = []
            for blk in blockers:
                if isinstance(blk, dict):
                    for f in blk.get("files") or []:
                        files.append(Path(str(f)).name)
            if files:
                notes.append(f"Overlap on {', '.join(files[:3])}")
        elif live and live.kind == "running":
            if live.docker_role == "review-loop":
                notes.append("Resolving review findings" if live.docker_resolve else "Ensemble reviewing PR")
            elif live.docker_role == "executor":
                notes.append("Executing plan in Docker")
            else:
                notes.append("Flow active")
        elif rev_status == "failed":
            err = _clean_halt_error(str(rev_stage.get("error") or ""))
            if err:
                notes.append(err)

        if wt.dirty_count and not (live and live.kind == "running"):
            notes.append(f"dirty: {wt.dirty_count} file(s)")

    if not notes and group_beans:
        blocked = [b.removeprefix("holon-agentic-coder-ref-metadata-") for g in group_beans for b in g.blocked_by]
        if blocked:
            notes.append(f"blocked by {', '.join(blocked)}")
        else:
            notes.append(f"status: {group_beans[0].status}")

    if pr and pr.reviews_count == 0 and wt is None:
        notes.append("PR open; no local flow worktree")

    return "; ".join(notes) if notes else "—"


def build_in_flight_rows(
    beans: dict[str, BeanRecord],
    intents: list[IntentMapping],
    worktrees: list[WorktreeFlow],
    prs: list[PullRequestInfo],
    live_by_key: dict[str, LiveFlowTree],
    now: datetime | None = None,
) -> list[InFlightRow]:
    """Correlate beans, intents, worktrees, open PRs, and live PIDs into active rows."""
    wt_by_slug = {w.slug: w for w in worktrees}
    now = now or datetime.now(UTC)

    # Index active intents by parent intent slug (json slug and file slug), filtering out completed/scrapped beans.
    active_by_slug: dict[str, list[str]] = {}
    all_by_slug: dict[str, list[str]] = {}
    for intent in intents:
        active_nums = [n for n in intent.bean_nums if n not in beans or beans[n].status not in EXCLUDED_STATUSES]
        for key in {intent.slug, intent.file_slug} - {""}:
            all_by_slug.setdefault(key, []).extend(intent.bean_nums)
            if active_nums:
                active_by_slug.setdefault(key, []).extend(active_nums)

    def _lookup(index: dict[str, list[str]], slug: str) -> list[str]:
        if slug in index:
            return index[slug]
        return index.get(VERSION_SUFFIX_RE.sub("", slug), [])

    class _SlugIndex:
        def get(self, slug: str, default: Any = None) -> list[str]:
            return list(_lookup(active_by_slug, slug))

    slug_to_intent_beans = _SlugIndex()

    def is_slug_completed_only(slug: str) -> bool:
        nums = _lookup(all_by_slug, slug)
        return bool(nums) and all(n in beans and beans[n].status in EXCLUDED_STATUSES for n in nums)

    used_beans: set[str] = set()
    used_worktrees: set[str] = set()
    used_prs: set[tuple[str, int]] = set()
    rows: list[InFlightRow] = []

    def resolve_live(wt: WorktreeFlow | None, slug: str | None) -> LiveFlowTree | None:
        if wt and str(wt.path) in live_by_key:
            return live_by_key[str(wt.path)]
        if slug and f"slug:{slug}" in live_by_key:
            return live_by_key[f"slug:{slug}"]
        return None

    # 1. Start from every flow worktree (unless mapped exclusively to completed/scrapped beans).
    for wt in worktrees:
        cand_beans = list(slug_to_intent_beans.get(wt.slug) or [])
        for emb in wt.embedded_bean_nums:
            if emb not in cand_beans and (emb not in beans or beans[emb].status not in EXCLUDED_STATUSES):
                cand_beans.append(emb)

        # Skip worktrees whose only associated beans are completed or scrapped.
        all_embedded_done = bool(wt.embedded_bean_nums) and all(
            n in beans and beans[n].status in EXCLUDED_STATUSES for n in wt.embedded_bean_nums
        )
        if is_slug_completed_only(wt.slug) or (not cand_beans and all_embedded_done):
            continue

        cand_beans = sorted(set(cand_beans))
        pr = _match_pr_for_unit(wt, wt.slug, cand_beans, prs)
        live = resolve_live(wt, wt.slug)

        group_beans = [beans[n] for n in cand_beans if n in beans]
        # Skip idle, un-PR'd todo/draft worktrees? Wait: a local worktree with checkpoint means flow started!
        if pr:
            used_prs.add((pr.repo_name, pr.number))
        used_worktrees.add(str(wt.path))
        used_beans.update(cand_beans)

        if group_beans:
            title = " + ".join(b.title for b in group_beans) if len(group_beans) > 1 else group_beans[0].title
        else:
            title = wt.slug.replace("-", " ")

        stage = _derive_stage(wt, live, pr is not None)
        live_runner = _derive_live_runner(wt, live)
        pr_ci = _derive_pr_ci(pr)
        notes = _derive_notes(group_beans, wt, pr, live)
        bucket = 0 if (live and live.kind == "running") else 1 if live else 2
        rows.append(
            InFlightRow(
                bean_nums=cand_beans,
                target=wt.repo_name,
                title=_truncate(title),
                stage=stage,
                pr_ci=pr_ci,
                live_runner=live_runner,
                notes=notes,
                sort_bucket=bucket,
                time_in_stage=format_duration(wt.stage_started, now) if stage != "Not started" else "—",
                total_time=format_duration(wt.flow_started, now),
                source=wt.dir_name,
                rank=_attempt_rank(wt, live, pr),
                agent=_derive_agent_model(wt, live)[0],
                model=_derive_agent_model(wt, live)[1],
                last_activity=_derive_last_activity(wt, live, now),
            )
        )

    # 2. Live flows or open PRs without a matching local worktree (e.g., from another checkout).
    for _key, live in live_by_key.items():
        if live.worktree_path and live.worktree_path in used_worktrees:
            continue
        if live.slug and live.slug in wt_by_slug and str(wt_by_slug[live.slug].path) in used_worktrees:
            continue
        if live.slug and is_slug_completed_only(live.slug):
            continue
        cand_beans = sorted(
            {
                n
                for n in (live.bean_nums + (slug_to_intent_beans.get(live.slug or "", [])))
                if n not in beans or beans[n].status not in EXCLUDED_STATUSES
            }
        )
        if live.bean_nums and not cand_beans:
            continue
        pr = _match_pr_for_unit(
            None, live.slug, cand_beans, [p for p in prs if (p.repo_name, p.number) not in used_prs]
        )
        if pr:
            used_prs.add((pr.repo_name, pr.number))
        used_beans.update(cand_beans)
        group_beans = [beans[n] for n in cand_beans if n in beans]
        target = pr.repo_name if pr else (_infer_target_from_bean(group_beans[0]) if group_beans else "HAC")
        title = group_beans[0].title if group_beans else (live.slug or "active flow")
        rows.append(
            InFlightRow(
                bean_nums=cand_beans,
                target=target,
                title=_truncate(title),
                stage=_derive_stage(None, live, pr is not None),
                pr_ci=_derive_pr_ci(pr),
                live_runner=_derive_live_runner(None, live),
                notes=_derive_notes(group_beans, None, pr, live),
                sort_bucket=0 if live.kind == "running" else 1,
                total_time=format_duration(branch_started(pr.head_ref_name) if pr else None, now),
                source=f"live PID {live.root_pid}",
                rank=_attempt_rank(None, live, pr),
                agent=_derive_agent_model(None, live)[0],
                model=_derive_agent_model(None, live)[1],
                last_activity=_derive_last_activity(None, live, now),
            )
        )

    # 3. Remaining open PRs not yet matched to a worktree or live flow.
    for pr in prs:
        if (pr.repo_name, pr.number) in used_prs:
            continue
        m_slug = BRANCH_SLUG_RE.match(pr.head_ref_name)
        pr_slug = m_slug.group(1) if m_slug else None
        if pr_slug and is_slug_completed_only(pr_slug):
            continue
        cand_beans = sorted(set(slug_to_intent_beans.get(pr_slug or "", [])))
        used_beans.update(cand_beans)
        group_beans = [beans[n] for n in cand_beans if n in beans]
        title = group_beans[0].title if group_beans else pr.title
        rows.append(
            InFlightRow(
                bean_nums=cand_beans,
                target=pr.repo_name,
                title=_truncate(title),
                stage=_derive_stage(None, None, True),
                pr_ci=_derive_pr_ci(pr),
                live_runner="idle",
                notes=_derive_notes(group_beans, None, pr, None),
                sort_bucket=2,
                total_time=format_duration(branch_started(pr.head_ref_name), now),
                source=f"PR #{pr.number}",
                rank=_attempt_rank(None, None, pr),
            )
        )

    # 4. Any remaining `in-progress` beans that have no flow worktree, open PR, or live PID yet.
    for bnum, bean in sorted(beans.items()):
        if bnum in used_beans or bean.status != "in-progress":
            continue
        rows.append(
            InFlightRow(
                bean_nums=[bnum],
                target=_infer_target_from_bean(bean),
                title=_truncate(bean.title),
                stage="Not started",
                pr_ci="—",
                live_runner="idle",
                notes=_derive_notes([bean], None, None, None),
                sort_bucket=3,
                source="bean",
            )
        )

    def sort_key(r: InFlightRow) -> tuple[int, str, str]:
        first_bean = r.bean_nums[0] if r.bean_nums else "9999"
        return (r.sort_bucket, first_bean, r.title)

    rows = merge_rows_per_bean(rows)
    rows.sort(key=sort_key)
    return rows


def merge_rows_per_bean(rows: list[InFlightRow]) -> list[InFlightRow]:
    """Collapse rows sharing a bean into one: keep the live/most-advanced attempt, note the stale ones."""
    kept: list[InFlightRow] = []
    for row in sorted(rows, key=lambda r: r.rank, reverse=True):
        host = next((k for k in kept if row.bean_nums and set(k.bean_nums) & set(row.bean_nums)), None)
        if host is None:
            kept.append(row)
            continue
        host.bean_nums = sorted(set(host.bean_nums) | set(row.bean_nums))
        note = f"stale attempt {row.source} ({row.stage}; {row.live_runner})"
        host.notes = note if host.notes == "—" else f"{host.notes}; {note}"
    return kept


def render_markdown_table(rows: list[InFlightRow]) -> str:
    """Render in-flight bean rows as a single GitHub-Flavored Markdown table."""
    if not rows:
        return "No beans are currently in flight."

    headers = [
        "Bean #",
        "Target",
        "Title",
        "Agent",
        "Model",
        "Stage",
        "Time in Stage",
        "PR & CI",
        "Total Time",
        "Last Activity",
        "Notes",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(":" + "-" * max(len(h) - 1, 4) for h in headers) + " |",
    ]
    for row in rows:
        bean_cell = ", ".join(row.bean_nums) if row.bean_nums else "—"
        cells = [
            bean_cell,
            row.target,
            row.title,
            row.agent,
            row.model,
            row.stage,
            row.time_in_stage,
            row.pr_ci,
            row.total_time,
            row.last_activity,
            row.notes_cell(),
        ]
        lines.append("| " + " | ".join(_escape_cell(c) for c in cells) + " |")
    return "\n".join(lines)


def collect_progress(
    repo_root: Path,
    beans_dir: Path | None = None,
    *,
    no_gh: bool = False,
    no_ps: bool = False,
) -> list[InFlightRow]:
    """Collect live in-flight bean progress across all repos and active sessions."""
    resolved_root = repo_root.resolve()
    resolved_beans = (beans_dir or (resolved_root / ".beans")).resolve()

    beans = scan_beans(resolved_beans)
    intents = scan_intents(resolved_root / "todo")
    repos = discover_repos(resolved_root)
    worktrees = scan_worktrees(repos)
    prs = fetch_open_prs(repos, no_gh=no_gh)
    processes = scan_processes(no_ps=no_ps)
    live_by_key = match_live_flows(processes, worktrees, intents)
    return build_in_flight_rows(beans, intents, worktrees, prs, live_by_key)


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for `bean-progress`."""
    parser = argparse.ArgumentParser(description="Show live progress of all in-flight Holon beans.")
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[4]),
        help="Path to the harness repository root.",
    )
    parser.add_argument(
        "--beans-dir",
        default=None,
        help="Explicit directory containing bean markdown files (default: <repo-root>/.beans).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON array instead of a Markdown table.",
    )
    parser.add_argument(
        "--no-gh",
        action="store_true",
        help="Skip querying GitHub PRs via gh CLI.",
    )
    parser.add_argument(
        "--no-ps",
        action="store_true",
        help="Skip inspecting live host processes via ps.",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root)
    beans_dir = Path(args.beans_dir) if args.beans_dir else None
    rows = collect_progress(repo_root, beans_dir, no_gh=args.no_gh, no_ps=args.no_ps)

    if args.json:
        print(json.dumps([r.as_dict() for r in rows], indent=2))
    else:
        print(render_markdown_table(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
