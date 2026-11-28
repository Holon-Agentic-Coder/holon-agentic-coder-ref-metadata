import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent.parent / ".agents" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import git_guard  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
WRAPPER = REPO_ROOT / ".agents" / "bin" / "git"
HARNESS = "/work/harness"
MAIN_CODER = "/work/harness/apps/holon-agentic-coder/main"
MAIN_COHERENCE = "/work/harness/apps/holon-coherence/main"
FLOW = "/work/harness/apps/holon-agentic-coder/flow-some-slug"

BLOCKED = [
    "git stash",
    "git stash pop",
    "git -C apps/x stash list",
    "cd /tmp && git stash push -m wip",
    "git commit --no-verify -m msg",
    "git push --no-verify",
    "git commit -n -m msg",
    "git add -A",
    "git add --all",
    "git add .",
    "git add -- .",
    "git add a.md && git add .",
    "git push --force origin branch",
    "git push -f origin branch",
    "git push --force-with-lease origin branch",
    "git push --force-with-lease=branch origin branch",
    "git push origin +branch",
    "git push -fu origin branch",
    "bash -c 'git stash'",
    "echo ok; git stash",
    "echo $(git stash)",
    "GIT_EDITOR=true git stash",
    "git -C /work/harness/apps/holon-agentic-coder/main commit -m x",
    "git -C /work/harness/apps/holon-coherence/main checkout -b other",
    "git -C apps/holon-agentic-coder/main switch other",
    "git -C apps/holon-agentic-coder/main reset --hard origin/main",
    "git -C apps/holon-coherence/main merge origin/main",
    "git -C apps/holon-coherence/main rebase origin/main",
    "git -C apps/holon-agentic-coder/main add file.py",
    "git -C apps/holon-agentic-coder/main pull origin main",
    "cd apps/holon-agentic-coder/main && git commit -m x",
]

ALLOWED = [
    "git status",
    "git diff --stat",
    "git add .agents/scripts/git_guard.py tests/test_git_guard.py",
    "git add -u",
    "git add apps/foo/.",
    "git commit -m 'fix: block git stash and --no-verify'",
    "git commit -m \"$(cat <<'EOF'\nfeat: x\n\nnever git stash, never git add . or --no-verify\nEOF\n)\"",
    "echo 'git stash is banned'",
    "git push origin branch",
    "git push -u origin branch",
    "git fetch origin",
    "git stash-list-is-not-a-command-but-a-path",
    "git -C /work/harness/apps/holon-agentic-coder/flow-x commit -m x",
    "git -C /work/harness/apps/holon-agentic-coder/flow-x push origin HEAD",
    "git -C /work/harness/apps/holon-agentic-coder/flow-x merge origin/main",
    "git -C /work/harness/apps/holon-agentic-coder/flow-x fetch origin",
    "git -C apps/holon-agentic-coder/main worktree add ../flow-new -b flow-new origin/main",
    "git -C apps/holon-agentic-coder/main worktree remove ../flow-old",
    "git -C apps/holon-agentic-coder/main fetch origin",
    "git -C apps/holon-agentic-coder/main merge --ff-only origin/main",
    "git -C apps/holon-coherence/main pull --ff-only origin main",
    "git -C apps/holon-agentic-coder/main rev-parse HEAD",
    "git -C apps/holon-agentic-coder/main status --porcelain",
    "git -C apps/holon-agentic-coder/main log --oneline",
    "git pull --rebase origin docs/harness-20261127",
    "git rebase origin/main",
    "cd apps/holon-agentic-coder/flow-x && git commit -m x",
]


@pytest.mark.parametrize("command", BLOCKED)
def test_blocked_forms(command):
    assert git_guard.check_command(command, HARNESS) is not None


@pytest.mark.parametrize("command", ALLOWED)
def test_allowed_forms(command):
    assert git_guard.check_command(command, HARNESS) is None


def test_cwd_inside_main_worktree_blocks_mutation():
    assert git_guard.check_command("git commit -m x", MAIN_CODER) is not None
    assert git_guard.check_command("git checkout other", MAIN_COHERENCE + "/src") is not None
    assert git_guard.check_command("git pull --ff-only origin main", MAIN_CODER) is None
    assert git_guard.check_command("git merge --ff-only origin/main", MAIN_COHERENCE) is None
    assert git_guard.check_command("git status", MAIN_CODER) is None


