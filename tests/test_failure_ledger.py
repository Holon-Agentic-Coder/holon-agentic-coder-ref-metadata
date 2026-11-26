import importlib.util
import json
from pathlib import Path

_p = Path(__file__).resolve().parents[1] / ".agents" / "scripts" / "check_failure_ledger.py"
_s = importlib.util.spec_from_file_location("check_failure_ledger", _p)
m = importlib.util.module_from_spec(_s)
_s.loader.exec_module(m)


def _entry(n, **kw):
    e = {k: "x" for k in m.REQUIRED}
    e.update(id=f"CF-{n:04d}", category="brief", refs=[])
    e.update(kw)
    return json.dumps(e)


def test_real_ledger_is_valid():
    lines = [x for x in m.LEDGER.read_text().splitlines() if x.strip()]
    assert len(lines) >= 9
    assert m.check_lines(lines) == []


def test_detects_bad_json_missing_field_and_gap():
    assert m.check_lines(["{nope"])
    assert m.check_lines([json.dumps({"id": "CF-0001"})])
    assert m.check_lines([_entry(1), _entry(3)])
    assert m.check_lines([_entry(1, category="other")])


def test_append_only():
    head = [_entry(1), _entry(2)]
    assert m.check_append_only(head + [_entry(3)], head) == []
    assert m.check_append_only([_entry(1), _entry(2, rule="y")], head)
    assert m.check_append_only([_entry(1)], head)
