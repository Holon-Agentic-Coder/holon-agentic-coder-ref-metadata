---
# holon-agentic-coder-ref-metadata-0558
title: "Self-explaining gate (#357): fail closed in CI, cover ledger text, and report per-PR counts"
status: in-progress
type: task
priority: high
tags:
  - pipeline
  - coding-standards
  - self-explaining-code
  - holon-agentic-coder
created_at: 2026-11-26T22:59:59Z
updated_at: 2026-11-27T07:43:42Z
---

## Evidence

Added lines in today's merged PRs (diff scan, `gh pr diff`; the comment count includes markdown headings in plan and
execution files, so it is an upper bound; docstring openers are a lower bound of docstrings):

| PR   | added lines | docstring opener lines | added `#` lines not `# why:` |
| :--- | ----------: | ---------------------: | ---------------------------: |
| #350 |         744 |                     12 |                           49 |
| #351 |       1,969 |                     62 |                           67 |
| #352 |         995 |                     17 |                           58 |
| #354 |         654 |                     11 |                           47 |
| #355 |         625 |                      1 |                           57 |
| #356 |         644 |                      4 |                           47 |

All six added docstrings; five of six exceed 11. CF-0012 records about 30 PRs today with the same fault. PR #357 (open)
adds `scripts/check_self_explaining.py`, diff-scoped, in lint, pre-commit and `test-hygiene.yml`, plus prompt sentences.
Reading its diff, it covers Python (ast, tokenize), shell, Makefile, Dockerfile, YAML, TOML and JavaScript, and skips
Markdown, JSON, JSONL.

## Gaps to close

1. **Fails open.** With no merge base the check prints "skipped" and exits 0. A shallow CI checkout would then pass
   everything. In CI it must fail when `origin/main` is missing.
2. **No count.** Nothing reports how many docstrings and comments a PR added or removed, so the trend and the effect of
   the gate are not measured. Emit the counts in the job summary and in the calibration report.
3. **The review already tells flows the rule (engineering-rules item 18), and 6 of 6 PRs ignored it**, so the gate must
   run in Stage 3 before the push (pre-push), not only in CI, or each violation costs a pipeline run plus a review
   iteration (churn under the end-state rule).
4. **Markdown ledger and plan files** are exempt, correctly, but the bean should confirm that exemption does not let
   code fences in `plans/` and `executions/` be the only place the prose lands.

## Expected gain

Turns a rule broken 6 of 6 times into a gate that fails in the executor turn. Cost: small change to #357 or a follow-up
after it merges.

## Resolution

## Progress (2026-11-27, PR #364 merged as f8adf665)

Delivered by #364 (`scripts/check_self_explaining.py`, `scripts/self_explaining_diff.py`, tests in
`apps/sandbox-executor/tests/test_check_self_explaining.py`):

- Fail closed: no merge base with `origin/main` exits 2 with an error on stderr; the skip notice and its exit-0 path are
  removed.
- Shallow checkout: the merge-base lookup fetches `origin/main` and unshallows, then fails if no merge base results.
- Per-file counts: each violating file gets a path and added docstring/comment count line, then the total; success
  prints the changed-file count.

Not delivered (bean stays in-progress):

1. Counts in the CI job summary and the calibration report: `.github/workflows/test-hygiene.yml` emits no
   `GITHUB_STEP_SUMMARY`.
2. Gate in the executor turn before push (Stage 3, gap 3): no executor or flow change; prompts still cite
   `uv run task lint` only.
3. Ledger text coverage (title, gap 4): the Markdown ledger and plan exemption is unchanged and not verified.

Measured in #364 code files (163 added lines): 0 added docstring lines, 0 added comments without `# why:`, 1 `# why:`
line. No note on bean 0153 needed.

## Progress (2026-11-27T05:12:05Z, PR #375 merged as c1968628)

Delivered via [PR #375](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/375) (`c1968628`, merged
`2026-11-27T05:06:55Z`, gap 3 — Stage 3 pre-push gate):

- Wired `scripts/check_self_explaining.py` into `PrePushSteps.record_branch` in
  `apps/sandbox-executor/src/sandbox_executor/entrypoint/executor/pre_push.py` so executions that add docstrings or
  explanatory comments are refused before sync/push (`self_explaining_violation` row with offending `path:line` output).
- Added rule 10 to `holon-config/prompts/executor.template.md` documenting the pre-push check.
- Verified by `apps/sandbox-executor/tests/test_pre_push_self_explaining.py` (execution `E-1795741267-CLA-CO5.5`:
  `uv run task test` 9530 passed, 7 skipped; `uv run task lint` passed). Worktree `flow-self-explaining-gate-pre-push`
  and its flow/remote branches pruned.

Not delivered yet (bean stays `in-progress`):

1. Counts report (gap 2): `self-explaining-counts-report` (PR #378 merged on `main`, pending its post-merge pass).
2. Markdown ledger/plan coverage verification (gap 4).

## Progress (2026-11-27T05:14:20Z, PR #378 merged as a59ef0d6)

Delivered via [PR #378](https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/378) (`a59ef0d6`, merged
`2026-11-27T05:08:41Z`, gap 2 — counts reporting):

- `scripts/check_self_explaining.py` appends a markdown summary table (checked files, added/removed docstrings and
  non-reason comments) to `GITHUB_STEP_SUMMARY` on pass and failure, and adds `--head REF` / `--counts-json` modes;
  `scripts/self_explaining_diff.py` tracks removed files and lines.
- `apps/sandbox-executor/src/sandbox_executor/calibration/self_explaining_counts.py`, `calibration/generate.py`, and
  `calibration/report.py` emit `## 7. Self-Explaining Code Counts` in Stage 5 calibration reports.
- Verified by `test_check_self_explaining.py`, `test_calibration_report_self_explaining_counts.py`, and
  `test_calibration_regression_merge_main.py` (`uv run task test` 9558 passed, 7 skipped; `uv run task lint` passed in
  `E-1795742983-CLA-CO5.5`). Worktree `flow-self-explaining-counts-report` and its flow/remote branches pruned.

Remaining (bean stays `in-progress`):

1. Markdown ledger/plan coverage verification (gap 4).
