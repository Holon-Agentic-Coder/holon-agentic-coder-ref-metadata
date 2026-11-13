---
name: resolve-conflict
description:
  Resolves merge conflicts on a Pull Request branch or worktree in a dedicated low-cost subagent. Merges `origin/main`
  into the branch (never a rebase of a flow branch), settles the append-only ledger and knowledge-base conflicts
  mechanically, resolves straightforward additive code and config conflicts, and escalates anything that needs a
  decision. Activate this skill whenever the user invokes `/resolve-conflict`, or a PR shows `CONFLICTING` or `DIRTY`.
---

# Resolve Conflict Skill (`resolve-conflict`)

> [!NOTE] **Model tier: lowest.** This skill is mechanical, so run it in a dedicated subagent on the lowest-tier model,
> found by probing the harness as described in [`.agents/model-tiers.md`](../../model-tiers.md). Do not hard-code a
> model name here.

Most conflicts here are mechanical: concurrent PRs each append rows to the same ledgers, or each add a line to the same
list. This skill handles those cheaply and hands back anything that needs a decision.

---

## 🤖 Execution Model: Dedicated Subagent on the Lowest Model

1. **Always a dedicated subagent.** Conflict resolution runs in its own subagent so the merge output and file diffs
   never enter the parent's context. The parent passes only the target (PR number or worktree path) and this file, and
   gets back a short report.
2. **Lowest tier.** The subagent runs on the lowest model tier of the harness, as defined in
   [`.agents/model-tiers.md`](../../model-tiers.md). This skill names a tier, never a model.
3. **Escalate, never improvise.** The subagent resolves only the cases below. On anything else it aborts that file's
   resolution, leaves it conflicted, and reports it. The parent then decides, or re-runs one tier up the ladder
   (**lowest** $\rightarrow$ **middle** $\rightarrow$ **top**).

---

## 🛠️ Procedure

### Step 1: Locate the branch and check the state

1. Take the PR number or worktree path from the request. For a PR, find its head branch and its worktree
   (`gh pr view <N> --json headRefName,mergeable,mergeStateStatus`; `git worktree list`). Use the existing `flow-<slug>`
   worktree; create `apps/<project>/pr<N>-<slug>` only when none exists. **Never use a `main` worktree.**
2. Stop and report if the PR is not `CONFLICTING` or `DIRTY`, if the worktree has uncommitted changes, or if a flow is
   still running on that branch (check `pgrep -fl "holon flow"` and the checkpoint).
3. `git fetch origin`, then confirm the branch is not behind its own remote (`git status -sb`).

### Step 2: Merge `origin/main` into the branch

```bash
git merge origin/main
```

Merge, never rebase: flow branches (`I-.../P-.../E-.../_`) are the audited provenance record and are never rewritten,
squashed or force-pushed. For any other branch, still prefer the merge unless the user asks for a rebase.

### Step 3: Resolve the append-only files mechanically

```bash
python3 .agents/skills/resolve_conflict/scripts/resolve_known.py --repo <worktree>
```

It handles, and stages:

- **`holon-knowledge/ledger/*.jsonl`** (`intents`, `plans`, `executions`): keeps every row from both sides, base branch
  order first, this branch's own rows interleaved by `created_at`. Nothing is de-duplicated or dropped, and no file is
  ever created beyond the three ledgers.
- **`holon-knowledge/kb/**/index.json`**: union of `entries` by `kb_id`, the later `updated_ts`.

Any other conflicted path prints `NEEDS-JUDGEMENT <path>`.

### Step 4: Resolve the straightforward remainder

Resolve a `NEEDS-JUDGEMENT` file yourself only when the conflict is purely additive and the two sides do not interact:

| Case                                                           | Resolution                                                                                                                                                |
| -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Both sides added different imports, list items or table rows   | Keep both, in the file's existing order                                                                                                                   |
| Both sides added different sentences to one description string | Keep the base text, append this branch's addition                                                                                                         |
| `flow_module_budgets.json`                                     | Take the base file, re-apply this branch's budget changes, then set any budget the merge touched to the file's real line count and run `uv run task lint` |
| One side only reformatted (whitespace, wrapping, import order) | Keep the other side's content, in the formatted style                                                                                                     |

**Escalate instead** (leave the file conflicted, run `git merge --abort` only if nothing else was resolved, and report
the path and both sides in one line each) when any of these hold: the two sides edit the same line differently; one side
deletes or renames a file the other modifies; the conflict is in logic, a test assertion, a prompt's rules or a
documented contract; or you cannot say with certainty that keeping both is correct. Never pick a side by guessing.

### Step 4b: Verify

- **Ledger and knowledge-base conflicts only:** do **not** run the test suites. Check that every line of each `.jsonl`
  parses as JSON, that no conflict marker remains (`grep -rn -E '^(<<<<<<<|>>>>>>>)'`), and that the diff against
  `origin/main` for those files contains additions only (`git diff --numstat origin/main -- <path>` shows `0`
  deletions).
- **Any code or config file touched:** run `uv run task lint` and the affected tests with `uv run pytest` (never
  `unittest`, never a `PYTHONPATH` override).

### Step 5: Commit, push, confirm

```bash
git commit --no-edit
git push origin HEAD
gh pr view <N> --json mergeable,mergeStateStatus
```

Push the branch you merged into; never push to `main`, never force-push. Re-check mergeability after a few seconds: the
PR is clean when it reads `MERGEABLE` (`UNSTABLE` only means checks are re-running). The commit message is the merge
commit's default; add no attribution trailer.

---

## 📋 Report Back (to the parent, five lines at most)

- PR or worktree, and the branch merged into.
- Files resolved mechanically and files resolved by hand (path and one phrase each).
- Files escalated, with the reason.
- Verification done (JSON check, additions-only diff, lint, tests).
- The pushed commit and the resulting `mergeable` / `mergeStateStatus`.

---

## 🚫 Hard Limits

- Never merge a PR, enable auto-merge or touch the merge queue (merging into `main` is human-only).
- Never rewrite, squash, rebase or force-push a flow-driven branch.
- Never edit, stage or reset anything in a `main` worktree.
- Never create a ledger other than `intents.jsonl`, `plans.jsonl` and `executions.jsonl`.
- Never name harness paths or bean ids in anything written into a target repository.
- Report outcomes faithfully: if a file was escalated or a check failed, say so.
