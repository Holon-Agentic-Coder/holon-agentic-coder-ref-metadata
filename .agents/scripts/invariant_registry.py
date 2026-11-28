#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / ".agents" / "invariants.yml"
AGENTS_PATH = ROOT / "AGENTS.md"
BEANS_DIRECTORY = ROOT / ".beans"
STATUSES = {"enforced", "partial", "missing"}
RUNS_AT = {"pre-commit", "commit-msg", "ci", "flow-gate", "agent-hook", "on-demand"}
CLOSED_BEAN_STATUSES = {"completed", "scrapped"}
LIST_FIELDS = {"agents_rules", "open_beans", "runs_at", "checks"}
ENTRY_START = re.compile(r"^  - (\w+): (.*)$")
FIELD = re.compile(r"^    (\w+):(?: (.*))?$")
LIST_ITEM = re.compile(r"^      - (.*)$")
HARD_RULE_TITLE = re.compile(r"^- \*\*(.+?)\*\*")
TARGET_DIRECTORY = "apps"
TARGET_MAIN_WORKTREES = ("apps/holon-agentic-coder/main/", "apps/holon-coherence/main/")


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('\\"', '"')
    return value


def load_registry(path: Path = REGISTRY_PATH) -> list[dict]:
    lines = path.read_text().splitlines()
    if not lines or lines[0] != "invariants:":
        raise ValueError(f"{path.name}: first line must be 'invariants:'")
    entries: list[dict] = []
    current_list: list | None = None
    for number, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        if start := ENTRY_START.match(line):
            entries.append({start.group(1): unquote(start.group(2))})
            current_list = None
        elif field := FIELD.match(line):
            key, value = field.group(1), field.group(2)
            if not entries:
                raise ValueError(f"line {number}: field before the first entry")
            if key in LIST_FIELDS:
                entries[-1][key] = []
                current_list = entries[-1][key]
                if value not in (None, "[]"):
                    raise ValueError(f"line {number}: list field '{key}' takes block items or []")
                if value == "[]":
                    current_list = None
            else:
                entries[-1][key] = unquote(value or "")
                current_list = None
        elif item := LIST_ITEM.match(line):
            if current_list is None:
                raise ValueError(f"line {number}: list item outside a list field")
            current_list.append(unquote(item.group(1)))
        else:
            raise ValueError(f"line {number}: unsupported syntax: {line!r}")
    return entries


def hard_rule_titles(agents_text: str) -> list[str]:
    section = agents_text.split("## ⚖️ Hard Rules", 1)[1].split("\n---", 1)[0]
    return [match.group(1) for line in section.splitlines() if (match := HARD_RULE_TITLE.match(line))]


def bean_status(bean_number: str, beans_directory: Path = BEANS_DIRECTORY) -> str | None:
    for path in beans_directory.glob(f"*-{bean_number}--*.md"):
        found = re.search(r"^status:\s*(\S+)", path.read_text(), re.MULTILINE)
        return found.group(1) if found else None
    return None


def check_reference(check: str) -> str:
    _, _, reference = check.partition(":")
    return reference


def is_target_check(check: str) -> bool:
    return check_reference(check).startswith(f"{TARGET_DIRECTORY}/")


def target_checkout_present(root: Path) -> bool:
    return (root / TARGET_DIRECTORY).is_dir()


def target_reference_problems(name: str, check: str) -> list[str]:
    if check_reference(check).startswith(TARGET_MAIN_WORKTREES):
        return []
    return [f"{name}: target check outside a main worktree: {check}"]


def unverifiable_target_checks(entries: list[dict], root: Path = ROOT) -> list[str]:
    if target_checkout_present(root):
        return []
    return [check for entry in entries for check in entry.get("checks", []) if is_target_check(check)]


def resolve_test(reference: str, root: Path) -> str | None:
    file_part, _, test_name = reference.partition("::")
    path = root / file_part
    if not path.is_file():
        return f"test file missing: {file_part}"
    if not test_name or not re.search(rf"^\s*def {re.escape(test_name)}\(", path.read_text(), re.MULTILINE):
        return f"test not found: {reference}"
    return None


