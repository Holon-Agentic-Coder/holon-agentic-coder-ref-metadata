import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent.parent / ".agents" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import check_main_worktrees  # noqa: E402

IDENTITY = ["-c", "user.name=t", "-c", "user.email=t@example.com"]


def git(path, *arguments):
    subprocess.run(["git", "-C", str(path), *IDENTITY, *arguments], check=True, capture_output=True)


@pytest.fixture
def worktree(tmp_path):
    origin = tmp_path / "origin"
    origin.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(origin)], check=True)
    (origin / "a.txt").write_text("a")
    git(origin, "add", "a.txt")
    git(origin, "commit", "-q", "-m", "first")
    clone = tmp_path / "root" / "apps" / "holon-agentic-coder" / "main"
    subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True)
    return clone


def violations(worktree):
    return check_main_worktrees.check_worktree(worktree)


def test_pristine_worktree_passes(worktree):
    assert violations(worktree) == []


def test_untracked_todo_directory_is_allowed(worktree):
    (worktree / "todo").mkdir()
    (worktree / "todo" / "note.md").write_text("n")
    assert violations(worktree) == []


def test_behind_origin_is_allowed(worktree):
    origin = worktree.parents[3] / "origin"
    (origin / "b.txt").write_text("b")
    git(origin, "add", "b.txt")
    git(origin, "commit", "-q", "-m", "second")
    git(worktree, "fetch", "-q", "origin")
    assert violations(worktree) == []


def test_other_branch_is_reported(worktree):
    git(worktree, "checkout", "-q", "-b", "flow-slug")
    assert any("not main" in violation for violation in violations(worktree))


def test_detached_head_is_reported(worktree):
    git(worktree, "checkout", "-q", "--detach")
    assert any("not main" in violation for violation in violations(worktree))


def test_tracked_modification_is_reported(worktree):
    (worktree / "a.txt").write_text("changed")
    assert any("not clean" in violation for violation in violations(worktree))


def test_other_untracked_file_is_reported(worktree):
    (worktree / "scratch.txt").write_text("s")
    assert any("scratch.txt" in violation for violation in violations(worktree))


def test_local_commit_ahead_of_origin_is_reported(worktree):
    (worktree / "b.txt").write_text("b")
    git(worktree, "add", "b.txt")
    git(worktree, "commit", "-q", "-m", "local only")
    assert any("origin/main" in violation for violation in violations(worktree))


def test_missing_worktree_is_reported(tmp_path):
    assert violations(tmp_path / "absent") == [f"{tmp_path / 'absent'}: missing"]


def test_main_exit_code_reflects_state(worktree, tmp_path):
    root = worktree.parents[2]
    coherence = root / "apps" / "holon-coherence" / "main"
    subprocess.run(
        ["git", "clone", "-q", str(worktree.parent.parent.parent.parent / "origin"), str(coherence)], check=True
    )
    assert check_main_worktrees.main([str(root)]) == 0
    (worktree / "a.txt").write_text("changed")
    assert check_main_worktrees.main([str(root)]) == 1
