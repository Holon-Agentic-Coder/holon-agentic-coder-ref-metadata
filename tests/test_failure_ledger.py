import importlib.util
import json
from datetime import UTC, datetime
from pathlib import Path

_p = Path(__file__).resolve().parents[1] / ".agents" / "scripts" / "check_failure_ledger.py"
_s = importlib.util.spec_from_file_location("check_failure_ledger", _p)
m = importlib.util.module_from_spec(_s)
_s.loader.exec_module(m)


EVIDENCE_NOW = datetime(2026, 11, 26, 23, 7, 49, tzinfo=UTC)


def _entry(n, **kw):
    e = {k: "x" for k in m.REQUIRED}
    e.update(id=f"CF-{n:04d}", category="brief", refs=[], created_at="2026-11-26T22:36:23Z")
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


def test_duplicate_ids_are_refused():
    rows = [_entry(n) for n in range(1, 4)] + [_entry(20), _entry(21)]
    rows[3], rows[4] = _entry(2), _entry(3)
    assert any("duplicate id CF-0002" in e for e in m.check_lines(rows))


def test_append_only():
    head = [_entry(1), _entry(2)]
    assert m.check_append_only(head + [_entry(3)], head) == []
    assert m.check_append_only([_entry(1), _entry(2, rule="y")], head)
    assert m.check_append_only([_entry(1)], head)


def test_today_s_invented_ledger_times_fail_before_cleanup():
    before = [
        _entry(1, created_at="2026-11-27T00:00:00Z"),
        _entry(2, created_at="2026-11-27T00:00:00Z"),
        _entry(3, created_at="2026-11-26T22:36:23Z"),
    ]
    errors = m.check_lines(before, now=EVIDENCE_NOW)
    assert any("in the future" in e for e in errors)
    assert any("ordered" in e for e in errors)


def test_corrected_ledger_times_pass():
    after = [_entry(n, created_at="2026-11-26T22:36:23Z") for n in (1, 2, 3)]
    assert m.check_lines(after, now=EVIDENCE_NOW) == []


def test_row_after_its_commit_fails():
    commit = datetime(2026, 11, 26, 22, 0, 0, tzinfo=UTC)
    assert m.check_lines([_entry(1)], written_at=[commit], now=EVIDENCE_NOW)


def test_malformed_ledger_timestamp_fails():
    assert m.check_lines([_entry(1, created_at="2026-11-26T22:36Z")], now=EVIDENCE_NOW)


def test_append_only_allows_correcting_a_stamp_that_postdates_its_commit():
    commit = datetime(2026, 11, 26, 22, 54, 22, tzinfo=UTC)
    head = [_entry(1, created_at="2026-11-27T00:00:00Z")]
    fixed = [_entry(1, created_at="2026-11-26T22:36:23Z")]
    assert m.check_append_only(fixed, head, [commit]) == []
    assert m.check_append_only(fixed, head, None)
    valid_head = [_entry(1, created_at="2026-11-26T22:00:00Z")]
    assert m.check_append_only(fixed, valid_head, [commit])
    assert m.check_append_only([_entry(1, created_at="2026-11-26T22:36:23Z", rule="y")], head, [commit])
