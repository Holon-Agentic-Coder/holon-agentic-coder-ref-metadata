"""Tests for the beans-to-issues importer. Fixtures are real bean files copied from .beans/; no GitHub call is made."""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent / ".agents" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import beans_to_issues as b  # noqa: E402

BEANS = Path(__file__).resolve().parent.parent / ".beans"


def bean_file(bid: str) -> Path:
    return next(BEANS.glob(f"{b.ID_PREFIX}{bid}--*.md"))


def corpus(tmp_path: Path, ids: list[str], edits: dict[str, list[tuple[str, str]]] | None = None) -> Path:
    """Copy real beans into tmp_path, optionally rewriting frontmatter lines to open them."""
    d = tmp_path / "beans"
    d.mkdir()
    for bid in ids:
        text = bean_file(bid).read_text(encoding="utf-8")
        for old, new in (edits or {}).get(bid, []):
            assert old in text
            text = text.replace(old, new, 1)
        (d / bean_file(bid).name).write_text(text, encoding="utf-8")
    return d


def test_real_corpus_parses_and_every_open_bean_has_a_title():
    beans = b.load_beans(BEANS)
    open_beans = [x for x in beans.values() if x["fm"].get("status") in b.OPEN_STATUSES]
    assert open_beans
    assert all(isinstance(x["fm"].get("title"), str) and x["fm"]["title"] for x in open_beans)


def test_folded_multiline_title_is_joined():
    bean = b.parse_bean(bean_file("0153"))
    assert bean["fm"]["title"].startswith("Remove comments and docstrings") and "\n" not in bean["fm"]["title"]


def synthetic_bean(d: Path, n: int, priority: str | None) -> str:
    bid = f"{n:04d}"
    pri_line = f"priority: {priority}\n" if priority is not None else ""
    (d / f"{b.ID_PREFIX}{bid}--synthetic-{bid}.md").write_text(
        f"---\n# {b.ID_PREFIX}{bid}\ntitle: Synthetic {bid}\nstatus: todo\ntype: task\n{pri_line}"
        "tags:\n  - holon-agentic-coder\ncreated_at: 2026-01-01T00:00:00Z\n"
        "updated_at: 2026-01-01T00:00:00Z\n---\n\nBody.\n",
        encoding="utf-8",
    )
    return bid


def test_priority_labels_and_the_invalid_medium_maps_to_p2(tmp_path):
    d = tmp_path / "beans"
    d.mkdir()
    cases = {"critical": "P0", "high": "P1", "normal": "P2", "medium": "P2", "low": "P3", None: "P2", "bogus": "P2"}
    ids = {pri: synthetic_bean(d, 9000 + i, pri) for i, pri in enumerate(cases)}
    plan = b.build_plan(b.load_beans(d))
    for pri, label in cases.items():
        labels = plan["issues"][ids[pri]]["labels"]
        assert f"priority:{label}" in labels
        assert sum(x.startswith("priority:") for x in labels) == 1
    assert plan["fidelity"]["priority"]["coerced"] == 1
    assert plan["fidelity"]["priority"]["exact"] == 4
    assert plan["fidelity"]["priority"]["defaulted"] == 2


def test_labels_drop_routing_tags_and_carry_type_priority_status():
    plan = b.build_plan(b.load_beans(BEANS))
    for iss in plan["issues"].values():
        assert not set(iss["labels"]) & b.ROUTING_TAGS
        assert sum(x.startswith("type:") for x in iss["labels"]) == 1
        assert sum(x.startswith("priority:") for x in iss["labels"]) == 1
    in_progress = [i for i in plan["issues"].values() if "status:in-progress" in i["labels"]]
    beans = b.load_beans(BEANS)
    assert len(in_progress) == sum(1 for i in plan["issues"] if beans[i]["fm"]["status"] == "in-progress")


def test_no_harness_references_survive_in_any_payload():
    plan = b.build_plan(b.load_beans(BEANS))
    known = set(b.load_beans(BEANS))
    for bid, iss in plan["issues"].items():
        text = iss["title"] + "\n" + iss["body"]
        assert b.ID_PREFIX not in text, bid
        for marker in (".beans/", ".agents/", "todo/"):
            assert marker not in text, (bid, marker)
        assert not b.residual_refs(text, known), bid


def test_references_to_migrated_beans_become_placeholders_and_others_are_reworded():
    out = b.strip_text(
        "See Beans 0215-0217 and holon-agentic-coder-ref-metadata-0333, also 0376.",
        migrated={"0216", "0376"},
        known={"0215", "0216", "0217", "0333", "0376"},
    )
    assert out == (
        "See an earlier work item, {{issue:0216}}, an earlier work item and an earlier work item, also {{issue:0376}}."
    )


def test_self_reference_and_paths_are_removed():
    out = b.strip_text("Plan in todo/plan-0376.md and .beans/x.md, bean 0376.", set(), known={"0376"}, self_id="0376")
    assert out == "Plan in [harness path] and [harness path], this issue."


