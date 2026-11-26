#!/usr/bin/env python3
"""Deterministic importer: open harness beans -> GitHub Issues (bean 0215).

Standard library only; the real import shells out to gh. The default mode is a dry
run: it renders every payload, label set and dependency link under todo/ and calls no
GitHub write API. The real import needs --apply and runs only on the maintainer's word.

    uv run python .agents/scripts/beans_to_issues.py              # dry run
    uv run python .agents/scripts/beans_to_issues.py --apply      # real import
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
ORG = "Holon-Agentic-Coder"
REPOS = ("holon-agentic-coder", "holon-coherence")
OPEN_STATUSES = ("todo", "draft", "in-progress")
ID_PREFIX = "holon-agentic-coder-ref-metadata-"
ROUTING_TAGS = {"holon-agentic-coder", "holon-coherence", "harness", "dev-env"}
NOT_MIGRATED_TAGS = {"harness", "dev-env"}
PRIORITY = {"critical": "P0", "high": "P1", "normal": "P2", "medium": "P2", "low": "P3"}
TYPES = {"bug", "feature", "task"}
BLOCKED_KEYS = ("blocked_by", "blocked-by")
BLOCKING_KEYS = ("blocking", "blocks")
KNOWN_KEYS = {"title", "status", "type", "priority", "tags", "labels", "parent", "created_at", "updated_at",
              *BLOCKED_KEYS, *BLOCKING_KEYS}
LABEL_COLORS = {"type": "1d76db", "priority": "d93f0b", "status": "fbca04", "tag": "ededed"}
PATH_RE = re.compile(r"(?<!\w)(?:\.beans|todo|\.agents)(?:/[\w.*{}<>@+~-]*)*/?(?![\w])")
ID_RE = re.compile(r"\b0\d{3}\b")
FULL_ID_RE = re.compile(re.escape(ID_PREFIX) + r"(\d{4})")
BEAN_LIST_RE = re.compile(
    r"\b[Bb]eans?\s+(\d{4}(?:\s*[-–]\s*\d{4})?(?:(?:\s*,\s*|\s*,?\s+and\s+|\s*/\s*|\s*&\s*)\d{4}(?:\s*[-–]\s*\d{4})?)*)"
)
PLACEHOLDER_RE = re.compile(r"\{\{issue:(\d{4})\}\}")


# ---------------------------------------------------------------- parsing

def parse_bean(path: Path) -> dict:
    """Parse one bean file: the frontmatter into a dict (scalars and lists) plus the body."""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path.name}: no frontmatter")
    end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    fm: dict = {}
    key = None
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        item = re.match(r"^\s+-\s+(.*)$", line)
        if item and key is not None:
            if not isinstance(fm.get(key), list):
                fm[key] = []
            fm[key].append(_scalar(item.group(1)))
            continue
        kv = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not kv:
            if line.startswith((" ", "\t")) and key is not None:  # folded continuation of a scalar
                prev = fm.get(key)
                joined = (prev + " " if isinstance(prev, str) and prev else "") + line.strip()
                if not isinstance(prev, list) or not prev:
                    fm[key] = _scalar(joined) if not joined.startswith(('"', "'")) or joined[-1] == joined[0] else joined
            continue
        key, val = kv.group(1), kv.group(2).strip()
        if val.startswith("[") and val.endswith("]"):
            fm[key] = [_scalar(v) for v in val[1:-1].split(",") if v.strip()]
        elif val == "":
            fm[key] = []
        else:
            fm[key] = _scalar(val)
    m = re.search(r"-(\d{4})--", path.name)
    bean_id = m.group(1) if m else None
    return {"id": bean_id, "file": path.name, "fm": fm, "body": "\n".join(lines[end + 1:]).strip("\n")}


def _scalar(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def as_list(v) -> list:
    if v is None or v == "":
        return []
    return v if isinstance(v, list) else [v]


def bean_ref(value: str) -> str | None:
    m = re.search(r"(\d{4})\s*$", str(value))
    return m.group(1) if m else None


def load_beans(beans_dir: Path) -> dict[str, dict]:
    beans = {}
    for p in sorted(beans_dir.glob(ID_PREFIX + "*.md")):
        b = parse_bean(p)
        if b["id"]:
            beans[b["id"]] = b
    return beans


# ---------------------------------------------------------------- routing

def route(bean: dict) -> tuple[str | None, str, str]:
    """Return (repo or None, basis, reason). repo None means not migrated."""
    fm = bean["fm"]
    tags = {t.lower() for t in as_list(fm.get("tags")) + as_list(fm.get("labels"))}
    text = (fm.get("title", "") + "\n" + bean["body"]).replace(ID_PREFIX, "")
    hits = {r: tags & {r} for r in REPOS}
    targets = [r for r in REPOS if hits[r]]
    if len(targets) == 1:
        return targets[0], "tag", ""
    if len(targets) == 2:
        counts = {r: len(re.findall(re.escape(r), text)) for r in REPOS}
        pick = max(REPOS, key=lambda r: (counts[r], r == REPOS[0]))
        return pick, "tag-ambiguous", f"both target tags; picked {pick} by mention count {counts}"
    if tags & NOT_MIGRATED_TAGS:
        why = "dev-env" if "dev-env" in tags else "harness-only"
        return None, "tag", why
    counts = {r: len(re.findall(re.escape(r), text)) for r in REPOS}
    best = max(counts.values())
    winners = [r for r in REPOS if counts[r] == best]
    if best and len(winners) == 1:
        return winners[0], "mention", f"mention counts {counts}"
    return None, "none", "harness-only: no target tag or mention"


# ---------------------------------------------------------------- stripping

def _expand(spec: str) -> list[str]:
    out = []
    for part in re.split(r"\s*(?:,|and|/|&)\s*", spec.strip()):
        part = part.strip()
        if not part:
            continue
        rng = re.match(r"^(\d{4})\s*[-–]\s*(\d{4})$", part)
        if rng:
            out.extend(f"{n:04d}" for n in range(int(rng.group(1)), int(rng.group(2)) + 1))
        else:
            out.append(part)
    return out


def strip_text(text: str, migrated: set[str], stats: Counter | None = None,
               known: set[str] = frozenset(), self_id: str | None = None) -> str:
    """Remove harness references. Migrated bean refs become {{issue:NNNN}} placeholders."""
    stats = stats if stats is not None else Counter()

    def ref(bid: str) -> str:
        if bid == self_id:
            stats["bean_ref_self"] += 1
            return "this issue"
        if bid in migrated:
            stats["bean_ref_to_issue"] += 1
            return "{{issue:" + bid + "}}"
        stats["bean_ref_dropped"] += 1
        return "an earlier work item"

    def lst(m: re.Match) -> str:
        return ", ".join(ref(b) for b in _expand(m.group(1)))

    combined = re.compile("|".join(f"(?P<{n}>{p.pattern})" for n, p in
                                   (("full", FULL_ID_RE), ("list", BEAN_LIST_RE), ("path", PATH_RE), ("bare", ID_RE))))

    def sub(m: re.Match) -> str:
        if m.group("full"):
            return ref(FULL_ID_RE.fullmatch(m.group("full")).group(1))
        if m.group("list"):
            return lst(BEAN_LIST_RE.fullmatch(m.group("list")))
        if m.group("path"):
            stats["path_removed"] += 1
            return "[harness path]"
        return ref(m.group("bare")) if m.group("bare") in known else m.group("bare")

    text = combined.sub(sub, text)
    return text


def residual_refs(text: str, known_ids: set[str]) -> list[str]:
    return [m for m in ID_RE.findall(PLACEHOLDER_RE.sub("", text)) if m in known_ids]


# ---------------------------------------------------------------- mapping

def build_plan(beans: dict[str, dict]) -> dict:
    open_beans = {i: b for i, b in beans.items() if b["fm"].get("status") in OPEN_STATUSES}
    routes = {i: route(b) for i, b in open_beans.items()}
    migrated = {i for i, r in routes.items() if r[0]}
    not_migrated = [
        {"id": i, "title": open_beans[i]["fm"].get("title", ""), "status": open_beans[i]["fm"].get("status"),
         "reason": routes[i][2], "tags": as_list(open_beans[i]["fm"].get("tags"))}
        for i in sorted(open_beans) if not routes[i][0]
    ]
    known = set(beans)
    fidelity: dict[str, Counter] = {k: Counter() for k in
                                    ("title", "body", "type", "priority", "status", "tags", "dependencies", "parent")}
    unmapped: list[dict] = []
    issues, label_sets = {}, {r: {} for r in REPOS}
    edges_blocked, edges_parent, dropped_edges = set(), set(), []

    for bid in sorted(migrated):
        b, fm = open_beans[bid], open_beans[bid]["fm"]
        repo = routes[bid][0]
        stats = Counter()
        title = re.sub(r"\s+", " ", strip_text(fm.get("title", ""), migrated, stats, known, bid)).strip()
        title = re.sub(r"\{\{issue:\d{4}\}\}", "", title).strip() if stats["bean_ref_to_issue"] else title
        fidelity["title"]["exact" if title == fm.get("title") else "stripped"] += 1
        body = strip_text(b["body"], migrated, stats, known, bid)
        fidelity["body"]["exact" if body == b["body"] else "stripped"] += 1
        left = residual_refs(title + "\n" + body, known)
        if left:
            unmapped.append({"bean": bid, "field": "body", "issue": "possible bean ids remain: " + ", ".join(sorted(set(left)))})
        pre = re.findall(r"(?<![\w&])#\d+", b["body"])
        if pre:
            unmapped.append({"bean": bid, "field": "body", "issue": f"{len(pre)} existing #N reference(s) "
                             f"({', '.join(sorted(set(pre))[:6])}) will auto-link to same-numbered issues"})
        typ = fm.get("type")
        if typ in TYPES:
            fidelity["type"]["exact"] += 1
        else:
            fidelity["type"]["defaulted" if not typ else "coerced"] += 1
            unmapped.append({"bean": bid, "field": "type", "issue": f"type {typ!r} has no label; used task"})
            typ = "task" if typ not in ("epic", "milestone") else "feature"
            if fm.get("type") in ("epic", "milestone"):
                unmapped[-1]["issue"] = f"type {fm.get('type')!r} has no label; used feature"
        pri_raw = fm.get("priority")
        pri = PRIORITY.get(pri_raw)
        if pri_raw is None:
            pri = "P2"
            fidelity["priority"]["defaulted"] += 1
            unmapped.append({"bean": bid, "field": "priority", "issue": "missing; used P2"})
        elif pri_raw == "medium":
            fidelity["priority"]["coerced"] += 1
        elif pri is None:
            pri = "P2"
            fidelity["priority"]["defaulted"] += 1
            unmapped.append({"bean": bid, "field": "priority", "issue": f"unknown {pri_raw!r}; used P2"})
        else:
            fidelity["priority"]["exact"] += 1
        labels = [f"type:{typ}", f"priority:{pri}"]
        status = fm.get("status")
        if status in ("in-progress", "draft"):
            labels.append(f"status:{status}")
            fidelity["status"]["labelled"] += 1
        else:
            fidelity["status"]["exact"] += 1
        tags = []
        for t in as_list(fm.get("tags")) + as_list(fm.get("labels")):
            t = str(t).strip().lower()
            if t in ROUTING_TAGS:
                fidelity["tags"]["routing_dropped"] += 1
            elif re.fullmatch(r"\d{4}", t):
                fidelity["tags"]["bean_id_dropped"] += 1
                unmapped.append({"bean": bid, "field": "tags", "issue": f"tag {t!r} is a bean id; dropped"})
            elif t not in tags:
                tags.append(t)
                fidelity["tags"]["exact"] += 1
        labels += tags
        for lab in labels:
            kind = lab.split(":")[0] if lab.split(":")[0] in LABEL_COLORS else "tag"
            label_sets[repo][lab] = {"color": LABEL_COLORS[kind], "description": ""}
        for k in fm:
            if k not in KNOWN_KEYS:
                unmapped.append({"bean": bid, "field": k, "issue": "frontmatter key has no issue field; dropped"})
        for k in ("created_at", "updated_at"):
            if k in fm:
                fidelity.setdefault(k, Counter())["dropped_api_sets_it"] += 1
        blockers = {bean_ref(v) for k in BLOCKED_KEYS for v in as_list(fm.get(k))}
        blocking = {bean_ref(v) for k in BLOCKING_KEYS for v in as_list(fm.get(k))}
        for blocker in sorted(x for x in blockers if x):
            _edge(edges_blocked, dropped_edges, fidelity, migrated, bid, blocker, "blocked_by")
        for blocked in sorted(x for x in blocking if x):
            _edge(edges_blocked, dropped_edges, fidelity, migrated, blocked, bid, "blocking")
        parent = bean_ref(fm["parent"]) if fm.get("parent") else None
        if parent:
            if parent in migrated:
                edges_parent.add((parent, bid))
                fidelity["parent"]["mapped"] += 1
            else:
                fidelity["parent"]["dropped_not_open"] += 1
                dropped_edges.append({"kind": "parent", "child": bid, "parent": parent, "why": "parent not migrated"})
        issues[bid] = {"bean": bid, "repo": f"{ORG}/{routes[bid][0]}", "route_basis": routes[bid][1],
                       "title": title, "body": body, "labels": labels, "state": "open",
                       "ref_stats": dict(stats)}
    return {"issues": issues, "labels": label_sets, "blocked_by": sorted(edges_blocked),
            "sub_issues": sorted(edges_parent), "dropped_edges": dropped_edges, "not_migrated": not_migrated,
            "fidelity": {k: dict(v) for k, v in fidelity.items()}, "unmapped": unmapped,
            "open_total": len(open_beans), "routes": {i: routes[i] for i in routes}}


def _edge(edges, dropped, fidelity, migrated, blocked, blocker, kind):
    if blocked in migrated and blocker in migrated and blocked != blocker:
        edges.add((blocked, blocker))
        fidelity["dependencies"]["mapped"] += 1
    else:
        fidelity["dependencies"]["dropped_not_migrated"] += 1
        dropped.append({"kind": kind, "blocked": blocked, "blocker": blocker, "why": "one side is not an open migrated bean"})


# ---------------------------------------------------------------- dry run

def render_dry_run(plan: dict, out: Path, mapping: dict) -> Path:
    out.mkdir(parents=True, exist_ok=True)
    for repo in REPOS:
        (out / "issues" / repo).mkdir(parents=True, exist_ok=True)
    for bid, iss in plan["issues"].items():
        payload = {**iss, "already_imported": bid in mapping}
        d = out / "issues" / iss["repo"].split("/")[1]
        (d / f"{bid}.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        (d / f"{bid}.md").write_text(iss["body"] + "\n", encoding="utf-8")
    (out / "labels.json").write_text(json.dumps(plan["labels"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    deps = {"blocked_by": [{"blocked": a, "blocker": b} for a, b in plan["blocked_by"]],
            "sub_issues": [{"parent": a, "child": b} for a, b in plan["sub_issues"]],
            "dropped": plan["dropped_edges"]}
    (out / "dependencies.json").write_text(json.dumps(deps, indent=2) + "\n", encoding="utf-8")
    (out / "not_migrated.json").write_text(json.dumps(plan["not_migrated"], indent=2) + "\n", encoding="utf-8")
    (out / "unmapped.json").write_text(json.dumps(plan["unmapped"], indent=2) + "\n", encoding="utf-8")
    (out / "report.md").write_text(render_report(plan, mapping), encoding="utf-8")
    return out / "report.md"


def render_report(plan: dict, mapping: dict) -> str:
    per_repo = Counter(i["repo"].split("/")[1] for i in plan["issues"].values())
    basis = Counter(i["route_basis"] for i in plan["issues"].values())
    totals = Counter()
    for i in plan["issues"].values():
        totals.update(i["ref_stats"])
    lines = ["# Beans to issues: dry run report", "",
             f"- Open beans scanned: {plan['open_total']}",
             f"- To migrate: {len(plan['issues'])} ({', '.join(f'{r}: {per_repo[r]}' for r in REPOS)})",
             f"- Routing basis: {dict(basis)}",
             f"- Not migrated: {len(plan['not_migrated'])}",
             f"- Already in the mapping file: {sum(1 for b in plan['issues'] if b in mapping)}",
             f"- Dependencies (blocked by): {len(plan['blocked_by'])}; sub-issue links: {len(plan['sub_issues'])}; "
             f"edges dropped: {len(plan['dropped_edges'])}",
             f"- Harness references: {totals['bean_ref_to_issue']} bean refs become #N, "
             f"{totals['bean_ref_dropped']} refs to unmigrated beans reworded, {totals['path_removed']} harness paths removed",
             f"- Labels per repository: {', '.join(f'{r}: {len(plan['labels'][r])}' for r in REPOS)}",
             "", "## Per-field fidelity", "", "| Field | Outcome counts |", "| :-- | :-- |"]
    for k, v in plan["fidelity"].items():
        lines.append(f"| {k} | {', '.join(f'{a}: {b}' for a, b in sorted(v.items())) or 'n/a'} |")
    lines += ["", "## Not migrated", "", "| Bean | Status | Reason | Title |", "| :-- | :-- | :-- | :-- |"]
    for n in plan["not_migrated"]:
        lines.append(f"| {n['id']} | {n['status']} | {n['reason']} | {n['title'][:80]} |")
    lines += ["", "## Could not be mapped", ""]
    lines += [f"- {u['bean']} {u['field']}: {u['issue']}" for u in plan["unmapped"]] or ["- none"]
    lines += ["", "## Dropped dependency and parent edges", ""]
    for e in plan["dropped_edges"]:
        lines.append("- " + ", ".join(f"{k}={v}" for k, v in e.items()))
    if not plan["dropped_edges"]:
        lines.append("- none")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- real import

def gh(args: list[str], runner=subprocess.run, stdin: str | None = None) -> str:
    r = runner(["gh", *args], capture_output=True, text=True, input=stdin)
    if r.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])} failed: {r.stderr.strip()}")
    return r.stdout.strip()


def load_mapping(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def save_mapping(path: Path, mapping: dict) -> None:
    path.write_text(json.dumps(mapping, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def apply_import(plan: dict, map_path: Path, runner=subprocess.run) -> dict:
    """Real import: labels, pass 1 create, pass 2 link bodies, then dependencies and sub-issues."""
    mapping = load_mapping(map_path)
    for repo, labels in plan["labels"].items():
        for name, meta in sorted(labels.items()):
            gh(["label", "create", name, "--repo", f"{ORG}/{repo}", "--color", meta["color"], "--force"], runner)
    for bid, iss in sorted(plan["issues"].items()):
        if bid in mapping:
            continue
        body = PLACEHOLDER_RE.sub("(link pending)", iss["body"])
        args = ["issue", "create", "--repo", iss["repo"], "--title", iss["title"], "--body-file", "-"]
        for lab in iss["labels"]:
            args += ["--label", lab]
        url = gh(args, runner, stdin=body)
        mapping[bid] = {"repo": iss["repo"].split("/")[1], "issue": int(url.rstrip("/").rsplit("/", 1)[1]),
                        "linked": False, "deps": []}
        save_mapping(map_path, mapping)
    for bid, iss in sorted(plan["issues"].items()):
        ent = mapping[bid]
        if ent["linked"]:
            continue
        body = PLACEHOLDER_RE.sub(lambda m: _link(m.group(1), ent["repo"], mapping), iss["body"])
        gh(["issue", "edit", str(ent["issue"]), "--repo", iss["repo"], "--body-file", "-"], runner, stdin=body)
        ent["linked"] = True
        save_mapping(map_path, mapping)
    for kind, edges in (("blocked_by", plan["blocked_by"]), ("sub_issues", plan["sub_issues"])):
        for a, b in edges:
            holder, other = (a, b)
            key = f"{kind}:{other}"
            ent = mapping[holder]
            if key in ent["deps"]:
                continue
            oent = mapping[other]
            oid = gh(["api", f"repos/{ORG}/{oent['repo']}/issues/{oent['issue']}", "--jq", ".id"], runner)
            if kind == "blocked_by":
                gh(["api", "-X", "POST", f"repos/{ORG}/{ent['repo']}/issues/{ent['issue']}/dependencies/blocked_by",
                    "-F", f"issue_id={oid}"], runner)
            else:  # edge is (parent, child): the parent holds the sub-issue
                gh(["api", "-X", "POST", f"repos/{ORG}/{ent['repo']}/issues/{ent['issue']}/sub_issues",
                    "-F", f"sub_issue_id={oid}"], runner)
            ent["deps"].append(key)
            save_mapping(map_path, mapping)
    return mapping


def _link(bid: str, from_repo: str, mapping: dict) -> str:
    ent = mapping[bid]
    return f"#{ent['issue']}" if ent["repo"] == from_repo else f"{ORG}/{ent['repo']}#{ent['issue']}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--beans-dir", type=Path, default=ROOT / ".beans")
    ap.add_argument("--out", type=Path, default=ROOT / "todo" / "beans-to-issues-dry-run")
    ap.add_argument("--map", type=Path, default=ROOT / ".agents" / "beans_to_issues_map.json")
    ap.add_argument("--apply", action="store_true", help="real import (writes to GitHub); default is a dry run")
    args = ap.parse_args(argv)
    plan = build_plan(load_beans(args.beans_dir))
    mapping = load_mapping(args.map)
    report = render_dry_run(plan, args.out, mapping)
    print(f"dry-run report: {report}")
    if args.apply:
        apply_import(plan, args.map)
        print(f"imported; mapping in {args.map}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
