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
4. **Existing Comment Audit & Resolution**: In addition to new code review passes, inspect pre-existing review comments
   posted on the GitHub PR. Evaluate each comment for diff grounding, technical accuracy, actionability, and scope. If
   verified to be true, apply the resolution, commit, and push the fix.
5. **Temporary Files & Intermediate Artifacts Location**: All temporary files, diff dumps (e.g.,
   `.subagent/pr<number>.diff`), draft review bodies (`.subagent/review_body.md`), and dry-run reports
   (`.subagent/dry_run_review_iter_<iteration>_{short_git_commit}.md`) **MUST be placed into the `.subagent/`
   directory** (git ignored). Never write intermediate files to `scratch/` or other root folders. Prior to execution,
   read `.subagent/coordination.json` (if it exists) to fetch user-rejected recommendations and active constraints.

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

#### Phase A0: Audit & Resolve Pre-existing PR Comments (Iteration 1 Only)

Before launching the new dry-run code review pass on Iteration 1:

1. Check for pre-existing review comments on the target PR (`gh pr view <pr> --json reviews`).
2. If actionable review comments exist from human reviewers or previous review passes:
   - Spawn a `pr_resolver` subagent to execute `pr-review-resolver` on `<pr_url_or_number>`.
   - The resolver will critically evaluate each comment for diff grounding, technical accuracy, actionability, and
     scope.
   - If any comment is verified to be true and valid, apply the fix, commit
     (`fix: resolve verified pre-existing PR review comments`), and push (`git push origin <branch_name>`).

#### Phase A: Run Reviewer Subagent (Dry-Run Mode)

Spawn a subagent using `invoke_subagent`:

- **TypeName**: `pr_reviewer`
- **Role**: `PR Reviewer (Iteration <iteration>)`
- **Model**: `inherit` (Inherit the parent agent's model for all dry-run review passes).
- **Prompt Instructions**:
  > Load and execute the `pr-reviewer` skill for `<pr_url_or_number>` in **Dry-Run Mode (`--dry-run`)** with
  > **Single-Agent Mode** enabled.
  >
  > 1. Fetch PR metadata, diff, and existing PR review comments via `gh`.
  > 2. Evaluate code changes against `.agents/prompts/pr_review_prompt.md`.
  > 3. **Single-Agent Execution**: Do NOT spawn 3 independent subagents. Perform the PR review evaluation directly in
  >    this single agent pass to minimize token consumption.
  > 4. **Conditional CI Check**: Verify CI build status via `gh pr checks` **ONLY IF** zero Critical (🔴) or Important
  >    (🟡) issues are found in the code review (defer checking build status if code changes are required).
  > 5. Do **NOT** post comments to GitHub (Dry-Run mode is ON).
  > 6. Save the detailed review findings and report to a markdown file:
  >    `.subagent/dry_run_review_iter_<iteration>_{short_git_commit}.md` (creating the directory if needed) so the user
  >    can review the dry-run feedback.
  > 7. Return a concise report containing:
  >    - Overall Verdict (`APPROVED`, `CHANGES_REQUESTED`, or `COMMENT`).
  >    - Total number of Critical, Important, and Nit findings.
  >    - Path to the generated dry run review markdown file
  >      (`.subagent/dry_run_review_iter_<iteration>_{short_git_commit}.md`).

Wait for the subagent to complete and inspect its report.

---

#### Phase B: Evaluate Exit Conditions & Post Final Review

1. **Approval / Clean Pass**:
   - The loop terminates with approval **ONLY IF**:
     1. The reviewer subagent verdict is **`APPROVED`** (or zero actionable CRITICAL/IMPORTANT issues were found).
     2. **ALL GitHub Actions CI checks (`gh pr checks <pr>`) pass cleanly** with no failing jobs.
   - **Post Final Review to GitHub (Real Mode)**: Spawn a final `pr_reviewer` subagent in **Real Mode** (using model
     `inherit`) with **Ensemble Consensus Mode** enabled.
     - **Prompt Instructions**:
       > Load and execute the `pr-reviewer` skill for `<pr_url_or_number>` in **Real Mode** using the **3-Agent Ensemble
       > Consensus Model**. Spawn 3 independent subagents, merge their consensus findings, and post the final review to
       > GitHub.
   - **STOP THE LOOP**.
   - Output success message:
     `PR review loop completed successfully! Final review posted to GitHub and all CI builds are passing.`

2. **Max Iterations Cap**:
   - If `iteration >= max_iterations` and issues remain:
   - **Post Final Review to GitHub (Real Mode)**: Spawn a final `pr_reviewer` subagent in **Real Mode** (using model
     `inherit`) with **Ensemble Consensus Mode** enabled to post the single final review comment detailing remaining
     issues to GitHub PR via `gh pr review`.
   - **STOP THE LOOP**.
   - Output a warning:
     `Reached maximum iteration cap (<max_iterations>). Posted final review comment to GitHub. Stopping loop.`

---

#### Phase C: Run Resolver Subagent

If changes were requested or actionable issues exist (from new review findings or existing PR comments):

Spawn a subagent using `invoke_subagent`:

- **TypeName**: `pr_resolver`
- **Role**: `PR Review Resolver (Iteration <iteration>)`
- **Model**: `inherit` (Inherit the parent agent's model for all resolution passes).
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
