"""Tests for the ledger merge in resolve_known: the base side stays byte for byte, only new rows are appended."""

import difflib
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent / ".agents" / "skills" / "resolve_conflict" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import resolve_known  # noqa: E402


def row(n: int, ts: str) -> str:
    return json.dumps({"id": n, "created_at": ts})


def text(*rows: str) -> str:
    return "".join(r + "\n" for r in rows)


MAIN = [row(1, "2026-01-05T00:00:00Z"), row(2, "2026-01-01T00:00:00Z"), row(3, "2026-01-09T00:00:00Z")]


def test_main_order_preserved_when_unsorted():
    out, kept, added = resolve_known.merge_ledger_text(text(*MAIN), text(*MAIN, row(4, "2026-01-02T00:00:00Z")))
    assert out.startswith(text(*MAIN))
    assert (kept, added) == (3, 1)


def test_branch_rows_appended_sorted():
    new = [row(5, "2026-02-03T00:00:00Z"), row(4, "2026-02-01T00:00:00Z")]
    out, _, _ = resolve_known.merge_ledger_text(text(*MAIN), text(*MAIN, *new))
    assert out.splitlines()[3:] == [new[1], new[0]]


def test_shared_row_appears_once():
    out, _, added = resolve_known.merge_ledger_text(text(*MAIN), text(MAIN[1], row(4, "2026-02-01T00:00:00Z")))
    assert out.splitlines().count(MAIN[1]) == 1
    assert added == 1


def test_mixed_z_and_offset_sort():
    a = row(4, "2026-02-01T10:00:00+00:00")
    b = row(5, "2026-02-01T09:00:00Z")
    c = row(6, "2026-02-01T09:30:00.5+00:00")
    out, _, _ = resolve_known.merge_ledger_text(text(*MAIN), text(a, b, c))
    assert out.splitlines()[3:] == [b, c, a]


def test_valid_jsonl_no_markers_and_diff_only_adds():
    main_text = text(*MAIN)
    out, _, _ = resolve_known.merge_ledger_text(main_text, text(row(4, "2026-02-01T00:00:00Z"), MAIN[0]))
    assert not any(line.startswith(("<<<<<<<", "=======", ">>>>>>>")) for line in out.splitlines())
    assert out.endswith("\n")
    for line in out.splitlines():
        json.loads(line)
    diff = list(difflib.unified_diff(main_text.splitlines(), out.splitlines(), lineterm="", n=0))
    assert not [d for d in diff if d.startswith("-") and not d.startswith("---")]
    assert [d for d in diff if d.startswith("+") and not d.startswith("+++")]


def test_base_stage_flip(monkeypatch, tmp_path):
    stages = {2: text(*MAIN), 3: text(MAIN[1], row(9, "2026-03-01T00:00:00Z"))}
    monkeypatch.setattr(resolve_known, "stage", lambda n, path, cwd: stages[n])
    resolve_known.merge_jsonl("l.jsonl", str(tmp_path), base_stage=2)
    lines = (tmp_path / "l.jsonl").read_text().splitlines()
    assert lines[:3] == MAIN and len(lines) == 4
