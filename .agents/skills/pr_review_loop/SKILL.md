---
name: pr-review-loop
description:
  Automates the iterative PR review and resolution process by running `pr-reviewer` and `pr-review-resolver` in fresh
  subagent contexts until the PR is approved or the maximum iteration cap (default 25) is reached. Activate this skill
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
2. **Termination Safety & Consensus Integrity**: The loop terminates when the 3-agent ensemble consensus review returns
   **`APPROVED`** (zero Critical or Important issues remain; only Nit/Optional findings allowed) AND all CI checks pass
   cleanly, or when the **max iteration cap** (default: `25`, configurable) is reached. **If the consensus agent
   reviewers flag any Critical or Important issues, the review results MUST NOT be posted to the PR on GitHub.** The
   loop must resolve the issues, push the fixes, and run the review again. Review results are **strictly posted to
   GitHub only when there are no more Critical or Important issues left to action** (or when the max iteration cap is
   reached).
3. **Deterministic Convergence (Never Pause)**: The loop has **no pause state and never asks for guidance mid-flight**.
   The only exits are a clean consensus approval posted to the PR, or the **max iteration cap** with a final review
   posted. If the exact same issue is flagged across 3 consecutive iterations with no diff change, or if reviewers
   oscillate between conflicting recommendations, the loop climbs the **Convergence Escalation Ladder** in
   [Phase B](#phase-b-evaluate-exit-conditions--post-final-review) instead of stopping: re-sync, re-adjudicate the
   finding against primary sources, apply the union of the competing recommendations, rule false findings out in writing
   in `.subagent/coordination.json`, or defer an out-of-scope finding to a new bean. Iterations are spent resolving, not
   waiting.
4. **Drift Self-Healing (Out-Of-Sync State Is Work, Not A Blocker)**: Divergence between what the loop expects and what
   the repository and PR actually contain -- a new commit pushed by someone else, a parallel agent session editing the
   same worktree, an unexpectedly dirty tree, a stale cached diff, a rejected push, CI that moved from `pending` to
   `failure` -- is always reconciled and then worked, never reported as a blocker and never turned into a stop. The
   reconciliation procedure is [Phase A0.5](#phase-a05-re-sync--consolidate-drifted-state-every-iteration), run before
   every review pass. Consolidating another author's verified in-flight edits (committing them on top, with attribution)
   is the default; discarding them is not.
5. **Remote Sync**: After each resolution pass, changes are committed and pushed to the remote feature branch so GitHub
   PR diffs update dynamically for subsequent review passes. Drift is integrated with `git pull --rebase`, never with a
   force-push.
6. **Existing Comment Audit & Resolution**: In addition to new code review passes, inspect pre-existing review comments
   posted on the GitHub PR. Evaluate each comment for diff grounding, technical accuracy, actionability, and scope. If
   verified to be true, apply the resolution, commit, and push the fix.
7. **Temporary Files & Intermediate Artifacts Location**: All temporary files, diff dumps (e.g.,
   `.subagent/pr<number>.diff`), draft review bodies (`.subagent/review_body.md`), and dry-run reports
   (`.subagent/dry_run_review_iter_<iteration>_{short_git_commit}.md`) **MUST be placed into the `.subagent/`
   directory** (git ignored). Never write intermediate files to `scratch/` or other root folders. Prior to execution,
   read `.subagent/coordination.json` (if it exists) to fetch user-rejected recommendations and active constraints.
8. **Human-Only PR Merging Boundary**: The loop scope strictly terminates upon posting the approved consensus review.
   This boundary is absolute and is **not** relaxed by the never-pause policy. Agents and subagents **MUST NEVER execute
   `gh pr merge`, enable auto-merge, or add the PR to a merge queue**. Merging is exclusively the human maintainer's
   responsibility.

---

## 🛠️ Step-by-Step Execution Guide

Follow these steps when executing the `pr-review-loop` skill:

### Step 1: Parse Parameters

Determine the target Pull Request and iteration limit from the user's request:

- **`<pr_url_or_number>`**: GitHub PR URL or PR number (e.g.,
  `https://github.com/Holon-Agentic-Coder/holon-agentic-coder/pull/25` or `25`).
- **`<max_iterations>`**: Maximum number of review-resolve cycles (precedence: CLI `--max-iterations <N>` > env var
  `HOLON_PR_LOOP_MAX_ITERATIONS` > default: `25`).

> [!TIP]  
> **CI Runner Job Timeouts**: In automated CI workflows (e.g., GitHub Actions), job timeout limits may be exceeded if
> running high-iteration cycles continuously. Operators should consider configuring `HOLON_PR_LOOP_MAX_ITERATIONS=5` or
> `10` in CI environments to prevent runner timeouts.

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
   - Spawn a resolver subagent (in AGY via `invoke_subagent` with `TypeName: "self"`, or native child agent delegation)
     to execute `pr-review-resolver` on `<pr_url_or_number>`.
   - The resolver will critically evaluate each comment for diff grounding, technical accuracy, actionability, and
     scope.
   - If any comment is verified to be true and valid, apply the fix, commit
     (`fix: resolve verified pre-existing PR review comments`), and push (`git push origin <branch_name>`).

#### Phase A0.5: Re-Sync & Consolidate Drifted State (Every Iteration)

Run this reconciliation before **every** review pass. Its purpose is to make the loop's view of the branch identical to
reality, so reviewers never evaluate a diff that no longer exists. Nothing here may end the loop.

1. **Refresh remote truth**: `git fetch origin <branch_name>` and
   `gh pr view <pr_url_or_number> --json headRefOid,state,mergeable`. Compare the PR head, local `HEAD`, and
   `origin/<branch_name>`. If any of them moved, delete cached dumps (`.subagent/pr<number>.diff`) and re-fetch, so the
   next review pass reads the current diff.
2. **Consolidate another author's in-flight work**: run `git status --porcelain`. If tracked files hold edits the loop
   did not author (a human maintainer or a parallel agent session working the same branch):
   - Capture them first: `git diff > .subagent/concurrent_iter_<iteration>_{short_git_commit}.patch`.
   - Re-verify each hunk against the PR diff, `.agents/rules.md`, `.beans/` ground truth and CI. Verified, in-scope,
     prettier-clean edits are **adopted**: commit them as their own `fix: consolidate concurrent review fixes ...`
     commit that names where the work came from and lists any dropped hunk with the reason (for example "re-wrapped by
     `prettier --check`, which CI enforces").
   - Only edits proven factually wrong or CI-breaking are reverted, and only after the patch file exists on disk, with
     the ruling recorded in `.subagent/coordination.json` and in the following resolution commit.
   - Never `git stash`, `git reset --hard`, `git checkout --`, or `git clean` unverified work: in-flight work must stay
     recoverable, and another author's commits are never dropped to make a push easy.
3. **Integrate diverged pushes**: if `origin/<branch_name>` carries commits the loop lacks, run
   `git pull --rebase origin <branch_name>`, keep both intents when rebasing documentation, re-run
   `npx prettier --write "**/*.md"`, and continue. A rejected push is a rebase, never a `--force`.
4. **Re-query volatile state**: CI status, review threads, and PR `mergeable` are re-read for the current head; results
   captured for an older head are never reused.
5. **Log the reconciliation**: append a row to the loop history (drift detected, action taken, head after sync) so the
   final report shows exactly what was consolidated.

#### Phase A: Run Reviewer Subagent (Dry-Run Mode)

Execute the review pass in a clean, isolated subagent context.

##### 📋 Generic Subagent Contract (Any Coding Agent):

- **Role**: `PR Reviewer (Iteration <iteration>)`
- **Context Isolation**: Spin off a dedicated child context using your agent's native subagent tool, child task runner,
  or child process to keep parent context clean and prevent prompt degradation.
- **Model**: Inherit the parent agent's model (`inherit`).
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

##### 🚀 Antigravity (AGY) Invocation:

In the AGY runtime, call `invoke_subagent`:

```json
{
  "Subagents": [
    {
      "TypeName": "self",
      "Role": "PR Reviewer (Iteration <iteration>)",
      "Model": "inherit",
      "Prompt": "<Prompt Instructions from above>"
    }
  ]
}
```

_Note on AGY: Do not poll or sleep; AGY resumes execution automatically upon subagent completion._

Wait for the subagent to complete and inspect its report.

---

#### Phase B: Evaluate Exit Conditions & Post Final Review

1. **Approval / Clean Pass**:
   - The loop moves to consensus review **ONLY IF**:
     1. The dry-run reviewer subagent verdict is **`APPROVED`** (zero Critical 🔴 or Important 🟡 issues remain; **only
        Nit / Optional 🟢 findings are allowed**).
     2. **ALL GitHub Actions CI checks (`gh pr checks <pr>`) pass cleanly** with no failing jobs.
   - **Execute 3-Agent Ensemble Consensus Review**: Spin off a consensus review in an isolated child context with
     **Ensemble Consensus Mode** enabled:
     - **Generic Subagent Contract (Any Coding Agent)**:
       - **Role**: `PR Ensemble Reviewer (Iteration <iteration>)`
       - **Model**: Inherit parent model (`inherit`).
       - **Prompt Instructions**:
         > Load and execute the `pr-reviewer` skill for `<pr_url_or_number>` using the **3-Agent Ensemble Consensus
         > Model**. Spawn 3 independent subagents, merge their consensus findings into a consolidated report, and
         > evaluate issue counts.
         >
         > **Posting Gate**:
         >
         > - If ANY Critical (🔴) or Important (🟡) issues are flagged by the consensus reviewers:
         >   - **DO NOT POST TO GITHUB**. Skip executing `gh pr review`.
         >   - Save the consolidated findings report locally to
         >     `.subagent/consensus_review_iter_<iteration>_{short_git_commit}.md`.
         > - If and ONLY IF zero Critical (🔴) and zero Important (🟡) issues remain (only Nit/Optional 🟢 findings
         >   allowed) AND all GitHub Actions CI checks pass cleanly:
         >   - Write the review body to `.subagent/review_body.md`.
         >   - Post the official review to GitHub via
         >     `gh pr review <pr_url_or_number> --approve -F .subagent/review_body.md` (falling back to `--comment` if
         >     PR author is the authenticated user).
     - **Antigravity (AGY) Invocation**:
       ```json
       {
         "Subagents": [
           {
             "TypeName": "self",
             "Role": "PR Ensemble Reviewer (Iteration <iteration>)",
             "Model": "inherit",
             "Prompt": "<Prompt Instructions from above>"
           }
         ]
       }
       ```
   - **Evaluate Consensus Review Verdict & Exit Conditions**:
     - **Case 1: Clean Consensus Pass (0 Critical, 0 Important issues remaining)**:
       - The PR has received unanimous ensemble consensus approval with zero blocking or important issues left to
         action.
       - Official review has been posted to GitHub.
       - **STOP THE LOOP.**
       - **Notify the user** that the PR is approved and awaits manual merge:
         > ✅ **PR #N is approved.** The 3-agent ensemble consensus review has been posted to GitHub and all CI checks
         > are passing. Please review and merge it manually at `<pr_url>` when you are ready.
       - **NEVER merge autonomously**: Agents MUST NOT run `gh pr merge`, add the PR to the merge queue, or enable
         auto-merge. Merging is strictly reserved for the human maintainer.
       - Branch and worktree cleanup must only be performed after the human confirms the merge has completed, or when
         the user explicitly requests cleanup.
     - **Case 2: Critical or Important Issues Flagged by Consensus Reviewers**:
       - **DO NOT POST TO GITHUB**. Ensure no intermediate review comment was posted to the GitHub PR thread.
       - If `iteration >= max_iterations`:
         - Spawn a final `pr_reviewer` subagent to post the final review comment detailing remaining issues to GitHub PR
           via `gh pr review`.
         - **STOP THE LOOP**.
         - Output warning:
           `Reached maximum iteration cap (<max_iterations>). Posted final review comment to GitHub. Stopping loop.`
       - Otherwise:
         - **DO NOT STOP THE LOOP**.
         - **Proceed immediately to Phase C (Resolver Subagent)** with the consensus findings report from
           `.subagent/consensus_review_iter_<iteration>_{short_git_commit}.md`. The resolver subagent MUST resolve all
           flagged Critical and Important issues, commit the fixes, push to the remote feature branch, and re-run the
           review in the next iteration.

2. **Convergence Escalation Ladder (Never Pause)**:
   - Inspect dry-run and consensus reports from prior iterations (`.subagent/*_review_iter_*.md`).
   - If the exact same issue is flagged across 3 consecutive iterations with no diff change, or if reviewers oscillate
     between conflicting recommendations: **do not post to GitHub, do not stop, do not wait for input.** Climb the
     ladder inside the same iteration and keep counting:
     1. **Re-sync** (Phase A0.5) and re-review the refreshed diff. Adopting a concurrent commit or rebasing a moved head
        silently clears a surprising share of "stuck" findings, because reviewers were reading a diff that no longer
        exists.
     2. **Re-adjudicate against primary sources.** Read the file, run the command, open the bean, check the YAML schema,
        or read the CI log instead of trusting any reviewer's recollection. A finding that cites a claim must be checked
        against that claim's source of truth (e.g. `grep '^status:' .beans/*-0039--*.md`).
     3. **Apply the union of recommendations.** When reviewers prescribe different fixes for the same defect, implement
        the most conservative superset that satisfies all of them simultaneously; for prose, choose the wording that is
        true under every reading.
     4. **Rule false findings out in writing.** Append each disproved, out-of-scope, or rule-conflicting finding to
        `rejected_suggestions` in `.subagent/coordination.json` with evidence and the ruling. Reviewer and resolver
        passes read that ledger (step 3e of `pr-review-resolver`), which is the mechanism that actually stops
        re-flagging -- a pause never did.
     5. **Re-scope oversized findings.** When a finding is real but bigger than this PR (cross-repository bug, missing
        migration, product decision), open a new sequentially numbered bean, mark the finding `deferred -> <bean id>` in
        the coordination ledger, and continue reviewing the reduced scope.
   - Every rung is executed and pushed by the loop itself. If the ladder is exhausted for a finding, keep iterating to
     the cap and surface it there: the iteration cap is the only place an unresolved finding may end the loop.

3. **Max Iterations Cap**:
   - If `iteration >= max_iterations` and unresolved Critical or Important issues remain after Phase C:
     - Post a single final review comment to GitHub PR via `gh pr review` summarizing remaining issues.
     - **STOP THE LOOP**.
     - Output a warning:
       `Reached maximum iteration cap (<max_iterations>). Posted final review comment to GitHub. Stopping loop.`

---

#### Phase C: Run Resolver Subagent

If changes were requested or actionable issues exist (any Critical 🔴 or Important 🟡 findings, or actionable Nit 🟢
suggestions):

Execute the resolution pass in a clean, isolated subagent context.

##### 📋 Generic Subagent Contract (Any Coding Agent):

- **Role**: `PR Review Resolver (Iteration <iteration>)`
- **Context Isolation**: Spin off a dedicated child context using your agent's native subagent tool, child task runner,
  or child process to keep parent context clean and apply code fixes safely.
- **Model**: Inherit the parent agent's model (`inherit`).
- **Target Worktree**: Locate the target repository worktree under `apps/holon-agentic-coder/{branch}`,
  `apps/holon-coherence/{branch}`, or repository root.
- **Prompt Instructions**:
  > Load and execute the `pr-review-resolver` skill for `<pr_url_or_number>`.
  >
  > 1. Fetch PR diff and existing review comments / dry-run review findings report via `gh` or `.subagent/`.
  > 2. Critically evaluate each comment/finding across **all severity levels (Critical 🔴, Important 🟡, and
  >    Nit/Optional 🟢)** for diff grounding, technical accuracy, actionability, and scope relevance.
  > 3. Apply changes to resolve **all Critical (🔴) and Important (🟡) issues**, as well as any actionable
  >    **Nit/Optional (🟢)** suggestions.
  > 4. Commit applied changes with message: `fix: apply validated PR review suggestions (Iteration <iteration>)`.
  > 5. Push local commits to remote feature branch (`git push origin <branch_name>`) so GitHub PR diff updates for the
  >    next review pass. If the push is rejected as non-fast-forward, run `git pull --rebase origin <branch_name>`, keep
  >    both intents, re-run `npx prettier --write "**/*.md"`, and push again -- never resolve drift with `--force`,
  >    `--force-with-lease`, or by dropping the other author's commits.
  > 6. Return a summary of applied fixes and skipped comments.

##### 🚀 Antigravity (AGY) Invocation:

In the AGY runtime, call `invoke_subagent`:

```json
{
  "Subagents": [
    {
      "TypeName": "self",
      "Role": "PR Review Resolver (Iteration <iteration>)",
      "Model": "inherit",
      "Prompt": "<Prompt Instructions from above>"
    }
  ]
}
```

_Note on AGY: Do not poll or sleep; AGY resumes execution automatically upon subagent completion._

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
- **Final PR Status**: `APPROVED` / `CHANGES_REQUESTED` (Cap Reached). There is no `PAUSED` status: the loop self-heals
  drift and escalates non-convergent findings instead of stopping.
- **Drift Consolidated During Loop**: `<none | list of adopted/rebased commits and patches>`

#### Cycle History:

| Iteration | Review Verdict    | Issues Found | Resolutions Applied | Commit Pushed | Drift & Sync Actions                |
| --------- | ----------------- | ------------ | ------------------- | ------------- | ----------------------------------- |
| 1         | CHANGES_REQUESTED | 3            | 3 applied           | `a1b2c3d`     | adopted concurrent commit `b7c2f1a` |
| 2         | APPROVED          | 0            | 0 applied           | N/A           | re-fetched diff after push          |
```
