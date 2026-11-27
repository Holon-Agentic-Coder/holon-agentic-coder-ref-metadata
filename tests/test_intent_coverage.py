import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent / ".agents" / "skills" / "holon_flow" / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import intent_coverage  # noqa: E402
import run_holon_flow  # noqa: E402

BEAN_0574 = """# 0574

## Acceptance

- [ ] Refresh both goal copies when a resume re-reads the intent file: `context.intent_data.goal` and
      `context.stage_results.intent.payload.intent.goal`.
- [ ] A goal without the self-explaining-code sentence is refused.
"""
INTENT_0574_MISSING_SECOND_COPY = [
    "A resume re-reads the intent file and refreshes context.intent_data.goal.",
    "A goal without the self-explaining-code sentence is refused.",
]
INTENT_0574_COMPLETE = [
    "A resume re-reads the intent file and refreshes both goal copies: context.intent_data.goal and "
    "context.stage_results.intent.payload.intent.goal.",
    "A goal without the self-explaining-code sentence is refused.",
]

BEAN_0570 = """# 0570

## Check

- Remove the auto-injection; a test proves an intent touching the budget file without the field is refused.
- Target CI: a PR changing the budget file fails unless it carries the `module-budget-change` label applied by the
  maintainer account, and the intent has the field.

## Common acceptance

- The check is proven to fail on a real or reconstructed violation before it is trusted.
"""
INTENT_0570_MISSING_CI_READ = [
    "The auto-injection of module_budget_change is removed; a test proves an intent touching the budget file without "
    "the field is refused.",
    "The check is proven to fail on a real or reconstructed violation before it is trusted.",
]
INTENT_0570_COMPLETE = INTENT_0570_MISSING_CI_READ + [
    "Target CI: a PR changing the budget file fails unless it carries the module-budget-change label applied by the "
    "maintainer account, and the intent has the field.",
]

BEAN_0558 = """# 0558

## Gaps to close

1. **Fails open.** With no merge base the check prints skipped and exits 0; in CI it must fail when origin/main is
   missing.
2. **No count.** Emit the docstring and comment counts in the CI job summary and in the calibration report.
3. **Run in Stage 3.** The gate must run in the executor turn before the push (pre-push), not only in CI.
"""
INTENT_0558_FAIL_CLOSED_ONLY = [
    "With no merge base the check fails in CI when origin/main is missing instead of skipping and exiting 0.",
    "The check reports per-file docstring and comment counts.",
]
INTENT_0558_COMPLETE = INTENT_0558_FAIL_CLOSED_ONLY + [
    "The docstring and comment counts are emitted in the CI job summary and in the calibration report.",
    "The gate runs in the executor turn before the push (pre-push), not only in CI.",
]


def missing_for(bean_markdown, intent_list, mapping=None):
    return intent_coverage.uncovered_items(intent_coverage.bean_items(bean_markdown), intent_list, mapping or {})


def test_bean_0574_missing_second_goal_copy_is_refused_and_complete_passes():
    missing = missing_for(BEAN_0574, INTENT_0574_MISSING_SECOND_COPY)
    assert len(missing) == 1 and "stage_results" in missing[0]
    assert missing_for(BEAN_0574, INTENT_0574_COMPLETE) == []


def test_bean_0570_missing_ci_read_is_refused_and_complete_passes():
    missing = missing_for(BEAN_0570, INTENT_0570_MISSING_CI_READ)
    assert len(missing) == 1 and missing[0].startswith("Target CI")
    assert missing_for(BEAN_0570, INTENT_0570_COMPLETE) == []


def test_bean_0558_missing_summary_calibration_and_pre_push_is_refused_and_complete_passes():
    missing = missing_for(BEAN_0558, INTENT_0558_FAIL_CLOSED_ONLY)
    assert len(missing) == 2
    assert any("job summary" in item for item in missing)
    assert any("pre-push" in item for item in missing)
    assert missing_for(BEAN_0558, INTENT_0558_COMPLETE) == []


def test_extraction_reads_checkboxes_bullets_numbers_table_rows_and_ignores_other_sections():
    markdown = (
        "## Problem\n\n- not an item\n\n## Acceptance\n\n- [x] first\n  continued\n* second\n3. third\n\n"
        "| a | b |\n| :-- | :-- |\n| row one | cell |\n\n## Notes\n\n- ignored\n"
    )
    assert intent_coverage.bean_items(markdown) == ["first continued", "second", "third", "a b", "row one cell"]


