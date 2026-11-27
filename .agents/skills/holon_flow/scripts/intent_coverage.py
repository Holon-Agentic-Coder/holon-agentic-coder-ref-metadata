from __future__ import annotations

import json
import re
import subprocess
import sys
from collections.abc import Collection, Mapping
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parents[4]
BEAN_SECTIONS = ("acceptance", "check", "common acceptance", "gaps to close", "next step", "done when")
SECTION_LIST = "Acceptance, Check, Common acceptance, Gaps to close, Next step or Done when"
DEFAULT_PR_REPO = "Holon-Agentic-Coder/holon-agentic-coder"
PR_REASON = re.compile(r"delivered by PR\s*#(\d+)", re.IGNORECASE)
INTENT_ACCEPTANCE_FIELDS = ("acceptance_criteria", "acceptance")
MATCH_THRESHOLD = 0.6
STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "in",
        "into",
        "is",
        "it",
        "its",
        "of",
        "on",
        "or",
        "that",
        "the",
        "this",
        "to",
        "with",
        "without",
        "when",
        "then",
        "not",
        "no",
        "must",
        "should",
        "each",
        "every",
        "any",
        "all",
        "only",
        "also",
        "can",
        "may",
        "via",
        "per",
    }
)
LIST_ITEM = re.compile(r"^\s*(?:[-*]\s+(?:\[[ xX]\]\s+)?|\d+[.)]\s+)(.*\S)\s*$")
TABLE_SEPARATOR = re.compile(r"^\s*\|?\s*:?-{2,}")


def bean_file(bean_id: str, root: Path = HARNESS_ROOT) -> Path | None:
    matches = sorted((root / ".beans").glob(f"*-{bean_id}--*.md"))
    return matches[0] if matches else None


def is_section_heading(heading: str) -> bool:
    return heading.strip().lower().startswith(BEAN_SECTIONS)


def has_acceptance_section(markdown: str) -> bool:
    return any(
        is_section_heading(heading.group(1))
        for heading in (re.match(r"^##\s+(.*?)\s*$", line) for line in markdown.splitlines())
        if heading
    )


def bean_items(markdown: str) -> list[str]:
    items: list[str] = []
    in_section = False
    for line in markdown.splitlines():
        heading = re.match(r"^##\s+(.*?)\s*$", line)
        if heading:
            in_section = is_section_heading(heading.group(1))
            continue
        if not in_section:
            continue
        item = LIST_ITEM.match(line)
        if item:
            items.append(item.group(1).strip())
        elif line.lstrip().startswith("|") and not TABLE_SEPARATOR.match(line):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            items.append(" ".join(cell for cell in cells if cell))
        elif items and line.strip() and line.startswith((" ", "\t")) and not line.lstrip().startswith("|"):
            items[-1] = f"{items[-1]} {line.strip()}"
    return items


def intent_items(intent: Mapping[str, object]) -> list[str]:
    found: list[str] = []
    for field in INTENT_ACCEPTANCE_FIELDS:
        value = intent.get(field)
        if isinstance(value, str):
            found.append(value)
        elif isinstance(value, list):
            found.extend(str(entry) for entry in value)
    return found


def tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower().replace("`", " "))
    return {stem(word) for word in words if word not in STOPWORDS and len(word) > 1}


