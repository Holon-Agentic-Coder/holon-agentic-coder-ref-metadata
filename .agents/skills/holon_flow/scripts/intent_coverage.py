from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parents[4]
BEAN_SECTIONS = ("acceptance", "check", "common acceptance", "gaps to close", "next step")
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


def bean_items(markdown: str) -> list[str]:
    items: list[str] = []
    in_section = False
    for line in markdown.splitlines():
        heading = re.match(r"^##\s+(.*?)\s*$", line)
        if heading:
            name = re.sub(r"\s*[(:].*$", "", heading.group(1)).strip().lower()
            in_section = name in BEAN_SECTIONS
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


def explicit_mapping(bean_id: str, root: Path = HARNESS_ROOT) -> dict[str, str]:
    path = root / "todo" / f"intent-coverage-{bean_id}.json"
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {str(key): str(value) for key, value in data.items() if value}


def uncovered_items(bean_list: list[str], intent_list: list[str], mapping: Mapping[str, str]) -> list[str]:
    missing = []
    for item in bean_list:
        mapped = mapping.get(item)
        if mapped is not None and mapped in intent_list:
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
    bean_list = bean_items(path.read_text(encoding="utf-8"))
    if not bean_list:
        return f"Bean {bean_id} lists no acceptance items in its Acceptance, Check or Common acceptance sections."
    missing = uncovered_items(bean_list, intent_items(intent), explicit_mapping(bean_id, root))
    if not missing:
        return None
    listing = "\n".join(f"  - {item}" for item in missing)
    return (
        f"Intent does not cover {len(missing)} of {len(bean_list)} acceptance items of bean {bean_id}; add each to "
        f"the intent acceptance_criteria or map it in todo/intent-coverage-{bean_id}.json:\n{listing}"
    )
