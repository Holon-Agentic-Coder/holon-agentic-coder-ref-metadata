---
name: pr-review-loop
description:
  Automates the iterative PR review and resolution process by running `pr-reviewer` and `pr-review-resolver` in fresh
  subagent contexts until the PR is approved or the maximum iteration cap (default 10) is reached. Activate this skill
  whenever the user asks to run an autonomous review loop, auto-fix PR issues continuously, or execute
  `/pr-review-loop`.
---

# Autonomous PR Review & Resolve Loop Skill

This skill orchestrates an autonomous feedback loop that continuously reviews a Pull Request and resolves flagged
issues. To ensure clean context and prevent prompt degradation across multiple iterations, **each review step and
resolution step is executed in a dedicated, fresh subagent**.

---

## 📐 Architecture & Principles

1. **Context Isolation**: Each review pass and resolution pass runs in a newly spawned subagent with fresh context.
2. **Termination Safety**: The loop terminates when the PR review returns **`APPROVED`** (or zero actionable issues
   remain), or when the **max iteration cap** (default: `10`) is reached.
3. **Remote Sync**: After each resolution pass, changes are committed and pushed to the remote feature branch so GitHub
   PR diffs update dynamically for subsequent review passes.

---

## 🛠️ Step-by-Step Execution Guide

Follow these steps when executing the `pr-review-loop` skill:

### Step 1: Parse Parameters

Determine the target Pull Request and iteration limit from the user's request:

- **`<pr_url_or_number>`**: GitHub PR URL or PR number (e.g.,
  `https://github.com/Holon-Agentic-Coder/holon-agentic-coder-ref/pull/25` or `25`).
- **`<max_iterations>`**: Maximum number of review-resolve cycles (default: `10`).

Verify GitHub CLI authentication before starting:

```bash
gh auth status
```

---

### Step 2: Main Loop Execution

Initialize iteration counter `iteration = 1`.

#### 🔁 Loop Body (While `iteration <= max_iterations`):

#### Phase A: Run Reviewer Subagent (Dry-Run Mode)

Spawn a subagent using `invoke_subagent`:

- **TypeName**: `pr_reviewer`
- **Role**: `PR Reviewer (Iteration <iteration>)`
- **Prompt Instructions**:
  > Load and execute the `pr-reviewer` skill for `<pr_url_or_number>` in **Dry-Run Mode (`--dry-run`)**.
  >
  > 1. Fetch PR metadata and diff via `gh`.
  > 2. Verify CI build status via `gh pr checks`.
  > 3. Evaluate changes against `.agents/prompts/pr_review_prompt.md`.
  > 4. Do **NOT** post comments to GitHub (Dry-Run mode is ON).
  > 5. Return a concise report containing:
  >    - Overall Verdict (`APPROVED`, `CHANGES_REQUESTED`, or `COMMENT`).
  >    - Total number of Critical, Important, and Nit findings.

Wait for the subagent to complete and inspect its report.

---

#### Phase B: Evaluate Exit Conditions & Post Final Review

1. **Approval / Clean Pass**:
   - The loop terminates with approval **ONLY IF**:
     1. The reviewer subagent verdict is **`APPROVED`** (or zero actionable CRITICAL/IMPORTANT issues were found).
     2. **ALL GitHub Actions CI checks (`gh pr checks <pr>`) pass cleanly** with no failing jobs.
   - **Post Final Review to GitHub (Real Mode)**: Spawn a final `pr_reviewer` subagent in **Real Mode** to post the
     single final compiled review comment to GitHub PR via `gh pr review`.
   - **STOP THE LOOP**.
   - Output success message:
     `PR review loop completed successfully! Final review posted to GitHub and all CI builds are passing.`

2. **Max Iterations Cap**:
   - If `iteration >= max_iterations` and issues remain:
   - **Post Final Review to GitHub (Real Mode)**: Spawn a final `pr_reviewer` subagent in **Real Mode** to post the
     single final review comment detailing remaining issues to GitHub PR via `gh pr review`.
   - **STOP THE LOOP**.
   - Output a warning:
     `Reached maximum iteration cap (<max_iterations>). Posted final review comment to GitHub. Stopping loop.`

---

#### Phase C: Run Resolver Subagent

If changes were requested or actionable issues exist:

Spawn a subagent using `invoke_subagent`:

- **TypeName**: `pr_resolver`
- **Role**: `PR Review Resolver (Iteration <iteration>)`
- **Prompt Instructions**:
  > Load and execute the `pr-review-resolver` skill for `<pr_url_or_number>`.
  >
  > 1. Fetch PR diff and existing review comments via `gh`.
  > 2. Critically evaluate each comment for diff grounding, technical accuracy, actionability, and scope relevance.
  > 3. Apply changes from valid comments to the working tree.
  > 4. Commit applied changes with message: `fix: apply validated PR review suggestions (Iteration <iteration>)`.
  > 5. Push local commits to remote feature branch (`git push origin <branch_name>`) so GitHub PR diff updates for the
  >    next review pass.
  > 6. Return a summary of applied fixes and skipped comments.

Wait for the subagent to complete and inspect its report.

---

#### Phase D: Next Iteration

Increment `iteration = iteration + 1` and proceed to the next cycle in Step 2.

---

### Step 3: Format & Report Final Summary

Once the loop terminates, format all findings into a clean summary table for the user:

```markdown
### 🔄 PR Review Loop Execution Summary

- **PR Target**: `<pr_url_or_number>`
- **Total Iterations Completed**: `<total_iterations>` / `<max_iterations>`
- **Final PR Status**: `APPROVED` / `CHANGES_REQUESTED` (Cap Reached)

#### Cycle History:

| Iteration | Review Verdict    | Issues Found | Resolutions Applied | Commit Pushed |
| --------- | ----------------- | ------------ | ------------------- | ------------- |
| 1         | CHANGES_REQUESTED | 3            | 3 applied           | `a1b2c3d`     |
| 2         | APPROVED          | 0            | 0 applied           | N/A           |
```