def test_an_explicit_mapping_covers_an_item_the_fuzzy_match_rejects():
    items = intent_coverage.bean_items(BEAN_0574)
    unrelated = "Resume keeps the checkpoint consistent."
    bean_item = items[0]
    assert missing_for(BEAN_0574, ["x", INTENT_0574_COMPLETE[1], unrelated]) == [bean_item]
    assert missing_for(BEAN_0574, ["x", INTENT_0574_COMPLETE[1], unrelated], {bean_item: unrelated}) == []


def test_a_mapping_to_an_item_the_intent_lacks_does_not_cover():
    bean_item = intent_coverage.bean_items(BEAN_0574)[0]
    assert missing_for(BEAN_0574, ["x", INTENT_0574_COMPLETE[1]], {bean_item: "not in the intent"}) == [bean_item]


def harness(tmp_path, bean_id, bean_markdown, mapping=None):
    (tmp_path / ".beans").mkdir()
    (tmp_path / ".beans" / f"proj-{bean_id}--title.md").write_text(bean_markdown)
    if mapping is not None:
        (tmp_path / "todo").mkdir()
        (tmp_path / "todo" / f"intent-coverage-{bean_id}.json").write_text(json.dumps(mapping))
    return tmp_path


def test_coverage_refusal_names_the_unmatched_items(tmp_path):
    root = harness(tmp_path, "0574", BEAN_0574)
    intent = {"slug": "s", "goal": "g", "acceptance_criteria": INTENT_0574_MISSING_SECOND_COPY}
    refusal = intent_coverage.coverage_refusal(intent, "0574", root)
    assert refusal and "1 of 2" in refusal and "stage_results" in refusal
    assert (
        intent_coverage.coverage_refusal({**intent, "acceptance_criteria": INTENT_0574_COMPLETE}, "0574", root) is None
    )


def test_the_mapping_file_in_todo_is_honoured(tmp_path):
    bean_item = intent_coverage.bean_items(BEAN_0574)[0]
    unrelated = "Resume keeps the checkpoint consistent."
    root = harness(tmp_path, "0574", BEAN_0574, {bean_item: unrelated})
    intent = {"acceptance_criteria": [unrelated, INTENT_0574_COMPLETE[1]]}
    assert intent_coverage.coverage_refusal(intent, "0574", root) is None


def test_an_unknown_bean_or_a_bean_without_items_refuses(tmp_path):
    assert "no file" in intent_coverage.coverage_refusal({}, "9999", tmp_path)
    root = harness(tmp_path, "0001", "# empty\n")
    assert "lists no acceptance items" in intent_coverage.coverage_refusal({}, "0001", root)


@pytest.fixture
def intent_file(tmp_path):
    path = tmp_path / "intent.json"
    path.write_text(json.dumps({"slug": "s", "goal": "g", "acceptance_criteria": ["unrelated"]}))
    return path


def test_run_flow_refuses_an_uncovered_bean_with_exit_2(intent_file, tmp_path, monkeypatch, capsys):
    (tmp_path / "h").mkdir()
    root = harness(tmp_path / "h", "0574", BEAN_0574)
    monkeypatch.setattr(
        run_holon_flow, "coverage_refusal", lambda intent, bean: intent_coverage.coverage_refusal(intent, bean, root)
    )
    code = run_holon_flow.run_flow(intent_file, tmp_path, "claude-agent", "m", dry_run=True, bean="0574")
    assert code == 2
    assert "acceptance items of bean 0574" in "".join(capsys.readouterr())


def test_run_flow_skips_the_check_when_resuming(intent_file, tmp_path, monkeypatch):
    called = []
    monkeypatch.setattr(run_holon_flow, "coverage_refusal", lambda intent, bean: called.append(bean) or "refused")
    monkeypatch.setattr(
        run_holon_flow, "resolve_flow_worktree", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("past gate"))
    )
    with pytest.raises(RuntimeError, match="past gate"):
        run_holon_flow.run_flow(
            intent_file, tmp_path, "claude-agent", "m", dry_run=True, bean="0574", from_stage="review"
        )
    assert called == []


def test_run_flow_warns_loudly_without_a_bean(intent_file, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        run_holon_flow, "resolve_flow_worktree", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("past gate"))
    )
    with pytest.raises(RuntimeError, match="past gate"):
        run_holon_flow.run_flow(intent_file, tmp_path, "claude-agent", "m", dry_run=True)
    assert "No --bean given" in "".join(capsys.readouterr())


def test_the_command_line_accepts_bean():
    out = subprocess.run(
        [sys.executable, str(SCRIPTS / "run_holon_flow.py"), "--help"], capture_output=True, text=True, check=True
    ).stdout
    assert "--bean" in out
