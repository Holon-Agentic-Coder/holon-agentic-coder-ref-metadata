"""Spend-limit step-down (bean 0434) and the wrapper's completion gate and state file (bean 0417). No real gh calls."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / ".agents" / "skills" / "holon_flow" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_holon_flow as rhf  # noqa: E402

SPEND = "You've hit your monthly spend limit. Switch to another model to continue."


def _flow(monkeypatch, tmp_path, outputs, with_checkpoint=True):
    intent = tmp_path / "intent.json"
    intent.write_text(json.dumps({"slug": "demo", "goal": "g"}))
    worktree = tmp_path / "flow-demo"
    (worktree / ".git").mkdir(parents=True)
    if with_checkpoint:
        chk = worktree / ".holon/flow/checkpoint-demo.json"
        chk.parent.mkdir(parents=True)
        chk.write_text(json.dumps({"completed_stages": ["intent", "plan"]}))
    runs, waits, outcome = [], [], {}
    results = iter(outputs)
    monkeypatch.setattr(rhf, "run_prerequisites_check", lambda w: None)
    monkeypatch.setattr(rhf, "build_flow_env", lambda agent: {})
    monkeypatch.setattr(rhf, "verify_pr_and_calibration", lambda *a, **k: {"ok": True, "problems": []})
    monkeypatch.setattr(rhf, "wait_for_limit_reset", lambda reset, slug: waits.append(reset))
    monkeypatch.setattr(rhf, "execute_flow_process", lambda cmd, **k: runs.append(cmd) or next(results))
    code = rhf.run_flow(intent, worktree, "claude-agent", "claude-fable-5-2", outcome=outcome)
    return code, runs, waits, worktree


def test_the_spend_limit_message_is_a_quota_error():
    assert rhf.is_quota_error("noise\n" + SPEND + "\n")
    assert rhf.is_quota_error("You've hit your monthly spend limit.")


def test_a_spend_limit_only_in_the_head_of_the_output_is_ignored():
    assert not rhf.is_quota_error(SPEND + "\n" + "ok\n" * 300)


def test_a_spend_limit_without_a_reset_steps_down_and_resumes_from_the_checkpoint(monkeypatch, tmp_path):
    code, runs, waits, worktree = _flow(monkeypatch, tmp_path, [(1, SPEND), (0, "")])
    assert code == 0 and waits == []
    assert runs[0][runs[0].index("--model") + 1] == "claude-fable-5-2"
    assert runs[1][runs[1].index("--model") + 1] == "claude-opus-5-5"
    assert runs[1][runs[1].index("--agent") + 1] == "claude-agent"
    assert runs[1][runs[1].index("--checkpoint") + 1] == str(worktree / ".holon/flow/checkpoint-demo.json")


def test_a_spend_limit_naming_a_reset_is_waited_out_on_the_same_model(monkeypatch, tmp_path):
    code, runs, waits, _ = _flow(monkeypatch, tmp_path, [(1, SPEND + " Resets in 51m58s"), (0, "")])
    assert code == 0 and len(waits) == 1
    assert all(r[r.index("--model") + 1] == "claude-fable-5-2" for r in runs)


# --- completion gate ---------------------------------------------------------------------------------------------

PR = {"number": 7, "headRefName": "flow/demo", "title": "demo", "url": "https://x/pull/7", "state": "OPEN"}


class FakeGh:
    def __init__(self, prs=(PR,), diff="a.py\nI-1_calibration.md\n", view=None, checks=(), fail=None):
        self.prs, self.diff, self.fail = list(prs), diff, fail
        self.view = view or {"mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN"}
        self.checks = [list(c) for c in checks] or [[]]
        self.polls = 0

    def __call__(self, cmd, **kwargs):
        assert cmd[0] == "gh", cmd
        sub = cmd[1:3]
        if self.fail == "list" and sub == ["pr", "list"]:
            raise subprocess.CalledProcessError(1, cmd)
        out = ""
        if sub == ["pr", "list"]:
            out = json.dumps(self.prs)
        elif sub == ["pr", "diff"]:
            out = self.diff
        elif sub == ["pr", "view"]:
            out = json.dumps(self.view)
        elif sub == ["pr", "checks"]:
            out = json.dumps(self.checks[min(self.polls, len(self.checks) - 1)])
            self.polls += 1
        return subprocess.CompletedProcess(cmd, 0, stdout=out, stderr="")


def _verify(monkeypatch, tmp_path, gh, **kw):
    monkeypatch.setattr(rhf.subprocess, "run", gh)
    return rhf.verify_pr_and_calibration(tmp_path, "demo", sleep=lambda s: None, checks_timeout=90, **kw)


def test_a_complete_pull_request_passes(monkeypatch, tmp_path):
    result = _verify(monkeypatch, tmp_path, FakeGh())
    assert result["ok"] and result["problems"] == [] and result["calibration"] == ["I-1_calibration.md"]


@pytest.mark.parametrize(
    ("gh", "needle"),
    [
        (FakeGh(prs=[]), "No pull request"),
        (FakeGh(fail="list"), "Could not query"),
        (FakeGh(diff="a.py\n"), "_calibration.md"),
        (FakeGh(view={"mergeable": "CONFLICTING", "mergeStateStatus": "DIRTY"}), "CONFLICTING"),
        (FakeGh(view={"mergeable": "UNKNOWN", "mergeStateStatus": "DIRTY"}), "CONFLICTING"),
        (FakeGh(prs=[{**PR, "state": "CLOSED"}]), "closed"),
    ],
)
def test_each_missing_deliverable_fails(monkeypatch, tmp_path, gh, needle):
    result = _verify(monkeypatch, tmp_path, gh)
    assert not result["ok"] and any(needle in p for p in result["problems"])


def test_a_merged_pull_request_is_a_clean_finish(monkeypatch, tmp_path):
    result = _verify(monkeypatch, tmp_path, FakeGh(prs=[{**PR, "state": "MERGED"}], diff=""))
    assert result["ok"] and result["merge_state"] == "MERGED"


def test_pending_checks_are_waited_for_then_pass(monkeypatch, tmp_path):
    pending = [{"name": "unit (macos-latest)", "state": "PENDING", "bucket": "pending"}]
    done = [{"name": "unit (macos-latest)", "state": "SUCCESS", "bucket": "pass"}]
    gh = FakeGh(checks=[pending, pending, done])
    result = _verify(monkeypatch, tmp_path, gh)
    assert result["ok"] and gh.polls == 3 and result["checks"] == done


def test_checks_still_pending_at_the_bound_fail(monkeypatch, tmp_path):
    pending = [{"name": "unit", "state": "PENDING", "bucket": "pending"}]
    result = _verify(monkeypatch, tmp_path, FakeGh(checks=[pending]))
    assert not result["ok"] and any("pending checks" in p for p in result["problems"])


def test_dry_run_verifies_nothing(monkeypatch, tmp_path):
    def boom(*a, **k):
        raise AssertionError("gh must not run")

    monkeypatch.setattr(rhf.subprocess, "run", boom)
    assert rhf.verify_pr_and_calibration(tmp_path, "demo", dry_run=True)["ok"]


def test_a_flow_that_exits_0_with_an_incomplete_pull_request_exits_1(monkeypatch, tmp_path):
    intent = tmp_path / "intent.json"
    intent.write_text(json.dumps({"slug": "demo", "goal": "g"}))
    worktree = tmp_path / "flow-demo"
    (worktree / ".git").mkdir(parents=True)
    monkeypatch.setattr(rhf, "run_prerequisites_check", lambda w: None)
    monkeypatch.setattr(rhf, "build_flow_env", lambda agent: {})
    monkeypatch.setattr(rhf, "execute_flow_process", lambda cmd, **k: (0, "done"))
    monkeypatch.setattr(rhf, "verify_pr_and_calibration", lambda *a, **k: {"ok": False, "problems": ["no PR"]})
    assert rhf.run_flow(intent, worktree, "claude-agent", "claude-opus-5-5") == 1


# --- state file --------------------------------------------------------------------------------------------------


def test_the_state_file_records_the_outcome(tmp_path):
    worktree = tmp_path / "flow-demo"
    chk = worktree / ".holon/flow/checkpoint-demo.json"
    chk.parent.mkdir(parents=True)
    chk.write_text(json.dumps({"completed_stages": ["intent", "plan", "execute", "review", "calibrate"]}))
    outcome = {
        "output": "Review consensus: APPROVED\nCalibration EV: 0.42\n",
        "agent": "claude-agent",
        "model": "claude-opus-5-5",
        "verification": {
            "ok": True,
            "problems": [],
            "pr": PR,
            "calibration": ["c_calibration.md"],
            "mergeable": "MERGEABLE",
            "merge_state": "CLEAN",
        },
    }
    path = rhf.write_flow_state("demo", 0, outcome, worktree, state_dir=tmp_path / ".subagent")
    state = json.loads(path.read_text())
    assert path.name == "flow_demo_state.json"
    assert state["status"] == "completed" and state["pr_number"] == 7 and state["pr_url"] == PR["url"]
    assert state["stage_reached"] == "calibrate" and state["consensus"] == "Review consensus: APPROVED"
    assert state["calibration_ev"] == 0.42 and state["merge_state"] == "CLEAN"
    assert state["next_action"] == "maintainer merges the pull request"


def test_the_state_file_of_a_failed_flow_names_the_problems(tmp_path):
    outcome = {"verification": {"ok": False, "problems": ["No pull request found"], "pr": None}}
    state = rhf.build_flow_state("demo", 1, outcome, None)
    assert state["status"] == "failed" and state["pr_number"] is None
    assert "No pull request found" in state["next_action"]
