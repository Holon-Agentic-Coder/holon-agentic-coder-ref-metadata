import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / ".agents" / "skills" / "holon_flow" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import flow_gates  # noqa: E402
import run_holon_flow  # noqa: E402


@pytest.fixture
def maintainer_home(tmp_path):
    token_file = tmp_path / flow_gates.AUTH_TOKEN_FILE
    token_file.parent.mkdir(parents=True)
    token_file.write_text("maintainer-secret\n")
    return tmp_path


def write_intent(tmp_path, **fields):
    import json

    path = tmp_path / "intent.json"
    path.write_text(json.dumps({"slug": "demo", "goal": "g", **fields}))
    return path


def test_skip_review_is_refused_even_with_authorisation(maintainer_home):
    environ = {flow_gates.AUTH_ENV: "maintainer-secret"}
    assert "never allowed" in flow_gates.forbidden_flag_refusal({"skip_review": True}, environ, maintainer_home)


@pytest.mark.parametrize("flag", ["skip_preflight", "allow_overlap"])
def test_maintainer_flags_are_refused_without_authorisation(flag, maintainer_home):
    assert flow_gates.forbidden_flag_refusal({flag: True}, {}, maintainer_home)
    assert flow_gates.forbidden_flag_refusal({flag: True}, {flow_gates.AUTH_ENV: "guess"}, maintainer_home)


@pytest.mark.parametrize("flag", ["skip_preflight", "allow_overlap"])
def test_maintainer_flags_pass_with_the_matching_token(flag, maintainer_home):
    environ = {flow_gates.AUTH_ENV: "maintainer-secret"}
    assert flow_gates.forbidden_flag_refusal({flag: True}, environ, maintainer_home) is None


def test_env_value_without_a_token_file_is_not_authorisation(tmp_path):
    assert not flow_gates.maintainer_authorised({flow_gates.AUTH_ENV: "x"}, tmp_path)


def test_no_flags_means_no_refusal(tmp_path):
    assert flow_gates.forbidden_flag_refusal({}, {}, tmp_path) is None


def test_budget_scope_without_the_field_is_refused():
    intent = {"scope": ["holon-config/hygiene/module_budgets.json"]}
    assert "module_budget_change" in flow_gates.budget_change_refusal(intent)
    assert flow_gates.budget_change_refusal({**intent, "module_budget_change": " "})


def test_budget_scope_with_the_field_and_other_scopes_pass():
    scope = ["holon-config/hygiene/module_budgets.json"]
    assert flow_gates.budget_change_refusal({"scope": scope, "module_budget_change": "quote"}) is None
    assert flow_gates.budget_change_refusal({"scope": ["a.py"]}) is None


def test_the_filename_0380_no_longer_injects_the_field(tmp_path, monkeypatch):
    import json

    seen = []
    monkeypatch.setattr(run_holon_flow, "execute_flow_process", lambda *a, **k: seen.append(a) or (0, ""))
    path = tmp_path / "intent-0380-x.json"
    path.write_text(json.dumps({"slug": "demo", "goal": "g", "scope": ["holon-config/hygiene/module_budgets.json"]}))
    assert run_holon_flow.run_flow(path, tmp_path, "claude-agent", "m", dry_run=True) == 2
    assert not seen
    assert not list(tmp_path.glob("intent-modified-*"))


def test_run_flow_refuses_skip_review_before_any_work(tmp_path):
    path = write_intent(tmp_path)
    assert run_holon_flow.run_flow(path, tmp_path, "claude-agent", "m", skip_review=True, dry_run=True) == 2


def test_run_flow_refuses_allow_overlap_without_authorisation(tmp_path, monkeypatch):
    monkeypatch.delenv(flow_gates.AUTH_ENV, raising=False)
    path = write_intent(tmp_path)
    assert run_holon_flow.run_flow(path, tmp_path, "claude-agent", "m", allow_overlap=True, dry_run=True) == 2


def test_the_command_line_refuses_skip_review(tmp_path, monkeypatch):
    path = write_intent(tmp_path)
    monkeypatch.setattr(sys, "argv", ["run_holon_flow.py", str(path), "--skip-review", "--dry-run"])
    with pytest.raises(SystemExit) as caught:
        run_holon_flow.main()
    assert caught.value.code == 2
