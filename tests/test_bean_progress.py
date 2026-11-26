"""Unit tests for bean_progress in-flight dashboard (bean-progress skill)."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent / ".agents" / "skills" / "bean_progress" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import bean_progress  # noqa: E402


def _make_bean(beans_dir: Path, num: str, slug: str, frontmatter: str) -> Path:
    path = beans_dir / f"holon-agentic-coder-ref-metadata-{num}--{slug}.md"
    path.write_text(
        f"---\n# holon-agentic-coder-ref-metadata-{num}\n{frontmatter}\n---\n\n## Action\n", encoding="utf-8"
    )
    return path


class TestParseFrontmatter:
    """Verify folded multiline scalars, sequence lists, and edge cases."""

    def test_multiline_title_and_lists(self) -> None:
        content = (
            "---\n"
            "# comment line\n"
            "title:\n"
            '  "Decompose the intent and\n'
            '  plan stage modules"\n'
            "status: in-progress\n"
            "tags:\n"
            "  - refactor\n"
            "  - holon-agentic-coder\n"
            "blocked_by:\n"
            "  - holon-agentic-coder-ref-metadata-0190\n"
            "---\n"
        )
        fm = bean_progress.parse_frontmatter(content)
        assert fm["title"] == "Decompose the intent and plan stage modules"
        assert fm["status"] == "in-progress"
        assert fm["tags"] == ["refactor", "holon-agentic-coder"]
        assert fm["blocked_by"] == ["holon-agentic-coder-ref-metadata-0190"]

    def test_missing_frontmatter(self) -> None:
        assert bean_progress.parse_frontmatter("# Not frontmatter\n") == {}


class TestExclusionAndCorrelation:
    """Strict exclusion of completed/scrapped beans and grouping across artifacts."""

    def test_excludes_completed_and_scrapped_even_with_stale_flow_and_pr(self, tmp_path: Path) -> None:
        beans_dir = tmp_path / ".beans"
        beans_dir.mkdir()
        _make_bean(beans_dir, "0199", "done-bean", "title: Done work\nstatus: completed\n")
        _make_bean(beans_dir, "0200", "scrapped-bean", "title: Scrapped work\nstatus: scrapped\n")
        _make_bean(beans_dir, "0354", "active-bug", "title: Active bug\nstatus: in-progress\n")
        _make_bean(beans_dir, "0351", "todo-with-wt", "title: Todo with worktree\nstatus: todo\n")
        _make_bean(
            beans_dir, "0353", "orphan-in-progress", "title: Needs worktree\nstatus: in-progress\ntags:\n  - harness\n"
        )

        beans = bean_progress.scan_beans(beans_dir)
        intents = [
            bean_progress.IntentMapping(path=tmp_path / "intent-0199-done.json", slug="done", bean_nums=["0199"]),
            bean_progress.IntentMapping(
                path=tmp_path / "intent-0199-0354-mixed.json",
                slug="mixed-flow",
                bean_nums=["0199", "0354"],
            ),
            bean_progress.IntentMapping(path=tmp_path / "intent-0351-todo.json", slug="todo-flow", bean_nums=["0351"]),
        ]
        worktrees = [
            bean_progress.WorktreeFlow(
                repo_name="HAC",
                path=tmp_path / "apps" / "flow-done",
                dir_name="flow-done",
                slug="done",
                current_stage="calibrate",
                completed_stages=["intent", "plan", "execute", "review", "calibrate"],
                timestamp="2026-11-21T10:00:00Z",
                agent="claude-agent",
                model="claude-opus-5-5",
                execution_branch="I-1-done/P-2/E-3/_",
                plan_branch="I-1-done/P-2/_",
                intent_branch="I-1-done/_",
                review_iterations_done=2,
                admission={"state": "admitted"},
                stage_results={"calibrate": {"status": "success"}},
            ),
            bean_progress.WorktreeFlow(
                repo_name="HAC",
                path=tmp_path / "apps" / "flow-mixed-flow",
                dir_name="flow-mixed-flow",
                slug="mixed-flow",
                current_stage="review",
                completed_stages=["intent", "plan", "execute"],
                timestamp="2026-11-21T11:00:00Z",
                agent="claude-agent",
                model="claude-sonnet-4-6",
                execution_branch="I-10-mixed-flow/P-2/E-3/_",
                plan_branch="I-10-mixed-flow/P-2/_",
                intent_branch="I-10-mixed-flow/_",
                review_iterations_done=6,
                admission={"state": "admitted"},
                stage_results={"review": {"status": "failed", "error": "Autonomous review halted: verdict FAILED."}},
                dirty_count=2,
            ),
            bean_progress.WorktreeFlow(
                repo_name="dev-env",
                path=tmp_path / "dev-env" / "flow-todo-flow",
                dir_name="flow-todo-flow",
                slug="todo-flow",
                current_stage="plan",
                completed_stages=["intent"],
                timestamp="2026-11-21T11:10:00Z",
                agent="antigravity-agent",
                model="gemini-3.8-flash-medium",
                execution_branch=None,
                plan_branch="I-20-todo-flow/P-1/_",
                intent_branch="I-20-todo-flow/_",
                review_iterations_done=0,
                admission={},
                stage_results={},
            ),
        ]
        prs = [
            bean_progress.PullRequestInfo(
                repo_name="HAC",
                number=227,
                title="Done PR",
                url="https://example.com/pr/227",
                head_ref_name="I-1-done/P-2/E-3/_",
                mergeable="MERGEABLE",
                is_draft=False,
                reviews_count=3,
                comments_count=0,
                ci_summary="11/11 pass",
            ),
            bean_progress.PullRequestInfo(
                repo_name="HAC",
                number=230,
                title="Mixed active PR",
                url="https://example.com/pr/230",
                head_ref_name="I-10-mixed-flow/P-2/E-3/_",
                mergeable="MERGEABLE",
                is_draft=False,
                reviews_count=0,
                comments_count=0,
                ci_summary="11/11 pass",
            ),
        ]

        rows = bean_progress.build_in_flight_rows(beans, intents, worktrees, prs, {})
        all_bean_ids = [n for r in rows for n in r.bean_nums]
        assert "0199" not in all_bean_ids
        assert "0200" not in all_bean_ids
        assert sorted(all_bean_ids) == ["0351", "0353", "0354"]

        by_first = {r.bean_nums[0]: r for r in rows}
        assert "#230" in by_first["0354"].pr_ci
        assert by_first["0354"].stage == "Stage 4 (Halted iter 6)"
        assert "dirty: 2 file(s)" in by_first["0354"].notes
        assert by_first["0351"].target == "dev-env"
        assert "bean status: todo" in by_first["0351"].notes
        assert by_first["0353"].stage == "Not started"
        assert by_first["0353"].target == "harness"

    def test_groups_combined_multi_bean_flow(self, tmp_path: Path) -> None:
        beans_dir = tmp_path / ".beans"
        beans_dir.mkdir()
        _make_bean(beans_dir, "0347", "a", "title: Part A\nstatus: in-progress\n")
        _make_bean(beans_dir, "0354", "b", "title: Part B\nstatus: in-progress\n")
        beans = bean_progress.scan_beans(beans_dir)
        intents = [
            bean_progress.IntentMapping(
                path=tmp_path / "intent-0347-0354-combined.json",
                slug="combined",
                bean_nums=["0347", "0354"],
            )
        ]
        wt = bean_progress.WorktreeFlow(
            repo_name="HAC",
            path=tmp_path / "flow-combined",
            dir_name="flow-combined",
            slug="combined",
            current_stage="review",
            completed_stages=["intent", "plan", "execute"],
            timestamp="2026-11-21T12:00:00Z",
            agent="claude-agent",
            model="claude-sonnet-4-6",
            execution_branch="I-1-combined/P-1/E-1/_",
            plan_branch="I-1-combined/P-1/_",
            intent_branch="I-1-combined/_",
            review_iterations_done=6,
            admission={"state": "admitted"},
            stage_results={"calibrate": {"status": "success"}, "review": {"status": "skipped"}},
        )
        rows = bean_progress.build_in_flight_rows(beans, intents, [wt], [], {})
        assert len(rows) == 1
        assert rows[0].bean_nums == ["0347", "0354"]
        assert rows[0].stage == "Stage 5 (Calibrated; review skipped)"
        assert "--skip-review" in rows[0].notes


class TestLiveProcessesAndChecks:
    """Verify strict ancestor session detection, live CLI overrides, and CI rollups."""

    def test_ancestor_owner_ignores_child_claude_agent_flag(self, tmp_path: Path) -> None:
        wt_path = (tmp_path / "flow-review").resolve()
        wt_path.mkdir()
        wt = bean_progress.WorktreeFlow(
            repo_name="HAC",
            path=wt_path,
            dir_name="flow-review",
            slug="review",
            current_stage="review",
            completed_stages=["intent", "plan", "execute"],
            timestamp=None,
            agent="claude-agent",
            model="claude-sonnet-4-6",
            execution_branch=None,
            plan_branch=None,
            intent_branch=None,
            review_iterations_done=6,
            admission={"state": "admitted"},
            stage_results={"review": {"status": "failed", "error": "Autonomous review halted: verdict FAILED."}},
        )
        procs = [
            bean_progress.ProcessInfo(1, 0, "05:00:00", "Ss", "/sbin/launchd"),
            bean_progress.ProcessInfo(41784, 1, "04:00:00", "S", "/Users/u/.local/bin/agy serve"),
            bean_progress.ProcessInfo(
                32031,
                41784,
                "32:03",
                "Ss+",
                f"python3 run_holon_flow.py --target-worktree {wt_path} --agent claude-agent --model claude-opus-5-5",
            ),
            bean_progress.ProcessInfo(
                34515,
                32031,
                "13:33",
                "S+",
                f"docker run -e HOLON_ROLE=review-loop -v {wt_path}:/home/holon/.holon-sandbox/workspace "
                "holon/agent-claude claude-agent claude-opus-5-5 --resolve --iteration=7",
            ),
        ]
        live = bean_progress.match_live_flows(procs, [wt], [])
        tree = live[str(wt_path)]
        assert tree.session_owner == "Antigravity"
        assert tree.root_pid == 32031
        assert tree.model == "claude-opus-5-5"
        assert tree.docker_role == "review-loop"
        assert tree.docker_resolve is True
        assert tree.docker_iteration == 7

        assert bean_progress._derive_stage(wt, tree, True) == "Stage 4 (Resolve iter 7)"
        assert bean_progress._derive_live_runner(wt, tree) == "live · 32m (PID 32031, Antigravity)"
        assert bean_progress._derive_notes([], wt, None, tree) == "Resolving review findings"

    def test_detects_claude_code_parent_and_duplicate_trees(self, tmp_path: Path) -> None:
        wt_path = (tmp_path / "flow-exec").resolve()
        wt_path.mkdir()
        wt = bean_progress.WorktreeFlow(
            repo_name="HAC",
            path=wt_path,
            dir_name="flow-exec",
            slug="exec",
            current_stage="execute",
            completed_stages=["intent", "plan"],
            timestamp=None,
            agent="antigravity-agent",
            model="gemini-3.8-flash-medium",
            execution_branch=None,
            plan_branch=None,
            intent_branch=None,
            review_iterations_done=0,
            admission={"state": "blocked", "blocked_by": [{"number": 228, "files": ["flow/__init__.py"]}]},
            stage_results={},
        )
        procs = [
            bean_progress.ProcessInfo(77752, 1, "03:00:00", "Ss", "claude --dangerously-skip-permissions"),
            bean_progress.ProcessInfo(
                12804,
                77752,
                "02:49:30",
                "Ss+",
                f"python3 run_holon_flow.py --target-worktree {wt_path} --model gemini-3.8-flash-medium",
            ),
            bean_progress.ProcessInfo(
                12900,
                77752,
                "00:05:00",
                "Ss+",
                f"holon flow --target-worktree {wt_path} --model gemini-3.8-flash-medium",
            ),
        ]
        live = bean_progress.match_live_flows(procs, [wt], [])
        tree = live[str(wt_path)]
        assert tree.session_owner == "Claude Code"
        assert tree.duplicate_trees == 2
        assert tree.kind == "polling"
        assert bean_progress._derive_stage(wt, tree, False) == "Stage 3 (Blocked: #228)"
        runner = bean_progress._derive_live_runner(wt, tree)
        assert "polling #228" in runner
        assert "2h49m" in runner
        assert "Claude Code" in runner

    def test_summarize_checks(self) -> None:
        assert bean_progress.summarize_checks([]) == "no checks"
        rollup = [
            {"status": "COMPLETED", "conclusion": "SUCCESS"},
            {"status": "COMPLETED", "conclusion": "FAILURE"},
            {"status": "IN_PROGRESS", "conclusion": ""},
            {"state": "SUCCESS"},
        ]
        assert bean_progress.summarize_checks(rollup) == "2/4 pass, 1 fail, 1 running"

    def test_table_escaping_and_empty_cli(self, tmp_path: Path, capsys) -> None:
        row = bean_progress.InFlightRow(
            bean_nums=["0123"],
            target="HAC",
            title="Pipe | inside title",
            stage="Stage 4",
            pr_ci="—",
            live_runner="Idle",
            notes="a | b",
            sort_bucket=0,
        )
        md = bean_progress.render_markdown_table([row])
        assert "Pipe \\| inside title" in md
        # The compact table carries no notes; they sit in the details list, where pipes need no escaping.
        assert "- **0123**: Idle; a | b" in md
        assert "a | b" not in md.split("**Last activity and notes**")[0]
        wide = bean_progress.render_markdown_table([row], wide=True)
        assert "Pipe \\| inside title" in wide
        assert "a \\| b" in wide

        (tmp_path / ".beans").mkdir()
        rc = bean_progress.main(["--repo-root", str(tmp_path), "--no-gh", "--no-ps"])
        assert rc == 0
        out = capsys.readouterr().out.strip()
        assert out == "No beans are currently in flight."

        rc_json = bean_progress.main(["--repo-root", str(tmp_path), "--no-gh", "--no-ps", "--json"])
        assert rc_json == 0
        assert json.loads(capsys.readouterr().out) == []


NOW = datetime(2026, 11, 23, 12, 0, 0, tzinfo=UTC)


def _wt(tmp_path: Path, name: str, slug: str, **kw) -> bean_progress.WorktreeFlow:
    base = {
        "repo_name": "HAC",
        "path": tmp_path / name,
        "dir_name": name,
        "slug": slug,
        "current_stage": "execute",
        "completed_stages": ["intent", "plan"],
        "timestamp": None,
        "agent": "claude-agent",
        "model": "claude-opus-5-5",
        "execution_branch": None,
        "plan_branch": None,
        "intent_branch": None,
        "review_iterations_done": 0,
        "admission": {},
        "stage_results": {},
    }
    base.update(kw)
    return bean_progress.WorktreeFlow(**base)


def _pr(number: int, head: str, title: str = "t") -> bean_progress.PullRequestInfo:
    return bean_progress.PullRequestInfo(
        "HAC", number, title, f"u/{number}", head, "MERGEABLE", False, 0, 0, "1/1 pass"
    )


class TestTimesAndColumns:
    def test_format_duration(self) -> None:
        f = bean_progress.format_duration
        assert f(None, NOW) == "—"
        assert f(datetime(2026, 11, 23, 11, 48, tzinfo=UTC), NOW) == "12m"
        assert f(datetime(2026, 11, 23, 10, 55, tzinfo=UTC), NOW) == "1h05m"
        assert f(datetime(2026, 11, 21, 9, 0, tzinfo=UTC), NOW) == "2d3h"
        assert f(datetime(2026, 11, 23, 11, 59, 30, tzinfo=UTC), NOW) == "30s"

    def test_stage_started_sources(self) -> None:
        mtime = datetime(2026, 11, 23, 1, 0, tzinfo=UTC)
        sr = {
            "execute": {"start_time": "2026-11-23T05:00:00Z", "end_time": "2026-11-23T06:00:00Z"},
            "review": {"status": "failed", "start_time": "2026-11-23T07:00:00Z", "end_time": "2026-11-23T08:00:00Z"},
        }
        assert bean_progress.derive_stage_started("review", sr, None, mtime) == parse(sr["review"]["start_time"])
        # current stage has no record: previous stage end
        assert bean_progress.derive_stage_started(
            "plan", {"intent": {"end_time": "2026-11-23T03:23:20Z"}}, "x", mtime
        ) == parse("2026-11-23T03:23:20Z")
        # nothing recorded: checkpoint timestamp then mtime
        assert bean_progress.derive_stage_started("plan", {}, "2026-11-23T02:00:00Z", mtime) == parse(
            "2026-11-23T02:00:00Z"
        )
        assert bean_progress.derive_stage_started("plan", {}, None, mtime) == mtime

    def test_total_time_earliest_of_branch_and_ledger(self, tmp_path: Path) -> None:
        ledger = tmp_path / "ledger.jsonl"
        ledger.write_text(
            json.dumps({"branch": "I-100-foo/_", "created_at": "2026-11-23T10:00:00Z"})
            + "\n"
            + json.dumps({"branch": "I-100-foo/P-1--1-child/_", "created_at": "2026-11-23T09:00:00Z"})
            + "\n"
            + json.dumps({"branch": "I-100-other/_", "created_at": "2026-11-01T00:00:00Z"})
            + "\n",
            encoding="utf-8",
        )
        assert bean_progress.ledger_first_created(ledger, "foo") == parse("2026-11-23T09:00:00Z")
        branch_ts = bean_progress.branch_started("I-1795388456-foo/_")
        assert branch_ts is not None
        assert bean_progress.earliest_of(branch_ts, parse("2030-01-01T00:00:00Z")) == branch_ts
        assert bean_progress.earliest_of(None, None) is None

    def test_row_columns_and_runner_in_notes(self, tmp_path: Path) -> None:
        beans = bean_progress.scan_beans(tmp_path / "none")
        intents = [bean_progress.IntentMapping(tmp_path / "i.json", "foo", ["0100"], "foo")]
        wt = _wt(
            tmp_path,
            "flow-foo",
            "foo",
            stage_started=parse("2026-11-23T11:48:00Z"),
            flow_started=parse("2026-11-21T09:00:00Z"),
        )
        rows = bean_progress.build_in_flight_rows(beans, intents, [wt], [], {}, now=NOW)
        assert len(rows) == 1
        assert rows[0].time_in_stage == "12m"
        assert rows[0].total_time == "2d3h"
        md = bean_progress.render_markdown_table(rows)
        header = md.splitlines()[0]
        assert header == "| Bean # | Target | Title | Agent | Model | Stage | In Stage | PR & CI | Total |"
        line = md.splitlines()[2]
        assert "| 12m |" in line and "| 2d3h |" in line
        assert "idle" in md.split("**Last activity and notes**")[1]
        wide_header = bean_progress.render_markdown_table(rows, wide=True).splitlines()[0]
        assert wide_header == (
            "| Bean # | Target | Title | Agent | Model | Stage | Time in Stage | PR & CI | Total Time "
            "| Last Activity | Notes |"
        )
        wt2 = _wt(tmp_path, "flow-bar", "bar")
        assert bean_progress.build_in_flight_rows(beans, [], [wt2], [], {}, now=NOW)[0].time_in_stage == "—"

    def test_scan_worktrees_reads_real_checkpoint(self, tmp_path: Path) -> None:
        root = tmp_path / "apps" / "holon-agentic-coder"
        wt = root / "flow-parent"
        (wt / ".holon" / "flow").mkdir(parents=True)
        (wt / "holon-knowledge" / "ledger").mkdir(parents=True)
        (wt / "holon-knowledge" / "ledger" / "intents.jsonl").write_text(
            json.dumps({"branch": "I-1795388456-parent/_", "created_at": "2026-11-22T23:00:00Z"}) + "\n"
        )
        (wt / ".holon" / "flow" / "checkpoint-child.json").write_text(
            json.dumps(
                {
                    "intent_slug": "child",
                    "current_stage": "review",
                    "completed_stages": ["intent", "plan", "execute"],
                    "timestamp": "2026-11-23T03:19:33.661Z",
                    "context": {
                        "intent_branch": "I-1795388456-parent/P-1--1-child/_",
                        "stage_results": {"review": {"status": "failed", "start_time": "2026-11-23T03:00:47Z"}},
                    },
                }
            )
        )
        repo = bean_progress.RepoTarget("HAC", root, True)
        (flow,) = bean_progress.scan_worktrees([repo])
        assert flow.slug == "parent"
        assert flow.stage_started == parse("2026-11-23T03:00:47Z")
        assert flow.flow_started == parse("2026-11-22T23:00:00Z")


def parse(text: str) -> datetime:
    parsed = bean_progress.parse_iso(text)
    assert parsed is not None
    return parsed


class TestMappingFixes:
    def _beans(self, tmp_path: Path, nums: list[str]) -> dict:
        beans_dir = tmp_path / ".beans"
        beans_dir.mkdir()
        for n in nums:
            _make_bean(beans_dir, n, f"b{n}", f"title: Bean {n}\nstatus: in-progress\n")
        return bean_progress.scan_beans(beans_dir)

    def test_child_pr_maps_to_parent_bean_only(self, tmp_path: Path) -> None:
        beans = self._beans(tmp_path, ["0174", "0191", "0198"])
        intents = [
            bean_progress.IntentMapping(tmp_path / "a.json", "github-adapter-pr-ci-review", ["0191"], "x"),
            bean_progress.IntentMapping(tmp_path / "b.json", "document-env", ["0174"], "document-env"),
            bean_progress.IntentMapping(tmp_path / "c.json", "runner-spec", ["0198"], "runner-spec"),
        ]
        child_head = "I-1795401745-github-adapter-pr-ci-review/P-1795397463-CLA--2-add-the-repository-scoped/E-1/_"
        wts = [
            # checkpoint-derived slug is already the root slug (child branch names the parent)
            _wt(
                tmp_path, "flow-github-adapter-pr-ci-review", "github-adapter-pr-ci-review", execution_branch=child_head
            ),
            _wt(tmp_path, "flow-document-env", "document-env"),
            _wt(tmp_path, "flow-runner-spec", "runner-spec"),
        ]
        rows = bean_progress.build_in_flight_rows(beans, intents, wts, [_pr(245, child_head)], {}, now=NOW)
        by_bean = {r.bean_nums[0]: r for r in rows}
        assert "#245" in by_bean["0191"].pr_ci or "u/245" in by_bean["0191"].pr_ci
        assert by_bean["0174"].pr_ci == "—"
        assert by_bean["0198"].pr_ci == "—"
        assert by_bean["0191"].stage != "Not started"
        assert len(rows) == 3

    def test_timestamp_digits_do_not_match_bean_number(self) -> None:
        pr = _pr(9, "I-1795401745-other/_")
        assert bean_progress._match_pr_for_unit(None, None, ["0174"], [pr]) is None
        pr2 = _pr(10, "I-5-x/bean-0174/_")
        assert bean_progress._match_pr_for_unit(None, None, ["0174"], [pr2]) is pr2

    def test_duplicate_attempts_merge_per_bean(self, tmp_path: Path) -> None:
        beans = self._beans(tmp_path, ["0175"])
        intents = [
            bean_progress.IntentMapping(tmp_path / "1.json", "scopes", ["0175"], "scopes"),
            bean_progress.IntentMapping(tmp_path / "2.json", "scopes-v2", ["0175"], "scopes-v2"),
        ]
        wts = [
            _wt(tmp_path, "flow-scopes", "scopes", current_stage="execute"),
            _wt(tmp_path, "flow-scopes-v2", "scopes-v2", current_stage="review"),
        ]
        live = {
            str(wts[1].path): bean_progress.LiveFlowTree(
                1,
                "01:00:00",
                "running",
                "Claude Code",
                str(wts[1].path),
                "scopes-v2",
                [],
                None,
                "claude-opus-5-5",
                "review-loop",
                False,
                1,
            )
        }
        rows = bean_progress.build_in_flight_rows(beans, intents, wts, [], live, now=NOW)
        assert len(rows) == 1
        assert rows[0].stage.startswith("Stage 4")
        assert "live · 1h00m (PID 1, Claude Code)" in rows[0].notes_cell()
        assert rows[0].model == "claude-opus-5-5"
        assert "stale attempt flow-scopes" in rows[0].notes_cell()

    def test_untracked_flow_gets_bean_from_intent_file_slug(self, tmp_path: Path) -> None:
        beans = self._beans(tmp_path, ["0175"])
        # json slug lacks the -v2 suffix that the file/branch slug carries
        intents = [bean_progress.IntentMapping(tmp_path / "i.json", "scopes", ["0175"], "scopes-v2")]
        wts = [_wt(tmp_path, "flow-scopes-v2", "scopes-v2")]
        (row,) = bean_progress.build_in_flight_rows(beans, intents, wts, [], {}, now=NOW)
        assert row.bean_nums == ["0175"]
        # PR-only row for a v2 branch also resolves
        (row2,) = bean_progress.build_in_flight_rows(
            beans, intents, [], [_pr(5, "I-100-scopes-v2/P-1/E-1/_")], {}, now=NOW
        )
        assert row2.bean_nums == ["0175"]
        assert row2.total_time != "—"


class TestBlockedStage:
    """The Stage cell names what blocks a flow at Stage 3 admission."""

    def _run(self, tmp_path: Path, blocked_by: list, prs=None, live=None, pr_state=None, intents=None):
        beans_dir = tmp_path / ".beans"
        beans_dir.mkdir(exist_ok=True)
        for n in ("0376", "0400", "0401"):
            _make_bean(beans_dir, n, f"b{n}", f"title: Bean {n}\nstatus: in-progress\n")
        beans = bean_progress.scan_beans(beans_dir)
        intents = [
            bean_progress.IntentMapping(tmp_path / "a.json", "resolve-conflicts-in-flow", ["0376"], "x"),
            bean_progress.IntentMapping(tmp_path / "b.json", "blocked-flow", ["0400"], "blocked-flow"),
            bean_progress.IntentMapping(tmp_path / "c.json", "other-flow", ["0401"], "other-flow"),
        ]
        wt = _wt(
            tmp_path,
            "flow-blocked-flow",
            "blocked-flow",
            admission={"state": "blocked", "blocked_by": blocked_by},
        )
        rows = bean_progress.build_in_flight_rows(
            beans, intents, [wt], prs or [], live or {}, now=NOW, pr_state=pr_state
        )
        return next(r for r in rows if r.bean_nums == ["0400"])

    @staticmethod
    def _local(slug: str, worktree: Path, files=("calibrate.py",)) -> dict:
        return {
            "kind": "local_flow",
            "number": None,
            "plan_branch": f"I-1795425253-{slug}/P-1795425271-CLA-CO5.5/_",
            "worktree": str(worktree),
            "files": list(files),
        }

    def test_pull_request_blocker(self, tmp_path: Path) -> None:
        row = self._run(tmp_path, [{"kind": "pull_request", "number": 275, "files": ["a.py"]}])
        assert row.stage == "Stage 3 (Blocked: #275)"
        assert row.blockers[0].kind == "pull_request"
        assert row.blockers[0].pr == 275

    def test_local_flow_with_open_pr(self, tmp_path: Path) -> None:
        wt_dir = tmp_path / "flow-resolve-conflicts-in-flow"
        wt_dir.mkdir()
        prs = [_pr(281, "I-1795425253-resolve-conflicts-in-flow/P-1/E-1/_")]
        row = self._run(tmp_path, [self._local("resolve-conflicts-in-flow", wt_dir)], prs=prs)
        assert row.stage == "Stage 3 (Blocked: #281 (bean 0376))"
        assert row.blockers[0].bean == "0376"
        assert row.blockers[0].pr == 281

    def test_local_flow_without_pr(self, tmp_path: Path) -> None:
        wt_dir = tmp_path / "flow-resolve-conflicts-in-flow"
        wt_dir.mkdir()
        row = self._run(tmp_path, [self._local("resolve-conflicts-in-flow", wt_dir)])
        assert row.stage == "Stage 3 (Blocked: bean 0376, no PR yet)"
        assert "overlap" not in row.stage

    def test_local_flow_without_bean_and_slug_from_worktree(self, tmp_path: Path) -> None:
        wt_dir = tmp_path / "flow-mystery"
        wt_dir.mkdir()
        entry = {"kind": "local_flow", "number": None, "worktree": str(wt_dir), "files": []}
        row = self._run(tmp_path, [entry])
        assert row.stage == "Stage 3 (Blocked: flow mystery, no PR yet)"

    def test_duplicate_blocker_shown_once(self, tmp_path: Path) -> None:
        wt_dir = tmp_path / "flow-resolve-conflicts-in-flow"
        wt_dir.mkdir()
        entry = self._local("resolve-conflicts-in-flow", wt_dir)
        row = self._run(tmp_path, [entry, dict(entry, files=["flow.py"])])
        assert row.stage == "Stage 3 (Blocked: bean 0376, no PR yet)"
        assert len(row.blockers) == 1
        assert row.blockers[0].files == ["calibrate.py", "flow.py"]

    def test_two_distinct_blockers(self, tmp_path: Path) -> None:
        wt_dir = tmp_path / "flow-resolve-conflicts-in-flow"
        wt_dir.mkdir()
        row = self._run(
            tmp_path,
            [{"kind": "pull_request", "number": 275}, self._local("resolve-conflicts-in-flow", wt_dir)],
        )
        assert row.stage == "Stage 3 (Blocked: #275, bean 0376, no PR yet)"
        assert row.stage_compact == "Stage 3 (Blocked: #275 +1 more)"
        assert "Blocked by #275, bean 0376, no PR yet" in row.notes_cell()
        md = bean_progress.render_markdown_table([row])
        table, _, details = md.partition("**Last activity and notes**")
        assert "+1 more" in table
        assert "bean 0376, no PR yet" not in table
        assert "bean 0376, no PR yet" in details

    def test_short_cell_is_not_truncated(self, tmp_path: Path) -> None:
        row = self._run(tmp_path, [{"number": 1}, {"number": 2}])
        assert row.stage == "Stage 3 (Blocked: #1, #2)"
        assert row.stage_compact == row.stage

    def test_blocker_gone_not_resumed(self, tmp_path: Path) -> None:
        gone_dir = tmp_path / "flow-removed"
        states = {275: "MERGED"}
        row = self._run(
            tmp_path,
            [{"kind": "pull_request", "number": 275}, self._local("removed", gone_dir)],
            pr_state=lambda _repo, n: states.get(n),
        )
        assert row.stage.endswith("; blocker gone, not resumed)")
        assert row.stage.startswith("Stage 3 (Blocked: #275, flow removed, no PR yet")
        assert all(b.gone for b in row.blockers)

    def test_not_gone_when_one_blocker_remains_or_unknown(self, tmp_path: Path) -> None:
        live_dir = tmp_path / "flow-resolve-conflicts-in-flow"
        live_dir.mkdir()
        row = self._run(
            tmp_path,
            [{"kind": "pull_request", "number": 275}, self._local("resolve-conflicts-in-flow", live_dir)],
            pr_state=lambda _repo, _n: "MERGED",
        )
        assert "blocker gone" not in row.stage
        assert [b.gone for b in row.blockers] == [True, False]
        # State unknown (no gh): never claimed as gone.
        row = self._run(tmp_path, [{"kind": "pull_request", "number": 275}])
        assert "blocker gone" not in row.stage
        # An open pull request is not gone even if the lookup says merged.
        row = self._run(
            tmp_path,
            [{"kind": "pull_request", "number": 275}],
            prs=[_pr(275, "I-5-x/_")],
            pr_state=lambda _repo, _n: "MERGED",
        )
        assert "blocker gone" not in row.stage

    def test_live_runner_suppresses_gone(self, tmp_path: Path) -> None:
        wt_dir = tmp_path / "flow-blocked-flow"
        live = {
            str(wt_dir): bean_progress.LiveFlowTree(
                9, "01:00", "polling", "terminal", str(wt_dir), "blocked-flow", [], None, None, None, False, None
            )
        }
        row = self._run(
            tmp_path,
            [{"kind": "pull_request", "number": 275}],
            live=live,
            pr_state=lambda _repo, _n: "MERGED",
        )
        assert row.stage == "Stage 3 (Blocked: #275)"

    def test_empty_or_unreadable_list_keeps_overlap(self, tmp_path: Path) -> None:
        assert self._run(tmp_path, []).stage == "Stage 3 (Blocked: overlap)"
        assert self._run(tmp_path, "garbage").stage == "Stage 3 (Blocked: overlap)"  # type: ignore[arg-type]
        assert self._run(tmp_path, [None, "x"]).blockers == []

    def test_json_blocked_by_field(self, tmp_path: Path) -> None:
        wt_dir = tmp_path / "flow-resolve-conflicts-in-flow"
        wt_dir.mkdir()
        row = self._run(tmp_path, [self._local("resolve-conflicts-in-flow", wt_dir)])
        assert row.as_dict()["blocked_by"] == [
            {
                "kind": "local_flow",
                "pr": None,
                "bean": "0376",
                "slug": "resolve-conflicts-in-flow",
                "files": ["calibrate.py"],
                "gone": False,
            }
        ]
        other = bean_progress.InFlightRow(["0001"], "HAC", "t", "Not started", "—", "idle", "—", 3)
        assert other.as_dict()["blocked_by"] == []
