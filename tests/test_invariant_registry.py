import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_DIR = ROOT / ".agents" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import install_git_hooks  # noqa: E402
import invariant_registry as registry  # noqa: E402

AGENTS_TEXT = (ROOT / "AGENTS.md").read_text()
ENTRIES = registry.load_registry()


def test_every_hard_rule_maps_to_a_registry_entry():
    assert registry.unmapped_hard_rules(ENTRIES, AGENTS_TEXT) == []
    assert registry.dangling_agents_rules(ENTRIES, AGENTS_TEXT) == []


def test_every_referenced_check_exists():
    problems = [problem for entry in ENTRIES for problem in registry.entry_problems(entry)]
    assert problems == []


def test_missing_and_partial_entries_name_an_open_bean():
    problems = [problem for entry in ENTRIES for problem in registry.open_bean_problems(entry)]
    assert problems == []


def test_the_registry_covers_every_maintainer_invariant():
    required = {
        "self-explaining-code",
        "clock-read-utc-timestamps",
        "three-append-only-ledgers",
        "no-harness-references-in-targets",
        "intent-scope-lists-files-only",
        "git-safety",
        "no-attribution-trailers",
        "main-worktrees-untouched",
        "forbidden-flow-flags",
        "budget-authorisation",
        "bean-format",
        "every-review-finding-actioned",
        "flow-concurrency",
        "tests-only-via-uv-run-pytest",
        "format-before-commit",
        "never-merge-into-main",
        "new-invariant-lands-with-its-check",
    }
    assert required - {entry["id"] for entry in ENTRIES} == set()


def test_entry_ids_are_unique():
    identifiers = [entry["id"] for entry in ENTRIES]
    assert len(identifiers) == len(set(identifiers))


def test_a_new_hard_rule_without_an_entry_fails():
    extended = AGENTS_TEXT.replace("\n---\n\n## 🚀", "\n- **Brand new rule**: something.\n\n---\n\n## 🚀", 1)
    assert "Brand new rule" in registry.unmapped_hard_rules(ENTRIES, extended)


def test_a_removed_hard_rule_leaves_a_dangling_entry():
    shortened = AGENTS_TEXT.replace("- **Tests**:", "- **Renamed**:", 1)
    assert registry.dangling_agents_rules(ENTRIES, shortened) == ["Tests"]
    assert "Renamed" in registry.unmapped_hard_rules(ENTRIES, shortened)


@pytest.mark.parametrize(
    "check",
    [
        "test:tests/test_git_guard.py::test_no_such_test",
        "test:tests/test_no_such_file.py::test_x",
        "hook:.agents/hooks/no-such-hook",
        "script:.agents/scripts/no_such_script.py",
        "workflow:.github/workflows/test-hygiene.yml#no-such-job",
        "workflow:.github/workflows/no-such.yml#hygiene",
        "tool:something",
    ],
)
def test_a_dangling_check_is_reported(check):
    assert registry.resolve_check(check, ROOT) is not None


def test_a_resolvable_check_passes():
    assert registry.resolve_check("workflow:.github/workflows/test-hygiene.yml#hygiene", ROOT) is None
    assert registry.resolve_check("test:tests/test_git_guard.py::test_blocked_forms", ROOT) is None


def test_enforced_without_a_check_and_bad_status_are_reported():
    entry = {"id": "x", "status": "enforced", "runs_at": ["ci"], "checks": []}
    assert registry.entry_problems(entry, ROOT) == ["x: enforced without a check"]
    assert registry.entry_problems({"id": "y", "status": "done", "runs_at": ["ci"]}, ROOT)


def test_missing_without_a_bean_or_with_a_completed_bean_is_reported(tmp_path):
    (tmp_path / "p-0001--a.md").write_text("---\nstatus: completed\n---\n")
    (tmp_path / "p-0002--b.md").write_text("---\nstatus: todo\n---\n")
    assert registry.open_bean_problems({"id": "a", "status": "missing", "open_beans": []}, tmp_path)
    assert registry.open_bean_problems({"id": "b", "status": "partial", "open_beans": ["0001"]}, tmp_path)
    assert registry.open_bean_problems({"id": "c", "status": "missing", "open_beans": ["0009"]}, tmp_path)
    assert registry.open_bean_problems({"id": "d", "status": "missing", "open_beans": ["0002"]}, tmp_path) == []
    assert registry.open_bean_problems({"id": "e", "status": "enforced", "open_beans": []}, tmp_path) == []


def test_the_loader_rejects_unsupported_syntax(tmp_path):
    path = tmp_path / "bad.yml"
    path.write_text("invariants:\n  - id: a\n  # a comment\n")
    with pytest.raises(ValueError):
        registry.load_registry(path)


def test_the_script_exits_zero_on_the_real_registry():
    completed = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "invariant_registry.py")], capture_output=True, text=True
    )
    assert completed.returncode == 0, completed.stderr


def test_agents_md_and_the_registry_reference_the_installer():
    assert ".agents/scripts/install_git_hooks.py" in AGENTS_TEXT
    assert any(
        ".agents/scripts/install_git_hooks.py" in entry.get("checks", [""])[0]
        for entry in ENTRIES
        if entry["id"] == "hooks-installed"
    )


def test_installer_is_idempotent_and_installs_every_hook(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "pre-commit").write_text("#!/bin/sh\nexit 0\n")
    (source / "commit-msg").write_text("#!/bin/sh\nexit 0\n")
    target = tmp_path / "hooks"
    assert install_git_hooks.install_hooks(source, target) == ["commit-msg", "pre-commit"]
    assert install_git_hooks.install_hooks(source, target) == []
    (source / "pre-commit").write_text("#!/bin/sh\nexit 1\n")
    assert install_git_hooks.install_hooks(source, target) == ["pre-commit"]
    assert (target / "pre-commit").read_text().endswith("exit 1\n")
    assert (target / "commit-msg").stat().st_mode & 0o100


def test_the_real_hooks_directory_resolves_inside_git():
    assert install_git_hooks.git_hooks_directory(ROOT).name == "hooks"
