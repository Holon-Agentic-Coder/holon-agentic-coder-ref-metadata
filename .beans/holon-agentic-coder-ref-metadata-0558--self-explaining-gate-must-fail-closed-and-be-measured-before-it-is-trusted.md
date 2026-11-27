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
updated_at: 2026-11-26T23:46:38Z
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
