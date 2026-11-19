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
    code, launched = _overlap_run(monkeypatch, tmp_path)
    assert code == 1 and len(launched) == 1
    assert "--allow-overlap" not in launched[0]
    assert "overlaps pull request #205" in capsys.readouterr().out


def test_the_override_is_passed_only_when_the_caller_asks_for_it(monkeypatch, tmp_path):
    code, launched = _overlap_run(monkeypatch, tmp_path, allow_overlap=True)
    assert code == 1 and len(launched) == 1
    assert "--allow-overlap" in launched[0]