def test_cd_out_of_main_worktree_allows_mutation():
    assert git_guard.check_command("cd /work/harness && git commit -m x", MAIN_CODER) is None


def test_rebase_blocked_in_flow_worktree_by_path():
    assert git_guard.check_command("git rebase origin/main", FLOW) is not None
    assert git_guard.check_command("git pull --rebase", FLOW) is not None
    assert git_guard.check_command("git -C " + FLOW + " rebase origin/main", HARNESS) is not None
    assert git_guard.check_command("git merge origin/main", FLOW) is None


@pytest.fixture
def repository(tmp_path):
    def create(branch):
        path = tmp_path / branch.replace("/", "_")
        path.mkdir()
        subprocess.run(["git", "init", "-q", "-b", branch, str(path)], check=True)
        return str(path)

    return create


@pytest.mark.parametrize("branch", ["I-1795-slug/P-1795-X/_", "I-1795-slug/_", "flow-slug"])
def test_rebase_blocked_on_flow_branch_by_name(repository, branch):
    path = repository(branch)
    assert git_guard.check_command("git rebase origin/main", path) is not None


def test_rebase_allowed_on_harness_branch(repository):
    path = repository("docs/harness-20261127")
    assert git_guard.check_command("git rebase origin/main", path) is None


def run_hook(command, cwd, environment=None):
    payload = {"tool_name": "Bash", "tool_input": {"command": command}, "cwd": cwd}
    return subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "git_guard.py"), "--hook"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env={**os.environ, **(environment or {})},
        check=False,
    )


def test_hook_exits_two_with_reason_on_violation():
    result = run_hook("git stash", HARNESS)
    assert result.returncode == 2
    assert "git stash" in result.stderr


def test_hook_exits_zero_on_clean_command_and_other_tools():
    assert run_hook("git status", HARNESS).returncode == 0
    other = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "git_guard.py"), "--hook"],
        input=json.dumps({"tool_name": "Read", "tool_input": {"command": "git stash"}}),
        capture_output=True,
        text=True,
        check=False,
    )
    assert other.returncode == 0


def test_hook_bypass_is_environment_only():
    assert run_hook("git stash", HARNESS, {"HOLON_GIT_GUARD_BYPASS": "1"}).returncode == 0


def test_project_settings_register_the_hook():
    settings = json.loads((REPO_ROOT / ".claude" / "settings.json").read_text())
    entries = settings["hooks"]["PreToolUse"]
    commands = [hook["command"] for entry in entries if entry["matcher"] == "Bash" for hook in entry["hooks"]]
    assert any("git_guard.py" in command and command.endswith("--hook") for command in commands)


@pytest.fixture
def wrapper_repository(tmp_path):
    path = tmp_path / "work"
    path.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "scratch", str(path)], check=True)
    return path


def run_wrapper(arguments, cwd):
    environment = {key: value for key, value in os.environ.items() if key != "HOLON_GIT_GUARD_BYPASS"}
    environment["PATH"] = f"{WRAPPER.parent}:{environment['PATH']}"
    return subprocess.run(
        [str(WRAPPER), *arguments], cwd=cwd, capture_output=True, text=True, env=environment, check=False
    )


@pytest.mark.parametrize(
    "arguments",
    [["stash"], ["add", "-A"], ["add", "."], ["commit", "--no-verify", "-m", "x"], ["push", "--force"], ["push", "-f"]],
)
def test_wrapper_refuses_forbidden_forms(wrapper_repository, arguments):
    result = run_wrapper(arguments, wrapper_repository)
    assert result.returncode == 1
    assert "git-guard blocked" in result.stderr


def test_wrapper_passes_allowed_forms_to_real_git(wrapper_repository):
    (wrapper_repository / "a.txt").write_text("a")
    assert run_wrapper(["add", "a.txt"], wrapper_repository).returncode == 0
    status = run_wrapper(["status", "--porcelain"], wrapper_repository)
    assert status.returncode == 0
    assert "A  a.txt" in status.stdout


def test_wrapper_refuses_mutation_in_main_worktree(wrapper_repository):
    result = run_wrapper(["-C", "/work/harness/apps/holon-agentic-coder/main", "commit", "-m", "x"], wrapper_repository)
    assert result.returncode == 1
