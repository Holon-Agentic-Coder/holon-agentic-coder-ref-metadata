"""Unit test suite for clean_workspace utility script."""

import sys
from pathlib import Path
from unittest.mock import patch

# Ensure clean_workspace script is importable
SCRIPT_DIR = Path(__file__).resolve().parent.parent / ".agents" / "skills" / "clean_workspace" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import clean_workspace  # noqa: E402


class TestHelperFunctions:
    """Test helper functions and utilities."""

    def test_run_cmd_success(self):
        code, stdout, stderr = clean_workspace.run_cmd(["echo", "hello"])
        assert code == 0
        assert stdout == "hello"
        assert stderr == ""

    def test_run_cmd_failure(self):
        code, _, stderr = clean_workspace.run_cmd(["non_existent_binary_12345"])
        assert code != 0
        assert len(stderr) > 0

    def test_format_rel(self, tmp_path):
        root = tmp_path / "repo"
        sub = root / "apps" / "proj"
        sub.mkdir(parents=True)

        assert clean_workspace.format_rel(sub, root) == "apps/proj"
        outside = tmp_path / "outside"
        assert clean_workspace.format_rel(outside, root) == str(outside)
        assert clean_workspace.format_rel(sub, None) == str(sub)

    @patch("clean_workspace.run_cmd")
    def test_is_git_clean(self, mock_run, tmp_path):
        mock_run.return_value = (0, "", "")
        assert clean_workspace.is_git_clean(tmp_path) is True

        mock_run.return_value = (0, " M file.txt", "")
        assert clean_workspace.is_git_clean(tmp_path) is False

        mock_run.return_value = (1, "", "error")
        assert clean_workspace.is_git_clean(tmp_path) is False

    @patch("clean_workspace.run_cmd")
    def test_get_pr_status(self, mock_run):
        mock_run.return_value = (0, "MERGED", "")
        status = clean_workspace.get_pr_status("org/repo", "feat/test")
        assert status == "MERGED"

        mock_run.return_value = (1, "", "not found")
        status = clean_workspace.get_pr_status("org/repo", "feat/unknown")
        assert status is None

    @patch("clean_workspace.run_cmd")
    def test_get_pr_status_by_number(self, mock_run):
        mock_run.return_value = (0, "OPEN", "")
        status = clean_workspace.get_pr_status_by_number("org/repo", "52")
        assert status == "OPEN"

        mock_run.return_value = (0, "MERGED", "")
        status = clean_workspace.get_pr_status_by_number("org/repo", "78")
        assert status == "MERGED"

    def test_is_permanent_subagent_file(self):
        # Permanent state files
        assert clean_workspace.is_permanent_subagent_file(".gitkeep") is True
        assert clean_workspace.is_permanent_subagent_file("coordination.json") is True
        assert clean_workspace.is_permanent_subagent_file("repo_pr52_coordination.json") is True
        assert clean_workspace.is_permanent_subagent_file("repo_pr52_state.json") is True
        assert clean_workspace.is_permanent_subagent_file("repo_pr52_loop_history.md") is True
        assert clean_workspace.is_permanent_subagent_file("repo_pr52_posted_review.md") is True
        assert clean_workspace.is_permanent_subagent_file("repo_pr52_consensus_review_iter_1_abc.md") is True

        # Ephemeral or intermediate review artifacts (not permanent)
        assert clean_workspace.is_permanent_subagent_file("repo_pr52_dry_run_review_iter_1_abc.md") is False
        assert clean_workspace.is_permanent_subagent_file("repo_pr52_reviewer_1_iter_1_abc.md") is False
        assert clean_workspace.is_permanent_subagent_file("repo_pr52_diff.txt") is False
        assert clean_workspace.is_permanent_subagent_file("repo_pr52_meta.json") is False


