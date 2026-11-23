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
| `--no-ps`     | Skip inspecting running host/Docker processes via `ps` | `false`                 |

### Output Table Schema

| Column          | Meaning                                                                                                                     |
| :-------------- | :-------------------------------------------------------------------------------------------------------------------------- |
| `Bean #`        | Clean 4-digit bean ID(s) (`0347, 0354`), or `—` for unmapped active flows/PRs                                               |
| `Target`        | Repository target (`HAC`, `Coherence`, `dev-env`, or `harness`)                                                             |
| `Title`         | Concise bean or flow title                                                                                                  |
| `Agent`         | The flow's runner agent (`claude-agent`, `antigravity-agent`, ...), from the live process or the checkpoint; `—` if unknown |
| `Model`         | The flow's model id (`claude-fable-5-2`, `gemini-4-argon`, ...), from the live process or the checkpoint; `—` if unknown    |
| `Stage`         | Active Holon stage (preferring live Docker role / admission wait over stale disk)                                           |
| `Time in Stage` | How long the bean has been in its current stage (compact: `45s`, `12m`, `1h05m`, `2d3h`; `—` if unknown)                    |
| `PR & CI`       | Open PR link, CI rollup (`pass`/`fail`/`running`), review count, mergeability flags                                         |
| `Total Time`    | How long the bean has been in flight overall (same format; `—` if unknown)                                                  |
| `Notes`         | Live state first (`live · 31m (PID, session)`, or `idle`), then blockers, warnings, stale attempts                          |

Rows are merged per bean: when several attempts exist (for example a stale first-attempt worktree plus a live `-v2`
flow), the live or most-advanced attempt is shown and the others are listed in Notes as `stale attempt ...`.

### Mapping rules

- Child intents/PRs of a split flow (branches `I-<ts>-<parent-slug>/P-...--1-<child-slug>/...`) map to the parent intent
  slug, which is matched to `todo/intent-<bean#>-*.json` (by the JSON `slug` or the file-name slug, ignoring a trailing
  `-vN`). Flows therefore receive their bean number even with no other link.
- A PR is only matched by branch (execution branch, then `I-<ts>-<slug>/`) or by a whole-number bean reference in its
  branch or title; digits inside timestamps never match.

### Time sources (real data only)

- **Time in Stage**: in the newest `.holon/flow/checkpoint-*.json` of the flow worktree, the current stage's
  `context.stage_results.<stage>.start_time`; if absent, the latest `end_time` of the stages already recorded (the
  previous stage ended when this one began); else the checkpoint `timestamp`; else the checkpoint file mtime. A live
  Stage 4 iteration still reports time since the stage began, not the iteration.
- **Total Time**: now minus the earliest of the `I-<ts>` epoch in the flow's intent/plan/execution branch and the first
  `holon-knowledge/ledger/intents.jsonl` row `created_at` for that intent (including its split children) in the flow
  worktree. Only open PRs are inspected, so the end point is always now. The bean's status change is not used (beans
  record no status history). PR-only rows use the `I-<ts>` epoch of the PR head branch.
