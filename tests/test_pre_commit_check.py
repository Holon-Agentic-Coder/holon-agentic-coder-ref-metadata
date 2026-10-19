"""Unit tests for pre_commit_check.py (Bean 0110)."""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent / ".agents" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import pre_commit_check  # noqa: E402


class TestPreCommitCheck:
    """Verify credential leakage and ephemeral scratch path detection."""

    def test_disallowed_scratch_paths(self):
        assert pre_commit_check.is_disallowed_scratch_path("tmp/test_write.txt") is not None
        assert pre_commit_check.is_disallowed_scratch_path("debug.tmp") is not None
        assert pre_commit_check.is_disallowed_scratch_path("run.log") is not None
        assert pre_commit_check.is_disallowed_scratch_path(".index/action_index.db") is not None
        assert pre_commit_check.is_disallowed_scratch_path("holon-knowledge/.index/action_index.db") is not None

        assert pre_commit_check.is_disallowed_scratch_path("src/main.py") is None
        assert pre_commit_check.is_disallowed_scratch_path("README.md") is None

    def test_scan_file_for_secrets_detects_credentials(self, tmp_path):
        secret_file = tmp_path / "leaked.py"
        # Construct test tokens dynamically so the test file itself doesn't trigger static scanners
        google_key = "AIza" + "SyB1234567890abcdefghijklmnopqrstuv"
        gh_pat = "ghp_" + "1234567890abcdefghijklmnopqrstuvwxyzABCD"
        openai_key = "sk-proj-" + "1234567890abcdefghijklmnopqrstuvwx"
        secret_file.write_text(f"GOOGLE_KEY = '{google_key}'\nGITHUB_TOKEN = '{gh_pat}'\nOPENAI_KEY = '{openai_key}'\n")

        findings = pre_commit_check.scan_file_for_secrets(secret_file, display_path="leaked.py")
        assert len(findings) == 3
        assert any("Google AI API Key" in f and "leaked.py:1" in f for f in findings)
        assert any("GitHub Personal Access Token" in f and "leaked.py:2" in f for f in findings)
        assert any("OpenAI API Key" in f and "leaked.py:3" in f for f in findings)

    def test_clean_files_pass(self, tmp_path):
        clean_file = tmp_path / "clean.py"
        clean_file.write_text("def add(a: int, b: int) -> int:\n    return a + b\n")

        exit_code = pre_commit_check.main(["--repo-root", str(tmp_path), "--files", "clean.py"])
        assert exit_code == 0

    def test_cli_fails_on_scratch_or_secret(self, tmp_path):
        scratch_dir = tmp_path / "tmp"
        scratch_dir.mkdir()
        scratch = scratch_dir / "test.txt"
        scratch.write_text("hello\n")

        exit_code = pre_commit_check.main(["--repo-root", str(tmp_path), "--files", "tmp/test.txt"])
        assert exit_code == 1
