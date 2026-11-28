#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

DEFAULT_REPO = "Holon-Agentic-Coder/holon-agentic-coder"
PR_URL_RE = re.compile(r"https?://github\.com/([^/]+/[^/]+)/pull/(\d+)(?:[/?#].*)?$")
CALIBRATION_FILE_RE = re.compile(r"^plans/.+/P-[^/]+_calibration\.md$")
ENSEMBLE_VERDICT_RE = re.compile(
    r"(?:\*\*Ensemble Consensus Verdict\*\*:\s*`?(APPROVED|CHANGES_REQUESTED)`?|"
    r"Ensemble Consensus Review\s+[\u2014-]+\s+(APPROVED|CHANGES_REQUESTED))"
)

FAIL_CONCLUSIONS = frozenset(
    {"FAILURE", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED", "STARTUP_FAILURE", "ERROR", "STALE"}
)
PASS_CONCLUSIONS = frozenset({"SUCCESS", "SKIPPED", "NEUTRAL"})


@dataclass(frozen=True)
class CheckRow:
    job: str
    state: str
    conclusion: str


@dataclass(frozen=True)
class ReadinessReport:
    repo: str
    pr_number: int
    url: str
    state: str
    base_ref: str
    head_ref: str
    head_sha: str
    mergeable: str
    merge_state_status: str
    review_verdict: str
    review_head_sha: str | None
    calibration_state: str
    calibration_files: tuple[str, ...]
    checks: tuple[CheckRow, ...]
    outstanding_gates: tuple[str, ...]
    reasons: tuple[str, ...]
    ready: bool


def parse_pr_target(target: str, repo: str = DEFAULT_REPO) -> tuple[str, int]:
    stripped = target.strip()
    match = PR_URL_RE.match(stripped)
    if match:
        return match.group(1), int(match.group(2))
    if stripped.isdigit():
        return repo, int(stripped)
    raise ValueError(f"Expected PR number or GitHub pull request URL, got: {target!r}")


def _effective_review_verdict(reviews: list[dict[str, Any]]) -> tuple[str, str | None]:
    if not reviews:
        return "missing", None

    formal_by_author: dict[str, str] = {}
    ensemble_verdicts: list[tuple[str, str | None]] = []
    latest_commit: str | None = None

    for idx, review in enumerate(reviews):
        commit_obj = review.get("commit") or {}
        commit_oid = commit_obj.get("oid") if isinstance(commit_obj, dict) else None
        if isinstance(commit_oid, str) and commit_oid:
            latest_commit = commit_oid

        state = str(review.get("state") or "").upper()
        body = str(review.get("body") or "")
        author_obj = review.get("author") or {}
        author = (
            str(author_obj.get("login") or f"reviewer-{idx}") if isinstance(author_obj, dict) else f"reviewer-{idx}"
        )

        if state in {"APPROVED", "CHANGES_REQUESTED"}:
            formal_by_author[author] = state

        match = ENSEMBLE_VERDICT_RE.search(body)
        if match:
            verdict = match.group(1) or match.group(2)
            ensemble_verdicts.append((verdict, commit_oid))

    if ensemble_verdicts:
        last_verdict, last_commit = ensemble_verdicts[-1]
        return last_verdict, last_commit or latest_commit

    verdicts = set(formal_by_author.values())
    if "CHANGES_REQUESTED" in verdicts:
        return "CHANGES_REQUESTED", latest_commit
    if "APPROVED" in verdicts:
        return "APPROVED", latest_commit
    return "COMMENTED", latest_commit


def _normalize_checks(rollup: list[dict[str, Any]]) -> tuple[CheckRow, ...]:
    rows: list[CheckRow] = []
    for item in rollup:
        if "context" in item and "name" not in item:
            job = str(item.get("context") or "status")
            raw_state = str(item.get("state") or "PENDING").upper()
            state = "COMPLETED" if raw_state in PASS_CONCLUSIONS | FAIL_CONCLUSIONS else raw_state
            conclusion = raw_state if state == "COMPLETED" else "PENDING"
        else:
            job = str(item.get("name") or item.get("context") or "check")
            state = str(item.get("status") or "PENDING").upper()
            raw_conclusion = item.get("conclusion")
            conclusion = str(raw_conclusion).upper() if raw_conclusion else "PENDING"
        rows.append(CheckRow(job=job, state=state, conclusion=conclusion))
    return tuple(sorted(rows, key=lambda row: row.job.lower()))


def _pipeline_status(checks: tuple[CheckRow, ...]) -> tuple[bool, str]:
    if not checks:
        return False, "CI pending"
    failed = [row for row in checks if row.conclusion in FAIL_CONCLUSIONS]
    if failed:
        return False, f"CI failed ({len(failed)}/{len(checks)})"
    pending = [row for row in checks if row.state != "COMPLETED" or row.conclusion not in PASS_CONCLUSIONS]
    if pending:
        return False, f"CI pending ({len(pending)}/{len(checks)})"
    return True, f"passed ({len(checks)}/{len(checks)})"


def _calibration_status(
    files: list[dict[str, Any]],
    checkpoint: dict[str, Any] | None,
) -> tuple[bool, str, tuple[str, ...]]:
    cal_files = tuple(
        sorted(
            str(f.get("path"))
            for f in files
            if isinstance(f, dict) and CALIBRATION_FILE_RE.match(str(f.get("path") or ""))
        )
    )
    if not cal_files:
        return False, "missing P-*_calibration.md on PR diff", ()
    if checkpoint is not None:
        stage_ok = checkpoint.get("current_stage") == "completed" or (
            checkpoint.get("status") == "completed" and "calibrate" in (checkpoint.get("completed_stages") or ())
        )
        if not stage_ok:
            return False, "calibrate stage not completed in checkpoint", cal_files
    return True, "calibrate=success", cal_files


def evaluate_pr(
    data: dict[str, Any],
    repo: str = DEFAULT_REPO,
    checkpoint: dict[str, Any] | None = None,
) -> ReadinessReport:
    reviews = list(data.get("reviews") or [])
    review_verdict, review_head_sha = _effective_review_verdict(reviews)
    cal_ok, cal_state, cal_files = _calibration_status(list(data.get("files") or []), checkpoint)
    checks = _normalize_checks(list(data.get("statusCheckRollup") or []))
    pipeline_ok, pipeline_note = _pipeline_status(checks)

    outstanding: list[str] = []
    reasons: list[str] = []

    if review_verdict != "APPROVED":
        outstanding.append("consensus")
        if review_verdict == "CHANGES_REQUESTED":
            reasons.append("consensus changes requested")
        else:
            reasons.append("consensus review missing")

    if not cal_ok:
        outstanding.append("calibration")
        reasons.append("Stage 5 calibration missing")

    if not pipeline_ok:
        outstanding.append("pipeline")
        reasons.append(pipeline_note)

    head_sha = str(data.get("headRefOid") or "")
    return ReadinessReport(
        repo=repo,
        pr_number=int(data.get("number") or 0),
        url=str(data.get("url") or f"https://github.com/{repo}/pull/{data.get('number')}"),
        state=str(data.get("state") or "UNKNOWN"),
        base_ref=str(data.get("baseRefName") or ""),
        head_ref=str(data.get("headRefName") or ""),
        head_sha=head_sha,
        mergeable=str(data.get("mergeable") or "UNKNOWN"),
        merge_state_status=str(data.get("mergeStateStatus") or "UNKNOWN"),
        review_verdict=review_verdict,
        review_head_sha=review_head_sha,
        calibration_state=cal_state,
        calibration_files=cal_files,
        checks=checks,
        outstanding_gates=tuple(outstanding),
        reasons=tuple(reasons),
        ready=not outstanding,
    )


def format_markdown(report: ReadinessReport) -> str:
    short_head = report.head_sha[:8] if report.head_sha else "unknown"
    if report.ready:
        first_line = (
            f"READY: PR #{report.pr_number} ({report.repo}) — head `{short_head}` "
            "(gates: consensus=ok, calibration=ok, pipeline=ok)"
        )
    else:
        reason_text = "; ".join(report.reasons)
        gate_text = ", ".join(report.outstanding_gates)
        first_line = f"not ready: {reason_text} (outstanding gates: {gate_text})"

    review_sha_note = f" on `{report.review_head_sha[:8]}`" if report.review_head_sha else ""
    cal_files_note = (
        f" ({', '.join(f'`{path}`' for path in report.calibration_files)})" if report.calibration_files else ""
    )
    gates_note = "none" if report.ready else ", ".join(report.outstanding_gates)
    head_sha = report.head_sha or "unknown"

    lines = [
        first_line,
        "",
        f"- **PR:** {report.url}",
        f"- **Head SHA:** `{head_sha}` ({report.state}, `{report.mergeable}` / `{report.merge_state_status}`)",
        f"- **Review Verdict:** `{report.review_verdict}`{review_sha_note}",
        f"- **Stage 5 Calibration:** {report.calibration_state}{cal_files_note}",
        f"- **Outstanding Gates:** {gates_note}",
        "",
        "| Job | State | Conclusion |",
        "| --- | --- | --- |",
    ]
    if report.checks:
        for row in report.checks:
            lines.append(f"| `{row.job}` | `{row.state}` | `{row.conclusion}` |")
    else:
        lines.append("| `(none)` | `PENDING` | `PENDING` |")
    return "\n".join(lines)


def fetch_pr_data(repo: str, pr_number: int) -> dict[str, Any]:
    fields = (
        "number,url,state,baseRefName,headRefName,headRefOid,mergeable,mergeStateStatus,reviews,files,statusCheckRollup"
    )
    raw = subprocess.check_output(
        ["gh", "pr", "view", str(pr_number), "--repo", repo, "--json", fields],
        text=True,
    )
    return dict(json.loads(raw))


def main(
    argv: list[str] | None = None,
    fetcher: Callable[[str, int], dict[str, Any]] = fetch_pr_data,
) -> int:
    parser = argparse.ArgumentParser(description="Check per-head PR readiness (consensus, calibration, CI).")
    parser.add_argument("pr", help="PR number or GitHub pull request URL.")
    parser.add_argument("--repo", default=DEFAULT_REPO, help="GitHub owner/repo when pr is a number.")
    parser.add_argument("--checkpoint", type=Path, default=None, help="Optional flow checkpoint/state JSON path.")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit structured JSON output.")
    parser.add_argument(
        "--record",
        action="store_true",
        help="Exit 0 even when not ready (used when recording merge-time state in post-pr-merge).",
    )
    args = parser.parse_args(argv)

    repo, pr_number = parse_pr_target(args.pr, args.repo)
    checkpoint_data = json.loads(args.checkpoint.read_text(encoding="utf-8")) if args.checkpoint else None
    report = evaluate_pr(fetcher(repo, pr_number), repo=repo, checkpoint=checkpoint_data)

    if args.as_json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(format_markdown(report))

    return 0 if (report.ready or args.record) else 1


if __name__ == "__main__":
    sys.exit(main())