class TestSubagentCleaning:
    """Test .subagent artifact cleaning and active PR preservation."""

    def test_clean_subagent_files_preserves_active_and_cleans_merged(self, tmp_path):
        subagent_dir = tmp_path / ".subagent"
        subagent_dir.mkdir(parents=True)

        # Permanent files
        gitkeep = subagent_dir / ".gitkeep"
        gitkeep.touch()
        state_52 = subagent_dir / "holon-agentic-coder-ref-metadata_pr52_state.json"
        state_52.touch()
        coord_52 = subagent_dir / "holon-agentic-coder-ref-metadata_pr52_coordination.json"
        coord_52.touch()
        consensus_78 = subagent_dir / "holon-agentic-coder_pr78_consensus_review_iter_1_0aad2fc.md"
        consensus_78.touch()

        # Active PR 52 intermediate files (must be preserved)
        active_diff_52 = subagent_dir / "holon-agentic-coder-ref-metadata_pr52_diff.txt"
        active_diff_52.touch()
        active_review_52 = subagent_dir / "holon-agentic-coder-ref-metadata_pr52_dry_run_review_iter_1_1993502.md"
        active_review_52.touch()

        # Merged PR 78 intermediate files (should be purged)
        merged_reviewer_78 = subagent_dir / "holon-agentic-coder_pr78_reviewer_1_iter_1_0aad2fc.md"
        merged_reviewer_78.touch()
        merged_diff_78 = subagent_dir / "holon-agentic-coder_pr78_diff.txt"
        merged_diff_78.touch()

        # Unknown PR without pr pattern (should be preserved to be safe)
        scratch_note = subagent_dir / "scratch_notes.txt"
        scratch_note.touch()

        # Mock status function
        def mock_pr_status(gh_repo: str, pr_num: str):
            if pr_num == "52":
                return "OPEN"
            elif pr_num == "78":
                return "MERGED"
            return None

        # 1. Test Dry Run
        dry_purged = clean_workspace.clean_subagent_files(tmp_path, dry_run=True, pr_status_fn=mock_pr_status)
        # All files still exist on disk in dry run
        assert merged_reviewer_78.exists()
        assert merged_diff_78.exists()
        assert len(dry_purged) == 2
        assert any("holon-agentic-coder_pr78_reviewer_1_iter_1_0aad2fc.md" in p for p in dry_purged)
        assert any("holon-agentic-coder_pr78_diff.txt" in p for p in dry_purged)

        # 2. Test Execution
        purged = clean_workspace.clean_subagent_files(tmp_path, dry_run=False, pr_status_fn=mock_pr_status)
        assert len(purged) == 2
        # Merged PR 78 non-permanent files deleted
        assert not merged_reviewer_78.exists()
        assert not merged_diff_78.exists()

        # Permanent and active PR files preserved
        assert gitkeep.exists()
        assert state_52.exists()
        assert coord_52.exists()
        assert consensus_78.exists()
        assert active_diff_52.exists()
        assert active_review_52.exists()
        assert scratch_note.exists()

    def test_clean_subagent_files_archive_mode(self, tmp_path):
        subagent_dir = tmp_path / ".subagent"
        subagent_dir.mkdir(parents=True)

        # Permanent files for merged PR 78
        state_78 = subagent_dir / "holon-agentic-coder_pr78_state.json"
        state_78.touch()
        posted_78 = subagent_dir / "holon-agentic-coder_pr78_posted_review.md"
        posted_78.touch()
        consensus_78 = subagent_dir / "holon-agentic-coder_pr78_consensus_review_iter_1_0aad2fc.md"
        consensus_78.touch()

        # Intermediate files for merged PR 78 (should be relocated into holon-agentic-coder_pr78_archive/)
        iter_rev = subagent_dir / "holon-agentic-coder_pr78_ensemble_review_iter_1_reviewer_1_0aad2fc.md"
        iter_rev.write_text("reviewer 1 notes")
        diff_78 = subagent_dir / "holon-agentic-coder_pr78_diff.txt"
        diff_78.write_text("diff content")

        def mock_pr_status(gh_repo: str, pr_num: str):
            return "MERGED" if pr_num == "78" else "OPEN"

        # 1. Dry-run archive
        dry_res = clean_workspace.clean_subagent_files(
            tmp_path, dry_run=True, pr_status_fn=mock_pr_status, archive=True
        )
        assert len(dry_res) == 2
        assert iter_rev.exists()
        assert diff_78.exists()
        assert not (subagent_dir / "holon-agentic-coder_pr78_archive").exists()

        # 2. Live archive relocation
        archived = clean_workspace.clean_subagent_files(
            tmp_path, dry_run=False, pr_status_fn=mock_pr_status, archive=True
        )
        assert len(archived) == 2
        archive_dir = subagent_dir / "holon-agentic-coder_pr78_archive"
        assert archive_dir.is_dir()
        assert not iter_rev.exists()
        assert not diff_78.exists()
        assert (archive_dir / iter_rev.name).read_text() == "reviewer 1 notes"
        assert (archive_dir / diff_78.name).read_text() == "diff content"

        # Permanent receipts remain untouched in .subagent/
        assert state_78.exists()
        assert posted_78.exists()
        assert consensus_78.exists()

    def test_prune_archived_subagent_bundles_retention(self, tmp_path):
        import os

        subagent_dir = tmp_path / ".subagent"
        archive_old = subagent_dir / "holon-agentic-coder_pr70_archive"
        archive_recent = subagent_dir / "holon-agentic-coder_pr78_archive"
        archive_old.mkdir(parents=True)
        archive_recent.mkdir(parents=True)

        now_ts = 1_800_000_000.0
        old_mtime = now_ts - (35 * 86400)  # 35 days old (> 30d cutoff)
        recent_mtime = now_ts - (10 * 86400)  # 10 days old (< 30d cutoff)

        old_file = archive_old / "holon-agentic-coder_pr70_diff.txt"
        old_file.touch()
        os.utime(old_file, (old_mtime, old_mtime))

        recent_file = archive_recent / "holon-agentic-coder_pr78_diff.txt"
        recent_file.touch()
        os.utime(recent_file, (recent_mtime, recent_mtime))

        # Permanent receipt in .subagent/ even if old must never be touched
        perm_state = subagent_dir / "holon-agentic-coder_pr70_state.json"
        perm_state.touch()
        os.utime(perm_state, (old_mtime, old_mtime))

        # 1. Dry run
        dry_pruned = clean_workspace.prune_archived_subagent_bundles(
            tmp_path, dry_run=True, retention_days=30, now_ts=now_ts
        )
        assert len(dry_pruned) == 1
        assert old_file.exists()

        # 2. Live prune
        pruned = clean_workspace.prune_archived_subagent_bundles(
            tmp_path, dry_run=False, retention_days=30, now_ts=now_ts
        )
        assert len(pruned) == 1
        assert not old_file.exists()
        # Empty archive directory is cleaned up
        assert not archive_old.exists()
        # Recent archive remains intact
        assert recent_file.exists()
        # Permanent receipt remains intact
        assert perm_state.exists()


