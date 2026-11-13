"""Unit tests for the lowest-tier model probe. No harness is called: every command is faked."""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent / ".agents" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import lowest_model  # noqa: E402


def test_picks_smallest_family_then_lowest_effort():
    result = lowest_model.rank(["acme-pro-high", "acme-flash-high", "acme-flash-low", "acme-flash-medium"])
    assert result["lowest"] == "acme-flash-low"


def test_a_new_lite_model_displaces_the_previous_lowest():
    before = lowest_model.rank(["x-flash-low", "x-pro-low"])["lowest"]
    after = lowest_model.rank(["x-flash-low", "x-pro-low", "x-9-lite"])["lowest"]
    assert (before, after) == ("x-flash-low", "x-9-lite")


def test_opaque_codenames_are_never_chosen_as_lowest():
    result = lowest_model.rank(["gemini-4-argon-low", "claude-sonnet-9-high"])
    assert result["lowest"] == "claude-sonnet-9-high"
    assert result["unranked"] == ["gemini-4-argon-low"]


def test_nothing_rankable_gives_no_lowest():
    assert lowest_model.rank(["argon", "hydrogen"])["lowest"] is None


def test_antigravity_probe_parses_tab_separated_ids(monkeypatch):
    out = "Fetching available models...\nm-flash-low\tM Flash (Low)\nm-pro-high\tM Pro (High)\n"
    monkeypatch.setattr(lowest_model, "run", lambda cmd: out)
    assert lowest_model.probe_antigravity() == ["m-flash-low", "m-pro-high"]


def test_holon_probe_reads_canonical_models(monkeypatch):
    rows = [{"canonical_model": "a-haiku"}, {"canonical_model": "a-opus"}, {"canonical_model": "a-haiku"}]
    seen = []
    monkeypatch.setattr(lowest_model, "run", lambda cmd: seen.append(cmd) or json.dumps(rows))
    assert lowest_model.probe_holon("claude-agent") == ["a-haiku", "a-opus"]
    assert seen == [["holon", "models", "--json", "--agent", "claude-agent"]]


def test_probe_failure_exits_one_with_an_error(monkeypatch, capsys):
    def boom(cmd):
        raise RuntimeError("agy exited 1")

    monkeypatch.setattr(lowest_model, "run", boom)
    monkeypatch.setattr(sys, "argv", ["lowest_model", "--probe", "antigravity"])
    assert lowest_model.main() == 1
    assert json.loads(capsys.readouterr().out)["lowest"] is None


def test_an_effort_word_alone_never_ranks_a_model():
    result = lowest_model.rank(["gemini-4-argon-medium", "gpt-oss-120b-medium", "acme-flash-high"])
    assert result["lowest"] == "acme-flash-high"
    assert result["unranked"] == ["gemini-4-argon-medium", "gpt-oss-120b-medium"]
