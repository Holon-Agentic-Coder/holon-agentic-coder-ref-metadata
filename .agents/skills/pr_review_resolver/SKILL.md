---
name: pr-review-resolver
description:
  Analyses an existing Pull Request review to determine whether each comment is accurate, justified by the actual code
  diff, and actionable. Fetches the PR diff and existing review comments using the `gh` CLI, evaluates each comment for
  correctness and relevance, applies the code changes suggested by all valid comments to the current branch, commits
  them, and posts an audit summary back to the PR. Activate this skill whenever the user asks to audit, validate, or
  sanity-check the comments left on a Pull Request review.
---

# Pull Request Review Resolver Skill

This skill critically evaluates an existing PR review against the actual code diff. It checks whether each review
comment is technically correct, grounded in the diff, proportionate in severity, and accompanied by actionable
recommendations. For every comment that passes the audit, it **applies the suggested code changes** to the current
branch and commits them. It then posts a full audit summary back to the PR as a comment.

## 🛠️ Step-by-Step Execution Guide

Follow these steps when tasked with resolving a Pull Request review:

### Step 1: Verify GitHub CLI Authentication

Ensure the host shell is logged into GitHub by running:

```bash
gh auth status
```

_If authentication fails, instruct the user to run `gh auth login` in their terminal before proceeding._

### Step 2: Fetch the PR Diff and Existing Review Comments

Fetch all the material needed to perform the audit:

```bash
# Fetch the title and description
gh pr view <pr_url_or_number> --json title,body

# Fetch the raw code diff
gh pr diff <pr_url_or_number>

# Fetch all existing review comments (reviews with body text)
gh pr view <pr_url_or_number> --json reviews --jq '.reviews[] | select(.body != "") | {author: .author.login, state: .state, body: .body, submittedAt: .submittedAt}'
```

### Step 3: Run the Audit Analysis

For each comment found in the existing reviews, evaluate it through the following lenses:

#### 3a. Diff Grounding

- **Is the comment anchored to a real change in the diff?** Verify that the file, line range, or code pattern cited by
  the comment actually exists in the diff.
- Flag any comment that references code or behaviour **not present** in the diff as **⚠️ UNGROUNDED**.

#### 3b. Technical Accuracy

- **Is the technical claim correct?** Evaluate whether the described problem (e.g. "raises `StopIteration` instead of
  `AssertionError`") is genuinely caused by the code as written, or whether it is factually incorrect.
- Flag technically incorrect claims as **❌ INACCURATE**.

#### 3c. Severity Proportionality

- **Is the severity label appropriate?** Compare the assigned severity (CRITICAL, IMPORTANT, NIT) against the actual
  risk surface of the issue (security, data loss, test failure, style preference, etc.).
- Flag over-inflated or under-reported severities as **🔄 MISCLASSIFIED**.

#### 3d. Actionability

- **Does the comment tell the author what to do?** Each non-NIT comment should include a concrete recommendation or
  proposed code change.
- Flag vague or recommendation-free comments as **💬 NOT ACTIONABLE**.

#### 3e. Relevance

- **Is this comment in scope for the PR?** Comments that flag pre-existing issues unrelated to the current changeset
  should be noted as **🔍 OUT OF SCOPE** (not necessarily wrong, but the author may not be responsible for fixing them).

### Step 4: Compose the Audit Report

Structure your output using the format below:

---

#### 📋 PR Review Audit — Summary

| Comment                      | Grounded? | Accurate? | Severity OK? | Actionable? | In Scope? | Verdict                            |
| :--------------------------- | :-------: | :-------: | :----------: | :---------: | :-------: | :--------------------------------- |
| [Short title of the comment] |   ✅/⚠️   |   ✅/❌   |    ✅/🔄     |    ✅/💬    |   ✅/🔍   | [VALID / NEEDS REVISION / INVALID] |

---

#### 🔎 Detailed Findings

For each comment that is **not fully valid**, provide:

- **Comment**: Quote or summarise the original comment.
- **Issues Found**: List which checks failed and why.
- **Suggested Revision**: Provide a corrected or improved version of the comment, or recommend removing it if invalid.

---

#### ✅ Valid Comments

List comments that passed all checks, with a one-line summary confirming their correctness.

---

#### 🏁 Audit Verdict

Provide an overall assessment:

- **✅ REVIEW ACCURATE**: All comments are grounded, technically correct, and actionable. The review can be trusted
  as-is.
- **⚠️ REVIEW PARTIALLY ACCURATE**: Most comments are valid, but some require revision. Note which comments the author
  should revisit.
- **❌ REVIEW UNRELIABLE**: A significant number of comments are inaccurate or ungrounded. Recommend the reviewer revise
  their feedback before the author acts on it.

### Step 5: Apply Changes from Valid Comments

For every comment that received a **VALID** verdict in the audit (i.e. it passed all five checks: grounded, accurate,
proportionate, actionable, and in scope), apply the suggested code change directly to the working tree:

- Use the proposed code diff or recommendation from the comment as the specification for the change.
- Make the minimal edit required — do not refactor or touch code outside the scope of the comment.
- If a comment's suggestion conflicts with another valid comment's suggestion on the same lines, apply them together and
  resolve the conflict sensibly, noting the resolution in the audit report.
- Skip any comment marked **NEEDS REVISION** or **INVALID** — do not apply changes from unverified or inaccurate
  feedback.

> [!IMPORTANT] Only apply changes from comments that are **fully valid** (all five audit checks pass). Never apply
> changes from UNGROUNDED, INACCURATE, or OUT OF SCOPE comments.

### Step 6: Commit the Applied Changes

Once all valid changes have been applied, stage and commit them to the current branch:

```bash
git add -A
git commit -m "fix: apply validated PR review suggestions from <pr_url_or_number>

Changes applied from the following valid review comments:
- <bullet list of applied comment titles>

Skipped (failed audit): <bullet list of skipped comment titles>"
```

Do **not** push to the remote unless the user explicitly instructs you to do so.

### Step 7: Post the Audit Back to GitHub

Write the audit report to a temporary file to prevent shell character escaping issues, then post it as a PR comment. The
report should include a section listing which comments were applied and which were skipped:

```bash
gh pr comment <pr_url_or_number> -F todo/resolve_body.md
```

### Step 8: Clean Up

Remove any temporary files created in the `todo/` directory:

```bash
rm todo/resolve_body.md
```
