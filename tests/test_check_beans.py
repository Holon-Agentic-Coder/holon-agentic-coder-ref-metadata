import importlib.util
from datetime import UTC, datetime
from pathlib import Path

_scripts = Path(__file__).resolve().parents[1] / ".agents" / "scripts"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, _scripts / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


import sys  # noqa: E402

sys.path.insert(0, str(_scripts))
beans = _load("check_beans")
stamps = _load("timestamps")

EVIDENCE_NOW = datetime(2026, 11, 26, 23, 7, 49, tzinfo=UTC)
COMMIT_0550 = datetime(2026, 11, 26, 22, 54, 22, tzinfo=UTC)


def _utc(text):
    return stamps.parse_strict(text)


def _bean(number="0550", status="todo", created="2026-11-26T22:50:00Z", updated="2026-11-26T22:50:00Z", extra=""):
    name = f"holon-agentic-coder-ref-metadata-{number}--sample-bean.md"
    text = (
        f"---\n# holon-agentic-coder-ref-metadata-{number}\ntitle: sample\nstatus: {status}\ntype: task\n"
        f"created_at: {created}\nupdated_at: {updated}\n{extra}---\n\nbody\n"
    )
    return Path(name), text


def _line_times(when):
    return {"times": [when] * 12, "introduced": when}


def test_bean_0550_invented_times_fail_before_cleanup():
    path, text = _bean(created="2026-11-27T00:20:00Z", updated="2026-11-27T00:30:00Z")
    problems = beans.check_bean(path, text, EVIDENCE_NOW, _line_times(COMMIT_0550))
    assert any("created_at" in p and "in the future" in p for p in problems)
    assert any("updated_at" in p and "after the commit" in p for p in problems)


def test_bean_0550_corrected_times_pass():
    path, text = _bean(created="2026-11-26T22:54:22Z", updated="2026-11-26T22:54:22Z")
    assert beans.check_bean(path, text, EVIDENCE_NOW, _line_times(COMMIT_0550)) == []


def test_bean_0549_future_updated_at_fails():
    path, text = _bean(number="0549", created="2026-11-26T22:00:00Z", updated="2026-11-27T01:00:00Z")
    assert beans.check_bean(path, text, EVIDENCE_NOW, None)


def test_bean_created_far_before_introducing_commit_fails():
    late_commit = datetime(2026, 11, 27, 2, 0, 0, tzinfo=UTC)
    path, text = _bean(created="2026-11-26T01:00:00Z", updated="2026-11-26T22:50:00Z")
    problems = beans.check_bean(path, text, datetime(2026, 11, 27, 3, tzinfo=UTC), _line_times(late_commit))
    assert any("over 24h before" in p for p in problems)


def test_bean_updated_before_created_fails():
    path, text = _bean(created="2026-11-26T22:50:00Z", updated="2026-11-26T22:40:00Z")
    assert any("precedes" in p for p in beans.check_bean(path, text, EVIDENCE_NOW, None))


def test_new_beans_need_strict_utc_but_legacy_offsets_are_tolerated():
    path, text = _bean(created="2026-11-27T09:10:00+11:00", updated="2026-11-27T09:10:00+11:00")
    assert any("strict UTC" in p for p in beans.check_bean(path, text, EVIDENCE_NOW, None))
    path, text = _bean(created="2026-11-17T15:08:00+11:00", updated="2026-11-17T15:38:00+11:00")
    assert beans.check_bean(path, text, EVIDENCE_NOW, None) == []


def test_bean_status_name_id_and_required_fields():
    path, text = _bean(status="done")
    assert any("invalid status" in p for p in beans.check_bean(path, text, EVIDENCE_NOW, None))
    path, text = _bean()
    assert any(
        "does not match" in p for p in beans.check_bean(path, text.replace("-0550\n", "-1lh8\n", 1), EVIDENCE_NOW, None)
    )
    assert any(
        "missing title" in p for p in beans.check_bean(path, text.replace("title: sample\n", ""), EVIDENCE_NOW, None)
    )
    assert beans.check_bean(Path("random.md"), text, EVIDENCE_NOW, None)