class TestTodoCleaning:
    """Test todo/ scratchpad cleaning and invariant preservation."""

    def test_clean_todo_files(self, tmp_path):
        todo_dir = tmp_path / "todo"
        todo_dir.mkdir()

        gitkeep = todo_dir / ".gitkeep"
        gitkeep.touch()
        triage = todo_dir / "bean-triage-prioritisation-2026-10-03.md"
        triage.touch()
        user_spec = todo_dir / "my_feature_design.md"
        user_spec.touch()

        intent = todo_dir / "intent-0052.json"
        intent.touch()
        debug_log = todo_dir / "run.log"
        debug_log.touch()
        temp_file = todo_dir / "test.tmp"
        temp_file.touch()

        # 1. Dry run
        dry_purged, dry_preserved = clean_workspace.clean_todo_files(tmp_path, dry_run=True)
        assert len(dry_purged) == 3
        assert intent.exists()
        assert debug_log.exists()
        assert temp_file.exists()

        # 2. Non dry run
        purged, preserved = clean_workspace.clean_todo_files(tmp_path, dry_run=False)
        assert len(purged) == 3
        assert not intent.exists()
        assert not debug_log.exists()
        assert not temp_file.exists()

        assert gitkeep.exists()
        assert triage.exists()
        assert user_spec.exists()
        assert ".gitkeep" in preserved
        assert "bean-triage-prioritisation-2026-10-03.md" in preserved
        assert "my_feature_design.md" in preserved


