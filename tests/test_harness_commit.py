import json
import re
import subprocess
import sys
import threading
from datetime import UTC, datetime
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent.parent / ".agents" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import harness_commit  # noqa: E402
import harness_lock  # noqa: E402
import new_bean  # noqa: E402
import staged_validation  # noqa: E402

LEDGER = ".agents/ledger/coordinator-failures.jsonl"
PAST = "2026-11-26T10:00:00Z"


def _git(repo, *arguments):
    done = subprocess.run(["git", *arguments], cwd=repo, capture_output=True, text=True, check=True)
    return done.stdout.strip()


def _bean_text(number, created=PAST, status="todo"):
    return (
        f'---\n# holon-agentic-coder-ref-metadata-{number:04d}\ntitle: "Sample"\nstatus: {status}\n'
        f"created_at: {created}\nupdated_at: {created}\n---\n"
    )


def _ledger_row(number, category="brief", created=PAST):
    return json.dumps(
        {
            "id": f"CF-{number:04d}",
            "created_at": created,
            "session_date": "2026-11-26",
            "category": category,
            "failure": "f",
            "my_part": "m",
            "cost": "c",
            "rule": "r",
            "refs": [],
        }
    )


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "docs/harness-test")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")
    (root / ".beans").mkdir()
    (root / ".agents" / "ledger").mkdir(parents=True)
    (root / ".beans" / f"{new_bean.PREFIX}-0001--first.md").write_text(_bean_text(1))
    (root / LEDGER).write_text(_ledger_row(1) + "\n")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "seed")
    return root


def _no_format(repo, paths):
    return None


def _commit(repo, message, paths):
    return harness_commit.commit_and_push(repo, message, paths, push=False, formatter=_no_format, index_wait=0.3)


def test_commits_named_paths_and_leaves_unnamed_changes_alone(repo):
    (repo / "a.txt").write_text("a\n")
    (repo / "other.txt").write_text("other\n")
    sha = _commit(repo, "add a", ["a.txt"])
    assert _git(repo, "rev-parse", "--short", "HEAD") == sha
    assert _git(repo, "show", "--name-only", "--format=", "HEAD") == "a.txt"
    assert "other.txt" in _git(repo, "status", "--porcelain")
    assert _git(repo, "diff", "--cached", "--name-only") == ""


def test_refuses_empty_path_list_and_directories(repo):
    with pytest.raises(harness_commit.HarnessCommitError):
        _commit(repo, "nothing", [])
    with pytest.raises(harness_commit.HarnessCommitError):
        _commit(repo, "dir", [".beans"])


def test_refuses_main_branch(repo):
    _git(repo, "checkout", "-q", "-b", "main")
    (repo / "a.txt").write_text("a\n")
    with pytest.raises(harness_commit.HarnessCommitError, match="refusing"):
        _commit(repo, "on main", ["a.txt"])


def test_waits_then_fails_when_another_agent_left_the_index_dirty(repo):
    (repo / "theirs.txt").write_text("t\n")
    _git(repo, "add", "theirs.txt")
    (repo / "mine.txt").write_text("m\n")
    with pytest.raises(harness_commit.HarnessCommitError, match="index not empty"):
        _commit(repo, "mine", ["mine.txt"])
    assert _git(repo, "diff", "--cached", "--name-only") == "theirs.txt"


def test_bad_staged_ledger_row_is_refused_and_unstaged(repo):
    (repo / LEDGER).write_text(_ledger_row(1) + "\n" + _ledger_row(2, category="no-such-category") + "\n")
    with pytest.raises(harness_commit.HarnessCommitError, match="bad category"):
        _commit(repo, "bad row", [LEDGER])
    assert _git(repo, "diff", "--cached", "--name-only") == ""
    assert _git(repo, "rev-list", "--count", "HEAD") == "1"


def test_validation_reads_the_staged_blob_not_the_working_tree(repo):
    (repo / LEDGER).write_text(_ledger_row(1) + "\n" + _ledger_row(2, category="no-such-category") + "\n")
    _git(repo, "add", LEDGER)
    (repo / LEDGER).write_text(_ledger_row(1) + "\n" + _ledger_row(2) + "\n")
    problems = staged_validation.staged_problems(repo)
    assert any("bad category" in problem for problem in problems)


def test_clean_staged_state_passes_validation(repo):
    (repo / LEDGER).write_text(_ledger_row(1) + "\n" + _ledger_row(2) + "\n")
    _git(repo, "add", LEDGER)
    assert staged_validation.staged_problems(repo) == []


def test_another_agents_bad_unstaged_bean_does_not_block_a_commit(repo):
    (repo / ".beans" / f"{new_bean.PREFIX}-0002--theirs.md").write_text(_bean_text(2, created="2999-01-01T00:00:00Z"))
    (repo / "a.txt").write_text("a\n")
    _commit(repo, "add a", ["a.txt"])
    assert _git(repo, "show", "--name-only", "--format=", "HEAD") == "a.txt"


def test_staged_future_bean_timestamp_is_refused(repo):
    path = repo / ".beans" / f"{new_bean.PREFIX}-0002--future.md"
    path.write_text(_bean_text(2, created="2999-01-01T00:00:00Z"))
    with pytest.raises(harness_commit.HarnessCommitError, match="future"):
        _commit(repo, "future bean", [str(path)])


def test_lock_is_released_after_a_failed_commit(repo):
    with pytest.raises(harness_commit.HarnessCommitError):
        _commit(repo, "nothing", ["missing.txt"])
    with harness_lock.exclusive_harness_lock(repo, timeout=0.5):
        pass


def test_lock_serialises_holders(repo):
    with (
        harness_lock.exclusive_harness_lock(repo),
        pytest.raises(harness_lock.HarnessLockTimeout),
        harness_lock.exclusive_harness_lock(repo, timeout=0.3),
    ):
        pass


def test_concurrent_allocations_get_distinct_ids(repo):
    created = []
    guard = threading.Lock()

    def allocate(index):
        path = new_bean.create_bean(repo, f"Concurrent bean {index}")
        with guard:
            created.append(path)

    threads = [threading.Thread(target=allocate, args=(index,)) for index in range(12)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    numbers = sorted(int(re.search(r"-(\d{4})--", path.name).group(1)) for path in created)
    assert numbers == list(range(2, 14))


def test_concurrent_allocations_across_processes_get_distinct_ids(repo):
    script = SCRIPT_DIR / "new_bean.py"
    processes = [
        subprocess.Popen(
            [sys.executable, str(script), f"Process bean {index}"], cwd=repo, stdout=subprocess.PIPE, text=True
        )
        for index in range(6)
    ]
    paths = [Path(process.communicate()[0].strip()) for process in processes]
    assert all(process.returncode == 0 for process in processes)
    assert len({path.name.split("--")[0] for path in paths}) == 6


def test_new_bean_skeleton_is_valid_and_clock_stamped(repo):
    before = datetime.now(UTC).replace(microsecond=0)
    path = new_bean.create_bean(repo, "A Fresh Bean!", bean_type="bug", priority="high", tags=["harness"])
    assert path.name == f"{new_bean.PREFIX}-0002--a-fresh-bean.md"
    text = path.read_text()
    stamp = next(line.split(": ")[1] for line in text.splitlines() if line.startswith("created_at"))
    assert before <= datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    _git(repo, "add", str(path))
    assert staged_validation.staged_problems(repo) == []
