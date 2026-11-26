# Subagent Invocation & AGY Runtime

How to delegate to subagents and the Antigravity runtime. Moved verbatim from `AGENTS.md`.

---

## 🤖 Subagent Invocation & AGY Runtime

Subagent delegation in this ecosystem is primarily targeted towards the **Antigravity (AGY)** runtime:

- **Invocation Tool**: Use the `invoke_subagent` tool to spawn child tasks, isolated review passes, and resolution
  passes.
- **Subagent Type**: Specify `TypeName: "self"` to inherit the full suite of parent capabilities, tools (file viewing,
  editing, command execution), instructions, and credentials. Use `TypeName: "research"` for read-only exploratory
  research.
- **Model Selection & Automatic Credit Fallback**: Set `Model: "inherit"` by default to inherit the parent agent's
  active model configuration. If credit or quota runs out on the higher-level model (`"inherit"` / `"pro"`),
  automatically fall back to `"flash"` and then `"flash_lite"` (and similarly step down `claude-fable-5-2` $\rightarrow$
  `claude-opus-5-5` $\rightarrow$ `claude-sonnet-4-6` $\rightarrow$ `claude-haiku-4-5` or `gemini-4-neon` $\rightarrow$
  `gemini-4-argon` $\rightarrow$ `gemini-4-hydrogen` $\rightarrow$ `gemini-3.8-flash` in `holon` CLI invocations) and
  continue the flow or review loop from the current stage without discarding completed work.
- **Reactive Wakeup (Zero Polling)**: The AGY runtime automatically wakes up the parent agent upon subagent completion
  or message delivery. Never poll or loop on subagent status.
- **Generic Coding Agent Compatibility**: Skill workflows (such as `pr-review-loop`) define generic subagent task
  contracts so any coding agent (Claude Code, Codex, Pi, OpenCodeInterpreter) can spin off subagents using its native
  delegation mechanism (child process, task tool, or isolated session), while retaining explicit AGY invocation
  parameters for seamless native execution.
- **Subagent names**: see [Subagent names](#subagent-names).

## Standing git-safety preamble

Every subagent brief includes this block verbatim. It overrides any conflicting instruction in a brief or skill.

- Never `git stash`. The stash stack is shared by every worktree and session. To set uncommitted work aside, save it as
  a patch file outside the tracked tree; if the tree must be clean, use a temporary WIP commit on your own branch.
- Never `--no-verify`. If a pre-commit hook fails on a file you did not change, run `npx prettier --write` on that file
  only; if the hook still fails, stop and report.
- Stage by explicit path only (`git add <path> ...`). Never `git add -A`, `git add .`, or a directory path that holds
  other agents' files.
- Never check out, edit, build or measure in a `main` worktree.
- Never force-push or rebase a flow branch, and never push to `main`.
- No co-author or attribution trailers on commits unless the user's own instructions require them.
- Clock-read UTC timestamps only: read every timestamp you write from `date -u +%Y-%m-%dT%H:%M:%SZ` at write time; never
  type, estimate, round or copy one, and never label a local time `Z`.

---

## Subagent names

Every subagent a skill spawns is named `#<PR> - <what it is doing>`. This applies to the AGY `Role`, Claude Code's Agent
`description`, or whatever your runtime uses. Claude Code's agent list shows the Agent `name` field, not `description`,
and `name` allows only `[A-Za-z0-9_-]` (max 64): set it too, as `pr<PR>-<what>` (`pr248-review-loop`) or
`bean<id>-<what>` (`bean0369-holon-flow`). The operator can then tell at a glance which pull request each running
subagent belongs to (maintainer, 2026-11-23).

- **With a PR:** `#244 - resolve conflicts`, `#244 - review loop orchestrator`, `#244 - iter 15 dry-run reviewer`,
  `#244 - iter 15 ensemble reviewer 2`, `#244 - iter 15 resolver`, `#244 - post-merge`.
- **Before a PR exists** (a flow in Stages 1–3): `bean <id> - <what it is doing>`, for example
  `bean 0363 - holon flow ci-gate-after-main-merge`. Use the PR number once the PR opens.
- The PR number comes from the target repository. When the repository is not obvious from context, add it after the
  number: `#38 dev-env - review loop orchestrator`.

---
