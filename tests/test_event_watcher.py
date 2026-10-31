"""Unit tests for the GitHub event watcher (Bean 0182). No network: `gh api -i` is faked."""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent / ".agents" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import event_watcher  # noqa: E402

REPO = "Holon-Agentic-Coder/holon-coherence"
PULLS = f"repos/{REPO}/pulls?state=open&per_page=100"


def checks_path(sha):
    return f"repos/{REPO}/commits/{sha}/check-runs?per_page=100"


def reviews_path(pr):
    return f"repos/{REPO}/pulls/{pr}/reviews?per_page=100"


class FakeGitHub:
    """Serves `gh api -i` responses from a dict of path -> JSON body, honouring If-None-Match like GitHub."""

    def __init__(self):
        self.bodies = {}
        self.calls = []
        self.fail = set()

    def __call__(self, args):
        assert args[:2] == ["api", "-i"]
        path = args[2]
        sent = args[args.index("-H") + 1].split(": ", 1)[1] if "-H" in args else None
        self.calls.append((path, sent))
        if path in self.fail:
            return subprocess.CompletedProcess(args, 1, "HTTP/2.0 502 Bad Gateway\r\n\r\n", "gh: HTTP 502")
        body = json.dumps(self.bodies.get(path, []), sort_keys=True)
        etag = f'W/"{abs(hash(body))}"'
        if sent == etag:
            return subprocess.CompletedProcess(args, 1, f"HTTP/2.0 304 Not Modified\r\nEtag: {etag}\r\n\r\n", "")
        return subprocess.CompletedProcess(args, 0, f"HTTP/2.0 200 OK\r\nEtag: {etag}\r\n\r\n{body}", "")

    def set_open(self, *prs):
        self.bodies[PULLS] = [{"number": n, "head": {"sha": sha}} for n, sha in prs]

    def set_checks(self, sha, *runs):
        self.bodies[checks_path(sha)] = {
            "total_count": len(runs),
            "check_runs": [{"name": n, "status": s, "conclusion": c} for n, s, c in runs],
        }


def make_watcher(tmp_path, gh, **kwargs):
    return event_watcher.Watcher(
        [REPO],
        tmp_path / "events.jsonl",
        tmp_path / "state.json",
        runner=gh,
        clock=lambda: "2026-10-29T00:00:00Z",
        **kwargs,
    )


def types(events):
    return [(e["type"], e["pr"], e["sha"]) for e in events]


def test_parse_include_output_handles_crlf_and_304():
    status, headers, body = event_watcher.parse_include_output('HTTP/2.0 200 OK\r\nEtag: W/"x"\r\n\r\n[1]')
    assert (status, headers["etag"], body) == (200, 'W/"x"', "[1]")
    assert event_watcher.parse_include_output("HTTP/2.0 304 Not Modified\r\n\r\n")[0] == 304
    assert event_watcher.parse_include_output("")[0] == 0


def test_summarise_check_runs():
    def runs(*items):
        return {"check_runs": [{"name": n, "status": s, "conclusion": c} for n, s, c in items]}

    assert event_watcher.summarise_check_runs({"check_runs": []}) == ("ci_pending", [])
    assert event_watcher.summarise_check_runs(runs(("a", "in_progress", None))) == ("ci_pending", [])
    assert event_watcher.summarise_check_runs(runs(("a", "completed", "success"), ("b", "completed", "skipped"))) == (
        "ci_passed",
        [],
    )
    failed = runs(("b", "completed", "failure"), ("a", "in_progress", None))
    assert event_watcher.summarise_check_runs(failed) == ("ci_failed", ["b"])


def test_first_cycle_is_a_silent_baseline_then_changes_emit(tmp_path):
    gh = FakeGitHub()
    gh.set_open((7, "aaa"))
    gh.set_checks("aaa", ("test", "in_progress", None))
    watcher = make_watcher(tmp_path, gh)
    assert watcher.poll_once() == []
    assert not (tmp_path / "events.jsonl").exists()

    gh.set_checks("aaa", ("test", "completed", "failure"))
    assert types(watcher.poll_once()) == [("ci_failed", 7, "aaa")]
    assert watcher.emitted[0]["detail"] == {"failing_jobs": ["test"]}

    gh.set_open((7, "bbb"))
    gh.set_checks("bbb", ("test", "completed", "success"))
    events = watcher.poll_once()
    assert types(events) == [("head_moved", 7, "bbb"), ("ci_passed", 7, "bbb")]
    assert events[0]["detail"] == {"from": "aaa", "to": "bbb"}
    assert checks_path("aaa") not in watcher.state["etags"]


def test_unchanged_resources_are_conditional_and_silent(tmp_path):
    gh = FakeGitHub()
    gh.set_open((7, "aaa"))
    gh.set_checks("aaa", ("test", "completed", "success"))
    watcher = make_watcher(tmp_path, gh)
    watcher.poll_once()
    gh.calls.clear()
    assert watcher.poll_once() == []
    assert gh.calls and all(sent is not None for _, sent in gh.calls)


