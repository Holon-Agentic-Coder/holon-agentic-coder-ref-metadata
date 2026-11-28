"""The flow runner builds the Claude auth route itself. A fake secrets directory is used; no real token is read."""

import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / ".agents" / "skills" / "holon_flow" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import flow_env  # noqa: E402
import run_holon_flow  # noqa: E402

FAKE = "sk-ant-oat-fake-token-for-tests"


@pytest.fixture(autouse=True)
def empty_keychain(monkeypatch):
    """No test reads the real OS secret store; a test that wants a stored token patches this again."""
    monkeypatch.setattr(flow_env, "_keychain_token", lambda: "")


@pytest.fixture
def secrets(tmp_path):
    (tmp_path / flow_env.TOKEN_FILE).write_text(FAKE + "\n")
    return tmp_path


def test_claude_agent_gets_the_route_built_from_the_secrets_file(secrets):
    env = flow_env.build_flow_env("claude-agent", environ={}, secrets_dir=secrets)
    settings = json.loads(env["HOLON_AGENT_SETTINGS"])
    assert settings["env"]["CLAUDE_CODE_OAUTH_TOKEN"] == FAKE
    assert len(settings["env"]["HOLON_ECHO_PAD"]) >= 300
    assert env["HOLON_TOKEN_REDUCE"] == "0"
    assert env["PYTHONUNBUFFERED"] == "1"


def test_an_existing_route_is_left_alone(secrets):
    env = flow_env.build_flow_env("claude-agent", environ={"HOLON_AGENT_SETTINGS": '{"env": {}}'}, secrets_dir=secrets)
    assert env["HOLON_AGENT_SETTINGS"] == '{"env": {}}'


def test_the_token_environment_variable_wins_over_the_file(tmp_path):
    env = flow_env.build_flow_env(
        "claude-agent", environ={"CLAUDE_CODE_OAUTH_TOKEN": " from-env "}, secrets_dir=tmp_path
    )
    assert json.loads(env["HOLON_AGENT_SETTINGS"])["env"]["CLAUDE_CODE_OAUTH_TOKEN"] == "from-env"


def test_missing_credentials_fail_loudly_and_name_what_is_missing(tmp_path):
    with pytest.raises(flow_env.AuthRouteMissing) as caught:
        flow_env.build_flow_env("claude-agent", environ={}, secrets_dir=tmp_path)
    message = str(caught.value)
    assert "HOLON_AGENT_SETTINGS" in message and str(tmp_path / flow_env.TOKEN_FILE) in message


def test_the_os_keychain_is_used_when_no_variable_and_no_file_hold_a_token(monkeypatch, tmp_path):
    monkeypatch.setattr(flow_env, "_keychain_token", lambda: "from-keychain")
    env = flow_env.build_flow_env("claude-agent", environ={}, secrets_dir=tmp_path)
    assert json.loads(env["HOLON_AGENT_SETTINGS"])["env"]["CLAUDE_CODE_OAUTH_TOKEN"] == "from-keychain"


def test_the_legacy_file_wins_over_the_keychain(monkeypatch, secrets):
    monkeypatch.setattr(flow_env, "_keychain_token", lambda: "from-keychain")
    env = flow_env.build_flow_env("claude-agent", environ={}, secrets_dir=secrets)
    assert json.loads(env["HOLON_AGENT_SETTINGS"])["env"]["CLAUDE_CODE_OAUTH_TOKEN"] == FAKE


def test_a_keychain_tool_that_cannot_run_or_has_no_entry_gives_no_token(monkeypatch):
    monkeypatch.undo()

    def missing_tool(*_args, **_kwargs):
        raise FileNotFoundError("security")

    monkeypatch.setattr(flow_env.subprocess, "run", missing_tool)
    assert flow_env._keychain_token() == ""

    class NoEntry:
        returncode = 44
        stdout = ""

    monkeypatch.setattr(flow_env.subprocess, "run", lambda *_a, **_k: NoEntry())
    assert flow_env._keychain_token() == ""


def test_the_missing_credentials_message_names_the_keychain_entry(tmp_path):
    with pytest.raises(flow_env.AuthRouteMissing) as raised:
        flow_env.build_flow_env("claude-agent", environ={}, secrets_dir=tmp_path)
    assert "keychain" in str(raised.value)
    assert flow_env.KEYCHAIN_ACCOUNT in str(raised.value)


def test_other_runners_need_no_claude_credentials(tmp_path):
    env = flow_env.build_flow_env("antigravity-agent", environ={}, secrets_dir=tmp_path)
    assert "HOLON_AGENT_SETTINGS" not in env


def test_the_runner_stops_before_dispatch_when_credentials_are_missing(monkeypatch, tmp_path, capsys):
    intent = tmp_path / "intent.json"
    intent.write_text(json.dumps({"slug": "demo", "goal": "g", "description": "d"}))
    worktree = tmp_path / "flow-demo"
    (worktree / ".git").mkdir(parents=True)
    launched = []
    monkeypatch.setattr(run_holon_flow, "run_prerequisites_check", lambda w: None)
    monkeypatch.setattr(run_holon_flow, "execute_flow_process", lambda *a, **k: launched.append(a) or (0, ""))
    monkeypatch.setattr(
        run_holon_flow, "build_flow_env", lambda agent: (_ for _ in ()).throw(flow_env.AuthRouteMissing("no route"))
    )
    code = run_holon_flow.run_flow(intent, worktree, "claude-agent", "claude-sonnet-5-5")
    assert code == 1 and launched == []
    assert FAKE not in capsys.readouterr().out


