---
# holon-agentic-coder-ref-metadata-0261
title: "Deduplicate and streamline PR review evaluation line in consensus report"
status: todo
type: bug
priority: normal
tags:
  - flow
  - review
  - review-report
  - token-reduction
  - holon-agentic-coder
created_at: 2026-11-09T07:42:00Z
updated_at: 2026-11-09T07:42:00Z
---

## Problem

In `apps/sandbox-executor/src/sandbox_executor/review_report.py` (`_evaluation`, lines 664–676):

```python
def _evaluation(repo_dir: str, target: str, consensus_data: Mapping[str, Any], data: ReviewData, title: str) -> str:
    """The evaluation paragraph: title, commit, base branch, finding counts, CI state and mergeability."""
    mergeability = _mergeability_word(consensus_data)
    note = _inline(consensus_data.get("mergeability_note"), MAX_REASON_CHARS)
    base = _inline(consensus_data.get("base_branch") or "main", MAX_PATH_CHARS)
    link = _pr_link(repo_dir, target, consensus_data)
    subject = link if title == target and link == f"`{target}`" else f"{title} ({link})"
    return (
        f"Reviewed {subject} at "
        f"`{_target_commit(repo_dir, consensus_data)}` against `{base}`: {_severity_counts(data.findings)}; "
        f"CI {_ci_state(consensus_data.get('ci_checks') or {})}; mergeability {mergeability}"
        + (f" ({note})." if note else ".")
    )
```

1. **Double Branch Ref Formatting**:
   - `resolve_report_title()` looks for `intent_data.get("title")`. Standard intent JSON specifications define `slug`
     and `description` (not `title`), so it falls back to the full hierarchical branch ref:
     `I-1794205862-.../P-1794205877-.../E-1794206943-.../_`.
   - `_pr_link()` resolves the target branch to markdown link `[I-.../_](https://github.com/.../pull/151)`.
   - `_evaluation()` joins them into `f"{title} ({link})"`, generating:
     `Reviewed I-.../_ ([I-.../_](https://github.com/.../pull/151)) at 12366f1e... against main: ...` This duplicates
     the 120-character branch ref twice consecutively.
2. **Context Redundancy on GitHub PR**:
   - When this consensus comment is posted to GitHub, it appears directly inside the PR conversation. The PR header
     already displays the head branch, the base branch (`main`), and the current commit SHA.
   - Repeating the full raw branch ref twice, plus the commit SHA and target branch, creates visual noise and wastes
     tokens.

## Decision

1. **Fallback to `slug` or PR title in `resolve_report_title()`**:
   - In `resolve_report_title()`, check `intent_data.get("title")`, then `intent_data.get("slug")`, then `target.title`,
     before falling back to the raw branch ref.
2. **Deduplicate `subject` in `_evaluation()`**:
   - If `link` already contains or links `title`, or if `title` is identical to `target` / `head_branch`, do not format
     as `f"{title} ({link})"`. Render `link` directly or use a clean subject label (e.g. `[PR #151](url)` or
     `[<slug>](url)`).
3. **Streamline Evaluation Sentence**:
   - For comments posted to GitHub PRs, format concisely: `Reviewed commit \`{short_commit}\` against \`{base}\`:
     {severity_counts}; CI {ci}; mergeability {mergeability}.`
   - Use short commit SHA (8 characters) rather than the 40-character full commit SHA.
4. **Tests**:
   - Update `apps/sandbox-executor/tests/test_review_report.py` to assert that:
     - No report duplicates the branch name in `{title} ({link})`.
     - Intent `slug` is used when `title` is absent.
     - The rendered evaluation paragraph is clean, deduplicated, and concise.

## Scope

- `apps/sandbox-executor/src/sandbox_executor/review_report.py`
- `apps/sandbox-executor/tests/test_review_report.py`
