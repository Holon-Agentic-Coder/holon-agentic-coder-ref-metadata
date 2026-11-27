import importlib.util
import json
import re
from pathlib import Path

import pytest

_p = Path(__file__).resolve().parents[1] / ".agents" / "scripts" / "stamp.py"
_s = importlib.util.spec_from_file_location("stamp", _p)
stamp = importlib.util.module_from_spec(_s)
_s.loader.exec_module(stamp)

STRICT = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
BEAN = (
    "---\n# holon-agentic-coder-ref-metadata-0900\ntitle: t\nstatus: todo\n"
    "created_at: 2026-01-01T00:00:00Z\nupdated_at: 2026-01-01T00:00:00.123Z\n---\n\nbody\n"
)
ROW = {"failure": "f", "my_part": "m", "cost": "c", "rule": "r"}


def test_current_stamp_is_strict_utc():
    assert STRICT.match(stamp.current_stamp())


def test_now_command_prints_strict_stamp(capsys):
    assert stamp.main(["now"]) == 0
    assert STRICT.match(capsys.readouterr().out.strip())


def test_touch_command_updates_only_updated_at(tmp_path, monkeypatch):
    bean = tmp_path / "holon-agentic-coder-ref-metadata-0900--t.md"
    bean.write_text(BEAN)
    monkeypatch.setattr(stamp, "BEANS", tmp_path)
    original = stamp.bean_file
    monkeypatch.setattr(stamp, "bean_file", lambda bean_id: original(bean_id, tmp_path))
    stamp.main(["touch", "0900"])
    text = bean.read_text()
    assert "created_at: 2026-01-01T00:00:00Z" in text
    updated = re.search(r"^updated_at: (.*)$", text, re.M).group(1)
    assert STRICT.match(updated)
    assert text.endswith("body\n")


def test_created_command_sets_both_stamps(tmp_path, monkeypatch):
    bean = tmp_path / "holon-agentic-coder-ref-metadata-0900--t.md"
    bean.write_text(BEAN)
    original = stamp.bean_file
    monkeypatch.setattr(stamp, "bean_file", lambda bean_id: original(bean_id, tmp_path))
    stamp.main(["created", "0900"])
    stamps = re.findall(r"^(?:created|updated)_at: (.*)$", bean.read_text(), re.M)
    assert len(stamps) == 2 and all(STRICT.match(s) for s in stamps)


def test_missing_stamp_field_is_added(tmp_path):
    bean = tmp_path / "b.md"
    bean.write_text("---\ntitle: t\n---\nbody\n")
    stamp.set_frontmatter_stamp(bean, "updated_at", "2026-11-27T00:00:00Z")
    assert bean.read_text() == "---\ntitle: t\nupdated_at: 2026-11-27T00:00:00Z\n---\nbody\n"


def test_unknown_bean_is_refused(tmp_path):
    with pytest.raises(SystemExit):
        stamp.bean_file("0999", tmp_path)


def test_ledger_append_takes_next_id_and_passes_the_ledger_checker(tmp_path):
    ledger = tmp_path / "full.jsonl"
    seed = {
        **ROW,
        "id": "CF-0001",
        "created_at": "2026-11-26T22:36:23Z",
        "session_date": "2026-11-26",
        "category": "brief",
        "refs": [],
    }
    ledger.write_text(json.dumps(seed) + "\n")
    row = stamp.append_ledger_row("brief", ROW, ["bean 0579"], ledger=ledger)
    assert row["id"] == "CF-0002"
    assert stamp.check_failure_ledger.check_lines(ledger.read_text().splitlines()) == []


def test_ledger_append_uses_highest_id_not_line_count(tmp_path):
    rows = [{"id": "CF-0003"}, {"id": "CF-0001"}]
    assert stamp.next_failure_id(rows) == "CF-0004"


def test_unknown_category_is_refused_and_ledger_untouched(tmp_path):
    ledger = tmp_path / "l.jsonl"
    ledger.write_text("")
    with pytest.raises(SystemExit):
        stamp.append_ledger_row("made-up", ROW, [], ledger=ledger)
    assert ledger.read_text() == ""


def test_empty_field_is_refused():
    with pytest.raises(SystemExit):
        stamp.ledger_row([], "brief", {**ROW, "rule": " "}, [], "2026-11-27T00:00:00Z")


def test_bean_checker_accepts_a_touched_bean(tmp_path):
    check_path = Path(__file__).resolve().parents[1] / ".agents" / "scripts" / "timestamps.py"
    spec = importlib.util.spec_from_file_location("timestamps_under_test", check_path)
    timestamps = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(timestamps)
    bean = tmp_path / "b.md"
    bean.write_text(BEAN)
    stamp.set_frontmatter_stamp(bean, "updated_at", stamp.current_stamp())
    value = re.search(r"^updated_at: (.*)$", bean.read_text(), re.M).group(1)
    assert timestamps.stamp_problems("updated_at", value, timestamps.utc_now()) == []
    assert timestamps.stamp_problems("updated_at", "2026-01-01T00:00:00.123Z", timestamps.utc_now())
