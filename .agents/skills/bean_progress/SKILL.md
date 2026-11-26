---
name: bean-progress
description: >-
  Reports live status and progress of all in-flight beans across the Holon ecosystem (holon-agentic-coder,
  holon-coherence, dev-env, and harness), correlating .beans/, todo/ intents, flow worktree checkpoints, open GitHub
  PRs, and active host/Docker processes across sessions (Antigravity, Claude Code, Codex, terminal) into a concise
  Markdown table while strictly excluding completed and scrapped beans. Activate whenever the user asks for bean
  progress, in-flight beans, active flows across sessions, or an in-flight bean status table.
---

# Bean Progress Skill (`bean-progress`)

> [!NOTE] **Model tier: lowest.** This skill is mechanical and read-only, so run it directly via its script (or in a
> dedicated subagent on the lowest tier from [`.agents/model-tiers.md`](../../model-tiers.md)). Do not hard-code a model
> name here.

Provides an instant, read-only Markdown table of every bean currently in flight across all local worktrees, open Pull
Requests, and active runner sessions.

---

## Core Invariants & Rules

1. **Strict Exclusion of Completed & Scrapped Beans**:
   - Any bean with `status: completed` or `status: scrapped` MUST NEVER appear in the output table, even if leftover
     `todo/intent-*.json` files or unpruned flow worktrees still exist on disk.
2. **Strictly Read-Only**:
   - Never modify `.beans/`, commit changes, kill processes, or mutate git branches or PRs.
3. **Cross-Session Visibility**:
   - Inspects live `run_holon_flow.py`, `holon flow`, Docker role containers, and quota/merge waiters across all
     sessions (Antigravity, Claude Code, Codex, and standalone terminal processes) using strict ancestor inspection.
4. **Clean 4-Digit Bean Numbers**:
   - Render bean IDs as clean 4-digit numbers (`0193`, `0347, 0354`), never file paths or `file://` links inside table
     cells.
5. **Authentic State Only**:
   - Every stage, PR link, CI summary, PID, and runner model comes directly from disk state, `gh`, and `ps` output.

---

## Execution Workflow

Run [bean_progress.py](./scripts/bean_progress.py) from the harness root:

```bash
uv run python .agents/skills/bean_progress/scripts/bean_progress.py
```

Return the resulting Markdown table directly to the user verbatim (with a brief one-line summary of totals if helpful).

### CLI Flags

| Flag          | Description                                            | Default                 |
| :------------ | :----------------------------------------------------- | :---------------------- |
| `--repo-root` | Harness repository root path                           | Auto-detected repo root |
| `--beans-dir` | Explicit directory containing bean markdown files      | `<repo-root>/.beans`    |
| `--json`      | Emit structured JSON array instead of a Markdown table | `false`                 |
| `--no-gh`     | Skip querying open Pull Requests via `gh pr list`      | `false`                 |
| `--wide`      | Render every column in one wide table (no detail list) | `false`                 |
| `--no-ps`     | Skip inspecting running host/Docker processes via `ps` | `false`                 |

### Output layout

The default output is a **compact table** (Bean #, Target, Title, Agent, Model, Stage, In Stage, Live, PR & CI, Merge,
Total) followed by a **"Last activity and notes"** list with one line per bean. The long cells are kept out of the table
on purpose: a table with them is too wide for a terminal and is then shown as raw text instead of a table. Agent and
model are shortened in the compact table (`claude`, `fable-5-2`). Pass `--wide` for every column in one table, and
`--json` for the full fields.

### Output Table Schema

| Column          | Meaning                                                                                                                                                                                                                                                                                                                                                                                 |
| :-------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Bean #`        | Clean 4-digit bean ID(s) (`0347, 0354`), or `—` for unmapped active flows/PRs                                                                                                                                                                                                                                                                                                           |
| `Target`        | Repository target (`HAC`, `Coherence`, `dev-env`, or `harness`)                                                                                                                                                                                                                                                                                                                         |
| `Title`         | Concise bean or flow title                                                                                                                                                                                                                                                                                                                                                              |
| `Agent`         | The flow's runner agent (`claude-agent`, `antigravity-agent`, ...), from the live process or the checkpoint; `—` if unknown                                                                                                                                                                                                                                                             |
| `Model`         | The flow's model id (`claude-fable-5-2`, `gemini-4-neon`, ...), from the live process or the checkpoint; `—` if unknown                                                                                                                                                                                                                                                                 |
| `Stage`         | Active Holon stage (preferring live Docker role / admission wait over stale disk). At Stage 3 admission it names every blocker (`Stage 3 (Blocked: #275, bean 0376, no PR yet)`); with no live runner and every blocker gone it adds `; blocker gone, not resumed`; the compact table shortens a long list to `first +N more` (full list in the notes line); `--json` adds `blocked_by` |
| `Time in Stage` | How long the bean has been in its current stage (compact: `45s`, `12m`, `1h05m`, `2d3h`; `—` if unknown)                                                                                                                                                                                                                                                                                |
| `Live`          | 🟢 when a process is actively working the row right now (a live `run_holon_flow`/`holon flow` runner or role container, or a review/resolver turn); 🔴 otherwise, including parked, idle and `Not started` rows                                                                                                                                                                         |
| `PR & CI`       | Open PR link, CI rollup (`pass`/`fail`/`running`), review count, mergeability flags                                                                                                                                                                                                                                                                                                     |
| `Merge`         | 🟢 only when the PR is open, approved by the consensus review on the head (or on a head followed only by plans/, executions/, holon-knowledge/ changes), calibrated, MERGEABLE and CLEAN with every check SUCCESS, so the maintainer can merge now; 🔴 otherwise; `--json`: `mergeable_now`                                                                                             |
| `Total Time`    | How long the bean has been in flight overall (same format; `—` if unknown)                                                                                                                                                                                                                                                                                                              |
| `Last Activity` | What the flow is doing or last did: the live role container (`now: review iter 2 running`), then the newest of the worktree's HEAD commit (`commit 2m ago: <subject>`; role agents commit step by step, so this is the closest thing to live work progress) and the last line of the latest checkpoint's flow log (`checkpoint 8m ago: execute: ok (...)`)                              |
| `Notes`         | Live state first (`live · 31m (PID, session)`, or `idle`), then blockers, warnings, stale attempts                                                                                                                                                                                                                                                                                      |

