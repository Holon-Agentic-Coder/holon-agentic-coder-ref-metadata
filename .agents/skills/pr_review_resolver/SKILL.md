---
name: pr-review-resolver
description:
  Analyses an existing Pull Request review to determine whether each comment is accurate, justified by the actual code
  diff, and actionable. Fetches the PR diff and existing review comments using the `gh` CLI, evaluates each comment for
  correctness and relevance, and applies the code changes suggested by all valid comments to the current branch and
  commits them. Activate this skill whenever the user asks to audit, validate, or sanity-check the comments left on a
  Pull Request review.
---

# Pull Request Review Resolver Skill

This skill critically evaluates an existing PR review against the actual code diff. It checks whether each review
comment is technically correct, grounded in the diff, proportionate in severity, and accompanied by actionable
recommendations. For every comment that passes the evaluation, it **applies the suggested code changes** to the current
branch and commits them.

## 🛠️ Step-by-Step Execution Guide

Follow these steps when tasked with resolving a Pull Request review:

### Step 1: Verify GitHub CLI Authentication

Ensure the host shell is logged into GitHub by running:

```bash
gh auth status
```

_If authentication fails, instruct the user to run `gh auth login` in their terminal before proceeding._

### Step 2: Fetch the PR Diff and Existing Review Comments

Fetch all the material needed to perform the evaluation:

```bash
# Fetch the title and description
gh pr view <pr_url_or_number> --json title,body

# Fetch the raw code diff
gh pr diff <pr_url_or_number>

# Fetch all existing review comments (reviews with body text)
gh pr view <pr_url_or_number> --json reviews --jq '.reviews[] | select(.body != "") | {author: .author.login, state: .state, body: .body, submittedAt: .submittedAt}'
```

### Step 3: Evaluate Each Comment

For each comment found in the existing reviews, internally evaluate it through the following lenses:

#### 3a. Diff Grounding

Is the comment anchored to a real change in the diff? Verify that the file, line range, or code pattern cited by the
comment actually exists in the diff. Comments referencing code **not present** in the diff are **invalid**.

#### 3b. Technical Accuracy

Is the technical claim correct? Evaluate whether the described problem is genuinely caused by the code as written.
Technically incorrect claims are **invalid**.

#### 3c. Actionability

Does the comment include a concrete recommendation or proposed code change? Vague comments with no clear action are
**invalid**.

#### 3d. Relevance

Is this comment in scope for the PR? Comments flagging pre-existing issues unrelated to the current changeset are **out
of scope** — do not apply them.

### Step 4: Apply Changes from Valid Comments

For every comment that passes all checks (grounded, accurate, actionable, and in scope), apply the suggested code change
directly to the working tree:

- Use the proposed code diff or recommendation from the comment as the specification for the change.
- Make the minimal edit required — do not refactor or touch code outside the scope of the comment.
- If a comment's suggestion conflicts with another valid comment's suggestion on the same lines, apply them together and
  resolve the conflict sensibly.
- Skip any comment that failed one or more checks — do not apply changes from unverified or inaccurate feedback.

> [!IMPORTANT] Only apply changes from comments that pass **all** evaluation checks. Never apply changes from
> ungrounded, inaccurate, or out-of-scope comments.

### Step 5: Commit the Applied Changes

Once all valid changes have been applied, stage and commit them to the current branch:

```bash
git add -A
git commit -m "fix: apply validated PR review suggestions from <pr_url_or_number>

Changes applied:
- <bullet list of applied comment titles>

Skipped (invalid/out of scope):
- <bullet list of skipped comment titles>"
```

Do **not** push to the remote unless the user explicitly instructs you to do so.