def test_the_token_never_reaches_the_printed_command(monkeypatch, tmp_path, capsys, secrets):
    seen = {}

    class FakeProc:
        stdout = iter(["done\n"])
        returncode = 0

        def wait(self):
            return 0

    def popen(cmd, **kwargs):
        seen["env"] = kwargs["env"]
        return FakeProc()

    monkeypatch.setattr(run_holon_flow.subprocess, "Popen", popen)
    env = flow_env.build_flow_env("claude-agent", environ={}, secrets_dir=secrets)
    run_holon_flow.execute_flow_process(["holon", "flow", "x.json"], env=env)
    assert FAKE in seen["env"]["HOLON_AGENT_SETTINGS"]
    assert FAKE not in capsys.readouterr().out


def test_the_execute_budget_is_raised_unless_the_caller_set_one(secrets):
    env = flow_env.build_flow_env("claude-agent", environ={}, secrets_dir=secrets)
    assert env["HOLON_STAGE_BUDGET_EXECUTE_MINUTES"] == "10080"
    kept = flow_env.build_flow_env(
        "claude-agent", environ={"HOLON_STAGE_BUDGET_EXECUTE_MINUTES": "90"}, secrets_dir=secrets
    )
    assert kept["HOLON_STAGE_BUDGET_EXECUTE_MINUTES"] == "90"


def test_claude_runs_get_code_mode_unless_the_caller_set_a_value(secrets):
    env = flow_env.build_flow_env("claude-agent", environ={}, secrets_dir=secrets)
    assert env["CLAUDE_CODE_EXPERIMENTAL_CODE_MODE"] == "1"
    assert json.loads(env["HOLON_AGENT_SETTINGS"])["env"]["CLAUDE_CODE_EXPERIMENTAL_CODE_MODE"] == "1"
    off = flow_env.build_flow_env(
        "claude-agent", environ={"CLAUDE_CODE_EXPERIMENTAL_CODE_MODE": "0"}, secrets_dir=secrets
    )
    assert off["CLAUDE_CODE_EXPERIMENTAL_CODE_MODE"] == "0"
    assert json.loads(off["HOLON_AGENT_SETTINGS"])["env"]["CLAUDE_CODE_EXPERIMENTAL_CODE_MODE"] == "0"


def test_other_runners_do_not_get_code_mode(tmp_path):
    env = flow_env.build_flow_env("antigravity-agent", environ={}, secrets_dir=tmp_path)
    assert "CLAUDE_CODE_EXPERIMENTAL_CODE_MODE" not in env


REFUSAL = (
    "[2026-11-18T06:22:15Z] Stage 3 refused: the touch set overlaps pull request #205 on flow/x.py; wait for it to "
    "merge, or rerun with --allow-overlap\n"
)


def _overlap_run(monkeypatch, tmp_path, **kwargs):
    intent = tmp_path / "intent.json"
    intent.write_text(json.dumps({"slug": "demo", "goal": "g", "description": "d"}))
    worktree = tmp_path / "flow-demo"
    (worktree / ".git").mkdir(parents=True)
    launched = []
    monkeypatch.setattr(run_holon_flow, "run_prerequisites_check", lambda w: None)
    monkeypatch.setattr(run_holon_flow, "build_flow_env", lambda agent: {})
    monkeypatch.setattr(run_holon_flow, "execute_flow_process", lambda cmd, **k: launched.append(cmd) or (1, REFUSAL))
    code = run_holon_flow.run_flow(intent, worktree, "claude-agent", "claude-sonnet-5-5", **kwargs)
    return code, launched


def test_an_admission_refusal_is_reported_and_never_overridden_by_the_runner(monkeypatch, tmp_path, capsys):
    code, launched = _overlap_run(monkeypatch, tmp_path, wait_on_overlap=False)
    assert code == 1 and len(launched) == 1
    assert "--allow-overlap" not in launched[0]
    assert "overlaps pull request #205" in capsys.readouterr().out


def test_the_override_is_passed_only_when_the_caller_asks_for_it(monkeypatch, tmp_path):
    monkeypatch.setattr(run_holon_flow, "forbidden_flag_refusal", lambda flags: None)
    code, launched = _overlap_run(monkeypatch, tmp_path, allow_overlap=True)
    assert code == 1 and len(launched) == 1
    assert "--allow-overlap" in launched[0]


LIVE_REFUSAL = (
    "[2026-11-20T01:07:44Z] Stage 3 refused: the touch set overlaps pull request #207 (branch I-1-a/P-2-CLA-CO5.5/"
    "E-3-CLA-CO5.5/_) on flow/x.py; pull request #209 (branch I-4-b/P-5-CLA-CO5.5/E-6-CLA-CO5.5/_) on flow/y.py; "
    "finish or merge that flow first, or rerun with --allow-overlap.\n"
)


