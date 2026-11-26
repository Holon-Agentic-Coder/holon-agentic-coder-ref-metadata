# PR Merging — Human-Only

The absolute rule that agents never merge a PR into `main`, what to do instead, and the post-merge protocol. Moved
verbatim from `AGENTS.md`.

---

## 🔒 PR Merging — Human-Only

> [!CAUTION] **Agents MUST NEVER merge a Pull Request that targets `main`.** This is an absolute, non-negotiable
> constraint. Merging into `main` is exclusively the human maintainer's responsibility. PRs into any other branch are
> covered by the maintainer ruling below.

The following actions are **strictly forbidden** for all agents at all times, regardless of context, user request
phrasing, or skill instructions:

- Running `gh pr merge` (with any flags: `--squash`, `--rebase`, `--merge`, `--auto`, `--delete-branch`, etc.).
- Running `gh pr merge --auto` or any command that enables auto-merge on a PR.
- Calling GitHub API endpoints (`gh api`) to merge, auto-merge, or queue a PR.
- Enabling repository settings that trigger automatic merging (`allow_auto_merge: true` via `gh repo edit` or any other
  method).
- Adding a PR to the merge queue by any means.

**Maintainer ruling (2026-11-09): only a PR that targets `main` is human-only.** A PR whose base branch is **not**
`main` (nor the repository's default branch) may be merged **autonomously**, by the Holon flow engine or by an agent:
for example a sub-intent PR into its plan branch. Before merging, verify immediately beforehand that the PR's
`baseRefName` is not `main` or the default branch (refuse otherwise), that its consensus review is approved, that its
calibration report is included, that CI is green and that it is mergeable. Prefer a merge commit, so the branch's
commits stay ancestors of the base. Auto-merge, the merge queue and `gh repo edit` settings that merge on their own stay
prohibited. **Everything else in this section applies unchanged to a PR that targets `main`**, including the combined PR
from a decomposed plan's branch into `main`.

**What agents must do instead:**

After the pr-reviewer ensemble consensus review is approved and posted to GitHub, the agent MUST stop all GitHub-facing
PR activity (no further `gh pr` writes of any kind). On a PR the Holon flow drove it then runs stage 5
(`holon calibrate <execution_branch>`) itself before requesting the merge, per "Ordering of the merge boundary" above:
it creates and pushes the `/calibrated` branch, merges or fast-forwards the calibration commit into the PR head
execution branch (`.../_`) so the calibration report is included in the PR diff, pushes the updated PR branch to
`origin`, and reports:

> ✅ **PR #N is approved.** The 3-agent ensemble consensus review has been posted to GitHub and Stage 5 calibration has
> been completed and included in the PR. Please review and merge it manually at `<pr_url>` when you are ready; merging
> before stage 5 (`holon calibrate`) has run destroys the `E-...` branch that calibration reads.

Branch and worktree cleanup (removal of feature branch worktrees, pruning tracking refs) must only be performed
**after** the human confirms the merge has completed, or when the user explicitly requests cleanup.

**Post-Merge Protocol (target repository PRs only).** When an agent detects that a **target repository** PR
(`holon-agentic-coder` or `holon-coherence`) it drove or tracked has been merged (the human says so, a merge watcher or
`pr_merged` event fires, or `gh pr view` shows `MERGED`), it MUST, without waiting for a further instruction — harness
PRs are exempt: harness branches are the operational logbook and their merge to `main` is an infrequent maintainer
checkpoint needing no reaction:

1. **Update the beans**: set the bean(s) the PR delivered to `completed` with a summary (PR number, merge commit, review
   id, calibration commit and EV predicted vs actual), and refresh any related beans the merge unblocks or supersedes.
2. **Refresh the triage**: update the `prioritise-beans` generator data (statistics, milestones, overrides, the
   Recommended Next Execution Sequence) and regenerate `.beans/bean-triage-prioritisation.md`.
3. **Backfill open flow slots (up to 4 concurrent flows; maintainer, 2026-11-24)**: after updating beans and refreshing
   triage, first resume parked flows unblocked by this merge from their checkpoint (they take free slots ahead of new
   beans; parked flows do not count toward the 4; maintainer, 2026-11-26). Then, if fewer than 4 `holon-flow` background
   subagents are active on hosted runtimes (local runtimes remain capped at 1), automatically pick up and launch the
   highest-priority ready bean from the refreshed triage (honouring `blocked_by`, solo-sweep rules, and
   pairwise-disjoint touch sets with active flows; at most one bean touching a shared hotspot such as `flow.py` or
   `cli.py` per repository unless explicitly allowed) via `holon-flow` in a background subagent. Report both the
   post-merge summary and the newly launched flow (or explain why no eligible bean could start).
4. **Self-improvement audit**: after each merge, count the pull requests merged into `main` of both target repositories
   since the newest entry in `.beans/self-improvement-audits.md`. When the count reaches five, launch the
   self-improvement audit subagent per [self-improvement-audit.md](self-improvement-audit.md).

---

**Post-merge steps run through the `post-pr-merge` skill** (maintainer, 2026-11-13): on any detected target-repository
merge, invoke the skill in a dedicated lowest-tier subagent (tier per [model-tiers.md](model-tiers.md)), passing it the
PR facts (repo, number, merge commit, review id, flow worktree, calibration report path), and verify its report. Never
run the post-merge steps inline.