def test_routing_by_tag_and_not_migrated_list():
    plan = b.build_plan(b.load_beans(BEANS))
    beans = b.load_beans(BEANS)
    for bid, iss in plan["issues"].items():
        tags = set(beans[bid]["fm"].get("tags") or [])
        if iss["route_basis"] == "tag" and tags & set(b.REPOS):
            assert iss["repo"].endswith("/" + sorted(tags & set(b.REPOS))[0])
    nm = {n["id"]: n for n in plan["not_migrated"]}
    assert "0215" in nm and nm["0215"]["reason"] == "harness-only"
    assert len(plan["issues"]) + len(nm) == plan["open_total"]


def test_dependencies_accept_every_key_spelling_and_parent_becomes_sub_issue(tmp_path):
    # 0122 is the real parent of 0124 and 0125; open the three and give 0124 the other spellings.
    open_ = ("status: completed", "status: todo")
    d = corpus(
        tmp_path,
        ["0122", "0124", "0125", "0126"],
        {
            "0122": [open_, ("tags:", "tags:\n  - holon-agentic-coder")],
            "0124": [
                open_,
                ("tags:", "tags:\n  - holon-agentic-coder"),
                ("parent:", "blocked-by:\n  - " + b.ID_PREFIX + "0125\nparent:"),
            ],
            "0125": [open_, ("tags:", "tags:\n  - holon-agentic-coder")],
            "0126": [
                open_,
                ("tags:", "tags:\n  - holon-agentic-coder"),
                ("parent:", "blocks:\n  - " + b.ID_PREFIX + "0125\nparent:"),
            ],
        },
    )
    plan = b.build_plan(b.load_beans(d))
    assert ("0124", "0125") in plan["blocked_by"]  # blocked-by
    assert ("0125", "0126") in plan["blocked_by"]  # blocks: 0126 blocks 0125
    assert ("0122", "0124") in plan["sub_issues"] and ("0122", "0125") in plan["sub_issues"]


def test_edges_to_unmigrated_beans_are_dropped_and_reported():
    plan = b.build_plan(b.load_beans(BEANS))
    migrated = set(plan["issues"])
    assert all(
        e["blocked"] not in migrated or e["blocker"] not in migrated
        for e in plan["dropped_edges"]
        if e["kind"] == "blocked_by"
    )
    assert all(a in plan["issues"] and c in plan["issues"] for a, c in plan["blocked_by"])


def test_dry_run_writes_files_and_calls_no_gh(tmp_path, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("dry run must not call gh")

    monkeypatch.setattr(b.subprocess, "run", boom)
    out = tmp_path / "out"
    code = b.main(["--out", str(out), "--map", str(tmp_path / "map.json")])
    assert code == 0
    assert (out / "report.md").read_text().startswith("# Beans to issues: dry run report")
    for name in ("labels.json", "dependencies.json", "not_migrated.json", "unmapped.json"):
        json.loads((out / name).read_text())
    assert not (tmp_path / "map.json").exists()
    payloads = list((out / "issues").glob("*/*.json"))
    assert payloads and json.loads(payloads[0].read_text())["labels"]


class FakeGh:
    def __init__(self):
        self.calls, self.n = [], 0

    def __call__(self, cmd, capture_output, text, input=None):
        self.calls.append((cmd, input))
        out = ""
        if cmd[1:3] == ["issue", "create"]:
            self.n += 1
            out = f"https://github.com/{b.ORG}/x/issues/{self.n}"
        elif cmd[1] == "api" and "--jq" in cmd:
            out = "9001"
        return type("R", (), {"returncode": 0, "stdout": out, "stderr": ""})()


def test_apply_is_idempotent_creates_labels_first_and_links_second(tmp_path):
    open_ = ("status: completed", "status: todo")
    tag = ("tags:", "tags:\n  - holon-agentic-coder")
    d = corpus(
        tmp_path,
        ["0124", "0125"],
        {
            "0124": [open_, tag, ("parent:", "blocked_by:\n  - " + b.ID_PREFIX + "0125\nparent:")],
            "0125": [open_, tag],
        },
    )
    plan = b.build_plan(b.load_beans(d))
    map_path = tmp_path / "map.json"
    gh = FakeGh()
    mapping = b.apply_import(plan, map_path, runner=gh)
    kinds = [c[0][1] for c in gh.calls]
    assert kinds.index("label") < kinds.index("issue")
    assert kinds.count("label") and mapping["0124"]["repo"] == "holon-agentic-coder"
    creates = [c for c in gh.calls if c[0][1:3] == ["issue", "create"]]
    assert len(creates) == 2
    assert any("blocked_by" in " ".join(c[0]) for c in gh.calls)
    before = len(gh.calls)
    gh2 = FakeGh()
    b.apply_import(plan, map_path, runner=gh2)
    assert [c for c in gh2.calls if c[0][1:3] == ["issue", "create"]] == []
    assert not [c for c in gh2.calls if c[0][1] == "api" and "POST" in c[0]]
    assert before > 0
    assert json.loads(map_path.read_text())["0125"]["issue"] in (1, 2)