def stem(word: str) -> str:
    for suffix in ("ing", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def code_spans_present(bean_item: str, intent_item: str) -> bool:
    return all(span.lower() in intent_item.lower() for span in re.findall(r"`([^`]+)`", bean_item))


def similarity(bean_item: str, intent_item: str) -> float:
    wanted = tokens(bean_item)
    if not wanted:
        return 1.0
    return len(wanted & tokens(intent_item)) / len(wanted)


def coverage_file(bean_id: str, root: Path = HARNESS_ROOT) -> dict[str, object]:
    path = root / "todo" / f"intent-coverage-{bean_id}.json"
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def explicit_mapping(bean_id: str, root: Path = HARNESS_ROOT) -> dict[str, str]:
    data = coverage_file(bean_id, root)
    return {
        str(key): str(value) for key, value in data.items() if key != "excluded" and isinstance(value, str) and value
    }


def exclusions(bean_id: str, root: Path = HARNESS_ROOT) -> dict[str, dict[str, object]]:
    raw = coverage_file(bean_id, root).get("excluded")
    if not isinstance(raw, dict):
        return {}
    return {str(item): entry for item, entry in raw.items() if isinstance(entry, dict)}


def pr_merged(number: int, repo: str = DEFAULT_PR_REPO) -> bool | None:
    try:
        result = subprocess.run(
            ["gh", "pr", "view", str(number), "--repo", repo, "--json", "state"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode == 0:
        return json.loads(result.stdout).get("state") == "MERGED"
    if "could not resolve" in result.stderr.lower() or "no pull requests found" in result.stderr.lower():
        return False
    return None


def excluded_refusals(excluded: Mapping[str, Mapping[str, object]]) -> tuple[dict[str, str], list[str]]:
    invalid: dict[str, str] = {}
    notes: list[str] = []
    for item, entry in excluded.items():
        reason = str(entry.get("reason") or "").strip()
        if not reason:
            invalid[item] = "exclusion has no reason"
            continue
        pr_match = PR_REASON.search(reason)
        number = entry.get("pr") if isinstance(entry.get("pr"), int) else int(pr_match.group(1)) if pr_match else None
        if number is None:
            if not reason.lower().startswith("out of scope:") or len(reason) <= len("out of scope:") + 1:
                invalid[item] = "reason must be 'delivered by PR #N' or 'out of scope: <why>'"
            else:
                notes.append(f"excluded (out of scope): {item} -- {reason}")
            continue
        merged = pr_merged(number, str(entry.get("repo") or DEFAULT_PR_REPO))
        if merged is False:
            invalid[item] = f"PR #{number} is not merged"
        elif merged is None:
            notes.append(f"WARNING: could not verify PR #{number} offline; excluded {item} -- {reason}")
        else:
            notes.append(f"excluded (PR #{number} merged): {item} -- {reason}")
    return invalid, notes


def uncovered_items(
    bean_list: list[str],
    intent_list: list[str],
    mapping: Mapping[str, str],
    excluded: Collection[str] = (),
) -> list[str]:
    missing = []
    for item in bean_list:
        if item in excluded:
            continue
        mapped = mapping.get(item)
        if mapped is not None and mapped in intent_list and tokens(item) & tokens(mapped):
            continue
        if any(
            code_spans_present(item, candidate) and similarity(item, candidate) >= MATCH_THRESHOLD
            for candidate in intent_list
        ):
            continue
        missing.append(item)
    return missing


def coverage_refusal(intent: Mapping[str, object], bean_id: str, root: Path = HARNESS_ROOT) -> str | None:
    path = bean_file(bean_id, root)
    if path is None:
        return (
            f"Bean {bean_id} has no file under .beans/, so its acceptance items cannot be checked against the intent."
        )
    markdown = path.read_text(encoding="utf-8")
    if not has_acceptance_section(markdown):
        return f"Bean {bean_id}: bean has no acceptance section ({SECTION_LIST})."
    bean_list = bean_items(markdown)
    if not bean_list:
        return f"Bean {bean_id} lists no acceptance items in its acceptance section."
    invalid, notes = excluded_refusals(exclusions(bean_id, root))
    for note in notes:
        print(note, file=sys.stderr)
    bad = [f"  - {item}: {why}" for item, why in invalid.items()]
    if bad:
        return f"Invalid exclusions in todo/intent-coverage-{bean_id}.json:\n" + "\n".join(bad)
    excluded = {item for item in exclusions(bean_id, root) if item not in invalid}
    missing = uncovered_items(bean_list, intent_items(intent), explicit_mapping(bean_id, root), excluded)
    if not missing:
        return None
    listing = "\n".join(f"  - {item}" for item in missing)
    return (
        f"Intent does not cover {len(missing)} of {len(bean_list)} acceptance items of bean {bean_id}; add each to "
        f"the intent acceptance_criteria or map or exclude it in todo/intent-coverage-{bean_id}.json:\n{listing}"
    )
