"""Unit tests for the prioritise_beans triage generator (prioritise-beans skill)."""

import sys
from pathlib import Path

# Ensure prioritise_beans script is importable
SCRIPT_DIR = Path(__file__).resolve().parent.parent / ".agents" / "skills" / "prioritise_beans" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import prioritise_beans  # noqa: E402


def make_bean(beans_dir: Path, bean_num: str, frontmatter: str, body: str = "## Summary\n\nA bean.\n") -> Path:
    path = beans_dir / f"holon-agentic-coder-ref-metadata-{bean_num}--test-bean.md"
    path.write_text(f"---\n{frontmatter}\n---\n\n{body}", encoding="utf-8")
    return path


class TestParseFrontmatter:
    """parse_frontmatter: folded quoted scalars, list/blank escapes, quote stripping."""

    def test_folded_quoted_title_real_bean_0153_shape(self):
        # Mirrors .beans/holon-agentic-coder-ref-metadata-0153--....md exactly.
        content = (
            "---\n"
            "# holon-agentic-coder-ref-metadata-0153\n"
            "title:\n"
            '  "Remove comments and docstrings from all code (Python, shell, JavaScript, build and CI files); '
            "make code\n"
            '  self-documenting"\n'
            "status: todo\n"
            "---\n"
        )
        fm = prioritise_beans.parse_frontmatter(content)
        assert fm["title"] == (
            "Remove comments and docstrings from all code (Python, shell, JavaScript, build and CI files); "
            "make code self-documenting"
        )
        assert fm["status"] == "todo"

    def test_tags_list_after_key_is_not_a_scalar_continuation(self):
        content = "---\ntitle: Short title\ntags:\n  - ledger\n  - calibration\nstatus: todo\n---\n"
        fm = prioritise_beans.parse_frontmatter(content)
        assert fm["title"] == "Short title"
        assert fm["tags"] == ""  # list items are not folded into the scalar
        assert fm["status"] == "todo"

    def test_blank_indented_line_ends_continuation(self):
        content = '---\ntitle:\n  "A title"\n   \nstatus: todo\n---\n'
        fm = prioritise_beans.parse_frontmatter(content)
        assert fm["title"] == "A title"
        assert fm["status"] == "todo"

    def test_paired_quote_stripping(self):
        content = '---\na: "double quoted"\nb: \'single quoted\'\nc: "unpaired\nd: plain\n---\n'
        fm = prioritise_beans.parse_frontmatter(content)
        assert fm["a"] == "double quoted"
        assert fm["b"] == "single quoted"
        assert fm["c"] == '"unpaired'  # unpaired quotes are left alone
        assert fm["d"] == "plain"

    def test_missing_frontmatter_returns_empty(self):
        assert prioritise_beans.parse_frontmatter("# No frontmatter here\n") == {}


class TestPriorityMapping:
    """extract_bean_metadata: frontmatter priority -> P-level mapping."""

    def test_critical_maps_to_p0(self, tmp_path):
        path = make_bean(tmp_path, "9001", "title: T\nstatus: todo\npriority: critical")
        bean = prioritise_beans.extract_bean_metadata(str(path))
        assert bean["priority_level"] == "P0"

    def test_high_normal_medium_map_to_p1(self, tmp_path):
        for i, priority in enumerate(("high", "normal", "medium")):
            path = make_bean(tmp_path, f"900{2 + i}", f"title: T\nstatus: todo\npriority: {priority}")
            bean = prioritise_beans.extract_bean_metadata(str(path))
            assert bean["priority_level"] == "P1", priority

    def test_low_and_minor_map_to_p2(self, tmp_path):
        for i, priority in enumerate(("low", "minor")):
            path = make_bean(tmp_path, f"900{5 + i}", f"title: T\nstatus: todo\npriority: {priority}")
            bean = prioritise_beans.extract_bean_metadata(str(path))
            assert bean["priority_level"] == "P2", priority

    def test_template_and_non_bean_files_are_skipped(self, tmp_path):
        template = tmp_path / "template.md"
        template.write_text("---\ntitle: T\n---\n", encoding="utf-8")
        assert prioritise_beans.extract_bean_metadata(str(template)) is None


class TestScanBeansSortAndStats:
    """scan_beans: OVERRIDES-insertion-order sort, fallback ordering, and status counters."""

    def test_sort_overrides_order_then_priority_then_number_desc(self, tmp_path):
        override_nums = list(prioritise_beans.OVERRIDES)
        first, second = override_nums[0], override_nums[1]
        # Create the two overridden beans out of OVERRIDES order, plus two
        # un-overridden beans where priority must outrank bean number.
        make_bean(tmp_path, second, "title: B\nstatus: todo\npriority: normal")
        make_bean(tmp_path, first, "title: A\nstatus: in-progress\npriority: critical")
        make_bean(tmp_path, "9998", "title: C\nstatus: todo\npriority: critical")  # P0
        make_bean(tmp_path, "9999", "title: D\nstatus: todo\npriority: normal")  # P1
        active, stats = prioritise_beans.scan_beans(str(tmp_path))
        assert [b["bean_num"] for b in active] == [first, second, "9998", "9999"]
        # Overridden beans take the curated display fields.
        assert active[0]["priority_display"] == prioritise_beans.OVERRIDES[first]["priority"]
        assert active[2]["priority_display"] == "**P0**"

    def test_number_descending_breaks_priority_ties(self, tmp_path):
        make_bean(tmp_path, "9001", "title: Old\nstatus: todo\npriority: normal")
        make_bean(tmp_path, "9002", "title: New\nstatus: todo\npriority: normal")
        active, _ = prioritise_beans.scan_beans(str(tmp_path))
        assert [b["bean_num"] for b in active] == ["9002", "9001"]

    def test_stats_count_statuses_separately(self, tmp_path):
        make_bean(tmp_path, "9001", "title: A\nstatus: completed")
        make_bean(tmp_path, "9002", "title: B\nstatus: scrapped")
        make_bean(tmp_path, "9003", "title: C\nstatus: in-progress")
        make_bean(tmp_path, "9004", "title: D\nstatus: todo")
        make_bean(tmp_path, "9005", "title: E\nstatus: draft")
        _, stats = prioritise_beans.scan_beans(str(tmp_path))
        assert stats == {
            "total_tracked": 5,
            "completed": 1,
            "scrapped": 1,
            "active": 3,
            "in_progress": 1,
            "draft": 1,
        }


class TestGenerateTriageDocument:
    """generate_triage_document: the Executive Summary breakdown line."""

    @staticmethod
    def _stats(active: int, in_progress: int, draft: int) -> dict[str, int]:
        return {
            "total_tracked": 163,
            "completed": 138,
            "scrapped": 2,
            "active": active,
            "in_progress": in_progress,
            "draft": draft,
        }

    def test_zero_drafts_keeps_committed_wording(self):
        doc = prioritise_beans.generate_triage_document([], self._stats(23, 3, 0), timestamp_str="TS")
        assert "- **Active**: 23 (14.1%), of which 3 are in progress and 20 are todo" in doc

    def test_draft_beans_are_not_counted_as_todo(self):
        doc = prioritise_beans.generate_triage_document([], self._stats(23, 3, 2), timestamp_str="TS")
        assert "of which 3 are in progress, 18 are todo and 2 are draft" in doc
