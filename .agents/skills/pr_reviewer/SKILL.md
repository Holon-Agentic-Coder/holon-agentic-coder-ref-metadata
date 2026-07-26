---
name: pr-reviewer
description:
  Automates Pull Request reviews using a multi-agent ensemble consensus model. It fetches the PR description and diff
  using the `gh` CLI, executes 3 independent subagent reviews, synthesizes a consolidated consensus report, and posts
  the compiled feedback to the PR. Activate this skill whenever the user provides a Pull Request URL or number and asks
  for a review.
---

# Pull Request Reviewer Skill

This skill allows any coding agent to automatically review a Pull Request using the `gh` CLI, a multi-role review
prompt, and an **Ensemble Consensus Model (3 Independent Reviewer Subagents)** to eliminate non-deterministic flakiness
and maximize detection of genuine code issues.

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

### Step 3: Run Multi-Agent Ensemble Review (3 Independent Passes)

To eliminate single-pass LLM variance, flakiness, and missed edge cases, execute **3 independent review passes** (via
subagents or isolated subagent contexts):

1. **Spawn 3 Independent Reviewer Subagents**:
   - Spawn subagents (`Reviewer Subagent 1`, `Reviewer Subagent 2`, `Reviewer Subagent 3`) concurrently in parallel
     using a subagent delegation tool (e.g. `invoke_subagent`).
   - Each reviewer subagent receives the PR Title, Description, Code Diff, and system prompt from
     `.agents/prompts/pr_review_prompt.md`.
   - Each reviewer subagent operates in an isolated context without visibility into the other reviewers' outputs.
   - **Subagent Fault Tolerance & Timeout Strategy**: If a subagent fails or times out (e.g. due to rate limits or API
     error), attempt 1 retry. If a subagent fails after retry, record its status as `FAILED` in the voting breakdown;
     the overall PR review cannot receive an `APPROVED` verdict since strict 3/3 unanimous approval is required.

2. **Per-Reviewer Multi-Role Evaluation**: Each subagent evaluates the PR through activated specialist roles and
   categorizes findings using standard severity levels:
   - 🔴 **CRITICAL / BLOCKER**
   - 🟡 **IMPORTANT / IMPROVEMENT**
   - 🟢 **NIT / OPTIONAL**
   - ✅ **APPROVED / PASS**

> [!IMPORTANT] Ensure positive findings, praise, and explicit confirmations of well-designed changes are categorized as
> **`✅ APPROVED / PASS`** (or **`✅ APPROVED`**), not `🟢 NIT`.

### Step 3.1: Ensemble Consensus Synthesis & Deduplication

Once all 3 reviewer subagents complete their evaluations, synthesize a single **Consolidated Review Report**:

1. **Deduplicate & Union Findings**:
   - Merge duplicate findings flagged by multiple reviewers into single, clear review items, highlighting multi-reviewer
     agreement (e.g. `[Flagged by Reviewer 1 & 3]`).
   - Union all unique findings across all severity levels (🔴 **CRITICAL / BLOCKER**, 🟡 **IMPORTANT / IMPROVEMENT**, 🟢
     **NIT / OPTIONAL**, and ✅ **APPROVED / PASS**) from all 3 passes.
2. **Consolidated Dynamic Role Matrix**:
   - Aggregate role activations across all 3 review passes to form a single master Dynamic Role Activation Matrix.

### Step 3.5: Consensus Verdict & Deferred CI Verification

> [!NOTE] **Ensemble Rule**: A PR can receive an overall **`APPROVED`** verdict **ONLY IF ALL THREE (3/3) independent
> review passes** return zero Critical (🔴) or Important (🟡) issues AND all GitHub Actions CI checks pass cleanly.

1. **If ANY Reviewer Subagent identified Critical (🔴) or Important (🟡) issues**:
   - **DO NOT** execute `gh pr checks`. Skip checking build status.
   - Set the overall ensemble review verdict to **`CHANGES_REQUESTED`**.

2. **If ALL THREE (3/3) Reviewer Subagents found NO Critical (🔴) or Important (🟡) issues (Ready to Approve)**:
   - Fetch the status of automated CI build and test checks for the target PR:
     ```bash
     gh pr checks <pr_url_or_number>
     ```
   - **If ALL CI checks pass cleanly**:
     - Set the overall ensemble review verdict to **`APPROVED`**.
   - **If any CI check has failed or broken**:
     1. Fetch the failure logs using `gh run view <run_id> --log-failed`.
     2. Flag the CI build failure as a **🔴 CRITICAL / BLOCKER** finding in the review body.
     3. Set the review verdict to **`CHANGES_REQUESTED`** (or `--comment` if author self-review). The PR CANNOT receive
        an `APPROVED` verdict until all CI checks pass cleanly.

### Step 3.6: Append Agent, Model & Ensemble Voting Breakdown Footer

Before writing the review to the temp file, append a footer that details the ensemble voting breakdown, agent identity,
and LLM model:

```markdown
---

### 🗳️ Ensemble Review Breakdown

- **Reviewer 1**: `<APPROVED | CHANGES_REQUESTED | COMMENT | FAILED | TIMEOUT>`
- **Reviewer 2**: `<APPROVED | CHANGES_REQUESTED | COMMENT | FAILED | TIMEOUT>`
- **Reviewer 3**: `<APPROVED | CHANGES_REQUESTED | COMMENT | FAILED | TIMEOUT>`
- **Ensemble Consensus Verdict**: `<APPROVED | CHANGES_REQUESTED | COMMENT>`

> 🤖 **Reviewed by**: `<agent-name>` (3-Agent Ensemble) · **Model**: `<llm-model>`
```

- **`<agent-name>`**: The primary agent executing the ensemble review (e.g. `antigravity-agent`, `pi-agent`,
  `claude-agent`). Determine this from the `HOLON_ROLE` or `AGENT_NAME` environment variable if available, otherwise use
  the agent's self-identified name from your system context.
- **`<llm-model>`**: The LLM model identifier used for the review passes (e.g. `gemini-3.5-flash`, `claude-sonnet-4-5`).
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
  - Submit the review to GitHub using the flag matching your overall ensemble verdict:
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

_Note: GitHub disallows users from approving or requesting changes on their own PRs. If `--approve` or
`--request-changes` returns an error because the PR author is the authenticated user, fallback to `--comment`._

### Step 5: Clean Up

Remove any temporary files created in the `todo/` directory:

```bash
rm -f todo/review_body.md
```
