"""The flow runner waits out a named reset and never switches runner on its own."""

import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent / ".agents" / "skills" / "holon_flow" / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import run_holon_flow  # noqa: E402


@pytest.mark.parametrize(
    "text",
    [
        "You've hit your session limit · resets 10am (UTC)",
        "You've hit your 5-hour limit · resets 9pm (Australia/Melbourne)",
        "limit reached, resets 5:40pm (Australia/Melbourne)",
    ],
)
def test_a_named_reset_is_recognised_with_or_without_minutes(text):
    assert run_holon_flow.parse_limit_reset(text) is not None


def test_an_hour_only_reset_is_that_hour_on_the_hour_in_the_named_zone():
    reset = run_holon_flow.parse_limit_reset("resets 10am (UTC)")
    assert isinstance(reset, datetime)
    assert (reset.hour, reset.minute, str(reset.tzinfo)) == (10, 0, "UTC")


def test_a_pm_reset_with_minutes_keeps_them():
    reset = run_holon_flow.parse_limit_reset("resets 5:40pm (Australia/Melbourne)")
    assert (reset.hour, reset.minute) == (17, 40)


def test_no_reset_time_returns_none():
    assert run_holon_flow.parse_limit_reset("insufficient_quota") is None


def test_claude_steps_down_its_own_ladder():
    first = run_holon_flow.FALLBACK_LADDER_CLAUDE[0]
    agent, model = run_holon_flow.resolve_next_model("claude-agent", first)
    assert agent == "claude-agent"
    assert model == run_holon_flow.FALLBACK_LADDER_CLAUDE[1]


def test_an_exhausted_claude_ladder_never_switches_to_antigravity():
    last = run_holon_flow.FALLBACK_LADDER_CLAUDE[-1]
    assert run_holon_flow.resolve_next_model("claude-agent", last) is None


def test_an_exhausted_antigravity_ladder_never_switches_to_claude():
    last = run_holon_flow.FALLBACK_LADDER_ANTIGRAVITY[-1]
    assert run_holon_flow.resolve_next_model("antigravity-agent", last) is None


def test_antigravity_ladder_starts_with_gemini_4_argon_then_hydrogen_then_flash():
    assert run_holon_flow.FALLBACK_LADDER_ANTIGRAVITY == [
        "gemini-4-argon",
        "gemini-4-hydrogen",
        "gemini-3.8-flash",
    ]
    assert run_holon_flow.resolve_next_model("antigravity-agent", "gemini-4-argon") == (
        "antigravity-agent",
        "gemini-4-hydrogen",
    )
    assert run_holon_flow.resolve_next_model("antigravity-agent", "gemini-4-hydrogen") == (
        "antigravity-agent",
        "gemini-3.8-flash",
    )
    assert run_holon_flow.resolve_next_model("antigravity-agent", "gemini-3.8-flash") is None


@pytest.mark.parametrize(
    ("suffixed_model", "expected_next"),
    [
        ("gemini-4-argon-medium", ("antigravity-agent", "gemini-4-hydrogen")),
        ("gemini-4-hydrogen-medium", ("antigravity-agent", "gemini-3.8-flash")),
        ("gemini-3.8-flash-medium", None),
    ],
)
def test_antigravity_step_down_normalises_effort_suffixes(suffixed_model, expected_next):
    assert run_holon_flow.resolve_next_model("antigravity-agent", suffixed_model) == expected_next


@pytest.mark.parametrize(
    "text",
    [
        "QUOTA_EXHAUSTED",
        "Quota exceeded for model",
        "usage limit reached",
    ],
)
def test_quota_error_patterns_match_gemini_and_usage_limit_messages(text):
    assert run_holon_flow.is_quota_error(text) is True


def test_cli_default_model_is_gemini_4_argon(monkeypatch):
    captured = {}

    def fake_run_flow(**kwargs):
        captured.update(kwargs)
        return 0

    monkeypatch.setattr(run_holon_flow, "run_flow", fake_run_flow)
    monkeypatch.setattr(sys, "argv", ["run_holon_flow.py", "todo/fake.json", "--dry-run"])
    with pytest.raises(SystemExit) as exc_info:
        run_holon_flow.main()
    assert exc_info.value.code == 0
    assert captured["model"] == "gemini-4-argon"