**One row per live flow or PR.** A bean with several concurrent flows (for example three test batches of one bean, each
with its own PR) gets one row each: the same `Bean #` repeated, rows adjacent, and in the notes list each line is
prefixed with the flow slug. A flow whose runner is live, or that has an open (or merged/closed) PR, is never labelled a
stale attempt. Only a dead attempt with no runner and no PR (for example a first-attempt worktree next to a live `-v2`
flow) is folded into the best row's Notes as `stale attempt ...`. A bean with no flow keeps its single row.

Only `flow-*` worktrees, or worktrees holding a `.holon/flow` checkpoint, count as flows; any other worktree (such as a
temporary audit worktree) is ignored.

### Split (decomposed) flows

When a plan was decomposed into child sub-intents (child branches `I-<ts>-<slug>/P-...--N-<child-slug>/...`, child PRs
merged into the parent plan branch, one parent PR into main), the parent flow is one row. Stage reads
`Stage 3 (child 4 of 5: <child-slug>)` (the active child's real stage; a non-generic sub-state follows a semicolon, e.g.
`Stage 4 (child 4 of 5: <child-slug>; Review iter 2)`). M comes from the parent checkpoint's `children_progress`; when
it is unknown the cell reads `child 4: <child-slug>`. `PR & CI` shows the active child's open PR followed by
`merged #316 #318 #320` for the child PRs already merged; once the parent PR into main exists it is shown instead of the
child PR.

### Stale rows

| Row shows                                                 | Meaning                                                              | Act                                                                                      |
| :-------------------------------------------------------- | :------------------------------------------------------------------- | :--------------------------------------------------------------------------------------- |
| Stage `Merged — post-merge pending`, PR cell `#n merged`  | PR is MERGED on GitHub (read via `gh`) but the bean is not completed | Run the `post-pr-merge` skill; the row disappears once the bean is completed             |
| Stage `PR closed — dead worktree`                         | Flow PR was closed unmerged and no runner is live                    | Decide: re-run the flow or scrap the bean; then `clean_branches` removes the worktree    |
| Stage `Stage 3 (Blocked: ...; blocker gone, not resumed)` | Blockers merged or vanished, no runner resumed the flow              | Park or backfill (see `.agents/coordination.md`); resume the flow if it should still run |
| `stale attempt ...` in Notes                              | An earlier attempt of the same bean with no runner and no PR         | Ignore it; remove with `clean_branches`                                                  |
| `idle` with a Stage but no PR for long                    | Runner died mid-flow                                                 | Resume or investigate the flow                                                           |

A merged PR with a completed bean never appears (completed beans are always excluded).

### Mapping rules

- Child intents/PRs of a split flow (branches `I-<ts>-<parent-slug>/P-...--1-<child-slug>/...`) map to the parent intent
  slug, which is matched to `todo/intent-<bean#>-*.json` (by the JSON `slug` or the file-name slug, ignoring a trailing
  `-vN`). Flows therefore receive their bean number even with no other link.
- A PR is only matched by branch (execution branch, then `I-<ts>-<slug>/`) or by a whole-number bean reference in its
  branch or title; digits inside timestamps never match.
- A flow shown as `Blocked` does not count toward the 4 flow slots; the reader should park it and backfill (see
  `.agents/coordination.md`).
- A Stage 3 blocker is named from the checkpoint's `admission.blocked_by`: a pull request as `#<n>`; a local flow by
  slug (its `plan_branch` `I-<ts>-<slug>/`, else its `flow-<slug>` worktree) mapped to a bean the same way, as
  `#<pr> (bean <id>)` when that flow has an open PR, else `bean <id>, no PR yet` (or `flow <slug>, no PR yet`).
  Duplicates show once; `overlap` only when the list is empty or unreadable.

### Time sources (real data only)

- **Time in Stage**: in the newest `.holon/flow/checkpoint-*.json` of the flow worktree, the current stage's
  `context.stage_results.<stage>.start_time`; if absent, the latest `end_time` of the stages already recorded (the
  previous stage ended when this one began); else the checkpoint `timestamp`; else the checkpoint file mtime. A live
  Stage 4 iteration still reports time since the stage began, not the iteration.
- **Total Time**: now minus the earliest of the `I-<ts>` epoch in the flow's intent/plan/execution branch and the first
  `holon-knowledge/ledger/intents.jsonl` row `created_at` for that intent (including its split children) in the flow
  worktree. Only open PRs are inspected, so the end point is always now. The bean's status change is not used (beans
  record no status history). PR-only rows use the `I-<ts>` epoch of the PR head branch.
