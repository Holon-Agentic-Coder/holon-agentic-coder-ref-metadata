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

### Step 2.5: Verify GitHub Actions CI Checks

Fetch the status of automated CI build and test checks for the target PR:

```bash
gh pr checks <pr_url_or_number>
```

> [!CRITICAL] **Mandatory CI Build Requirement**: A Pull Request **MUST NOT** be approved if any automated GitHub
> Actions CI check is failing or broken (e.g. failing unit tests, build errors, or lint failures). If any CI check has
> failed:
>
> 1. Fetch the failure logs using `gh run view <run_id> --log-failed`.
> 2. Flag the CI build failure as a **🔴 CRITICAL / BLOCKER** finding in the review body.
> 3. Set the review verdict to **`CHANGES_REQUESTED`** (or `--comment` if author self-review). The PR CANNOT receive an
>    `APPROVED` verdict until all CI checks pass cleanly.

### Step 3: Run the Multi-Role Review

Read the system prompt from the repository's `.agents/prompts/pr_review_prompt.md` file.

Feed the PR Title, Description, and Diff to your context, and evaluate the changes through each of the activated
specialist roles. Categorize findings using the standard severity levels:

- 🔴 **CRITICAL / BLOCKER**
- 🟡 **IMPORTANT / IMPROVEMENT**
- 🟢 **NIT / OPTIONAL**
- ✅ **APPROVED / PASS**

> [!IMPORTANT] Ensure positive findings, praise, and explicit confirmations of well-designed changes are categorized as
> **`✅ APPROVED / PASS`** (or **`✅ APPROVED`**), not `🟢 NIT`.

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

### Step 4: Post the Review Back to GitHub (Real Mode vs Dry-Run Mode)

Check if **Dry-Run Mode** is enabled (e.g. via `--dry-run` parameter or loop instruction):

- **If Dry-Run Mode is ON**:
  - **DO NOT** execute `gh pr review`.
  - Skip posting comments to GitHub to prevent PR discussion thread clutter during intermediate loop iterations.
  - Output the structured review findings and verdict strictly to local context/logs for the resolver subagent.

- **If Real Mode is ON (Default / Final Pass)**:
  - Write your review output to a temporary file (`todo/review_body.md`) to prevent shell character escaping issues.
  - Submit the review to GitHub using the flag matching your overall verdict:
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

_Note: GitHub disallows users from approving their own PRs. If `--approve` returns an error because the PR author is the
authenticated user, fallback to `--comment`._

### Step 5: Clean Up

Remove any temporary files created in the `todo/` directory:

```bash
rm -f todo/review_body.md
```
