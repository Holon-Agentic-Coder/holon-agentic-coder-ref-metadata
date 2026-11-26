"""The flow runner refuses an intent whose scope names a directory."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / ".agents" / "skills" / "holon_flow" / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import run_holon_flow  # noqa: E402


def test_a_trailing_slash_entry_is_a_directory():
    assert run_holon_flow.directory_scope_entries(["a/b.py", "apps/x/tests/"]) == ["apps/x/tests/"]


def test_an_existing_directory_without_a_slash_is_a_directory(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "mod.py").write_text("")
    assert run_holon_flow.directory_scope_entries(["pkg", "pkg/mod.py", "pkg/new.py"], tmp_path) == ["pkg"]


def test_a_scope_of_files_passes():
    assert run_holon_flow.directory_scope_entries(["a.py", "b/c.py"]) == []


def test_run_flow_refuses_a_directory_scope_before_any_stage(tmp_path, capsys):
    intent = tmp_path / "intent.json"
    intent.write_text(json.dumps({"slug": "s", "goal": "g", "scope": ["tests/"]}))
    code = run_holon_flow.run_flow(intent, tmp_path, "claude-agent", "m", dry_run=True)
    assert code == 2
    captured = capsys.readouterr()
    assert "never directories" in captured.out + captured.err