def test_merge_close_new_pr_and_reviews(tmp_path):
    gh = FakeGitHub()
    gh.set_open((7, "aaa"), (8, "bbb"))
    gh.bodies[reviews_path(7)] = [{"id": 1, "state": "COMMENTED", "commit_id": "aaa", "user": {"login": "x"}}]
    watcher = make_watcher(tmp_path, gh)
    watcher.poll_once()

    gh.set_open((9, "ccc"))
    gh.bodies[f"repos/{REPO}/pulls/7"] = {"merged_at": "2026-10-29T01:00:00Z", "merge_commit_sha": "m7"}
    gh.bodies[f"repos/{REPO}/pulls/8"] = {"merged_at": None, "closed_at": "2026-10-29T01:00:00Z"}
    gh.bodies[reviews_path(9)] = [{"id": 5, "state": "APPROVED", "commit_id": "ccc", "user": {"login": "y"}}]
    events = watcher.poll_once()
    assert types(events) == [
        ("pr_merged", 7, "aaa"),
        ("pr_closed", 8, "bbb"),
        ("head_moved", 9, "ccc"),
        ("ci_pending", 9, "ccc"),
        ("review_posted", 9, "ccc"),
    ]
    assert events[0]["detail"]["merge_commit"] == "m7"
    assert events[2]["detail"] == {"from": None, "to": "ccc"}
    assert events[4]["detail"]["state"] == "APPROVED"
    assert [e["seq"] for e in events] == [1, 2, 3, 4, 5]
    assert set(watcher.state["prs"][REPO]) == {"9"}


def test_state_survives_restart_without_duplicate_events(tmp_path):
    gh = FakeGitHub()
    gh.set_open((7, "aaa"))
    make_watcher(tmp_path, gh).poll_once()
    gh.set_open((7, "bbb"))
    assert types(make_watcher(tmp_path, gh).poll_once())[0] == ("head_moved", 7, "bbb")
    restarted = make_watcher(tmp_path, gh)
    assert restarted.poll_once() == []
    assert restarted.state["next_seq"] == 3


def test_errors_are_contained_per_pr(tmp_path, capsys):
    gh = FakeGitHub()
    gh.set_open((7, "aaa"), (8, "bbb"))
    watcher = make_watcher(tmp_path, gh)
    watcher.poll_once()
    gh.fail.add(checks_path("aaa"))
    gh.set_checks("bbb", ("test", "completed", "success"))
    assert types(watcher.poll_once()) == [("ci_passed", 8, "bbb")]
    assert "502" in capsys.readouterr().err


def test_written_events_are_redacted(tmp_path):
    token = "gh" + "p_" + "Z" * 36
    gh = FakeGitHub()
    gh.set_open((7, "aaa"))
    watcher = make_watcher(tmp_path, gh)
    watcher.poll_once()
    gh.bodies[reviews_path(7)] = [{"id": 2, "state": "COMMENTED", "html_url": f"https://x/{token}"}]
    watcher.poll_once()
    assert token not in (tmp_path / "events.jsonl").read_text()


def test_rotation_and_consumer_cursor(tmp_path):
    log = tmp_path / "events.jsonl"
    cursor = tmp_path / "cursor.json"
    gh = FakeGitHub()
    gh.set_open()
    watcher = make_watcher(tmp_path, gh, max_bytes=200, keep=2)
    watcher.poll_once()
    for i in range(1, 6):
        gh.set_open((i, f"sha{i}"))
        watcher.poll_once()
    assert log.with_name("events.jsonl.1").exists()

    first = event_watcher.consume(log, cursor, keep=2)
    seqs = [e["seq"] for e in first]
    assert seqs == sorted(seqs) and seqs[-1] == watcher.state["next_seq"] - 1
    assert event_watcher.consume(log, cursor, keep=2) == []

    gh.set_open((9, "sha9"))
    watcher.poll_once()
    assert event_watcher.consume(log, cursor, peek=True, keep=2)
    assert [e["type"] for e in event_watcher.consume(log, cursor, keep=2)][0] == "pr_closed"


def test_read_events_skips_torn_lines(tmp_path):
    log = tmp_path / "events.jsonl"
    log.write_text('{"seq": 1}\n{"seq": 2\n')
    assert [e["seq"] for e in event_watcher.read_events(log)] == [1]


def test_cli_watch_and_consume(tmp_path, capsys):
    gh = FakeGitHub()
    gh.set_open((7, "aaa"))
    args = ["--dir", str(tmp_path), "watch", "--repo", REPO, "--max-cycles", "2", "--interval", "0"]
    sleeps = []
    assert event_watcher.main(args, runner=gh, sleep=sleeps.append) == 0
    assert sleeps == [0.0]
    assert (tmp_path / "events_watcher_state.json").exists()
    assert event_watcher.main(["--dir", str(tmp_path), "consume"]) == 0
    assert capsys.readouterr().out == ""


def test_default_events_dir_handles_shallow_install_paths():
    assert event_watcher.default_events_dir(Path("/app/event_watcher.py")) == Path(".subagent")
    harness = Path("/h/.agents/scripts/event_watcher.py")
    assert event_watcher.default_events_dir(harness) == Path("/h/.subagent")


def test_failed_first_read_does_not_consume_the_baseline(tmp_path):
    gh = FakeGitHub()
    gh.set_open((7, "aaa"))
    gh.fail.add(PULLS)
    watcher = make_watcher(tmp_path, gh)
    assert watcher.poll_once() == []
    assert watcher.state["baselined"] == []
    gh.fail.clear()
    assert watcher.poll_once() == []
    assert watcher.state["baselined"] == [REPO]
