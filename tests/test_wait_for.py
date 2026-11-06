"""Unit tests for the shared wait helper (Bean 0182). No network: every gh call is faked."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent.parent / ".agents" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import wait_for  # noqa: E402

REPO = "Holon-Agentic-Coder/holon-coherence"


def completed(returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(["gh"], returncode, stdout, stderr)


class FakeGh:
    """Returns queued responses per gh subcommand (`pr view` / `pr checks`) and records every call."""

    def __init__(self, views=(), checks=()):
        self.views = list(views)
        self.checks = list(checks)
        self.calls = []

    def __call__(self, args, timeout=None):
        self.calls.append(list(args))
        queue = self.views if args[1] == "view" else self.checks
        item = queue.pop(0) if len(queue) > 1 else queue[0]
        if isinstance(item, BaseException):
            raise item
        return item


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


def head(sha):
    return completed(stdout=json.dumps({"headRefOid": sha}))


def test_redact_masks_github_and_anthropic_tokens():
    token = "gh" + "o_" + "A" * 36
    pat = "github_pat_" + "B" * 60
    ant = "sk-" + "ant-" + "C" * 30
    out = wait_for.redact(f"a {token} b {pat} c {ant} d")
    assert token not in out and pat not in out and ant not in out
    assert out.count(wait_for.REDACTED) == 3


@pytest.mark.parametrize(("returncode", "expected"), [(0, wait_for.EXIT_OK), (1, wait_for.EXIT_FAILED)])
def test_ci_maps_gh_watch_exit_status(returncode, expected, capsys):
    gh = FakeGh(checks=[completed(returncode, stdout="build\tpass\n")])
    clock = FakeClock()
    assert wait_for.wait_ci(REPO, 7, None, 60, 5, runner=gh, sleep=clock.sleep, clock=clock) == expected
    assert gh.calls[0][:4] == ["pr", "checks", "7", "--repo"]
    assert "--watch" in gh.calls[0]


def test_ci_timeout_when_gh_watch_overruns():
    gh = FakeGh(checks=[subprocess.TimeoutExpired("gh", 60)])
    clock = FakeClock()
    assert wait_for.wait_ci(REPO, 7, None, 60, 5, runner=gh, sleep=clock.sleep, clock=clock) == wait_for.EXIT_TIMEOUT


def test_ci_retries_until_checks_register_then_times_out():
    gh = FakeGh(checks=[completed(1, stderr="no checks reported on the 'x' branch")])
    clock = FakeClock()
    code = wait_for.wait_ci(REPO, 7, None, 30, 10, runner=gh, sleep=clock.sleep, clock=clock)
    assert code == wait_for.EXIT_TIMEOUT
    assert len(gh.calls) == 3


def test_ci_gh_error_without_table_is_not_a_ci_failure():
    gh = FakeGh(checks=[completed(1, stderr="HTTP 401: Bad credentials")])
    clock = FakeClock()
    assert wait_for.wait_ci(REPO, 7, None, 60, 5, runner=gh, sleep=clock.sleep, clock=clock) == wait_for.EXIT_ERROR


def test_ci_superseded_before_and_after_watch():
    clock = FakeClock()
    before = FakeGh(views=[head("bbb")], checks=[completed(0, stdout="ok")])
    assert wait_for.wait_ci(REPO, 7, "aaa", 60, 5, before, clock.sleep, clock) == wait_for.EXIT_SUPERSEDED
    assert not any(c[1] == "checks" for c in before.calls)

    after = FakeGh(views=[head("aaa"), head("ccc")], checks=[completed(0, stdout="ok")])
    assert wait_for.wait_ci(REPO, 7, "aaa", 60, 5, after, clock.sleep, clock) == wait_for.EXIT_SUPERSEDED

    same = FakeGh(views=[head("aaa")], checks=[completed(0, stdout="ok")])
    assert wait_for.wait_ci(REPO, 7, "aaa", 60, 5, same, clock.sleep, clock) == wait_for.EXIT_OK


def test_ci_output_is_redacted(capsys):
    token = "gh" + "s_" + "D" * 36
    gh = FakeGh(checks=[completed(0, stdout=f"build pass {token}")])
    clock = FakeClock()
    wait_for.wait_ci(REPO, 7, None, 60, 5, runner=gh, sleep=clock.sleep, clock=clock)
    assert token not in capsys.readouterr().out


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"state": "MERGED", "mergeCommit": {"oid": "m1"}}, wait_for.EXIT_OK),
        ({"state": "CLOSED", "mergeCommit": None}, wait_for.EXIT_FAILED),
    ],
)
def test_merged_terminal_states(payload, expected, capsys):
    gh = FakeGh(views=[completed(stdout=json.dumps({"state": "OPEN"})), completed(stdout=json.dumps(payload))])
    clock = FakeClock()
    assert wait_for.wait_merged(REPO, 7, 600, 60, runner=gh, sleep=clock.sleep, clock=clock) == expected
    assert len(gh.calls) == 2
    if expected == wait_for.EXIT_OK:
        assert "merge_commit=m1" in capsys.readouterr().out


def test_merged_times_out_and_survives_transient_gh_errors():
    gh = FakeGh(views=[completed(1, stderr="network"), completed(stdout=json.dumps({"state": "OPEN"}))])
    clock = FakeClock()
    assert wait_for.wait_merged(REPO, 7, 120, 60, runner=gh, sleep=clock.sleep, clock=clock) == wait_for.EXIT_TIMEOUT
    assert len(gh.calls) == 3


def test_cli_parses_subcommands(monkeypatch):
    seen = {}
    monkeypatch.setattr(wait_for, "wait_ci", lambda *a: seen.setdefault("ci", a) and 0)
    monkeypatch.setattr(wait_for, "wait_merged", lambda *a: seen.setdefault("merged", a) and 2)
    assert wait_for.main(["ci", REPO, "5", "--sha", "abc", "--timeout", "10"]) == 0
    assert seen["ci"] == (REPO, 5, "abc", 10.0, 30)
    assert wait_for.main(["merged", REPO, "5"]) == 2
    assert seen["merged"] == (REPO, 5, 86400.0, 60)