class TestWorktreeAndDirCleaning:
    """Test worktree and orphaned directory cleaning."""

    @patch("clean_workspace.run_cmd")
    @patch("clean_workspace.is_git_clean")
    @patch("clean_workspace.get_pr_status")
    def test_clean_worktrees_with_force_and_relative_path(self, mock_pr_status, mock_clean, mock_run, tmp_path):
        bare_dir = tmp_path / "bare.git"
        main_wt = tmp_path / "main"
        feature_wt = tmp_path / "fix-0001"
        feature_wt.mkdir(parents=True)

        porcelain = (
            f"worktree {main_wt}\nHEAD 123456\nbranch refs/heads/main\n\n"
            f"worktree {feature_wt}\nHEAD abcdef\nbranch refs/heads/fix-0001\n\n"
        )

        mock_clean.return_value = True
        mock_pr_status.return_value = "MERGED"

        def fake_run_cmd(cmd, cwd=None, check=False):
            if "worktree" in cmd and "list" in cmd:
                return (0, porcelain, "")
            elif "worktree" in cmd and "remove" in cmd:
                # Verify --force is used
                assert "--force" in cmd
                return (0, "", "")
            elif "branch" in cmd and "-D" in cmd or "worktree" in cmd and "prune" in cmd:
                return (0, "", "")
            return (0, "", "")

        mock_run.side_effect = fake_run_cmd

        # Test execution
        rm_wt, del_br = clean_workspace.clean_worktrees(bare_dir, main_wt, "org/repo", dry_run=False, root=tmp_path)

        assert "fix-0001" in rm_wt
        assert "fix-0001" in del_br

    @patch("clean_workspace.run_cmd")
    def test_clean_orphaned_dirs(self, mock_run, tmp_path):
        bare_dir = tmp_path / "bare.git"
        apps_dir = tmp_path / "apps"
        apps_dir.mkdir()

        registered_wt = apps_dir / "registered"
        registered_wt.mkdir()

        orphan_dir = apps_dir / "orphan_wt"
        orphan_dir.mkdir()

        porcelain = f"worktree {registered_wt}\nHEAD 123456\nbranch refs/heads/registered\n\n"

        def fake_run_cmd(cmd, cwd=None, check=False):
            if "worktree" in cmd and "list" in cmd:
                return (0, porcelain, "")
            elif "status" in cmd:
                # Git status in detached/orphan dir fails
                return (128, "", "fatal: this operation must be run in a work tree")
            return (0, "", "")

        mock_run.side_effect = fake_run_cmd

        # Dry run
        dry_purged = clean_workspace.clean_orphaned_dirs(bare_dir, apps_dir, dry_run=True, root=tmp_path)
        assert len(dry_purged) == 1
        assert "orphan_wt" in dry_purged[0]
        assert orphan_dir.exists()

        # Non dry run
        purged = clean_workspace.clean_orphaned_dirs(bare_dir, apps_dir, dry_run=False, root=tmp_path)
        assert len(purged) == 1
        assert "apps/orphan_wt" in purged[0]
        assert not orphan_dir.exists()
        assert registered_wt.exists()


class TestCliMain:
    """Test CLI flags and dry-run execution."""

    @patch("clean_workspace.run_cmd")
    def test_cli_dry_run_flag(self, mock_run, monkeypatch):
        monkeypatch.setattr(
            "sys.argv",
            ["clean_workspace.py", "--dry-run", "--todo-only"],
        )
        mock_run.return_value = (0, "", "")
        with patch("clean_workspace.clean_todo_files") as mock_todo:
            mock_todo.return_value = ([], [])
            clean_workspace.main()
            mock_todo.assert_called_once()
            _, kwargs = mock_todo.call_args
            # dry_run passed as True
            assert mock_todo.call_args[0][1] is True
