import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent / ".agents" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import slot_keeper  # noqa: E402

NOW = datetime(2026, 11, 27, 5, 0, 0, tzinfo=UTC)


class Harness:
    def __init__(self, root, live=(), pr_files=None):
        self.root = root
        self.live = list(live)
        self.pr_files = pr_files or {}
        self.launches = []
        self.environment = slot_keeper.Environment(
            root=root,
            process_lines=lambda: self.live,
            open_pr_files=lambda: self.pr_files,
            launch=lambda argv, cwd, log: self.launches.append((argv, cwd, log)),
            now=lambda: NOW,
        )

    def intent(self, name, scope):
        path = self.root / "todo" / f"intent-{name}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"slug": name, "scope": scope}))
        return f"todo/intent-{name}.json"

    def entry(self, bean, name, scope, **fields):
        return slot_keeper.Entry(bean=bean, intent_path=self.intent(name, scope), **fields)

    def live_line(self, intent_path):
        return f"python .agents/skills/holon_flow/scripts/run_holon_flow.py {intent_path} --bean 1 --agent a"


def test_live_count_dedupes_wrapper_and_child_processes_by_intent():
    lines = [
        "uv run python .agents/skills/holon_flow/scripts/run_holon_flow.py todo/i-a.json --bean 1 --model m",
        "/venv/bin/python .agents/skills/holon_flow/scripts/run_holon_flow.py todo/i-a.json --bean 1 --model m",
        "python run_holon_flow.py todo/i-b.json --target-worktree apps/x/main --agent claude-agent",
        "python run_holon_flow.py --checkpoint todo/checkpoint-c.json todo/i-c.json",
        "grep run_holon_flow",
        "python something_else.py",
    ]
    keys = slot_keeper.live_flow_keys(lines)
    assert keys == {"todo/i-a.json", "todo/i-b.json", "todo/i-c.json", "grep"} - {"grep"}


def test_live_4_cap_8_launches_disjoint_until_cap_and_logs_reason_for_each_held(tmp_path):
    harness = Harness(tmp_path)
    live = [harness.live_line(harness.intent(f"live{i}", [f"src/live{i}.py"])) for i in range(4)]
    harness.live = live
    entries = [
        harness.entry("0400", "q400", ["src/a.py"]),
        harness.entry("0532", "q532", ["src/b.py"]),
        harness.entry("0570", "q570", ["src/shared.py"]),
        harness.entry("0558", "q558", ["src/shared.py"]),
        harness.entry("0559", "q559", ["src/live1.py"]),
        harness.entry("0560", "q560", ["src/c.py"]),
    ]
    result, remaining = slot_keeper.run_pass(harness.environment, entries)
    assert result.live == 4
    assert result.launched == ["0400", "0532", "0570", "0560"]
    assert dict(result.held) == {
        "0558": "overlap:src/shared.py:launched:0570",
        "0559": "overlap:src/live1.py:live:intent-live1",
    }
    assert [entry.bean for entry in remaining] == ["0558", "0559"]


def test_cap_reached_holds_the_rest_with_reason_cap(tmp_path):
    harness = Harness(tmp_path)
    harness.live = [harness.live_line(harness.intent(f"live{i}", [f"src/live{i}.py"])) for i in range(7)]
    entries = [harness.entry("0001", "n1", ["a.py"]), harness.entry("0002", "n2", ["b.py"])]
    result, _ = slot_keeper.run_pass(harness.environment, entries)
    assert result.launched == ["0001"]
    assert result.held == [("0002", "cap")]


def test_open_pr_files_hold_a_candidate_and_own_pr_does_not(tmp_path):
    harness = Harness(tmp_path, pr_files={7: ["src/a.py"], 9: ["src/z.py"]})
    blocked = harness.entry("0001", "n1", ["src/a.py"])
    own = harness.entry("0002", "n2", ["src/z.py"], own_pr=9)
    result, _ = slot_keeper.run_pass(harness.environment, [blocked, own])
    assert result.held == [("0001", "overlap:src/a.py:pr:7")]
    assert result.launched == ["0002"]