def resolve_workflow(reference: str, root: Path) -> str | None:
    file_part, _, job = reference.partition("#")
    path = root / file_part
    if not path.is_file():
        return f"workflow missing: {file_part}"
    jobs_block = path.read_text().split("\njobs:\n", 1)
    if len(jobs_block) < 2 or not re.search(rf"^  {re.escape(job)}:\s*$", jobs_block[1], re.MULTILINE):
        return f"workflow job not found: {reference}"
    return None


def resolve_file(reference: str, root: Path) -> str | None:
    return None if (root / reference).is_file() else f"file missing: {reference}"


RESOLVERS = {"test": resolve_test, "workflow": resolve_workflow, "hook": resolve_file, "script": resolve_file}


def resolve_check(check: str, root: Path = ROOT) -> str | None:
    kind, _, reference = check.partition(":")
    if kind not in RESOLVERS or not reference:
        return f"unknown check form: {check!r}"
    return RESOLVERS[kind](reference, root)


def entry_problems(entry: dict, root: Path = ROOT) -> list[str]:
    name = entry.get("id", "<no id>")
    problems = []
    if entry.get("status") not in STATUSES:
        problems.append(f"{name}: status must be one of {sorted(STATUSES)}")
    for place in entry.get("runs_at", []):
        if place not in RUNS_AT:
            problems.append(f"{name}: unknown runs_at {place!r}")
    if not entry.get("runs_at"):
        problems.append(f"{name}: runs_at is empty")
    if entry.get("status") == "enforced" and not entry.get("checks"):
        problems.append(f"{name}: enforced without a check")
    if entry.get("status") == "partial" and not entry.get("checks"):
        problems.append(f"{name}: partial without a check; mark it missing")
    targets_absent = not target_checkout_present(root)
    for check in entry.get("checks", []):
        if is_target_check(check):
            problems += target_reference_problems(name, check)
            if targets_absent:
                continue
        if (problem := resolve_check(check, root)) is not None:
            problems.append(f"{name}: {problem}")
    return problems


def open_bean_problems(entry: dict, beans_directory: Path = BEANS_DIRECTORY) -> list[str]:
    name = entry.get("id", "<no id>")
    if entry.get("status") not in {"missing", "partial"}:
        return []
    beans = entry.get("open_beans", [])
    if not beans:
        return [f"{name}: {entry.get('status')} without an open bean"]
    problems = []
    for bean in beans:
        status = bean_status(bean, beans_directory)
        if status is None:
            problems.append(f"{name}: bean {bean} does not exist")
        elif status in CLOSED_BEAN_STATUSES:
            problems.append(f"{name}: bean {bean} is {status}; update the entry")
    return problems


def unmapped_hard_rules(entries: list[dict], agents_text: str) -> list[str]:
    mapped = {rule for entry in entries for rule in entry.get("agents_rules", [])}
    return [title for title in hard_rule_titles(agents_text) if title not in mapped]


def dangling_agents_rules(entries: list[dict], agents_text: str) -> list[str]:
    titles = set(hard_rule_titles(agents_text))
    return [rule for entry in entries for rule in entry.get("agents_rules", []) if rule not in titles]


def all_problems(entries: list[dict] | None = None) -> list[str]:
    entries = load_registry() if entries is None else entries
    agents_text = AGENTS_PATH.read_text()
    problems = [f"hard rule without a registry entry: {title}" for title in unmapped_hard_rules(entries, agents_text)]
    problems += [
        f"registry names a hard rule AGENTS.md lacks: {rule}" for rule in dangling_agents_rules(entries, agents_text)
    ]
    for entry in entries:
        problems += entry_problems(entry) + open_bean_problems(entry)
    return problems


def main() -> int:
    entries = load_registry()
    problems = all_problems(entries)
    for problem in problems:
        print(problem, file=sys.stderr)
    unverified = len(unverifiable_target_checks(entries))
    if unverified:
        print(f"{unverified} target-repo checks unverified: {TARGET_DIRECTORY}/ is not checked out here")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
