import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent / ".agents" / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import pr_readiness  # noqa: E402


def _sample_pr(
    *,
    reviews=None,
    files=None,
    checks=None,
    head_sha="abcdef1234567890",
):
    return {
        "number": 455,
        "url": "https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/455",
        "state": "OPEN",
        "baseRefName": "main",
        "headRefName": "I-1795819107-demo/P-1795819130/E-1795819432/_",
        "headRefOid": head_sha,
        "mergeable": "MERGEABLE",
        "mergeStateStatus": "CLEAN",
        "reviews": reviews
        if reviews is not None
        else [
            {
                "state": "COMMENTED",
                "author": {"login": "thomashan"},
                "commit": {"oid": "23ba28bc41e81a74"},
                "body": "## ✅ Ensemble Consensus Review — APPROVED (3/3)\n**Ensemble Consensus Verdict**: `APPROVED`",
            }
        ],
        "files": files
        if files is not None
        else [
            {"path": "plans/I-1795819107-demo/P-1795819130-ANA-G4N_calibration.md"},
            {"path": "apps/sandbox-executor/src/sandbox_executor/touch_set.py"},
        ],
        "statusCheckRollup": checks
        if checks is not None
        else [
            {"name": "unit (ubuntu-latest)", "status": "COMPLETED", "conclusion": "SUCCESS"},
            {"name": "unit (macos-latest, shard 1 of 2)", "status": "COMPLETED", "conclusion": "SUCCESS"},
        ],
    }


def test_ready_pr_formats_ready_line_and_exits_zero(capsys):
    code = pr_readiness.main(["https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/455"], fetcher=lambda r, n: _sample_pr())
    out = capsys.readouterr().out
    first_line = out.splitlines()[0]
    assert code == 0
    assert first_line.startswith("READY: PR #455 (Holon-Agentic-Coder/holon-agentic-coder)")
    assert "abcdef12" in first_line
    assert "| `unit (ubuntu-latest)` | `COMPLETED` | `SUCCESS` |" in out


def test_pending_ci_prints_not_ready_ci_pending_and_exits_one(capsys):
    data = _sample_pr(
        checks=[
            {"name": "unit (ubuntu-latest)", "status": "COMPLETED", "conclusion": "SUCCESS"},
            {"name": "unit (macos-latest, shard 1 of 2)", "status": "IN_PROGRESS", "conclusion": None},
        ]
    )
    code = pr_readiness.main(["455"], fetcher=lambda r, n: data)
    out = capsys.readouterr().out
    first_line = out.splitlines()[0]
    assert code == 1
    assert first_line.startswith("not ready: CI pending")
    assert "outstanding gates: pipeline" in first_line
    assert "| `unit (macos-latest, shard 1 of 2)` | `IN_PROGRESS` | `PENDING` |" in out


def test_failed_ci_prints_not_ready_ci_failed_and_exits_one(capsys):
    data = _sample_pr(
        checks=[
            {"name": "hygiene (ubuntu-latest)", "status": "COMPLETED", "conclusion": "FAILURE"},
            {"name": "scan", "status": "COMPLETED", "conclusion": "SUCCESS"},
        ]
    )
    code = pr_readiness.main(["455"], fetcher=lambda r, n: data)
    first_line = capsys.readouterr().out.splitlines()[0]
    assert code == 1
    assert first_line.startswith("not ready: CI failed")
    assert "pipeline" in first_line


def test_missing_calibration_report_prints_not_ready(capsys):
    data = _sample_pr(files=[{"path": "apps/sandbox-executor/src/sandbox_executor/touch_set.py"}])
    code = pr_readiness.main(["455"], fetcher=lambda r, n: data)
    first_line = capsys.readouterr().out.splitlines()[0]
    assert code == 1
    assert first_line.startswith("not ready: Stage 5 calibration missing")
    assert "outstanding gates: calibration" in first_line


def test_missing_consensus_review_prints_not_ready(capsys):
    data = _sample_pr(reviews=[])
    code = pr_readiness.main(["455"], fetcher=lambda r, n: data)
    first_line = capsys.readouterr().out.splitlines()[0]
    assert code == 1
    assert first_line.startswith("not ready:")
    assert "consensus" in first_line


def test_combined_missing_calibration_and_pending_ci(capsys):
    data = _sample_pr(
        files=[{"path": "README.md"}],
        checks=[{"name": "unit (macos-latest)", "status": "QUEUED", "conclusion": None}],
    )
    code = pr_readiness.main(["455"], fetcher=lambda r, n: data)
    first_line = capsys.readouterr().out.splitlines()[0]
    assert code == 1
    assert "Stage 5 calibration missing" in first_line
    assert "CI pending" in first_line
    assert "calibration, pipeline" in first_line


def test_url_parsing_json_and_record_flag(capsys):
    seen = []

    def fetcher(repo, num):
        seen.append((repo, num))
        return _sample_pr(checks=[])

    code = pr_readiness.main(
        ["https://github.com/Holon-Agentic-Coder/holon-coherence/pull/94", "--json", "--record"],
        fetcher=fetcher,
    )
    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert seen == [("Holon-Agentic-Coder/holon-coherence", 94)]
    assert payload["ready"] is False
    assert payload["outstanding_gates"] == ["pipeline"]


def test_checkpoint_must_show_completed_calibration(tmp_path, capsys):
    cp = tmp_path / "checkpoint.json"
    cp.write_text(json.dumps({"current_stage": "review"}), encoding="utf-8")
    code = pr_readiness.main(["455", "--checkpoint", str(cp)], fetcher=lambda r, n: _sample_pr())
    first_line = capsys.readouterr().out.splitlines()[0]
    assert code == 1
    assert "Stage 5 calibration missing" in first_line
