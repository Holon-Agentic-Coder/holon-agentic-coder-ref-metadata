"""The flow runner notifies only when calibration is done. No ntfy call is made: the notifier is faked."""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent / ".agents" / "skills" / "holon_flow" / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import notify_ntfy  # noqa: E402
import run_holon_flow  # noqa: E402


@pytest.fixture
def sent(monkeypatch):
    calls = []
    monkeypatch.setattr(notify_ntfy, "notify", lambda *a, **k: calls.append((a, k)))
    return calls


def make_flow(tmp_path, completed):
    intent = tmp_path / "intent.json"
    intent.write_text(json.dumps({"slug": "demo", "goal": "g", "description": "d"}))
    worktree = tmp_path / "flow-demo"
    (worktree / ".holon" / "flow").mkdir(parents=True)
    (worktree / ".holon" / "flow" / "checkpoint-demo.json").write_text(json.dumps({"completed_stages": completed}))
    return intent, worktree


def test_notifies_once_when_calibration_is_done(tmp_path, sent):
    intent, worktree = make_flow(tmp_path, ["intent", "plan", "execute", "review", "calibrate"])
    run_holon_flow._notify_outcome(intent, 0, worktree)
    assert len(sent) == 1
    assert "calibrated" in sent[0][0][0]


def test_silent_when_calibration_is_not_done(tmp_path, sent):
    intent, worktree = make_flow(tmp_path, ["intent", "plan", "execute"])
    run_holon_flow._notify_outcome(intent, 0, worktree)
    assert sent == []


def test_silent_when_the_flow_stopped_even_if_calibration_was_recorded(tmp_path, sent):
    intent, worktree = make_flow(tmp_path, ["calibrate"])
    run_holon_flow._notify_outcome(intent, 1, worktree)
    assert sent == []


def test_silent_without_a_checkpoint(tmp_path, sent):
    intent, _ = make_flow(tmp_path, [])
    run_holon_flow._notify_outcome(intent, 0, tmp_path / "missing")
    assert sent == []