def test_plan_touch_set_of_a_live_flow_blocks_a_candidate(tmp_path):
    harness = Harness(tmp_path)
    live_intent = harness.intent("liveone", ["src/declared.py"])
    plan_dir = tmp_path / "apps" / "repo" / "flow-liveone" / "plans" / "I-1-liveone"
    plan_dir.mkdir(parents=True)
    (plan_dir / "P-1.md").write_text("# Plan\n\n## Touch Set\n\n- `src/planned.py`\n- `src/other.py`\n\n## Next\n")
    (plan_dir / "P-1_calibration.md").write_text("## Touch Set\n\n- `src/ignored.py`\n")
    harness.live = [harness.live_line(live_intent)]
    entries = [harness.entry("0001", "n1", ["src/planned.py"]), harness.entry("0002", "n2", ["src/ignored.py"])]
    result, _ = slot_keeper.run_pass(harness.environment, entries)
    assert result.held == [("0001", "overlap:src/planned.py:live:intent-liveone")]
    assert result.launched == ["0002"]


def test_parked_resume_reserves_files_and_launches_before_new_entries(tmp_path):
    harness = Harness(tmp_path)
    checkpoint = tmp_path / "todo" / "checkpoint.json"
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    checkpoint.write_text("{}")
    resume = harness.entry(
        "0010", "p10", ["src/p.py"], kind="resume", checkpoint="todo/checkpoint.json", blocked_by=("0011",)
    )
    (tmp_path / ".beans").mkdir()
    (tmp_path / ".beans" / "x-0011-blocker.md").write_text("---\nstatus: in-progress\n---\n")
    fresh = harness.entry("0001", "n1", ["src/p.py"])
    result, remaining = slot_keeper.run_pass(harness.environment, [fresh, resume])
    assert result.held == [("0010", "blocked_by:0011"), ("0001", "overlap:src/p.py:parked:0010")]
    assert result.launched == []
    assert len(remaining) == 2


def test_resume_launches_with_checkpoint_and_never_when_already_live(tmp_path):
    harness = Harness(tmp_path)
    (tmp_path / "todo").mkdir(exist_ok=True)
    (tmp_path / "todo" / "checkpoint.json").write_text("{}")
    resume = harness.entry("0010", "p10", ["src/p.py"], kind="resume", checkpoint="todo/checkpoint.json")
    result, _ = slot_keeper.run_pass(harness.environment, [resume])
    argv = harness.launches[0][0]
    assert result.launched == ["0010"]
    assert argv[argv.index("--checkpoint") + 1] == "todo/checkpoint.json"
    assert "--bean" not in argv
    assert "--no-wait-on-overlap" in argv
    harness.live = [harness.live_line(resume.intent_path)]
    harness.launches.clear()
    result, _ = slot_keeper.run_pass(harness.environment, [resume])
    assert result.held == [("0010", "already-live")]
    assert harness.launches == []


def test_new_launch_passes_bean_agent_and_model(tmp_path):
    harness = Harness(tmp_path)
    slot_keeper.run_pass(harness.environment, [harness.entry("0042", "n42", ["src/a.py"])])
    argv = harness.launches[0][0]
    assert slot_keeper.DEFAULT_AGENT == "antigravity-agent"
    assert slot_keeper.DEFAULT_MODEL == "gemini-4-neon"
    assert argv[:4] == ["uv", "run", "python", slot_keeper.FLOW_SCRIPT_PATH]
    assert argv[argv.index("--bean") + 1] == "0042"
    assert argv[argv.index("--agent") + 1] == "antigravity-agent"
    assert argv[argv.index("--model") + 1] == "gemini-4-neon"
    assert harness.launches[0][2] == tmp_path / "todo" / "flow-n42.log"


def test_check_failures_are_held_with_a_reason(tmp_path):
    harness = Harness(tmp_path)
    directory = harness.entry("0001", "n1", ["src/pkg/"])
    empty = harness.entry("0002", "n2", [])
    missing = slot_keeper.Entry(bean="0003", intent_path="todo/nope.json")
    result, _ = slot_keeper.run_pass(harness.environment, [directory, empty, missing])
    assert result.held == [
        ("0001", "check:scope-has-directory"),
        ("0002", "check:scope-empty"),
        ("0003", "check:intent-missing"),
    ]


