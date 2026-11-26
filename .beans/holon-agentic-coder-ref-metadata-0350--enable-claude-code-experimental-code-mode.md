---
# holon-agentic-coder-ref-metadata-0350
title: "Enable Claude Code code mode (CLAUDE_CODE_EXPERIMENTAL_CODE_MODE=1) for every Claude run"
status: in-progress
type: feature
priority: high
tags:
  - claude
  - holon-flow
  - subagents
  - harness
  - holon-agentic-coder
created_at: 2026-11-21T01:06:00Z
updated_at: 2026-11-24T13:00:00Z
---

## Problem

Claude Code added an experimental code mode, switched on with the environment variable
`CLAUDE_CODE_EXPERIMENTAL_CODE_MODE=1`. The maintainer wants it enabled for every place that runs Claude: the Holon
flow, subagents, and anything else. Nothing sets the variable today.

## Action

1. **Harness flow runner (direct edit).** `.agents/skills/holon_flow/scripts/flow_env.py` builds the environment for
   `holon flow` with `--agent claude-agent`. Add `CLAUDE_CODE_EXPERIMENTAL_CODE_MODE=1` there, and keep a value the
   caller already set. Add a test in `tests/test_flow_env.py`. Document it in `.agents/skills/holon_flow/SKILL.md`.
2. **Harness Claude sessions and subagents (direct edit).** Set the variable in the project's `.claude/settings.json`
   `env` block, so interactive sessions and every subagent they spawn inherit it. Check that subagents and skills run
   through the Agent tool pick it up. Never put credentials in that file.
3. **Target containers (through the Holon flow on `holon-agentic-coder`).** The claude runner inside the sandbox
   containers must run with the variable set for every role: Stage 1-3 agents, the Stage 4 reviewers and resolver, and
   Stage 5. Candidates on `main`:
   - `agent_runner.py`
   - `agent_defaults.py`
   - `claude_credential.py`
   - the env passed to role containers
   - `entrypoint/role_dispatcher.sh`

   Make it a documented default that an operator can override (for example `HOLON_CLAUDE_CODE_MODE=0`), pass it through
   to the container, and record it in `holon doctor`. Add hermetic tests showing that the claude runner's command
   environment contains the variable and that the override turns it off.

4. **Other Claude entry points.** Check the remaining places that start `claude`: the review-loop skills, post-merge,
   resolve-conflict, holon-coherence if it runs Claude, and the dev-env shell profile if the maintainer wants it
   globally. Set the variable in each, or record why one is excluded.
5. **Verification.**
   - Run one real flow with the variable set and confirm it shows in the runner environment (never print secrets).
   - Compare token use and duration against a recent flow of similar size, and record any regressions.
   - Because the mode is experimental, note how to switch it off quickly if it misbehaves.

## Notes

- Keep it switchable, because the feature is experimental.
- Intent JSON must not name harness paths. The target-repo part goes through the Holon flow.

## Progress

- 2026-11-23: Harness half done, uncommitted: `flow_env.py` sets `CLAUDE_CODE_EXPERIMENTAL_CODE_MODE=1` for
  `claude-agent` (flow process and the settings `env` the containers read; a caller-set value such as `0` is kept), two
  tests in `tests/test_flow_env.py`, a note in the `holon_flow` skill, and the `env` block of `.claude/settings.json`.
- Target half: flow `claude-code-mode-default-on` launched (`antigravity-agent` / `gemini-4-argon`), scoped to
  `agent_runner.py`, `env_registry.py`, their tests and `docs/environment_variables.md`; off switch
  `HOLON_CLAUDE_CODE_MODE=0`.
- 2026-11-24: `Holon-Agentic-Coder/holon-agentic-coder#268` (`claude-code-mode-default-on`, Action 3 target containers)
  merged into `main` at `28340ea2` (11/11 CI green, Stage 5 calibrated EV predicted `61.88` / actual `67.77` / delta
  `+5.89`), `apps/holon-agentic-coder/main` was fast-forwarded, Docker images and `holon` CLI were rebuilt/reinstalled,
  and `flow-claude-code-mode-default-on` was pruned.
- 2026-11-24: Maintainer-instructed host-side cleanup exception on PR #268 (`ce56b34d`): reverted 36 unrelated
  historical `plans/` files back to `origin/main` (touched by Stage 4 resolver's repo-wide Prettier and
  `prettier-ignore` edits in iterations 2–3) and relaunched from `--from-stage review` (follow-up Bean `0392`).

- 2026-11-24 (clean-up): stays open. Target containers (Action 3) are delivered by PR #268. Remaining: Action 4 (check
  the other Claude entry points: review-loop skills, post-merge, resolve-conflict, holon-coherence, dev-env profile),
  Action 5 (verification run: variable visible in the runner environment, token and duration comparison, how to switch
  it off), and committing the harness half (Actions 1 and 2, still uncommitted on this branch).
