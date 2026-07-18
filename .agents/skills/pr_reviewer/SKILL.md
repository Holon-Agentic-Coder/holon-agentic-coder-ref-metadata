---
name: pr-reviewer
description:
  Automates Pull Request reviews using a comprehensive multi-role prompt. It fetches the PR description and diff using
  the `gh` CLI, executes the multi-role review, and posts the compiled feedback back to the PR. Activate this skill
  whenever the user provides a Pull Request URL or number and asks for a review.
---

# Pull Request Reviewer Skill

This skill allows any coding agent to automatically review a Pull Request using the `gh` CLI and the project's
multi-role review prompt.

## 🛠️ Step-by-Step Execution Guide

Follow these steps when tasked with reviewing a Pull Request:

### Step 1: Verify GitHub CLI Authentication

Ensure the host shell is logged into GitHub by running:

```bash
gh auth status
```

_If authentication fails, instruct the user to run `gh auth login` in their terminal before proceeding._

### Step 2: Fetch Pull Request Metadata & Code Diff

Fetch the PR description and diff using the following commands:

```bash
# Fetch the title and description
gh pr view <pr_url_or_number> --json title,body

# Fetch the raw code diff
gh pr diff <pr_url_or_number>
```

### Step 3: Run the Multi-Role Review

Read the system prompt from the repository's `.agents/prompts/pr_review_prompt.md` file.

Feed the PR Title, Description, and Diff to your context, and evaluate the changes through each of the activated
specialist roles.

### Step 4: Post the Review Back to GitHub

Write your review output to a temporary file (e.g., `todo/review_body.md`) to prevent shell character escaping issues.
Submit the review using the flag matching your overall verdict:

- **APPROVED**:
  ```bash
  gh pr review <pr_url_or_number> --approve -F todo/review_body.md
  ```
- **CHANGES REQUESTED**:
  ```bash
  gh pr review <pr_url_or_number> --request-changes -F todo/review_body.md
  ```
- **COMMENT**:
  ```bash
  gh pr review <pr_url_or_number> --comment -F todo/review_body.md
  ```

### Step 5: Clean Up

Remove any temporary files created in the `todo/` directory:

```bash
rm todo/review_body.md
```