def _entries(*parts):
    return [(path, text, None) for path, text in parts]


def test_collection_flags_duplicate_gap_and_missing_blocker():
    first = _bean(number="0001", created="2026-10-01T00:00:00Z", updated="2026-10-01T00:00:00Z")
    third = _bean(
        number="0003",
        created="2026-10-01T00:00:00Z",
        updated="2026-10-01T00:00:00Z",
        extra="blocked_by:\n  - holon-agentic-coder-ref-metadata-0099\n",
    )
    duplicate = (Path("holon-agentic-coder-ref-metadata-0001--other.md"), first[1])
    problems = beans.check_collection(_entries(first, third, duplicate), EVIDENCE_NOW)
    assert any("duplicate bean id 0001" in p for p in problems)
    assert any("0002 is missing" in p for p in problems)
    assert any("0099 does not exist" in p for p in problems)


def test_collection_accepts_sequential_beans_with_existing_blocker():
    one = _bean(number="0001", created="2026-10-01T00:00:00Z", updated="2026-10-01T00:00:00Z")
    two = _bean(
        number="0002",
        created="2026-10-01T00:00:00Z",
        updated="2026-10-01T00:00:00Z",
        extra="blocked_by:\n  - holon-agentic-coder-ref-metadata-0001\n",
    )
    beans.KNOWN_GAPS, saved = set(), beans.KNOWN_GAPS
    try:
        assert beans.check_collection(_entries(one, two), EVIDENCE_NOW) == []
    finally:
        beans.KNOWN_GAPS = saved


AUDIT_BEFORE_CLEANUP = (
    "# Audits\n\n## Entries\n\n"
    "### 2026-11-27T00:30:00Z — Fifth-Merge Audit\n\n"
    "### 2026-11-26T21:10:00Z — Fifth-Merge Audit\n"
)
AUDIT_AFTER_CLEANUP = AUDIT_BEFORE_CLEANUP.replace("2026-11-27T00:30:00Z", "2026-11-26T22:59:59Z")


def test_audit_entry_in_the_future_fails_then_passes_after_cleanup():
    assert any("in the future" in p for p in beans.check_audits(AUDIT_BEFORE_CLEANUP, EVIDENCE_NOW))
    assert beans.check_audits(AUDIT_AFTER_CLEANUP, EVIDENCE_NOW) == []


def test_audit_entries_must_be_newest_first():
    swapped = "### 2026-11-26T21:10:00Z — a\n### 2026-11-26T22:59:59Z — b\n"
    assert any("newer than" in p for p in beans.check_audits(swapped, EVIDENCE_NOW))


def test_audit_entry_after_its_commit_fails():
    assert beans.check_audits(AUDIT_AFTER_CLEANUP, EVIDENCE_NOW, [stamps.parse_strict("2026-11-26T20:00:00Z")] * 6)


def test_real_beans_and_audits_are_clean():
    now = stamps.utc_now()
    audit_text, audit_written = beans.load_audits()
    assert beans.check_collection(beans.load(), now) == []
    assert beans.check_audits(audit_text, now, audit_written) == []


def test_stamp_rules_directly():
    assert stamps.stamp_problems("x", "2026-11-26T22:00:00Z", EVIDENCE_NOW) == []
    assert stamps.stamp_problems("x", "2026-11-26T23:09:00Z", EVIDENCE_NOW) == []
    assert stamps.stamp_problems("x", "2026-11-26T23:13:00Z", EVIDENCE_NOW)
    assert stamps.stamp_problems("x", "2026-11-26 22:00:00", EVIDENCE_NOW)
    assert stamps.stamp_problems("x", "2026-11-26T22:00:00.000Z", EVIDENCE_NOW)
    assert stamps.stamp_problems("x", "2026-11-26T22:00Z", EVIDENCE_NOW)
