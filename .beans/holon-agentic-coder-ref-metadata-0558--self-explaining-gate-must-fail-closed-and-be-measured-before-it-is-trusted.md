---
# holon-agentic-coder-ref-metadata-0558
title: "Self-explaining gate (#357): fail closed in CI, cover ledger text, and report per-PR counts"
status: todo
type: task
priority: high
tags:
  - pipeline
  - coding-standards
  - self-explaining-code
  - holon-agentic-coder
created_at: 2026-11-27T00:30:00Z
updated_at: 2026-11-27T00:30:00Z
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
