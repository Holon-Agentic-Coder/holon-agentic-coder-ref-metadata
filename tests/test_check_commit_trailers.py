import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent.parent / ".agents" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import check_commit_trailers  # noqa: E402

ATTRIBUTION_MESSAGES = [
    "feat: x\n\nCo-Authored-By: Someone <someone@example.com>",
    "feat: x\n\nco-authored-by: Someone <someone@example.com>",
    "feat: x\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>",
    "feat: x\n\nCo-developed-by: Someone <someone@example.com>",
    "feat: x\n\nGenerated-by: tool",
    "feat: x\n\nAssisted-by: tool",
    "feat: x\n\nGenerated with [Claude Code](https://claude.com/claude-code)",
]

CLEAN_MESSAGES = [
    "feat: x",
    "docs(beans): bean 0567 no co-author trailer hook",
    "fix: reject Co-Authored-By trailers in commit messages",
    "feat: x\n\nSigned-off-by: Someone <someone@example.com>",
    "feat: x\n\n# Co-Authored-By: comment line git strips",
]


@pytest.mark.parametrize("message", ATTRIBUTION_MESSAGES)
def test_attribution_trailers_detected(message):
    assert check_commit_trailers.find_attribution_lines(message)


@pytest.mark.parametrize("message", CLEAN_MESSAGES)
def test_clean_messages_pass(message):
    assert check_commit_trailers.find_attribution_lines(message) == []


def test_message_file_mode_exit_codes(tmp_path):
    bad = tmp_path / "bad"
    bad.write_text(ATTRIBUTION_MESSAGES[0])
    good = tmp_path / "good"
    good.write_text(CLEAN_MESSAGES[0])
    assert check_commit_trailers.main(["--message-file", str(bad)]) == 1
    assert check_commit_trailers.main(["--message-file", str(good)]) == 0


def commit(path, message):
    (path / "f.txt").write_text(message)
    subprocess.run(["git", "-C", str(path), "add", "f.txt"], check=True)
    subprocess.run(
        ["git", "-C", str(path), "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "-m", message],
        check=True,
    )


def test_range_mode_checks_only_the_range(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    commit(tmp_path, "old: x\n\nCo-Authored-By: Old <old@example.com>")
    commit(tmp_path, "new: clean")
    monkeypatch.chdir(tmp_path)
    assert check_commit_trailers.main(["--range", "HEAD~1..HEAD"]) == 0
    commit(tmp_path, "new: dirty\n\nCo-Authored-By: New <new@example.com>")
    assert check_commit_trailers.main(["--range", "HEAD~1..HEAD"]) == 1
    assert check_commit_trailers.main(["--range", "HEAD~2..HEAD"]) == 1


def test_installed_hook_rejects_a_commit_with_trailer(tmp_path):
    hooks = tmp_path / ".git" / "hooks"
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    scripts = tmp_path / ".agents" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "check_commit_trailers.py").write_text((SCRIPT_DIR / "check_commit_trailers.py").read_text())
    hook = hooks / "commit-msg"
    hook.write_text((SCRIPT_DIR.parent / "hooks" / "commit-msg").read_text())
    hook.chmod(0o755)
    (tmp_path / "f.txt").write_text("x")
    subprocess.run(["git", "-C", str(tmp_path), "add", "f.txt"], check=True)
    identity = ["-c", "user.name=t", "-c", "user.email=t@example.com"]
    rejected = subprocess.run(
        ["git", "-C", str(tmp_path), *identity, "commit", "-q", "-m", "x\n\nCo-Authored-By: A <a@example.com>"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert rejected.returncode != 0
    accepted = subprocess.run(
        ["git", "-C", str(tmp_path), *identity, "commit", "-q", "-m", "x"], capture_output=True, text=True, check=False
    )
    assert accepted.returncode == 0
