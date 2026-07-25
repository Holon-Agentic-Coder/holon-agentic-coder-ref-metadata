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

### Step 3.5: Append Agent & Model Footer

Before writing the review to the temp file, append a footer that identifies **who** performed the review and **which LLM
model** was used. This provides full traceability on every review comment posted to GitHub.

The footer must be appended as the last section of the review body:

```markdown
---

> 🤖 **Reviewed by**: `<agent-name>` · **Model**: `<llm-model>`
```

- **`<agent-name>`**: The name of the agent that executed this review (e.g. `antigravity-agent`, `pi-agent`,
  `claude-agent`). Determine this from the `HOLON_ROLE` or `AGENT_NAME` environment variable if available, otherwise use
  the agent's self-identified name from your system context.
- **`<llm-model>`**: The LLM model identifier used during the review (e.g. `gemini-3.5-flash`, `claude-sonnet-4-5`).
  Determine this from the `MODEL_NAME` environment variable if set, otherwise use the model name you know yourself to be
  running as.

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