def test_the_overlapping_pull_requests_are_parsed_from_the_refusal():
    assert run_holon_flow.parse_overlapping_prs(LIVE_REFUSAL) == [207, 209]
    local = "Stage 3 refused: the touch set overlaps local flow on branch I-1-a/P-2/_ (worktree /w) on x.py; or rerun"
    assert run_holon_flow.parse_overlapping_prs(local) == []
    assert run_holon_flow.is_overlap_refusal(local)
    assert not run_holon_flow.is_overlap_refusal("Stage 3 refused: the plan declares no touch set; or rerun")


def test_an_overlap_is_waited_out_and_stage_3_resumes_from_the_checkpoint(monkeypatch, tmp_path):
    intent = tmp_path / "intent.json"
    intent.write_text(json.dumps({"slug": "demo", "goal": "g", "description": "d"}))
    worktree = tmp_path / "flow-demo"
    (worktree / ".git").mkdir(parents=True)
    checkpoint = worktree / ".holon" / "flow" / "checkpoint-demo.json"
    checkpoint.parent.mkdir(parents=True)
    checkpoint.write_text("{}")
    runs = iter([(1, LIVE_REFUSAL), (0, "")])
    launched, polled, slept = [], [], []
    states = {207: iter(["OPEN", "MERGED"]), 209: iter([None, "CLOSED"])}
    monkeypatch.setattr(run_holon_flow, "run_prerequisites_check", lambda w: None)
    monkeypatch.setattr(run_holon_flow, "build_flow_env", lambda agent: {})
    monkeypatch.setattr(run_holon_flow, "verify_pr_and_calibration", lambda *a, **k: {"ok": True})
    monkeypatch.setattr(run_holon_flow, "execute_flow_process", lambda cmd, **k: launched.append(cmd) or next(runs))
    monkeypatch.setattr(run_holon_flow, "pr_state", lambda n, d: polled.append(n) or next(states[n]))
    monkeypatch.setattr("time.sleep", slept.append)
    code = run_holon_flow.run_flow(intent, worktree, "claude-agent", "claude-opus-5-5", overlap_poll_seconds=7)
    assert code == 0 and len(launched) == 2
    assert all("--allow-overlap" not in cmd for cmd in launched)
    assert launched[1][launched[1].index("--checkpoint") + 1] == str(checkpoint)
    assert polled == [207, 209, 207, 209] and slept == [7]


def test_a_refusal_that_is_not_an_overlap_still_stops(monkeypatch, tmp_path):
    refusal = "Stage 3 refused: the plan declares no touch set; or rerun with --allow-overlap to admit it anyway.\n"
    intent = tmp_path / "intent.json"
    intent.write_text(json.dumps({"slug": "demo", "goal": "g", "description": "d"}))
    worktree = tmp_path / "flow-demo"
    (worktree / ".git").mkdir(parents=True)
    launched = []
    monkeypatch.setattr(run_holon_flow, "run_prerequisites_check", lambda w: None)
    monkeypatch.setattr(run_holon_flow, "build_flow_env", lambda agent: {})
    monkeypatch.setattr(run_holon_flow, "execute_flow_process", lambda cmd, **k: launched.append(cmd) or (1, refusal))
    code = run_holon_flow.run_flow(intent, worktree, "claude-agent", "claude-opus-5-5")
    assert code == 1 and len(launched) == 1


def _record_git(monkeypatch):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        return run_holon_flow.subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(run_holon_flow.subprocess, "run", fake_run)
    return calls


def test_a_missing_flow_worktree_beside_main_is_cut_from_origin_main(monkeypatch, tmp_path):
    (tmp_path / "main").mkdir()
    calls = _record_git(monkeypatch)
    resolved = run_holon_flow.resolve_flow_worktree(tmp_path / "flow-review-keeps-branch", "ignored-slug")
    assert resolved == (tmp_path / "flow-review-keeps-branch").resolve()
    assert calls[-1][-5:] == [
        "--no-track",
        "-b",
        "flow-review-keeps-branch",
        str(resolved),
        "origin/main",
    ]
    assert calls[-1][:3] == ["git", "-C", str((tmp_path / "main").resolve())]


def test_an_existing_flow_worktree_is_reused_untouched(monkeypatch, tmp_path):
    (tmp_path / "main").mkdir()
    (tmp_path / "flow-x").mkdir()
    calls = _record_git(monkeypatch)
    assert run_holon_flow.resolve_flow_worktree(tmp_path / "flow-x", "x") == (tmp_path / "flow-x").resolve()
    assert calls == []


def test_a_missing_worktree_that_is_not_a_flow_worktree_is_not_created(monkeypatch, tmp_path):
    (tmp_path / "main").mkdir()
    calls = _record_git(monkeypatch)
    assert run_holon_flow.resolve_flow_worktree(tmp_path / "other", "x") == (tmp_path / "other").resolve()
    assert calls == []