def test_log_line_lists_only_this_pass_and_queue_drops_launched(tmp_path):
    harness = Harness(tmp_path)
    queue = tmp_path / "todo" / "slot-queue.json"
    log = tmp_path / "todo" / "slot-keeper.log"
    entries = [harness.entry("0001", "n1", ["src/a.py"]), harness.entry("0002", "n2", ["src/a.py"])]
    slot_keeper.write_queue(queue, entries)
    first = slot_keeper.pass_once(harness.environment, queue, log)
    assert first.launched == ["0001"]
    assert [entry.bean for entry in slot_keeper.read_queue(queue)] == ["0002"]
    harness.live = [harness.live_line(entries[0].intent_path)]
    slot_keeper.pass_once(harness.environment, queue, log)
    lines = log.read_text().splitlines()
    assert lines[0] == "2026-11-27T05:00:00Z live=0 cap=8 launched=0001 held=0002:overlap:src/a.py:launched:0001"
    assert lines[1] == "2026-11-27T05:00:00Z live=1 cap=8 launched=- held=0002:overlap:src/a.py:live:intent-n1"


def test_dry_run_launches_nothing_and_keeps_the_queue(tmp_path):
    harness = Harness(tmp_path)
    queue = tmp_path / "todo" / "slot-queue.json"
    slot_keeper.write_queue(queue, [harness.entry("0001", "n1", ["src/a.py"])])
    slot_keeper.pass_once(harness.environment, queue, tmp_path / "log", dry_run=True)
    assert [entry.bean for entry in slot_keeper.read_queue(queue)] == ["0001"]


def test_pull_request_lookup_failure_is_logged_not_swallowed(tmp_path):
    harness = Harness(tmp_path)

    def broken():
        raise RuntimeError("gh pr list failed")

    harness.environment.open_pr_files = broken
    queue = tmp_path / "q.json"
    slot_keeper.write_queue(queue, [harness.entry("0001", "n1", ["src/a.py"])])
    result = slot_keeper.pass_once(harness.environment, queue, tmp_path / "log")
    assert result.held == [("all", "check:gh pr list failed")]
    assert harness.launches == []


def test_heartbeat_notice_after_120_seconds_without_a_pass(tmp_path):
    log = tmp_path / "slot-keeper.log"
    alerts = tmp_path / "slot-keeper-alerts.log"
    log.write_text("2026-11-27T05:00:00Z live=8 cap=8 launched=- held=-\n")
    assert slot_keeper.check_heartbeat(log, alerts, NOW + timedelta(seconds=120)) == 0
    assert not alerts.exists()
    assert slot_keeper.check_heartbeat(log, alerts, NOW + timedelta(seconds=121)) == 3
    assert "silent for 121s" in alerts.read_text()


def test_heartbeat_notice_when_the_log_is_missing(tmp_path):
    assert slot_keeper.check_heartbeat(tmp_path / "none.log", tmp_path / "alerts", NOW) == 3


def test_flow_state_change_triggers_a_pass_within_one_poll(tmp_path):
    state_dir = tmp_path / ".subagent"
    state_dir.mkdir()
    passes = []
    ticks = {"count": 0}

    def sleep(_):
        ticks["count"] += 1
        if ticks["count"] == 2:
            (state_dir / "flow_x_state.json").write_text("{}")

    clock_values = iter(range(0, 1000))
    slot_keeper.loop_forever(
        lambda: passes.append(ticks["count"]),
        state_dir,
        interval_seconds=10_000,
        sleep=sleep,
        clock=lambda: next(clock_values) * 0.001,
        max_ticks=5,
    )
    assert passes == [0, 2]


def test_main_check_heartbeat_exit_code(tmp_path):
    (tmp_path / "todo").mkdir()
    assert slot_keeper.main(["--root", str(tmp_path), "--check-heartbeat"]) == 3


def test_script_has_no_docstrings_or_explanatory_comments():
    source = (SCRIPT_DIR / "slot_keeper.py").read_text().splitlines()
    comments = [line for line in source[1:] if line.strip().startswith("#") and not line.strip().startswith("# why:")]
    assert comments == []
    assert '"""' not in "\n".join(source)
